from datetime import datetime
from curl_cffi import requests
import json
import os
import gzip


headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://www.flipkart.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.flipkart.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'X-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36 FKUA/website/41/website/Desktop',
    'flipkart_secure': 'true',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'T=TI177925521412100104176139679411356012510746827392241186387225372910; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFkOTYzYzUwLTM0YjctNDA1OC1iMTNmLWY2NDhiODFjYTBkYSJ9.eyJleHAiOjE3ODA5ODMyMTQsImlhdCI6MTc3OTI1NTIxNCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTg4NmU1MTktYWIzMi00MTkxLTgyZjktMTBiODc2OTlkZTVkIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzc5MjU1MjE0MTIxMDAxMDQxNzYxMzk2Nzk0MTEzNTYwMTI1MTA3NDY4MjczOTIyNDExODYzODcyMjUzNzI5MTAiLCJrZXZJZCI6IlZJNTRFNjIxRjAxNDVBNDYxOEEzNDk4N0YxNTUzQjM0MTkiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjN9.8a0JGUPMCnFGpIjOL8tgK-4mgL7x15ot-jlS-pCpiNM; K-ACTION=null; vh=307; vw=1707; dpr=1.125; vd=VI54E621F0145A4618A34987F1553B3419-1779255215712-1.1779255215.1779255215.149018313; ud=5.C-qjxZfTgyj7ggjhZvArzoBhiDLOcLLJccB94sOzGCDCgckkEYyIFlxgVB98FVTNm3X3eGORImWu41IucuZbsJyEOQW3dFpHBNpqJp2YAxUgVBS3DYsCvb8j6B3vfloP_pjFNsVm2PljHBJLRDH_Xw; S=d1t16P1s/Pww/Pz8/PzBwIz8uP3MCquIIg0vXPJDiU0WDac8XShveT+o3YNUEflf0oWabEmXXzphxriZKZMHn9WX6zw==; SN=VI54E621F0145A4618A34987F1553B3419.TOKF8FD4851F4F345509802650408DB6982.1779255226822.LO',
}
def get_update_ud(address_info):

    os.makedirs(f'pagesaves/pagesaves {datetime.now().strftime("%Y-%m-%d")}/update', exist_ok=True)

    json_data = {
        'geoLocation': {
            'latitude': address_info.get('latitude'),
            'longitude': address_info.get('longitude'),
        },
        'addressInfo': {
            'addressLine1': address_info.get('formatted_address', ''),
            # 'city': 'Ahmedabad',
            # 'state': 'Gujarat',
            'pincode': str(address_info.get('pincode', '')),
        },
        'redirectionUrl': '',
        'marketplace': 'GROCERY',
    }
   
    response = requests.post('https://2.rome.api.flipkart.com/api/4/location/update',  headers=headers, json=json_data)
    if response.status_code == 200:
        headers_dict = dict(response.headers)
        cookie = headers_dict.get("set-cookie", "")
        if cookie:
            try:
                ud=cookie.split('ud=')[1].split(';')[0]
                
                with gzip.open(f'pagesaves/pagesaves {datetime.now().strftime("%Y-%m-%d")}/update/{address_info.get("pincode")}.html.gz', 'wt', encoding='utf-8') as f:
                    json.dump(headers_dict, f, indent=2, ensure_ascii=False)
                return ud
            except IndexError:
                print("UD not found in cookie")
                return None
    else:
        print(f"UPDATE Request failed with status code : {response.status_code}")
        return None