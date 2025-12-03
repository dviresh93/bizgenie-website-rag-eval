"""
Semantic Cache Manager for MCP Search Results

Implements two-tier hybrid caching:
- Tier 1: Exact match via metadata filtering (10-20ms)
- Tier 2: Semantic match via vector similarity (30-50ms)
"""

import hashlib
import json
import os
import time
from typing import Dict, List, Optional, Tuple

import chromadb
from openai import OpenAI


class SemanticCacheManager:
    """
    Manages semantic caching of search results using ChromaDB.

    Features:
    - Exact match caching via metadata filtering
    - Semantic similarity matching via vector embeddings
    - Configurable similarity threshold
    - Cache statistics tracking
    """

    def __init__(
        self,
        chroma_host: str = "chromadb",
        chroma_port: int = 8000,
        embedding_model: str = "text-embedding-3-small",
        semantic_threshold: float = 0.90
    ):
        """
        Initialize the Semantic Cache Manager.

        Args:
            chroma_host: ChromaDB server hostname (default: "chromadb" for Docker)
            chroma_port: ChromaDB server port (default: 8000)
            embedding_model: OpenAI embedding model to use
            semantic_threshold: Minimum similarity score for semantic matches (0.0-1.0)
        """
        # Connect to existing ChromaDB instance
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

        # Get or create cache collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="search_cache",
            metadata={"description": "Semantic cache for MCP search results"}
        )

        # Initialize OpenAI client for embeddings
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.embedding_model = embedding_model

        # Configuration
        self.semantic_threshold = semantic_threshold

        # Statistics
        self.stats = {
            "exact_hits": 0,
            "semantic_hits": 0,
            "misses": 0,
            "total_queries": 0,
            "total_saved_time": 0.0,
            "total_exact_time": 0.0,
            "total_semantic_time": 0.0
        }

    def _generate_cache_key(self, tool: str, question: str, context: str = "") -> str:
        """Generate a deterministic cache key from inputs."""
        combined = f"{tool}|{question}|{context}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Warning: Embedding generation failed: {e}")
            return None

    def get_cached_search(
        self,
        tool: str,
        question: str,
        context: str = ""
    ) -> Tuple[Optional[Dict], str, float]:
        """
        Retrieve cached search result if available.

        Args:
            tool: MCP tool name (jina, tavily, firecrawl, exa)
            question: User question
            context: Additional context (optional)

        Returns:
            Tuple of (cached_result, cache_status, retrieval_time)
            - cached_result: Dict with search results or None if not found
            - cache_status: "exact_hit", "semantic_hit", or "miss"
            - retrieval_time: Time taken to check cache in seconds
        """
        start_time = time.time()
        self.stats["total_queries"] += 1

        cache_key = self._generate_cache_key(tool, question, context)

        # TIER 1: Exact match via metadata filtering
        try:
            exact_results = self.collection.get(
                ids=[cache_key],
                include=["documents", "metadatas"]
            )

            if exact_results and exact_results["ids"]:
                # Exact match found
                cached_data = json.loads(exact_results["documents"][0])
                retrieval_time = time.time() - start_time

                self.stats["exact_hits"] += 1
                self.stats["total_exact_time"] += retrieval_time

                return cached_data, "exact_hit", retrieval_time
        except Exception as e:
            print(f"Warning: Exact match lookup failed: {e}")

        # TIER 2: Semantic match via vector similarity
        query_embedding = self._generate_embedding(question)

        if query_embedding is None:
            # Embedding failed, return miss
            retrieval_time = time.time() - start_time
            self.stats["misses"] += 1
            return None, "miss", retrieval_time

        try:
            semantic_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1,
                where={"tool": tool},  # Filter by same tool
                include=["documents", "metadatas", "distances"]
            )

            if (semantic_results and
                semantic_results["ids"] and
                len(semantic_results["ids"][0]) > 0):

                # Convert distance to similarity (ChromaDB uses L2 distance)
                # Similarity = 1 / (1 + distance)
                distance = semantic_results["distances"][0][0]
                similarity = 1.0 / (1.0 + distance)

                if similarity >= self.semantic_threshold:
                    # Semantic match found
                    cached_data = json.loads(semantic_results["documents"][0][0])
                    retrieval_time = time.time() - start_time

                    self.stats["semantic_hits"] += 1
                    self.stats["total_semantic_time"] += retrieval_time

                    # Add similarity score to metadata
                    cached_data["_cache_similarity"] = similarity

                    return cached_data, "semantic_hit", retrieval_time
        except Exception as e:
            print(f"Warning: Semantic match lookup failed: {e}")

        # TIER 3: Cache miss
        retrieval_time = time.time() - start_time
        self.stats["misses"] += 1

        return None, "miss", retrieval_time

    def store_search_result(
        self,
        tool: str,
        question: str,
        context: str,
        search_result: Dict,
        search_time: float
    ) -> bool:
        """
        Store search result in cache.

        Args:
            tool: MCP tool name
            question: User question
            context: Additional context
            search_result: Search result data to cache
            search_time: Original search time (for statistics)

        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(tool, question, context)
            query_embedding = self._generate_embedding(question)

            if query_embedding is None:
                return False

            # Prepare metadata
            metadata = {
                "tool": tool,
                "question": question[:500],  # Truncate for metadata
                "context": context[:500] if context else "",
                "cached_at": time.time(),
                "original_search_time": search_time
            }

            # Store in ChromaDB
            self.collection.upsert(
                ids=[cache_key],
                documents=[json.dumps(search_result)],
                embeddings=[query_embedding],
                metadatas=[metadata]
            )

            return True

        except Exception as e:
            print(f"Warning: Failed to store cache entry: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get cache performance statistics."""
        total_hits = self.stats["exact_hits"] + self.stats["semantic_hits"]
        hit_rate = (total_hits / self.stats["total_queries"] * 100
                   if self.stats["total_queries"] > 0 else 0)

        avg_exact_time = (self.stats["total_exact_time"] / self.stats["exact_hits"]
                         if self.stats["exact_hits"] > 0 else 0)
        avg_semantic_time = (self.stats["total_semantic_time"] / self.stats["semantic_hits"]
                            if self.stats["semantic_hits"] > 0 else 0)

        return {
            "total_queries": self.stats["total_queries"],
            "exact_hits": self.stats["exact_hits"],
            "semantic_hits": self.stats["semantic_hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "avg_exact_retrieval_time": avg_exact_time,
            "avg_semantic_retrieval_time": avg_semantic_time,
            "total_saved_time": self.stats["total_saved_time"]
        }

    def reset_stats(self):
        """Reset cache statistics."""
        self.stats = {
            "exact_hits": 0,
            "semantic_hits": 0,
            "misses": 0,
            "total_queries": 0,
            "total_saved_time": 0.0,
            "total_exact_time": 0.0,
            "total_semantic_time": 0.0
        }

    def clear_cache(self):
        """Clear all cached entries."""
        try:
            # Delete and recreate collection
            self.chroma_client.delete_collection("search_cache")
            self.collection = self.chroma_client.get_or_create_collection(
                name="search_cache",
                metadata={"description": "Semantic cache for MCP search results"}
            )
            return True
        except Exception as e:
            print(f"Error: Failed to clear cache: {e}")
            return False
