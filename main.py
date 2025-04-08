import os
import json
from pprint import pprint
import pandas as pd
from urllib.parse import urlparse

def split_concatenated_json(content):
    """
    Split a string that contains multiple concatenated JSON objects.
    Returns a list of individual JSON objects.
    """
    objects = []
    i = 0
    content_len = len(content)
    
    while i < content_len:
        # Find the start of a JSON object
        while i < content_len and content[i] != '{':
            i += 1
            
        if i >= content_len:
            break
            
        # Keep track of nested braces
        start_pos, brace_count = i, 1
        i += 1
        
        # Find the matching closing brace
        while i < content_len and brace_count > 0:
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
            i += 1
            
        if brace_count == 0:
            # Extract the complete JSON object
            json_str = content[start_pos:i]
            try:
                obj = json.loads(json_str)
                objects.append(obj)
            except json.JSONDecodeError:
                pass  # Skip invalid JSON
    
    return objects

def load_ndjson(input_file):
    """Process NDJSON file with concatenated JSON objects per line."""
    objects, line_count = [], 0

    # Get file size for reporting
    # Process the file line by line
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line_count += 1
            if not line.strip():
                continue
                
            # Split the line into individual JSON objects
            objs = split_concatenated_json(line)
            for obj in objs:
                objects.append(obj)            

        return objects

objects = load_ndjson('xsy.ndjson')

product_names = []
descriptions = []
references = []

#pprint( objects[0]["containers"]["cna"].keys() )

urls = {}

for obj in objects:
    product_names.append(obj["containers"]["cna"].get("affected","none"))
    descriptions.append(obj["containers"]["cna"].get("descriptions","none"))
    for url in obj["containers"]["cna"].get("references", "none"):
        #print(url)
        if type(url) == str:
            #print(f" str : {url}")
            continue
        if url.get("url","").startswith("https://") and url.get("url","") not in urls:
            domain = urlparse(url.get("url","")).netloc

            if domain not in urls:
                urls[domain] = 1
            else:
                urls[domain] += 1


sorted_dict_desc = dict(sorted(urls.items(), key=lambda item: item[1], reverse=True))


for domain in sorted_dict_desc:
    print(f"{domain} : {urls[domain]}\n")

#references.append(obj["containers"]["cna"].get("references", "none"))


##print(urls)

#df = pd.DataFrame({
#    'product_name': product_names,
#    'description': descriptions,
#    'reference': references
#})


#df.to_csv('output.csv', index=False)  # index=False prevents writing row numbers
