"""
Database Agent for Intelligent Data Management

This agent is specialized for document analysis, entity extraction, and intelligent
data merging. It uses a lightweight LLM (Qwen2.5:3b-instruct) optimized for
structured data tasks.

Key Responsibilities:
- Document structure analysis and data type detection
- Entity extraction and relationship mapping
- Intelligent comparison with existing database content
- Merge planning with version tracking and conflict resolution
- Data quality assurance and validation
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import asyncio

try:
    from langchain_ollama import OllamaLLM
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM

from langchain_core.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentAnalysis:
    """Structured analysis of a document by the Database Agent."""
    document_type: str
    data_schema: Dict[str, str]
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    confidence_score: float
    processing_notes: List[str]


@dataclass
class EntityComparison:
    """Comparison result between new and existing entities."""
    entity_id: str
    action: str  # "ADD", "UPDATE", "KEEP", "DELETE"
    new_data: Optional[Dict[str, Any]]
    old_data: Optional[Dict[str, Any]]
    changes: List[str]
    confidence: float


@dataclass
class MergePlan:
    """Complete plan for merging new data with existing database."""
    document_source: str
    total_entities: int
    actions: List[EntityComparison]
    summary: str
    warnings: List[str]
    estimated_processing_time: float


class DatabaseAgent:
    """
    Specialized LLM agent for intelligent database operations.
    
    This agent uses a lightweight model (Qwen2.5:3b-instruct) optimized for:
    - Fast document processing
    - Reliable structured output
    - Efficient resource usage
    - Thermal-safe operation
    """
    
    def __init__(self, config):
        self.config = config
        self._llm = None
        self._is_active = False
        
        # Specialized prompts for database operations
        self._setup_prompts()
        
        logger.info("🤖 Database Agent initialized (model will load on first use)")
    
    def _setup_prompts(self):
        """Setup specialized prompts optimized for the 3b model."""
        
        # Document analysis prompt - very specific instructions
        self.analysis_prompt = PromptTemplate(
            input_variables=["document_content", "filename"],
            template="""You are a data extraction specialist. Analyze this document and return ONLY valid JSON.

Document: {filename}
Content: {document_content}

Identify the data type and extract entities. Return this exact JSON structure:

{{
    "document_type": "contacts|inventory|notes|schedule|other",
    "data_schema": {{"field1": "type", "field2": "type"}},
    "entities": [
        {{"id": "unique_identifier", "field1": "value1", "field2": "value2"}}
    ],
    "relationships": [
        {{"from": "entity1", "to": "entity2", "type": "relationship_type"}}
    ],
    "confidence_score": 0.95,
    "processing_notes": ["note1", "note2"]
}}

For contacts: extract name, phone, email, address
For inventory: extract item, quantity, price, category
For notes: extract topic, content, tags, date
For schedule: extract event, date, time, location

Return ONLY valid JSON, no explanations."""
        )
        
        # Entity comparison prompt
        self.comparison_prompt = PromptTemplate(
            input_variables=["new_entities", "existing_entities", "document_type"],
            template="""You are a data comparison specialist. Compare entities and return ONLY valid JSON.

Document Type: {document_type}
New Entities: {new_entities}
Existing Entities: {existing_entities}

For each new entity, determine the action needed. Return this exact JSON structure:

{{
    "comparisons": [
        {{
            "entity_id": "unique_identifier",
            "action": "ADD|UPDATE|KEEP|DELETE",
            "new_data": {{"field": "value"}},
            "old_data": {{"field": "old_value"}},
            "changes": ["field1 updated", "field2 added"],
            "confidence": 0.95
        }}
    ],
    "summary": "Brief summary of changes",
    "warnings": ["warning1", "warning2"]
}}

Actions:
- ADD: New entity not in existing data
- UPDATE: Entity exists but has changes
- KEEP: Entity exists and unchanged
- DELETE: Entity no longer in new data

