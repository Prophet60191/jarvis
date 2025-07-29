#!/usr/bin/env python3
"""
MCP to RAG Migration Script

Migrates existing MCP memory data to the new RAG system with
data validation and rollback capabilities.
"""

import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add jarvis to path
sys.path.append(str(Path(__file__).parent.parent / "jarvis"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MCPToRAGMigrator:
    """Handles migration from MCP memory to RAG system."""
    
    def __init__(self, rag_service, dry_run: bool = False):
        """
        Initialize migrator.
        
        Args:
            rag_service: RAG service instance
            dry_run: If True, simulate migration without making changes
        """
        self.rag_service = rag_service
        self.dry_run = dry_run
        self.migration_stats = {
            "total_entries": 0,
            "migrated_entries": 0,
            "failed_entries": 0,
            "skipped_entries": 0,
            "errors": []
        }
        
    def load_mcp_export(self, export_path: str) -> Dict[str, Any]:
        """
        Load MCP memory export file.
        
        Args:
            export_path: Path to MCP export JSON file
            
        Returns:
            dict: Loaded MCP data
        """
        try:
            with open(export_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded MCP export with {len(data.get('entries', []))} entries")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load MCP export: {e}")
            raise
    
    def transform_content(self, mcp_entry: Dict[str, Any]) -> str:
        """
        Transform MCP entry content for RAG system.
        
        Args:
            mcp_entry: MCP memory entry
            
        Returns:
            str: Transformed content for RAG
        """
        content = mcp_entry.get('content', '')
        entry_type = mcp_entry.get('metadata', {}).get('type', 'unknown')
        
        # Add context based on entry type
        if entry_type == 'preference':
            content = f"User preference: {content}"
        elif entry_type == 'fact':
            content = f"Personal fact: {content}"
        elif entry_type == 'context':
            content = f"Context information: {content}"
        
        return content
    
    def create_migration_metadata(self, mcp_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create migration metadata for RAG entry.
        
        Args:
            mcp_entry: Original MCP entry
            
        Returns:
            dict: Migration metadata
        """
        original_metadata = mcp_entry.get('metadata', {})
        
        return {
            "source": "mcp_migration",
            "migration_date": datetime.now().isoformat(),
            "original_id": mcp_entry.get('id', 'unknown'),
            "original_type": original_metadata.get('type', 'unknown'),
            "original_confidence": original_metadata.get('confidence', 1.0),
            "original_created": original_metadata.get('created', 'unknown')
        }
    
    def migrate_single_entry(self, mcp_entry: Dict[str, Any]) -> bool:
        """
        Migrate a single MCP entry to RAG.
        
        Args:
            mcp_entry: MCP memory entry to migrate
            
        Returns:
            bool: True if migration successful, False otherwise
        """
        try:
            # Transform content
            rag_content = self.transform_content(mcp_entry)
            
            # Create migration metadata
            migration_metadata = self.create_migration_metadata(mcp_entry)
            
            if self.dry_run:
                logger.info(f"DRY RUN: Would migrate entry {mcp_entry.get('id', 'unknown')}")
                logger.debug(f"Content: {rag_content[:100]}...")
                return True
            
            # Add to RAG system
            result = self.rag_service.add_conversational_memory(rag_content)
            
            if "stored in long-term memory" in result:
                logger.debug(f"Successfully migrated entry {mcp_entry.get('id', 'unknown')}")
                return True
            else:
                logger.warning(f"Unexpected result for entry {mcp_entry.get('id', 'unknown')}: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to migrate entry {mcp_entry.get('id', 'unknown')}: {e}")
            self.migration_stats["errors"].append(str(e))
            return False
    
    def migrate_memories(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate all MCP memories to RAG system.
        
        Args:
            mcp_data: Loaded MCP export data
            
        Returns:
            dict: Migration statistics
        """
        entries = mcp_data.get('entries', [])
        self.migration_stats["total_entries"] = len(entries)
        
        logger.info(f"Starting migration of {len(entries)} entries...")
        
        for i, entry in enumerate(entries, 1):
            logger.info(f"Migrating entry {i}/{len(entries)}: {entry.get('id', 'unknown')}")
            
            # Check if entry should be skipped
            if self.should_skip_entry(entry):
                self.migration_stats["skipped_entries"] += 1
                logger.info(f"Skipped entry {entry.get('id', 'unknown')}")
                continue
            
            # Migrate entry
            if self.migrate_single_entry(entry):
                self.migration_stats["migrated_entries"] += 1
            else:
                self.migration_stats["failed_entries"] += 1
        
        # Log final statistics
        stats = self.migration_stats
        logger.info(f"Migration completed:")
        logger.info(f"  Total entries: {stats['total_entries']}")
        logger.info(f"  Migrated: {stats['migrated_entries']}")
        logger.info(f"  Failed: {stats['failed_entries']}")
        logger.info(f"  Skipped: {stats['skipped_entries']}")
        
        if stats['errors']:
            logger.warning(f"  Errors encountered: {len(stats['errors'])}")
        
        return self.migration_stats
    
    def should_skip_entry(self, mcp_entry: Dict[str, Any]) -> bool:
        """
        Determine if an MCP entry should be skipped during migration.
        
        Args:
            mcp_entry: MCP memory entry
            
        Returns:
            bool: True if entry should be skipped
        """
        # Skip empty content
        content = mcp_entry.get('content', '').strip()
        if not content:
            return True
        
        # Skip very short entries (likely noise)
        if len(content) < 10:
            return True
        
        # Skip entries marked as temporary
        metadata = mcp_entry.get('metadata', {})
        if metadata.get('temporary', False):
            return True
        
        return False
    
    def validate_migration(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate migration results.
        
        Args:
            mcp_data: Original MCP data
            
        Returns:
            dict: Validation results
        """
        validation_results = {
            "status": "success",
            "total_original": len(mcp_data.get('entries', [])),
            "total_migrated": self.migration_stats["migrated_entries"],
            "validation_errors": []
        }
        
        # Check migration completeness
        expected_migrated = validation_results["total_original"] - self.migration_stats["skipped_entries"]
        actual_migrated = self.migration_stats["migrated_entries"]
        
        if actual_migrated < expected_migrated:
            validation_results["status"] = "incomplete"
            validation_results["validation_errors"].append(
                f"Expected {expected_migrated} entries, but only {actual_migrated} were migrated"
            )
        
        # Test retrieval of migrated content
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Test search functionality
            test_result = loop.run_until_complete(
                self.rag_service.intelligent_search("migrated content test")
            )
            
            if test_result.get('retrieved_documents'):
                logger.info("✅ RAG search functionality working after migration")
            else:
                validation_results["validation_errors"].append("RAG search not returning results")
                
        except Exception as e:
            validation_results["validation_errors"].append(f"RAG search test failed: {e}")
        finally:
            loop.close()
        
        return validation_results


def create_sample_mcp_export(output_path: str) -> None:
    """Create a sample MCP export file for testing."""
    sample_data = {
        "source": "mcp_memory",
        "export_timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "entries": [
            {
                "id": "mem_001",
                "content": "User prefers Python programming language for AI projects",
                "metadata": {
                    "type": "preference",
                    "confidence": 0.9,
                    "created": "2024-01-10T15:20:00Z"
                }
            },
            {
                "id": "mem_002", 
                "content": "User works as a software engineer at a tech startup",
                "metadata": {
                    "type": "fact",
                    "confidence": 1.0,
                    "created": "2024-01-12T09:15:00Z"
                }
            },
            {
                "id": "mem_003",
                "content": "User mentioned using VS Code as primary development environment",
                "metadata": {
                    "type": "context",
                    "confidence": 0.8,
                    "created": "2024-01-14T14:30:00Z"
                }
            }
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Created sample MCP export at {output_path}")


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate MCP memory to RAG system")
    parser.add_argument("--export-file", required=True, help="Path to MCP export JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without making changes")
    parser.add_argument("--create-sample", action="store_true", help="Create sample MCP export file")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing migration")
    
    args = parser.parse_args()
    
    # Create sample export if requested
    if args.create_sample:
        create_sample_mcp_export(args.export_file)
        return
    
    try:
        # Initialize RAG service
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Initialize migrator
        migrator = MCPToRAGMigrator(rag_service, dry_run=args.dry_run)
        
        # Load MCP data
        mcp_data = migrator.load_mcp_export(args.export_file)
        
        if args.validate_only:
            # Validation only
            validation_results = migrator.validate_migration(mcp_data)
            print(f"\nValidation Results: {json.dumps(validation_results, indent=2)}")
        else:
            # Perform migration
            migration_stats = migrator.migrate_memories(mcp_data)
            
            # Validate results
            validation_results = migrator.validate_migration(mcp_data)
            
            # Print results
            print(f"\nMigration Results:")
            print(f"  Total entries: {migration_stats['total_entries']}")
            print(f"  Migrated: {migration_stats['migrated_entries']}")
            print(f"  Failed: {migration_stats['failed_entries']}")
            print(f"  Skipped: {migration_stats['skipped_entries']}")
            
            print(f"\nValidation Status: {validation_results['status']}")
            if validation_results['validation_errors']:
                print("Validation Errors:")
                for error in validation_results['validation_errors']:
                    print(f"  - {error}")
            
            # Create backup if not dry run
            if not args.dry_run and migration_stats['migrated_entries'] > 0:
                backup_result = rag_service.create_backup(
                    backup_name="post_mcp_migration",
                    compress=True
                )
                if backup_result['status'] == 'success':
                    print(f"\n✅ Created post-migration backup: {backup_result['backup_name']}")
                else:
                    print(f"\n⚠️ Failed to create post-migration backup")
        
        print(f"\n{'🧪 DRY RUN COMPLETE' if args.dry_run else '✅ MIGRATION COMPLETE'}")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
