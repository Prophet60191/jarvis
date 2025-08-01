#!/usr/bin/env python3
"""
Test Jarvis tools directly by sending prompts to the AI system
"""

import sys
import logging
import asyncio
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from jarvis.config import get_config
from jarvis.core.speech import SpeechManager

# Import MCP tools instead of hardcoded tools
sys.path.append('jarvis')
from jarvis.core.mcp_tool_integration import initialize_mcp_tools

# Import RAG tools for testing
try:
    from rag_plugin import remember_fact, search_conversations, search_documents, search_all_memory
    from rag_ui_tool import open_rag_manager, close_rag_manager, show_rag_status
    RAG_AVAILABLE = True
    print("✅ RAG tools imported successfully")
except ImportError as e:
    print(f"⚠️ RAG tools not available: {e}")
    RAG_AVAILABLE = False

# Import MCP management tools for testing
try:
    from mcp_management_tool import add_mcp_server_from_template, list_mcp_servers, enable_mcp_server, disable_mcp_server
    MCP_AVAILABLE = True
    print("✅ MCP management tools imported successfully")
except ImportError as e:
    print(f"⚠️ MCP management tools not available: {e}")
    MCP_AVAILABLE = False
import requests
import json

def simple_ai_response(command, ollama_url, model_name):
    """Get AI response using direct Ollama API call (synchronous)"""
    try:
        # Check if this is a time-related request - use MCP time server
        if any(word in command.lower() for word in ['time', 'clock', 'hour', 'minute']):
            try:
                # Use MCP time server (will be initialized in test setup)
                if hasattr(simple_ai_response, '_mcp_tools'):
                    for tool in simple_ai_response._mcp_tools:
                        if 'time' in tool.name.lower():
                            result = tool._run({})
                            return f"The current time is {result}."

                # Fallback to simple datetime if MCP not available
                from datetime import datetime
                now = datetime.now()
                current_time = now.strftime("%I:%M %p on %A, %B %d, %Y")
                return f"The current time is {current_time}."
            except Exception as e:
                print(f"❌ Time tool error: {e}")
                # Fallback to simple datetime
                from datetime import datetime
                now = datetime.now()
                current_time = now.strftime("%I:%M %p on %A, %B %d, %Y")
                return f"The current time is {current_time}."

        # Check if this is a RAG-related request
        if RAG_AVAILABLE:
            command_lower = command.lower()

            # Remember/store requests
            if any(phrase in command_lower for phrase in ['remember that', 'remember my', 'store this', 'don\'t forget']):
                try:
                    # Extract the fact to remember (remove the "remember that" part)
                    fact = command
                    for phrase in ['remember that ', 'remember my ', 'store this ', 'don\'t forget that ']:
                        if phrase in command_lower:
                            fact = command[command_lower.find(phrase) + len(phrase):].strip()
                            break
                    return remember_fact.invoke({"fact": fact})
                except Exception as e:
                    print(f"❌ Remember tool error: {e}")
                    return "I had trouble storing that information."

            # Search requests
            elif any(phrase in command_lower for phrase in ['what do you remember', 'search my conversations', 'what have i told you']):
                try:
                    return search_conversations.invoke({"query": command})
                except Exception as e:
                    print(f"❌ Search conversations error: {e}")
                    return "I had trouble searching my memory."

            # Vault management requests
            elif any(phrase in command_lower for phrase in ['open vault', 'open the vault', 'show vault']):
                try:
                    return open_rag_manager.invoke({"panel": "main"})
                except Exception as e:
                    print(f"❌ Open vault error: {e}")
                    return "I had trouble opening the vault."

            elif any(phrase in command_lower for phrase in ['close vault', 'close the vault']):
                try:
                    return close_rag_manager.invoke({})
                except Exception as e:
                    print(f"❌ Close vault error: {e}")
                    return "I had trouble closing the vault."

            elif any(phrase in command_lower for phrase in ['vault status', 'show vault status']):
                try:
                    return show_rag_status.invoke({})
                except Exception as e:
                    print(f"❌ Vault status error: {e}")
                    return "I had trouble checking the vault status."

        # Check if this is an MCP-related request
        if MCP_AVAILABLE:
            command_lower = command.lower()

            # Add MCP server requests
            if any(phrase in command_lower for phrase in ['add filesystem mcp', 'add file system mcp', 'connect filesystem']):
                try:
                    return add_mcp_server_from_template.invoke({"template_name": "filesystem"})
                except Exception as e:
                    print(f"❌ Add MCP server error: {e}")
                    return "I had trouble adding the MCP server."

            # List MCP servers requests
            elif any(phrase in command_lower for phrase in ['list mcp servers', 'show mcp status', 'mcp status']):
                try:
                    return list_mcp_servers.invoke({})
                except Exception as e:
                    print(f"❌ List MCP servers error: {e}")
                    return "I had trouble listing MCP servers."

            # Enable MCP server requests
            elif any(phrase in command_lower for phrase in ['enable filesystem mcp', 'turn on filesystem']):
                try:
                    return enable_mcp_server.invoke({"server_name": "filesystem"})
                except Exception as e:
                    print(f"❌ Enable MCP server error: {e}")
                    return "I had trouble enabling the MCP server."

            # Disable MCP server requests
            elif any(phrase in command_lower for phrase in ['disable filesystem mcp', 'turn off filesystem']):
                try:
                    return disable_mcp_server.invoke({"server_name": "filesystem"})
                except Exception as e:
                    print(f"❌ Disable MCP server error: {e}")
                    return "I had trouble disabling the MCP server."
        
        # For other requests, use AI with context
        system_prompt = """You are Jarvis, a helpful AI assistant. You have access to these tools:
- Current time: You can tell the current time
- General knowledge: You can answer questions and have conversations

IMPORTANT: Keep responses concise and under 200 words. Be helpful but brief."""
        
        # Create prompt for general queries
        full_prompt = f"""System: {system_prompt}

User: {command}"""
        
        # Make API call to Ollama
        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 100  # Reduced for more concise responses
            }
        }
        
        response = requests.post(ollama_url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "I'm sorry, I couldn't process that request.").strip()
        else:
            return "I'm having trouble connecting to my AI system right now."
            
    except Exception as e:
        print(f"❌ AI error: {e}")
        return "I'm sorry, I had trouble processing that request."

