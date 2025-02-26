# Original Admiral SYN-ACKbar's AbuseIPDB Bulk Checker (https://github.com/AdmiralSYN-ACKbar/AbuseIPDB-Bulk-Checker)

#############
# FIRST BLOCK
#############
import csv
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Import the tqdm library

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

def bulk_check(csv_filename, api_key, export_filename):
    start_time = time.time()
    
    with open(csv_filename, 'r') as file, open(export_filename, 'w', newline='') as csv_file:
        csv_reader = csv.reader(file)
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["ipAddress", "abuseConfidenceScore", "isp", "domain", "countryCode", "totalReports", "lastReportedAt"])

        total_rows = sum(1 for _ in csv_reader)
        file.seek(0)

        print(f"🔍 Started check of {total_rows} IPs at {time.strftime('%b %d %H:%M:%S', time.localtime(start_time))}")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_ip_data, row[0], api_key): row[0] for row in csv_reader}

            with tqdm(total=total_rows, desc="Processing IPs") as pbar:
                for future in as_completed(futures):
                    ip, data = future.result()
                    if data:
                        data = data["data"]
                        csv_writer.writerow([
                            data["ipAddress"], data["abuseConfidenceScore"],
                            data["isp"], data["domain"],
                            data["countryCode"], data["totalReports"],
                            data["lastReportedAt"]
                        ])
                    pbar.update(1)

    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_minutes, elapsed_seconds = divmod(elapsed_time, 60)
    avg_time_per_ip = round(elapsed_time / total_rows, 1) if total_rows > 0 else 0

    print(f"✅ Completed check at {time.strftime('%b %d %H:%M:%S', time.localtime(end_time))}")
    print(f"⏱ Time elapsed was {int(elapsed_minutes)} minutes and {elapsed_seconds:.1f} seconds")
    print(f"⏱ Average time per IP checked was {avg_time_per_ip} seconds")

###########
# 2ND BLOCK
###########
api_key = 'your_api_key'  # You need to provide your AbuseIPDB API key
csv_filename = 'ip.csv'     # CSV file with IPs, should be in the same directory as this notebook
export_filename = 'output.csv' # Export CSV file, will also be in the same directory

bulk_check(csv_filename, api_key, export_filename)
