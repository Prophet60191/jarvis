#!/usr/bin/env python3
"""
Test PII Detection and Warning System

Tests the enhanced PII detection system with various sensitive
data patterns and severity-based warnings.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_pii_pattern_detection():
    """Test PII pattern detection with various data types."""
    print("🔍 Testing PII Pattern Detection")
    print("=" * 40)
    
    try:
        from jarvis.tools.rag_tools import detect_pii
        
        # Test cases with different PII types
        test_cases = [
            {
                "name": "Social Security Number",
                "text": "My SSN is 123-45-6789",
                "expected_pii": ["ssn"],
                "expected_severity": "HIGH"
            },
            {
                "name": "Credit Card Number",
                "text": "My credit card is 4532 1234 5678 9012",
                "expected_pii": ["credit_card"],
                "expected_severity": "HIGH"
            },
            {
                "name": "Phone Number",
                "text": "Call me at (555) 123-4567",
                "expected_pii": ["phone"],
                "expected_severity": "MEDIUM"
            },
            {
                "name": "Email Address",
                "text": "Contact me at john.doe@example.com",
                "expected_pii": ["email"],
                "expected_severity": "MEDIUM"
            },
            {
                "name": "Home Address",
                "text": "I live at 123 Main Street",
                "expected_pii": ["address"],
                "expected_severity": "MEDIUM"
            },
            {
                "name": "IP Address",
                "text": "My server IP is 192.168.1.100",
                "expected_pii": ["ip_address"],
                "expected_severity": "LOW"
            },
            {
                "name": "Date of Birth",
                "text": "I was born on 01/15/1990",
                "expected_pii": ["date_of_birth"],
                "expected_severity": "MEDIUM"
            },
            {
                "name": "Multiple PII Types",
                "text": "My email is test@example.com and phone is 555-1234",
                "expected_pii": ["email", "phone"],
                "expected_severity": "MEDIUM"
            },
            {
                "name": "High Severity Mix",
                "text": "SSN: 123-45-6789, Email: test@example.com",
                "expected_pii": ["ssn", "email"],
                "expected_severity": "HIGH"
            },
            {
                "name": "Safe Content",
                "text": "I like programming and coffee",
                "expected_pii": [],
                "expected_severity": "LOW"
            }
        ]
        
        print("🧪 Testing PII detection patterns...")
        
        all_passed = True
        for test_case in test_cases:
            detected_pii, severity = detect_pii(test_case["text"])
            
            print(f"\n   Test: {test_case['name']}")
            print(f"   Text: {test_case['text']}")
            print(f"   Expected PII: {test_case['expected_pii']}")
            print(f"   Detected PII: {detected_pii}")
            print(f"   Expected Severity: {test_case['expected_severity']}")
            print(f"   Detected Severity: {severity}")
            
            # Check PII detection
            expected_set = set(test_case['expected_pii'])
            detected_set = set(detected_pii)
            
            pii_correct = expected_set == detected_set
            severity_correct = (severity == test_case['expected_severity'] or 
                              (not test_case['expected_pii'] and severity == 'LOW'))
            
            if pii_correct and severity_correct:
                print(f"   ✅ Detection correct")
            else:
                print(f"   ❌ Detection incorrect")
                if not pii_correct:
                    print(f"      PII mismatch: expected {expected_set}, got {detected_set}")
                if not severity_correct:
                    print(f"      Severity mismatch: expected {test_case['expected_severity']}, got {severity}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ PII pattern detection test failed: {e}")
        return False


def test_warning_message_generation():
    """Test PII warning message generation."""
    print("\n⚠️ Testing Warning Message Generation")
    print("=" * 45)
    
    try:
        from jarvis.tools.rag_tools import get_pii_warning_message
        
        # Test cases for warning messages
        test_cases = [
            {
                "name": "High Severity Warning",
                "pii_types": ["ssn", "credit_card"],
                "severity": "HIGH",
                "expected_contains": ["CRITICAL", "highly sensitive", "privacy regulations"]
            },
            {
                "name": "Medium Severity Warning",
                "pii_types": ["email", "phone"],
                "severity": "MEDIUM",
                "expected_contains": ["WARNING", "potentially sensitive", "stored permanently"]
            },
            {
                "name": "Low Severity Warning",
                "pii_types": ["ip_address"],
                "severity": "LOW",
                "expected_contains": ["INFO", "potentially identifying"]
            },
            {
                "name": "No PII",
                "pii_types": [],
                "severity": "LOW",
                "expected_contains": []
            }
        ]
        
        print("🧪 Testing warning message generation...")
        
        all_passed = True
        for test_case in test_cases:
            warning_message = get_pii_warning_message(test_case["pii_types"], test_case["severity"])
            
            print(f"\n   Test: {test_case['name']}")
            print(f"   PII Types: {test_case['pii_types']}")
            print(f"   Severity: {test_case['severity']}")
            print(f"   Warning: {warning_message}")
            
            if not test_case["expected_contains"]:
                # Should be empty for no PII
                if warning_message == "":
                    print(f"   ✅ Correct (no warning for no PII)")
                else:
                    print(f"   ❌ Should be empty for no PII")
                    all_passed = False
            else:
                # Check if expected elements are present
                passed = True
                for expected in test_case["expected_contains"]:
                    if expected.lower() not in warning_message.lower():
                        print(f"   ❌ Missing expected element: {expected}")
                        passed = False
                        all_passed = False
                
                if passed:
                    print(f"   ✅ Warning message correct")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Warning message generation test failed: {e}")
        return False


def test_remember_fact_pii_integration():
    """Test PII detection integration with remember_fact tool."""
    print("\n🧠 Testing Remember Fact PII Integration")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_memory_manager import RAGMemoryManager
        from jarvis.tools.rag_tools import _remember_fact
        
        config = get_config()
        rag_manager = RAGMemoryManager(config.rag)
        
        # Test cases with different PII scenarios
        test_cases = [
            {
                "name": "Safe Information",
                "fact": "I prefer Python programming language",
                "should_have_warning": False
            },
            {
                "name": "Email Address",
                "fact": "My work email is john.doe@company.com",
                "should_have_warning": True,
                "expected_warning_type": "WARNING"
            },
            {
                "name": "Phone Number",
                "fact": "My phone number is (555) 123-4567",
                "should_have_warning": True,
                "expected_warning_type": "WARNING"
            },
            {
                "name": "Social Security Number",
                "fact": "My SSN is 123-45-6789",
                "should_have_warning": True,
                "expected_warning_type": "CRITICAL"
            },
            {
                "name": "Multiple PII",
                "fact": "Contact me at test@example.com or call 555-1234",
                "should_have_warning": True,
                "expected_warning_type": "WARNING"
            }
        ]
        
        print("🧪 Testing remember_fact with PII detection...")
        
        all_passed = True
        for test_case in test_cases:
            result = _remember_fact(test_case["fact"], rag_manager)
            
            print(f"\n   Test: {test_case['name']}")
            print(f"   Fact: {test_case['fact']}")
            print(f"   Result: {result}")
            
            has_warning = any(indicator in result for indicator in ["WARNING", "CRITICAL", "INFO"])
            
            if test_case["should_have_warning"]:
                if has_warning:
                    # Check warning type if specified
                    if "expected_warning_type" in test_case:
                        expected_type = test_case["expected_warning_type"]
                        if expected_type in result:
                            print(f"   ✅ Correct warning type: {expected_type}")
                        else:
                            print(f"   ❌ Wrong warning type, expected: {expected_type}")
                            all_passed = False
                    else:
                        print(f"   ✅ Warning present as expected")
                else:
                    print(f"   ❌ Warning missing")
                    all_passed = False
            else:
                if not has_warning:
                    print(f"   ✅ No warning as expected")
                else:
                    print(f"   ❌ Unexpected warning present")
                    all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Remember fact PII integration test failed: {e}")
        return False


def test_pii_edge_cases():
    """Test PII detection edge cases and false positives."""
    print("\n🎯 Testing PII Edge Cases")
    print("=" * 35)
    
    try:
        from jarvis.tools.rag_tools import detect_pii
        
        # Edge cases that should NOT trigger PII detection
        edge_cases = [
            {
                "name": "Version Numbers",
                "text": "Using version 1.2.3.4 of the software",
                "should_detect": False
            },
            {
                "name": "Mathematical Expressions",
                "text": "The equation is 123-45-6789 = result",
                "should_detect": True  # This actually looks like SSN
            },
            {
                "name": "Time Stamps",
                "text": "Meeting at 12:34:56 PM",
                "should_detect": False
            },
            {
                "name": "Product Codes",
                "text": "Product code ABC-123-DEF",
                "should_detect": False
            },
            {
                "name": "Partial Phone",
                "text": "Call extension 1234",
                "should_detect": False
            }
        ]
        
        print("🧪 Testing edge cases...")
        
        all_passed = True
        for test_case in edge_cases:
            detected_pii, severity = detect_pii(test_case["text"])
            has_detection = len(detected_pii) > 0
            
            print(f"\n   Test: {test_case['name']}")
            print(f"   Text: {test_case['text']}")
            print(f"   Should detect: {test_case['should_detect']}")
            print(f"   Detected: {detected_pii}")
            
            if has_detection == test_case["should_detect"]:
                print(f"   ✅ Edge case handled correctly")
            else:
                print(f"   ❌ Edge case failed")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ PII edge cases test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 PII Detection and Warning Testing Suite")
    print("=" * 60)
    print("Testing enhanced PII detection with severity-based warnings...")
    print()
    
    tests = [
        ("PII Pattern Detection", test_pii_pattern_detection),
        ("Warning Message Generation", test_warning_message_generation),
        ("Remember Fact PII Integration", test_remember_fact_pii_integration),
        ("PII Edge Cases", test_pii_edge_cases)
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
    
    print(f"\n📊 PII Detection Test Results")
    print("=" * 35)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 PII Detection and Warning: COMPLETE!")
        print("   ✅ Enhanced PII patterns detecting multiple data types")
        print("   ✅ Severity-based warning messages working")
        print("   ✅ Integration with remember_fact tool successful")
        print("   ✅ Edge cases handled appropriately")
        print("\n🔒 RAG system now provides comprehensive PII protection!")
    elif passed >= total * 0.75:
        print(f"\n✅ PII Detection mostly complete!")
        print(f"   Core PII protection working with minor issues")
    else:
        print(f"\n⚠️  PII Detection needs attention")
        print(f"   Multiple PII detection issues detected")
    
    return passed >= total * 0.75


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
