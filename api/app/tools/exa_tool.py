import os
import time
from exa_py import Exa
from api.app.tools.base import MCPTool, SearchResult
from api.app.core.logging import get_logger

logger = get_logger("exa_tool")

class ExaTool(MCPTool):
    """Exa AI Search MCP tool"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = os.environ.get(config.get("api_key_env", "EXA_API_KEY"))
        if not self.api_key:
            raise ValueError("Exa API key is required")
        self.client = Exa(api_key=self.api_key)
        self.options = config.get("config", {})

    def search(self, question: str, context: str = None) -> SearchResult:
        """Search using Exa API"""
        start_time = time.time()
        
        query = question
        include_domains = self.options.get("include_domains", [])
        if context and context not in include_domains:
            # Extract domain from URL if full URL provided
            from urllib.parse import urlparse
            try:
                domain = urlparse(context).netloc
                if domain:
                    include_domains.append(domain)
            except:
                pass

        logger.info(f"Searching Exa with query: {query}")

        try:
            # Use config options
            num_results = self.options.get("max_results", 5)
            # Removed use_autoprompt as it caused validation errors
            # use_autoprompt = self.options.get("use_autoprompt", True) 

            response = self.client.search_and_contents(
                query,
                num_results=num_results,
                # use_autoprompt=use_autoprompt, # Removed
                type="neural", # Use neural search explicitly which handles query understanding
                include_domains=include_domains if include_domains else None,
                text=True
            )
            
            # Process results
            results = response.results
            content_parts = []
            sources = []
            
            logger.info(f"Exa returned {len(results)} results.")

            for res in results:
                title = res.title or "No title"
                url = res.url
                text = res.text or ""
                
                content_parts.append(f"Source: {title}\nURL: {url}\nContent: {text}\n")
                sources.append(url)
            
            content = "\n---\n".join(content_parts)
            
            # --- LOGGING ---
            logger.info(f"Sources found: {sources}")
            
        except Exception as e:
            logger.info(f"Exa search failed: {e}") # Changed to error log
            raise e

        search_time = time.time() - start_time
        search_cost = 0.0 # Exa pricing depends on plan

        return SearchResult(
            content=content,
            sources=sources,
            metadata={"tool": "exa", "query": query, "count": len(results)},
            search_time=search_time,
            search_cost=search_cost
        )

    def get_info(self) -> dict:
        return {
            "name": "Exa AI Search",
            "cost_per_search": "Varies",
            "capabilities": ["search", "autoprompt"]
        }