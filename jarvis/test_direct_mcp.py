#!/usr/bin/env python3
"""
Test direct MCP server connection.
"""

import asyncio
import json
import subprocess
import sys
import os

# Add the jarvis package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_direct_mcp_connection():
    """Test direct connection to MCP server."""
    print("🧪 Testing Direct MCP Server Connection")
    print("=" * 50)
    
    try:
        # Start the MCP server process
        cmd = ["npx", "@modelcontextprotocol/server-memory"]
        print(f"Starting command: {' '.join(cmd)}")
        
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
        await asyncio.sleep(1)
        
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
                    "name": "jarvis-voice-assistant",
                    "version": "1.0.0"
                }
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Sending initialize request...")
        
        # Send the request
        process.stdin.write(request_json)
        process.stdin.flush()
        print("✅ Request sent")
        
        # Try to read response with timeout
        print("📥 Waiting for response...")
        
        # Use asyncio to read with timeout
        async def read_line():
            return await asyncio.get_event_loop().run_in_executor(
                None, process.stdout.readline
            )
        
        try:
            response_line = await asyncio.wait_for(read_line(), timeout=10.0)
            
            if response_line:
                print(f"✅ Received response: {response_line.strip()}")
                try:
                    response = json.loads(response_line)
                    if "error" in response:
                        print(f"❌ MCP server returned error: {response['error']}")
                        return False
                    else:
                        print("✅ MCP server initialized successfully!")
                        
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
                        tools_response_line = await asyncio.wait_for(read_line(), timeout=5.0)
                        if tools_response_line:
                            print(f"✅ Tools response: {tools_response_line.strip()}")
                            try:
                                tools_response = json.loads(tools_response_line)
                                if "result" in tools_response and "tools" in tools_response["result"]:
                                    tools = tools_response["result"]["tools"]
                                    print(f"🛠️ Found {len(tools)} tools:")
                                    for tool in tools:
                                        print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                                    return True
                                else:
                                    print(f"❌ Unexpected tools response format: {tools_response}")
                                    return False
                            except json.JSONDecodeError as e:
                                print(f"❌ Failed to parse tools JSON response: {e}")
                                return False
                        else:
                            print("❌ No tools response received")
                            return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON response: {e}")
                    print(f"Raw response: {response_line}")
                    return False
            else:
                print("❌ No response received from MCP server")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Timeout waiting for response from MCP server")
            return False
        
    except Exception as e:
        print(f"❌ Exception during MCP connection test: {e}")
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

async def main():
    """Main test function."""
    print("🧪 Direct MCP Connection Test")
    print("=" * 50)
    
    success = await test_direct_mcp_connection()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Result: {'✅ PASS' if success else '❌ FAIL'}")

if __name__ == "__main__":
    asyncio.run(main())
