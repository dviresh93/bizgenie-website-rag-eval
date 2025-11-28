# Adding New Plugins to the Framework

## Framework Flexibility

The testing framework is designed to be **fully extensible**. You can easily add:
- New MCP servers (data retrieval tools)
- New LLMs
- New configurations

All without modifying the testing infrastructure!

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   TESTING FRAMEWORK                     │
│                  (Never needs changes)                  │
├─────────────────────────────────────────────────────────┤
│  • collect_notebookllm_baseline.py                      │
│  • run_evaluation.py                                    │
│  • generate_comparison_report.py                        │
│  • standard_questions.json                              │
└─────────────────────────────────────────────────────────┘
                            ↓
                    Uses plugin system
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   PLUGIN SYSTEM                         │
│                 (Add plugins here)                      │
├─────────────────────────────────────────────────────────┤
│  MCP Servers:                                           │
│  • jina_plugin.py                                       │
│  • tavily_plugin.py          ← Add new ones here       │
│  • firecrawl_plugin.py                                  │
│  • your_new_mcp_plugin.py                               │
│                                                         │
│  LLMs:                                                  │
│  • claude_plugin.py                                     │
│  • gpt4_plugin.py            ← Add new ones here       │
│  • gemini_plugin.py                                     │
│  • your_new_llm_plugin.py                               │
└─────────────────────────────────────────────────────────┘
                            ↓
                    Configuration
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  config/configs.yaml                    │
│                  (Add configurations)                   │
├─────────────────────────────────────────────────────────┤
│  jina_gpt4:       ← Existing                            │
│  tavily_claude:   ← Existing                            │
│  firecrawl_gemini: ← Add new combinations here          │
└─────────────────────────────────────────────────────────┘
```

---

## Adding a New MCP Server Plugin

### Step 1: Create Plugin File

Create a new file: `api/app/plugins/data_retrieval/{name}_plugin.py`

### Step 2: Implement the Interface

```python
"""
Your New MCP Server Plugin
"""
from typing import List, Dict
from datetime import datetime
from api.app.plugins.base import DataRetrievalPlugin, StandardDocument


class YourMCPPlugin(DataRetrievalPlugin):
    """
    Description of your MCP server.

    Example: Firecrawl for professional web scraping
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        # Initialize your plugin
        self.api_key = config.get("api_key")
        self.base_url = config.get("options", {}).get("base_url", "https://api.example.com")

        # Initialize your client
        # self.client = YourMCPClient(api_key=self.api_key)

    def fetch_url(self, url: str) -> StandardDocument:
        """
        Fetch a single URL using your MCP server.

        Must return StandardDocument with:
        - url: Original URL
        - content: Clean markdown/text
        - metadata: Any additional data
        - timestamp: ISO format timestamp
        - source_plugin: Your plugin name
        """
        try:
            # Call your MCP server API
            # response = self.client.fetch(url)
            # content = response.get('markdown')

            # For this example, placeholder
            content = "Fetched content from " + url

            return StandardDocument(
                url=url,
                content=content,
                metadata={
                    "word_count": len(content.split()),
                    "fetch_time": 1.5,
                    # Add any relevant metadata
                },
                timestamp=datetime.utcnow().isoformat(),
                source_plugin="your_mcp"  # Change this
            )

        except Exception as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")

    def fetch_batch(self, urls: List[str]) -> List[StandardDocument]:
        """
        Fetch multiple URLs.

        Can implement parallel processing if your MCP supports it.
        """
        documents = []
        for url in urls:
            try:
                doc = self.fetch_url(url)
                documents.append(doc)
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue
        return documents

    def get_capabilities(self) -> Dict:
        """
        Return plugin capabilities.

        This helps users understand what your plugin supports.
        """
        return {
            "name": "Your MCP Server Name",
            "supports_js": True,  # Can handle JavaScript-rendered sites?
            "supports_batch": True,  # Can fetch multiple URLs efficiently?
            "rate_limit": "Your rate limit info",
            "cost_per_request": 0.01,  # Cost in USD, 0 if free
            "output_format": "markdown",  # or "html", "text"
            "requires_api_key": True,  # or False
        }


# Register the plugin
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_data_retrieval_plugin("your_mcp", YourMCPPlugin)
```

### Step 3: Add Configuration

Edit `config/configs.yaml`:

```yaml
configurations:
  # Add new configuration using your MCP
  your_mcp_gpt4:
    name: "Your MCP + GPT-4"
    description: "Your MCP server with GPT-4"
    data_retrieval:
      plugin: "your_mcp"        # Must match registration name
      api_key: ${YOUR_MCP_API_KEY}
      options:
        base_url: "https://api.yourmcp.com"
        timeout: 30
        # Add any options your plugin needs
    llm:
      plugin: "gpt4"
      api_key: ${OPENAI_API_KEY}
      options:
        model: "gpt-4-turbo-preview"
        temperature: 0.7
```

### Step 4: Add API Key to .env

```bash
# Add to .env file
YOUR_MCP_API_KEY=your-api-key-here
```

### Step 5: Test Your Plugin

```bash
# Import test
cd api
python -c "from app.plugins.data_retrieval.your_mcp_plugin import YourMCPPlugin; print('✓ Plugin loads')"

# Full test
cd ..
python scripts/run_evaluation.py --config your_mcp_gpt4
```

### Step 6: Run Comparison

```bash
# Your new plugin is automatically included!
python scripts/generate_comparison_report.py
```

---

## Adding a New LLM Plugin

### Step 1: Create Plugin File

Create: `api/app/plugins/llm/{name}_plugin.py`

### Step 2: Implement the Interface

```python
"""
Your New LLM Plugin
"""
from typing import List, Dict, Optional
from api.app.plugins.base import LLMPlugin, StandardResponse


class YourLLMPlugin(LLMPlugin):
    """
    Description of your LLM.

    Example: Google Gemini for answer generation
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("options", {}).get("model", "default-model")
        self.temperature = config.get("options", {}).get("temperature", 0.7)
        self.max_tokens = config.get("options", {}).get("max_tokens", 1000)

        # Initialize your LLM client
        # self.client = YourLLMClient(api_key=self.api_key)

    def generate(
        self,
        question: str,
        context: List[str],
        prompt_template: Optional[str] = None
    ) -> StandardResponse:
        """
        Generate answer using your LLM.

        Must return StandardResponse with:
        - answer: The generated answer
        - sources: List of source references
        - confidence: 0-1 confidence score
        - model_used: Model name
        - tokens_used: Total tokens consumed
        """
        # Build prompt
        if not prompt_template:
            prompt_template = self._default_prompt_template()

        context_text = "\n\n".join([f"[{i+1}] {chunk}" for i, chunk in enumerate(context)])
        full_prompt = prompt_template.format(context=context_text, question=question)

        try:
            # Call your LLM API
            # response = self.client.generate(
            #     prompt=full_prompt,
            #     model=self.model,
            #     temperature=self.temperature,
            #     max_tokens=self.max_tokens
            # )
            # answer = response.text
            # tokens = response.tokens_used

            # Placeholder for example
            answer = f"Answer generated by {self.model} for: {question}"
            tokens = 500

            return StandardResponse(
                answer=answer,
                sources=[f"Context chunk {i+1}" for i in range(len(context))],
                confidence=0.85,
                model_used=self.model,
                tokens_used=tokens
            )

        except Exception as e:
            raise Exception(f"LLM generation error: {str(e)}")

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

    def get_model_info(self) -> Dict:
        """Return model information"""
        return {
            "provider": "Your Provider Name",
            "model_name": self.model,
            "context_window": 32000,  # Token limit
            "cost_per_1m_input_tokens": 1.00,  # USD
            "cost_per_1m_output_tokens": 5.00,  # USD
            "supports_function_calling": False,
            "supports_vision": False
        }


