#!/usr/bin/env python3
"""
Final Root Directory Cleanup
Clean up remaining utility scripts, diagnostic files, and other clutter
"""

import os
import shutil
from pathlib import Path

def analyze_remaining_files():
    """Analyze remaining files in root directory."""
    
    # Essential files that must stay in root
    essential_files = {
        # Core documentation
        'README.md', 'CHANGELOG.md', 'ARCHITECTURE.md', 'USER_GUIDE.md',
        'JARVIS_CAPABILITIES.md', 'COMPLEXITY_DEPENDENCY_ANALYSIS.md',
        
        # Core application files
        'jarvis_app.py', 'main.py',
        
        # Configuration files
        'package.json', 'requirements-enhanced.txt',
        '.env', '.gitignore', '.vscodeignore',
        
        # Essential directories (will be skipped)
        'jarvis', 'docs', 'data', 'projects', 'tests', 'scripts', 'examples',
        'frontend', 'backend', 'ui', 'voices', 'web', 'src', 'mcp_servers',
        'database', 'cache'
    }
    
    # Categories for cleanup
    categories = {
        'diagnostic_scripts': [
            'audio_capture_diagnostic.py',
            'wake_word_diagnostic.py', 
            'check_current_voice.py',
            'discover_us_voices.py',
            'validate_implementation.py'
        ],
        
        'utility_scripts': [
            'ingest.py',
            'ingest_complete_codebase.py',
            'initialize_rag_workflow.py',
            'rag_app.py',
            'web_automation_tool.py',
            'script.py'
        ],
        
        'cleanup_scripts': [
            'cleanup_documentation.py',
            'cleanup_obsolete_files.py', 
            'complete_root_cleanup.py'
        ],
        
        'summary_files': [
            'desktop_app_fix_summary.py',
            'name_storage_summary.py',
            'settings_fix_summary.py'
        ],
        
        'data_files': [
            'caching.py',
            'dal.py',
            'data_integrity.py',
            'migrations.py',
            'models.py',
            'queries.py',
            'utils.py'
        ],
        
        'weird_files': [
            'AWS S3 or Cloudinary account (for file upload and storage)',
            "Here's the complete project structure",
            'test_audio_mic_2.wav'
        ],
        
        'shell_scripts': [
            'start_rag_manager.sh'
        ]
    }
    
    # Get all files in root
    all_files = [f for f in Path('.').iterdir() if f.is_file()]
    
    results = {
        'essential': [],
        'diagnostic_scripts': [],
        'utility_scripts': [],
        'cleanup_scripts': [],
        'summary_files': [],
        'data_files': [],
        'weird_files': [],
        'shell_scripts': [],
        'cleanup_backups': [],
        'other': []
    }
    
    for file_path in all_files:
        filename = file_path.name
        
        # Skip hidden files
        if filename.startswith('.'):
            continue
            
        if filename in essential_files:
            results['essential'].append(filename)
            continue
        
        # Check for cleanup backup directories
        if filename.startswith('cleanup_backup_'):
            results['cleanup_backups'].append(filename)
            continue
            
        # Categorize files
        categorized = False
        for category, file_list in categories.items():
            if filename in file_list:
                results[category].append(filename)
                categorized = True
                break
        
        if not categorized:
            results['other'].append(filename)
    
    return results

