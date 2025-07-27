#!/usr/bin/env python3
"""
Simple test of MCP Memory Storage server.
"""

import subprocess
import json
import time

def test_mcp_simple():
    """Simple test of MCP server communication."""
    print("🧪 Simple MCP Server Test")
    print("=" * 40)
    
    try:
        # Start the MCP server process
        cmd = ["npx", "@modelcontextprotocol/server-memory"]
        print(f"🚀 Starting: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Process started with PID: {process.pid}")
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Sending initialize request...")
        
        # Send the request
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Wait and read response
        time.sleep(2)
        
        # Try to read any output
        try:
            stdout, stderr = process.communicate(timeout=5)
            print(f"📥 STDOUT: {stdout}")
            print(f"📥 STDERR: {stderr}")
            print(f"📊 Return code: {process.returncode}")
            
            if stdout:
                lines = stdout.strip().split('\n')
                for i, line in enumerate(lines):
                    print(f"Line {i+1}: {line}")
                    try:
                        response = json.loads(line)
                        print(f"✅ Valid JSON response: {response}")
                        return True
                    except json.JSONDecodeError:
                        print(f"⚠️ Non-JSON line: {line}")
            
            return False
            
        except subprocess.TimeoutExpired:
            print("❌ Process timeout")
            process.kill()
            return False
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_simple()
    print(f"\n🎯 Result: {'✅ PASS' if success else '❌ FAIL'}")
