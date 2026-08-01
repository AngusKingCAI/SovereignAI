#!/usr/bin/env python3
"""
Test script that writes directly to Windows console device
This bypasses redirection and writes to the actual terminal
"""
import sys
import os

def write_to_console(message):
    """Write directly to Windows console device"""
    if sys.platform.startswith('win'):
        console_device = 'con'
    else:
        console_device = '/dev/tty'
    
    try:
        with open(console_device, 'w') as console:
            console.write(message + '\n')
            console.flush()
        return True
    except Exception as e:
        print(f"Failed to write to console: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    write_to_console("=== DIRECT CONSOLE MESSAGE ===")
    write_to_console("This should appear in the terminal")
    write_to_console("Even if stdout is redirected")
    write_to_console("=== END CONSOLE MESSAGE ===")