def create_directories():
    """Create directories for organization."""
    dirs = [
        'scripts/diagnostics',
        'scripts/utilities', 
        'scripts/cleanup',
        'scripts/summaries',
        'jarvis/data_models',
        'temp'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")

def move_files(file_list, target_dir, action_name):
    """Move files to target directory."""
    if not file_list:
        return 0
    
    print(f"\n📁 {action_name} ({len(file_list)} files):")
    moved_count = 0
    
    for filename in file_list:
        try:
            source = Path(filename)
            if source.is_file():
                destination = Path(target_dir) / filename
                shutil.move(str(source), str(destination))
                print(f"  ✅ Moved: {filename}")
                moved_count += 1
        except Exception as e:
            print(f"  ❌ Failed to move {filename}: {e}")
    
    return moved_count

def remove_files(file_list, action_name):
    """Remove files completely."""
    if not file_list:
        return 0
    
    print(f"\n🗑️ {action_name} ({len(file_list)} files):")
    removed_count = 0
    
    for filename in file_list:
        try:
            file_path = Path(filename)
            if file_path.is_file():
                file_path.unlink()
                print(f"  ✅ Removed: {filename}")
                removed_count += 1
            elif file_path.is_dir():
                shutil.rmtree(file_path)
                print(f"  ✅ Removed directory: {filename}")
                removed_count += 1
        except Exception as e:
            print(f"  ❌ Failed to remove {filename}: {e}")
    
    return removed_count

def main():
    """Clean up remaining root directory files."""
    print("🧹 FINAL ROOT DIRECTORY CLEANUP")
    print("=" * 40)
    
    # Analyze files
    results = analyze_remaining_files()
    
    print(f"\n📊 ANALYSIS RESULTS:")
    for category, files in results.items():
        if files:
            print(f"{category.replace('_', ' ').title()}: {len(files)}")
    
    # Show essential files that will stay
    print(f"\n✅ ESSENTIAL FILES (staying in root):")
    for file in sorted(results['essential'])[:10]:  # Show first 10
        print(f"  • {file}")
    if len(results['essential']) > 10:
        print(f"  ... and {len(results['essential']) - 10} more")
    
    # Show what will be moved/removed
    print(f"\n📋 FILES TO BE ORGANIZED:")
    
    move_categories = ['diagnostic_scripts', 'utility_scripts', 'summary_files', 'data_files', 'shell_scripts']
    remove_categories = ['cleanup_scripts', 'weird_files', 'cleanup_backups']
    
    for category in move_categories + remove_categories:
        if results[category]:
            action = "MOVE" if category in move_categories else "REMOVE"
            print(f"\n{category.upper().replace('_', ' ')} ({action}):")
            for file in results[category][:5]:  # Show first 5
                print(f"  • {file}")
            if len(results[category]) > 5:
                print(f"  ... and {len(results[category]) - 5} more")
    
    if results['other']:
        print(f"\nOTHER FILES (need manual review):")
        for file in results['other']:
            print(f"  • {file}")
    
    # Calculate total
    total_to_process = sum(len(files) for cat, files in results.items() 
                          if cat not in ['essential', 'other'])
    
    # Confirm action
    response = input(f"\n🚨 Process {total_to_process} files? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Cleanup cancelled")
        return False
    
    # Create directories
    create_directories()
    
    # Move files to appropriate locations
    total_moved = 0
    total_moved += move_files(results['diagnostic_scripts'], 'scripts/diagnostics', 'Moving diagnostic scripts')
    total_moved += move_files(results['utility_scripts'], 'scripts/utilities', 'Moving utility scripts')
    total_moved += move_files(results['summary_files'], 'scripts/summaries', 'Moving summary files')
    total_moved += move_files(results['data_files'], 'jarvis/data_models', 'Moving data model files')
    total_moved += move_files(results['shell_scripts'], 'scripts', 'Moving shell scripts')
    
    # Remove unnecessary files
    total_removed = 0
    total_removed += remove_files(results['cleanup_scripts'], 'Removing cleanup scripts')
    total_removed += remove_files(results['weird_files'], 'Removing weird/temp files')
    total_removed += remove_files(results['cleanup_backups'], 'Removing cleanup backup directories')
    
    # Final count
    remaining_files = len([f for f in Path('.').iterdir() if f.is_file() and not f.name.startswith('.')])
    
    print(f"\n🎉 FINAL ROOT CLEANUP COMPLETE!")
    print(f"📊 Files moved: {total_moved}")
    print(f"🗑️ Files removed: {total_removed}")
    print(f"📁 Root files remaining: {remaining_files}")
    
    if results['other']:
        print(f"\n⚠️ {len(results['other'])} files need manual review:")
        for file in results['other']:
            print(f"  • {file}")
    
    print(f"\n✅ Root directory is now professionally clean!")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
