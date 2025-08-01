#!/usr/bin/env python3
"""
Run MCP test and save results to file.
"""

import sys
import os
from pathlib import Path
import traceback

# Add the jarvis package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test():
    """Run the MCP test and save results."""
    results = []
    
    def log(message):
        print(message)
        results.append(message)
    
    try:
        log("🧪 MCP System Test Results")
        log("=" * 50)
        
        # Import and run the test
        from quick_mcp_test import test_mcp_system
        
        # Redirect stdout to capture output
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            test_mcp_system()
        
        output = f.getvalue()
        log(output)
        
    except Exception as e:
        log(f"❌ Error running test: {e}")
        log(traceback.format_exc())
    
    # Save results to file
    results_file = Path(__file__).parent / "mcp_test_results.txt"
    with open(results_file, 'w') as f:
        f.write('\n'.join(results))
    
    log(f"📄 Results saved to: {results_file}")
    return results_file

if __name__ == "__main__":
    run_test()
