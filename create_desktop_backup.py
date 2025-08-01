#!/usr/bin/env python3
"""
Create a comprehensive backup of the JARVIS project on the desktop
"""

import os
import sys
import shutil
import tarfile
import zipfile
from pathlib import Path
from datetime import datetime
import subprocess

def get_desktop_path():
    """Get the desktop path for the current user."""
    home = Path.home()
    desktop = home / "Desktop"
    
    if not desktop.exists():
        # Try alternative desktop locations
        alternatives = [
            home / "desktop",
            home / "Bureau",  # French
            home / "Escritorio",  # Spanish
        ]
        
        for alt in alternatives:
            if alt.exists():
                return alt
        
        # If no desktop found, use home directory
        print("⚠️ Desktop directory not found, using home directory")
        return home
    
    return desktop

def create_git_backup():
    """Create a git bundle backup if this is a git repository."""
    try:
        # Check if this is a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("ℹ️ Not a git repository, skipping git backup")
            return None
        
        # Create git bundle
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        bundle_name = f"jarvis_git_backup_{timestamp}.bundle"
        
        print("📦 Creating git bundle backup...")
        subprocess.run(['git', 'bundle', 'create', bundle_name, '--all'], check=True)
        
        print(f"✅ Git bundle created: {bundle_name}")
        return bundle_name
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git backup failed: {e}")
        return None
    except FileNotFoundError:
        print("ℹ️ Git not found, skipping git backup")
        return None

def get_project_size():
    """Calculate the total size of the project."""
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 
                    '.venv', 'venv', 'env', '.env', 'data/vector_store'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            try:
                file_path = Path(root) / file
                if file_path.exists():
                    total_size += file_path.stat().st_size
                    file_count += 1
            except (OSError, PermissionError):
                continue
    
    return total_size, file_count

def create_file_backup(desktop_path, backup_name):
    """Create a comprehensive file backup."""
    print("📁 Creating comprehensive file backup...")
    
    # Create backup directory
    backup_dir = desktop_path / backup_name
    backup_dir.mkdir(exist_ok=True)
    
    # Items to backup
    items_to_backup = [
        'jarvis/',
        'docs/',
        'apps/',
        'projects/',
        'scripts/',
        'tests/',
        'data/',
        '*.md',
        '*.txt',
        '*.py',
        '*.json',
        '*.yaml',
        '*.yml',
        '*.sh',
        '*.command'
    ]
    
    copied_files = 0
    skipped_files = 0
    
    # Copy files and directories
    for item_pattern in items_to_backup:
        if '*' in item_pattern:
            # Handle glob patterns
            for item in Path('.').glob(item_pattern):
                if item.is_file():
                    try:
                        shutil.copy2(item, backup_dir / item.name)
                        copied_files += 1
                        print(f"  ✅ Copied: {item}")
                    except Exception as e:
                        print(f"  ⚠️ Failed to copy {item}: {e}")
                        skipped_files += 1
        else:
            # Handle specific files/directories
            item_path = Path(item_pattern)
            if item_path.exists():
                try:
                    if item_path.is_dir():
                        # Copy directory, excluding certain subdirectories
                        def ignore_patterns(dir, files):
                            ignore = set()
                            for file in files:
                                if file in {'.git', '__pycache__', '.pytest_cache', 
                                          'node_modules', '.venv', 'venv', 'env'}:
                                    ignore.add(file)
                                # Skip large vector store files
                                elif 'vector_store' in file and Path(dir, file).is_dir():
                                    ignore.add(file)
                            return ignore
                        
                        shutil.copytree(item_path, backup_dir / item_path.name, 
                                      ignore=ignore_patterns, dirs_exist_ok=True)
                        print(f"  ✅ Copied directory: {item_path}")
                        copied_files += 1
                    else:
                        shutil.copy2(item_path, backup_dir / item_path.name)
                        print(f"  ✅ Copied file: {item_path}")
                        copied_files += 1
                except Exception as e:
                    print(f"  ⚠️ Failed to copy {item_path}: {e}")
                    skipped_files += 1
    
    return backup_dir, copied_files, skipped_files

