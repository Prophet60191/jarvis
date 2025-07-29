#!/usr/bin/env python3
"""
Live Conversation TTS Debug

This script monitors the actual conversation flow to identify
where TTS is being skipped during real usage.
"""

import sys
import logging
import threading
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('conversation_debug.log')
    ]
)

class TTSMonitor:
    """Monitor TTS calls and track when they're skipped."""
    
    def __init__(self):
        self.tts_calls = []
        self.response_count = 0
        self.tts_success_count = 0
        self.tts_failure_count = 0
        
    def log_response(self, response_text):
        """Log when a response is generated."""
        self.response_count += 1
        print(f"\n📝 Response #{self.response_count}: '{response_text[:50]}...'")
        self.tts_calls.append({
            'response_num': self.response_count,
            'text': response_text,
            'tts_attempted': False,
            'tts_success': False,
            'timestamp': time.time()
        })
        
    def log_tts_attempt(self, response_text):
        """Log when TTS is attempted."""
        # Find the matching response
        for call in reversed(self.tts_calls):
            if call['text'] == response_text:
                call['tts_attempted'] = True
                print(f"🔊 TTS attempted for response #{call['response_num']}")
                break
                
    def log_tts_success(self, response_text):
        """Log when TTS succeeds."""
        for call in reversed(self.tts_calls):
            if call['text'] == response_text and call['tts_attempted']:
                call['tts_success'] = True
                self.tts_success_count += 1
                print(f"✅ TTS succeeded for response #{call['response_num']}")
                break
                
    def log_tts_failure(self, response_text, error):
        """Log when TTS fails."""
        for call in reversed(self.tts_calls):
            if call['text'] == response_text and call['tts_attempted']:
                call['tts_error'] = str(error)
                self.tts_failure_count += 1
                print(f"❌ TTS failed for response #{call['response_num']}: {error}")
                break
                
    def get_summary(self):
        """Get summary of TTS performance."""
        skipped = self.response_count - sum(1 for call in self.tts_calls if call['tts_attempted'])
        return {
            'total_responses': self.response_count,
            'tts_attempted': sum(1 for call in self.tts_calls if call['tts_attempted']),
            'tts_succeeded': self.tts_success_count,
            'tts_failed': self.tts_failure_count,
            'tts_skipped': skipped
        }

# Global monitor instance
monitor = TTSMonitor()

def patch_conversation_system():
    """Patch the conversation system to monitor TTS calls."""
    
    # Patch the respond method
    from jarvis.core.conversation import ConversationManager
    original_respond = ConversationManager.respond
    
    def monitored_respond(self, response_text):
        """Monitored version of respond method."""
        monitor.log_response(response_text)
        
        # Call original method
        try:
            result = original_respond(self, response_text)
            return result
        except Exception as e:
            print(f"❌ Respond method failed: {e}")
            raise
    
    ConversationManager.respond = monitored_respond
    
    # Patch the speech manager speak_text method
    from jarvis.core.speech import SpeechManager
    original_speak_text = SpeechManager.speak_text
    
    def monitored_speak_text(self, text, wait=True):
        """Monitored version of speak_text method."""
        monitor.log_tts_attempt(text)
        
        try:
            result = original_speak_text(self, text, wait)
            monitor.log_tts_success(text)
            return result
        except Exception as e:
            monitor.log_tts_failure(text, e)
            raise
    
    SpeechManager.speak_text = monitored_speak_text
    
    print("✅ Conversation system patched for monitoring")

def run_live_test():
    """Run a live conversation test."""
    print("🔧 Live Conversation TTS Monitor")
    print("=" * 60)
    print("This will monitor actual conversation TTS calls.")
    print("Speak to Jarvis and watch for TTS patterns.\n")
    
    try:
        # Patch the system
        patch_conversation_system()
        
        # Import and start Jarvis
        from jarvis.config import get_config
        from jarvis.core.conversation import ConversationManager
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        config = get_config()
        
        # Create agent
        agent = JarvisAgent(config.llm)
        tools = get_langchain_tools()
        agent.initialize(tools)
        
        # Create speech manager
        from jarvis.core.speech import SpeechManager
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()

        # Create conversation manager
        conversation = ConversationManager(config.conversation, speech_manager, agent)
        conversation.initialize()
        
        print("🚀 Jarvis conversation system started")
        print("🎤 Speak to Jarvis and watch the TTS monitoring...")
        print("📊 Press Ctrl+C to see summary\n")
        
        # Start conversation loop
        conversation.start_conversation()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
        
        # Show summary
        summary = monitor.get_summary()
        print("\n📊 TTS Monitoring Summary:")
        print("=" * 40)
        print(f"Total Responses: {summary['total_responses']}")
        print(f"TTS Attempted: {summary['tts_attempted']}")
        print(f"TTS Succeeded: {summary['tts_succeeded']}")
        print(f"TTS Failed: {summary['tts_failed']}")
        print(f"TTS Skipped: {summary['tts_skipped']}")
        
        if summary['tts_skipped'] > 0:
            print(f"\n⚠️  {summary['tts_skipped']} responses had NO TTS attempt!")
            print("This indicates the conversation system is not calling TTS.")
        
        if summary['tts_failed'] > 0:
            print(f"\n❌ {summary['tts_failed']} TTS calls failed")
            print("Check the logs above for specific error details.")
        
        # Show detailed call log
        print("\n📋 Detailed Call Log:")
        for i, call in enumerate(monitor.tts_calls, 1):
            status = "✅" if call['tts_success'] else "❌" if call['tts_attempted'] else "⚠️ "
            print(f"{status} Response {call['response_num']}: TTS {'✓' if call['tts_attempted'] else '✗'}")
        
    except Exception as e:
        print(f"❌ Live test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    try:
        run_live_test()
    except Exception as e:
        print(f"❌ Debug script error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Debug cancelled by user")
    except Exception as e:
        print(f"\n❌ Debug script error: {e}")
        sys.exit(1)
