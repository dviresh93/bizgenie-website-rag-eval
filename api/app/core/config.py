import yaml
import copy
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise Exception(f"Config file not found at {self.config_path}")

    def get_active_config(self) -> str:
        return self.config.get("active_config")

    def get_data_retrieval_config(self, config_name: str) -> Dict[str, Any]:
        return copy.deepcopy(self.config["configurations"][config_name]["data_retrieval"])

    def get_llm_config(self, config_name: str) -> Dict[str, Any]:
        return copy.deepcopy(self.config["configurations"][config_name]["llm"])

    def get_processing_config(self) -> Dict[str, Any]:
        return copy.deepcopy(self.config["processing"])

    def list_configs(self) -> Dict[str, Any]:
        return copy.deepcopy(self.config["configurations"])
