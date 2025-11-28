import os
import time
from urllib.parse import urlparse
from tavily import TavilyClient
from api.app.tools.base import MCPTool, SearchResult
from api.app.core.logging import get_logger

logger = get_logger("tavily_tool")

class TavilyTool(MCPTool):
    """Tavily AI Search MCP tool"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = os.environ.get(config.get("api_key_env", "TAVILY_API_KEY"))
        if not self.api_key:
            raise ValueError("Tavily API key is required")
        self.client = TavilyClient(api_key=self.api_key)
        self.options = config.get("config", {})

    def search(self, question: str, context: str = None) -> SearchResult:
        """
        Search using Tavily API.
        If context (URL) is provided, restricts search to that domain.
        """
        start_time = time.time()
        
        query = question
        include_domains = self.options.get("include_domains", [])

        # Domain restriction logic
        if context:
            try:
                # Extract hostname from URL (e.g., "https://bizgenieai.com/" -> "bizgenieai.com")
                parsed_url = urlparse(context)
                domain = parsed_url.netloc
                if domain:
                    # Remove 'www.' if present for broader matching
                    if domain.startswith("www."):
                        domain = domain[4:]
                    if domain not in include_domains:
                        include_domains.append(domain)
                    logger.info(f"Restricting Tavily search to domain: {domain}")
            except Exception as e:
                logger.warning(f"Could not parse context URL '{context}': {e}")

        logger.info(f"Searching Tavily with query: {query}")

        try:
            # Use config options
            search_depth = self.options.get("search_depth", "basic")
            max_results = self.options.get("max_results", 5)

            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains if include_domains else None,
                include_answer=False,
                include_raw_content=False,
                include_images=False
            )
            
            # Process results
            results = response.get("results", [])
            content_parts = []
            sources = []
            
            logger.info(f"Tavily returned {len(results)} results.")

            for res in results:
                title = res.get("title", "No title")
                url = res.get("url", "")
                text = res.get("content", "")
                
                content_parts.append(f"Source: {title}\nURL: {url}\nContent: {text}\n")
                sources.append(url)
            
            content = "\n---\n".join(content_parts)
            
            # --- LOGGING SEARCH RESULTS ---
            logger.info(f"Sources found: {sources}")
            preview = content[:500].replace("\n", " ") + "..."
            logger.info(f"Content Preview: {preview}")
            # ------------------------------
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            raise e

        search_time = time.time() - start_time
        search_cost = 0.0

        return SearchResult(
            content=content,
            sources=sources,
            metadata={"tool": "tavily", "query": query, "count": len(results)},
            search_time=search_time,
            search_cost=search_cost
        )

    def get_info(self) -> dict:
        return {
            "name": "Tavily AI Search",
            "cost_per_search": "Varies",
            "capabilities": ["search"]
        }