def create_compressed_backup(backup_dir, desktop_path):
    """Create compressed versions of the backup."""
    print("🗜️ Creating compressed backups...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create ZIP backup
    zip_name = f"jarvis_backup_{timestamp}.zip"
    zip_path = desktop_path / zip_name
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        zip_size = zip_path.stat().st_size
        print(f"  ✅ ZIP backup created: {zip_name} ({zip_size / 1024 / 1024:.1f} MB)")
        
    except Exception as e:
        print(f"  ⚠️ ZIP backup failed: {e}")
        zip_path = None
    
    # Create TAR.GZ backup
    tar_name = f"jarvis_backup_{timestamp}.tar.gz"
    tar_path = desktop_path / tar_name
    
    try:
        with tarfile.open(tar_path, 'w:gz') as tarf:
            tarf.add(backup_dir, arcname=backup_dir.name)
        
        tar_size = tar_path.stat().st_size
        print(f"  ✅ TAR.GZ backup created: {tar_name} ({tar_size / 1024 / 1024:.1f} MB)")
        
    except Exception as e:
        print(f"  ⚠️ TAR.GZ backup failed: {e}")
        tar_path = None
    
    return zip_path, tar_path

def create_backup_manifest(backup_dir):
    """Create a manifest of what was backed up."""
    manifest_file = backup_dir / "BACKUP_MANIFEST.txt"
    
    with open(manifest_file, 'w') as f:
        f.write(f"JARVIS PROJECT BACKUP MANIFEST\n")
        f.write(f"=" * 50 + "\n")
        f.write(f"Backup Date: {datetime.now().isoformat()}\n")
        f.write(f"Source Directory: {Path.cwd()}\n")
        f.write(f"Backup Directory: {backup_dir}\n\n")
        
        f.write("BACKED UP ITEMS:\n")
        f.write("-" * 20 + "\n")
        
        # List all backed up items
        for root, dirs, files in os.walk(backup_dir):
            level = len(Path(root).relative_to(backup_dir).parts)
            indent = "  " * level
            
            if root != str(backup_dir):
                f.write(f"{indent}{Path(root).name}/\n")
            
            for file in files:
                if file != "BACKUP_MANIFEST.txt":
                    file_path = Path(root) / file
                    size = file_path.stat().st_size
                    f.write(f"{indent}  {file} ({size} bytes)\n")
    
    print(f"  ✅ Backup manifest created: {manifest_file.name}")

def main():
    """Create comprehensive backup on desktop."""
    print("💾 JARVIS PROJECT BACKUP CREATOR")
    print("=" * 50)
    
    # Get desktop path
    desktop_path = get_desktop_path()
    print(f"🖥️ Desktop path: {desktop_path}")
    
    # Get project info
    total_size, file_count = get_project_size()
    print(f"📊 Project size: {total_size / 1024 / 1024:.1f} MB ({file_count} files)")
    
    # Create timestamp for backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"JARVIS_BACKUP_{timestamp}"
    
    print(f"📦 Creating backup: {backup_name}")
    
    # Create git backup if possible
    git_bundle = create_git_backup()
    if git_bundle:
        # Move git bundle to desktop
        shutil.move(git_bundle, desktop_path / git_bundle)
        print(f"  ✅ Git bundle moved to desktop: {git_bundle}")
    
    # Create file backup
    backup_dir, copied_files, skipped_files = create_file_backup(desktop_path, backup_name)
    
    # Create backup manifest
    create_backup_manifest(backup_dir)
    
    # Create compressed backups
    zip_path, tar_path = create_compressed_backup(backup_dir, desktop_path)
    
    # Summary
    print(f"\n🎉 BACKUP COMPLETE")
    print("=" * 50)
    print(f"📁 Backup directory: {backup_dir}")
    print(f"📊 Files copied: {copied_files}")
    if skipped_files > 0:
        print(f"⚠️ Files skipped: {skipped_files}")
    
    if git_bundle:
        print(f"📦 Git bundle: {desktop_path / git_bundle}")
    
    if zip_path:
        print(f"🗜️ ZIP backup: {zip_path}")
    
    if tar_path:
        print(f"🗜️ TAR.GZ backup: {tar_path}")
    
    print(f"\n✅ All backups saved to desktop: {desktop_path}")
    print("🛡️ Your project is now safely backed up!")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("1. Keep the compressed backups (.zip or .tar.gz) for long-term storage")
    print("2. The uncompressed folder is good for quick access/comparison")
    print("3. The git bundle preserves complete version history")
    print("4. Test restore from backup before making major changes")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
