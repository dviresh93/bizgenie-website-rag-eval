import os
import time
import anthropic
from typing import List, Dict
from api.app.llm.base import LLM, LLMResponse
from api.app.core.logging import get_logger
from api.app.core.prompts import PromptManager

logger = get_logger("claude_llm")

class ClaudeLLM(LLM):
    """Claude LLM implementation"""

    def __init__(self, config: dict):
        super().__init__(config)
        api_key = os.environ.get(config.get("api_key_env", "ANTHROPIC_API_KEY"))
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = config["config"]["model"]
        self.temperature = config["config"].get("temperature", 0.7)
        self.max_tokens = config["config"].get("max_tokens", 2048)

    def generate(self, messages: List[Dict[str, str]], context: str, system_prompt: str = None) -> LLMResponse:
        """Generate answer using Claude"""
        start_time = time.time()
        
        logger.info(f"Generating answer with {self.model}")

        # Deep copy messages
        api_messages = [m.copy() for m in messages]
        
        # Inject context into the last user message using PromptManager
        last_user_msg_index = -1
        for i in range(len(api_messages) - 1, -1, -1):
            if api_messages[i]["role"] == "user":
                last_user_msg_index = i
                break
        
        if last_user_msg_index != -1:
            original_question = api_messages[last_user_msg_index]["content"]
            # Use PromptManager to format the enriched user prompt
            enriched_content = PromptManager.get_user_prompt(original_question, context)
            api_messages[last_user_msg_index]["content"] = enriched_content
        else:
            # Fallback
            api_messages.append({
                "role": "user", 
                "content": PromptManager.get_user_prompt("Please provide an update.", context)
            })

        # Prepare arguments
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": api_messages
        }

        if system_prompt:
            kwargs["system"] = system_prompt
            logger.info(f"Using System Prompt: {system_prompt[:100]}...")

        try:
            response = self.client.messages.create(**kwargs)

            answer = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            # Logging
            answer_preview = answer[:500].replace('\n', ' ')
            logger.info(f"Claude Answer: {answer_preview}...")
            logger.info(f"Tokens used: Input={response.usage.input_tokens}, Output={response.usage.output_tokens}")

            generation_time = time.time() - start_time

            # Pricing
            input_cost = response.usage.input_tokens * 3.00 / 1_000_000
            output_cost = response.usage.output_tokens * 15.00 / 1_000_000
            generation_cost = input_cost + output_cost

            return LLMResponse(
                answer=answer,
                model=self.model,
                tokens_used=tokens_used,
                generation_time=generation_time,
                generation_cost=generation_cost
            )
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise e

    def get_info(self) -> dict:
        return {
            "name": "Claude 3.5 Sonnet",
            "cost_per_1k_input_tokens": 0.003,
            "cost_per_1k_output_tokens": 0.015,
            "max_tokens": 8192
        }
