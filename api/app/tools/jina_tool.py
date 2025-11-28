import os
import time
import requests
import urllib.parse
from urllib.parse import urlparse
from api.app.tools.base import MCPTool, SearchResult
from api.app.core.logging import get_logger

logger = get_logger("jina_tool")

class JinaTool(MCPTool):
    """Jina AI Reader MCP tool"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = os.environ.get(config.get("api_key_env", "JINA_API_KEY"))
        self.base_url = "https://r.jina.ai"

    def search(self, question: str, context: str = None) -> SearchResult:
        """
        Fetch content using Jina.
        Priority:
        1. If context (Target URL) is provided, READ that URL directly.
        2. If no context, SEARCH using the question.
        """
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Return-Format": "markdown"
        }

        content = ""
        sources = []
        used_query = question

        try:
            # STRATEGY 1: Direct Read of Target URL (Highest Priority)
            if context and context.startswith("http"):
                logger.info(f"Strategy 1: Reading target URL directly: {context}")
                url = f"https://r.jina.ai/{context}"
                
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    content = response.text
                    sources.append(context)
                    used_query = f"Read content of {context}"
                    logger.info(f"Jina Read successful. Length: {len(content)}")
                except Exception as e:
                    logger.warning(f"Strategy 1 failed: {e}")
                    # Fall through to search if read fails
            
            # STRATEGY 2: Search (Only if no context or read failed)
            if not content:
                logger.info("Strategy 2: Performing Search")
                
                # Construct search query
                search_query = question
                if context:
                    try:
                        parsed_url = urlparse(context)
                        domain = parsed_url.netloc
                        if domain:
                            search_query = f"{question} site:{domain}"
                    except:
                        pass
                
                encoded_query = urllib.parse.quote(search_query)
                url = f"https://s.jina.ai/{encoded_query}"
                
                response = requests.get(url, headers=headers)
                
                # Handle 422 Fallback (Broad Search)
                if response.status_code == 422:
                    logger.warning("Search 422. Retrying without site filter...")
                    encoded_simple = urllib.parse.quote(question)
                    url = f"https://s.jina.ai/{encoded_simple}"
                    response = requests.get(url, headers=headers)

                response.raise_for_status()
                content = response.text
                used_query = search_query
                
                # Extract sources from search results
                sources = self._extract_sources(content)
                logger.info(f"Jina Search successful. Length: {len(content)}")

        except Exception as e:
            logger.error(f"Jina operation failed: {e}")
            raise e

        search_time = time.time() - start_time
        
        return SearchResult(
            content=content,
            sources=sources,
            metadata={"tool": "jina", "query": used_query},
            search_time=search_time,
            search_cost=0.0
        )

    def _extract_sources(self, content: str) -> list:
        """Extract URLs from Jina markdown response"""
        import re
        markdown_links = re.findall(r'\[.*?\]\((https?://[\w\-\./\?=&%]+)\)', content)
        plain_links = re.findall(r'https?://[\w\-\./\?=&%]+', content)
        all_links = markdown_links + plain_links
        unique_urls = list(set(all_links))
        filtered_urls = [u for u in unique_urls if "jina.ai" not in u]
        return filtered_urls[:5]

    def get_info(self) -> dict:
        return {
            "name": "Jina AI",
            "cost_per_search": 0.0,
            "capabilities": ["search", "read_url"]
        }
