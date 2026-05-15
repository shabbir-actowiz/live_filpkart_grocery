import asyncio
import aiohttp
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import sys

# ========================= CONFIG =========================
API_KEY = "AIzaSyAtKsoYaqKOXMV00f9qLDAgbYYevlxAGsQ"
PLACE_ID = "ChIJN1t_tDeuEmsRUsoyG83frY4"   # Sydney Opera House

TOTAL_REQUESTS = 50000
CONCURRENT_WORKERS = 100          # Adjust this (30-80 is safe)
# =========================================================

success_count = 0
error_count = 0
rate_limit_count = 0
start_time = None

async def make_request(session, request_id):
    global success_count, error_count, rate_limit_count
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": PLACE_ID,
        "key": API_KEY,
        "fields": "name,formatted_address,geometry,rating,formatted_phone_number,website"
    }

    try:
        async with session.get(url, params=params, timeout=10) as response:
            status = response.status
            text = await response.text()
            print(f"📡 [{request_id:5d}] HTTP {status}")
            if status == 200:
                data = json.loads(text)
                if data.get("status") == "OK":
                    success_count += 1
                    if request_id % 500 == 0:   # Log every 500 requests
                        print(f"✅ [{request_id:5d}] Success | Status: OK")
                else:
                    error_count += 1
                    print(f"⚠️  [{request_id:5d}] API Error: {data.get('status')}")
            elif status == 429:
                rate_limit_count += 1
                print(f"⛔ [{request_id:5d}] RATE LIMITED (429)")
            else:
                error_count += 1
                print(f"❌ [{request_id:5d}] HTTP {status}")
                
    except asyncio.TimeoutError:
        error_count += 1
        print(f"⏱️  [{request_id:5d}] Timeout")
    except Exception as e:
        error_count += 1
        print(f"🔥 [{request_id:5d}] Exception: {type(e).__name__}")


async def main():
    global start_time
    start_time = time.time()
    
    print(f"🚀 Starting Load Test: {TOTAL_REQUESTS} requests | Concurrency: {CONCURRENT_WORKERS}\n")
    print("="*80)

    connector = aiohttp.TCPConnector(limit=CONCURRENT_WORKERS, limit_per_host=CONCURRENT_WORKERS)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(TOTAL_REQUESTS):
            task = asyncio.create_task(make_request(session, i+1))
            tasks.append(task)
            
            # Control concurrency
            if len(tasks) >= CONCURRENT_WORKERS:
                await asyncio.gather(*tasks)
                tasks = []
        
        # Run remaining tasks
        if tasks:
            await asyncio.gather(*tasks)

    # Final Report
    end_time = time.time()
    duration = end_time - start_time
    requests_per_second = TOTAL_REQUESTS / duration if duration > 0 else 0

    print("\n" + "="*80)
    print("🏁 LOAD TEST COMPLETED")
    print("="*80)
    print(f"Total Requests     : {TOTAL_REQUESTS:,}")
    print(f"Successful         : {success_count:,}")
    print(f"Errors             : {error_count:,}")
    print(f"Rate Limited (429) : {rate_limit_count:,}")
    print(f"Duration           : {duration:.2f} seconds")
    print(f"Requests/sec       : {requests_per_second:.2f}")
    print(f"API Key Used       : {API_KEY[:15]}...")
    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user.")
    except Exception as e:
        print(f"\n💥 Critical Error: {e}")