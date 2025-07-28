import os
import logging
from pathlib import Path
from typing import List, Optional
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

    def ingest_documents_from_folder(self, documents_path: Optional[str] = None):
        """Loads and processes all supported files from the configured documents folder."""
        if documents_path is None:
            documents_path = self.config.rag.documents_path

        documents_dir = Path(documents_path)
        if not documents_dir.exists():
            logger.warning(f"Documents directory does not exist: {documents_path}")
            return

        try:
            for file_path in documents_dir.iterdir():
                if file_path.is_file():
                    loader = None
                    filename = file_path.name

                    # Choose a loader based on the file extension
                    if filename.lower().endswith(".pdf"):
                        loader = PyPDFLoader(str(file_path))
                    elif filename.lower().endswith(".txt"):
                        loader = TextLoader(str(file_path))
                    elif filename.lower().endswith((".doc", ".docx")):
                        loader = UnstructuredWordDocumentLoader(str(file_path))

                    if loader:
                        logger.info(f"Ingesting document: {filename}")
                        documents = loader.load()
                        # Add source metadata for better tracking
                        for doc in documents:
                            doc.metadata["source"] = filename
                        chunks = self.text_splitter.split_documents(documents)
                        self.vector_store.add_documents(chunks)

            logger.info(f"Document ingestion from '{documents_path}' complete.")
        except Exception as e:
            logger.error(f"Failed during document ingestion: {e}")

    def get_retriever_tool(self):
        """Creates a LangChain tool that allows the agent to search the ChromaDB vector store."""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": self.config.rag.search_k})
        return create_retriever_tool(
            retriever,
            "search_long_term_memory",
            "Searches PERMANENT, LONG-TERM memory for facts the user explicitly told you to remember in previous conversations. Use this when user asks about remembered facts, preferences, or information from past sessions."
        )
