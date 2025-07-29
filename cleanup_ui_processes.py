#!/usr/bin/env python3
"""
Jarvis UI Process Cleanup Tool

Cleans up zombie UI processes and provides AppManager maintenance.
"""

import sys
import os
from pathlib import Path

# Add jarvis to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "jarvis"))

try:
    import psutil
except ImportError:
    print("❌ psutil required. Install with: pip install psutil")
    sys.exit(1)

def main():
    print("🧹 Jarvis UI Process Cleanup Tool")
    print("=" * 40)
    
    # Find UI processes
    ui_processes = []
    ui_scripts = ['jarvis_ui.py', 'jarvis_settings_app.py', 'rag_app.py']
    
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline:
                cmdline_str = ' '.join(cmdline)
                for script in ui_scripts:
                    if script in cmdline_str and 'python' in cmdline_str:
                        ui_processes.append(proc)
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not ui_processes:
        print("✅ No UI processes found")
        return
    
    print(f"Found {len(ui_processes)} UI processes:")
    for proc in ui_processes:
        try:
            cmdline = ' '.join(proc.cmdline())
            print(f"  PID {proc.pid}: {cmdline[:60]}...")
        except:
            print(f"  PID {proc.pid}: <access denied>")
    
    if input("\nTerminate all? (y/N): ").lower() == 'y':
        for proc in ui_processes:
            try:
                proc.terminate()
                proc.wait(timeout=3)
                print(f"✅ Terminated PID {proc.pid}")
            except:
                try:
                    proc.kill()
                    print(f"⚠️  Force killed PID {proc.pid}")
                except:
                    print(f"❌ Failed to kill PID {proc.pid}")

if __name__ == "__main__":
    main()
