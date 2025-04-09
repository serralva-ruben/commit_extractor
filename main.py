from utils import load_ndjson
import json
from extractors import extract_references, extract_valid_git_domains

objects = load_ndjson('./jsondumps/xsy.ndjson')

with open('output/output.txt', 'w') as file:
    extracted_refs = extract_references(objects)
    extracted_valid_git_domains = extract_valid_git_domains(extracted_refs)
    json.dump(extracted_valid_git_domains, file, indent=4)

