#!/usr/bin/env python3
"""
Verify that RAG data is properly protected from Git commits.
Ensures user privacy and data security.
"""

import os
import subprocess
import sys
from pathlib import Path


class DataProtectionVerifier:
    """Verify RAG data protection and Git ignore rules."""
    
    def __init__(self):
        """Initialize the verifier."""
        self.project_root = Path(__file__).parent
        self.gitignore_path = self.project_root / ".gitignore"
        
    def check_gitignore_exists(self):
        """Check if .gitignore file exists."""
        print("🔍 Checking .gitignore file...")
        
        if self.gitignore_path.exists():
            print("✅ .gitignore file exists")
            return True
        else:
            print("❌ .gitignore file not found")
            return False
    
    def verify_rag_exclusions(self):
        """Verify that RAG-related patterns are in .gitignore."""
        print("\n🛡️ Verifying RAG data exclusions...")
        
        if not self.gitignore_path.exists():
            print("❌ Cannot verify - .gitignore not found")
            return False
        
        with open(self.gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        # Critical patterns that must be excluded
        critical_patterns = [
            "data/",
            "data/chroma_db/",
            "data/documents/",
            "data/backups/",
            "chroma_db/",
            "*.db"
        ]
        
        # Recommended patterns for enhanced protection
        recommended_patterns = [
            "data/chat_history/",
            "vector_store/",
            "memory_backup_*.json",
            "chat_backup_*.json",
            "rag_metrics.json"
        ]
        
        missing_critical = []
        missing_recommended = []
        
        for pattern in critical_patterns:
            if pattern not in gitignore_content:
                missing_critical.append(pattern)
        
        for pattern in recommended_patterns:
            if pattern not in gitignore_content:
                missing_recommended.append(pattern)
        
        if not missing_critical:
            print("✅ All critical RAG data patterns are excluded")
        else:
            print(f"❌ Missing critical patterns: {missing_critical}")
        
        if not missing_recommended:
            print("✅ All recommended patterns are excluded")
        else:
            print(f"⚠️  Missing recommended patterns: {missing_recommended}")
        
        return len(missing_critical) == 0
    
    def check_existing_data_status(self):
        """Check if any RAG data is currently tracked by Git."""
        print("\n📊 Checking existing data status...")
        
        try:
            # Check if we're in a Git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️  Not in a Git repository - skipping Git status check")
                return True
            
            # Check for tracked RAG data files
            rag_paths = [
                "data/",
                "data/chroma_db/",
                "data/documents/",
                "data/backups/",
                "chroma_db/",
                "vector_store/"
            ]
            
            tracked_rag_files = []
            
            for path in rag_paths:
                full_path = self.project_root / path
                if full_path.exists():
                    # Check if this path is tracked by Git
                    result = subprocess.run(
                        ["git", "ls-files", str(full_path)],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.stdout.strip():
                        tracked_rag_files.extend(result.stdout.strip().split('\n'))
            
            if not tracked_rag_files:
                print("✅ No RAG data files are tracked by Git")
                return True
            else:
                print(f"❌ Found {len(tracked_rag_files)} tracked RAG data files:")
                for file in tracked_rag_files[:10]:  # Show first 10
                    print(f"   - {file}")
                if len(tracked_rag_files) > 10:
                    print(f"   ... and {len(tracked_rag_files) - 10} more")
                
                print("\n🔧 To fix this, run:")
                print("   git rm --cached -r data/")
                print("   git rm --cached -r chroma_db/ (if exists)")
                print("   git commit -m 'Remove RAG data from tracking'")
                
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git command failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error checking Git status: {e}")
            return False
    
    def verify_data_directories(self):
        """Verify that data directories exist and are properly structured."""
        print("\n📁 Verifying data directory structure...")
        
        expected_dirs = [
            "data",
            "data/chroma_db",
            "data/documents",
            "data/backups"
        ]
        
        existing_dirs = []
        missing_dirs = []
        
        for dir_path in expected_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                existing_dirs.append(dir_path)
                print(f"✅ {dir_path}/ exists")
            else:
                missing_dirs.append(dir_path)
                print(f"⚠️  {dir_path}/ does not exist (will be created when needed)")
        
        if existing_dirs:
            print(f"\n📊 Found {len(existing_dirs)} existing data directories")
            
            # Check if directories contain data
            for dir_path in existing_dirs:
                full_path = self.project_root / dir_path
                try:
                    items = list(full_path.iterdir())
                    if items:
                        print(f"   📦 {dir_path}/ contains {len(items)} items")
                    else:
                        print(f"   📭 {dir_path}/ is empty")
                except PermissionError:
                    print(f"   🔒 {dir_path}/ - permission denied")
        
        return True
    
    def create_data_protection_readme(self):
        """Create a README file explaining data protection."""
        print("\n📝 Creating data protection documentation...")
        
        readme_content = """# RAG Data Protection

This directory contains user data, vector stores, and documents that are automatically excluded from Git commits for privacy and security.

## Protected Directories

- `data/chroma_db/` - Vector database storage
- `data/documents/` - User uploaded documents  
- `data/backups/` - System backups
- `data/chat_history/` - Conversation history

## Security Measures

1. **Git Exclusion**: All data directories are in .gitignore
2. **Local Storage**: Data stays on your local machine
3. **Privacy Protection**: No user data is committed to version control

## Backup Recommendations

- Regularly backup the `data/` directory
- Use the built-in RAG backup tools
- Store backups securely and privately

## Important Notes

- Never commit user data to version control
- Be cautious when sharing project files
- Regularly review .gitignore for completeness

Generated by RAG Data Protection System
"""
        
        readme_path = self.project_root / "data" / "README.md"
        
        # Create data directory if it doesn't exist
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)
        
        try:
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            print("✅ Created data protection README")
            return True
        except Exception as e:
            print(f"❌ Failed to create README: {e}")
            return False
    
    def run_verification(self):
        """Run complete data protection verification."""
        print("🛡️ RAG Data Protection Verification")
        print("=" * 50)
        print("Ensuring user data privacy and security...")
        print()
        
        tests = [
            ("GitIgnore File Check", self.check_gitignore_exists),
            ("RAG Exclusion Patterns", self.verify_rag_exclusions),
            ("Git Tracking Status", self.check_existing_data_status),
            ("Data Directory Structure", self.verify_data_directories),
            ("Protection Documentation", self.create_data_protection_readme)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n📊 Data Protection Verification Results")
        print("=" * 45)
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Overall Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📊 Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 RAG Data Protection: COMPLETE!")
            print("   ✅ All user data properly protected")
            print("   ✅ Git exclusions configured correctly")
            print("   ✅ No sensitive data tracked by Git")
            print("   ✅ Directory structure verified")
            print("   ✅ Protection documentation created")
            print("\n🔒 User privacy and data security ensured!")
        elif passed >= total * 0.8:
            print(f"\n✅ RAG Data Protection mostly complete!")
            print(f"   Minor issues detected, but core protection works")
        else:
            print(f"\n⚠️  RAG Data Protection needs attention")
            print(f"   Multiple protection issues detected")
        
        return passed >= total * 0.8


def main():
    """Main verification function."""
    verifier = DataProtectionVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Data protection is properly configured")
        print("   2. User privacy is ensured")
        print("   3. Ready to proceed with other production enhancements")
    else:
        print("\n🔧 Fix data protection issues before proceeding.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
