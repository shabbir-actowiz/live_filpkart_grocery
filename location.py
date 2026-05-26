from curl_cffi import requests
import json
import os
import gzip
from update import *
from datetime import datetime
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
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
    'X-User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 FKUA/website/42/website/Desktop',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'T=TI177193051592500108100310423094531036956455118585140618128981427018; K-ACTION=null; vw=1920; dpr=1; rt=null; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3ODA0MDgwODUsImlhdCI6MTc3ODY4MDA4NSwiaXNzIjoia2V2bGFyIiwianRpIjoiZjViZTUwN2QtNGYzOS00MWY2LWEzMDUtN2JkMTNjNmI0ZjE0IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzcxOTMwNTE1OTI1MDAxMDgxMDAzMTA0MjMwOTQ1MzEwMzY5NTY0NTUxMTg1ODUxNDA2MTgxMjg5ODE0MjcwMTgiLCJrZXZJZCI6IlZJODUxNDA5NTAzQ0JENEU3Mjg2NjlEM0NBNTNDM0M1MzYiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjN9.gjHorXUKvhXZoCLWaUBITiLOQQtqh5x6DdPfXTBSJc8; Network-Type=4g; vh=945; vd=VI851409503CBD4E728669D3CA53C3C536-1771930519700-4.1778834267.1778832559.151541542; AMCVS_17EB401053DAF4840A490D4C%40AdobeOrg=1; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C20589%7CMCMID%7C10799054206039868633353306468551813230%7CMCAAMLH-1779284966%7C12%7CMCAAMB-1779439077%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1778841477s%7CNONE%7CMCAID%7CNONE; ud=1.Sf6wmi1txOQ-py5AqyL1KkuWvkCW7BYMhaBZfS7fpwCFpH1CBhxS1LMIkrOaIh1ZN1ScJMipEVN0HmHr5UxcykNKWK7fre7FpUqcPf92Qu6GjDw2lT1q2BuQANWV45vSkW35BWFGsZEYl84Y9c6JDTUnLITVYJChBMP57iBGLL9mlvjtnFf-RpXj__SVE3O9dxDesLoWldhqiFY5QVWNH7AdNK1IDADdzHcG5vAUK4v4TpA5jrzLdmxOWhonKj_z5O8yeuU5eczn7s7Adgjkc7gYheq6LPXTq_mA7cX6xHoffufqIW4nCJSGIxSRj_jptktoNBz3t7ohjOOUGsMxWwHRbiEeoWimFsOQXR-CB7XPF65A9EkPr4qPLsrLPG_8J01FUdjSmz644zwckpIcibb6IhCoTNHylHam9VWhUdIuMFIihwikYcQuCWlUKXmxVM4dj1uehCmRq5apFtOq3REpZTs6QUiRMtgo8HNCjkmTUjPCvx6Wbaa3FMQyf6AFj5tu_sni9szyHKlTKOQWXoejltWbzbOkuO4xkjB9fDzZglmje9Dn5tozrfs6ZYEz; S=d1t16Gz8aWD8/anAyYiwyNT0/TzRAU/AeXTHiw3cVRj3gvT7xN2HOTfrh3DzhgKi/gjLnfNRnjVZEMBeixS2kfo8IYw==; SN=VI851409503CBD4E728669D3CA53C3C536.TOKEF07EFC0D5F94172903F98FD3018A662.1778834284277.LO; s_sq=flipkart-prd%3D%2526pid%253Dwww.flipkart.com%25253Asearch%2526pidt%253D1%2526oid%253DfunctionJr%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DDIV; S=d1t16Pz9dPz8/Tj8/Aj8/PzYuP5WDwsd+LWTvRU9YdcrCkC2YNeckmdIN3XA47lhxPfVfyFtIEgkHj+PQe56IDMgEDw==; SN=VI851409503CBD4E728669D3CA53C3C536.TOKFD9A0F4C80014012BEB90ED41C6425BC.1778834498493.LO; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3ODA0MDgwODUsImlhdCI6MTc3ODY4MDA4NSwiaXNzIjoia2V2bGFyIiwianRpIjoiZjViZTUwN2QtNGYzOS00MWY2LWEzMDUtN2JkMTNjNmI0ZjE0IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzcxOTMwNTE1OTI1MDAxMDgxMDAzMTA0MjMwOTQ1MzEwMzY5NTY0NTUxMTg1ODUxNDA2MTgxMjg5ODE0MjcwMTgiLCJrZXZJZCI6IlZJODUxNDA5NTAzQ0JENEU3Mjg2NjlEM0NBNTNDM0M1MzYiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjN9.gjHorXUKvhXZoCLWaUBITiLOQQtqh5x6DdPfXTBSJc8; rt=null; ud=1.Sf6wmi1txOQ-py5AqyL1KkuWvkCW7BYMhaBZfS7fpwCFpH1CBhxS1LMIkrOaIh1ZN1ScJMipEVN0HmHr5UxcykNKWK7fre7FpUqcPf92Qu6GjDw2lT1q2BuQANWV45vSkW35BWFGsZEYl84Y9c6JDTUnLITVYJChBMP57iBGLL9mlvjtnFf-RpXj__SVE3O9dxDesLoWldhqiFY5QVWNH7AdNK1IDADdzHcG5vAUK4v4TpA5jrzLdmxOWhonKj_z5O8yeuU5eczn7s7Adgjkc7gYheq6LPXTq_mA7cX6xHoffufqIW4nCJSGIxSRj_jptktoNBz3t7ohjOOUGsMxWwHRbiEeoWimFsOQXR-CB7XPF65A9EkPr4qPLsrLPG_8J01FUdjSmz644zwckpIcibb6IhCoTNHylHam9VWhUdIuMFIihwikYcQuCWlUKXmxVM4dj1uehCmRq5apFtOq3REpZTs6QUiRMtgo8HNCjkmTUjPCvx6Wbaa3FMQyf6AFj5tu_sni9szyHKlTKOQWXoejltWbzbOkuO4xkjB9fDzZglmje9Dn5tozrfs6ZYEz; vd=VI851409503CBD4E728669D3CA53C3C536-1771930519700-4.1778834498.1778832559.151623471',
}

