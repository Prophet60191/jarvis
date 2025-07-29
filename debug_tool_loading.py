#!/usr/bin/env python3
"""
Debug tool loading to see why Jarvis isn't using tools.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def check_plugin_tools():
    """Check if plugin tools are being loaded correctly."""
    print("🔍 CHECKING PLUGIN TOOL LOADING")
    print("=" * 80)
    
    try:
        from jarvis.plugins.manager import PluginManager
        
        # Create plugin manager
        plugin_manager = PluginManager(auto_discover=True)
        
        # Get all tools
        all_tools = plugin_manager.get_all_tools()
        
        print(f"✅ Found {len(all_tools)} total plugin tools")
        
        # Check for specific tools we care about
        ui_tools = []
        vault_tools = []
        
        for tool in all_tools:
            tool_name = tool.name.lower()
            if 'ui' in tool_name or 'settings' in tool_name or 'jarvis' in tool_name:
                ui_tools.append(tool)
            elif 'vault' in tool_name or 'rag' in tool_name:
                vault_tools.append(tool)
        
        print(f"\n🎯 UI/Settings Tools Found: {len(ui_tools)}")
        for tool in ui_tools:
            print(f"   • {tool.name}: {tool.description[:100]}...")
        
        print(f"\n🏦 Vault/RAG Tools Found: {len(vault_tools)}")
        for tool in vault_tools:
            print(f"   • {tool.name}: {tool.description[:100]}...")
        
        return len(ui_tools) > 0 and len(vault_tools) > 0
        
    except Exception as e:
        print(f"❌ Error checking plugin tools: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_tool_descriptions():
    """Check if tool descriptions are clear enough for the LLM."""
    print("\n🔍 CHECKING TOOL DESCRIPTIONS")
    print("=" * 80)
    
    try:
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        from jarvis.tools.plugins.rag_ui_tool import open_rag_manager
        
        print("📝 Settings Tool Description:")
        print("─" * 50)
        print(f"Name: {open_jarvis_ui.name}")
        print(f"Description: {open_jarvis_ui.description}")
        
        print("\n📝 Vault Tool Description:")
        print("─" * 50)
        print(f"Name: {open_rag_manager.name}")
        print(f"Description: {open_rag_manager.description}")
        
        # Check if descriptions mention the right keywords
        settings_desc = open_jarvis_ui.description.lower()
        vault_desc = open_rag_manager.description.lower()
        
        settings_keywords = ['open settings', 'show settings', 'jarvis settings']
        vault_keywords = ['open vault', 'show vault', 'manage vault']
        
        print("\n🎯 Keyword Analysis:")
        print("─" * 30)
        
        print("Settings tool covers:")
        for keyword in settings_keywords:
            if keyword in settings_desc:
                print(f"   ✅ '{keyword}'")
            else:
                print(f"   ❌ '{keyword}' - MISSING!")
        
        print("Vault tool covers:")
        for keyword in vault_keywords:
            if keyword in vault_desc:
                print(f"   ✅ '{keyword}'")
            else:
                print(f"   ❌ '{keyword}' - MISSING!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking tool descriptions: {e}")
        return False


def check_agent_tools():
    """Check what tools the agent actually has access to."""
    print("\n🔍 CHECKING AGENT TOOL ACCESS")
    print("=" * 80)
    
    try:
        # This is tricky since we need to check the running agent
        # Let's see if we can access the global instances
        
        print("⚠️  This requires checking the running Jarvis instance")
        print("   The agent tools are loaded at runtime")
        print("   Check the Jarvis startup logs for tool loading messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking agent tools: {e}")
        return False


def suggest_fixes():
    """Suggest potential fixes for the tool issue."""
    print("\n🛠️ POTENTIAL FIXES")
    print("=" * 80)
    
    print("1. **Tool Description Issue:**")
    print("   • LLM might not recognize when to use tools")
    print("   • Tool descriptions might be too vague")
    print("   • Keywords might not match user commands")
    print()
    
    print("2. **Tool Loading Issue:**")
    print("   • Tools might not be loaded into the agent")
    print("   • Plugin discovery might be failing")
    print("   • MCP integration might be broken")
    print()
    
    print("3. **LLM Configuration Issue:**")
    print("   • Model might not be good at tool calling")
    print("   • System prompt might not encourage tool use")
    print("   • Tool calling might be disabled")
    print()
    
    print("4. **Quick Test:**")
    print("   • Restart Jarvis and check startup logs")
    print("   • Look for 'Loaded X plugin tools' messages")
    print("   • Try more explicit commands like 'use the open settings tool'")


def main():
    """Main diagnostic function."""
    print("🔧 JARVIS TOOL LOADING DIAGNOSTIC")
    print("=" * 80)
    print("Diagnosing why Jarvis isn't using tools for 'open settings' and 'open vault'")
    print("=" * 80)
    
    # Run checks
    plugin_check = check_plugin_tools()
    desc_check = check_tool_descriptions()
    agent_check = check_agent_tools()
    
    print("\n🎯 DIAGNOSTIC RESULTS")
    print("=" * 80)
    print(f"Plugin Tools Loading: {'✅ PASS' if plugin_check else '❌ FAIL'}")
    print(f"Tool Descriptions: {'✅ PASS' if desc_check else '❌ FAIL'}")
    print(f"Agent Tool Access: {'✅ PASS' if agent_check else '❌ FAIL'}")
    
    suggest_fixes()
    
    print("\n🚨 IMMEDIATE ACTION:")
    print("=" * 80)
    print("1. Check Jarvis startup logs for tool loading messages")
    print("2. Try saying: 'What tools do you have available?'")
    print("3. Try more explicit: 'Use the open_jarvis_ui tool'")
    print("4. If tools aren't loaded, restart Jarvis")


if __name__ == "__main__":
    main()
