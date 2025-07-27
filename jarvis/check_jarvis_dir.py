#!/usr/bin/env python3
"""
Simple check for .jarvis directory.
"""

from pathlib import Path
import json

# Check directory
jarvis_dir = Path.home() / ".jarvis"
print(f"Directory exists: {jarvis_dir.exists()}")

if jarvis_dir.exists():
    print(f"Contents: {list(jarvis_dir.iterdir())}")
    
    # Check MCP config
    mcp_config = jarvis_dir / "mcp_servers.json"
    if mcp_config.exists():
        with open(mcp_config, 'r') as f:
            config = json.load(f)
        print(f"MCP config: {config}")
    else:
        print("No MCP config file")
else:
    print("Directory does not exist")

# Try to create it
try:
    jarvis_dir.mkdir(exist_ok=True)
    print(f"Created directory: {jarvis_dir}")
except Exception as e:
    print(f"Error creating directory: {e}")

# Write results to file for viewing
results_file = Path(__file__).parent / "dir_check_results.txt"
with open(results_file, 'w') as f:
    f.write(f"Directory exists: {jarvis_dir.exists()}\n")
    if jarvis_dir.exists():
        f.write(f"Contents: {list(jarvis_dir.iterdir())}\n")
    f.write("Check complete\n")

print(f"Results written to: {results_file}")
