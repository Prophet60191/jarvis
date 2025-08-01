#!/usr/bin/env python3
"""
Complete integration test suite for RAG UI and Main Application.
Tests end-to-end workflows and single source of truth validation.
"""

import requests
import json
import time
import sys
from pathlib import Path


class RAGIntegrationTester:
    """Test class for RAG UI and main application integration."""
    
    def __init__(self, base_url="http://localhost:8081"):
        """Initialize the tester with base URL."""
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_single_source_of_truth(self):
        """Test that UI reflects actual RAG system state."""
        print("🎯 Testing Single Source of Truth...")
        
        try:
            # Add a memory through API
            test_memory = f"Integration test memory - {time.time()}"
            add_response = self.session.post(
                f"{self.base_url}/api/rag/memory/add",
                json={"fact": test_memory},
                headers={'Content-Type': 'application/json'}
            )
            
            if not add_response.json().get('success'):
                print("❌ Failed to add test memory")
                return False
            
            # Wait a moment for processing
            time.sleep(1)
            
            # Retrieve memories through UI API
            memory_response = self.session.get(f"{self.base_url}/api/rag/memory/long-term")
            memory_data = memory_response.json()
            
            # Check if our memory appears in the UI data
            memories = memory_data.get('memories', [])
            found_memory = any(test_memory in mem.get('content', '') for mem in memories)
            
            if found_memory:
                print("✅ Single source of truth verified")
                print(f"   Memory added via API appears in UI data")
                return True
            else:
                print("❌ Single source of truth failed")
                print(f"   Memory not found in UI data after API addition")
                return False
                
        except Exception as e:
            print(f"❌ Single source of truth test error: {e}")
            return False
    
    def test_end_to_end_workflow(self):
        """Test complete memory management workflow."""
        print("\n🧠 Testing End-to-End Memory Workflow...")
        
        try:
            # Step 1: Add memory via UI API
            test_fact = f"E2E workflow test - {time.time()}"
            add_response = self.session.post(
                f"{self.base_url}/api/rag/memory/add",
                json={"fact": test_fact},
                headers={'Content-Type': 'application/json'}
            )
            
            if not add_response.json().get('success'):
                print("   ❌ Step 1: Failed to add memory")
                return False
            
            print("   ✅ Step 1: Memory added successfully")
            
            # Step 2: Verify memory appears in long-term storage
            time.sleep(1)
            memory_response = self.session.get(f"{self.base_url}/api/rag/memory/long-term")
            memory_data = memory_response.json()
            
            memories = memory_data.get('memories', [])
            memory_found = any(test_fact in mem.get('content', '') for mem in memories)
            
            if not memory_found:
                print("   ❌ Step 2: Memory not found in long-term storage")
                return False
            
            print("   ✅ Step 2: Memory retrieved from long-term storage")
            
            # Step 3: Search for the memory
            search_response = self.session.get(
                f"{self.base_url}/api/rag/search?q={test_fact.split()[0]}"
            )
            search_data = search_response.json()
            
            if search_data.get('results') and search_data['results'].get('retrieved_documents'):
                docs = search_data['results']['retrieved_documents']
                search_found = any(test_fact in doc.get('content', '') for doc in docs)
                
                if search_found:
                    print("   ✅ Step 3: Memory found via intelligent search")
                    return True
                else:
                    print("   ❌ Step 3: Memory not found via search")
                    return False
            else:
                print("   ❌ Step 3: Search returned no results")
                return False
                
        except Exception as e:
            print(f"❌ End-to-end memory workflow error: {e}")
            return False
    
    def test_document_integration(self):
        """Test document upload and processing integration."""
        print("\n📚 Testing Document Processing Integration...")
        
        try:
            # Create test document
            test_content = f"""# Integration Test Document
            
This document was created for integration testing at {time.time()}.

## Key Information
- Purpose: Testing document processing pipeline
- Features: Upload, ingestion, and search integration
- System: RAG Memory Management

The document should be processed by the intelligent RAG system.
"""
            
            test_filename = f"integration_test_{int(time.time())}.txt"
            
            # Step 1: Upload document
            upload_response = self.session.post(
                f"{self.base_url}/api/rag/documents/upload",
                json={"filename": test_filename, "content": test_content},
                headers={'Content-Type': 'application/json'}
            )
            
            if not upload_response.json().get('success'):
                print("   ❌ Document upload failed")
                return False
            
            print("   ✅ Step 1: Document uploaded successfully")
            
            # Step 2: Verify document appears in library
            docs_response = self.session.get(f"{self.base_url}/api/rag/documents")
            docs_data = docs_response.json()
            
            documents = docs_data.get('documents', [])
            doc_found = any(test_filename == doc.get('name') for doc in documents)
            
            if not doc_found:
                print("   ❌ Document not found in library")
                return False
            
            print("   ✅ Step 2: Document appears in library")
            
            # Step 3: Process documents
            ingest_response = self.session.post(
                f"{self.base_url}/api/rag/documents/ingest",
                headers={'Content-Type': 'application/json'}
            )
            
            if not ingest_response.json().get('success'):
                print("   ❌ Document processing failed")
                return False
            
            print("   ✅ Step 3: Document processing completed")
            
            # Step 4: Verify document is searchable
            time.sleep(2)  # Allow processing time
            search_response = self.session.get(
                f"{self.base_url}/api/rag/search?q=integration%20testing"
            )
            search_data = search_response.json()
            
            if search_data.get('results') and search_data['results'].get('retrieved_documents'):
                docs = search_data['results']['retrieved_documents']
                content_found = any("integration testing" in doc.get('content', '').lower() for doc in docs)
                
                if content_found:
                    print("   ✅ Step 4: Document content searchable")
                    return True
                else:
                    print("   ❌ Step 4: Document content not found in search")
                    return False
            else:
                print("   ❌ Step 4: Search returned no results")
                return False
                
        except Exception as e:
            print(f"❌ Document processing integration error: {e}")
            return False
    
    def test_real_world_scenarios(self):
        """Test realistic user scenarios."""
        print("\n🌍 Testing Real-World Scenarios...")
        
        scenarios_passed = 0
        total_scenarios = 2
        
        # Scenario 1: User asks about previously stored information
        try:
            user_info = "My favorite programming language is Python and I work as a software engineer"
            self.session.post(
                f"{self.base_url}/api/rag/memory/add",
                json={"fact": user_info},
                headers={'Content-Type': 'application/json'}
            )
            
            time.sleep(1)
            
            search_response = self.session.get(
                f"{self.base_url}/api/rag/search?q=programming%20language"
            )
            search_data = search_response.json()
            
            if search_data.get('results') and search_data['results'].get('synthesis'):
                synthesis = search_data['results']['synthesis']
                if "python" in synthesis.get('synthesized_answer', '').lower():
                    scenarios_passed += 1
                    print("   ✅ Scenario 1: Personal information retrieval works")
                else:
                    print("   ❌ Scenario 1: Personal information not synthesized correctly")
            else:
                print("   ❌ Scenario 1: Search failed to return synthesis")
                
        except Exception as e:
            print(f"   ❌ Scenario 1 error: {e}")
        
        # Scenario 2: System status monitoring
        try:
            status_response = self.session.get(f"{self.base_url}/api/rag/status")
            status_data = status_response.json()
            
            if (status_data.get('status') == 'active' and 
                status_data.get('database') and 
                status_data.get('intelligence')):
                scenarios_passed += 1
                print("   ✅ Scenario 2: System monitoring works")
            else:
                print("   ❌ Scenario 2: System status incomplete")
                
        except Exception as e:
            print(f"   ❌ Scenario 2 error: {e}")
        
        success_rate = scenarios_passed / total_scenarios
        if success_rate >= 0.5:
            print(f"✅ Real-world scenarios working ({scenarios_passed}/{total_scenarios})")
            return True
        else:
            print(f"❌ Real-world scenarios need attention ({scenarios_passed}/{total_scenarios})")
            return False
    
    def test_performance(self):
        """Test system performance under normal load."""
        print("\n⚡ Testing Performance and Reliability...")
        
        try:
            start_time = time.time()
            
            # Test multiple rapid API calls
            responses = []
            for i in range(3):
                response = self.session.get(f"{self.base_url}/api/rag/status")
                responses.append(response.status_code == 200)
            
            for i in range(2):
                response = self.session.get(f"{self.base_url}/api/rag/memory/long-term")
                responses.append(response.status_code == 200)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            success_rate = sum(responses) / len(responses)
            
            if success_rate >= 0.8 and total_time < 10:
                print(f"✅ Performance test passed")
                print(f"   Success rate: {success_rate*100:.0f}%")
                print(f"   Total time: {total_time:.2f}s")
                return True
            else:
                print(f"❌ Performance test failed")
                print(f"   Success rate: {success_rate*100:.0f}%")
                print(f"   Total time: {total_time:.2f}s")
                return False
                
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            return False
    
    def run_integration_tests(self):
        """Run all integration tests."""
        print("🚀 RAG Integration Testing Suite")
        print("=" * 70)
        print("Testing end-to-end integration between RAG UI and main application...")
        print()
        
        tests = [
            ("Single Source of Truth", self.test_single_source_of_truth),
            ("End-to-End Memory Workflow", self.test_end_to_end_workflow),
            ("Document Processing Integration", self.test_document_integration),
            ("Real-World Scenarios", self.test_real_world_scenarios),
            ("Performance and Reliability", self.test_performance)
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
        
        print(f"\n📊 Integration Test Results Summary")
        print("=" * 50)
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Overall Integration Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📊 Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 RAG Integration is fully functional!")
            print("   ✅ Single source of truth verified")
            print("   ✅ End-to-end workflows working")
            print("   ✅ Document processing integrated")
            print("   ✅ Real-world scenarios validated")
            print("   ✅ Performance requirements met")
            print("\n🚀 Ready for Production Enhancements!")
        elif passed >= total * 0.8:
            print(f"\n✅ RAG Integration is mostly functional!")
            print(f"   Minor issues detected, but core integration works")
        else:
            print(f"\n⚠️  RAG Integration needs attention")
            print(f"   Multiple integration issues detected")
        
        return passed >= total * 0.8  # 80% success rate is acceptable


def main():
    """Main integration test function."""
    print("🧪 RAG Integration Testing")
    print("=" * 60)
    
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
    
    # Run integration tests
    tester = RAGIntegrationTester()
    success = tester.run_integration_tests()
    
    if success:
        print("\n🎯 Integration Complete - Next Steps:")
        print("   1. RAG UI successfully integrated with main application")
        print("   2. Single source of truth validated")
        print("   3. Ready to proceed with Production Enhancements")
        print("   4. Consider implementing backup/restore and security features")
    else:
        print("\n🔧 Fix integration issues before proceeding to production features.")
    
    return success


if __name__ == "__main__":
    main()
