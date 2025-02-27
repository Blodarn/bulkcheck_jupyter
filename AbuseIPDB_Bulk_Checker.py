import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import pandas as pd

def fetch_ip_data(ip, api_key):
    try:
        response = requests.get(
            f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}",
            headers={'Accept': 'application/json', 'Key': api_key}
        )
        if response.status_code == 200:
            return ip, response.json()
        else:
            print(f"{ip} is not a valid IP!")
            return ip, None
    except Exception as e:
        print(f"Error fetching {ip}: {e}")
        return ip, None

def bulk_check_from_input(api_key):
    ip_input = input("Enter IP addresses (separated by commas, spaces, or on separate lines) and press ENTER:\n")
    # Split on both spaces and new lines to accommodate input from Excel or manual entry
    ips = [ip.strip() for ip in ip_input.replace(",", " ").replace("\n", " ").split() if ip.strip()]

    start_time = time.time()
    
    print(f"🔍 Started check of {len(ips)} IPs at {time.strftime('%b %d %H:%M:%S', time.localtime(start_time))}")
    
    results = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_ip_data, ip, api_key): ip for ip in ips}

        with tqdm(total=len(ips), desc="Processing IPs") as pbar:
            for future in as_completed(futures):
                ip, data = future.result()
                if data:
                    data = data["data"]
                    results.append([
                        data["ipAddress"], data["abuseConfidenceScore"],
                        data["isp"], data["domain"],
                        data["countryCode"], data["totalReports"],
                        data["lastReportedAt"]
                    ])
                pbar.update(1)

    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_minutes, elapsed_seconds = divmod(elapsed_time, 60)
    avg_time_per_ip = round(elapsed_time / len(ips), 1) if len(ips) > 0 else 0

    print(f"✅ Completed check at {time.strftime('%b %d %H:%M:%S', time.localtime(end_time))}")
    print(f"⏱ Time elapsed was {int(elapsed_minutes)} minutes and {elapsed_seconds:.1f} seconds")
    print(f"⏱ Average time per IP checked was {avg_time_per_ip} seconds")
    
    # Display results as a pandas DataFrame
    df = pd.DataFrame(results, columns=["ipAddress", "abuseConfidenceScore", "isp", "domain", "countryCode", "totalReports", "lastReportedAt"])
    return df

api_key = 'api_key'  # You need to provide your AbuseIPDB API key

# Call the function and display the table
result_df = bulk_check_from_input(api_key)
result_df
