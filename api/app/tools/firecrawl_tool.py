"""Firecrawl MCP Tool Implementation

Firecrawl is an advanced web scraping service that:
- Handles JavaScript-heavy websites better than basic scrapers
- Converts web content to clean, LLM-optimized markdown
- Provides structured metadata about scraped content
- Similar architecture to Jina but with better quality output

Official Docs: https://docs.firecrawl.dev/sdks/python
"""

import os
import time
from typing import Optional
from firecrawl import FirecrawlApp
from api.app.tools.base import MCPTool, SearchResult
from api.app.core.logging import get_logger

logger = get_logger("firecrawl_tool")


class FirecrawlTool(MCPTool):
    """Firecrawl Advanced Web Scraper MCP tool

    This tool scrapes web pages using Firecrawl's API and converts them to
    clean markdown suitable for LLM processing.

    Key Features:
    - JavaScript rendering (handles dynamic content)
    - Clean markdown conversion
    - Structured metadata extraction
    - Better quality than basic HTTP scrapers

    Limitations:
    - Requires direct URL (cannot perform web search)
    - Requires valid API key
    - Paid service (~$0.004 per scrape)
    """

    def __init__(self, config: dict):
        """Initialize Firecrawl tool

        Args:
            config: Dictionary with configuration:
                - api_key_env: Name of environment variable containing API key
                             (default: "FIRECRAWL_API_KEY")

        Raises:
            ValueError: If API key is not found in environment
        """
        super().__init__(config)

        # Get API key from environment
        api_key_env = config.get("api_key_env", "FIRECRAWL_API_KEY")
        self.api_key = os.environ.get(api_key_env)

        if not self.api_key:
            raise ValueError(
                f"Firecrawl API key not found. "
                f"Please set {api_key_env} environment variable. "
                f"Get your key at: https://firecrawl.dev"
            )

        # Initialize Firecrawl client
        try:
            self.client = FirecrawlApp(api_key=self.api_key)
            logger.info("Firecrawl client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firecrawl client: {e}")
            raise

    def search(self, question: str, context: str = None) -> SearchResult:
        """Scrape content using Firecrawl

        Args:
            question: The question being asked (used for logging, not search)
            context: URL to scrape (REQUIRED - Firecrawl is a scraper, not search)

        Returns:
            SearchResult containing:
                - content: Markdown-formatted page content
                - sources: List with single URL that was scraped
                - metadata: Tool info and scrape statistics
                - search_time: Time taken to scrape in seconds
                - search_cost: Estimated cost of the scrape operation

        Raises:
            ValueError: If context URL is not provided or invalid
            Exception: If scraping fails
        """
        start_time = time.time()

        # Validate that context URL is provided
        if not context:
            raise ValueError(
                "Firecrawl requires a URL context. "
                "Please provide a URL to scrape in the 'context' parameter."
            )

        if not context.startswith("http"):
            raise ValueError(
                f"Invalid URL context: '{context}'. "
                f"URL must start with 'http://' or 'https://'"
            )

        logger.info(f"Scraping URL with Firecrawl: {context}")
        logger.info(f"Question context: {question}")

        try:
            # Scrape the URL with markdown format
            # Updated to use direct kwargs for SDK > 0.0.16
            result = self.client.scrape(
                url=context,
                formats=['markdown']
            )

            # Extract markdown content (access as attribute for Pydantic model)
            content = getattr(result, 'markdown', '') or ''

            if not content:
                logger.warning(f"Firecrawl returned empty content for {context}")
                content = "No content was retrieved from the URL."

            # Firecrawl scrapes a single URL, so sources is just that URL
            sources = [context]

            # Log success
            content_length = len(content)
            logger.info(
                f"Firecrawl scrape successful. "
                f"Content length: {content_length} characters"
            )

            # Build metadata
            metadata = {
                "tool": "firecrawl",
                "url": context,
                "content_length": content_length,
                "success": True
            }

            # Add any additional metadata from Firecrawl response
            if hasattr(result, 'metadata') and result.metadata:
                # Convert Pydantic model to dict if needed, or access directly
                try:
                    metadata['firecrawl_metadata'] = result.metadata if isinstance(result.metadata, dict) else result.metadata.model_dump()
                except:
                    metadata['firecrawl_metadata'] = str(result.metadata)

        except Exception as e:
            logger.error(f"Firecrawl scrape failed for {context}: {e}")
            # Re-raise with more context
            raise Exception(f"Firecrawl scraping error: {str(e)}") from e

        # Calculate time taken
        search_time = time.time() - start_time
        logger.info(f"Scrape completed in {search_time:.2f} seconds")

        # Return structured result
        return SearchResult(
            content=content,
            sources=sources,
            metadata=metadata,
            search_time=search_time,
            search_cost=0.004  # Estimated cost per scrape
        )

    def get_info(self) -> dict:
        """Get information about this tool

        Returns:
            Dictionary with tool metadata for reporting and analysis
        """
        return {
            "name": "Firecrawl",
            "type": "web_scraper",
            "cost_per_search": 0.004,
            "capabilities": [
                "scrape",
                "javascript_rendering",
                "markdown_conversion",
                "metadata_extraction"
            ],
            "limitations": [
                "requires_url",
                "no_search_capability",
                "paid_service"
            ],
            "api_docs": "https://docs.firecrawl.dev/sdks/python"
        }
