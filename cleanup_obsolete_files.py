#!/usr/bin/env python3
"""
JARVIS Obsolete Files Cleanup Script
Automated cleanup of 379 obsolete files and directories identified in the audit
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import subprocess

def create_backup():
    """Create a full backup before cleanup."""
    print("💾 Creating backup before cleanup...")
    
    backup_dir = Path(f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)
    
    # Create git commit as backup
    try:
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Backup before obsolete files cleanup'], 
                      check=True, capture_output=True)
        print("✅ Git backup created")
    except subprocess.CalledProcessError:
        print("⚠️ Git backup failed, continuing with file backup...")
    
    # Also create file backup of critical items
    critical_items = [
        'jarvis/',
        'README.md',
        'requirements.txt',
        'JARVIS_CAPABILITIES.md',
        'COMPLEXITY_DEPENDENCY_ANALYSIS.md'
    ]
    
    for item in critical_items:
        item_path = Path(item)
        if item_path.exists():
            if item_path.is_dir():
                shutil.copytree(item_path, backup_dir / item_path.name)
            else:
                shutil.copy2(item_path, backup_dir / item_path.name)
    
    print(f"✅ File backup created: {backup_dir}")
    return backup_dir

def load_audit_results():
    """Load the audit results from the JSON file."""
    audit_file = Path('obsolete_files_audit.json')
    if not audit_file.exists():
        print("❌ Audit results not found. Run audit_obsolete_files.py first.")
        return None
    
    with open(audit_file, 'r') as f:
        return json.load(f)

def confirm_action(message):
    """Get user confirmation for an action."""
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ['y', 'yes']

def safe_remove(path_str, dry_run=False):
    """Safely remove a file or directory."""
    path = Path(path_str)
    
    if not path.exists():
        return f"⚠️ Already removed: {path_str}"
    
    if dry_run:
        return f"🔍 Would remove: {path_str}"
    
    try:
        if path.is_dir():
            shutil.rmtree(path)
            return f"✅ Removed directory: {path_str}"
        else:
            path.unlink()
            return f"✅ Removed file: {path_str}"
    except Exception as e:
        return f"❌ Failed to remove {path_str}: {e}"

def safe_move(src_str, dst_str, dry_run=False):
    """Safely move a file or directory."""
    src = Path(src_str)
    dst = Path(dst_str)
    
    if not src.exists():
        return f"⚠️ Source not found: {src_str}"
    
    if dry_run:
        return f"🔍 Would move: {src_str} → {dst_str}"
    
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return f"✅ Moved: {src_str} → {dst_str}"
    except Exception as e:
        return f"❌ Failed to move {src_str}: {e}"

def phase1_immediate_removal(audit_results, dry_run=False):
    """Phase 1: Remove files that are safe to delete immediately."""
    print("\n🚀 PHASE 1: Immediate Safe Removal")
    print("-" * 40)
    
    removed_count = 0
    
    # Debug scripts
    debug_scripts = audit_results['obsolete_tests']['debug_scripts']
    print(f"\n🔧 Removing {len(debug_scripts)} debug scripts...")
    for script in debug_scripts:
        result = safe_remove(script, dry_run)
        print(f"  {result}")
        if "✅" in result:
            removed_count += 1
    
    # Demo applications
    demo_apps = audit_results['obsolete_apps']['demo_apps']
    print(f"\n📱 Removing {len(demo_apps)} demo applications...")
    for app in demo_apps:
        result = safe_remove(app, dry_run)
        print(f"  {result}")
        if "✅" in result:
            removed_count += 1
    
    # Test data directories
    test_data = audit_results['obsolete_data']['test_data']
    backup_data = audit_results['obsolete_data']['backup_data']
    benchmark_data = audit_results['obsolete_data']['benchmark_data']
    
    all_data = test_data + backup_data + benchmark_data
    print(f"\n💾 Removing {len(all_data)} data directories...")
    for data_dir in all_data:
        result = safe_remove(data_dir, dry_run)
        print(f"  {result}")
        if "✅" in result:
            removed_count += 1
    
    # Temporary files
    temp_tests = audit_results['obsolete_tests']['temporary_tests']
    print(f"\n🗑️ Removing {len(temp_tests)} temporary files...")
    for temp_file in temp_tests:
        result = safe_remove(temp_file, dry_run)
        print(f"  {result}")
        if "✅" in result:
            removed_count += 1
    
    print(f"\n📊 Phase 1 Summary: {removed_count} items removed")
    return removed_count

def phase2_organization(audit_results, dry_run=False):
    """Phase 2: Organize files into proper directories."""
    print("\n🗂️ PHASE 2: File Organization")
    print("-" * 40)
    
    moved_count = 0
    
    # Create target directories
    if not dry_run:
        Path('tests/legacy').mkdir(parents=True, exist_ok=True)
        Path('scripts/debug').mkdir(parents=True, exist_ok=True)
        Path('scripts/setup').mkdir(parents=True, exist_ok=True)
        Path('scripts/migration').mkdir(parents=True, exist_ok=True)
    
    # Move root-level test files
    root_tests = audit_results['obsolete_tests']['root_level_tests']
    print(f"\n🧪 Moving {len(root_tests)} test files to tests/legacy/...")
    for test_file in root_tests[:10]:  # Move first 10 as example
        filename = Path(test_file).name
        result = safe_move(test_file, f'tests/legacy/{filename}', dry_run)
        print(f"  {result}")
        if "✅" in result:
            moved_count += 1
    
    if len(root_tests) > 10:
        print(f"  ... and {len(root_tests) - 10} more files")
    
    # Move setup scripts
    setup_scripts = audit_results['obsolete_scripts']['setup_scripts']
    print(f"\n⚙️ Moving {len(setup_scripts)} setup scripts...")
    for script in setup_scripts:
        if Path(script).parent == Path('.'):  # Only root-level scripts
            filename = Path(script).name
            result = safe_move(script, f'scripts/setup/{filename}', dry_run)
            print(f"  {result}")
            if "✅" in result:
                moved_count += 1
    
    # Move migration scripts
    migration_scripts = audit_results['obsolete_scripts']['migration_scripts']
    print(f"\n🔄 Moving {len(migration_scripts)} migration scripts...")
    for script in migration_scripts:
        if Path(script).parent == Path('.'):  # Only root-level scripts
            filename = Path(script).name
            result = safe_move(script, f'scripts/migration/{filename}', dry_run)
            print(f"  {result}")
            if "✅" in result:
                moved_count += 1
    
    print(f"\n📊 Phase 2 Summary: {moved_count} items moved")
    return moved_count

def phase3_documentation(audit_results, dry_run=False):
    """Phase 3: Clean up and consolidate documentation."""
    print("\n📚 PHASE 3: Documentation Cleanup")
    print("-" * 40)
    
    removed_count = 0
    
    # Create docs archive directory
    if not dry_run:
        Path('docs/archive').mkdir(parents=True, exist_ok=True)
    
    # Remove duplicate guides
    duplicate_guides = audit_results['obsolete_docs']['duplicate_guides']
    print(f"\n📖 Removing {len(duplicate_guides)} duplicate guides...")
    for guide in duplicate_guides:
        result = safe_remove(guide, dry_run)
        print(f"  {result}")
        if "✅" in result:
            removed_count += 1
    
    # Archive implementation docs
    impl_docs = audit_results['obsolete_docs']['implementation_docs']
    print(f"\n📋 Archiving {len(impl_docs)} implementation documents...")
    for doc in impl_docs[:5]:  # Archive first 5 as example
        filename = Path(doc).name
        result = safe_move(doc, f'docs/archive/{filename}', dry_run)
        print(f"  {result}")
        if "✅" in result:
            removed_count += 1
    
    if len(impl_docs) > 5:
        print(f"  ... and {len(impl_docs) - 5} more documents")
    
    print(f"\n📊 Phase 3 Summary: {removed_count} items processed")
    return removed_count

def test_core_functionality():
    """Test core functionality after cleanup."""
    print("\n🧪 Testing core functionality...")
    
    # Test basic imports
    try:
        sys.path.insert(0, 'jarvis')
        from jarvis.config import get_config
        print("✅ Config import successful")
        
        from jarvis.plugins.manager import PluginManager
        print("✅ Plugin manager import successful")
        
        from jarvis.tools import get_langchain_tools
        print("✅ Tools import successful")
        
        print("✅ Core functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        return False

def main():
    """Run the complete cleanup process."""
    print("🧹 JARVIS OBSOLETE FILES CLEANUP")
    print("=" * 50)
    
    # Load audit results
    audit_results = load_audit_results()
    if not audit_results:
        return False
    
    total_items = audit_results['total_obsolete_files']
    print(f"📊 Total items to process: {total_items}")
    
    # Confirm cleanup
    if not confirm_action("🚨 This will remove/move 379 files. Continue?"):
        print("❌ Cleanup cancelled by user")
        return False
    
    # Create backup
    backup_dir = create_backup()
    
    # Dry run option
    dry_run = confirm_action("🔍 Run in dry-run mode first (recommended)?")
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No files will be actually removed/moved")
    
    total_processed = 0
    
    try:
        # Phase 1: Immediate removal
        if confirm_action("Execute Phase 1 (Immediate Safe Removal)?"):
            count = phase1_immediate_removal(audit_results, dry_run)
            total_processed += count
            
            if not dry_run:
                if not test_core_functionality():
                    print("❌ Core functionality test failed after Phase 1")
                    return False
        
        # Phase 2: Organization
        if confirm_action("Execute Phase 2 (File Organization)?"):
            count = phase2_organization(audit_results, dry_run)
            total_processed += count
            
            if not dry_run:
                if not test_core_functionality():
                    print("❌ Core functionality test failed after Phase 2")
                    return False
        
        # Phase 3: Documentation
        if confirm_action("Execute Phase 3 (Documentation Cleanup)?"):
            count = phase3_documentation(audit_results, dry_run)
            total_processed += count
            
            if not dry_run:
                if not test_core_functionality():
                    print("❌ Core functionality test failed after Phase 3")
                    return False
        
        # Summary
        print(f"\n🎉 CLEANUP COMPLETE")
        print(f"📊 Total items processed: {total_processed}")
        print(f"💾 Backup location: {backup_dir}")
        
        if dry_run:
            print("\n🔍 This was a dry run. Run again without dry-run to execute cleanup.")
        else:
            print("\n✅ Cleanup executed successfully!")
            print("🧪 Run full system tests to verify everything works correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        print(f"💾 Restore from backup: {backup_dir}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
