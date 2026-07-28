"""Extract web search summaries from Architect session logs."""

import re
import sys
from pathlib import Path
from datetime import datetime


def extract_web_searches(log_path: str) -> list:
    """Extract web search results from session log."""
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match web search sections
    web_search_pattern = r'# Web Search Results for "(.*?)"\n\n(##.*?)(?=\n# Web Search Results for "|\n---\n\n|$)'
    
    web_searches = []
    matches = re.finditer(web_search_pattern, content, re.DOTALL)
    
    for match in matches:
        query = match.group(1)
        results = match.group(2)
        
        web_searches.append({
            'query': query,
            'results': results
        })
    
    return web_searches


def save_web_searches(web_searches: list, output_path: str):
    """Save web search summaries to a markdown file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Extracted Web Search Summaries\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n")
        f.write(f"**Total Web Searches**: {len(web_searches)}\n\n")
        f.write("---\n\n")
        
        for i, search in enumerate(web_searches, 1):
            f.write(f"## Web Search {i}\n\n")
            f.write(f"**Query**: {search['query']}\n\n")
            f.write("### Results\n\n")
            f.write(search['results'])
            f.write("\n\n---\n\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_web_searches.py <session_log.md> [output.md]")
        sys.exit(1)
    
    log_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "extracted_web_searches.md"
    
    print(f"Extracting web searches from {log_path}...")
    web_searches = extract_web_searches(log_path)
    print(f"Found {len(web_searches)} web searches")
    
    print(f"Saving to {output_path}...")
    save_web_searches(web_searches, output_path)
    print("Done!")


if __name__ == "__main__":
    main()