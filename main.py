import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import gzip
import json
from location import get_serviceability
from parser import *
from db import *
from products import *


EXCEL_FILE = "Excel/act-jnssav-7544-pincodes.xlsx"
SHEET_NAME = "Flipkart Grocery"

PRODUCT_FILE = "Excel/act-jnssav-7544-sku-based-data-collection-from-q-commerce-platforms-weekly.xlsx"

def get_pid_from_url(product_url):
    try:
        if "pid=" in product_url:
            return product_url.split("pid=")[1].split("&")[0]
    except Exception:
        pass

    return None

def process_single_product_from_pagesave(row):
    row_id = row["id"]
    product_url = row["product_url"]
    pincode = row["pincode"]

    pid = get_pid_from_url(product_url)

    if not pid:
        print(f"PID not found | ID: {row_id}")
        return row_id, "failed"

    file_path = f"pagesaves/pdp/{pid}_{pincode}.html.gz"

    if not os.path.exists(file_path):
        print(f"Pagesave not found | ID: {row_id} | {file_path}")
        return row_id, "failed"

    location_data = {
        "static_location": row.get("static_location"),
        "pincode": row.get("pincode"),
        "locality": row.get("locality"),
        "city": row.get("city"),
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
        "ean_code": row.get("ean_code"),
        'ud': row.get('ud'),
    }

    try:
        with gzip.open(file_path, "rt", encoding="utf-8") as file:
            response_text = file.read()

        product_json = json.loads(response_text)

        cleaned_data = extract_product_data(
            product_json,
            location_data,
            product_url
        )
        if cleaned_data == 'not found':
            print(f"Parser found page but product not found | ID: {row_id}")
            return row_id, "not found"
        
        elif not cleaned_data:
            print(f"Parser failed | ID: {row_id}")
            return row_id, "failed"

        insert_multiple_data([cleaned_data])

        print(f"Inserted from pagesave | ID: {row_id}")
        return row_id, "done"

    except Exception as e:
        print(f"Failed pagesave parse | ID: {row_id} | Error: {e}")
        return row_id, "failed"

def read_pincodes_from_excel(file_path):
    df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    df.columns = df.columns.str.strip().str.lower()

    required_columns = ["location", "pincode"]
    for col in required_columns:
        if col not in df.columns:
            raise Exception(f"Missing required column: {col}")

    df = df[required_columns].dropna(subset=["pincode"])
    df["pincode"] = df["pincode"].astype(int)
    df = df.drop_duplicates(subset=["pincode"])

    return df.to_dict("records")


def check_and_store_pincodes(pincode_rows):
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    for row in pincode_rows:
        static_location = row["location"]
        pincode = row["pincode"]

        print(f"Checking serviceability: {pincode}")

        try:
            location_data = get_serviceability(pincode)

            if location_data == "failed":
                insert_pincode_location(
                    cursor, static_location, pincode, "failed",
                    0, None, None, None, None
                )
                con.commit()
                continue

            if location_data and not location_data.get("error"):
                insert_pincode_location(
                    cursor,
                    static_location,
                    pincode,
                    "done",
                    1,
                    location_data.get("formatted_address"),
                    location_data.get("city"),
                    location_data.get("latitude"),
                    location_data.get("longitude"),
                    location_data.get("ud")
                )
                print(f"Serviceable: {pincode}")

            else:
                insert_pincode_location(
                    cursor, static_location, pincode, "done",
                    0, None, None, None, None, None
                )
                print(f"Not serviceable: {pincode}")

            con.commit()

        except Exception as e:
            insert_pincode_location(
                cursor, static_location, pincode, "failed",
                0, None, None, None, None, None
            )
            con.commit()
            print(f"Failed: {pincode} | {e}")

    cursor.close()
    con.close()


def read_grocery_products_from_excel(file_path):
    df = pd.read_excel(file_path, sheet_name=1, header=1)

    df = df.iloc[:, [0, 3]]
    df.columns = ["ean_code", "product_url"]

    df = df.dropna(subset=["product_url"])

    df["product_url"] = df["product_url"].astype(str).str.strip()
    df["ean_code"] = df["ean_code"].astype(str).str.strip()

    df = df[df["product_url"].str.upper() != "N/A"]
    df = df[df["product_url"].str.startswith("http")]
    df = df.drop_duplicates(subset=["product_url"])

    products = df.to_dict("records")

    print(f"Total valid grocery products found: {len(products)}")

    return products


def build_master_table_data(product_file):
    products = read_grocery_products_from_excel(product_file)

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    serviceable_locations = get_serviceable_locations(cursor)

    master_rows = []

    for location in serviceable_locations:
        for product in products:
            master_rows.append({
                "static_location": location.get("static_location"),
                "pincode": location.get("pincode"),
                "status": location.get("status"),
                "serviceability": location.get("serviceability"),
                "locality": location.get("locality"),
                "city": location.get("city"),
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "ean_code": product.get("ean_code"),
                "product_url": product.get("product_url"),
                "ud": location.get("ud")
            })

    insert_master_data(cursor, master_rows)

    con.commit()
    cursor.close()
    con.close()


