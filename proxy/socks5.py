#!/usr/bin/env python3
import socket
import socks
import sys
import time
import threading
import concurrent.futures
import os
import csv

def check_proxy(proxy_str):
    """Check if a SOCKS5 proxy is active."""
    # Parse the proxy string (expected format is ip:port)
    try:
        if ':' in proxy_str:
            ip, port = proxy_str.strip().split(':')
            port = int(port)
        else:
            return f"{proxy_str} - Invalid format. Expected ip:port"
    except ValueError:
        return f"{proxy_str} - Invalid format. Expected ip:port"
    
    # Create a socket and set it to use the proxy
    s = socks.socksocket()
    s.settimeout(10)  # Set timeout to 10 seconds
    
    try:
        # Configure SOCKS5 proxy
        s.set_proxy(socks.SOCKS5, ip, port)
        
        # Try to connect to a well-known site (Google's DNS)
        start_time = time.time()
        s.connect(('8.8.8.8', 53))
        response_time = time.time() - start_time
        
        # If we get here, the proxy is working
        return f"{proxy_str} - ACTIVE (Response: {response_time:.2f}s)", True, response_time
    except Exception as e:
        # If there's an exception, the proxy is not working
        return f"{proxy_str} - INACTIVE ({str(e)})", False, 0
    finally:
        s.close()

def read_proxies_from_file(filename):
    """Read proxies from either a text file or CSV file."""
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
        else:
            # Assume it's a regular text file
            with open(filename, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    return proxies

def main():
    
    # Check if filename was provided
    if len(sys.argv) != 2:
        print("Usage: python socks5_checker.py <proxy_file>")
        print("  proxy_file: A file containing SOCKS5 proxies (text file or CSV)")
        print("  For text files: one proxy per line in format ip:port")
        print("  For CSV files: first column should contain proxies in format ip:port")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Read proxies from file
    proxies = read_proxies_from_file(filename)
    
    if not proxies:
        print(f"No proxies found in '{filename}'")
        sys.exit(0)
    
    print(f"Checking {len(proxies)} proxies...")
    print("Working... Please wait...\n")
    
    active_proxies = []
    
    # Use a thread pool to check proxies concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
        
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
    output_file = os.path.join(folder_path, "aliveproxy.txt")
    
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
