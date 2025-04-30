import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

proxies_list = [
    {"http": "156.228.84.160:3128", "https": "156.228.84.160:3128"},
    # {"http": "http://192.241.138.166:80", "https": "http://192.241.138.166:80"},
    # {"http": "http://49.51.232.92:13001", "https": "http://49.51.232.92:13001"},
    # {"http": "http://49.51.207.125:13001", "https": "http://49.51.207.125:13001"},
    # {"http": "http://43.130.9.63:13001", "https": "http://43.130.9.63:13001"},
    # {"http": "http://188.68.52.244:80", "https": "http://188.68.52.244:80"},
    # {"http": "http://43.153.21.13:13001", "https": "http://43.153.21.13:13001"},
    # {"http": "http://185.105.102.179:80", "https": "http://185.105.102.179:80"},
    # {"http": "http://161.35.70.249:80", "https": "http://161.35.70.249:80"},
    # {"http": "http://185.26.201.73:8080", "https": "http://185.26.201.73:8080"},
    # {"http": "http://45.140.143.77:18080", "https": "http://45.140.143.77:18080"},
]

# Test URLs
initial_test_url = "http://httpbin.org/ip"  # Simpler URL to confirm proxy functionality
target_url = "https://internshala.com/internships"

# Set up retry strategy
session = requests.Session()
retries = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))

valid_proxies = []

for i, proxy in enumerate(proxies_list, 1):
    try:
        print(f"\nTesting Proxy {i}: {proxy['http']}")

        # Step 1: Test with a simple URL to confirm proxy is functional
        start_time = time.time()
        initial_response = session.get(
            initial_test_url, proxies=proxy, timeout=15, verify=False
        )
        initial_time = time.time() - start_time

        if initial_response.status_code == 200:
            print(f"Initial Test SUCCESS (Response Time: {initial_time:.2f}s)")

            # Step 2: Test with Internshala
            start_time = time.time()
            response = session.get(target_url, proxies=proxy, timeout=15, verify=False)
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                print(f"Internshala Test SUCCESS (Response Time: {elapsed_time:.2f}s)")
                valid_proxies.append(proxy["http"])
            else:
                print(
                    f"Internshala Test FAILED (Status: {response.status_code}, Time: {elapsed_time:.2f}s)"
                )
        else:
            print(
                f"Initial Test FAILED (Status: {initial_response.status_code}, Time: {initial_time:.2f}s)"
            )
    except Exception as e:
        print(f"ERROR ({str(e)})")
    time.sleep(2)  # Polite delay between tests

# Save valid proxies to proxies.txt
with open("proxies.txt", "w") as f:
    for proxy in valid_proxies:
        f.write(f"{proxy}\n")
print(f"\nSaved {len(valid_proxies)} valid proxies to proxies.txt")
