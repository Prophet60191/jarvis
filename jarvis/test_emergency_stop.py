#!/usr/bin/env python3
"""
Test script for Emergency Stop functionality.

This script demonstrates the emergency stop system working during
various operations like TTS, processing, etc.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jarvis.core.emergency_stop import setup_emergency_stop

def simulate_tts_speaking():
    """Simulate TTS speaking that can be interrupted."""
    print("🔊 Simulating TTS speaking...")
    print("   (This would normally be uninterruptible)")
    for i in range(10):
        print(f"   Speaking... {i+1}/10")
        time.sleep(1)
    print("✅ TTS finished normally")

def simulate_llm_processing():
    """Simulate LLM processing that can be interrupted."""
    print("🧠 Simulating LLM processing...")
    print("   (This would normally take time to complete)")
    for i in range(15):
        print(f"   Processing... {i+1}/15")
        time.sleep(0.5)
    print("✅ LLM processing finished normally")

def main():
    """Test emergency stop functionality."""
    print("🔧 Emergency Stop Test")
    print("=" * 30)
    
    # Setup emergency stop system
    print("Setting up emergency stop system...")
    
    # Create mock components for testing
    class MockComponent:
        def __init__(self, name):
            self.name = name
            self.stopped = False
        
        def stop_listening(self):
            print(f"🛑 {self.name}: Stopped listening")
            self.stopped = True
        
        def stop_speaking(self):
            print(f"🛑 {self.name}: Stopped speaking")
            self.stopped = True
        
        def cleanup(self):
            print(f"🛑 {self.name}: Cleaned up")
            self.stopped = True
        
        def stop(self):
            print(f"🛑 {self.name}: Stopped")
            self.stopped = True
        
        def interrupt(self):
            print(f"🛑 {self.name}: Interrupted")
            self.stopped = True
    
    # Create mock components
    mock_speech = MockComponent("SpeechManager")
    mock_agent = MockComponent("JarvisAgent")
    mock_conversation = MockComponent("ConversationManager")
    mock_tts = MockComponent("TTSManager")
    
    # Setup emergency stop with mock components
    manager = setup_emergency_stop(
        speech_manager=mock_speech,
        agent=mock_agent,
        conversation_manager=mock_conversation,
        tts_manager=mock_tts
    )
    
    print("\n🎯 Emergency stop system is now active!")
    print("\n📋 Available stop methods:")
    print("   1. Ctrl+C - Enhanced signal handler (most reliable)")
    if manager._keyboard_available:
        print("   2. F12 - Emergency hotkey")
    print("\n💡 Try pressing Ctrl+C or F12 during the simulation below:")
    print("   The system should stop immediately and clean up all components")
    
    input("\nPress Enter to start simulation...")
    
    try:
        print("\n🚀 Starting simulation...")
        print("   (Press Ctrl+C or F12 to test emergency stop)")
        
        # Simulate various operations
        simulate_tts_speaking()
        simulate_llm_processing()
        
        print("\n✅ All simulations completed normally")
        print("   (Emergency stop was not triggered)")
        
    except KeyboardInterrupt:
        print("\n🛑 Ctrl+C detected - emergency stop would have been triggered")
    except SystemExit:
        print("\n🛑 Emergency stop was triggered!")
    
    print("\n🎉 Emergency stop test completed!")

if __name__ == "__main__":
    main()
