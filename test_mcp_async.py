#!/usr/bin/env python3
"""
Async test of MCP tools discovery.
"""

import asyncio
import subprocess
import json

async def test_mcp_async():
    """Test MCP with proper async handling."""
    print("🧪 Async MCP Tools Test")
    print("=" * 40)
    
    try:
        # Start the MCP server process
        cmd = ["npx", "@modelcontextprotocol/server-memory"]
        print(f"🚀 Starting: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print(f"✅ Process started with PID: {process.pid}")
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        message = json.dumps(init_request) + "\n"
        print("📤 Sending initialize...")
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        # Read initialize response
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        response_text = response_line.decode().strip()
        print(f"📥 Initialize response: {response_text}")
        
        if response_text:
            try:
                init_response = json.loads(response_text)
                if "result" in init_response:
                    print("✅ Initialize successful")
                    
                    # Send notifications/initialized
                    initialized_notification = {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized"
                    }
                    
                    message = json.dumps(initialized_notification) + "\n"
                    print("📤 Sending notifications/initialized...")
                    process.stdin.write(message.encode())
                    await process.stdin.drain()
                    
                    # Small delay
                    await asyncio.sleep(0.5)
                    
                    # Send tools/list request
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list"
                    }
                    
                    message = json.dumps(tools_request) + "\n"
                    print("📤 Sending tools/list...")
                    process.stdin.write(message.encode())
                    await process.stdin.drain()
                    
                    # Read tools response
                    tools_response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
                    tools_response_text = tools_response_line.decode().strip()
                    print(f"📥 Tools response: {tools_response_text}")
                    
                    if tools_response_text:
                        try:
                            tools_response = json.loads(tools_response_text)
                            if "result" in tools_response:
                                tools = tools_response["result"].get("tools", [])
                                print(f"🛠️ Found {len(tools)} tools:")
                                for tool in tools:
                                    name = tool.get('name', 'Unknown')
                                    desc = tool.get('description', 'No description')
                                    print(f"   - {name}: {desc}")
                                return len(tools) > 0
                            else:
                                print(f"❌ Tools request failed: {tools_response}")
                                return False
                        except json.JSONDecodeError as e:
                            print(f"❌ Failed to parse tools response: {e}")
                            return False
                    else:
                        print("❌ No tools response received")
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
        
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    finally:
        # Clean up process
        if 'process' in locals():
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()

if __name__ == "__main__":
    success = asyncio.run(test_mcp_async())
    print(f"\n🎯 Async Test: {'✅ PASS - Tools discovered!' if success else '❌ FAIL - No tools found'}")