Return ONLY valid JSON, no explanations."""
        )
    
    async def activate(self):
        """Activate the Database Agent LLM when needed."""
        if not self._is_active:
            try:
                logger.info("🔄 Activating Database Agent (Qwen2.5:3b-instruct)...")
                self._llm = OllamaLLM(
                    model="qwen2.5:3b-instruct",
                    temperature=0.1,  # Low temperature for consistent structured output
                    num_ctx=4096,     # Sufficient context for document analysis
                )
                self._is_active = True
                logger.info("✅ Database Agent activated and ready")
            except Exception as e:
                logger.error(f"❌ Failed to activate Database Agent: {e}")
                raise
    
    async def deactivate(self):
        """Deactivate the Database Agent to free resources."""
        if self._is_active:
            self._llm = None
            self._is_active = False
            logger.info("💤 Database Agent deactivated (resources freed)")
    
    async def analyze_document(self, content: str, filename: str) -> DocumentAnalysis:
        """
        Analyze document structure and extract entities.
        
        Args:
            content: Raw document content
            filename: Source filename for context
            
        Returns:
            DocumentAnalysis with structured data extraction
        """
        await self.activate()
        
        try:
            logger.info(f"📄 Analyzing document structure: {filename}")
            
            # Generate analysis using specialized prompt
            prompt = self.analysis_prompt.format(
                document_content=content[:4000],  # Limit content for 3b model
                filename=filename
            )
            
            response = await self._llm.ainvoke(prompt)
            
            # Parse JSON response
            try:
                analysis_data = json.loads(response.strip())
                
                return DocumentAnalysis(
                    document_type=analysis_data.get("document_type", "other"),
                    data_schema=analysis_data.get("data_schema", {}),
                    entities=analysis_data.get("entities", []),
                    relationships=analysis_data.get("relationships", []),
                    confidence_score=analysis_data.get("confidence_score", 0.0),
                    processing_notes=analysis_data.get("processing_notes", [])
                )
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON parsing failed, using fallback analysis: {e}")
                # Fallback to basic analysis
                return self._fallback_analysis(content, filename)
                
        except Exception as e:
            logger.error(f"❌ Document analysis failed: {e}")
            return self._fallback_analysis(content, filename)
    
    def _fallback_analysis(self, content: str, filename: str) -> DocumentAnalysis:
        """Fallback analysis when LLM processing fails."""
        logger.info("🔄 Using fallback document analysis")
        
        # Simple heuristic-based analysis
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['phone', 'email', 'contact', 'address']):
            doc_type = "contacts"
            schema = {"name": "string", "phone": "string", "email": "string"}
        elif any(word in content_lower for word in ['quantity', 'price', 'inventory', 'stock']):
            doc_type = "inventory"
            schema = {"item": "string", "quantity": "number", "price": "number"}
        else:
            doc_type = "notes"
            schema = {"content": "string", "topic": "string"}
        
        return DocumentAnalysis(
            document_type=doc_type,
            data_schema=schema,
            entities=[],  # Would need more sophisticated parsing
            relationships=[],
            confidence_score=0.5,  # Lower confidence for fallback
            processing_notes=["Used fallback analysis due to LLM processing error"]
        )
    
    async def compare_entities(self, new_entities: List[Dict], existing_entities: List[Dict], 
                             document_type: str) -> List[EntityComparison]:
        """
        Compare new entities with existing database content.
        
        Args:
            new_entities: Entities extracted from new document
            existing_entities: Entities currently in database
            document_type: Type of document being processed
            
        Returns:
            List of EntityComparison objects with merge actions
        """
        await self.activate()
        
        try:
            logger.info(f"🔍 Comparing {len(new_entities)} new entities with {len(existing_entities)} existing")
            
            # Generate comparison using specialized prompt
            prompt = self.comparison_prompt.format(
                new_entities=json.dumps(new_entities[:20]),  # Limit for 3b model
                existing_entities=json.dumps(existing_entities[:20]),
                document_type=document_type
            )
            
            response = await self._llm.ainvoke(prompt)
            
            # Parse JSON response
            try:
                comparison_data = json.loads(response.strip())
                comparisons = []
                
                for comp in comparison_data.get("comparisons", []):
                    comparisons.append(EntityComparison(
                        entity_id=comp.get("entity_id", ""),
                        action=comp.get("action", "ADD"),
                        new_data=comp.get("new_data"),
                        old_data=comp.get("old_data"),
                        changes=comp.get("changes", []),
                        confidence=comp.get("confidence", 0.0)
                    ))
                
                return comparisons
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Comparison JSON parsing failed: {e}")
                return self._fallback_comparison(new_entities, existing_entities)
                
        except Exception as e:
            logger.error(f"❌ Entity comparison failed: {e}")
            return self._fallback_comparison(new_entities, existing_entities)
    
    def _fallback_comparison(self, new_entities: List[Dict], 
                           existing_entities: List[Dict]) -> List[EntityComparison]:
        """Fallback comparison when LLM processing fails."""
        logger.info("🔄 Using fallback entity comparison")
        
        # Simple comparison - mark all new entities as ADD
        comparisons = []
        for i, entity in enumerate(new_entities):
            comparisons.append(EntityComparison(
                entity_id=f"entity_{i}",
                action="ADD",
                new_data=entity,
                old_data=None,
                changes=["New entity"],
                confidence=0.5
            ))
        
        return comparisons
    
    async def create_merge_plan(self, document_source: str, 
                              comparisons: List[EntityComparison]) -> MergePlan:
        """
        Create a comprehensive merge plan based on entity comparisons.
        
        Args:
            document_source: Source document filename
            comparisons: List of entity comparisons
            
        Returns:
            MergePlan with detailed merge strategy
        """
        logger.info(f"📋 Creating merge plan for {len(comparisons)} entities")
        
        # Analyze actions
        actions_count = {}
        for comp in comparisons:
            actions_count[comp.action] = actions_count.get(comp.action, 0) + 1
        
        # Generate summary
        summary_parts = []
        for action, count in actions_count.items():
            if count > 0:
                summary_parts.append(f"{count} {action.lower()}")
        
        summary = f"Processing {document_source}: " + ", ".join(summary_parts)
        
        # Identify warnings
        warnings = []
        low_confidence = [c for c in comparisons if c.confidence < 0.7]
        if low_confidence:
            warnings.append(f"{len(low_confidence)} entities have low confidence scores")
        
        # Estimate processing time (rough estimate)
        estimated_time = len(comparisons) * 0.1  # 0.1 seconds per entity
        
        return MergePlan(
            document_source=document_source,
            total_entities=len(comparisons),
            actions=comparisons,
            summary=summary,
            warnings=warnings,
            estimated_processing_time=estimated_time
        )
    
    async def process_document_upload(self, content: str, filename: str, 
                                    existing_data: Optional[List[Dict]] = None) -> MergePlan:
        """
        Complete document processing workflow.
        
        This is the main entry point for document uploads.
        
        Args:
            content: Raw document content
            filename: Source filename
            existing_data: Existing entities in database (optional)
            
        Returns:
            MergePlan ready for execution
        """
        try:
            logger.info(f"🚀 Starting intelligent document processing: {filename}")
            
            # Step 1: Analyze document structure
            analysis = await self.analyze_document(content, filename)
            logger.info(f"📊 Document analysis complete: {analysis.document_type} with {len(analysis.entities)} entities")
            
            # Step 2: Compare with existing data
            existing_data = existing_data or []
            comparisons = await self.compare_entities(analysis.entities, existing_data, analysis.document_type)
            logger.info(f"🔍 Entity comparison complete: {len(comparisons)} comparisons generated")
            
            # Step 3: Create merge plan
            merge_plan = await self.create_merge_plan(filename, comparisons)
            logger.info(f"📋 Merge plan created: {merge_plan.summary}")
            
            return merge_plan
            
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            raise
        finally:
            # Always deactivate to free resources
            await self.deactivate()


# Global instance (lazy initialization)
_database_agent = None

def get_database_agent(config):
    """Get or create the global Database Agent instance."""
    global _database_agent
    if _database_agent is None:
        _database_agent = DatabaseAgent(config)
    return _database_agent
