"""
Jina AI Reader plugin for data retrieval.
Uses Jina's free r.jina.ai service to convert URLs to markdown.
"""
import httpx
from typing import List, Dict
from datetime import datetime
from api.app.plugins.base import DataRetrievalPlugin, StandardDocument


class JinaPlugin(DataRetrievalPlugin):
    """
    Jina AI Reader plugin.

    Uses https://r.jina.ai/{url} to fetch and convert web pages to markdown.
    No API key required for basic usage.
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://r.jina.ai"
        self.api_key = config.get("api_key")  # Optional
        self.batch_size = config.get("options", {}).get("batch_size", 10)

    def fetch_url(self, url: str) -> StandardDocument:
        """
        Fetch a single URL using Jina AI Reader.

        Args:
            url: The URL to fetch

        Returns:
            StandardDocument with markdown content
        """
        jina_url = f"{self.base_url}/{url}"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(jina_url, headers=headers)
                response.raise_for_status()

                markdown_content = response.text

                # Extract metadata from headers if available
                metadata = {
                    "content_length": len(markdown_content),
                    "jina_response_time": response.elapsed.total_seconds(),
                }

                return StandardDocument(
                    url=url,
                    content=markdown_content,
                    metadata=metadata,
                    timestamp=datetime.utcnow().isoformat(),
                    source_plugin="jina"
                )

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch URL with Jina: {str(e)}")

    def fetch_batch(self, urls: List[str]) -> List[StandardDocument]:
        """
        Fetch multiple URLs using parallel processing.

        Args:
            urls: List of URLs to fetch

        Returns:
            List of StandardDocuments
        """
        documents = []

        # Process in batches for rate limiting
        for i in range(0, len(urls), self.batch_size):
            batch = urls[i:i + self.batch_size]

            for url in batch:
                try:
                    doc = self.fetch_url(url)
                    documents.append(doc)
                except Exception as e:
                    print(f"Error fetching {url}: {e}")
                    continue

        return documents

    def get_capabilities(self) -> Dict:
        """Return plugin capabilities"""
        return {
            "name": "Jina AI Reader",
            "supports_js": True,
            "supports_batch": True,
            "rate_limit": "20 req/sec (free tier)" if not self.api_key else "higher",
            "cost_per_request": 0.0,  # Free tier
            "output_format": "markdown",
            "requires_api_key": False,
        }


# Register the plugin
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_data_retrieval_plugin("jina", JinaPlugin)
