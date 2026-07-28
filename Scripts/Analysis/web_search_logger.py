"""Real-time web search logger for BP scans."""

import json
import sys
from pathlib import Path
from datetime import datetime


def log_web_search() -> None:
    """Log web search results in real-time during BP scan."""
    try:
        data = json.load(sys.stdin)
    except:
        print("❌ Failed to parse stdin JSON", file=sys.stderr)
        return
    
    # Check if this is a web_search tool call
    tool_name = data.get("tool_name", "")
    if tool_name != "web_search":
        return
    
    # Extract web search information
    tool_input = data.get("tool_input", {})
    query = tool_input.get("query", "unknown")
    
    tool_response = data.get("tool_response", {})
    success = tool_response.get("success", False)
    output = tool_response.get("output", "")
    
    if not success or not output:
        return
    
    # Create web search summary directory
    summary_dir = Path("Logs/Analysis/WebSearch/Summaries")
    summary_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped file for current scan
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    summary_file = summary_dir / f"web_search_summaries_{timestamp}.md"
    
    # Format the web search summary
    summary_entry = f"""## Web Search
**Query**: {query}
**Timestamp**: {datetime.now().isoformat()}

### Results

{output}

---
"""
    
    # Append to summary file
    with open(summary_file, 'a', encoding='utf-8') as f:
        f.write(summary_entry)
    
    print(f"✅ Web search logged: {query}", file=sys.stderr)


if __name__ == "__main__":
    log_web_search()