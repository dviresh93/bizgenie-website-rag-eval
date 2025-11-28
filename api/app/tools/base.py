from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SearchResult:
    """Result from MCP tool search"""
    content: str              # Relevant content found
    sources: List[str]        # Source URLs
    metadata: dict            # Tool-specific metadata
    search_time: float        # Time taken (seconds)
    search_cost: float        # Cost of search

class MCPTool(ABC):
    """Base class for all MCP tools (Jina, Tavily, etc.)"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def search(self, question: str, context: Optional[str] = None) -> SearchResult:
        """
        Perform real-time search based on question.

        Args:
            question: User's question
            context: Optional context (e.g., "bizgenieai.com" to focus search)

        Returns:
            SearchResult with content, sources, and metrics
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """
        Return tool metadata.

        Returns:
            {
                "name": "Tool Name",
                "cost_per_search": 0.01,
                "capabilities": ["search", "crawl"]
            }
        """
        pass
