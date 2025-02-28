#!/usr/bin/env python3
import sys
import os
from proxy.HTTPproxy import check_http_proxy, read_proxies_from_file as read_http_proxies
from proxy.socks5 import check_proxy as check_socks5_proxy, read_proxies_from_file as read_socks5_proxies

def print_banner():
    banner = """
    ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
    ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
    ██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝     ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
    ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝      ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
    ██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║       ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝        ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                                
                                            By 0x1Jar
    """
    print(banner)

def print_menu():
    print("\nProxy Checker Menu:")
    print("1. Check HTTP/HTTPS Proxies")
    print("2. Check SOCKS5 Proxies")
    print("3. Exit")
    print("\nEnter your choice (1-3): ")

def main():
    print_banner()
    
    while True:
        print_menu()
        choice = input().strip()
        
        if choice not in ['1', '2', '3']:
            print("Invalid choice! Please enter 1, 2, or 3.")
            continue
            
        if choice == '3':
            print("Thanks for using Proxy Checker!")
            sys.exit(0)
            
        # Get proxy file path
        print("\nEnter the path to your proxy file: ")
        file_path = input().strip()
        
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found!")
            continue
            
        # Process based on choice
        if choice == '1':
            print("\nChecking HTTP/HTTPS Proxies...")
            # Import and use HTTP proxy checker functionality
            proxies = read_http_proxies(file_path)
            if not proxies:
                print(f"No valid proxies found in '{file_path}'")
                continue
                
            print(f"Checking {len(proxies)} HTTP proxies...")
            print("Working... Please wait...\n")
            
            active_proxies = []
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(check_http_proxy, proxy): proxy for proxy in proxies}
                
                for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                    proxy = futures[future]
                    result, is_active, response_time = future.result()
                    print(f"\rProgress: {i}/{len(proxies)} ({i/len(proxies)*100:.1f}%)", end="")
                    if is_active:
                        active_proxies.append((proxy, response_time))
            
        elif choice == '2':
            print("\nChecking SOCKS5 Proxies...")
            # Import and use SOCKS5 proxy checker functionality
            proxies = read_socks5_proxies(file_path)
            if not proxies:
                print(f"No valid proxies found in '{file_path}'")
                continue
                
            print(f"Checking {len(proxies)} SOCKS5 proxies...")
            print("Working... Please wait...\n")
            
            active_proxies = []
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(check_socks5_proxy, proxy): proxy for proxy in proxies}
                
                for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                    proxy = futures[future]
                    result, is_active, response_time = future.result()
                    print(f"\rProgress: {i}/{len(proxies)} ({i/len(proxies)*100:.1f}%)", end="")
                    if is_active:
                        active_proxies.append((proxy, response_time))
        
        # Save results
        print("\n\nResults:")
        active_count = len(active_proxies)
        
        # Save active proxies to file
        folder_path = os.path.dirname(os.path.abspath(file_path))
        output_file = os.path.join(folder_path, f"aliveproxy_{'http' if choice == '1' else 'socks5'}.txt")
        
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
        
        print("\nPress Enter to continue...")
        input()

if __name__ == "__main__":
    main()
