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

DB_NAME = 'Flipkart_Grocery'

TABLE_NAME = f"products_{datetime.now().strftime('%Y_%m_%d')}"

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
           
            sku VARCHAR(100) NOT NULL,
        
            product_name VARCHAR(255) NOT NULL,
            pincode INT,
            locality VARCHAR(255),
            city VARCHAR(100),
            product_url VARCHAR(500),
            brand VARCHAR(100),
            stock_avaliblity_status VARCHAR(20),
            EAN_code VARCHAR(50),
            
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_query)
        print(f"Table '{TABLE_NAME}' created successfully")
        cursor.close()
        return True
    
    except Error as e:
        print(f"Error creating table: {e}")
        return False
    return False


def insert_data(product_json) :

    con=get_connection()
    cursor=con.cursor()
    try:
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            sku, product_name, pincode, locality, city, product_url,
            brand, stock_avaliblity_status, EAN_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            # Primitives
            product_json.get('sku'),
            product_json.get('product_name'),
            product_json.get('pincode'),
            product_json.get('locality'),
            product_json.get('city'),
            product_json.get('url'),
            product_json.get('brand'),
            product_json.get('stock_avaliblity_status'),
            product_json.get('EAN_code'),
            
        )
        
        cursor.execute(insert_query, values)
        con.commit()
        
        sku = product_json.get('sku')
        print(f"Product SKU {sku} inserted successfully")
        
        cursor.close()
        con.close()
        return True
    
    except Error as e:
        print(f" Error inserting data: {e}")
        return None

def insert_multiple_data(product_json_list):
   
    if not product_json_list:
        print("No products to insert")
        return True

    con = get_connection()
    cursor = con.cursor()
    
    try:
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            sku, product_name, pincode, locality, city, product_url,
            brand, stock_avaliblity_status, EAN_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values_list = []
        
        for product_json in product_json_list:
            values = (
                # Primitives
                product_json.get('sku'),
                product_json.get('product_name'),
                product_json.get('pincode'),
                product_json.get('locality'),
                product_json.get('city'),
                product_json.get('url'),
                product_json.get('brand'),
                product_json.get('stock_avaliblity_status'),
                product_json.get('EAN_code'),
            )
            values_list.append(values)
        
        cursor.executemany(insert_query, values_list)
        con.commit()
        
        print(f"Successfully inserted {len(product_json_list)} products")
        
        return True
    
    except Error as e:
        print(f"Error inserting multiple data: {e}")
        return None
    
    finally:
        cursor.close()
        con.close()