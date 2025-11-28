"""
Tavily plugin for data retrieval.
Uses Tavily's API to extract content from URLs.
"""
from typing import List, Dict, Any
from datetime import datetime
from api.app.plugins.base import DataRetrievalPlugin, StandardDocument
from tavily import TavilyClient

class TavilyPlugin(DataRetrievalPlugin):
    """
    Tavily data retrieval plugin.
    Uses Tavily API to extract content from URLs.
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        if not self.api_key:
             raise ValueError("Tavily API key is required")
        self.client = TavilyClient(api_key=self.api_key)
        self.options = config.get("options", {})

    def fetch_url(self, url: str) -> StandardDocument:
        """
        Fetch a single URL using Tavily.

        Args:
            url: The URL to fetch

        Returns:
            StandardDocument with content
        """
        try:
            # Use the 'extract' functionality if available/appropriate for direct URL
            # Note: Tavily Python client has .extract() method
            response = self.client.extract(urls=[url])
            
            if not response or 'results' not in response or not response['results']:
                raise Exception("No results from Tavily extract")

            result = response['results'][0]
            
            # Prefer 'raw_content' if requested/available, otherwise 'content'
            # content is usually the cleaned text
            content = result.get('raw_content') or result.get('content')
            
            if not content:
                raise Exception("Empty content from Tavily")

            return StandardDocument(
                url=url,
                content=content,
                metadata={
                    "tavily_images": result.get('images', []),
                    "tavily_title": result.get('title', '')
                },
                timestamp=datetime.utcnow().isoformat(),
                source_plugin="tavily"
            )

        except Exception as e:
            raise Exception(f"Failed to fetch URL with Tavily: {str(e)}")

    def fetch_batch(self, urls: List[str]) -> List[StandardDocument]:
        """
        Fetch multiple URLs.
        """
        try:
            response = self.client.extract(urls=urls)
            documents = []
            
            for result in response.get('results', []):
                content = result.get('raw_content') or result.get('content')
                if content:
                    documents.append(StandardDocument(
                        url=result.get('url', 'unknown'),
                        content=content,
                        metadata={
                            "tavily_images": result.get('images', []),
                            "tavily_title": result.get('title', '')
                        },
                        timestamp=datetime.utcnow().isoformat(),
                        source_plugin="tavily"
                    ))
            return documents
            
        except Exception as e:
            print(f"Error in batch fetch: {e}")
            return []

    def get_capabilities(self) -> Dict:
        """Return plugin capabilities"""
        return {
            "name": "Tavily",
            "supports_js": True, # Tavily handles rendering
            "supports_batch": True,
            "rate_limit": "Depends on plan",
            "cost_per_request": "Paid",
            "output_format": "text/markdown", # Tavily tries to clean
            "requires_api_key": True,
        }

# Register the plugin
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_data_retrieval_plugin("tavily", TavilyPlugin)
