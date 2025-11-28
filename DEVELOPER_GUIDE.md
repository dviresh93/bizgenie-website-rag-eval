# Developer Implementation Guide

**Last Updated**: 2025-01-26

This guide contains everything you need to implement the MCP Tool + LLM evaluation framework.

---

## Table of Contents
1. [Quick Overview](#quick-overview)
2. [Architecture](#architecture)
3. [Base Interfaces](#base-interfaces)
4. [Implementation Checklist](#implementation-checklist)
5. [AI-as-Judge Evaluation](#ai-as-judge-evaluation)
6. [Testing Workflow](#testing-workflow)
7. [Configuration](#configuration)
8. [Example Code](#example-code)

---

## Quick Overview

### What We're Building
A testing framework to evaluate MCP tool + LLM combinations:
- User picks: **MCP Tool** (Jina/Tavily) + **LLM** (Claude/GPT-4)
- System: Searches in real-time → Generates answer
- Metrics: Latency, Cost, Quality (AI-as-judge vs NotebookLLM)

### What We're Testing
```
Combinations to test:
  - Tavily + Claude
  - Tavily + GPT-4
  - Jina + Claude
  - Jina + GPT-4

For each combination, measure:
  ✅ Search latency (automated)
  ✅ LLM latency (automated)
  ✅ Search cost (automated)
  ✅ LLM cost (automated)
  ✅ Answer quality (AI-as-judge comparing to NotebookLLM baseline)
```

---

## Architecture

### System Flow
```
User selects: mcp_tool="tavily", llm_model="claude"
User asks: "What services does BizGenie offer?"
    ↓
System executes Tavily search (measure time & cost)
    ↓
Returns: fresh web content
    ↓
System calls Claude to generate answer (measure time & cost)
    ↓
Returns: answer + sources + metrics
    ↓
AI-as-Judge evaluates answer vs NotebookLLM baseline
    ↓
Store all metrics for comparison
```

### No Indexing, No ChromaDB
- **Real-time only**: Search happens per query
- **No pre-processing**: No indexing phase
- **Optional caching**: Can add later if needed

---

## Base Interfaces

### 1. MCPTool Base Class

**File**: `api/app/tools/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SearchResult:
    """Result from MCP tool search"""
    content: str              # Relevant content found
    sources: List[str]        # Source URLs
    metadata: dict            # Tool-specific metadata
    search_time: float        # Time taken (seconds)
    search_cost: float        # Cost of search

class MCPTool(ABC):
    """Base class for all MCP tools (Jina, Tavily, etc.)"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def search(self, question: str, context: Optional[str] = None) -> SearchResult:
        """
        Perform real-time search based on question.

        Args:
            question: User's question
            context: Optional context (e.g., "bizgenieai.com" to focus search)

        Returns:
            SearchResult with content, sources, and metrics
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """
        Return tool metadata.

        Returns:
            {
                "name": "Tool Name",
                "cost_per_search": 0.01,
                "capabilities": ["search", "crawl"]
            }
        """
        pass
```

### 2. LLM Base Class

**File**: `api/app/llm/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

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
    def generate(self, question: str, context: str) -> LLMResponse:
        """
        Generate answer from question and context.

        Args:
            question: User's question
            context: Search results from MCP tool

        Returns:
            LLMResponse with answer and metrics
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """
        Return model metadata.

        Returns:
            {
                "name": "Model Name",
                "cost_per_1k_tokens": 0.003,
                "max_tokens": 4096
            }
        """
        pass
```

---

## Implementation Checklist

### Phase 1: Base Classes ✅
- [ ] Create `api/app/tools/base.py` with `MCPTool` and `SearchResult`
- [ ] Create `api/app/llm/base.py` with `LLM` and `LLMResponse`

### Phase 2: MCP Tool Implementations
- [ ] **JinaTool** (`api/app/tools/jina_tool.py`)
  - Implement `search()` using Jina MCP
  - Measure search time and cost
  - Return SearchResult

- [ ] **TavilyTool** (`api/app/tools/tavily_tool.py`)
  - Implement `search()` using Tavily API
  - Measure search time and cost
  - Return SearchResult

### Phase 3: LLM Implementations
- [ ] **ClaudeLLM** (`api/app/llm/claude_llm.py`)
  - Implement `generate()` using Anthropic API
  - Measure generation time and cost
  - Return LLMResponse

- [ ] **GPT4LLM** (`api/app/llm/gpt4_llm.py`)
  - Implement `generate()` using OpenAI API
  - Measure generation time and cost
  - Return LLMResponse

### Phase 4: API Endpoints
- [ ] **Remove** `/index` endpoint (not needed)
- [ ] **Update** `/query` endpoint:
  - Accept `mcp_tool` and `llm_model` parameters
  - Execute selected MCP tool
  - Execute selected LLM
  - Return combined metrics
- [ ] **Update** `/components` endpoint:
  - Return list of available MCP tools
  - Return list of available LLMs

### Phase 5: Testing Scripts
- [ ] **collect_notebookllm_baseline.py** (mostly done, minor updates)
- [ ] **run_evaluation.py** with AI-as-judge
- [ ] **generate_comparison_report.py**

### Phase 6: UI Updates
- [ ] Remove indexing section
- [ ] Add two dropdowns: MCP Tool + LLM Model
- [ ] Display metrics breakdown (search + LLM separate)

---

## AI-as-Judge Evaluation

### Concept
Instead of manual review, use an LLM to compare answers:
- **Judge LLM**: GPT-4 or Claude (consistent, separate from test subjects)
- **Inputs**: Question, Our Answer, NotebookLLM Answer
- **Output**: Scores on accuracy, completeness, clarity

### Implementation

**File**: `scripts/ai_judge.py`

```python
import anthropic
import os

class AIJudge:
    """AI-as-judge for answer quality evaluation"""

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

    def evaluate_answer(
        self,
        question: str,
        our_answer: str,
        baseline_answer: str,
        our_sources: list,
        baseline_sources: list
    ) -> dict:
        """
        Compare our answer to NotebookLLM baseline.

        Returns:
            {
                "accuracy": 0-100,
                "completeness": 0-100,
                "clarity": 0-100,
                "source_quality": 0-100,
                "overall_quality": 0-100,
                "reasoning": "explanation"
            }
        """

        prompt = f"""You are an expert evaluator comparing two AI-generated answers.

QUESTION:
{question}

ANSWER A (Our System):
{our_answer}

Sources: {', '.join(our_sources)}

ANSWER B (NotebookLLM Baseline):
{baseline_answer}

Sources: {', '.join(baseline_sources)}

Please evaluate Answer A compared to Answer B on the following criteria:

1. ACCURACY (0-100): Is Answer A factually correct?
   - 100: Completely accurate, no errors
   - 75: Mostly accurate, minor errors
   - 50: Partially accurate, some errors
   - 25: Many errors
   - 0: Completely inaccurate

2. COMPLETENESS (0-100): Does Answer A fully address the question?
   - 100: Complete, addresses all parts
   - 75: Mostly complete, minor gaps
   - 50: Partially complete, missing important info
   - 25: Incomplete, major gaps
   - 0: Barely addresses question

3. CLARITY (0-100): Is Answer A clear and well-written?
   - 100: Excellent clarity, easy to understand
   - 75: Good clarity
   - 50: Adequate clarity
   - 25: Confusing
   - 0: Incomprehensible

4. SOURCE_QUALITY (0-100): Are Answer A's sources appropriate?
   - 100: Excellent, authoritative sources
   - 75: Good sources
   - 50: Adequate sources
   - 25: Questionable sources
   - 0: Poor or no sources

Respond in JSON format:
{
  "accuracy": <score>,
  "completeness": <score>,
  "clarity": <score>,
  "source_quality": <score>,
  "overall_quality": <average of above>,
  "reasoning": "<brief explanation of scores>"
}"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse JSON response
        import json
        result = json.loads(response.content[0].text)

        # Calculate overall quality if not provided
        if "overall_quality" not in result:
            result["overall_quality"] = (
                result["accuracy"] * 0.40 +
                result["completeness"] * 0.30 +
                result["clarity"] * 0.20 +
                result["source_quality"] * 0.10
            )

        return result
```

### Why AI-as-Judge?

**Benefits:**
- ✅ **Automated**: No manual review needed
- ✅ **Consistent**: Same criteria for all answers
- ✅ **Scalable**: Can evaluate 100s of answers
- ✅ **Objective**: No human bias
- ✅ **Fast**: Seconds per evaluation

**Cost:**
- ~$0.002 per evaluation (Claude Sonnet)
- 25 questions × 6 combinations = 150 evaluations = $0.30 total
- Very affordable!

---

## Testing Workflow

### Step 1: Collect NotebookLLM Baseline (One-time, Manual)

**Script**: `scripts/collect_notebookllm_baseline.py`

```bash
python scripts/collect_notebookllm_baseline.py
```

**What it does:**
1. Loads 25 test questions from `config/test_suites/standard_questions.json`
2. For each question, prompts you to:
   - Ask NotebookLLM the question
   - Paste NotebookLLM's answer
   - Paste sources
   - Record response time
3. Saves to: `test_results/ground_truth/notebookllm_baseline.json`

**Time**: 2-3 hours (one-time setup)

---

### Step 2: Run Automated Evaluation (Per Combination)

**Script**: `scripts/run_evaluation.py`

```bash
# Test Tavily + Claude
python scripts/run_evaluation.py --mcp tavily --llm claude

# Test Jina + GPT-4
python scripts/run_evaluation.py --mcp jina --llm gpt4
```

**What it does:**
1. Loads test questions and baseline
2. For each question:
   - Execute MCP tool search (measure time & cost)
   - Execute LLM generation (measure time & cost)
   - Get answer
   - **AI-as-Judge**: Compare answer to baseline
   - Store all metrics
3. Saves to: `test_results/{mcp}_{llm}/results.json`

**Time**: ~15-20 min per combination (fully automated!)

**Key Code:**
```python
from api.app.tools.jina_tool import JinaTool
from api.app.llm.claude_llm import ClaudeLLM
from scripts.ai_judge import AIJudge

# Initialize
mcp_tool = JinaTool(config)
llm = ClaudeLLM(config)
judge = AIJudge()

# Load baseline
baseline = load_baseline()

results = []
for question_data in test_questions:
    question = question_data["question"]

    # Step 1: MCP search
    search_result = mcp_tool.search(question, context="bizgenieai.com")

    # Step 2: LLM generation
    llm_response = llm.generate(question, search_result.content)

    # Step 3: AI-as-Judge evaluation
    baseline_answer = baseline[question_data["id"]]["answer"]
    quality_scores = judge.evaluate_answer(
        question=question,
        our_answer=llm_response.answer,
        baseline_answer=baseline_answer,
        our_sources=search_result.sources,
        baseline_sources=baseline[question_data["id"]]["sources"]
    )

    # Store everything
    results.append({
        "question": question,
        "answer": llm_response.answer,
        "sources": search_result.sources,
        "mcp_metrics": {
            "search_time": search_result.search_time,
            "search_cost": search_result.search_cost
        },
        "llm_metrics": {
            "generation_time": llm_response.generation_time,
            "generation_cost": llm_response.generation_cost,
            "tokens_used": llm_response.tokens_used
        },
        "quality_scores": quality_scores,
        "total_time": search_result.search_time + llm_response.generation_time,
        "total_cost": search_result.search_cost + llm_response.generation_cost
    })
```

---

### Step 3: Generate Comparison Report

**Script**: `scripts/generate_comparison_report.py`

```bash
python scripts/generate_comparison_report.py
```

**What it does:**
1. Loads all combination results
2. Aggregates metrics
3. Ranks combinations
4. Identifies best MCP tool, best LLM, best combination
5. Generates report

**Output**: `test_results/comparison_report.txt`

```
========================================
MCP TOOL + LLM EVALUATION REPORT
========================================

OVERALL RANKINGS (by overall_quality score):
#1  tavily + claude     Quality: 89.2, Time: 3.1s, Cost: $0.034
#2  tavily + gpt4       Quality: 86.5, Time: 2.8s, Cost: $0.029
#3  jina + claude       Quality: 84.3, Time: 2.6s, Cost: $0.022
#4  jina + gpt4         Quality: 82.1, Time: 2.3s, Cost: $0.018

MCP TOOL RANKINGS (averaged across all LLMs):
#1  Tavily    Quality: 87.9, Time: 2.0s, Cost: $0.012
#2  Jina      Quality: 83.2, Time: 1.5s, Cost: $0.00

LLM RANKINGS (averaged across all MCP tools):
#1  Claude    Quality: 86.8, Time: 1.2s, Cost: $0.023
#2  GPT-4     Quality: 84.3, Time: 1.0s, Cost: $0.019

RECOMMENDATION:
For customer-facing chatbot: Tavily + Claude (best quality)
For internal tool: Jina + GPT-4 (best value)
========================================
```

---

## Configuration

### config/configs.yaml

```yaml
# Available MCP Tools
mcp_tools:
  tavily:
    name: "Tavily AI Search"
    class: "TavilyTool"
    module: "api.app.tools.tavily_tool"
    api_key_env: "TAVILY_API_KEY"
    config:
      search_depth: "advanced"
      max_results: 5
      include_domains: ["bizgenieai.com"]  # Optional: focus on specific domain

  jina:
    name: "Jina AI Reader"
    class: "JinaTool"
    module: "api.app.tools.jina_tool"
    api_key_env: "JINA_API_KEY"
    config:
      mode: "search"

# Available LLMs
llm_models:
  claude:
    name: "Claude 3.5 Sonnet"
    class: "ClaudeLLM"
    module: "api.app.llm.claude_llm"
    api_key_env: "ANTHROPIC_API_KEY"
    config:
      model: "claude-3-5-sonnet-20241022"
      temperature: 0.7
      max_tokens: 2048

  gpt4:
    name: "GPT-4 Turbo"
    class: "GPT4LLM"
    module: "api.app.llm.gpt4_llm"
    api_key_env: "OPENAI_API_KEY"
    config:
      model: "gpt-4-turbo-preview"
      temperature: 0.7
      max_tokens: 2048

# AI Judge configuration
ai_judge:
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"

# Test configuration
testing:
  questions_file: "config/test_suites/standard_questions.json"
  baseline_file: "test_results/ground_truth/notebookllm_baseline.json"
  results_dir: "test_results"
```

### .env.example

```bash
# MCP Tool API Keys
TAVILY_API_KEY=your_tavily_key_here
JINA_API_KEY=your_jina_key_here

# LLM API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

---

## Example Code

### Example: JinaTool Implementation

**File**: `api/app/tools/jina_tool.py`

```python
import os
import time
import requests
from api.app.tools.base import MCPTool, SearchResult

class JinaTool(MCPTool):
    """Jina AI Reader MCP tool"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = os.environ.get(config.get("api_key_env", "JINA_API_KEY"))
        self.base_url = "https://r.jina.ai"

    def search(self, question: str, context: str = None) -> SearchResult:
        """Search using Jina AI Reader"""
        start_time = time.time()

        # Construct search query
        if context:
            search_query = f"{question} site:{context}"
        else:
            search_query = question

        # Call Jina API
        url = f"{self.base_url}/{search_query}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Return-Format": "markdown"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content = response.text

        # Extract sources (simplified)
        sources = self._extract_sources(content)

        search_time = time.time() - start_time
        search_cost = 0.0  # Jina is free

        return SearchResult(
            content=content,
            sources=sources,
            metadata={"tool": "jina", "query": search_query},
            search_time=search_time,
            search_cost=search_cost
        )

    def _extract_sources(self, content: str) -> list:
        """Extract URLs from Jina markdown response"""
        # Implement URL extraction from markdown
        # This is simplified - improve based on Jina's actual format
        import re
        urls = re.findall(r'https?://[^\s\)]+', content)
        return list(set(urls))[:5]  # Top 5 unique URLs

    def get_info(self) -> dict:
        return {
            "name": "Jina AI Reader",
            "cost_per_search": 0.0,
            "capabilities": ["search", "read_url"]
        }
```

### Example: ClaudeLLM Implementation

**File**: `api/app/llm/claude_llm.py`

```python
import os
import time
import anthropic
from api.app.llm.base import LLM, LLMResponse

class ClaudeLLM(LLM):
    """Claude LLM implementation"""

    def __init__(self, config: dict):
        super().__init__(config)
        api_key = os.environ.get(config.get("api_key_env", "ANTHROPIC_API_KEY"))
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = config["config"]["model"]
        self.temperature = config["config"].get("temperature", 0.7)
        self.max_tokens = config["config"].get("max_tokens", 2048)

    def generate(self, question: str, context: str) -> LLMResponse:
        """Generate answer using Claude"""
        start_time = time.time()

        prompt = f"""Based on the following information, please answer the question.

INFORMATION:
{context}

QUESTION:
{question}

Please provide a clear, accurate answer. Cite specific sources when possible."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        generation_time = time.time() - start_time

        # Calculate cost (Claude Sonnet pricing)
        input_cost = response.usage.input_tokens * 0.003 / 1000
        output_cost = response.usage.output_tokens * 0.015 / 1000
        generation_cost = input_cost + output_cost

        return LLMResponse(
            answer=answer,
            model=self.model,
            tokens_used=tokens_used,
            generation_time=generation_time,
            generation_cost=generation_cost
        )

    def get_info(self) -> dict:
        return {
            "name": "Claude 3.5 Sonnet",
            "cost_per_1k_input_tokens": 0.003,
            "cost_per_1k_output_tokens": 0.015,
            "max_tokens": 8192
        }
```

### Example: Updated /query Endpoint

**File**: `api/app/api/v1/endpoints/rag.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import importlib

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    mcp_tool: str      # e.g., "tavily", "jina"
    llm_model: str     # e.g., "claude", "gpt4"
    context: str = None  # Optional: "bizgenieai.com"

class QueryResponse(BaseModel):
    answer: str
    sources: list
    metrics: dict

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Execute query with selected MCP tool + LLM"""

    # Load configuration
    config = load_config("config/configs.yaml")

    # Get MCP tool config
    mcp_config = config["mcp_tools"].get(request.mcp_tool)
    if not mcp_config:
        raise HTTPException(404, f"MCP tool '{request.mcp_tool}' not found")

    # Get LLM config
    llm_config = config["llm_models"].get(request.llm_model)
    if not llm_config:
        raise HTTPException(404, f"LLM model '{request.llm_model}' not found")

    # Dynamically load MCP tool
    mcp_module = importlib.import_module(mcp_config["module"])
    mcp_class = getattr(mcp_module, mcp_config["class"])
    mcp_tool = mcp_class(mcp_config)

    # Dynamically load LLM
    llm_module = importlib.import_module(llm_config["module"])
    llm_class = getattr(llm_module, llm_config["class"])
    llm = llm_class(llm_config)

    # Execute search
    search_result = mcp_tool.search(request.question, request.context)

    # Generate answer
    llm_response = llm.generate(request.question, search_result.content)

    # Return combined result
    return QueryResponse(
        answer=llm_response.answer,
        sources=search_result.sources,
        metrics={
            "mcp_tool": request.mcp_tool,
            "mcp_search_time": search_result.search_time,
            "mcp_cost": search_result.search_cost,
            "llm_model": request.llm_model,
            "llm_time": llm_response.generation_time,
            "llm_cost": llm_response.generation_cost,
            "llm_tokens": llm_response.tokens_used,
            "total_time": search_result.search_time + llm_response.generation_time,
            "total_cost": search_result.search_cost + llm_response.generation_cost
        }
    )

@router.get("/components")
async def get_components():
    """Get available MCP tools and LLMs for UI dropdowns"""
    config = load_config("config/configs.yaml")

    return {
        "mcp_tools": [
            {"id": key, "name": value["name"]}
            for key, value in config["mcp_tools"].items()
        ],
        "llm_models": [
            {"id": key, "name": value["name"]}
            for key, value in config["llm_models"].items()
        ]
    }
```

---

## Summary: Do We Have Everything?

### ✅ What's Ready

**Architecture:**
- ✅ Clear system design (user picks, system executes)
- ✅ Real-time flow (no indexing)
- ✅ Base interfaces defined

**Testing:**
- ✅ AI-as-judge approach (automated quality evaluation)
- ✅ Latency measurement (automated)
- ✅ Cost calculation (automated)
- ✅ Comparison to NotebookLLM baseline

**Documentation:**
- ✅ Architecture guide
- ✅ Metrics specification
- ✅ Implementation examples
- ✅ Configuration format

### 📋 Implementation Checklist

**Developer can start with:**
1. Implement base classes (`MCPTool`, `LLM`)
2. Implement JinaTool and TavilyTool
3. Implement ClaudeLLM and GPT4LLM
4. Update `/query` endpoint
5. Implement AI-as-judge script
6. Update testing scripts
7. Update UI

**Everything is specified!** Developer has:
- Interface definitions
- Example implementations
- Configuration structure
- Testing workflow
- AI-as-judge logic

---

## Quick Start for Developer

```bash
# 1. Set up environment
cp .env.example .env
# Add API keys to .env

# 2. Implement base classes
# Follow examples in this guide

# 3. Test single query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does BizGenie offer?",
    "mcp_tool": "jina",
    "llm_model": "claude"
  }'

# 4. Collect baseline
python scripts/collect_notebookllm_baseline.py

# 5. Run evaluation
python scripts/run_evaluation.py --mcp jina --llm claude

# 6. Generate report
python scripts/generate_comparison_report.py
```

---

**Ready to build!** 🚀
