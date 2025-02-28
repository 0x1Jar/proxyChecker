#!/usr/bin/env python3
import requests
import sys
import time
import os
import csv
import json
import concurrent.futures
from urllib.parse import urlparse

def normalize_proxy_string(proxy_str):
    """Normalize proxy string to ip:port format without protocol prefix."""
    proxy_str = proxy_str.strip()
    
    # Handle URLs with http:// or https:// prefix
    if proxy_str.startswith(('http://', 'https://')):
        parsed = urlparse(proxy_str)
        # Extract host and port
        host = parsed.netloc
        # If netloc contains port, use it directly
        if ':' in host:
            return host
        # If no port in netloc, use default port based on scheme or 80
        else:
            default_port = '443' if parsed.scheme == 'https' else '80'
            return f"{host}:{default_port}"
    
    # If it's already in ip:port format, return as is
    return proxy_str

def check_http_proxy(proxy_str):
    """Check if an HTTP proxy is active."""
    # Normalize the proxy string
    normalized_proxy = normalize_proxy_string(proxy_str)
    
    # Parse the normalized proxy string (expected format is ip:port)
    try:
        if ':' in normalized_proxy:
            ip, port = normalized_proxy.split(':')
            port = int(port)
        else:
            return f"{proxy_str} - Invalid format. Expected ip:port or http://ip:port", False, 0
    except ValueError:
        return f"{proxy_str} - Invalid format. Expected ip:port or http://ip:port", False, 0
    
    # Format the proxy for requests library
    proxies = {
        'http': f'http://{ip}:{port}',
        'https': f'http://{ip}:{port}'
    }
    
    # Test URL - using a reliable test site
    test_url = 'http://httpbin.org/ip'
    
    try:
        # Try to connect using the proxy
        start_time = time.time()
        response = requests.get(test_url, proxies=proxies, timeout=10)
        response_time = time.time() - start_time
        
        # Check if the request was successful
        if response.status_code == 200:
            # Verify we're getting the expected response from httpbin
            json_response = response.json()
            if 'origin' in json_response:
                proxy_ip = json_response['origin']
                # If we see our proxy IP or a different IP (transparent proxy), it's working
                return f"{proxy_str} - ACTIVE (Response: {response_time:.2f}s, IP: {proxy_ip})", True, response_time
        
        return f"{proxy_str} - INACTIVE (Bad response: {response.status_code})", False, 0
    except requests.exceptions.RequestException as e:
        # If there's an exception, the proxy is not working
        return f"{proxy_str} - INACTIVE ({str(e)})", False, 0

def read_proxies_from_file(filename):
    """Read proxies from text, CSV, or JSON file."""
    proxies = []
    
    # Check file extension
    file_ext = os.path.splitext(filename)[1].lower()
    
    try:
        if file_ext == '.csv':
            with open(filename, 'r', newline='') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if row and len(row) > 0:
                        # Take the first column as the proxy
                        proxies.append(row[0].strip())
        elif file_ext == '.json':
            with open(filename, 'r') as f:
                data = json.load(f)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    # If it's a list of strings
                    if all(isinstance(item, str) for item in data):
                        proxies = [item.strip() for item in data if item.strip()]
                    # If it's a list of objects with proxy information
                    elif all(isinstance(item, dict) for item in data):
                        for item in data:
                            # Try common key names for proxy information
                            for key in ['proxy', 'ip', 'address', 'host', 'url']:
                                if key in item and isinstance(item[key], str):
                                    proxy_str = item[key].strip()
                                    # If we have a URL format or ip:port format, use it directly
                                    if proxy_str.startswith(('http://', 'https://')) or ':' in proxy_str:
                                        proxies.append(proxy_str)
                                        break
                                    # Look for port in a separate field
                                    elif 'port' in item:
                                        port = item['port']
                                        if isinstance(port, int):
                                            port = str(port)
                                        proxy_str = f"http://{proxy_str}:{port}"
                                        proxies.append(proxy_str)
                                        break
                elif isinstance(data, dict):
                    # Try to find proxy list in the dictionary
                    for key in ['proxies', 'proxy_list', 'hosts', 'servers']:
                        if key in data and isinstance(data[key], list):
                            for item in data[key]:
                                if isinstance(item, str):
                                    proxies.append(item.strip())
                                elif isinstance(item, dict):
                                    # Try to extract proxy information from the object
                                    for field in ['proxy', 'ip', 'address', 'host', 'url']:
                                        if field in item and isinstance(item[field], str):
                                            proxy_str = item[field].strip()
                                            # If we have a URL format or ip:port format, use it directly
                                            if proxy_str.startswith(('http://', 'https://')) or ':' in proxy_str:
                                                proxies.append(proxy_str)
                                                break
                                            # Look for port in a separate field
                                            elif 'port' in item:
                                                port = item['port']
                                                if isinstance(port, int):
                                                    port = str(port)
                                                proxy_str = f"http://{proxy_str}:{port}"
                                                proxies.append(proxy_str)
                                                break
                            break
        else:
            # Assume it's a regular text file
            with open(filename, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' is not a valid JSON file")
        sys.exit(1)
    
    # Remove duplicates
    proxies = list(set(proxies))
    return proxies

def main():
    # Check if filename was provided
    if len(sys.argv) != 2:
        print("Usage: python http_proxy_checker.py <proxy_file>")
        print("  proxy_file: A file containing HTTP proxies (text, CSV, or JSON)")
        print("  Supported formats:")
        print("    - http://ip:port (e.g., http://172.64.151.116:80)")
        print("    - ip:port (e.g., 172.64.151.116:80)")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Read proxies from file
    proxies = read_proxies_from_file(filename)
    
    if not proxies:
        print(f"No valid proxies found in '{filename}'")
        sys.exit(0)
    
    print(f"Checking {len(proxies)} HTTP proxies...")
    print("Working... Please wait...\n")
    
    active_proxies = []
    
    # Use a thread pool to check proxies concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_http_proxy, proxy): proxy for proxy in proxies}
        
        # Process results as they complete
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            proxy = futures[future]
            result, is_active, response_time = future.result()
            
            # Display progress
            print(f"\rProgress: {i}/{len(proxies)} ({i/len(proxies)*100:.1f}%)", end="")
            
            # Store active proxies
            if is_active:
                active_proxies.append((proxy, response_time))
    
    print("\n\nResults:")
    # Print full results
    active_count = len(active_proxies)
    
    # Save active proxies to file
    folder_path = os.path.dirname(os.path.abspath(filename))
    output_file = os.path.join(folder_path, "aliveproxy_http.txt")
    
    with open(output_file, 'w') as f:
        for proxy, response_time in active_proxies:
            f.write(f"{proxy}\n")
            print(f"{proxy} - ACTIVE (Response: {response_time:.2f}s)")
    
    # Print inactive proxies
    for proxy in proxies:
        if proxy not in [p[0] for p in active_proxies]:
            print(f"{proxy} - INACTIVE")
    
    print(f"\nSummary: {active_count} active, {len(proxies) - active_count} inactive proxies")
    print(f"Active proxies have been saved to: {output_file}")

if __name__ == "__main__":
    main()