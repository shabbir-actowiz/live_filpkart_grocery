

from datetime import datetime
import pandas as pd
import pymysql


def adjust_time():
    """Adjust time for file naming convention."""
    now = datetime.now()
    return now.strftime("%Y_%m_%d")


todayDateTime = adjust_time()
scrape_date = datetime.now().strftime("%Y-%m-%d")

# todayDateTime = "2025_04_06"
def main():
    con = pymysql.connect(
       host="localhost",
            user="root",
            password="actowiz",
            database="flipkart_grocery"
    )

    # create cursor, used to execute commands
    qr = f"""select id,
            pincode,
            city,
            state,
            locality,
            sku,
            ean_code,
            url,
            product_name,
            brand,
            stock_avaliblity_status
            from products_{todayDateTime}
            WHERE pincode IN (
            SELECT pincode
            FROM products_{todayDateTime}
            GROUP BY pincode
            HAVING SUM(
                CASE 
                    WHEN LOWER(TRIM(stock_avaliblity_status)) = 'yes'
                    THEN 1 ELSE 0 
                END
            ) >= 1
        ); """
    df = pd.read_sql(qr, con)

    # Drop column by name
    df.drop(columns=['id'], inplace=True)   # Replace 'column_name' with actual column name
    df.insert(0, 'id', range(1, 1 + len(df)))
    # Add new columns
    df.insert(10, 'platform', "Flipkart Grocery")
    df['Scrape_date'] = scrape_date

    # Add serial number column
    # df.insert(0, 'id', range(1, 1 + len(df)))

    writer = pd.ExcelWriter(
        rf"Export/flipkart_grocery_{todayDateTime}.xlsx",
        engine='xlsxwriter',
        engine_kwargs={"options": {'strings_to_urls': False}}
    )

    df.to_excel(writer, sheet_name='data', index=False)

    # Access the workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['data']

    # Define a format with borders
    border_format = workbook.add_format({'border': 1})  # Applies a thin border to all sides

    # Get the range of the data
    num_rows, num_cols = df.shape

    worksheet.conditional_format(
        0, 0, num_rows, num_cols - 1,
        {'type': 'no_blanks', 'format': border_format}
    )

    worksheet.conditional_format(
        0, 0, num_rows, num_cols - 1,
        {'type': 'blanks', 'format': border_format}
    )

    writer.close()

if __name__ == "__main__":
    main()