import json
import os.path
import shutil
import subprocess
from datetime import datetime
import pandas as pd
import mysql.connector as pymysqll
import requests
from slack_sdk import WebClient

from db import *
from main import main as runMain
from export import main as exportMain



def makeConn():
    return pymysqll.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='flipkart_grocery'
    )

def fetchDateTime():

    now = datetime.now()
    timeCheker = int(now.strftime("%H%M"))

    if timeCheker < 1330:
        next_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
    elif timeCheker < 2330:
        next_time = now.replace(hour=22, minute=0, second=0, microsecond=0)

    return next_time.strftime("%Y_%m_%d")
    # return next_time.strftime("%Y_%m_%d_%I%p")
    # return "2026_06_04_10PM"

def checkPendingPincode():

    with makeConn() as conn:
        with conn.cursor() as curr:
            curr.execute("select count(*) from pincodes where status='pending'")
            count = curr.fetchone()
            if count[0]:
                return True
            else:
                return False

def checkPendingPdp():
    with makeConn() as conn:
        with conn.cursor() as curr:
            curr.execute(f"select count(*) from master_table_{fetchDateTime()} where scraping_status='pending'")
            count = curr.fetchone()
            if count[0]:
                return True
            else:
                return False

def movePagesaves():

    source=rf"C:\Testing\Flipkart-grocery\pagesaves\pagesaves {datetime.now().strftime('%Y-%m-%d')}"
    destination = rf"\\172.28.151.201\temp-storage\SynologyBackup\Q-Comm\Flipkart_Grocery\India\Web\Partial Run\act-jnssav-7544\data\Html\pagesaves {datetime.now().strftime('%Y-%m-%d')}"

    source_excel = rf'C:\Testing\Flipkart-grocery\Export\flipkart_grocery_{fetchDateTime()}.xlsx'
    destination_excel = rf'\\172.28.151.201\temp-storage\SynologyBackup\Q-Comm\Flipkart_Grocery\India\Web\Partial Run\act-jnssav-7544\data\Excels'

    if os.path.exists(source):
        if not os.path.exists(destination):
            os.makedirs(destination,exist_ok=True)

        cmd = f'robocopy "{source}" "{destination}" /E /MOVE /MT:128 /R:3 /W:5 /LOG:move_log.txt'

        subprocess.run(cmd, shell=True)

    if source_excel and destination_excel:
        if os.path.exists(source_excel):
            if not os.path.exists(destination_excel):
                os.mkdir(destination_excel)
            shutil.copy2(source_excel, destination_excel)

def get_data_for_gsheet():

    dateTime = fetchDateTime()
    with makeConn() as conn:
        qr = f"SELECT * FROM products_{dateTime}"
        df = pd.read_sql(qr, conn)
        data_count = len(df)

    file_count = 0
    folders = [rf'\\172.28.151.201\temp-storage\SynologyBackup\Q-Comm\Flipkart_Grocery\India\Web\Partial Run\act-jnssav-7544\data\Html\pagesaves {datetime.now().strftime("%Y-%m-%d")}']
    for folder_path in folders:
        for root, dirs, files in os.walk(folder_path):
            if root != folder_path:
                break
            if not dirs:
                break
            for folder in dirs:
                folder_full_path = os.path.join(root, folder)
                file_count += sum([len(files) for _, _, files in os.walk(folder_full_path)])
    return data_count, file_count

# def append_gsheet():

#     data_count, request_count = get_data_for_gsheet()

#     url = "http://172.27.132.182:7000/append-data"

#     run_time = fetchDateTime()
#     run_time = run_time.split("_")[-1]
#     if run_time == "10AM":
#         run_time = "10:00"
#     else:
#         run_time = "22:00"

#     payload = json.dumps({
#         "sheet_name": "KS-003120",
#         "project_code": "KS-003120",
#         "project_name": "Blinkit Avocado",
#         "domain": "Blinkit",
#         "date": f"{datetime.today().strftime('%Y-%m-%d')}",
#         # "date": f"2026-03-30",
#         "time": f"{run_time}",
#         "data_count": data_count,
#         "request_count": request_count,
#         "developer_name": "Manav Mehta"
#     })
#     headers = {
#         'Content-Type': 'application/json'
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)

#     print(response.text)





def upload_to_nexus():
    run_time = fetchDateTime()
    # run_time = run_time.split("_")[-1]
    # if run_time == "10AM":
    #     batch = 1
    # else:
    #     batch = 2

    destination_html = rf"\\172.28.151.201\temp-storage\SynologyBackup\Q-Comm\Flipkart_Grocery\India\Web\Partial Run\act-jnssav-7544\data\Html\pagesaves {datetime.now().strftime('%Y-%m-%d')}"
    destination_file = rf"\\172.28.151.201\temp-storage\SynologyBackup\Q-Comm\Flipkart_Grocery\India\Web\Partial Run\act-jnssav-7544\data\Excels\Flipkart_Grocery_{fetchDateTime()}.xlsx"

    data_count, request_count = get_data_for_gsheet()

    feed_id = "1733"
    project_code = "ACT-JNSSAV-7544"
    file_path = destination_file
    html_path = destination_html
    remark = "Please QA this file"
    data_count = data_count
    user_key = "?{*qclHmh?lKsk^H"
    batch = 1
    date = datetime.today().strftime("%Y-%m-%d")

    url = "http://172.28.161.32:5005/api/assign-to-qa"

    payload = json.dumps({
        "feed_id": feed_id,
        "project_code": project_code,
        "file_path": file_path,
        "html_path": html_path,
        "remark": remark,
        "data_count": data_count,
        "user_key": user_key,
        "batch": batch,
        "date": date
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    print(response.status_code)

def main():
    with makeConn() as conn:
        with conn.cursor() as curr:
            curr.execute("UPDATE pincodes SET status='pending'")
            conn.commit()
    
    # runMain()   
    exportMain()
    movePagesaves()
    # upload_to_nexus()
    # append_gsheet()

if __name__ == '__main__':
    main()