# Register the plugin
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_llm_plugin("your_llm", YourLLMPlugin)
```

### Step 3: Add Configuration

Edit `config/configs.yaml`:

```yaml
configurations:
  # Add new configuration using your LLM
  jina_your_llm:
    name: "Jina + Your LLM"
    description: "Jina retrieval with your LLM"
    data_retrieval:
      plugin: "jina"
      api_key: ${JINA_API_KEY}
    llm:
      plugin: "your_llm"        # Must match registration name
      api_key: ${YOUR_LLM_API_KEY}
      options:
        model: "your-model-name"
        temperature: 0.7
        max_tokens: 1000
```

### Step 4: Add API Key to .env

```bash
# Add to .env file
YOUR_LLM_API_KEY=your-api-key-here
```

### Step 5: Test Your Plugin

```bash
# Test
python scripts/run_evaluation.py --config jina_your_llm
```

---

## Real Examples

### Example 1: Adding Firecrawl MCP

```python
# api/app/plugins/data_retrieval/firecrawl_plugin.py

from firecrawl import FirecrawlApp
from typing import List, Dict
from datetime import datetime
from api.app.plugins.base import DataRetrievalPlugin, StandardDocument


class FirecrawlPlugin(DataRetrievalPlugin):
    """Firecrawl MCP plugin for professional web scraping"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.client = FirecrawlApp(api_key=self.api_key)

    def fetch_url(self, url: str) -> StandardDocument:
        result = self.client.scrape_url(
            url,
            params={'formats': ['markdown']}
        )

        return StandardDocument(
            url=url,
            content=result['markdown'],
            metadata={
                "word_count": len(result['markdown'].split()),
                "scrape_time": result.get('time', 0)
            },
            timestamp=datetime.utcnow().isoformat(),
            source_plugin="firecrawl"
        )

    def fetch_batch(self, urls: List[str]) -> List[StandardDocument]:
        # Firecrawl supports batch crawling
        return [self.fetch_url(url) for url in urls]

    def get_capabilities(self) -> Dict:
        return {
            "name": "Firecrawl",
            "supports_js": True,
            "supports_batch": True,
            "rate_limit": "Based on plan",
            "cost_per_request": 0.01,
            "output_format": "markdown",
            "requires_api_key": True
        }


# Register
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_data_retrieval_plugin("firecrawl", FirecrawlPlugin)
```

**Config:**
```yaml
firecrawl_gpt4:
  name: "Firecrawl + GPT-4"
  data_retrieval:
    plugin: "firecrawl"
    api_key: ${FIRECRAWL_API_KEY}
  llm:
    plugin: "gpt4"
    api_key: ${OPENAI_API_KEY}
```

**Test:**
```bash
python scripts/run_evaluation.py --config firecrawl_gpt4
```

### Example 2: Adding Google Gemini LLM

```python
# api/app/plugins/llm/gemini_plugin.py

import google.generativeai as genai
from typing import List, Dict, Optional
from api.app.plugins.base import LLMPlugin, StandardResponse


class GeminiPlugin(LLMPlugin):
    """Google Gemini LLM plugin"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        genai.configure(api_key=self.api_key)

        model_name = config.get("options", {}).get("model", "gemini-pro")
        self.model = genai.GenerativeModel(model_name)
        self.temperature = config.get("options", {}).get("temperature", 0.7)

    def generate(self, question: str, context: List[str],
                 prompt_template: Optional[str] = None) -> StandardResponse:

        if not prompt_template:
            prompt_template = self._default_prompt_template()

        context_text = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(context)])
        full_prompt = prompt_template.format(context=context_text, question=question)

        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature
            )
        )

        return StandardResponse(
            answer=response.text,
            sources=[f"Context {i+1}" for i in range(len(context))],
            confidence=0.85,
            model_used="gemini-pro",
            tokens_used=response.usage_metadata.total_token_count
        )

    def _default_prompt_template(self) -> str:
        return """Answer the question based on the context provided.

Context:
{context}

Question: {question}

Answer:"""

    def get_model_info(self) -> Dict:
        return {
            "provider": "Google",
            "model_name": "gemini-pro",
            "context_window": 32000,
            "cost_per_1m_input_tokens": 0.50,
            "cost_per_1m_output_tokens": 1.50,
            "supports_function_calling": True,
            "supports_vision": True
        }


