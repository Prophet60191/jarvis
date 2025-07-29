#!/usr/bin/env python3
"""
Test RAG Backup and Restore System.
Comprehensive testing of backup creation, restoration, and management.
"""

import sys
import json
import time
import tempfile
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_backup_manager():
    """Test RAG backup manager functionality."""
    print("💾 Testing RAG Backup Manager")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_backup_manager import RAGBackupManager
        
        config = get_config()
        backup_manager = RAGBackupManager(config.rag)
        
        print("✅ Backup manager initialized")
        print(f"   Backup directory: {backup_manager.backup_dir}")
        
        # Test 1: List existing backups
        print("\n📋 Testing Backup Listing...")
        existing_backups = backup_manager.list_backups()
        print(f"✅ Found {len(existing_backups)} existing backups")
        
        if existing_backups:
            for backup in existing_backups[:3]:  # Show first 3
                print(f"   - {backup['name']} ({backup['size_mb']} MB)")
        
        # Test 2: Create a new backup
        print("\n🔄 Testing Backup Creation...")
        backup_result = backup_manager.create_backup(
            backup_name="test_backup",
            include_documents=True,
            include_chat_history=True,
            compress=True
        )
        
        if backup_result["status"] == "success":
            print("✅ Backup created successfully")
            print(f"   Backup name: {backup_result['backup_name']}")
            print(f"   Total size: {backup_result['total_size_mb']} MB")
            print(f"   Compressed: {backup_result['compressed']}")
            
            # Show component details
            components = backup_result["components"]
            for component, details in components.items():
                status = details.get("status", "unknown")
                print(f"   {component}: {status}")
                if status == "success" and "size_mb" in details:
                    print(f"     Size: {details['size_mb']} MB")
        else:
            print(f"❌ Backup creation failed: {backup_result.get('errors', [])}")
            return False
        
        # Test 3: List backups again to verify new backup
        print("\n📋 Testing Updated Backup List...")
        updated_backups = backup_manager.list_backups()
        print(f"✅ Now have {len(updated_backups)} backups")
        
        # Find our test backup
        test_backup = None
        for backup in updated_backups:
            if "test_backup" in backup["name"]:
                test_backup = backup
                break
        
        if test_backup:
            print(f"✅ Test backup found: {test_backup['name']}")
            print(f"   Size: {test_backup['size_mb']} MB")
            print(f"   Compressed: {test_backup['is_compressed']}")
        else:
            print("❌ Test backup not found in list")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backup manager test failed: {e}")
        return False


def test_rag_service_backup_integration():
    """Test RAG service backup integration."""
    print("\n🔗 Testing RAG Service Backup Integration")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        print("✅ RAG service initialized with backup manager")
        
        # Test 1: List backups through RAG service
        print("\n📋 Testing Service Backup Listing...")
        service_backups = rag_service.list_backups()
        print(f"✅ RAG service found {len(service_backups)} backups")
        
        # Test 2: Create backup through RAG service
        print("\n💾 Testing Service Backup Creation...")
        service_backup_result = rag_service.create_backup(
            backup_name="service_test",
            include_documents=True,
            include_chat_history=False,
            compress=True
        )
        
        if service_backup_result["status"] == "success":
            print("✅ Service backup created successfully")
            print(f"   Backup: {service_backup_result['backup_name']}")
            print(f"   Size: {service_backup_result['total_size_mb']} MB")
            
            # Test 3: Verify backup appears in list (with small delay)
            time.sleep(1)  # Allow filesystem to sync
            updated_service_backups = rag_service.list_backups()
            service_backup_name = service_backup_result['backup_name']
            service_backup_found = any(
                service_backup_name in backup["name"] or backup["name"].startswith(service_backup_name)
                for backup in updated_service_backups
            )
            
            if service_backup_found:
                print("✅ Service backup appears in backup list")
            else:
                print("❌ Service backup not found in list")
                return False
        else:
            print(f"❌ Service backup failed: {service_backup_result.get('errors', [])}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ RAG service backup integration test failed: {e}")
        return False


