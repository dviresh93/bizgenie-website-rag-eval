# Architecture: MCP Tool + LLM Evaluation Framework

**Last Updated**: 2025-01-26

---

## Goal: Find the Best MCP Tool + LLM Combination

**What we're building:**
A testing framework that allows us to systematically evaluate different combinations of:
- **MCP Tools** (Jina, Tavily, Firecrawl, etc.) - for real-time web search
- **LLMs** (GPT-4, Claude, etc.) - for answer generation

**Purpose:**
Determine which MCP tool + LLM combination produces the best chatbot answers.

---

## User Flow

### 1. UI (User picks combination)
```
┌─────────────────────────────┐
│  Select MCP Tool:           │
│  [Tavily ▼]                 │  ← User selects search tool
│                             │
│  Select LLM:                │
│  [Claude ▼]                 │  ← User selects answer model
│                             │
│  Question: ________________ │
│  [Ask]                      │
└─────────────────────────────┘
```

### 2. System Flow (Real-time per query)
```
User Question
    ↓
Selected MCP Tool searches (e.g., Tavily)
    ↓
Fresh web content returned
    ↓
Selected LLM generates answer (e.g., Claude)
    ↓
Answer + Sources + Metrics
```

### 3. Evaluation (Compare combinations)
```
Test all combinations:
  - Tavily + GPT-4
  - Tavily + Claude
  - Jina + GPT-4
  - Jina + Claude
  - Firecrawl + GPT-4
  - Firecrawl + Claude

Find winner based on:
  - Answer quality
  - Speed
  - Cost
  - Reliability
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                          UI Layer                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ MCP Dropdown   │  │ LLM Dropdown   │  │ Question Input │ │
│  │ - Tavily       │  │ - Claude       │  │                │ │
│  │ - Jina         │  │ - GPT-4        │  │                │ │
│  │ - Firecrawl    │  │ - Gemini       │  │                │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                        API Layer                              │
│  POST /query                                                  │
│  {                                                            │
│    "question": "What does BizGenie offer?",                  │
│    "mcp_tool": "tavily",    ← User's selection               │
│    "llm_model": "claude"    ← User's selection               │
│  }                                                            │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Processing Layer                           │
│                                                               │
│  Step 1: Use Selected MCP Tool                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  if mcp_tool == "tavily":                           │    │
│  │      results = tavily.search(question)              │    │
│  │  elif mcp_tool == "jina":                           │    │
│  │      results = jina.search(question)                │    │
│  │  elif mcp_tool == "firecrawl":                      │    │
│  │      results = firecrawl.search(question)           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  Step 2: Use Selected LLM                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  if llm_model == "claude":                          │    │
│  │      answer = claude.generate(question, results)    │    │
│  │  elif llm_model == "gpt4":                          │    │
│  │      answer = gpt4.generate(question, results)      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  Step 3: Collect Metrics                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  - MCP search time                                   │    │
│  │  - MCP search cost                                   │    │
│  │  - Content quality from MCP                          │    │
│  │  - LLM generation time                               │    │
│  │  - LLM cost                                          │    │
│  │  - Answer quality                                    │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                     Response                                  │
│  {                                                            │
│    "answer": "BizGenie offers...",                           │
│    "sources": ["url1", "url2"],                              │
│    "metrics": {                                              │
│      "mcp_search_time": 1.8,                                 │
│      "mcp_cost": 0.01,                                       │
│      "llm_time": 1.2,                                        │
│      "llm_cost": 0.02,                                       │
│      "total_time": 3.0,                                      │
│      "total_cost": 0.03                                      │
│    }                                                          │
│  }                                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Principles

### 1. User Control (Not Agent Control)
- **User picks** the MCP tool and LLM
- System uses exactly what user selected
- No agent deciding which tool to use

### 2. Real-time Search
- Each query triggers fresh MCP search
- No pre-indexing
- No ChromaDB (unless we add caching later)

### 3. Modular & Extensible
- Easy to add new MCP tools
- Easy to add new LLMs
- Dropdown automatically populated from available options

### 4. Metric Isolation
- Can measure MCP tool quality separately
- Can measure LLM quality separately
- Can measure combination synergy

---

## Configuration Structure

```yaml
# Available MCP Tools
mcp_tools:
  tavily:
    name: "Tavily AI Search"
    class: "TavilyTool"
    api_key: ${TAVILY_API_KEY}
    config:
      search_depth: "advanced"
      max_results: 5

  jina:
    name: "Jina AI Reader"
    class: "JinaTool"
    api_key: ${JINA_API_KEY}
    config:
      mode: "search"

  firecrawl:
    name: "Firecrawl"
    class: "FirecrawlTool"
    api_key: ${FIRECRAWL_API_KEY}
    config:
      crawl_depth: 2

# Available LLMs
llm_models:
  claude:
    name: "Claude 3.5 Sonnet"
    class: "ClaudeLLM"
    api_key: ${ANTHROPIC_API_KEY}
    config:
      model: "claude-3-5-sonnet-20241022"
      temperature: 0.7

  gpt4:
    name: "GPT-4 Turbo"
    class: "GPT4LLM"
    api_key: ${OPENAI_API_KEY}
    config:
      model: "gpt-4-turbo-preview"
      temperature: 0.7

  gemini:
    name: "Gemini Pro"
    class: "GeminiLLM"
    api_key: ${GOOGLE_API_KEY}
    config:
      model: "gemini-pro"
