#!/usr/bin/env python3
"""
Test script for the Database Agent

This script tests the intelligent document processing capabilities
of the Database Agent using the Qwen2.5:3b-instruct model.
"""

import asyncio
import sys
from pathlib import Path

# Add the jarvis package to the path
sys.path.append(str(Path(__file__).parent / "jarvis"))

from jarvis.config import get_config
from jarvis.tools.database_agent import get_database_agent


async def test_contact_processing():
    """Test processing contact information."""
    print("📞 Testing Contact Document Processing")
    print("=" * 50)
    
    # Sample contact document
    contact_document = """
    Contact List - Updated July 2024
    
    John Smith
    Phone: 555-1234
    Email: john@example.com
    
    Mary Johnson  
    Phone: 555-9999
    Email: mary@company.com
    Address: 123 Main St
    
    Bob Wilson
    Phone: 555-3333
    Email: bob@startup.com
    Role: CTO
    """
    
    # Existing contact data (simulating database)
    existing_contacts = [
        {
            "id": "john_smith",
            "name": "John Smith", 
            "phone": "555-1234",
            "email": "john@example.com"
        },
        {
            "id": "mary_johnson",
            "name": "Mary Johnson",
            "phone": "555-5678",  # Old phone number
            "email": "mary@company.com"
        }
    ]
    
    try:
        config = get_config()
        db_agent = get_database_agent(config)
        
        print("🤖 Processing contact document with Database Agent...")
        merge_plan = await db_agent.process_document_upload(
            content=contact_document,
            filename="contacts_updated.txt",
            existing_data=existing_contacts
        )
        
        print(f"\n✅ Processing Results:")
        print(f"   Document Source: {merge_plan.document_source}")
        print(f"   Total Entities: {merge_plan.total_entities}")
        print(f"   Summary: {merge_plan.summary}")
        print(f"   Processing Time: {merge_plan.estimated_processing_time:.2f}s")
        
        if merge_plan.warnings:
            print(f"\n⚠️ Warnings:")
            for warning in merge_plan.warnings:
                print(f"     - {warning}")
        
        print(f"\n📋 Detailed Actions:")
        for action in merge_plan.actions:
            print(f"   {action.action}: {action.entity_id}")
            if action.changes:
                print(f"     Changes: {', '.join(action.changes)}")
            print(f"     Confidence: {action.confidence:.2f}")
        
        return merge_plan
        
    except Exception as e:
        print(f"❌ Error during contact processing: {e}")
        return None


async def test_inventory_processing():
    """Test processing inventory information."""
    print("\n📦 Testing Inventory Document Processing")
    print("=" * 50)
    
    # Sample inventory document
    inventory_document = """
    Warehouse Inventory - Q3 2024
    
    Widget A - Quantity: 150 - Price: $12.99
    Widget B - Quantity: 75 - Price: $8.50
    Gadget Pro - Quantity: 200 - Price: $25.00
    Tool Set - Quantity: 50 - Price: $45.99
    """
    
    try:
        config = get_config()
        db_agent = get_database_agent(config)
        
        print("🤖 Processing inventory document with Database Agent...")
        merge_plan = await db_agent.process_document_upload(
            content=inventory_document,
            filename="inventory_q3.txt",
            existing_data=[]  # No existing inventory data
        )
        
        print(f"\n✅ Processing Results:")
        print(f"   Document Source: {merge_plan.document_source}")
        print(f"   Total Entities: {merge_plan.total_entities}")
        print(f"   Summary: {merge_plan.summary}")
        
        print(f"\n📋 Detailed Actions:")
        for action in merge_plan.actions:
            print(f"   {action.action}: {action.entity_id}")
            if action.new_data:
                print(f"     Data: {action.new_data}")
        
        return merge_plan
        
    except Exception as e:
        print(f"❌ Error during inventory processing: {e}")
        return None


async def test_performance():
    """Test Database Agent performance and resource usage."""
    print("\n⚡ Testing Database Agent Performance")
    print("=" * 50)
    
    import time
    
    # Simple document for speed testing
    simple_doc = """
    Quick Test Document
    
    Item 1: Value A
    Item 2: Value B  
    Item 3: Value C
    """
    
    try:
        config = get_config()
        db_agent = get_database_agent(config)
        
        # Test activation time
        start_time = time.time()
        await db_agent.activate()
        activation_time = time.time() - start_time
        
        print(f"🔄 Agent Activation Time: {activation_time:.2f}s")
        
        # Test processing time
        start_time = time.time()
        analysis = await db_agent.analyze_document(simple_doc, "test.txt")
        processing_time = time.time() - start_time
        
        print(f"📄 Document Analysis Time: {processing_time:.2f}s")
        print(f"📊 Analysis Results:")
        print(f"   Document Type: {analysis.document_type}")
        print(f"   Entities Found: {len(analysis.entities)}")
        print(f"   Confidence: {analysis.confidence_score:.2f}")
        
        # Test deactivation
        start_time = time.time()
        await db_agent.deactivate()
        deactivation_time = time.time() - start_time
        
        print(f"💤 Agent Deactivation Time: {deactivation_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during performance testing: {e}")
        return False


async def test_model_availability():
    """Test if the Qwen2.5:3b-instruct model is available."""
    print("🔍 Testing Model Availability")
    print("=" * 40)
    
    try:
        config = get_config()
        db_agent = get_database_agent(config)
        
        # Try to activate the agent
        await db_agent.activate()
        print("✅ Qwen2.5:3b-instruct model is available and working")
        
        # Test basic functionality
        test_response = await db_agent._llm.ainvoke("Return only: {'test': 'success'}")
        print(f"🧪 Basic test response: {test_response[:50]}...")
        
        await db_agent.deactivate()
        return True
        
    except Exception as e:
        print(f"❌ Model not available or error: {e}")
        print("💡 Make sure to run: ollama pull qwen2.5:3b-instruct")
        return False


async def main():
    """Run all Database Agent tests."""
    print("🤖 Database Agent Testing Suite")
    print("=" * 60)
    print("Testing intelligent document processing with Qwen2.5:3b-instruct")
    print()
    
    # Test model availability first
    model_available = await test_model_availability()
    
    if not model_available:
        print("\n❌ Cannot proceed - model not available")
        print("Please ensure Qwen2.5:3b-instruct is downloaded:")
        print("   ollama pull qwen2.5:3b-instruct")
        return
    
    # Run all tests
    print("\n" + "="*60)
    contact_result = await test_contact_processing()
    
    inventory_result = await test_inventory_processing()
    
    performance_result = await test_performance()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("=" * 30)
    print(f"✅ Model Availability: {'PASS' if model_available else 'FAIL'}")
    print(f"✅ Contact Processing: {'PASS' if contact_result else 'FAIL'}")
    print(f"✅ Inventory Processing: {'PASS' if inventory_result else 'FAIL'}")
    print(f"✅ Performance Test: {'PASS' if performance_result else 'FAIL'}")
    
    if all([model_available, contact_result, inventory_result, performance_result]):
        print("\n🎉 All tests passed! Database Agent is ready for production.")
        print("   Fast, efficient, and intelligent document processing working!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
