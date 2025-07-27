#!/usr/bin/env python3
"""
Jarvis Plugin Management Script

This script provides a simple interface for managing Jarvis plugins
without needing to import the full Jarvis application.
"""

import sys
import os
from pathlib import Path

# Add jarvis to Python path
jarvis_dir = Path(__file__).parent / "jarvis"
sys.path.insert(0, str(jarvis_dir))

from jarvis.plugins.cli import main

if __name__ == "__main__":
    sys.exit(main())
