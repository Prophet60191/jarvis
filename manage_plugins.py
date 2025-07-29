#!/usr/bin/env python3
"""
Jarvis Plugin Management Script

This script provides a simple interface for managing Jarvis plugins
without needing to import the full Jarvis application.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "jarvis"))

try:
    from jarvis.plugins.cli import main
except ImportError:
    print("❌ Error: Could not import plugin CLI")
    print("Make sure you're running from the Jarvis root directory")
    print("Current directory:", current_dir)
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