json_data = {
    'locationContext': {
        'pincode': '',
    },
    'marketplaceContext': {
        'marketplace': 'GROCERY',
    },
}

def get_serviceability(pincode):

    os.makedirs(f'pagesaves/pagesaves {datetime.now().strftime("%Y-%m-%d")}/serviceability', exist_ok=True)

    json_data['locationContext']['pincode'] = str(pincode)

    response = requests.post(
        'https://2.rome.api.flipkart.com/api/3/marketplace/serviceability',
        # cookies=cookies,
        headers=headers,
        json=json_data,
    impersonate='chrome116'
    )
    
    with gzip.open(f'pagesaves/pagesaves {datetime.now().strftime("%Y-%m-%d")}/serviceability/{pincode}.html.gz', 'wt', encoding='utf-8') as f:
            json.dump(response.json(), f, indent=2,ensure_ascii=False)

    if response.status_code == 200:

        data=response.json()

        if data.get('RESPONSE', {}).get('serviceability'):

            print(f"Pincode {pincode} is serviceable.")
            
            location_data=get_lat_long_from_pincode(pincode)
            if location_data == 'not found':
                print(f"Location data not found for pincode {pincode}.")
                return None
            ud=get_update_ud(location_data)
            location_data['ud']=ud

            return location_data
        else:
            print(f"Pincode {pincode} is not serviceable.")
            return None
        
    else:
        print(f"Failed to check serviceability for pincode {pincode}. Status code: {response.status_code}")
        return 'failed'
    
def get_lat_long_from_pincode(pincode, country="India"):
    
    os.makedirs(f'pagesaves/pagesaves {datetime.now().strftime("%Y-%m-%d")}/location_data', exist_ok=True)
    api_key = "AIzaSyAtKsoYaqKOXMV00f9qLDAgbYYevlxAGsQ"  # Replace with your actual API key
    
    # Format the address with pincode and country
    address = f"{pincode}, {country}"
    
    params = {
        'address': address,
        'key': api_key,
        'components':f"country:IN|postal_code:{pincode}", # Optional: restrict to postal code
        "region": "in"
    }
    
    response = requests.get(
        'https://maps.googleapis.com/maps/api/geocode/json',
        params=params
    )

    data = response.json()

    if not data['results']:
        return 'not found'
    
    if data['status'] == 'OK':

        location = data['results'][0]['geometry']['location']

        with gzip.open(f'pagesaves/pagesaves {datetime.now().strftime("%Y-%m-%d")}/location_data/{pincode}.html.gz', 'wt',encoding='utf-8') as f:
            json.dump(data, f, indent=2,ensure_ascii=False)
        result = data["results"][0]
        address_components = result["address_components"]
        city = None
        state = None
        pincode_extracted = None
        formatted_address = result.get("formatted_address")
        for component in address_components:
            types = component["types"]
            
            if "locality" in types and not city:                    # City / Town
                city = component["long_name"]
            
            elif "administrative_area_level_1" in types:            # State
                state = component["long_name"]
            
            elif "postal_code" in types:                            # Pincode
                pincode_extracted = component["long_name"]

        # Fallbacks
        if not city:
            # Try administrative_area_level_2 or sublocality as city
            for component in address_components:
                if "administrative_area_level_2" in component["types"]:
                    city = component["long_name"]
                    break
        
        if not city or not state :
            city,state,formatted_address = get_city_state_from_lat_lng(location['lat'], location['lng'],api_key)

        return {
            'latitude': location['lat'],
            'longitude': location['lng'],
            'formatted_address': formatted_address,
            'city': city,
            'state': state,
            'pincode': pincode_extracted
        }
    
    else:
        return {'error': data['status']}

def get_city_state_from_lat_lng(lat, lng, api_key):
    os.makedirs(f'pagesaves/pagesaves {datetime.now().strftime("%Y-%m-%d")}/reverse_geocode', exist_ok=True)
    
    reverse_params = {
        "latlng": f"{lat},{lng}",
        "key": api_key
    }

    reverse_resp = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params=reverse_params
    )
    with gzip.open(f'pagesaves/pagesaves {datetime.now().strftime("%Y-%m-%d")}/reverse_geocode/{lat}_{lng}.html.gz', 'wt', encoding='utf-8') as f:
        json.dump(reverse_resp.json(), f, indent=2, ensure_ascii=False)
    reverse_data = reverse_resp.json()


    for result in reverse_data.get("results", []):

        for comp in result.get("address_components", []):

            types = comp.get("types", [])

            # State
            if "administrative_area_level_1" in types:
                state = comp.get("long_name")

            # City
            if "locality" in types :
                city = comp.get("long_name")

            # Backup city
            if (
                "administrative_area_level_2" in types
                and not city
            ):
                city = comp.get("long_name")

    formatted_address = reverse_data.get("plus_code",{}).get("compound_code")

    return city, state, formatted_address