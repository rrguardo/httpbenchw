import requests
import time
import statistics
from multiprocessing import Pool, Manager
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='HTTP Load Testing Tool')
parser.add_argument('--url', type=str, default='', help='Target URL to test')
parser.add_argument('--proxy-ip', type=str, default='127.0.0.1', help='Proxy IP address')
parser.add_argument('--proxy-port', type=int, default=8080, help='Proxy port number')
parser.add_argument('--proxy-user', type=str, default='', help='Proxy username')
parser.add_argument('--proxy-pass', type=str, default='', help='Proxy password')
parser.add_argument('--use-proxy', type=bool, default=False, help='Use proxy (True/False)')
parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
parser.add_argument('--host-header', type=str, default='', help='Host header value')
parser.add_argument('--process-count', type=int, default=2, help='Number of processes to use')
parser.add_argument('--test-duration', type=int, default=5, help='Test duration in seconds')

args = parser.parse_args()

# Global URL variable
TARGET_URL = args.url

# Global proxy info
PROXY_IP = args.proxy_ip
PROXY_PORT = args.proxy_port
PROXY_USER = args.proxy_user
PROXY_PASS = args.proxy_pass

# Global settings
USE_PROXY = args.use_proxy
TIMEOUT = args.timeout
HOST_HEADER = args.host_header

PROCESS_COUNT = args.process_count
TEST_DURATION = args.test_duration

# Proxy with authentication
if PROXY_USER and PROXY_PASS:
    proxies = {
        'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}',
        'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}'
    }
else:
    proxies = {
        'http': f'http://{PROXY_IP}:{PROXY_PORT}',
        'https': f'http://{PROXY_IP}:{PROXY_PORT}'
    }


def run_benchmark_process(process_id, shared_stats):
    """
    Run benchmark test in a separate process

    Args:
        process_id (int): Identifier for the process
        shared_stats (dict): Shared dictionary to store statistics
    """
    # Initialize lists to store performance metrics
    request_times = []
    status_codes = []
    error_count = 0

    # Run benchmark for TEST_DURATION seconds
    start_time = time.time()
    end_time = start_time + TEST_DURATION

    while time.time() < end_time:
        try:
            # Record start time of request
            start_request = time.time()

            # Prepare request headers
            headers = {'Host': HOST_HEADER} if HOST_HEADER else {}

            # Select proxies based on USE_PROXY flag
            request_proxies = proxies if USE_PROXY else None

            # Make HTTP GET request
            response = requests.get(TARGET_URL, proxies=request_proxies, timeout=TIMEOUT, headers=headers)

            # Record end time of request
            end_request = time.time()

            # Store timing and status code
            request_times.append(end_request - start_request)
            status_codes.append(response.status_code)

        except requests.exceptions.Timeout:
            # Handle timeout specifically
            error_count += 1
            print(f"Process {process_id}: Request timed out after {TIMEOUT}s")

        except requests.RequestException as e:
            # Increment error count if request fails
            error_count += 1
            print(f"Process {process_id}: Request failed with error: {e}")

        # Store results in shared memory
    with shared_stats['lock']:
        shared_stats['request_times'].extend(request_times)
        shared_stats['status_codes'].extend(status_codes)
        shared_stats['error_count'] += error_count


def main():
    """
    Main function to execute the load testing benchmark
    """
    num_processes = PROCESS_COUNT  # Number of processes to spawn

    with Manager() as manager:
        # Use Manager to share data between processes
        shared_stats = manager.dict()
        shared_stats['request_times'] = manager.list()
        shared_stats['status_codes'] = manager.list()
        shared_stats['error_count'] = 0
        shared_stats['lock'] = manager.Lock()

        # Create and start processes
        processes = []
        for i in range(num_processes):
            p = Pool(processes=1)
            p.apply_async(run_benchmark_process, args=(i, shared_stats))
            processes.append(p)

        # Wait for all processes to complete
        for p in processes:
            p.close()
            p.join()

        # Calculate and display stats
        request_times = shared_stats['request_times']
        status_codes = shared_stats['status_codes']
        error_count = shared_stats['error_count']

        if request_times:
            print("\n" + "="*50)
            print("LOAD TEST RESULTS")
            print("="*50)
            print(f"Total requests completed: {len(request_times)}")
            print(f"Test duration: {TEST_DURATION} seconds")
            print(f"Average response time: {statistics.mean(request_times):.3f}s")
            print(f"Median response time: {statistics.median(request_times):.3f}s")
            print(f"Fastest response: {min(request_times):.3f}s")
            print(f"Slowest response: {max(request_times):.3f}s")
            print("-"*30)

            # Count occurrences of each status code
            status_code_counts = {}
            for code in status_codes:
                status_code_counts[code] = status_code_counts.get(code, 0) + 1

            print("Status codes breakdown:")
            for code, count in sorted(status_code_counts.items()):
                print(f"  {code}: {count}")

            print("-"*30)
            print(f"Total errors: {error_count}")
            print(f"Requests per second (RPS): {len(request_times) / TEST_DURATION:.2f}")
            print("="*50)
        else:
            print("No successful requests completed")


if __name__ == "__main__":
    main()