```

---

## Plugin Interfaces

### MCP Tool Interface
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class SearchResult:
    content: str           # Relevant content found
    sources: list[str]     # Source URLs
    metadata: dict         # Tool-specific metadata

class MCPTool(ABC):
    """Base class for all MCP tools"""

    @abstractmethod
    def search(self, question: str, context: str = None) -> SearchResult:
        """
        Search for information based on question.

        Args:
            question: User's question
            context: Optional context (e.g., "bizgenieai.com")

        Returns:
            SearchResult with relevant content
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """Return tool information (name, cost, capabilities)"""
        pass
```

### LLM Interface
```python
@dataclass
class LLMResponse:
    answer: str           # Generated answer
    model: str            # Model used
    tokens: int           # Tokens consumed

class LLM(ABC):
    """Base class for all LLMs"""

    @abstractmethod
    def generate(self, question: str, context: str) -> LLMResponse:
        """
        Generate answer from question and context.

        Args:
            question: User's question
            context: Search results from MCP tool

        Returns:
            LLMResponse with answer
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """Return model information (name, cost, limits)"""
        pass
```

---

## API Endpoints

### GET /components
Returns available MCP tools and LLMs for dropdowns.

```json
{
  "mcp_tools": [
    {"id": "tavily", "name": "Tavily AI Search"},
    {"id": "jina", "name": "Jina AI Reader"},
    {"id": "firecrawl", "name": "Firecrawl"}
  ],
  "llm_models": [
    {"id": "claude", "name": "Claude 3.5 Sonnet"},
    {"id": "gpt4", "name": "GPT-4 Turbo"},
    {"id": "gemini", "name": "Gemini Pro"}
  ]
}
```

### POST /query
Execute query with selected combination.

**Request:**
```json
{
  "question": "What services does BizGenie offer?",
  "mcp_tool": "tavily",
  "llm_model": "claude",
  "context": "bizgenieai.com"  // optional
}
```

**Response:**
```json
{
  "answer": "BizGenie offers AI automation services...",
  "sources": [
    "https://bizgenieai.com/services",
    "https://bizgenieai.com/about"
  ],
  "metrics": {
    "mcp_tool_used": "tavily",
    "mcp_search_time": 1.8,
    "mcp_cost": 0.01,
    "mcp_sources_count": 5,

    "llm_model_used": "claude",
    "llm_time": 1.2,
    "llm_cost": 0.02,
    "llm_tokens": 850,

    "total_time": 3.0,
    "total_cost": 0.03
  }
}
```

---

## Evaluation Framework

### Test Combinations
```python
combinations = [
    {"mcp": "tavily", "llm": "claude"},
    {"mcp": "tavily", "llm": "gpt4"},
    {"mcp": "jina", "llm": "claude"},
    {"mcp": "jina", "llm": "gpt4"},
    {"mcp": "firecrawl", "llm": "claude"},
    {"mcp": "firecrawl", "llm": "gpt4"},
]

for combo in combinations:
    for question in test_questions:
        result = query(question, combo["mcp"], combo["llm"])
        collect_metrics(result)
```

### Metrics Collected

**Per Combination:**
- Average search time
- Average search cost
- Search quality score
- Average LLM time
- Average LLM cost
- Answer quality score
- Total cost per query
- Error rate

**Comparison:**
```
Winner: tavily + claude
  - Best answer quality: 89/100
  - Good speed: 3.2s average
  - Acceptable cost: $0.035/query
  - Low error rate: 1%

Runner-up: jina + gpt4
  - Good quality: 85/100
  - Fastest: 2.8s average
  - Cheapest: $0.018/query
  - Low error rate: 2%
```

---

## Adding New MCP Tools (Easy!)

### Step 1: Create tool class
```python
# api/app/tools/mcp/my_new_tool.py

from api.app.tools.base import MCPTool, SearchResult

class MyNewTool(MCPTool):
    def search(self, question: str, context: str = None) -> SearchResult:
        # Your implementation
        results = self.client.search(question)
        return SearchResult(
            content=results.content,
            sources=results.urls,
            metadata={"tool": "mynew"}
        )

    def get_info(self) -> dict:
        return {
            "name": "My New Tool",
            "cost_per_search": 0.02,
            "capabilities": ["search", "crawl"]
        }
```

### Step 2: Add to config
```yaml
mcp_tools:
  mynew:
    name: "My New Tool"
    class: "MyNewTool"
    api_key: ${MYNEW_API_KEY}
```

### Step 3: Done!
- Automatically appears in dropdown
- Automatically included in evaluations
- No other code changes needed

---

## What We're Evaluating

### Question 1: Which MCP tool is best?
Compare across all LLMs:
- Tavily average: 87/100
- Jina average: 83/100
- Firecrawl average: 81/100

**Winner: Tavily**

### Question 2: Which LLM is best?
Compare across all MCP tools:
- Claude average: 86/100
- GPT-4 average: 84/100
- Gemini average: 79/100

**Winner: Claude**

### Question 3: Best combination?
Look at specific combos:
- Tavily + Claude: 89/100 (synergy!)
- Tavily + GPT-4: 85/100
- Jina + Claude: 84/100

**Winner: Tavily + Claude**

### Question 4: Best for our use case?
Consider factors:
- Customer-facing? → Best quality (Tavily + Claude)
- Internal tool? → Best cost (Jina + GPT-4)
- High volume? → Best speed (Jina + GPT-4)

---

## Summary

**Architecture:**
- User selects MCP tool + LLM via dropdowns
- System uses exactly those components
- Real-time search per query
- Collect detailed metrics

**Goal:**
- Test all combinations
- Find best MCP tool
- Find best LLM
- Find best combination
- Make data-driven recommendation

**Extensibility:**
- Add new MCP tool: 1 file + config entry
- Add new LLM: 1 file + config entry
- Framework handles the rest

**No agent complexity** - just clean, controlled evaluation!
