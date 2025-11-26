from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class StandardDocument:
    """Standardized document format all plugins must return"""
    url: str
    content: str  # Clean markdown/text
    metadata: Dict
    timestamp: str
    source_plugin: str

class DataRetrievalPlugin(ABC):
    """Base interface all data retrieval plugins must implement"""

    def __init__(self, config: Dict):
        self.config = config

    @abstractmethod
    def fetch_url(self, url: str) -> StandardDocument:
        """Fetch and process a single URL"""
        pass

    @abstractmethod
    def fetch_batch(self, urls: List[str]) -> List[StandardDocument]:
        """Fetch multiple URLs (optional optimization)"""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict:
        """Return plugin capabilities (supports_js, rate_limit, etc.)"""
        pass

@dataclass
class StandardResponse:
    """Standardized response format"""
    answer: str
    sources: List[str]
    confidence: float
    model_used: str
    tokens_used: int

class LLMPlugin(ABC):
    """Base interface for LLM plugins"""

    def __init__(self, config: Dict):
        self.config = config

    @abstractmethod
    def generate(
        self,
        question: str,
        context: List[str],
        prompt_template: Optional[str] = None
    ) -> StandardResponse:
        """Generate answer from question and context"""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        """Return model information (name, cost, limits)"""
        pass