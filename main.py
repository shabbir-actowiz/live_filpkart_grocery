from curl_cffi import requests
import json
from location import get_serviceability
from products import get_product
import os
from db import *

product_urls=[
    '/classic-chana-dal-besan-flipkart-grocery/p/itm7b7ac8fcd5f19?pid=FLRGRFDXFEBRZACY&marketplace=GROCERY&lid=LSTFLRGRFDXFEBRZACYNXPOPQ',
    '/dettol-original-bathing-soap-bar-12-hr-protective-shield/p/itm86fb101e8ee73?pid=SOPH4M2BJHMGJDPY&lid=LSTSOPH4M2BJHMGJDPYBI1ZKM&hl_lid=&marketplace=GROCERY',
    '/nivea-creme-soft-soap-travel-handwash-bath-ph-balanced-men-women/p/itm1aaf7797f7d74?pid=SOPEU6NPMP3PZURX&lid=LSTSOPEU6NPMP3PZURXMVJFXZ&hl_lid=&marketplace=GROCERY',
]
pincodes=[
    382405,380001,560001]



def main():
    for pincode in pincodes:
        location_data = get_serviceability(pincode)
        if location_data:
            get_product(product_urls,location_data)
        else:
            continue

if __name__=='__main__':

    con=get_connection()
    cursor=con.cursor()

    create_database(cursor)
    create_table(cursor)

    cursor.close()
    con.close()

    main()