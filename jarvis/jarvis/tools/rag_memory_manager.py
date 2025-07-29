import os
import logging
from pathlib import Path
from typing import List, Optional
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.tools.retriever import create_retriever_tool

# Import document loaders for the file types you want to support
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader

logger = logging.getLogger(__name__)

class RAGMemoryManager:
    """
    Manages the ChromaDB-based RAG system for long-term conversational memory and
    document-based knowledge with proper configuration integration.
    """

    def __init__(self, config):
        """
        Initializes the RAG Memory Manager with configuration.

        Args:
            config: Configuration object containing RAG and LLM settings.
        """
        self.config = config
        self.embeddings = OllamaEmbeddings(model=self.config.llm.model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.rag.chunk_size,
            chunk_overlap=self.config.rag.chunk_overlap
        )

        # Ensure vector store directory exists
        vector_store_path = Path(self.config.rag.vector_store_path)
        vector_store_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB vector store
        self.vector_store = Chroma(
            persist_directory=str(vector_store_path),
            embedding_function=self.embeddings,
            collection_name=self.config.rag.collection_name
        )

        logger.info(f"RAGMemoryManager initialized with ChromaDB at {vector_store_path}")

    def add_conversational_memory(self, fact: str):
        """Adds a single piece of text (a memory) to the ChromaDB vector store."""
        try:
            document = Document(page_content=fact)
            self.vector_store.add_documents([document])
            logger.info(f"Successfully added conversational memory: '{fact[:50]}...'")
        except Exception as e:
            logger.error(f"Failed to add conversational memory: {e}")

    def ingest_documents_from_folder(self, documents_path: Optional[str] = None, force_reingest: bool = False):
        """
        Loads and processes all supported files from the configured documents folder.

        Args:
            documents_path: Path to documents folder (uses config default if None)
            force_reingest: If True, re-processes all documents even if already ingested

        Returns:
            dict: Summary of ingestion results with counts and any errors
        """
        if documents_path is None:
            documents_path = self.config.rag.documents_path

        documents_dir = Path(documents_path)
        if not documents_dir.exists():
            logger.warning(f"Documents directory does not exist: {documents_path}")
            documents_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created documents directory: {documents_path}")
            return {"status": "created_directory", "processed": 0, "errors": []}

        # Track ingestion results
        results = {
            "status": "success",
            "processed": 0,
            "skipped": 0,
            "errors": [],
            "files_processed": []
        }

        supported_extensions = {".pdf", ".txt", ".doc", ".docx"}

        try:
            # Get all supported files
            all_files = [f for f in documents_dir.iterdir()
                        if f.is_file() and f.suffix.lower() in supported_extensions]

            if not all_files:
                logger.info(f"No supported documents found in {documents_path}")
                results["status"] = "no_files"
                return results

            logger.info(f"Found {len(all_files)} supported documents to process")

            for file_path in all_files:
                try:
                    filename = file_path.name
                    file_extension = file_path.suffix.lower()

                    # Choose appropriate loader
                    loader = None
                    if file_extension == ".pdf":
                        loader = PyPDFLoader(str(file_path))
                    elif file_extension == ".txt":
                        loader = TextLoader(str(file_path), encoding='utf-8')
                    elif file_extension in [".doc", ".docx"]:
                        loader = UnstructuredWordDocumentLoader(str(file_path))

                    if loader:
                        logger.info(f"Processing document: {filename}")

                        # Load and process document
                        documents = loader.load()

                        if not documents:
                            logger.warning(f"No content extracted from {filename}")
                            results["errors"].append(f"No content: {filename}")
                            continue

                        # Add comprehensive metadata
                        for doc in documents:
                            doc.metadata.update({
                                "source": filename,
                                "source_type": "document",
                                "file_extension": file_extension,
                                "ingestion_timestamp": str(Path(file_path).stat().st_mtime)
                            })

                        # Split into chunks
                        chunks = self.text_splitter.split_documents(documents)

                        if chunks:
                            # Add to vector store
                            self.vector_store.add_documents(chunks)
                            results["processed"] += 1
                            results["files_processed"].append(filename)
                            logger.info(f"Successfully ingested {filename} ({len(chunks)} chunks)")
                        else:
                            logger.warning(f"No chunks created from {filename}")
                            results["errors"].append(f"No chunks: {filename}")

                except Exception as file_error:
                    error_msg = f"Error processing {file_path.name}: {str(file_error)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            # Final summary
            if results["processed"] > 0:
                logger.info(f"Document ingestion complete: {results['processed']} files processed successfully")
            if results["errors"]:
                logger.warning(f"Ingestion completed with {len(results['errors'])} errors")

        except Exception as e:
            error_msg = f"Failed during document ingestion: {e}"
            logger.error(error_msg)
            results["status"] = "failed"
            results["errors"].append(error_msg)

        return results

    def get_ingested_documents(self):
        """
        Get a list of all documents that have been ingested into the vector store.

        Returns:
            list: List of unique document sources with metadata
        """
        try:
            # Use similarity search with empty query to get all documents
            all_docs = self.vector_store.similarity_search("", k=1000)

            # Extract unique sources
            sources = {}
            for doc in all_docs:
                source = doc.metadata.get('source', 'unknown')
                source_type = doc.metadata.get('source_type', 'unknown')

                if source not in sources:
                    sources[source] = {
                        'source': source,
                        'source_type': source_type,
                        'chunk_count': 0,
                        'file_extension': doc.metadata.get('file_extension', ''),
                        'ingestion_timestamp': doc.metadata.get('ingestion_timestamp', '')
                    }
                sources[source]['chunk_count'] += 1

            return list(sources.values())

        except Exception as e:
            logger.error(f"Error getting ingested documents: {e}")
            return []

    def get_document_stats(self):
        """
        Get statistics about the current document collection.

        Returns:
            dict: Statistics about ingested documents and memory usage
        """
        try:
            ingested_docs = self.get_ingested_documents()

            # Count by type
            doc_types = {}
            total_chunks = 0

            for doc_info in ingested_docs:
                source_type = doc_info['source_type']
                doc_types[source_type] = doc_types.get(source_type, 0) + 1
                total_chunks += doc_info['chunk_count']

            return {
                'total_documents': len(ingested_docs),
                'total_chunks': total_chunks,
                'document_types': doc_types,
                'documents': ingested_docs
            }

        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {'total_documents': 0, 'total_chunks': 0, 'document_types': {}, 'documents': []}

    def get_retriever_tool(self):
        """Creates a LangChain tool that allows the agent to search the ChromaDB vector store."""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": self.config.rag.search_k})
        return create_retriever_tool(
            retriever,
            "search_long_term_memory",
            "Searches PERMANENT, LONG-TERM memory for facts the user explicitly told you to remember in previous conversations. Use this when user asks about remembered facts, preferences, or information from past sessions."
        )
