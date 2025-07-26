#!/usr/bin/env python3
"""
Jarvis Voice Assistant Startup Script

This script starts the Jarvis voice assistant with Apple TTS backend
for optimal compatibility and performance on Apple Silicon Macs.
"""

import os
import sys

def main():
    """Main startup function."""
    print("🤖 Starting Jarvis Voice Assistant (100% Local)...")
    print("=" * 70)
    print("🎤 Speech Recognition: Whisper (Local)")
    print("🍎 Text-to-Speech: Apple System Voices")
    print("🧠 AI Brain: Ollama (Local)")
    print("🔒 Complete Privacy - No Internet Required")
    print("=" * 70)
    print("💡 Say 'Jarvis' to activate voice interaction")
    print("=" * 70)

    try:
        # Import and run Jarvis
        from jarvis.main import main as jarvis_main
        jarvis_main()
    except KeyboardInterrupt:
        print("\n🛑 Jarvis shutdown requested by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting Jarvis: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