def process_single_product(row):
    row_id = row["id"]
    product_url = row["product_url"]

    location_data = {
        "static_location": row.get("static_location"),
        "pincode": row.get("pincode"),
        "locality": row.get("locality"),
        "city": row.get("city"),
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
        "ean_code": row.get("ean_code"),
        'ud': row.get('ud'),
    }

    print(f"Processing ID: {row_id} | Pincode: {row.get('pincode')}")

    try:
        result = get_product([product_url], location_data)
        if result == 'not found':
            print(f"Product not found | ID: {row_id}")
            return row_id, "not found"
        elif result:
            return row_id, "done"
        else:
            return row_id, "failed"

    except Exception as e:
        print(f"Failed ID: {row_id} | Error: {e}")
        return row_id, "failed"


def process_pending_product_urls(batch_size=100, max_workers=50):
    # con = get_connection()
    # cursor = con.cursor(dictionary=True)
    i=0
    while True:
        # if i>=4:
        #     break
        # i+=1
        con = get_connection()
        cursor = con.cursor(dictionary=True)
        rows = fetch_pending_master_rows(cursor, batch_size)

        if not rows:
            print("No pending product URLs found")
            cursor.close()
            con.close()
            break

        row_ids = [row["id"] for row in rows]

        update_master_rows_status(cursor, row_ids, "processing")
        con.commit()

        cursor.close()
        con.close()

        done_ids = []
        failed_ids = []
        not_found_ids = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_single_product, row)
                # executor.submit(process_single_product_from_pagesave, row)
                for row in rows
            ]

            for future in as_completed(futures):
                row_id, status = future.result()

                if status == "done":
                    done_ids.append(row_id)
                elif status == "not found":
                    not_found_ids.append(row_id)
                else:
                    failed_ids.append(row_id)

        status_con = get_connection()
        status_cursor = status_con.cursor()

        if done_ids:
            update_master_rows_status(status_cursor, done_ids, "done")
        if not_found_ids:
            update_master_rows_status(status_cursor, not_found_ids, "not found")
        if failed_ids:
            update_master_rows_status(status_cursor, failed_ids, "failed")

        status_con.commit()
        status_cursor.close()
        status_con.close()

        print(f"Batch completed | Done: {len(done_ids)} | Failed: {len(failed_ids)} | Not Found: {len(not_found_ids)}")

# ===========================

def process_pending_product_urls_from_pagesaves(batch_size=100, max_workers=10):
    while True:
        con = get_connection()
        cursor = con.cursor(dictionary=True)

        rows = fetch_pending_master_rows(cursor, batch_size)

        if not rows:
            print("No pending product URLs found")
            cursor.close()
            con.close()
            break

        row_ids = [row["id"] for row in rows]

        update_master_rows_status(cursor, row_ids, "processing")
        con.commit()

        cursor.close()
        con.close()

        done_ids = []
        failed_ids = []
        not_found_ids = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_single_product_from_pagesave, row)
                for row in rows
            ]

            for future in as_completed(futures):
                row_id, status = future.result()

                if status == "done":
                    done_ids.append(row_id)
                elif status == "not found":
                    not_found_ids.append(row_id)
                else:
                    failed_ids.append(row_id)

        status_con = get_connection()
        status_cursor = status_con.cursor()

        if done_ids:
            update_master_rows_status(status_cursor, done_ids, "done")

        if failed_ids:
            update_master_rows_status(status_cursor, failed_ids, "failed")

        if not_found_ids:
            update_master_rows_status(status_cursor, not_found_ids, "not found")

        status_con.commit()
        status_cursor.close()
        status_con.close()

        print(f"Batch completed | Done: {len(done_ids)} | Failed: {len(failed_ids)} | Not Found: {len(not_found_ids)}")


# ============================

def main():
    # con = get_connection()
    # cursor = con.cursor()

    # create_database(cursor)
    # create_table(cursor)
    # cursor.close()
    # con.close()

    # # process_pending_product_urls_from_pagesaves(
    # #     batch_size=100,
    # #     max_workers=10
    # # )
    # -------------------------
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    create_database(cursor)
   
    # create_location_table(cursor) 
    
    # create_master_table(cursor)    # pincode/location table
      
    # create_table(cursor)            # final product data table
    
    # pincode_rows = read_pincodes_from_excel(EXCEL_FILE)
    # failed_rows = fetch_failed_pincodes(cursor)

    cursor.close()
    con.close()

    # if not failed_rows:
    #     print("No failed pincodes found")
    #     return

    # print(f"Retrying failed pincodes: {len(failed_rows)}")

    # check_and_store_pincodes(failed_rows)

    # # check_and_store_pincodes(pincode_rows)

    # build_master_table_data(PRODUCT_FILE)
    # print("Master table built successfully")

    process_pending_product_urls(batch_size=200)

if __name__ == "__main__":
    main()