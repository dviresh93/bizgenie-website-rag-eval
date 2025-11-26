"""
Claude (Anthropic) LLM plugin for answer generation.
"""
from typing import List, Dict, Optional
from anthropic import Anthropic
from api.app.plugins.base import LLMPlugin, StandardResponse


class ClaudePlugin(LLMPlugin):
    """
    Claude 3.5 Sonnet plugin for answer generation.
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("options", {}).get("model", "claude-3-5-sonnet-20241022")
        self.temperature = config.get("options", {}).get("temperature", 0.7)
        self.max_tokens = config.get("options", {}).get("max_tokens", 1000)

        self.client = Anthropic(api_key=self.api_key)

    def generate(
        self,
        question: str,
        context: List[str],
        prompt_template: Optional[str] = None
    ) -> StandardResponse:
        """
        Generate answer using Claude.

        Args:
            question: User's question
            context: List of relevant text chunks
            prompt_template: Optional custom prompt

        Returns:
            StandardResponse with answer
        """
        # Build prompt
        if not prompt_template:
            prompt_template = self._default_prompt_template()

        context_text = "\n\n".join([f"[{i+1}] {chunk}" for i, chunk in enumerate(context)])

        full_prompt = prompt_template.format(
            context=context_text,
            question=question
        )

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )

            answer = response.content[0].text

            # Extract source references (if any)
            sources = self._extract_sources(answer, context)

            return StandardResponse(
                answer=answer,
                sources=sources,
                confidence=0.85,  # Could implement confidence scoring
                model_used=self.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def _default_prompt_template(self) -> str:
        """Default prompt template for Q&A"""
        return """You are a helpful assistant answering questions based on the provided context.

Context from website:
{context}

Question: {question}

Instructions:
1. Answer the question using ONLY information from the context above
2. If the answer is not in the context, say "I don't have enough information to answer that question."
3. Be concise and accurate
4. If you reference specific information, mention which part of the context it came from

Answer:"""

    def _extract_sources(self, answer: str, context: List[str]) -> List[str]:
        """Extract which context chunks were likely used (simple heuristic)"""
        # Simple implementation: return all provided context
        # Could be enhanced with semantic matching
        return [f"Context chunk {i+1}" for i in range(len(context))]

    def get_model_info(self) -> Dict:
        """Return model information"""
        return {
            "provider": "Anthropic",
            "model_name": self.model,
            "context_window": 200000,
            "cost_per_1m_input_tokens": 3.00,
            "cost_per_1m_output_tokens": 15.00,
            "supports_function_calling": True,
            "supports_vision": True
        }


# Register the plugin
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_llm_plugin("claude", ClaudePlugin)
