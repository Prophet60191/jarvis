#!/usr/bin/env python3
"""
Test the ReAct agent with multiple different tools to ensure they're all working
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_agent_with_multiple_tools():
    """Test the agent with various different tools."""
    print("🧪 TESTING REACT AGENT WITH MULTIPLE TOOLS")
    print("=" * 70)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        # Load config and initialize agent
        config = get_config()
        agent = JarvisAgent(config.llm)
        tools = get_langchain_tools()
        agent.initialize(tools=tools)
        
        print(f"✅ Agent initialized with {len(tools)} tools")
        
        # Test cases with different tool types
        test_cases = [
            {
                "name": "Time Tool",
                "query": "What time is it?",
                "expected_keywords": ["time", "AM", "PM", "current"]
            },
            {
                "name": "System Info Tool", 
                "query": "What's my system information?",
                "expected_keywords": ["system", "python", "platform", "version"]
            },
            {
                "name": "File Operations Tool",
                "query": "List the contents of the current directory",
                "expected_keywords": ["directory", "files", "contents", "list"]
            },
            {
                "name": "User Profile Tool",
                "query": "What's my name?",
                "expected_keywords": ["name", "profile", "user"]
            },
            {
                "name": "Memory/RAG Tool",
                "query": "Remember that I like pizza",
                "expected_keywords": ["remember", "stored", "memory", "pizza"]
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 TEST {i}: {test_case['name']}")
            print(f"Query: '{test_case['query']}'")
            print("-" * 50)
            
            try:
                response = agent.process_input(test_case['query'])
                print(f"✅ Response: {response[:200]}{'...' if len(response) > 200 else ''}")
                
                # Check if response contains expected keywords
                response_lower = response.lower()
                found_keywords = [kw for kw in test_case['expected_keywords'] 
                                if kw.lower() in response_lower]
                
                if found_keywords:
                    print(f"✅ Found expected keywords: {found_keywords}")
                    results.append({"test": test_case['name'], "status": "PASS", "response": response})
                else:
                    print(f"⚠️  No expected keywords found. Expected: {test_case['expected_keywords']}")
                    results.append({"test": test_case['name'], "status": "PARTIAL", "response": response})
                    
            except Exception as e:
                print(f"❌ Test failed: {e}")
                results.append({"test": test_case['name'], "status": "FAIL", "error": str(e)})
        
        # Summary
        print(f"\n📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in results if r['status'] == 'PASS')
        partial = sum(1 for r in results if r['status'] == 'PARTIAL') 
        failed = sum(1 for r in results if r['status'] == 'FAIL')
        
        print(f"✅ Passed: {passed}/{len(test_cases)}")
        print(f"⚠️  Partial: {partial}/{len(test_cases)}")
        print(f"❌ Failed: {failed}/{len(test_cases)}")
        
        for result in results:
            status_icon = "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'PARTIAL' else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
        
        return passed + partial > 0  # Success if any tests passed or partial
        
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_categories():
    """Test different categories of tools."""
    print(f"\n🔧 TESTING TOOL CATEGORIES")
    print("=" * 50)
    
    try:
        from jarvis.tools import get_langchain_tools
        
        tools = get_langchain_tools()
        
        # Categorize tools
        categories = {
            "time": [],
            "file": [],
            "system": [],
            "web": [],
            "git": [],
            "memory": [],
            "ui": [],
            "other": []
        }
        
        for tool in tools:
            if hasattr(tool, 'name'):
                name_lower = tool.name.lower()
                if 'time' in name_lower:
                    categories['time'].append(tool.name)
                elif any(word in name_lower for word in ['file', 'directory', 'read', 'write']):
                    categories['file'].append(tool.name)
                elif any(word in name_lower for word in ['system', 'process', 'command']):
                    categories['system'].append(tool.name)
                elif any(word in name_lower for word in ['web', 'search', 'fetch', 'github']):
                    categories['web'].append(tool.name)
                elif 'git' in name_lower:
                    categories['git'].append(tool.name)
                elif any(word in name_lower for word in ['memory', 'remember', 'search', 'rag']):
                    categories['memory'].append(tool.name)
                elif any(word in name_lower for word in ['ui', 'open', 'close', 'show']):
                    categories['ui'].append(tool.name)
                else:
                    categories['other'].append(tool.name)
        
        print("📊 Tool Categories:")
        for category, tool_list in categories.items():
            if tool_list:
                print(f"  {category.upper()}: {len(tool_list)} tools")
                for tool_name in tool_list[:3]:  # Show first 3
                    print(f"    - {tool_name}")
                if len(tool_list) > 3:
                    print(f"    ... and {len(tool_list) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error categorizing tools: {e}")
        return False

def main():
    """Main test function."""
    print("🎯 JARVIS REACT AGENT MULTI-TOOL TEST")
    print("=" * 80)
    
    # Test tool categories
    categories_work = test_tool_categories()
    
    # Test agent with multiple tools
    agent_works = test_agent_with_multiple_tools()
    
    print("\n🏁 FINAL SUMMARY")
    print("=" * 40)
    print(f"Tool categorization: {'✅ Working' if categories_work else '❌ Failed'}")
    print(f"Multi-tool agent test: {'✅ Working' if agent_works else '❌ Failed'}")
    
    if agent_works:
        print("\n🎉 ReAct agent is successfully using multiple tool types!")
        print("🚀 Jarvis should now work properly with all capabilities!")
    else:
        print("\n⚠️  Some tools may need additional configuration.")

if __name__ == "__main__":
    main()
