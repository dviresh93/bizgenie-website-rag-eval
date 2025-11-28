from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class LLMResponse:
    """Response from LLM generation"""
    answer: str               # Generated answer
    model: str                # Model identifier
    tokens_used: int          # Tokens consumed
    generation_time: float    # Time taken (seconds)
    generation_cost: float    # Cost of generation

class LLM(ABC):
    """Base class for all LLMs (Claude, GPT-4, etc.)"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], context: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """
        Generate answer from conversation history and context.

        Args:
            messages: List of messages [{"role": "user", "content": "..."}]
            context: Search results from MCP tool
            system_prompt: Optional system instruction/persona

        Returns:
            LLMResponse with answer and metrics
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """
        Return model metadata.
        """
        pass
