#!/usr/bin/env python3
"""
Test script to verify RAG API endpoints are working correctly.
"""

import requests
import json
import time
import sys
from pathlib import Path


class RAGAPITester:
    """Test class for RAG API endpoints."""
    
    def __init__(self, base_url="http://localhost:8081"):
        """Initialize the tester with base URL."""
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_rag_status(self):
        """Test RAG status endpoint."""
        print("🔍 Testing RAG Status API...")
        try:
            response = self.session.get(f"{self.base_url}/api/rag/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ RAG Status API working")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Total Documents: {data.get('database', {}).get('total_documents', 0)}")
                print(f"   Unique Sources: {data.get('database', {}).get('unique_sources', 0)}")
                print(f"   Intelligence Features: {data.get('intelligence', {}).get('features', [])}")
                return True
            else:
                print(f"❌ RAG Status API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ RAG Status API error: {e}")
            return False
    
    def test_long_term_memory(self):
        """Test long-term memory endpoint."""
        print("\n🧠 Testing Long-Term Memory API...")
        try:
            response = self.session.get(f"{self.base_url}/api/rag/memory/long-term")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Long-Term Memory API working")
                print(f"   Total Memories: {data.get('total_count', 0)}")
                print(f"   Conversational: {data.get('conversational_count', 0)}")
                print(f"   Document: {data.get('document_count', 0)}")
                
                memories = data.get('memories', [])
                if memories:
                    print(f"   Sample Memory: {memories[0].get('content', 'N/A')[:50]}...")
                
                return True
            else:
                print(f"❌ Long-Term Memory API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Long-Term Memory API error: {e}")
            return False
    
    def test_documents_api(self):
        """Test documents endpoint."""
        print("\n📚 Testing Documents API...")
        try:
            response = self.session.get(f"{self.base_url}/api/rag/documents")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Documents API working")
                print(f"   Total Documents: {data.get('total_count', 0)}")
                print(f"   Ingested: {data.get('ingested_count', 0)}")
                print(f"   Total Size: {data.get('total_size_mb', 0)} MB")
                print(f"   Documents Path: {data.get('documents_path', 'unknown')}")
                
                documents = data.get('documents', [])
                if documents:
                    print(f"   Sample Document: {documents[0].get('name', 'N/A')}")
                
                return True
            else:
                print(f"❌ Documents API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Documents API error: {e}")
            return False
    
    def test_document_stats(self):
        """Test document statistics endpoint."""
        print("\n📊 Testing Document Stats API...")
        try:
            response = self.session.get(f"{self.base_url}/api/rag/documents/stats")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Document Stats API working")
                print(f"   Total Chunks: {data.get('database', {}).get('total_chunks', 0)}")
                print(f"   Avg Chunks/Doc: {data.get('database', {}).get('average_chunks_per_document', 0)}")
                print(f"   Processing Features: {data.get('processing', {}).get('features', [])}")
                return True
            else:
                print(f"❌ Document Stats API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Document Stats API error: {e}")
            return False
    
    def test_search_api(self):
        """Test RAG search endpoint."""
        print("\n🔍 Testing RAG Search API...")
        try:
            test_query = "How do I create plugins?"
            response = self.session.get(f"{self.base_url}/api/rag/search?q={test_query}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ RAG Search API working")
                print(f"   Query: {data.get('query', 'unknown')}")
                
                results = data.get('results', {})
                synthesis = results.get('synthesis', {})
                search_meta = results.get('search_metadata', {})
                
                print(f"   Confidence: {synthesis.get('confidence_score', 0.0)}")
                print(f"   Completeness: {synthesis.get('answer_completeness', 'unknown')}")
                print(f"   Queries Tried: {search_meta.get('queries_tried', [])}")
                print(f"   Final Results: {search_meta.get('final_results', 0)}")
                
                return True
            else:
                print(f"❌ RAG Search API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ RAG Search API error: {e}")
            return False
    
    def test_add_memory(self):
        """Test adding memory endpoint."""
        print("\n➕ Testing Add Memory API...")
        try:
            test_fact = f"API test memory added at {time.time()}"
            payload = {"fact": test_fact}
            
            response = self.session.post(
                f"{self.base_url}/api/rag/memory/add",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Add Memory API working")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Message: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ Add Memory API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Add Memory API error: {e}")
            return False
    
    def test_document_upload(self):
        """Test document upload endpoint."""
        print("\n📤 Testing Document Upload API...")
        try:
            test_content = f"""# Test Document
            
This is a test document uploaded via API at {time.time()}.

## Features
- API testing
- Document management
- RAG integration

This document should be processed by the intelligent RAG system.
"""
            
            payload = {
                "filename": f"api_test_{int(time.time())}.txt",
                "content": test_content
            }
            
            response = self.session.post(
                f"{self.base_url}/api/rag/documents/upload",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Document Upload API working")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Filename: {data.get('filename', 'N/A')}")
                print(f"   Size: {data.get('size', 0)} bytes")
                return True
            else:
                print(f"❌ Document Upload API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Document Upload API error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🚀 RAG API Testing Suite")
        print("=" * 50)
        print("Testing all RAG management API endpoints...")
        print()
        
        tests = [
            self.test_rag_status,
            self.test_long_term_memory,
            self.test_documents_api,
            self.test_document_stats,
            self.test_search_api,
            self.test_add_memory,
            self.test_document_upload
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print(f"\n📊 Test Results Summary")
        print("=" * 30)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All RAG API endpoints are working!")
            print("   The backend REST API is ready for frontend integration.")
        else:
            print(f"\n⚠️  {total - passed} endpoints need attention.")
            print("   Check the error messages above for details.")
        
        return passed == total


def main():
    """Main test function."""
    print("🧪 RAG API Endpoint Testing")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8081/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Jarvis UI server is running")
        else:
            print("⚠️  Jarvis UI server responded with non-200 status")
    except requests.exceptions.RequestException:
        print("❌ Jarvis UI server is not running")
        print("   Please start the server with: python jarvis/ui/jarvis_ui.py")
        sys.exit(1)
    
    print()
    
    # Run tests
    tester = RAGAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Ready for Step 2: Build RAG Management UI!")
    else:
        print("\n🔧 Fix API issues before proceeding to frontend development.")


if __name__ == "__main__":
    main()
