# Proxy Checker Tools

A collection of Python scripts for checking and validating HTTP and SOCKS5 proxies.

## Features

- Support for both HTTP and SOCKS5 proxy checking
- Concurrent proxy testing using thread pools
- Multiple input file formats supported (TXT, CSV, JSON)
- Detailed output with response times
- Saves working proxies to separate files
- Progress tracking during checks

## Requirements

```python
pysocks==1.7.1
requests==2.31.0
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/proxy-checker.git
cd proxy-checker
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### HTTP Proxy Checker

```bash
python HTTPproxy.py <proxy_file>
```

Supported proxy formats:
- `http://ip:port` (e.g., http://172.64.151.116:80)
- `ip:port` (e.g., 172.64.151.116:80)

### SOCKS5 Proxy Checker

```bash
python socks5.py <proxy_file>
```

Supported proxy format:
- `ip:port` (e.g., 172.64.151.116:1080)

### Input File Formats

The tools support multiple input file formats:

1. Text File (.txt):
```
ip:port
ip:port
```

2. CSV File (.csv):
```
ip:port,other_data
ip:port,other_data
```

3. JSON File (.json) - HTTP proxy checker only:
```json
{
    "proxies": [
        "ip:port",
        "http://ip:port"
    ]
}
```

### Output

Both tools will:
1. Display real-time progress during checking
2. Show detailed results for each proxy
3. Save working proxies to:
   - `aliveproxy_http.txt` for HTTP proxies
   - `aliveproxy.txt` for SOCKS5 proxies
4. Provide a summary of active and inactive proxies

## Features Details

### HTTP Proxy Checker
- Tests proxies against httpbin.org
- Verifies proxy functionality by checking returned IP
- Supports both HTTP and HTTPS protocols
- Handles various proxy string formats

### SOCKS5 Proxy Checker
- Tests proxies against Google's DNS (8.8.8.8)
- Measures response time for each proxy
- Handles connection timeouts gracefully
- Simple and efficient checking mechanism

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