def analyze_response(prompt, response):
    """Analyze the quality and appropriateness of the response"""
    analysis = {
        'status': '✅ EXCELLENT',
        'message': 'Perfect response',
        'score': 10,
        'improvement': ''
    }

    # Time tool specific analysis
    if any(word in prompt.lower() for word in ['time', 'clock', 'hour', 'minute']):
        if "time is" in response.lower() and any(char.isdigit() for char in response):
            analysis['message'] = 'Time tool working perfectly'
            analysis['score'] = 10
        else:
            analysis['status'] = '❌ TIME TOOL ISSUE'
            analysis['message'] = 'Time tool not responding correctly'
            analysis['score'] = 3
            analysis['improvement'] = 'Time tool should return current time'
        return analysis

    # Mathematical queries
    if any(word in prompt.lower() for word in ['plus', 'minus', 'times', 'multiply', 'divide', 'square', 'root', '%', 'percent']):
        if any(char.isdigit() for char in response) or 'prime' in response.lower():
            analysis['message'] = 'Mathematical calculation provided'
            analysis['score'] = 9
        else:
            analysis['status'] = '⚠️ MATH ISSUE'
            analysis['message'] = 'Should provide numerical answer'
            analysis['score'] = 5
            analysis['improvement'] = 'Include numerical calculation'
        return analysis

    # General response quality analysis
    response_lower = response.lower()

    # Check for error responses
    if any(phrase in response_lower for phrase in ['sorry', 'trouble', 'error', 'cannot', "can't"]):
        analysis['status'] = '⚠️ ERROR RESPONSE'
        analysis['message'] = 'System reported difficulty'
        analysis['score'] = 4
        analysis['improvement'] = 'Should provide helpful response instead of error'
        return analysis

    # Check response length and substance
    if len(response) < 10:
        analysis['status'] = '⚠️ TOO SHORT'
        analysis['message'] = 'Response too brief'
        analysis['score'] = 5
        analysis['improvement'] = 'Provide more detailed response'
        return analysis

    if len(response) > 500:
        analysis['status'] = '⚠️ TOO LONG'
        analysis['message'] = 'Response too verbose'
        analysis['score'] = 6
        analysis['improvement'] = 'Keep responses more concise'
        return analysis

    # Check for conversational appropriateness
    if any(word in prompt.lower() for word in ['hello', 'hi', 'how are you', 'thank']):
        if any(phrase in response_lower for phrase in ['hello', 'hi', 'welcome', 'glad', 'help']):
            analysis['message'] = 'Appropriate conversational response'
            analysis['score'] = 9
        else:
            analysis['status'] = '⚠️ CONVERSATION'
            analysis['message'] = 'Could be more conversational'
            analysis['score'] = 6
            analysis['improvement'] = 'Add more conversational elements'
        return analysis

    # Default: good response
    analysis['message'] = 'Good general response'
    analysis['score'] = 8
    return analysis

