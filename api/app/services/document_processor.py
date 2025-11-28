"""
Document processing service.
Handles chunking, embedding, and storage of documents.
"""
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import tiktoken
from api.app.plugins.base import StandardDocument
from api.app.core.logging import get_logger

logger = get_logger("document_processor")

class DocumentProcessor:
    """Processes and stores documents in ChromaDB"""

    def __init__(self, config: Dict):
        """
        Initialize document processor.

        Args:
            config: Processing configuration from configs.yaml
        """
        self.config = config

        # Initialize ChromaDB client
        chroma_config = config.get("storage", {})
        
        import os
        host = os.getenv("CHROMA_HOST", chroma_config.get("host", "localhost"))
        port = int(os.getenv("CHROMA_PORT", chroma_config.get("port", 8001)))
        
        logger.info(f"Connecting to ChromaDB at {host}:{port}")
        self.chroma_client = chromadb.HttpClient(
            host=host,
            port=port
        )

        # Initialize OpenAI for embeddings
        embedding_config = config.get("embedding", {})
        self.openai_client = OpenAI(api_key=embedding_config.get("api_key"))
        self.embedding_model = embedding_config.get("model", "text-embedding-3-small")

        # Chunking config
        chunking_config = config.get("chunking", {})
        self.chunk_size = chunking_config.get("chunk_size", 500)
        self.chunk_overlap = chunking_config.get("chunk_overlap", 50)

        # Initialize tokenizer
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks based on token count.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        tokens = self.tokenizer.encode(text)
        chunks = []

        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)

        return chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks.

        Args:
            texts: List of text chunks

        Returns:
            List of embedding vectors
        """
        logger.debug(f"Generating embeddings for {len(texts)} chunks using {self.embedding_model}")
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )

        return [item.embedding for item in response.data]

    def process_and_store(
        self,
        documents: List[StandardDocument],
        collection_name: str = "website_content"
    ) -> Dict:
        """
        Process documents and store in ChromaDB.

        Args:
            documents: List of StandardDocuments
            collection_name: Name of ChromaDB collection

        Returns:
            Statistics about the processing
        """
        # Get or create collection
        collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Website content for RAG"}
        )

        total_chunks = 0

        for doc in documents:
            # Chunk the document
            chunks = self.chunk_text(doc.content)

            if not chunks:
                continue

            logger.info(f"Generated {len(chunks)} chunks for document: {doc.url}")

            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)

            # Prepare metadata
            metadatas = [
                {
                    "url": doc.url,
                    "source_plugin": doc.source_plugin,
                    "timestamp": doc.timestamp,
                    "chunk_index": i,
                    **doc.metadata
                }
                for i in range(len(chunks))
            ]

            # Generate IDs
            ids = [f"{doc.url}_{i}" for i in range(len(chunks))]

            # Store in ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )

            total_chunks += len(chunks)

        return {
            "documents_processed": len(documents),
            "total_chunks": total_chunks,
            "collection_name": collection_name
        }

    def retrieve(
        self,
        query: str,
        collection_name: str = "website_content",
        n_results: int = 5
    ) -> Dict:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            collection_name: ChromaDB collection to search
            n_results: Number of results to return

        Returns:
            Dict with results
        """
        collection = self.chroma_client.get_collection(name=collection_name)

        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]

        # Search
        logger.info(f"Querying ChromaDB collection '{collection_name}' with query: '{query}'")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0]
        }
