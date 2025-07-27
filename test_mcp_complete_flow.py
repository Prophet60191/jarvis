#!/usr/bin/env python3
"""
Test complete MCP flow according to 2025-06-18 specification.
"""

import subprocess
import json
import time
import asyncio

async def test_complete_mcp_flow():
    """Test the complete MCP initialization and tool discovery flow."""
    print("🧪 Complete MCP Flow Test (2025-06-18 Spec)")
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
            text=True
        )
        
        print(f"✅ Process started with PID: {process.pid}")
        
        # Step 1: Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",  # Use server's supported version
                "capabilities": {
                    "tools": {}  # Request tool capabilities
                },
                "clientInfo": {
                    "name": "jarvis-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Step 1: Sending initialize request...")
        print(f"Request: {json.dumps(init_request, indent=2)}")
        
        # Send the request
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read initialize response
        print("📥 Reading initialize response...")
        time.sleep(1)
        
        # Get response
        stdout, stderr = process.communicate(timeout=5)
        print(f"📥 STDERR: {stderr}")
        
        if stdout:
            lines = stdout.strip().split('\n')
            init_response_line = lines[0] if lines else ""
            
            if init_response_line:
                print(f"📥 Initialize response: {init_response_line}")
                
                try:
                    init_response = json.loads(init_response_line)
                    
                    if "result" in init_response:
                        server_capabilities = init_response["result"].get("capabilities", {})
                        server_tools_cap = server_capabilities.get("tools", {})
                        
                        print(f"✅ Server capabilities: {server_capabilities}")
                        print(f"🛠️ Server tools capability: {server_tools_cap}")
                        
                        if "tools" in server_capabilities:
                            print("✅ Server supports tools!")
                            
                            # Step 2: Send notifications/initialized
                            print("\n📤 Step 2: Sending notifications/initialized...")
                            
                            # Restart process for step 2 (since we already consumed stdout)
                            process = subprocess.Popen(
                                cmd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            
                            # Send init again
                            process.stdin.write(request_json)
                            process.stdin.flush()
                            time.sleep(0.5)
                            
                            # Send notifications/initialized
                            initialized_notification = {
                                "jsonrpc": "2.0",
                                "method": "notifications/initialized"
                            }
                            
                            notification_json = json.dumps(initialized_notification) + "\n"
                            print(f"Notification: {json.dumps(initialized_notification, indent=2)}")
                            
                            process.stdin.write(notification_json)
                            process.stdin.flush()
                            time.sleep(0.5)
                            
                            # Step 3: Send tools/list request
                            print("\n📤 Step 3: Sending tools/list request...")
                            
                            tools_request = {
                                "jsonrpc": "2.0",
                                "id": 2,
                                "method": "tools/list"
                            }
                            
                            tools_json = json.dumps(tools_request) + "\n"
                            print(f"Request: {json.dumps(tools_request, indent=2)}")
                            
                            process.stdin.write(tools_json)
                            process.stdin.flush()
                            
                            # Read tools response
                            print("📥 Reading tools response...")
                            time.sleep(2)
                            
                            # Read all output
                            process.stdin.close()
                            stdout, stderr = process.communicate(timeout=5)
                            
                            print(f"📥 Full STDOUT: {stdout}")
                            print(f"📥 Full STDERR: {stderr}")
                            
                            if stdout:
                                lines = stdout.strip().split('\n')
                                for i, line in enumerate(lines):
                                    if line.strip():
                                        print(f"Line {i+1}: {line}")
                                        try:
                                            response = json.loads(line)
                                            if response.get("id") == 2:  # tools/list response
                                                tools = response.get("result", {}).get("tools", [])
                                                print(f"🛠️ Found {len(tools)} tools:")
                                                for tool in tools:
                                                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                                                return len(tools) > 0
                                        except json.JSONDecodeError:
                                            print(f"   Non-JSON line: {line}")
                            
                            return False
                        else:
                            print("❌ Server does not support tools")
                            return False
                    else:
                        print(f"❌ Initialize failed: {init_response}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse initialize response: {e}")
                    return False
            else:
                print("❌ No initialize response received")
                return False
        else:
            print("❌ No output from server")
            return False
        
    except subprocess.TimeoutExpired:
        print("❌ Process timeout")
        if 'process' in locals():
            process.kill()
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
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
    success = asyncio.run(test_complete_mcp_flow())
    print(f"\n🎯 Complete Flow Test: {'✅ PASS' if success else '❌ FAIL'}")
