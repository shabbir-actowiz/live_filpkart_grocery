import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

# ============ DATABASE CONFIGURATION ============
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'actowiz',
}
location_table=f"locations{datetime.now().strftime('%Y_%m_%d')}"
DB_NAME = 'Flipkart_Grocery'
TABLE_NAME = f"products_{datetime.now().strftime('%Y_%m_%d')}"
master_table_name=f"master_table_{datetime.now().strftime('%Y_%m_%d')}"
# ================================================

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_database(cursor):
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")
    DB_CONFIG['database'] = DB_NAME
    print(f"Database '{DB_NAME}' created/selected successfully")


def create_table(cursor):

    try:
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (

            id INT AUTO_INCREMENT PRIMARY KEY,

            sku VARCHAR(255),
            pincode INT,
            locality VARCHAR(255),
            city VARCHAR(255),
            state VARCHAR(255),
            url text,
            product_name text,
            brand VARCHAR(255),
            stock_avaliblity_status VARCHAR(255),
            quantity VARCHAR(255),
            ean_code VARCHAR(255),
            pls JSON,
            product_data JSON,
           
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        cursor.execute(create_table_query)
        print(f"Table '{TABLE_NAME}' created successfully")
        
        return True

    except Error as e:
        print(f"Error creating table: {e}")
        return False



def insert_data(json_dict):

    con = get_connection()
    cursor = con.cursor()

    try:
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            sku,
            pincode,
            locality,
            city,
            state,
            url,
            product_name,
            brand,
            stock_avaliblity_status,
            quantity,
            ean_code,
            pls,
            product_data
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            json_dict.get('sku'),
            json_dict.get('pincode'),
            json_dict.get('locality'),
            json_dict.get('city'),
            json_dict.get('state'),
            json_dict.get('url'),
            json_dict.get('product_name'),
            json_dict.get('brand'),
            json_dict.get('stock_avaliblity_status'),
            json_dict.get('quantity'),
            json_dict.get('EAN_code'),
            json.dumps(json_dict.get('pls')) ,
            json.dumps(json_dict.get('product_data')) if json_dict.get('product_data') else None
        )

        cursor.execute(insert_query, values)
        con.commit()

        print("Data inserted successfully")

        cursor.close()
        con.close()
        return True

    except Error as e:
        print(f"Error inserting data: {e}")
        return None


def insert_multiple_data(json_list):

    if not json_list:
        print("No data to insert")
        return True

    con = get_connection()
    cursor = con.cursor()

    try:
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            sku,
            pincode,
            locality,
            city,
            state,
            url,
            product_name,
            brand,
            quantity,
            stock_avaliblity_status,
            ean_code,
            pls,
            product_data
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values_list = []

        for json_dict in json_list:
            values = (
                json_dict.get('sku'),
                json_dict.get('pincode'),
                json_dict.get('locality'),
                json_dict.get('city'),
                json_dict.get('state'),
                json_dict.get('url'),
                json_dict.get('product_name'),
                json_dict.get('brand'),
                json_dict.get('quantity'),
                json_dict.get('stock_avaliblity_status'),
                json_dict.get('EAN_code'),
                json.dumps(json_dict.get('pls')),
                json.dumps(json_dict.get('product_data')) if json_dict.get('product_data') else None
            )
            values_list.append(values)

        cursor.executemany(insert_query, values_list)
        con.commit()

        print(f"Successfully inserted {len(json_list)} records")

        return True

    except Error as e:
        print(f"Error inserting multiple data: {e}")
        return None

    finally:
        cursor.close()
        con.close()

