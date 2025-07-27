#!/usr/bin/env python3
"""
Test MCP Memory Storage server directly to check for stdout issues.
"""

import subprocess
import json
import time
import sys

def test_mcp_server_direct():
    """Test the MCP Memory Storage server directly."""
    print("🧪 Testing MCP Memory Storage Server Directly")
    print("=" * 60)
    
    try:
        # Start the MCP server process
        cmd = ["npx", "@modelcontextprotocol/server-memory"]
        print(f"🚀 Starting: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        print(f"✅ Process started with PID: {process.pid}")
        
        # Wait a moment for the server to start
        time.sleep(1)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Process exited with code: {process.returncode}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        print("✅ Process is running")
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "jarvis-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Sending initialize request...")
        print(f"Request: {request_json.strip()}")
        
        # Send the request
        process.stdin.write(request_json)
        process.stdin.flush()
        print("✅ Request sent")
        
        # Try to read response
        print("📥 Reading response...")
        
        # Read with timeout
        import select
        import os
        
        # Set non-blocking
        fd = process.stdout.fileno()
        fl = os.fcntl(fd, os.F_GETFL)
        os.fcntl(fd, os.F_SETFL, fl | os.O_NONBLOCK)
        
        response_lines = []
        start_time = time.time()
        
        while time.time() - start_time < 10:  # 10 second timeout
            try:
                ready, _, _ = select.select([process.stdout], [], [], 1)
                if ready:
                    line = process.stdout.readline()
                    if line:
                        response_lines.append(line.strip())
                        print(f"📥 Received: {line.strip()}")
                        
                        # Try to parse as JSON
                        try:
                            response = json.loads(line.strip())
                            if "result" in response:
                                print("✅ Valid initialize response received!")
                                
                                # Send tools/list request
                                tools_request = {
                                    "jsonrpc": "2.0",
                                    "id": 2,
                                    "method": "tools/list"
                                }
                                
                                tools_json = json.dumps(tools_request) + "\n"
                                print(f"📤 Sending tools/list request...")
                                
                                process.stdin.write(tools_json)
                                process.stdin.flush()
                                
                                # Read tools response
                                time.sleep(1)
                                ready, _, _ = select.select([process.stdout], [], [], 5)
                                if ready:
                                    tools_line = process.stdout.readline()
                                    if tools_line:
                                        print(f"📥 Tools response: {tools_line.strip()}")
                                        try:
                                            tools_response = json.loads(tools_line.strip())
                                            if "result" in tools_response and "tools" in tools_response["result"]:
                                                tools = tools_response["result"]["tools"]
                                                print(f"🛠️ Found {len(tools)} tools:")
                                                for tool in tools:
                                                    print(f"   - {tool.get('name', 'Unknown')}")
                                                return True
                                        except json.JSONDecodeError as e:
                                            print(f"❌ Failed to parse tools JSON: {e}")
                                            print(f"Raw response: {tools_line}")
                                
                                return True
                            elif "error" in response:
                                print(f"❌ Server returned error: {response['error']}")
                                return False
                        except json.JSONDecodeError:
                            print(f"⚠️ Non-JSON output: {line.strip()}")
                            # This could be the problem - stdout pollution
                            
            except:
                pass
            
            time.sleep(0.1)
        
        print("❌ Timeout waiting for response")
        return False
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up process
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    success = test_mcp_server_direct()
    print(f"\n🎯 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