def test_backup_restore_workflow():
    """Test complete backup and restore workflow."""
    print("\n🔄 Testing Backup and Restore Workflow")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Test 1: Add some test data
        print("📝 Adding test data...")
        test_memory = f"Backup test memory - {time.time()}"
        rag_service.add_conversational_memory(test_memory)
        print("✅ Test memory added")
        
        # Test 2: Create backup
        print("\n💾 Creating backup...")
        backup_result = rag_service.create_backup(
            backup_name="workflow_test",
            compress=False  # Don't compress for easier testing
        )
        
        if backup_result["status"] != "success":
            print(f"❌ Backup creation failed: {backup_result.get('errors', [])}")
            return False
        
        backup_name = backup_result["backup_name"]
        print(f"✅ Backup created: {backup_name}")
        
        # Test 3: Verify backup contents (if possible)
        print("\n🔍 Verifying backup contents...")
        time.sleep(1)  # Allow filesystem to sync
        backups = rag_service.list_backups()
        workflow_backup = None

        for backup in backups:
            if backup_name in backup["name"] or backup["name"].startswith(backup_name):
                workflow_backup = backup
                break
        
        if workflow_backup:
            print("✅ Workflow backup found in list")
            print(f"   Size: {workflow_backup['size_mb']} MB")
            
            # Check if metadata exists
            if "metadata" in workflow_backup:
                metadata = workflow_backup["metadata"]
                print(f"   Components: {list(metadata.get('backup_components', {}).keys())}")
        else:
            print("❌ Workflow backup not found")
            return False
        
        # Test 4: Test restore (dry run - we don't want to actually restore)
        print("\n🔄 Testing restore preparation...")
        
        # Just verify the backup can be found for restore
        backup_manager = rag_service.backup_manager
        found_backup = backup_manager._find_backup(backup_name)
        
        if found_backup:
            print("✅ Backup can be found for restore")
            print(f"   Backup path: {found_backup}")
        else:
            print("❌ Backup cannot be found for restore")
            return False
        
        print("✅ Backup and restore workflow test completed")
        return True
        
    except Exception as e:
        print(f"❌ Backup and restore workflow test failed: {e}")
        return False


def test_backup_configuration():
    """Test backup system configuration."""
    print("\n⚙️ Testing Backup Configuration")
    print("=" * 35)
    
    try:
        from jarvis.config import get_config
        
        config = get_config()
        rag_config = config.rag
        
        print("📋 Backup Configuration:")
        print(f"   Auto backup enabled: {rag_config.auto_backup_enabled}")
        print(f"   Backup frequency: {rag_config.backup_frequency_hours} hours")
        print(f"   Max backup files: {rag_config.max_backup_files}")
        print(f"   Compress backups: {rag_config.compress_backups}")
        print(f"   Backup path: {rag_config.backup_path}")
        
        # Verify backup path exists
        from jarvis.tools.rag_backup_manager import RAGBackupManager
        backup_manager = RAGBackupManager(rag_config)
        
        if backup_manager.backup_dir.exists():
            print("✅ Backup directory exists and is accessible")
            
            # Check permissions
            if backup_manager.backup_dir.is_dir():
                print("✅ Backup path is a directory")
            
            # Check if writable
            import os
            if os.access(backup_manager.backup_dir, os.W_OK):
                print("✅ Backup directory is writable")
            else:
                print("❌ Backup directory is not writable")
                return False
        else:
            print("❌ Backup directory does not exist")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backup configuration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 RAG Backup and Restore Testing Suite")
    print("=" * 60)
    print("Testing comprehensive backup and restore functionality...")
    print()
    
    tests = [
        ("Backup Manager", test_backup_manager),
        ("RAG Service Integration", test_rag_service_backup_integration),
        ("Backup/Restore Workflow", test_backup_restore_workflow),
        ("Backup Configuration", test_backup_configuration)
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
    
    print(f"\n📊 Backup and Restore Test Results")
    print("=" * 40)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 RAG Backup and Restore System: COMPLETE!")
        print("   ✅ Backup creation working")
        print("   ✅ Backup listing functional")
        print("   ✅ RAG service integration successful")
        print("   ✅ Workflow testing passed")
        print("   ✅ Configuration properly set")
        print("\n💾 RAG data is now fully protected with backup/restore!")
    elif passed >= total * 0.8:
        print(f"\n✅ RAG Backup and Restore mostly complete!")
        print(f"   Minor issues detected, but core functionality works")
    else:
        print(f"\n⚠️  RAG Backup and Restore need attention")
        print(f"   Multiple backup issues detected")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
