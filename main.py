#!/usr/bin/env python

import argparse
from urllib.parse import urlparse, parse_qs
from tabulate import tabulate

def parse_curl_file(file_path):
    with open(file_path, 'r') as f:
        curl_command = f.read().strip()
    
    parts = [part.strip() for part in curl_command.split("'")]
    url = next(part for part in parts if part.startswith('http'))
    
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    endpoint = parsed_url.path
    
    params = parse_qs(parsed_url.query, keep_blank_values=True, )
    headers = {}
    cookies = {}
    
    for i, part in enumerate(parts):
        if part == '-H':
            header = parts[i+1].split(': ', 1)
            if header[0].lower() == 'cookie':
                for cookie in header[1].split('; '):
                    key, value = cookie.split('=', 1)
                    cookies[key] = value
            else:
                headers[header[0]] = header[1]
    
    return {
        'base_url': base_url,
        'endpoint': endpoint,
        'params': params,
        'headers': headers,
        'cookies': cookies
    }

def compare_curls(curl1, curl2):
    differences = []
    
    for key in set(curl1.keys()) | set(curl2.keys()):
        if key in ['params', 'headers', 'cookies']:
            for subkey in set(curl1.get(key, {}).keys()) | set(curl2.get(key, {}).keys()):
                value1 = curl1.get(key, {}).get(subkey)
                value2 = curl2.get(key, {}).get(subkey)
                if value1 != value2:
                    differences.append([key, subkey, value1, value2])
        else:
            value1 = curl1.get(key)
            value2 = curl2.get(key)
            if value1 != value2:
                differences.append([key, '', value1, value2])
    
    return differences

def main():
    parser = argparse.ArgumentParser(description='Compare two curl commands from files')
    parser.add_argument('file1', help='Path to the first curl file')
    parser.add_argument('file2', help='Path to the second curl file')
    args = parser.parse_args()
    
    curl1 = parse_curl_file(args.file1)
    curl2 = parse_curl_file(args.file2)
    
    differences = compare_curls(curl1, curl2)
    
    if differences:
        print(tabulate(differences, headers=['Component', 'Key', 'Curl 1', 'Curl 2'], tablefmt='grid'))
    else:
        print("No differences found between the two curl commands.")

if __name__ == '__main__':
    main()
