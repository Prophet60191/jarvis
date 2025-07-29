"""
Mock Database Agent for RAG Management UI Testing

This is a temporary mock implementation of the Database Agent to test
the RAG Management UI functionality while we develop the full agent.
"""

import asyncio
import random
import time
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class MergePlan:
    """Mock merge plan structure."""
    document_source: str
    total_entities: int
    summary: str
    estimated_processing_time: float
    warnings: List[str]
    entities_to_add: List[Dict]
    entities_to_update: List[Dict]
    entities_to_mark_outdated: List[Dict]


class MockDatabaseAgent:
    """Mock Database Agent for testing RAG Management UI."""
    
    def __init__(self, config=None):
        self.config = config
        self.model_name = "Qwen2.5:3b-instruct"
        
    async def process_document_upload(self, content: str, filename: str, existing_data: list) -> MergePlan:
        """Mock document processing with realistic delays and responses."""
        
        # Simulate processing time
        processing_time = random.uniform(1.0, 3.0)
        await asyncio.sleep(processing_time)
        
        # Analyze content to generate realistic mock data
        content_length = len(content)
        word_count = len(content.split())
        
        # Mock entity extraction based on content
        mock_entities = self._extract_mock_entities(content, filename)
        
        # Generate mock summary
        summary = self._generate_mock_summary(filename, content_length, word_count)
        
        # Mock warnings based on content analysis
        warnings = self._generate_mock_warnings(content, filename)
        
        return MergePlan(
            document_source=filename,
            total_entities=len(mock_entities),
            summary=summary,
            estimated_processing_time=round(processing_time, 2),
            warnings=warnings,
            entities_to_add=mock_entities[:3],  # First 3 as new
            entities_to_update=mock_entities[3:5] if len(mock_entities) > 3 else [],  # Next 2 as updates
            entities_to_mark_outdated=[]  # None for now
        )
    
    def _extract_mock_entities(self, content: str, filename: str) -> List[Dict]:
        """Extract mock entities based on content analysis."""
        entities = []
        
        # Look for common patterns and generate mock entities
        lines = content.split('\n')
        
        for i, line in enumerate(lines[:10]):  # Process first 10 lines
            line = line.strip()
            if not line:
                continue
                
            # Mock different entity types based on content patterns
            if '@' in line:
                entities.append({
                    "type": "email",
                    "value": line,
                    "confidence": random.uniform(0.8, 0.95),
                    "line_number": i + 1
                })
            elif any(word in line.lower() for word in ['phone', 'tel', 'call']):
                entities.append({
                    "type": "contact_info",
                    "value": line,
                    "confidence": random.uniform(0.7, 0.9),
                    "line_number": i + 1
                })
            elif any(word in line.lower() for word in ['name', 'person', 'contact']):
                entities.append({
                    "type": "person",
                    "value": line,
                    "confidence": random.uniform(0.6, 0.85),
                    "line_number": i + 1
                })
            elif len(line.split()) > 5:  # Longer lines might be descriptions
                entities.append({
                    "type": "description",
                    "value": line[:50] + "..." if len(line) > 50 else line,
                    "confidence": random.uniform(0.5, 0.8),
                    "line_number": i + 1
                })
        
        # Add some mock structured data
        if filename.lower().endswith('.txt'):
            entities.append({
                "type": "document_metadata",
                "value": f"Text document with {len(content.split())} words",
                "confidence": 0.95,
                "line_number": 0
            })
        
        return entities[:8]  # Limit to 8 entities for testing
    
    def _generate_mock_summary(self, filename: str, content_length: int, word_count: int) -> str:
        """Generate a realistic mock summary."""
        file_type = filename.split('.')[-1].upper() if '.' in filename else 'Unknown'
        
        summaries = [
            f"Processed {file_type} document containing {word_count} words with structured data extraction",
            f"Analyzed {filename} and identified key entities including contacts and metadata",
            f"Document processing complete: {content_length} characters analyzed for entity relationships",
            f"Intelligent parsing of {file_type} format yielded {random.randint(3, 12)} distinct data points",
            f"Content analysis revealed structured information suitable for knowledge base integration"
        ]
        
        return random.choice(summaries)
    
    def _generate_mock_warnings(self, content: str, filename: str) -> List[str]:
        """Generate realistic mock warnings."""
        warnings = []
        
        # Check for potential issues
        if len(content) < 100:
            warnings.append("Document is very short - may have limited extractable data")
        
        if len(content) > 50000:
            warnings.append("Large document - processing may take longer than usual")
        
        if not any(char.isalpha() for char in content):
            warnings.append("Document contains mostly non-text content")
        
        # Random warnings for testing
        if random.random() < 0.3:  # 30% chance
            warnings.append("Some entities may require manual verification")
        
        if random.random() < 0.2:  # 20% chance
            warnings.append("Detected potential duplicate information")
        
        return warnings


def get_database_agent(config=None):
    """Factory function to get Database Agent instance."""
    return MockDatabaseAgent(config)


# For testing
if __name__ == "__main__":
    async def test_mock_agent():
        agent = MockDatabaseAgent()
        
        test_content = """
        John Doe
        Email: john.doe@example.com
        Phone: (555) 123-4567
        
        Mary Smith
        Email: mary.smith@company.com
        Phone: (555) 987-6543
        
        This is a test document with some contact information
        and other structured data for testing the Database Agent.
        """
        
        result = await agent.process_document_upload(
            content=test_content,
            filename="test_contacts.txt",
            existing_data=[]
        )
        
        print("Mock Database Agent Test Results:")
        print(f"Document: {result.document_source}")
        print(f"Entities: {result.total_entities}")
        print(f"Summary: {result.summary}")
        print(f"Processing Time: {result.estimated_processing_time}s")
        print(f"Warnings: {result.warnings}")
        print(f"New Entities: {len(result.entities_to_add)}")
        print(f"Updated Entities: {len(result.entities_to_update)}")
    
    asyncio.run(test_mock_agent())