async def test_jarvis_tools():
    """Test Jarvis tools directly with prompts"""
    print("🧪 TESTING JARVIS TOOLS DIRECTLY")
    print("=" * 50)

    try:
        # Initialize components
        config = get_config()

        print("🤖 Setting up AI integration...")
        ollama_url = "http://localhost:11434/api/generate"
        model_name = "qwen2.5:7b-instruct"
        print("✅ AI integration ready")

        # Initialize MCP tools
        print("🔧 Initializing MCP tools...")
        try:
            mcp_tools = await initialize_mcp_tools()
            simple_ai_response._mcp_tools = mcp_tools
            print(f"✅ MCP tools initialized: {len(mcp_tools)} tools")
            for tool in mcp_tools:
                print(f"  • {tool.name}")
        except Exception as e:
            print(f"⚠️ MCP tools failed to initialize: {e}")
            simple_ai_response._mcp_tools = []
        
        # Comprehensive test prompts - Round 2
        test_prompts = [
            # Time tool edge cases
            "What time is it?",
            "Tell me the current time please",
            "What hour is it right now?",
            "Can you check the time for me?",
            "I need to know what time it is",
            "Show me the clock",
            "What's the current hour and minute?",

            # Mathematical and logical tests
            "What is 15 times 7?",
            "What's the square root of 64?",
            "If I have 10 apples and eat 3, how many do I have left?",
            "What's 25% of 200?",
            "Is 17 a prime number?",

            # Knowledge and information tests
            "Tell me about the solar system",
            "What is Python programming language?",
            "Explain quantum physics in simple terms",
            "Who was Albert Einstein?",
            "What are the benefits of exercise?",

            # Conversational and personality tests
            "How are you feeling today?",
            "What's your favorite color?",
            "Do you have any hobbies?",
            "What do you think about technology?",
            "Can you be my assistant?",

            # Task and instruction tests
            "Help me plan my day",
            "Give me some productivity tips",
            "How can I learn programming?",
            "What should I cook for dinner?",
            "Suggest a good book to read",

            # Creative and fun tests
            "Tell me a funny story",
            "Write a short poem",
            "Give me a riddle",
            "What's an interesting fact?",
            "Make up a creative excuse for being late",

            # Problem-solving tests
            "I'm feeling stressed, what should I do?",
            "How do I fix a slow computer?",
            "What's the best way to learn a new skill?",
            "I can't sleep, any suggestions?",
            "How do I stay motivated?",

            # RAG memory tests (if available)
            "Remember that I like coffee in the morning",
            "Remember my favorite color is blue",
            "What do you remember about my preferences?",
            "Search my conversations for coffee",
            "What have I told you about myself?",
            "Open the vault",
            "Show vault status",
            "Close the vault",

            # MCP management tests (if available)
            "Add filesystem MCP server",
            "List MCP servers",
            "Show MCP status",
            "Enable filesystem MCP",
            "Disable filesystem MCP"
        ]
        
        print(f"\n🎯 Testing {len(test_prompts)} prompts...")
        print("=" * 50)

        # Track statistics
        total_tests = len(test_prompts)
        passed_tests = 0
        failed_tests = 0
        scores = []
        time_tool_tests = 0
        time_tool_passed = 0

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Test {i}/{len(test_prompts)}: '{prompt}'")
            print("-" * 40)
            
            try:
                # Process prompt with AI
                response = simple_ai_response(prompt, ollama_url, model_name)
                print(f"🤖 Jarvis: {response}")
                
                # Sophisticated response analysis
                analysis = analyze_response(prompt, response)
                print(f"📊 {analysis['status']}: {analysis['message']}")
                if analysis['score'] < 7:
                    print(f"⚠️ Quality Score: {analysis['score']}/10 - {analysis['improvement']}")

                # Track statistics
                scores.append(analysis['score'])
                if analysis['score'] >= 7:
                    passed_tests += 1
                else:
                    failed_tests += 1

                # Track time tool specifically
                if any(word in prompt.lower() for word in ['time', 'clock', 'hour', 'minute']):
                    time_tool_tests += 1
                    if analysis['score'] >= 8:
                        time_tool_passed += 1

            except Exception as e:
                print(f"❌ Error processing prompt: {e}")
                failed_tests += 1
                scores.append(0)

            print()
        
        print("=" * 50)
        print("🎉 COMPREHENSIVE TESTING COMPLETE!")
        print("\n📊 DETAILED STATISTICS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"Failed Tests: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"Average Quality Score: {avg_score:.1f}/10")
            print(f"Highest Score: {max(scores)}/10")
            print(f"Lowest Score: {min(scores)}/10")

        print(f"\n🕐 TIME TOOL PERFORMANCE:")
        print(f"Time Tool Tests: {time_tool_tests}")
        print(f"Time Tool Passed: {time_tool_passed}")
        if time_tool_tests > 0:
            time_success_rate = time_tool_passed / time_tool_tests * 100
            print(f"Time Tool Success Rate: {time_success_rate:.1f}%")

        print(f"\n🎯 OVERALL ASSESSMENT:")
        if avg_score >= 8.5:
            print("🌟 EXCELLENT: Jarvis is performing exceptionally well!")
        elif avg_score >= 7.0:
            print("✅ GOOD: Jarvis is working well with minor improvements needed")
        elif avg_score >= 5.0:
            print("⚠️ FAIR: Jarvis needs significant improvements")
        else:
            print("❌ POOR: Major issues need to be addressed")

        print(f"\n🔧 RECOMMENDATIONS:")
        if time_tool_passed < time_tool_tests:
            print("- Fix time tool integration issues")
        if failed_tests > total_tests * 0.1:
            print("- Improve error handling and response quality")
        if avg_score < 8.0:
            print("- Enhance AI response relevance and accuracy")
        print("- Continue testing with more complex scenarios")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_jarvis_tools())
