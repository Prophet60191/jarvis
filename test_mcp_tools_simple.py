#!/usr/bin/env python3
"""
Simple test to verify MCP tools/list works.
"""

import subprocess
import json
import time

def test_mcp_tools():
    """Test MCP tools/list after proper initialization."""
    print("🧪 MCP Tools List Test")
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
        
        # Send all messages at once
        messages = [
            # 1. Initialize
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test", "version": "1.0.0"}
                }
            },
            # 2. Initialized notification
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            },
            # 3. Tools list request
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
        ]
        
        # Send all messages
        for i, message in enumerate(messages, 1):
            message_json = json.dumps(message) + "\n"
            print(f"📤 Sending message {i}: {message.get('method', 'unknown')}")
            process.stdin.write(message_json)
            process.stdin.flush()
            time.sleep(0.5)  # Small delay between messages
        
        # Close stdin and read all output
        process.stdin.close()
        
        # Wait and read output
        print("📥 Reading all responses...")
        stdout, stderr = process.communicate(timeout=10)
        
        print(f"📥 STDERR: {stderr}")
        print(f"📥 STDOUT: {stdout}")
        
        if stdout:
            lines = stdout.strip().split('\n')
            tools_found = False
            
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"Line {i+1}: {line}")
                    try:
                        response = json.loads(line)
                        
                        # Check for tools/list response
                        if response.get("id") == 2:
                            result = response.get("result", {})
                            tools = result.get("tools", [])
                            
                            print(f"🛠️ Tools response received!")
                            print(f"🛠️ Found {len(tools)} tools:")
                            
                            for tool in tools:
                                name = tool.get('name', 'Unknown')
                                desc = tool.get('description', 'No description')
                                print(f"   - {name}: {desc}")
                            
                            tools_found = len(tools) > 0
                            
                    except json.JSONDecodeError:
                        print(f"   Non-JSON line: {line}")
            
            return tools_found
        else:
            print("❌ No output received")
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
    success = test_mcp_tools()
    print(f"\n🎯 Tools Test: {'✅ PASS - Tools discovered!' if success else '❌ FAIL - No tools found'}")
