#!/usr/bin/env python3
"""
Quick diagnostic for Jarvis conversation issues.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def check_conversation_flow():
    """Check if our terminal UI changes broke the conversation flow."""
    print("🔍 JARVIS CONVERSATION DIAGNOSTIC")
    print("=" * 60)
    
    print("🎯 Likely Issues:")
    print("─" * 30)
    print("1. Speech recognition not working")
    print("2. Response display broken")
    print("3. Terminal UI changes broke conversation flow")
    print("4. Agent/LLM not responding")
    
    print("\n🔧 Quick Fixes to Try:")
    print("─" * 30)
    print("1. Check microphone permissions")
    print("2. Verify speech recognition is working")
    print("3. Test if responses are generated but not displayed")
    print("4. Check if terminal UI changes broke message display")
    
    print("\n📋 What We Changed That Could Cause This:")
    print("─" * 30)
    print("• Modified terminal_ui.py show_user_input()")
    print("• Modified terminal_ui.py show_jarvis_response()")
    print("• Changed visual_feedback.py status indicators")
    print("• Modified conversation display flow")
    
    print("\n🚨 Most Likely Cause:")
    print("─" * 30)
    print("The terminal UI changes may have broken the conversation")
    print("display system. The conversations start but responses")
    print("aren't being shown properly.")


def suggest_immediate_fixes():
    """Suggest immediate fixes."""
    print("\n🛠️ IMMEDIATE FIXES TO TRY:")
    print("=" * 60)
    
    print("1. **Quick Test - Check Logs:**")
    print("   • Look at Jarvis logs to see if responses are generated")
    print("   • Check if speech recognition is working")
    print()
    
    print("2. **Revert Terminal UI Changes:**")
    print("   • The issue likely started after our UI cleanup")
    print("   • We may have broken the response display")
    print()
    
    print("3. **Test Speech Recognition:**")
    print("   • Speak clearly and wait longer")
    print("   • Check if microphone permissions are working")
    print()
    
    print("4. **Check Agent Response:**")
    print("   • The LLM might be failing to generate responses")
    print("   • Or responses are generated but not displayed")


def provide_debug_steps():
    """Provide step-by-step debugging."""
    print("\n🔬 DEBUG STEPS:")
    print("=" * 60)
    
    print("Step 1: Check if speech is being recognized")
    print("   • You should see 'You: [your question]' after speaking")
    print("   • If missing, speech recognition is broken")
    print()
    
    print("Step 2: Check if responses are generated")
    print("   • Look for 'Jarvis: [response]' after processing")
    print("   • If missing, either LLM failed or display is broken")
    print()
    
    print("Step 3: Check Jarvis logs")
    print("   • Run with verbose logging to see what's happening")
    print("   • Look for errors in speech recognition or LLM calls")
    print()
    
    print("Step 4: Test with simple commands")
    print("   • Try 'what time is it' - should be quick to respond")
    print("   • Try 'hello' - simple response")


def main():
    """Main diagnostic function."""
    check_conversation_flow()
    suggest_immediate_fixes()
    provide_debug_steps()
    
    print("\n🎯 MOST LIKELY SOLUTION:")
    print("=" * 60)
    print("The terminal UI cleanup we just did probably broke")
    print("the conversation display. We need to check:")
    print()
    print("1. Are user inputs being displayed?")
    print("2. Are Jarvis responses being displayed?")
    print("3. Did our emoji removal break the message flow?")
    print()
    print("💡 Quick fix: Check the conversation.py file to see")
    print("   if it's still calling the right terminal UI methods")
    print("   for displaying user input and responses.")


if __name__ == "__main__":
    main()
