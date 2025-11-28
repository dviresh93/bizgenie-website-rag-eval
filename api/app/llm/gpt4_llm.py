import os
import time
from typing import List, Dict
from openai import OpenAI
from api.app.llm.base import LLM, LLMResponse
from api.app.core.logging import get_logger
from api.app.core.prompts import PromptManager

logger = get_logger("gpt4_llm")

class GPT4LLM(LLM):
    """GPT-4 LLM implementation"""

    def __init__(self, config: dict):
        super().__init__(config)
        api_key = os.environ.get(config.get("api_key_env", "OPENAI_API_KEY"))
        self.client = OpenAI(api_key=api_key)
        self.model = config["config"]["model"]
        self.temperature = config["config"].get("temperature", 0.7)
        self.max_tokens = config["config"].get("max_tokens", 2048)

    def generate(self, messages: List[Dict[str, str]], context: str, system_prompt: str = None) -> LLMResponse:
        """Generate answer using GPT-4"""
        start_time = time.time()
        
        logger.info(f"Generating answer with {self.model}")

        # Build Messages List
        api_messages = []
        
        # 1. System Prompt
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
            logger.info(f"Using System Prompt: {system_prompt[:100]}...")
        else:
            api_messages.append({"role": "system", "content": "You are a helpful assistant."})

        # 2. History + Context Injection
        input_msgs_copy = [m.copy() for m in messages]
        
        last_user_index = -1
        for i in range(len(input_msgs_copy) - 1, -1, -1):
            if input_msgs_copy[i]["role"] == "user":
                last_user_index = i
                break
        
        if last_user_index != -1:
            original_question = input_msgs_copy[last_user_index]["content"]
            # Use PromptManager
            enriched_content = PromptManager.get_user_prompt(original_question, context)
            input_msgs_copy[last_user_index]["content"] = enriched_content
        
        # Add to api_messages
        api_messages.extend(input_msgs_copy)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Logging
            answer_preview = answer[:500].replace('\n', ' ')
            logger.info(f"GPT-4 Answer: {answer_preview}...")
            logger.info(f"Tokens used: Total={tokens_used}")

            generation_time = time.time() - start_time

            # Pricing
            input_cost = response.usage.prompt_tokens * 10.00 / 1_000_000
            output_cost = response.usage.completion_tokens * 30.00 / 1_000_000
            generation_cost = input_cost + output_cost

            return LLMResponse(
                answer=answer,
                model=self.model,
                tokens_used=tokens_used,
                generation_time=generation_time,
                generation_cost=generation_cost
            )
        except Exception as e:
            logger.error(f"GPT-4 generation failed: {e}")
            raise e

    def get_info(self) -> dict:
        return {
            "name": "GPT-4 Turbo",
            "cost_per_1k_input_tokens": 0.01,
            "cost_per_1k_output_tokens": 0.03,
            "max_tokens": 4096
        }
