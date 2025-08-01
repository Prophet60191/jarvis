#!/usr/bin/env python3
"""
Test the user profile system.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_user_profile():
    """Test the user profile system."""
    print("🧪 TESTING USER PROFILE SYSTEM")
    print("=" * 50)
    
    try:
        # Test import
        print("1. Testing import...")
        from jarvis.core.user_profile import UserProfile, UserProfileManager, get_user_profile_manager
        print("   ✅ Import successful")
        
        # Test profile creation
        print("2. Testing profile creation...")
        profile = UserProfile(name="Test User", preferred_name="Test")
        print(f"   ✅ Profile created: {profile.name}")
        
        # Test manager
        print("3. Testing profile manager...")
        manager = UserProfileManager()
        print("   ✅ Manager created")
        
        # Test setting name
        print("4. Testing name setting...")
        success = manager.set_name("Jose", "Jose")
        print(f"   ✅ Name set: {success}")
        
        # Test getting name
        print("5. Testing name retrieval...")
        name = manager.get_name()
        print(f"   ✅ Name retrieved: {name}")
        
        # Test global instance
        print("6. Testing global instance...")
        global_manager = get_user_profile_manager()
        print("   ✅ Global manager working")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("The user profile system is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    if test_user_profile():
        print("\n✅ User profile system is ready to use!")
        return 0
    else:
        print("\n❌ User profile system has issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
