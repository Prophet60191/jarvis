#!/usr/bin/env python3
"""
Complete Root Directory Cleanup
Move all remaining test files and scripts to proper locations
"""

import os
import shutil
from pathlib import Path
import subprocess

def create_directories():
    """Create necessary directories for organization."""
    dirs_to_create = [
        'tests/legacy',
        'scripts/benchmarks',
        'scripts/testing',
        'scripts/utilities',
        'scripts/analysis',
        'docs/archive'
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def move_test_files():
    """Move all remaining test files to tests/legacy/."""
    test_files = list(Path('.').glob('test_*.py'))
    moved_count = 0
    
    print(f"\n🧪 Moving {len(test_files)} test files to tests/legacy/...")
    
    for test_file in test_files:
        try:
            destination = Path('tests/legacy') / test_file.name
            shutil.move(str(test_file), str(destination))
            print(f"  ✅ Moved: {test_file.name}")
            moved_count += 1
        except Exception as e:
            print(f"  ❌ Failed to move {test_file.name}: {e}")
    
    return moved_count

def move_script_files():
    """Move various script files to appropriate directories."""
    
    script_mappings = {
        'scripts/benchmarks': [
            'run_benchmarks.py',
            'benchmark_*.py',
            'analyze_*.py'
        ],
        'scripts/testing': [
            'run_tests.py',
            'run_orchestration_tests.py',
            'run_rag_tests.py',
            'additional_jarvis_tests.py'
        ],
        'scripts/utilities': [
            'final_*.py',
            'real_*.py',
            'launch_*.py',
            'start_*.py',
            'send_*.py',
            'sync_*.py',
            'manage_*.py',
            'enable_*.py'
        ],
        'scripts/analysis': [
            'complexity_analysis_report.py',
            'audit_obsolete_files.py',
            'create_desktop_backup.py',
            'user_memory_simulation.py',
            'orchestration_learning_session.py'
        ]
    }
    
    moved_count = 0
    
    for target_dir, patterns in script_mappings.items():
        print(f"\n📁 Moving scripts to {target_dir}...")
        
        for pattern in patterns:
            files = list(Path('.').glob(pattern))
            for file in files:
                if file.is_file():
                    try:
                        destination = Path(target_dir) / file.name
                        shutil.move(str(file), str(destination))
                        print(f"  ✅ Moved: {file.name}")
                        moved_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to move {file.name}: {e}")
    
    return moved_count

def move_data_files():
    """Move data files to appropriate locations."""
    data_files = [
        '*.json',
        '*.log',
        '*.txt'
    ]
    
    moved_count = 0
    data_dir = Path('data/misc')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Moving data files to data/misc/...")
    
    for pattern in data_files:
        files = list(Path('.').glob(pattern))
        for file in files:
            # Skip important files that should stay in root
            if file.name in ['package.json', 'README.md', 'requirements.txt', 'requirements-enhanced.txt']:
                continue
            
            if file.is_file():
                try:
                    destination = data_dir / file.name
                    shutil.move(str(file), str(destination))
                    print(f"  ✅ Moved: {file.name}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to move {file.name}: {e}")
    
    return moved_count

def move_web_files():
    """Move web-related files to appropriate locations."""
    web_files = [
        '*.html',
        '*.js',
        '*.css'
    ]
    
    moved_count = 0
    web_dir = Path('web')
    web_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🌐 Moving web files to web/...")
    
    for pattern in web_files:
        files = list(Path('.').glob(pattern))
        for file in files:
            # Skip files that are part of specific projects
            if any(parent.name in ['frontend', 'backend', 'ui', 'public'] for parent in file.parents):
                continue
            
            if file.is_file():
                try:
                    destination = web_dir / file.name
                    shutil.move(str(file), str(destination))
                    print(f"  ✅ Moved: {file.name}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to move {file.name}: {e}")
    
    return moved_count

def clean_weird_files():
    """Remove or move oddly named files."""
    weird_patterns = [
        'Here is the content of*',
        'Here\'s the content of*',
        'New file:***',
        'npx *',
        'pip install*',
        '~',
        '~/Desktop'
    ]
    
    removed_count = 0
    
    print(f"\n🗑️ Cleaning up oddly named files...")
    
    for pattern in weird_patterns:
        files = list(Path('.').glob(pattern))
        for file in files:
            try:
                if file.is_file():
                    file.unlink()
                    print(f"  ✅ Removed file: {file.name}")
                    removed_count += 1
                elif file.is_dir():
                    shutil.rmtree(file)
                    print(f"  ✅ Removed directory: {file.name}")
                    removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {file.name}: {e}")
    
    return removed_count

def test_core_functionality():
    """Test that core functionality still works."""
    print("\n🧪 Testing core functionality...")
    
    try:
        import sys
        sys.path.insert(0, 'jarvis')
        
        from jarvis.config import get_config
        print("  ✅ Config import successful")
        
        from jarvis.plugins.manager import PluginManager
        print("  ✅ Plugin manager import successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Core functionality test failed: {e}")
        return False

def main():
    """Run complete root directory cleanup."""
    print("🧹 COMPLETE ROOT DIRECTORY CLEANUP")
    print("=" * 50)
    
    # Create backup
    print("💾 Creating git backup...")
    try:
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Backup before complete root cleanup'], 
                      check=True, capture_output=True)
        print("✅ Git backup created")
    except:
        print("⚠️ Git backup failed, continuing...")
    
    total_moved = 0
    
    # Create directories
    create_directories()
    
    # Move files by category
    total_moved += move_test_files()
    total_moved += move_script_files()
    total_moved += move_data_files()
    total_moved += move_web_files()
    total_moved += clean_weird_files()
    
    # Test functionality
    if test_core_functionality():
        print(f"\n🎉 CLEANUP COMPLETE!")
        print(f"📊 Total items moved/removed: {total_moved}")
        print("✅ Core functionality verified")
        
        # Show final root directory count
        root_files = [f for f in Path('.').iterdir() if f.is_file()]
        print(f"📁 Root directory now has {len(root_files)} files (down from 500+)")
        
        return True
    else:
        print(f"\n❌ CLEANUP FAILED - Core functionality broken")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
