import json
import sys
import os

# List of recognized Git hosting domains
GIT_DOMAINS = ["github.com", "gitlab.com", "bitbucket.org"]

def is_git_url(url):
    """Return True if the URL points to a recognized Git hosting service."""
    if not isinstance(url, str):
        return False
    return any(domain in url for domain in GIT_DOMAINS)

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
        start_pos = i
        brace_count = 1
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

def process_ndjson(input_file, output_file):
    """Process NDJSON file with concatenated JSON objects per line."""
    results = []
    total_records = 0
    valid_records = 0
    line_count = 0
    
    try:
        # Get file size for reporting
        file_size = os.path.getsize(input_file)
        print(f"Processing file '{input_file}' ({file_size:,} bytes)...")
        
        # Process the file line by line
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                if not line.strip():
                    continue
                    
                # Split the line into individual JSON objects
                objects = split_concatenated_json(line)
                
                if not objects and line.strip():
                    # Try simple JSON parsing as fallback
                    try:
                        obj = json.loads(line)
                        objects = [obj]
                    except json.JSONDecodeError:
                        print(f"Warning: Failed to parse line {line_count}")
                        continue
                
                total_records += len(objects)
                
                # Process each JSON object
                for obj in objects:
                    git_urls = []
                    
                    # Extract Git URLs from references
                    for ref in obj.get("references", []):
                        if isinstance(ref, dict):
                            url = ref.get("url", "")
                            if url and is_git_url(url):
                                git_urls.append(url)
                    
                    if git_urls:
                        results.append({
                            "cve_id": obj.get("id"),
                            "aliases": obj.get("aliases", []),
                            "git_urls": git_urls
                        })
                        valid_records += 1
                
                # Print progress every 100 lines
                if line_count % 100 == 0:
                    print(f"Processed {line_count} lines, found {valid_records} records with Git URLs")
                
                # Save intermediate results every 10,000 records
                if len(results) > 0 and len(results) % 10000 == 0:
                    print(f"Saving intermediate results ({len(results)} records)...")
                    with open(output_file, "w", encoding="utf-8") as outfile:
                        json.dump(results, outfile, indent=2)
        
        # Write final results
        print(f"Writing {len(results):,} records to output file...")
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(results, outfile, indent=2)
            
        print(f"\nMapping saved to '{output_file}'.")
        print(f"Total JSON objects processed: {total_records:,}")
        print(f"Total records with Git URLs: {valid_records:,}")
            
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")
        # Save partial results
        if results:
            with open(output_file, "w", encoding="utf-8") as outfile:
                json.dump(results, outfile, indent=2)
            print(f"Partial results ({len(results):,} records) saved to '{output_file}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to save partial results on error
        if results:
            try:
                with open(output_file, "w", encoding="utf-8") as outfile:
                    json.dump(results, outfile, indent=2)
                print(f"Partial results ({len(results):,} records) saved to '{output_file}'.")
            except:
                print("Failed to save partial results.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_git_refs.py <input_ndjson_file> [output_json_file]")
        sys.exit(1)
    
    input_ndjson = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) >= 3 else "cve_git_mapping.json"

    if not os.path.isfile(input_ndjson):
        print(f"Error: File '{input_ndjson}' does not exist.")
        sys.exit(1)

    process_ndjson(input_ndjson, output_json)