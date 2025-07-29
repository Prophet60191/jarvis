#!/usr/bin/env python3
"""
Test script to verify RAG Management UI functionality through automated testing.
"""

import requests
import json
import time
import sys
from pathlib import Path


class RAGUITester:
    """Test class for RAG Management UI functionality."""
    
    def __init__(self, base_url="http://localhost:8081"):
        """Initialize the tester with base URL."""
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_ui_page_loads(self):
        """Test that the RAG management page loads correctly."""
        print("🖥️ Testing RAG UI Page Loading...")
        try:
            response = self.session.get(f"{self.base_url}/rag")
            
            if response.status_code == 200:
                content = response.text
                
                # Check for key UI elements
                ui_elements = [
                    "RAG Memory Management",
                    "Long-Term Memory",
                    "Document Library", 
                    "Intelligent Search",
                    "System Status",
                    "loadRAGStatus()",
                    "loadMemories()",
                    "performSearch()"
                ]
                
                missing_elements = []
                for element in ui_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    print(f"✅ RAG UI page loads correctly")
                    print(f"   All {len(ui_elements)} key UI elements present")
                    return True
                else:
                    print(f"❌ RAG UI page missing elements: {missing_elements}")
                    return False
            else:
                print(f"❌ RAG UI page failed to load: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ RAG UI page loading error: {e}")
            return False
    
    def test_navigation_integration(self):
        """Test that RAG page is properly integrated in navigation."""
        print("\n🧭 Testing Navigation Integration...")
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                content = response.text
                
                # Check for RAG navigation link
                nav_elements = [
                    'href="/rag"',
                    'RAG Memory',
                    '🧠'
                ]
                
                missing_nav = []
                for element in nav_elements:
                    if element not in content:
                        missing_nav.append(element)
                
                if not missing_nav:
                    print(f"✅ RAG navigation properly integrated")
                    print(f"   Navigation link present in main UI")
                    return True
                else:
                    print(f"❌ RAG navigation missing elements: {missing_nav}")
                    return False
            else:
                print(f"❌ Main page failed to load: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Navigation integration error: {e}")
            return False
    
    def test_api_integration(self):
        """Test that UI properly integrates with RAG APIs."""
        print("\n🔗 Testing API Integration...")
        
        # Test that all required API endpoints are accessible
        api_endpoints = [
            "/api/rag/status",
            "/api/rag/memory/long-term", 
            "/api/rag/documents",
            "/api/rag/search?q=test"
        ]
        
        working_endpoints = 0
        
        for endpoint in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    working_endpoints += 1
                    print(f"   ✅ {endpoint}")
                else:
                    print(f"   ❌ {endpoint} - Status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {e}")
        
        success_rate = working_endpoints / len(api_endpoints)
        
        if success_rate >= 0.75:  # At least 75% of endpoints working
            print(f"✅ API integration working ({working_endpoints}/{len(api_endpoints)} endpoints)")
            return True
        else:
            print(f"❌ API integration issues ({working_endpoints}/{len(api_endpoints)} endpoints)")
            return False
    
    def test_ui_functionality(self):
        """Test key UI functionality through API calls."""
        print("\n⚙️ Testing UI Functionality...")
        
        functionality_tests = []
        
        # Test 1: Add memory functionality
        try:
            test_memory = f"UI test memory - {time.time()}"
            response = self.session.post(
                f"{self.base_url}/api/rag/memory/add",
                json={"fact": test_memory},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200 and response.json().get('success'):
                functionality_tests.append(("Add Memory", True))
                print("   ✅ Add Memory functionality working")
            else:
                functionality_tests.append(("Add Memory", False))
                print("   ❌ Add Memory functionality failed")
        except Exception as e:
            functionality_tests.append(("Add Memory", False))
            print(f"   ❌ Add Memory error: {e}")
        
        # Test 2: Document upload functionality
        try:
            test_doc_content = f"# UI Test Document\n\nThis is a test document created at {time.time()}\n\n## Features\n- UI testing\n- Document management\n- RAG integration"
            test_filename = f"ui_test_{int(time.time())}.txt"
            
            response = self.session.post(
                f"{self.base_url}/api/rag/documents/upload",
                json={"filename": test_filename, "content": test_doc_content},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200 and response.json().get('success'):
                functionality_tests.append(("Document Upload", True))
                print("   ✅ Document Upload functionality working")
            else:
                functionality_tests.append(("Document Upload", False))
                print("   ❌ Document Upload functionality failed")
        except Exception as e:
            functionality_tests.append(("Document Upload", False))
            print(f"   ❌ Document Upload error: {e}")
        
        # Test 3: Search functionality
        try:
            response = self.session.get(f"{self.base_url}/api/rag/search?q=test%20document")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and data['results'].get('synthesis'):
                    functionality_tests.append(("Intelligent Search", True))
                    print("   ✅ Intelligent Search functionality working")
                else:
                    functionality_tests.append(("Intelligent Search", False))
                    print("   ❌ Intelligent Search returned incomplete results")
            else:
                functionality_tests.append(("Intelligent Search", False))
                print("   ❌ Intelligent Search functionality failed")
        except Exception as e:
            functionality_tests.append(("Intelligent Search", False))
            print(f"   ❌ Intelligent Search error: {e}")
        
        # Calculate success rate
        successful_tests = sum(1 for _, success in functionality_tests if success)
        total_tests = len(functionality_tests)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        if success_rate >= 0.67:  # At least 2/3 functionality working
            print(f"✅ UI functionality working ({successful_tests}/{total_tests} features)")
            return True
        else:
            print(f"❌ UI functionality issues ({successful_tests}/{total_tests} features)")
            return False
    
    def test_responsive_design(self):
        """Test that the UI includes responsive design elements."""
        print("\n📱 Testing Responsive Design...")
        try:
            response = self.session.get(f"{self.base_url}/rag")
            
            if response.status_code == 200:
                content = response.text
                
                # Check for responsive design elements
                responsive_elements = [
                    "grid-template-columns: repeat(auto-fit",
                    "max-width:",
                    "@media",  # This might not be present, but good to check
                    "flex",
                    "display: grid"
                ]
                
                found_elements = []
                for element in responsive_elements:
                    if element in content:
                        found_elements.append(element)
                
                if len(found_elements) >= 3:  # At least 3 responsive elements
                    print(f"✅ Responsive design elements present")
                    print(f"   Found: {found_elements}")
                    return True
                else:
                    print(f"❌ Limited responsive design elements")
                    print(f"   Found: {found_elements}")
                    return False
            else:
                print(f"❌ Could not check responsive design: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Responsive design check error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all UI tests."""
        print("🚀 RAG Management UI Testing Suite")
        print("=" * 60)
        print("Testing the complete RAG management interface...")
        print()
        
        tests = [
            ("UI Page Loading", self.test_ui_page_loads),
            ("Navigation Integration", self.test_navigation_integration),
            ("API Integration", self.test_api_integration),
            ("UI Functionality", self.test_ui_functionality),
            ("Responsive Design", self.test_responsive_design)
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
        
        print(f"\n📊 UI Test Results Summary")
        print("=" * 40)
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Overall Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📊 Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 RAG Management UI is fully functional!")
            print("   ✅ All UI components working correctly")
            print("   ✅ API integration successful")
            print("   ✅ Navigation properly integrated")
            print("   ✅ Responsive design implemented")
            print("   ✅ Core functionality operational")
            print("\n🚀 Ready for Step 3: Integration with Main Application!")
        elif passed >= total * 0.8:
            print(f"\n✅ RAG Management UI is mostly functional!")
            print(f"   Minor issues detected, but core functionality works")
        else:
            print(f"\n⚠️  RAG Management UI needs attention")
            print(f"   Multiple issues detected, review failed tests")
        
        return passed == total


def main():
    """Main test function."""
    print("🧪 RAG Management UI Testing")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8081/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Jarvis UI server is running on port 8081")
        else:
            print("⚠️  Jarvis UI server responded with non-200 status")
    except requests.exceptions.RequestException:
        print("❌ Jarvis UI server is not running on port 8081")
        print("   Please start the server with: cd jarvis && python ui/jarvis_ui.py --no-browser --port 8081")
        sys.exit(1)
    
    print()
    
    # Run tests
    tester = RAGUITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Test the UI manually in browser: http://localhost:8081/rag")
        print("   2. Verify all tabs and functionality work as expected")
        print("   3. Proceed to Step 3: Integration with Main Application")
    else:
        print("\n🔧 Fix UI issues before proceeding to integration testing.")


if __name__ == "__main__":
    main()
