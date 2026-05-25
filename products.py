from parser import *
import os
import json
from db import *
from curl_cffi import requests
import gzip
from datetime import datetime
BATCH_SIZE = 100



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
    'X-User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 FKUA/msite/0.0.4/msite/Mobile',
    'flipkart_secure': 'true',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'T=TI177365037834400268559257852189663951613045103649178426782120501420; vw=1280; dpr=1.5; K-ACTION=null; rt=null; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFkOTYzYzUwLTM0YjctNDA1OC1iMTNmLWY2NDhiODFjYTBkYSJ9.eyJleHAiOjE3Nzk3MDY3NzUsImlhdCI6MTc3Nzk3ODc3NSwiaXNzIjoia2V2bGFyIiwianRpIjoiNTUzZTkyYzMtNThiZS00NTg2LWFkMzQtMDBhYWExYTlhMWFkIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzczNjUwMzc4MzQ0MDAyNjg1NTkyNTc4NTIxODk2NjM5NTE2MTMwNDUxMDM2NDkxNzg0MjY3ODIxMjA1MDE0MjAiLCJrZXZJZCI6IlZJNjgwMzQ4QjY3RDhDNDA0RkJGMjBGOUUyRkNCODMyREUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjN9.z9KgTJ4GsgIN7HjAq6rAFm4LF-y0S73CGA7gukAA9AQ; AMCVS_17EB401053DAF4840A490D4C%40AdobeOrg=1; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C20588%7CMCMID%7C59857464694264040971777249017038482341%7CMCAAMLH-1779363817%7C12%7CMCAAMB-1779363817%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1778766217s%7CNONE%7CMCAID%7CNONE; vh=632; _gcl_au=1.1.1672431933.1778833736; Network-Type=4g; vd=VI680348B67D8C404FBF20F9E2FCB832DE-1773651250989-10.1778839435.1778838907.159393798; ud=2.YOKqx9JHMp80DdNjUKLH8dYhT9qvEUXz7P6qk15O9jTPG3vyW2cD94-O1W8ptUbk6C5X75Xwn4tY1DV_59l6HXaLywHhuWKbXtQyQG9uQtxq5NrzDf4JkuAeo-yufqzGGkJjreKH2g7j1e308WzZiHthKrCQIcR3_V60ztaSRvTXpH-iX1Lw9uifxjztIrp_K1J_S2rCw2F0vsdrmrfKRUj8RHPRhHWN8ZBEZ0fnWguwHKi2toGjnULaqKkfGMk4Y2uRdx7S9L2SWvbZ34jB8r55sJGIDvSG7sBsZrnuF2QUxUaEKONEEyOzYjWimKLVtZN2-YoophHGPU4GtqMh2HhFs05dT9knjGKFYuZdt6qFmv4TVGh4SiSrV9z1vdKnt2fm7Jm_7uOV0hfNNuSfG8DTQoQJQ60zO9GiqMwK6xo; s_sq=flipkart-prd%3D%2526pid%253Dwww.flipkart.com%25253Asearch%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.flipkart.com%25252Fclassic-chana-dal-besan-flipkart-grocery%25252Fp%25252Fitm7b7ac8fcd5f19%25253Fpid%25253DFLRGRFDXUZY%2526ot%253DA; S=d1t15aj8KPzY/Pz8/JSVQeUU2QDGQIVEaK+2Bf96nlE06LUg7m9UTvFWk28Cl3+Nnh+MWpHPsU3HRvWoLbKhD1Tp3uw==; SN=VI680348B67D8C404FBF20F9E2FCB832DE.TOKC15D7C138D064C169DAA6BEA12F7F0F5.1778839462499.LO',
}

params = {
    'cacheFirst': 'false',
}





def get_product(product_urls, location_data):
    batch=[]

    os.makedirs(f'pagesaves {datetime.now().strftime("%Y-%m-%d")}/pdp', exist_ok=True)
    os.makedirs(f'pagesaves {datetime.now().strftime("%Y-%m-%d")}/parsed', exist_ok=True)

    for product_url in product_urls:
        cookies = {
            'T': 'TI177365037834400268559257852189663951613045103649178426782120501420',
            # 'vw': '1280',
            # 'dpr': '1.5',
            # 'K-ACTION': 'null',
            # 'rt': 'null',
            # 'at': location_data.get('at'),
            # 'AMCVS_17EB401053DAF4840A490D4C%40AdobeOrg': '1',
            # 'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C20588%7CMCMID%7C59857464694264040971777249017038482341%7CMCAAMLH-1779363817%7C12%7CMCAAMB-1779363817%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1778766217s%7CNONE%7CMCAID%7CNONE',
            # 'vh': '632',
            # '_gcl_au': '1.1.1672431933.1778833736',
            # 'Network-Type': '4g',
            # 'vd': 'VI680348B67D8C404FBF20F9E2FCB832DE-1773651250989-10.1778839435.1778838907.159393798',
            'ud': location_data.get('ud'),
            # 's_sq': 'flipkart-prd%3D%2526pid%253Dwww.flipkart.com%25253Asearch%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.flipkart.com%25252Fclassic-chana-dal-besan-flipkart-grocery%25252Fp%25252Fitm7b7ac8fcd5f19%25253Fpid%25253DFLRGRFDXUZY%2526ot%253DA',
            # 'S': 'd1t15aj8KPzY/Pz8/JSVQeUU2QDGQIVEaK+2Bf96nlE06LUg7m9UTvFWk28Cl3+Nnh+MWpHPsU3HRvWoLbKhD1Tp3uw==',
            # 'SN': location_data.get('sn'),
        }
        json_data = {
            'pageUri': product_url,
            'pageContext': {
                'trackingContext': {
                    'context': {
                        'eVar61': 'direct_product',
                    },
                },
                'networkSpeed': 10000,
            },
            'locationContext': {
                'pincode': int(location_data['pincode']),
                'changed': False,
            },
        }
        response = requests.post(
            'https://2.rome.api.flipkart.com/api/4/page/fetch',
            params=params,
            cookies=cookies,
            headers=headers,
            json=json_data,
            impersonate='chrome116'
        )
        pid=product_url.split('pid=')[1].split('&')[0]
        with gzip.open(f'pagesaves {datetime.now().strftime("%Y-%m-%d")}/pdp/{pid}_{location_data["pincode"]}.html.gz', 'wt', encoding='utf-8') as file:
                    json.dump(response.json(), file, indent=2,ensure_ascii=False)

        if response.status_code == 200:
            print(f"Successfully fetched product data for {product_url}")
            product_json = response.json()
            
            cleaned_data = extract_product_data(product_json, location_data, product_url)

            if type(cleaned_data) == dict:
                batch.append(cleaned_data)
            else:
                print(f"Parser failed for: {product_url}")
                return 'not found'

            # with gzip.open(f'pagesaves {datetime.now().strftime("%Y-%m-%d")}/parsed/{pid}_{location_data["pincode"]}.html.gz', 'wt', encoding='utf-8') as file:
            #         json.dump(cleaned_data, file, indent=2, ensure_ascii=False)

            if len(batch)>=BATCH_SIZE:
                insert_multiple_data(batch)
                batch=[]

        else:
            print(f"Failed to fetch product data for {product_url}. Status code: {response.status_code}")
            return 'failed'
        
    if batch:
        insert_multiple_data(batch)
        batch=[]
    return True