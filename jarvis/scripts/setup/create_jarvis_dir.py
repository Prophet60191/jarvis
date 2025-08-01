#!/usr/bin/env python3
"""
Create .jarvis directory and test MCP configuration.
"""

import os
import json
from pathlib import Path

def create_jarvis_dir():
    """Create .jarvis directory and test configuration."""
    print("🔧 Creating Jarvis directory and testing MCP")
    
    # Create .jarvis directory
    jarvis_dir = Path.home() / ".jarvis"
    jarvis_dir.mkdir(exist_ok=True)
    print(f"✅ Created directory: {jarvis_dir}")
    
    # Test if we can create a simple file
    test_file = jarvis_dir / "test.txt"
    test_file.write_text("test")
    print(f"✅ Created test file: {test_file}")
    
    # Remove test file
    test_file.unlink()
    print("✅ Removed test file")
    
    print("🎉 Directory creation successful!")

if __name__ == "__main__":
    create_jarvis_dir()
