import yaml
import copy
import os
import re
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()
            
            # Resolve environment variables in the YAML content
            def replace_env_var(match):
                env_var = match.group(1)
                return os.getenv(env_var, "")

            content = re.sub(r'\${(\w+)}', replace_env_var, content)
            
            return yaml.safe_load(content)
        except FileNotFoundError:
            raise Exception(f"Config file not found at {self.config_path}")

    def get_mcp_tool_config(self, tool_name: str) -> Dict[str, Any]:
        tools = self.config.get("mcp_tools", {})
        if tool_name not in tools:
            raise ValueError(f"MCP tool '{tool_name}' not found")
        return copy.deepcopy(tools[tool_name])

    def get_llm_model_config(self, model_name: str) -> Dict[str, Any]:
        models = self.config.get("llm_models", {})
        if model_name not in models:
            raise ValueError(f"LLM model '{model_name}' not found")
        return copy.deepcopy(models[model_name])

    def list_components(self) -> Dict[str, Any]:
        return {
            "mcp_tools": copy.deepcopy(self.config.get("mcp_tools", {})),
            "llm_models": copy.deepcopy(self.config.get("llm_models", {}))
        }
