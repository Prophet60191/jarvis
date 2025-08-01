#!/usr/bin/env python3
"""
RAG Database Mock Data Cleanup Script

This script removes mock/test data from the RAG database while preserving
legitimate documents and system information.
"""

import sys
import os
sys.path.insert(0, '.')
os.environ['PYTHONPATH'] = '/Users/josed/Desktop/Voice App'

def cleanup_mock_data():
    """Clean up mock test data from the RAG database."""
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        print('🧹 RAG Database Mock Data Cleanup')
        print('=' * 50)
        
        # Get total count before cleanup
        total_before = rag_service.vector_store._collection.count()
        print(f'Total items before cleanup: {total_before}')
        
        # Define patterns that identify mock test data
        mock_data_patterns = [
            # Personal info from user simulation
            'Alex', 'name is Alex', '28 years old',
            'San Francisco', 'software engineer',
            'favorite food is sushi', 'Japanese cuisine',
            'wake up at 6 AM', 'morning run',
            'Python and JavaScript', 'programming languages',
            'cat named Whiskers', '3 years old',
            'Sarah works at Google', 'met in college',
            'trip to Japan', 'December for my birthday',
            'learning to play guitar', 'practice 30 minutes daily',
            'machine learning project', 'natural language processing',
            'senior AI engineer', 'tech meetup every Thursday',
            
            # Test data from earlier sessions
            'favorite color is blue',
            'I like coffee in the morning',
            'I like coffee',
            'I like tea',
            'I like to travel during holidays',
            'User likes to code at 3 PM every day',
            'I work as a software engineer',
            
            # RAG testing specific data
            'RAG system testing on July 31, 2025',
            'it works perfectly',
            'My favorite programming language is Python because',
            'elegant and powerful',
            'I prefer working in the morning between 8 AM and 11 AM',
            'most productive',
            'voice assistant called Jarvis with RAG capabilities',
            'science fiction books',
            'Isaac Asimov and Philip K. Dick',
            'VS Code with the Python extension'
        ]
        
        print(f'\\nSearching for mock data using {len(mock_data_patterns)} patterns...')
        
        # Collect items to delete
        items_to_delete = set()  # Use set to avoid duplicates
        
        for pattern in mock_data_patterns:
            try:
                # Search for items matching this pattern
                results = rag_service.vector_store.similarity_search(
                    pattern, 
                    k=20,  # Get more results to catch variations
                    filter={'source_type': 'conversational'}
                )
                
                for result in results:
                    content = result.page_content.lower()
                    pattern_lower = pattern.lower()
                    
                    # Check if this content contains the mock data pattern
                    if pattern_lower in content:
                        # Create a unique identifier for this item
                        item_id = (result.page_content, str(result.metadata))
                        items_to_delete.add(item_id)
                        
            except Exception as e:
                print(f'Warning: Error searching for pattern "{pattern}": {e}')
        
        print(f'Found {len(items_to_delete)} unique mock data items to remove')
        
        if len(items_to_delete) == 0:
            print('✅ No mock data found - database is already clean!')
            return True
        
        # Show some examples of what will be deleted
        print('\\nExamples of mock data to be removed:')
        print('-' * 40)
        for i, (content, metadata) in enumerate(list(items_to_delete)[:10], 1):
            preview = content[:80].replace('\\n', ' ')
            print(f'{i}. {preview}...')
        
        if len(items_to_delete) > 10:
            print(f'... and {len(items_to_delete) - 10} more items')
        
        # Ask for confirmation
        print(f'\\n⚠️  This will delete {len(items_to_delete)} items from the database.')
        print('This action cannot be undone.')
        
        # For automated cleanup, we'll proceed (in a real scenario, you might want user confirmation)
        print('\\n🗑️  Proceeding with cleanup...')
        
        # Unfortunately, ChromaDB doesn't have a direct way to delete by content
        # The safest approach is to recreate the collection with only the data we want to keep
        
        print('\\n📋 Collecting legitimate data to preserve...')
        
        # Get all documents (these should be preserved)
        documents_to_keep = rag_service.vector_store.similarity_search(
            'system', 
            k=100,
            filter={'source_type': 'document'}
        )
        
        print(f'Found {len(documents_to_keep)} documents to preserve')
        
        # Get legitimate conversational data (system updates, etc.)
        legitimate_conv_data = []
        
        # Search for legitimate system information
        system_patterns = [
            'JARVIS SYSTEM UPDATE',
            'FILE: jarvis/',
            'LAST_UPDATED:',
            'PURPOSE:',
            'Fast/Slow Path Routing',
            'Wake word detection'
        ]
        
        for pattern in system_patterns:
            try:
                results = rag_service.vector_store.similarity_search(
                    pattern,
                    k=50,
                    filter={'source_type': 'conversational'}
                )
                
                for result in results:
                    content = result.page_content
                    # Check if this is legitimate system data (not mock user data)
                    if any(sys_pattern.lower() in content.lower() for sys_pattern in system_patterns):
                        # Make sure it's not mock data
                        is_mock = any(mock_pattern.lower() in content.lower() for mock_pattern in mock_data_patterns)
                        if not is_mock:
                            legitimate_conv_data.append(result)
                            
            except Exception as e:
                print(f'Warning: Error searching for system pattern "{pattern}": {e}')
        
        # Remove duplicates from legitimate data
        unique_legitimate = []
        seen_content = set()
        
        for item in legitimate_conv_data:
            content_key = item.page_content[:100]  # Use first 100 chars as key
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_legitimate.append(item)
        
        print(f'Found {len(unique_legitimate)} legitimate conversational items to preserve')
        
        # Calculate what will be removed
        total_to_keep = len(documents_to_keep) + len(unique_legitimate)
        total_to_remove = total_before - total_to_keep
        
        print(f'\\n📊 Cleanup Summary:')
        print(f'  Total items before: {total_before}')
        print(f'  Documents to keep: {len(documents_to_keep)}')
        print(f'  Legitimate conv data to keep: {len(unique_legitimate)}')
        print(f'  Total to keep: {total_to_keep}')
        print(f'  Total to remove: {total_to_remove}')
        
        if total_to_remove <= 0:
            print('✅ No cleanup needed - all data appears legitimate!')
            return True
        
        print(f'\\n🔄 Performing cleanup by recreating collection...')
        
        # Get the collection name
        collection_name = rag_service.config.rag.collection_name
        
        # Delete the existing collection
        try:
            rag_service.vector_store._client.delete_collection(collection_name)
            print(f'✅ Deleted old collection: {collection_name}')
        except Exception as e:
            print(f'Warning: Could not delete collection: {e}')
        
        # Recreate the RAG service to get a fresh collection
        rag_service = RAGService(config)
        print(f'✅ Created fresh collection: {collection_name}')
        
        # Add back the legitimate data
        print('\\n📥 Restoring legitimate data...')
        
        # Add documents
        if documents_to_keep:
            rag_service.vector_store.add_documents(documents_to_keep)
            print(f'✅ Restored {len(documents_to_keep)} documents')
        
        # Add legitimate conversational data
        if unique_legitimate:
            rag_service.vector_store.add_documents(unique_legitimate)
            print(f'✅ Restored {len(unique_legitimate)} legitimate conversational items')
        
        # Verify final count
        final_count = rag_service.vector_store._collection.count()
        removed_count = total_before - final_count
        
        print(f'\\n🎉 Cleanup Complete!')
        print(f'  Items before: {total_before}')
        print(f'  Items after: {final_count}')
        print(f'  Items removed: {removed_count}')
        print(f'  Cleanup efficiency: {(removed_count/total_before)*100:.1f}%')
        
        return True
        
    except Exception as e:
        print(f'❌ Error during cleanup: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = cleanup_mock_data()
    if success:
        print('\\n✅ Mock data cleanup completed successfully!')
    else:
        print('\\n❌ Mock data cleanup failed!')
    
    sys.exit(0 if success else 1)
