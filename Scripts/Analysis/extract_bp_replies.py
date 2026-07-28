"""Extract agent replies with best practices from ATIF transcripts."""

import json
import sys
from pathlib import Path
from datetime import datetime


def extract_agent_replies(transcript_path: str) -> list:
    """Extract agent replies from ATIF transcript."""
    with open(transcript_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    agent_replies = []
    
    for step in data.get('steps', []):
        if step.get('source') == 'agent':
            message = step.get('message', '')
            if message and len(message) > 100:  # Filter out short responses
                # Extract timestamp if available
                timestamp = step.get('metadata', {}).get('created_at', 'unknown')
                
                # Extract token usage if available
                metrics = step.get('metadata', {}).get('metrics', {})
                tokens = {
                    'input': metrics.get('input_tokens', 0),
                    'output': metrics.get('output_tokens', 0)
                }
                
                agent_replies.append({
                    'timestamp': timestamp,
                    'message': message,
                    'tokens': tokens,
                    'step_id': step.get('step_id', 'unknown')
                })
    
    return agent_replies


def filter_bp_replies(replies: list) -> list:
    """Filter replies that contain best practices information."""
    bp_keywords = [
        'best practice', 'best practices', 'recommended', 'should',
        'standard', 'guideline', 'pattern', 'convention', 'approach',
        'implementation', 'architecture', 'design', 'structure'
    ]
    
    bp_replies = []
    for reply in replies:
        message_lower = reply['message'].lower()
        if any(keyword in message_lower for keyword in bp_keywords):
            bp_replies.append(reply)
    
    return bp_replies


def save_bp_replies(bp_replies: list, output_path: str):
    """Save best practices replies to a markdown file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Extracted Best Practices from Transcript\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n")
        f.write(f"**Total BP Replies**: {len(bp_replies)}\n\n")
        f.write("---\n\n")
        
        for i, reply in enumerate(bp_replies, 1):
            f.write(f"## Reply {i}\n\n")
            f.write(f"**Timestamp**: {reply['timestamp']}\n")
            f.write(f"**Tokens**: Input={reply['tokens']['input']}, Output={reply['tokens']['output']}\n")
            f.write(f"**Step ID**: {reply['step_id']}\n\n")
            f.write("### Content\n\n")
            f.write(reply['message'])
            f.write("\n\n---\n\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_bp_replies.py <transcript.json> [output.md]")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "extracted_bp_replies.md"
    
    print(f"Extracting agent replies from {transcript_path}...")
    replies = extract_agent_replies(transcript_path)
    print(f"Found {len(replies)} agent replies")
    
    print("Filtering for best practices content...")
    bp_replies = filter_bp_replies(replies)
    print(f"Found {len(bp_replies)} replies with best practices")
    
    print(f"Saving to {output_path}...")
    save_bp_replies(bp_replies, output_path)
    print("Done!")


if __name__ == "__main__":
    main()