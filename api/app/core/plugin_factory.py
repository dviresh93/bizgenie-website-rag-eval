from typing import Dict, Type
from api.app.plugins.base import DataRetrievalPlugin, LLMPlugin

class PluginFactory:
    """
    Manages the registration and creation of plugin instances.
    """
    _data_retrieval_plugins: Dict[str, Type[DataRetrievalPlugin]] = {}
    _llm_plugins: Dict[str, Type[LLMPlugin]] = {}

    @staticmethod
    def register_data_retrieval_plugin(name: str, plugin_class: Type[DataRetrievalPlugin]):
        """Registers a data retrieval plugin."""
        PluginFactory._data_retrieval_plugins[name] = plugin_class

    @staticmethod
    def create_data_retrieval_plugin(name: str, config: Dict) -> DataRetrievalPlugin:
        """Creates an instance of a registered data retrieval plugin."""
        plugin_class = PluginFactory._data_retrieval_plugins.get(name)
        if not plugin_class:
            raise ValueError(f"Data retrieval plugin '{name}' not found.")
        return plugin_class(config)

    @staticmethod
    def register_llm_plugin(name: str, plugin_class: Type[LLMPlugin]):
        """Registers an LLM plugin."""
        PluginFactory._llm_plugins[name] = plugin_class

    @staticmethod
    def create_llm_plugin(name: str, config: Dict) -> LLMPlugin:
        """Creates an instance of a registered LLM plugin."""
        plugin_class = PluginFactory._llm_plugins.get(name)
        if not plugin_class:
            raise ValueError(f"LLM plugin '{name}' not found.")
        return plugin_class(config)
