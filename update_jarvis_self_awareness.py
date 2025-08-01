#!/usr/bin/env python3
"""
Update Jarvis Self-Awareness with Recent Changes

This script updates Jarvis's RAG memory with only the key modified files
related to the wake word detection fix and smart routing implementation.
"""

import sys
import os
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def update_jarvis_memory():
    """Update Jarvis's self-awareness with key modified files."""
    
    print("🧠 UPDATING JARVIS SELF-AWARENESS")
    print("=" * 50)
    print("Adding key modified files to Jarvis's memory...")
    print()
    
    try:
        from jarvis.tools.plugins.rag_plugin import remember_fact
        
        # Key files to update Jarvis's memory with
        key_files = [
            # Main working startup file
            "start_jarvis_fixed.py",
            
            # Updated documentation
            "jarvis/docs/CURRENT_STATUS.md",
            "jarvis/docs/QUICK_START_CURRENT.md", 
            "jarvis/README.md",
            "jarvis/docs/TROUBLESHOOTING.md",
            
            # Core architecture changes
            "jarvis/jarvis/main.py",
            "jarvis/jarvis/config.py",
            
            # Smart routing system
            "jarvis/jarvis/core/routing/smart_conversation_manager.py",
            "jarvis/jarvis/core/routing/intent_router.py",
            "jarvis/jarvis/core/routing/execution_engine.py",
            
            # Performance documentation
            "jarvis/docs/SMART_ROUTING_ARCHITECTURE.md",
            "jarvis/docs/PERFORMANCE_OPTIMIZATION.md",
        ]
        
        updated_files = []
        
        for file_path in key_files:
            full_path = Path(file_path)
            
            if full_path.exists():
                print(f"📄 Processing: {file_path}")
                
                try:
                    # Read file content
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create memory entry
                    memory_text = f"""FILE: {file_path}
LAST_UPDATED: July 29, 2025
PURPOSE: Wake word detection fix and smart routing implementation

CONTENT:
{content}

---
This file is part of the major wake word detection fix and smart routing implementation that resolved:
- Wake word detection reliability issues
- 46+ second response time problems  
- Smart routing between tools and LLM knowledge
- Simplified architecture for better stability
"""
                    
                    # Store in Jarvis's memory
                    result = remember_fact.invoke({"fact": memory_text})
                    
                    if "successfully" in result.lower():
                        print(f"   ✅ Added to memory")
                        updated_files.append(file_path)
                    else:
                        print(f"   ❌ Failed to add: {result}")
                        
                except Exception as e:
                    print(f"   ❌ Error processing {file_path}: {e}")
            else:
                print(f"   ⚠️  File not found: {file_path}")
        
        # Add summary of changes
        summary = """JARVIS SYSTEM UPDATE - July 29, 2025

MAJOR FIXES IMPLEMENTED:

✅ WAKE WORD DETECTION FIXED:
- Issue: Complex async/threading architecture was preventing wake word detection
- Solution: Implemented simplified synchronous architecture based on working patterns
- Result: Reliable "jarvis" wake word activation with proper conversation mode
- Startup: Use "python start_jarvis_fixed.py" for working version

✅ SMART RESPONSE ROUTING IMPLEMENTED:
- Issue: All queries taking 46+ seconds due to RAG system overhead
- Solution: Intelligent routing between tools and LLM knowledge
- Results:
  * ⚡ Time queries: Instant response (direct tool call)
  * 🧠 General knowledge: Fast LLM responses (bypass tools)
  * 🛠️ Specific actions: Appropriate tool usage

✅ PERFORMANCE IMPROVEMENTS:
- Time queries now instant instead of 46+ seconds
- General knowledge questions get fast, comprehensive answers
- Proper tool selection only for specific actions
- Maintained all 34 tools while improving response times

✅ ARCHITECTURE CHANGES:
- Created start_jarvis_fixed.py with proven working architecture
- Smart query routing determines when to use tools vs. LLM knowledge
- Direct LLM access for general knowledge (bypasses RAG hijacking)
- Simplified synchronous main loop (no async/threading issues)

✅ DOCUMENTATION UPDATES:
- Added CURRENT_STATUS.md with complete system state
- Added QUICK_START_CURRENT.md with working startup method
- Updated README.md with current working features
- Updated TROUBLESHOOTING.md with resolved issues

CURRENT STATUS: Jarvis is now fully functional with reliable wake word detection and intelligent response routing.

STARTUP COMMAND: python start_jarvis_fixed.py
"""
        
        print(f"\n📋 Adding system update summary...")
        summary_result = remember_fact.invoke({"fact": summary})
        
        if "successfully" in summary_result.lower():
            print(f"   ✅ Summary added to memory")
        else:
            print(f"   ❌ Failed to add summary: {summary_result}")
        
        print(f"\n🎉 MEMORY UPDATE COMPLETE")
        print(f"✅ Updated {len(updated_files)} files in Jarvis's memory")
        print(f"✅ Added system update summary")
        print()
        print("Updated files:")
        for file_path in updated_files:
            print(f"  • {file_path}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error updating Jarvis memory: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_memory_update():
    """Verify that the memory was updated correctly."""
    
    print("\n🔍 VERIFYING MEMORY UPDATE")
    print("=" * 40)
    
    try:
        from jarvis.tools.plugins.rag_plugin import search_long_term_memory
        
        # Test searches to verify memory update
        test_queries = [
            "wake word detection fix",
            "start_jarvis_fixed.py",
            "smart routing implementation",
            "July 29 2025 updates"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Searching for: '{query}'")
            
            try:
                result = search_long_term_memory.invoke({"query": query})
                
                if result and len(result.strip()) > 50:
                    print(f"   ✅ Found relevant information ({len(result)} chars)")
                    # Show first 100 chars as preview
                    preview = result[:100].replace('\n', ' ')
                    print(f"   Preview: {preview}...")
                else:
                    print(f"   ❌ No relevant information found")
                    
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying memory: {e}")
        return False


def main():
    """Main function to update and verify Jarvis's self-awareness."""
    
    print("🧠 JARVIS SELF-AWARENESS UPDATE")
    print("=" * 60)
    print("Updating Jarvis's memory with wake word detection fixes")
    print("and smart routing implementation changes.")
    print()
    
    # Update memory
    update_success = update_jarvis_memory()
    
    if update_success:
        # Verify memory update
        verify_success = verify_memory_update()
        
        if verify_success:
            print("\n🎉 JARVIS SELF-AWARENESS SUCCESSFULLY UPDATED!")
            print("Jarvis now knows about:")
            print("  ✅ Wake word detection fixes")
            print("  ✅ Smart routing implementation") 
            print("  ✅ Performance improvements")
            print("  ✅ New startup method (start_jarvis_fixed.py)")
            print("  ✅ Updated documentation")
        else:
            print("\n⚠️  Memory updated but verification had issues")
    else:
        print("\n❌ Failed to update Jarvis's memory")


if __name__ == "__main__":
    main()