# Register
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_llm_plugin("gemini", GeminiPlugin)
```

**Config:**
```yaml
jina_gemini:
  name: "Jina + Gemini"
  data_retrieval:
    plugin: "jina"
  llm:
    plugin: "gemini"
    api_key: ${GOOGLE_API_KEY}
    options:
      model: "gemini-pro"
      temperature: 0.7
```

**Test:**
```bash
python scripts/run_evaluation.py --config jina_gemini
```

---

## Testing Multiple New Plugins at Once

```bash
# Add 3 new plugins: Firecrawl, Gemini, Mixtral
# Create plugin files and configs

# Test all combinations
python scripts/run_evaluation.py --config firecrawl_gpt4
python scripts/run_evaluation.py --config firecrawl_gemini
python scripts/run_evaluation.py --config jina_mixtral

# Generate comparison
python scripts/generate_comparison_report.py

# Report automatically includes all new plugins!
```

---

## Plugin Development Checklist

### For MCP Server Plugins

- [ ] Create plugin file in `api/app/plugins/data_retrieval/`
- [ ] Implement `DataRetrievalPlugin` interface
- [ ] Implement `fetch_url()` method
- [ ] Implement `fetch_batch()` method
- [ ] Implement `get_capabilities()` method
- [ ] Return `StandardDocument` format
- [ ] Register plugin with `PluginFactory`
- [ ] Add configuration to `configs.yaml`
- [ ] Add API key to `.env`
- [ ] Test with `run_evaluation.py`
- [ ] Verify in comparison report

### For LLM Plugins

- [ ] Create plugin file in `api/app/plugins/llm/`
- [ ] Implement `LLMPlugin` interface
- [ ] Implement `generate()` method
- [ ] Implement `get_model_info()` method
- [ ] Return `StandardResponse` format
- [ ] Register plugin with `PluginFactory`
- [ ] Add configuration to `configs.yaml`
- [ ] Add API key to `.env`
- [ ] Test with `run_evaluation.py`
- [ ] Verify in comparison report

---

## Plugin Registry

The system automatically discovers plugins through registration:

```python
# In your plugin file
from api.app.core.plugin_factory import PluginFactory

# Register MCP server
PluginFactory.register_data_retrieval_plugin("plugin_name", YourPluginClass)

# Or register LLM
PluginFactory.register_llm_plugin("plugin_name", YourPluginClass)
```

No other changes needed - the framework automatically:
- Loads your plugin when referenced in config
- Includes it in evaluations
- Compares it in reports
- Tracks its performance

---

## Summary

### To Add New MCP Server:
1. Create plugin file (15 min)
2. Implement interface (30 min)
3. Add config (5 min)
4. Test (5 min)
**Total: ~1 hour**

### To Add New LLM:
1. Create plugin file (15 min)
2. Implement interface (30 min)
3. Add config (5 min)
4. Test (5 min)
**Total: ~1 hour**

### Framework Automatically:
✅ Tests new plugins
✅ Compares against existing
✅ Generates analytics
✅ Recommends best option
✅ No framework code changes needed!

---

**The framework is ready for any new plugins you want to test!**