def create_location_table(cursor):
    query = f"""
    CREATE TABLE IF NOT EXISTS {location_table}(
        id INT AUTO_INCREMENT PRIMARY KEY,
        ud text,
       
        static_location VARCHAR(255),
        pincode INT NOT NULL UNIQUE,
        status VARCHAR(50),
        serviceability BOOLEAN DEFAULT FALSE,
        locality VARCHAR(500),
        city VARCHAR(255),
        state VARCHAR(255),
        latitude DECIMAL(12, 8),
        longitude DECIMAL(12, 8),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    cursor.execute(query)
    
    print("Table 'locations' created successfully")

def insert_pincode_location(
    cursor,
    static_location,
    pincode,
    status,
    serviceability,
    locality=None,
    city=None,
    state=None,
    latitude=None,
    longitude=None,
    ud=None
    
):
    query = f"""
    INSERT INTO {location_table} (
        static_location, pincode, status, serviceability,
        locality, city, state, latitude, longitude, ud
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        static_location = VALUES(static_location),
        status = VALUES(status),
        serviceability = VALUES(serviceability),
        locality = VALUES(locality),
        city = VALUES(city),
        state = VALUES(state),
        latitude = VALUES(latitude),
        longitude = VALUES(longitude),
        ud = VALUES(ud)
    """

    values = (
        static_location, pincode, status, serviceability,
        locality, city, state, latitude, longitude, ud
    )

    cursor.execute(query, values)


def get_serviceable_locations(cursor):
    query = f"""
    SELECT
    ud,
        static_location,
        pincode,
        status,
        serviceability,
        locality,
        city,
        state,
        latitude,
        longitude
    FROM {location_table}
    WHERE serviceability = 1
      AND status = 'done'
    """
    cursor.execute(query)
    return cursor.fetchall()

def create_master_table(cursor):
    query = f"""
    CREATE TABLE IF NOT EXISTS {master_table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ud text,
        static_location VARCHAR(255),
        pincode INT,
        status VARCHAR(50),
        serviceability BOOLEAN,
        locality VARCHAR(500),
        city VARCHAR(255),
        latitude DECIMAL(12, 8),
        longitude DECIMAL(12, 8),
        state VARCHAR(255),
        ean_code VARCHAR(100),
        product_url text,
        scraping_status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(query)
    # cursor.close()
    print(f"Table '{master_table_name}' created successfully")

def insert_master_data(cursor, rows):
    if not rows:
        print("No master data to insert")
        return True

    query = f"""
   INSERT INTO {master_table_name} (
    ud,
    static_location, pincode, status, serviceability,
    locality, city, state, latitude, longitude,
    ean_code, product_url
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    values = []

    for row in rows:
        values.append((
            row.get("ud"),
            row.get("static_location"),
            row.get("pincode"),
            row.get("status"),
            row.get("serviceability"),
            row.get("locality"),
            row.get("city"),
            row.get("state"),
            row.get("latitude"),
            row.get("longitude"),
            row.get("ean_code"),
            row.get("product_url"),
        ))

    cursor.executemany(query, values)
    print(f"Inserted/updated {len(values)} master rows")
    return True

def fetch_pending_master_rows(cursor, limit=50):
    query = f"""
    SELECT
        id,
        static_location,
        pincode,
        locality,
        city,
        state,
        latitude,
        longitude,
        ean_code,
        product_url,
        ud
    FROM {master_table_name}
    WHERE scraping_status = 'pending'
    ORDER BY id
    LIMIT %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()


def update_master_rows_status(cursor, row_ids, status):

    if not row_ids:
        return

    placeholders = ",".join(["%s"] * len(row_ids))

    query = f"""
    UPDATE {master_table_name}
    SET scraping_status = %s
    WHERE id IN ({placeholders})
    """

    cursor.execute(query, [status] + row_ids)

def update_master_row_status(cursor, row_id, status):
    query = f"""
    UPDATE {master_table_name}
    SET scraping_status = %s
    WHERE id = %s
    """
    cursor.execute(query, (status, row_id))

def fetch_failed_pincodes(cursor):
    query = f"""
    SELECT
        static_location AS location,
        pincode
    FROM {location_table}
    WHERE status = 'pending'
    """
    cursor.execute(query)
    return cursor.fetchall()