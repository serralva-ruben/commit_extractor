from pprint import pprint
import pandas as pd
from urllib.parse import urlparse
from utils import split_concatenated_json, load_ndjson
import requests
from bs4 import BeautifulSoup
import json
import os
import concurrent
import concurrent.futures
from tqdm import tqdm
import threading 
from regex_analyze import detect_git_commit_info

objects = load_ndjson('./jsondumps/xsy.ndjson')



def extract_references(objects):
    print("Extracting references from objects...")
    urls = {}

    def process_object(obj_index):
        obj = objects[obj_index]
        obj_urls = {}
        
        for url in obj["containers"]["cna"].get("references", "none"):
            if isinstance(url, str) or url.get("url", "") in urls:
                continue

            if (url.get("url", "").startswith("https://") or url.get("url", "").startswith("http://")):
                domain = urlparse(url.get("url", "")).netloc
                if domain not in obj_urls:
                    obj_urls[domain] = []
                
                if len(obj_urls[domain]) < 5:  # Limit to 5 URLs per domain
                    obj_urls[domain].append(url.get("url", ""))
        
        return obj_urls
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Process objects in parallel
        futures = [executor.submit(process_object, i) for i in range(len(objects))]
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(objects)):
            obj_urls = future.result()
            
            for domain, domain_urls in obj_urls.items():
                if domain not in urls:
                    urls[domain] = []
                
                for url in domain_urls:
                    if len(urls[domain]) < 5 and url not in urls[domain]:
                        urls[domain].append(url)
    return urls


def extract_valid_git_domains(references):
    print("Extracting valid domains...")
    git_domains = {}
    # Use thread-safe dictionary access
    domains_lock = threading.Lock()

    def process_url(ref, url):
        try:
            response = requests.get(url, timeout=2)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            for script in soup(["script", "style", "head", "title", "meta", "[document]"]):
                script.decompose()
    
            text = soup.get_text(separator=' ', strip=True)

            analysis = detect_git_commit_info(text)

            print(f"Analyzing {url} from ref {ref}:")
            print(analysis)

            if analysis:
                # Use lock when modifying the shared dictionary
                with domains_lock:
                    if ref not in git_domains:
                        git_domains[ref] = []
                    git_domains[ref].append(url)
                
                return (ref, url)
            return None

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    tasks = []
    for ref in references.keys():
        for url in references[ref]:
            tasks.append((ref, url))

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Process URLs in parallel
        futures = [executor.submit(process_url, ref, url) for ref, url in tasks]
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            future.result()
    
    return git_domains

with open('output.txt', 'w') as file:
    json.dump(extract_valid_git_domains(extract_references(objects)), file, indent=4)

