"""SessionEnd transcript parser - merges transcript data with real-time logs for complete chronological ordering."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import re


def get_session_id_from_filename(filename: str) -> str:
    """Extract session_id from transcript filename."""
    # Transcript files are named like "ordinary-basilisk.json"
    return filename.replace('.json', '')


def parse_transcript_file(transcript_path: Path) -> list:
    """Parse transcript file and extract all events with timestamps."""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to parse transcript: {e}", file=sys.stderr)
        return []
    
    events = []
    
    # Parse conversation steps
    for step in transcript_data.get('conversation', []):
        timestamp = step.get('timestamp', '')
        step_id = step.get('step_id', 0)
        source = step.get('source', 'unknown')
        message = step.get('message', '')
        
        # Extract tool calls from this step
        tool_calls = step.get('tool_calls', [])
        for tool_call in tool_calls:
            tool_name = tool_call.get('function_name', 'unknown')
            tool_call_id = tool_call.get('tool_call_id', 'unknown')
            arguments = tool_call.get('arguments', {})
            
            # Create tool attempt event
            events.append({
                'timestamp': timestamp,
                'event_type': 'tool_attempt_from_transcript',
                'tool_name': tool_name,
                'tool_call_id': tool_call_id,
                'arguments': arguments,
                'source': 'transcript',
                'step_id': step_id
            })
        
        # Extract tool observations (results/failures)
        observation = step.get('observation', {})
        if observation:
            results = observation.get('results', [])
            for result in results:
                source_call_id = result.get('source_call_id', 'unknown')
                content = result.get('content', '')
                
                # Check if this is a failure/error
                if 'failed' in content.lower() or 'error' in content.lower() or 'not found' in content.lower():
                    events.append({
                        'timestamp': timestamp,
                        'event_type': 'tool_failure_from_transcript',
                        'tool_call_id': source_call_id,
                        'error_message': content,
                        'source': 'transcript',
                        'step_id': step_id
                    })
        
        # Extract agent messages
        if message:
            events.append({
                'timestamp': timestamp,
                'event_type': 'agent_message_from_transcript',
                'message': message,
                'source': 'transcript',
                'step_id': step_id
            })
    
    return events


def parse_realtime_log(log_path: Path) -> list:
    """Parse our real-time log file and extract events with timestamps."""
    events = []
    
    if not log_path.exists():
        return events
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file is JSONL format (one JSON object per line)
        if log_path.suffix == '.jsonl' or content.strip().startswith('{'):
            # Parse JSONL format
            for line in content.strip().split('\n'):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    # Skip if entry is not a dict
                    if not isinstance(entry, dict):
                        continue
                    timestamp = entry.get('timestamp', '')
                    event = entry.get('event', 'unknown')
                    
                    events.append({
                        'timestamp': timestamp,
                        'event_type': f'{event}_from_realtime',
                        'content': entry,
                        'source': 'realtime'
                    })
                except (json.JSONDecodeError, AttributeError):
                    continue
        else:
            # Parse markdown format entries (primary format now)
            # Look for sections that start with ### EVENT_NAME
            sections = re.split(r'### ', content)
            
            for section in sections:
                if not section.strip():
                    continue
                
                # Extract timestamp from the section
                timestamp_match = re.search(r'\*\*Timestamp\*\*: ([^\n]+)', section)
                if not timestamp_match:
                    continue
                
                timestamp = timestamp_match.group(1).strip()
                event_type = section.split('\n')[0].strip()
                
                events.append({
                    'timestamp': timestamp,
                    'event_type': f'{event_type}_from_realtime',
                    'content': section,
                    'source': 'realtime'
                })
            
    except Exception as e:
        print(f"❌ Failed to parse real-time log: {e}", file=sys.stderr)
    
    return events


def merge_events_by_timestamp(realtime_events: list, transcript_events: list) -> list:
    """Merge events from both sources and sort by timestamp."""
    all_events = realtime_events + transcript_events
    
    # Sort by timestamp
    all_events.sort(key=lambda x: x['timestamp'])
    
    return all_events


def format_merged_events(merged_events: list) -> str:
    """Format merged events into readable markdown."""
    formatted = []
    
    formatted.append("# Complete Session Timeline (Real-time + Transcript Reconstruction)")
    formatted.append(f"**Generated**: {datetime.now().isoformat()}")
    formatted.append(f"**Total Events**: {len(merged_events)}")
    formatted.append("")
    formatted.append("---")
    formatted.append("")
    
    for event in merged_events:
        timestamp = event['timestamp']
        source = event['source']
        event_type = event['event_type']
        
        formatted.append(f"### {event_type}")
        formatted.append(f"**Timestamp**: {timestamp}")
        formatted.append(f"**Source**: {source}")
        formatted.append("")
        
        if event_type == 'tool_attempt_from_transcript':
            formatted.append(f"**Tool**: {event['tool_name']}")
            formatted.append(f"**Tool Call ID**: {event['tool_call_id']}")
            formatted.append(f"**Arguments**:")
            formatted.append("```")
            formatted.append(json.dumps(event['arguments'], indent=2))
            formatted.append("```")
        
        elif event_type == 'tool_failure_from_transcript':
            formatted.append(f"**Tool Call ID**: {event['tool_call_id']}")
            formatted.append(f"**Error Message**:")
            formatted.append("```")
            formatted.append(event['error_message'])
            formatted.append("```")
        
        elif event_type == 'agent_message_from_transcript':
            formatted.append(f"**Message**:")
            formatted.append("```")
            formatted.append(event['message'])
            formatted.append("```")
        
        elif event_type.endswith('_from_realtime'):
            content = event.get('content', {})
            if isinstance(content, dict):
                # JSONL format - display the entry nicely
                formatted.append(f"**Event Type**: {content.get('event', 'unknown')}")
                if 'prompt' in content:
                    formatted.append(f"**Prompt**:")
                    formatted.append("```")
                    formatted.append(str(content['prompt']))
                    formatted.append("```")
                elif 'tool_name' in content:
                    formatted.append(f"**Tool**: {content.get('tool_name', 'unknown')}")
                    formatted.append(f"**Success**: {content.get('success', 'unknown')}")
                else:
                    formatted.append("**Details**:")
                    formatted.append("```")
                    formatted.append(json.dumps(content, indent=2))
                    formatted.append("```")
            else:
                # Markdown format
                formatted.append(f"**Original Event**:")
                formatted.append("```")
                formatted.append(str(content))
                formatted.append("```")
        
        formatted.append("---")
        formatted.append("")
    
    return "\n".join(formatted)


def merge_transcript_with_realtime_log() -> None:
    """Main function to merge transcript data with real-time log."""
    try:
        # Read hook data
        data = json.load(sys.stdin)
    except:
        print("❌ Failed to parse stdin JSON", file=sys.stderr)
        return
    
    session_id = data.get("session_id", "unknown")
    
    # Find the transcript file
    transcript_dir = Path(os.path.expandvars("$APPDATA/devin/cli/transcripts"))
    transcript_file = transcript_dir / f"{session_id}.json"
    
    if not transcript_file.exists():
        print(f"⚠️ Transcript file not found: {transcript_file}", file=sys.stderr)
        return
    
    # Find our real-time log file
    log_dir = Path("Logs/Architect/Session")
    # Look for existing session files (both .md and .jsonl)
    # Try both exact session_id and title version
    session_name = session_id if session_id else "Unknown"
    session_name_title = session_id.title() if session_id else "Unknown"
    
    md_files = list(log_dir.glob(f"Architect_*_{session_name}.md")) + list(log_dir.glob(f"Architect_*_{session_name_title}.md"))
    jsonl_files = list(log_dir.glob(f"Architect_*_{session_name}.jsonl")) + list(log_dir.glob(f"Architect_*_{session_name_title}.jsonl"))
    log_files = md_files + jsonl_files
    
    if not log_files:
        print(f"⚠️ No real-time log file found for session: {session_id}", file=sys.stderr)
        return
    
    # Use the most recent log file
    log_file = max(log_files, key=lambda f: f.stat().st_mtime)
    
    print(f"🔄 Processing transcript merge for session: {session_id}", file=sys.stderr)
    
    # Parse both sources
    transcript_events = parse_transcript_file(transcript_file)
    realtime_events = parse_realtime_log(log_file)
    
    print(f"📊 Found {len(transcript_events)} transcript events", file=sys.stderr)
    print(f"📊 Found {len(realtime_events)} real-time events", file=sys.stderr)
    
    # Merge by timestamp
    merged_events = merge_events_by_timestamp(realtime_events, transcript_events)
    
    # Format merged timeline
    merged_content = format_merged_events(merged_events)
    
    # Append to the log file
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(merged_content)
    
    print(f"✅ Successfully merged transcript data into: {log_file}", file=sys.stderr)


if __name__ == "__main__":
    merge_transcript_with_realtime_log()