#!/usr/bin/env python3
"""
Test the robust path finding approach.
"""

import os

def test_robust_path():
    """Test the robust path finding."""
    print("🔍 TESTING ROBUST PATH FINDING")
    print("=" * 50)
    
    # Simulate the robust path finding
    current_file = os.path.abspath("jarvis/jarvis/tools/plugins/jarvis_ui_tool.py")
    print(f"Current file: {current_file}")
    
    # Walk up the directory tree to find the project root (contains rag_app.py)
    search_dir = os.path.dirname(current_file)
    project_root = None
    
    print(f"Starting search from: {search_dir}")
    
    for i in range(10):  # Limit search to prevent infinite loop
        print(f"  Checking: {search_dir}")
        if os.path.exists(os.path.join(search_dir, "rag_app.py")):
            project_root = search_dir
            print(f"  ✅ Found project root: {project_root}")
            break
        parent = os.path.dirname(search_dir)
        if parent == search_dir:  # Reached filesystem root
            print(f"  ❌ Reached filesystem root")
            break
        search_dir = parent
    
    if not project_root:
        # Fallback: assume we're in the project root
        project_root = os.getcwd()
        print(f"Fallback to current directory: {project_root}")
    
    # Try desktop app first (preferred)
    desktop_script = os.path.join(project_root, "jarvis", "jarvis_settings_app.py")
    
    print(f"\nFinal result:")
    print(f"Project root: {project_root}")
    print(f"Settings script: {desktop_script}")
    print(f"Exists: {os.path.exists(desktop_script)}")
    
    if os.path.exists(desktop_script):
        print("✅ ROBUST PATH FINDING WORKS!")
    else:
        print("❌ Still not finding the correct path")
        
        # Show what files actually exist
        print(f"\nFiles in project root:")
        if os.path.exists(project_root):
            for item in os.listdir(project_root):
                print(f"  {item}")
        
        print(f"\nFiles in jarvis subdirectory:")
        jarvis_dir = os.path.join(project_root, "jarvis")
        if os.path.exists(jarvis_dir):
            for item in os.listdir(jarvis_dir):
                print(f"  {item}")

def main():
    test_robust_path()

if __name__ == "__main__":
    main()
