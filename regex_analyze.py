import re
import json

def detect_git_commit_info(html_content):
    """
    A balanced approach to detect Git commit information without ML training.
    Uses multiple signals and a weighted scoring system.
    
    Returns:
        tuple: (is_commit_page, confidence_score, detection_method)
    """
    from bs4 import BeautifulSoup
    import re
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Clean the HTML
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get plain text
    text = soup.get_text(separator=' ', strip=True)
    
    # Initialize score
    score = 0
    evidence = []
    
    # 1. Check HTML structure (GitHub/GitLab/Bitbucket commit pages have specific structures)
    commit_ui_elements = soup.select('.commit, .diff, .blob-code, .blob-num, .commit-tease, [data-commit-id]')
    if commit_ui_elements:
        score += 30
        evidence.append(f"Found {len(commit_ui_elements)} commit UI elements")
    
    # 2. Check for commit hashes (40 hex chars)
    sha_pattern = r'\b[0-9a-f]{40}\b'
    sha_matches = re.findall(sha_pattern, text)
    if sha_matches:
        score += 25
        evidence.append(f"Found {len(sha_matches)} commit SHA hashes")
    
    # 3. Check for diff headers
    diff_headers = re.findall(r'diff --git a/\S+ b/\S+', text)
    if diff_headers:
        score += 30
        evidence.append(f"Found {len(diff_headers)} diff headers")
    
    # 4. Check for diff chunks
    diff_chunks = re.findall(r'@@ -\d+,\d+ \+\d+,\d+ @@', text)
    if diff_chunks:
        score += 25
        evidence.append(f"Found {len(diff_chunks)} diff chunks")
    
    # 5. Look for added/removed line indicators
    plus_lines = len(re.findall(r'\n\+[^\+]', text))
    minus_lines = len(re.findall(r'\n-[^-]', text))
    if plus_lines > 5 or minus_lines > 5:
        score += 15
        evidence.append(f"Found {plus_lines} added lines and {minus_lines} removed lines")
    
    # 6. Check commit metadata
    author_pattern = r'Author:\s+[^<]+<[^>]+>'
    date_pattern = r'Date:\s+\w{3}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}'
    
    if re.search(author_pattern, text):
        score += 15
        evidence.append("Found Author information")
    
    if re.search(date_pattern, text):
        score += 10
        evidence.append("Found commit date information")
    
    # 7. Check vocabulary
    commit_terms = [
        'commit', 'patch', 'diff', 'author', 'date:', 'modified', 'added', 'removed',
        'index', 'blob', 'repository', 'pull request', 'merge', 'branch', 'version'
    ]
    
    term_matches = sum(1 for term in commit_terms if term.lower() in text.lower())
    if term_matches >= 3:
        score += min(term_matches * 2, 15)  # Cap at 15 points
        evidence.append(f"Found {term_matches} commit-related terms")
    
    # 8. Check for file paths in diffs
    file_paths = re.findall(r'(a/|b/)[a-zA-Z0-9_\-./]+\.(java|py|js|c|cpp|h|rb|go|php|html|css|xml|json)', text)
    if file_paths:
        score += 10
        evidence.append(f"Found {len(file_paths)} file paths in diffs")
    
    # Calculate confidence score (0-1)
    confidence = min(score / 100.0, 1.0)
    
    # Determine result based on threshold
    is_commit_page = confidence > 0.4  # Lower threshold for higher recall
    
    detection_method = "hybrid_scoring"
    
    return is_commit_page, confidence, {
        "score": score,
        "evidence": evidence,
        "method": detection_method
    }