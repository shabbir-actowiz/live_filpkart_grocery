import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import gzip
import json
from location import get_serviceability
from parser import *
from db import *
from products import *
from datetime import datetime


EXCEL_FILE = "Excel/act-jnssav-7544-pincodes.xlsx"
SHEET_NAME = "Flipkart Grocery"

PRODUCT_FILE = "Excel/Mapping Sheet.xlsx"
PRODUCT_LOCATION_FILE = "Excel/Flipkart Product vise locations.xlsx"


def normalize_text(value):
    return (
        str(value)
        .strip()
        .lower()
        .replace("&", "and")
    )


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

    file_path = f"pagesaves {datetime.now().strftime('%Y-%m-%d')}/pdp/{pid}_{pincode}.html.gz"

    if not os.path.exists(file_path):
        print(f"Pagesave not found | ID: {row_id} | {file_path}")
        return row_id, "failed"

    location_data = {
        "static_location": row.get("static_location"),
        "pincode": row.get("pincode"),
        "locality": row.get("locality"),
        "city": row.get("city"),
        "state": row.get("state"),
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
        "ean_code": row.get("ean_code"),
        "ud": row.get("ud"),
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

        if cleaned_data == "not found":
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
    df["location"] = df["location"].astype(str).str.strip()
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
                    cursor,
                    static_location,
                    pincode,
                    "failed",
                    0,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None
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
                    location_data.get("state"),
                    location_data.get("latitude"),
                    location_data.get("longitude"),
                    location_data.get("ud")
                )
                print(f"Serviceable: {pincode}")

            else:
                insert_pincode_location(
                    cursor,
                    static_location,
                    pincode,
                    "done",
                    0,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None
                )
                print(f"Not serviceable: {pincode}")

            con.commit()

        except Exception as e:
            insert_pincode_location(
                cursor,
                static_location,
                pincode,
                "failed",
                0,
                None,
                None,
                None,
                None,
                None,
                None
            )
            con.commit()
            print(f"Failed: {pincode} | {e}")

    cursor.close()
    con.close()


def read_grocery_products_from_excel(file_path):
    df = pd.read_excel(
        file_path,
        sheet_name="Flipkart Minutes and Grocery",
        header=1
    )

    df = df.iloc[:, [0, 1, 3]]
    df.columns = ["ean_code", "product_title", "product_url"]

    # product title and product url are required
    df = df.dropna(subset=["product_title", "product_url"])

    df["product_title"] = df["product_title"].astype(str).str.strip()
    df["product_url"] = df["product_url"].astype(str).str.strip()

    # EAN is optional, so blank EAN becomes N/A
    df["ean_code"] = df["ean_code"].fillna("N/A").astype(str).str.strip()
    df["ean_code"] = df["ean_code"].replace(
        ["", "nan", "NaN", "None", "NONE"],
        "N/A"
    )

    # product_url N/A / blank should not go into master
    df = df[df["product_url"].str.upper() != "N/A"]
    df = df[df["product_url"].str.startswith("http")]

    df = df.drop_duplicates(subset=["product_url"])

    products = df.to_dict("records")

    print(f"Total valid grocery products found: {len(products)}")

    return products

def read_product_city_mapping(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip().str.lower()

    required_columns = ["product_title", "city"]
    for col in required_columns:
        if col not in df.columns:
            raise Exception(f"Missing required column in product location file: {col}")

    df = df.dropna(subset=["product_title", "city"])

    mapping = {}

    for _, row in df.iterrows():
        product_title = normalize_text(row["product_title"])
        city = normalize_text(row["city"])

        if product_title not in mapping:
            mapping[product_title] = set()

        mapping[product_title].add(city)

    print(f"Product-city mapping loaded: {len(mapping)} products")

    return mapping


def build_master_table_data(product_file, product_location_file):
    products = read_grocery_products_from_excel(product_file)
    product_city_mapping = read_product_city_mapping(product_location_file)

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    serviceable_locations = get_serviceable_locations(cursor)

    master_rows = []
    skipped_products = []

    for product in products:
        product_title_key = normalize_text(product.get("product_title"))

        allowed_cities = product_city_mapping.get(product_title_key)

        if not allowed_cities:
            skipped_products.append(product.get("product_title"))
            continue

        for location in serviceable_locations:
            location_city = normalize_text(location.get("static_location"))

            if location_city not in allowed_cities:
                continue

            master_rows.append({
                "static_location": location.get("static_location"),
                "pincode": location.get("pincode"),
                "status": location.get("status"),
                "serviceability": location.get("serviceability"),
                "locality": location.get("locality"),
                "city": location.get("city"),
                "state": location.get("state"),
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "ean_code": product.get("ean_code"),
                "product_url": product.get("product_url"),
                "ud": location.get("ud")
            })

    if master_rows:
        insert_master_data(cursor, master_rows)

    con.commit()
    cursor.close()
    con.close()

    print(f"Master rows inserted: {len(master_rows)}")

    if skipped_products:
        print("Skipped products because no city mapping found:")
        for product in skipped_products:
            print(product)


def process_single_product(row):
    row_id = row["id"]
    product_url = row["product_url"]

    location_data = {
        "static_location": row.get("static_location"),
        "pincode": row.get("pincode"),
        "locality": row.get("locality"),
        "city": row.get("city"),
        "state": row.get("state"),
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
        "ean_code": row.get("ean_code"),
        "ud": row.get("ud"),
    }

    print(f"Processing ID: {row_id} | Pincode: {row.get('pincode')}")

    try:
        result = get_product([product_url], location_data)

        if result == "not found":
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
                executor.submit(process_single_product, row)
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

        print(
            f"Batch completed | Done: {len(done_ids)} | "
            f"Failed: {len(failed_ids)} | Not Found: {len(not_found_ids)}"
        )


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

        print(
            f"Batch completed | Done: {len(done_ids)} | "
            f"Failed: {len(failed_ids)} | Not Found: {len(not_found_ids)}"
        )


def main():
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    create_database(cursor)
    create_location_table(cursor)
    create_master_table(cursor)
    create_table(cursor)

    # pincode_rows = read_pincodes_from_excel(EXCEL_FILE)

    # failed_rows = fetch_failed_pincodes(cursor)
    cursor.close() 
    con.close()

    # if not failed_rows: 
    #     print("No failed pincodes found") 
    #     return  
    # print(f"Retrying failed pincodes: {len(failed_rows)}") 
    # check_and_store_pincodes(failed_rows)

    # check_and_store_pincodes(pincode_rows)
    print('serviceability check completed')
    # build_master_table_data(
    #     PRODUCT_FILE,
    #     PRODUCT_LOCATION_FILE
    # )

    # print("Master table built successfully")

    # Start product crawling after master table is ready.
    process_pending_product_urls(batch_size=200, max_workers=100)

    # Use this only when parsing saved pages.
    # process_pending_product_urls_from_pagesaves(batch_size=100, max_workers=10)


if __name__ == "__main__":
    main()