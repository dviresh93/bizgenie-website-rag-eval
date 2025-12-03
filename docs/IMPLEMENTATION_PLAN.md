# Implementation Plan: Adding Firecrawl MCP Tool

**Date:** 2025-12-01
**Status:** Ready for Implementation
**Primary Goal:** Add Firecrawl as a new MCP tool to the evaluation framework
**Secondary Goals:** Exa AI (optional), Crawl4AI (optional)
**Current State:** 4 combinations (Jina, Tavily × Claude, GPT-4)
**Target State:** 6+ combinations (add Firecrawl × Claude, GPT-4)

---

## 🎯 PRIORITY: Firecrawl Implementation (START HERE)

**Why Firecrawl First:**
- ✅ **Simple Integration:** Similar architecture to existing Jina tool (scraper-based)
- ✅ **Clear Value:** Better JavaScript handling and markdown conversion than Jina
- ✅ **Lower Risk:** Well-documented SDK, stable API
- ✅ **High Impact:** Expected to beat current winner (Jina_Claude) in quality
- ✅ **Reasonable Cost:** ~$0.004/scrape (cheaper than Jina's $0.006/scrape)

**Why NOT Exa First:**
- ⚠️ Exa has indexing issues (BizGenie site not in neural index)
- ⚠️ More complex architecture (hybrid search + retrieval)
- ⚠️ Higher cost (~$0.008/query)
- ⚠️ Requires different implementation pattern

**Implementation Time:** 2-3 hours for an AI agent
**Complexity:** LOW (follows existing Jina pattern)
**Success Probability:** VERY HIGH (95%+)

---

## 📋 AI AGENT IMPLEMENTATION GUIDE

**You are an AI agent implementing Firecrawl. Follow these steps EXACTLY in order.**

---

## 🚦 PRE-IMPLEMENTATION CHECKLIST

Before starting, verify the following:

### ✅ Step 0: Environment Verification

1. **Verify you're in the correct directory:**
   ```bash
   pwd  # Should show: /home/virus/Documents/repo/bizgenie/website-rag
   ```

2. **Verify existing tools are working:**
   ```bash
   ls -la api/app/tools/
   # Should see: base.py, jina_tool.py, tavily_tool.py, __init__.py
   ```

3. **Verify Docker is available:**
   ```bash
   docker-compose --version
   # Should show version info
   ```

4. **Check current git status:**
   ```bash
   git status
   # Note any uncommitted changes
   ```

5. **Verify you have access to Firecrawl API:**
   - You will need: `FIRECRAWL_API_KEY` environment variable
   - Get key from: https://firecrawl.dev (user should provide this)
   - Test key validity before proceeding

---

## 🎯 FIRECRAWL IMPLEMENTATION - DETAILED STEPS

### Phase 1: Add Firecrawl Dependency

**Objective:** Add Firecrawl Python SDK to project requirements

**Step 1.1: Read current requirements**
```bash
# Read the file first to understand current structure
Read api/requirements.txt
```

**Step 1.2: Add Firecrawl dependency**
- **File:** `api/requirements.txt`
- **Action:** Add this line at the end of the file (after last existing requirement)
- **Exact text to add:**
  ```
  firecrawl-py>=0.0.16
  ```
- **Important Notes:**
  - Do NOT remove any existing dependencies
  - Maintain consistent formatting (no extra blank lines)
  - Use Edit tool, NOT manual text editing
  - Version 0.0.16+ is required for latest API compatibility

**Step 1.3: Verify the change**
```bash
# Verify the line was added correctly
grep "firecrawl-py" api/requirements.txt
```

**Expected Output:**
```
firecrawl-py>=0.0.16
```

---

### Phase 2: Add API Key to Environment Template

**Objective:** Document the required environment variable for future users

**Step 2.1: Read current .env.example**
```bash
Read .env.example
```

**Step 2.2: Add Firecrawl API key placeholder**
- **File:** `.env.example`
- **Location:** After the last API key line (should be after `OPENAI_API_KEY` or similar)
- **Exact text to add:**
  ```
  FIRECRAWL_API_KEY=your_firecrawl_api_key_here
  ```
- **Important Notes:**
  - Add a blank line before if the file doesn't end with one
  - Use exact placeholder text: `your_firecrawl_api_key_here`
  - Maintain consistent formatting with other keys

**Step 2.3: Verify the change**
```bash
grep "FIRECRAWL" .env.example
```

**Expected Output:**
```
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

---

### Phase 3: Create Firecrawl Tool Implementation

**Objective:** Create a new MCP tool class that implements the MCPTool interface

**Step 3.1: Review the base interface**
```bash
# Read base.py to understand the interface contract
Read api/app/tools/base.py
```

**Step 3.2: Review existing implementation example**
```bash
# Read Jina tool as reference (similar scraper architecture)
Read api/app/tools/jina_tool.py
```

**Step 3.3: Create the Firecrawl tool file**
- **File:** `api/app/tools/firecrawl_tool.py` **(NEW FILE - use Write tool)**
- **Full implementation code:**

```python
"""Firecrawl MCP Tool Implementation

Firecrawl is an advanced web scraping service that:
- Handles JavaScript-heavy websites better than basic scrapers
- Converts web content to clean, LLM-optimized markdown
- Provides structured metadata about scraped content
- Similar architecture to Jina but with better quality output

Official Docs: https://docs.firecrawl.dev/sdks/python
"""

import os
import time
from typing import Optional
from firecrawl import FirecrawlApp
from api.app.tools.base import MCPTool, SearchResult
from api.app.core.logging import get_logger

logger = get_logger("firecrawl_tool")


class FirecrawlTool(MCPTool):
    """Firecrawl Advanced Web Scraper MCP tool

    This tool scrapes web pages using Firecrawl's API and converts them to
    clean markdown suitable for LLM processing.

    Key Features:
    - JavaScript rendering (handles dynamic content)
    - Clean markdown conversion
    - Structured metadata extraction
    - Better quality than basic HTTP scrapers

    Limitations:
    - Requires direct URL (cannot perform web search)
    - Requires valid API key
    - Paid service (~$0.004 per scrape)
    """

    def __init__(self, config: dict):
        """Initialize Firecrawl tool

        Args:
            config: Dictionary with configuration:
                - api_key_env: Name of environment variable containing API key
                             (default: "FIRECRAWL_API_KEY")

        Raises:
            ValueError: If API key is not found in environment
        """
        super().__init__(config)

        # Get API key from environment
        api_key_env = config.get("api_key_env", "FIRECRAWL_API_KEY")
        self.api_key = os.environ.get(api_key_env)

        if not self.api_key:
            raise ValueError(
                f"Firecrawl API key not found. "
                f"Please set {api_key_env} environment variable. "
                f"Get your key at: https://firecrawl.dev"
            )

        # Initialize Firecrawl client
        try:
            self.client = FirecrawlApp(api_key=self.api_key)
            logger.info("Firecrawl client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firecrawl client: {e}")
            raise

    def search(self, question: str, context: str = None) -> SearchResult:
        """Scrape content using Firecrawl

        Args:
            question: The question being asked (used for logging, not search)
            context: URL to scrape (REQUIRED - Firecrawl is a scraper, not search)

        Returns:
            SearchResult containing:
                - content: Markdown-formatted page content
                - sources: List with single URL that was scraped
                - metadata: Tool info and scrape statistics
                - search_time: Time taken to scrape in seconds
                - search_cost: Estimated cost of the scrape operation

        Raises:
            ValueError: If context URL is not provided or invalid
            Exception: If scraping fails
        """
        start_time = time.time()

        # Validate that context URL is provided
        if not context:
            raise ValueError(
                "Firecrawl requires a URL context. "
                "Please provide a URL to scrape in the 'context' parameter."
            )

        if not context.startswith("http"):
            raise ValueError(
                f"Invalid URL context: '{context}'. "
                f"URL must start with 'http://' or 'https://'"
            )

        logger.info(f"Scraping URL with Firecrawl: {context}")
        logger.info(f"Question context: {question}")

        try:
            # Scrape the URL with markdown format
            result = self.client.scrape_url(
                url=context,
                params={
                    'formats': ['markdown'],  # Request markdown output
                }
            )

            # Extract markdown content
            content = result.get('markdown', '')

            if not content:
                logger.warning(f"Firecrawl returned empty content for {context}")
                content = "No content was retrieved from the URL."

            # Firecrawl scrapes a single URL, so sources is just that URL
            sources = [context]

            # Log success
            content_length = len(content)
            logger.info(
                f"Firecrawl scrape successful. "
                f"Content length: {content_length} characters"
            )

            # Build metadata
            metadata = {
                "tool": "firecrawl",
                "url": context,
                "content_length": content_length,
                "success": True
            }

            # Add any additional metadata from Firecrawl response
            if 'metadata' in result:
                metadata['firecrawl_metadata'] = result['metadata']

        except Exception as e:
            logger.error(f"Firecrawl scrape failed for {context}: {e}")
            # Re-raise with more context
            raise Exception(f"Firecrawl scraping error: {str(e)}") from e

        # Calculate time taken
        search_time = time.time() - start_time
        logger.info(f"Scrape completed in {search_time:.2f} seconds")

        # Return structured result
        return SearchResult(
            content=content,
            sources=sources,
            metadata=metadata,
            search_time=search_time,
            search_cost=0.004  # Estimated cost per scrape
        )

    def get_info(self) -> dict:
        """Get information about this tool

        Returns:
            Dictionary with tool metadata for reporting and analysis
        """
        return {
            "name": "Firecrawl",
            "type": "web_scraper",
            "cost_per_search": 0.004,
            "capabilities": [
                "scrape",
                "javascript_rendering",
                "markdown_conversion",
                "metadata_extraction"
            ],
            "limitations": [
                "requires_url",
                "no_search_capability",
                "paid_service"
            ],
            "api_docs": "https://docs.firecrawl.dev/sdks/python"
        }
```

**Step 3.4: Verify file creation**
```bash
# Check that file was created
ls -la api/app/tools/firecrawl_tool.py
# Should show the new file with ~200+ lines

# Verify it's valid Python
python3 -m py_compile api/app/tools/firecrawl_tool.py
# Should have no output (no syntax errors)
```

**Step 3.5: Check for import errors**
```bash
# Try importing the module (will fail if dependencies missing, but structure should be OK)
docker-compose exec api python3 -c "from api.app.tools.firecrawl_tool import FirecrawlTool; print('Import successful')"
```

---

### Phase 4: Update Evaluation Script Integration

**Objective:** Register Firecrawl tool in the evaluation runner so it can be selected and used

**Step 4.1: Read the current evaluation script**
```bash
Read scripts/run_evaluation.py
```

**Step 4.2: Add Firecrawl import**
- **File:** `scripts/run_evaluation.py`
- **Location:** In the imports section (around line 11-13), after existing tool imports
- **Find this code:**
  ```python
  from api.app.tools.jina_tool import JinaTool
  from api.app.tools.tavily_tool import TavilyTool
  ```
- **Add this line after it:**
  ```python
  from api.app.tools.firecrawl_tool import FirecrawlTool
  ```

**Step 4.3: Update CLI argument choices**
- **File:** `scripts/run_evaluation.py`
- **Location:** In the argument parser setup (around line 23-25)
- **Find this code:**
  ```python
  parser.add_argument("--mcp", required=True, choices=["jina", "tavily"], help="MCP Tool to test")
  ```
- **Replace with:**
  ```python
  parser.add_argument("--mcp", required=True, choices=["jina", "tavily", "firecrawl"], help="MCP Tool to test")
  ```

**Step 4.4: Add tool instantiation logic**
- **File:** `scripts/run_evaluation.py`
- **Location:** In the tool selection logic (around line 36-40)
- **Find this code:**
  ```python
  if args.mcp == "jina":
      mcp_tool = JinaTool({"api_key_env": "JINA_API_KEY"})
  else:
      mcp_tool = TavilyTool({"api_key_env": "TAVILY_API_KEY", "config": {"search_depth": "advanced"}})
  ```
- **Replace with:**
  ```python
  if args.mcp == "jina":
      mcp_tool = JinaTool({"api_key_env": "JINA_API_KEY"})
  elif args.mcp == "tavily":
      mcp_tool = TavilyTool({"api_key_env": "TAVILY_API_KEY", "config": {"search_depth": "advanced"}})
  elif args.mcp == "firecrawl":
      mcp_tool = FirecrawlTool({"api_key_env": "FIRECRAWL_API_KEY"})
  else:
      raise ValueError(f"Unknown MCP tool: {args.mcp}")
  ```

**Step 4.5: Verify changes**
```bash
# Check that all edits were applied
grep -n "FirecrawlTool" scripts/run_evaluation.py
# Should show import line and instantiation line

grep -n "firecrawl" scripts/run_evaluation.py
# Should show multiple matches in choices and elif
```

---

### Phase 5: Update Benchmark Script

**Objective:** Add Firecrawl combinations to the parallel benchmark runner

**Step 5.1: Read the benchmark script**
```bash
Read scripts/run_benchmark.sh
```

**Step 5.2: Add Firecrawl to combinations array**
- **File:** `scripts/run_benchmark.sh`
- **Location:** In the combinations array (around line 20-25)
- **Find this code:**
  ```bash
  declare -a combinations=(
      "tavily claude"
      "tavily gpt4"
      "jina claude"
      "jina gpt4"
  )
  ```
- **Replace with:**
  ```bash
  declare -a combinations=(
      "tavily claude"
      "tavily gpt4"
      "jina claude"
      "jina gpt4"
      "firecrawl claude"
      "firecrawl gpt4"
  )
  ```

**Step 5.3: Verify change**
```bash
grep -A 8 "declare -a combinations" scripts/run_benchmark.sh
# Should show all 6 combinations including firecrawl
```

---

### Phase 6: Build and Test

**Objective:** Build Docker container with new dependencies and run tests

**Step 6.1: Rebuild Docker container**
```bash
# Stop existing containers
docker-compose down

# Rebuild with new firecrawl-py dependency
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Verify containers are running
docker-compose ps
# Should show 'api' and 'chromadb' containers running
```

**Step 6.2: Verify Firecrawl SDK installed**
```bash
# Check that firecrawl-py is installed
docker-compose exec api pip list | grep firecrawl
# Should show: firecrawl-py    0.0.16 (or higher)
```

**Step 6.3: Set up API key**
- **IMPORTANT:** Before testing, ensure you have:
  1. Created a `.env` file (copy from `.env.example`)
  2. Added your actual Firecrawl API key: `FIRECRAWL_API_KEY=fc-xxx...`
  3. Restarted containers: `docker-compose restart api`

**Step 6.4: Run single test (Firecrawl + Claude)**
```bash
# Test Firecrawl with Claude on 25 questions
docker-compose exec api python3 scripts/run_evaluation.py --mcp firecrawl --llm claude

# Expected output:
# - "Firecrawl client initialized successfully"
# - "Scraping URL with Firecrawl: https://bizgenieai.com"
# - Progress through 25 questions
# - Files created in test_results/firecrawl_claude/
```

**Expected files created:**
- `test_results/firecrawl_claude/results_[TIMESTAMP].json` (performance metrics)
- `test_results/firecrawl_claude/eval_[TIMESTAMP].json` (quality scores)

**Step 6.5: Run single test (Firecrawl + GPT-4)**
```bash
# Test Firecrawl with GPT-4
docker-compose exec api python3 scripts/run_evaluation.py --mcp firecrawl --llm gpt4

# Expected files:
# - test_results/firecrawl_gpt4/results_[TIMESTAMP].json
# - test_results/firecrawl_gpt4/eval_[TIMESTAMP].json
```

**Step 6.6: Run full benchmark (all 6 combinations)**
```bash
# Run all combinations in parallel
docker-compose exec api bash scripts/run_benchmark.sh

# Expected output:
# - Launches 6 parallel processes
# - Each completes in 3-5 minutes
# - Generates comparison report
```

**Expected final output:**
- `test_results/benchmark_report_[TIMESTAMP].md` with 6 combinations

---

### Phase 7: Validation and Quality Checks

**Objective:** Verify implementation quality and correctness

**Step 7.1: Check test results structure**
```bash
# Verify directory structure
ls -la test_results/firecrawl_claude/
ls -la test_results/firecrawl_gpt4/

# Each should contain:
# - results_*.json
# - eval_*.json
```

**Step 7.2: Inspect results file**
```bash
# Check a results file
cat test_results/firecrawl_claude/results_*.json | python3 -m json.tool | head -50

# Verify it contains:
# - "tool": "firecrawl"
# - "llm": "claude"
# - "avg_search_time": <number>
# - "total_cost": <number>
# - "results": [array of 25 items]
```

**Step 7.3: Inspect evaluation file**
```bash
# Check an eval file
cat test_results/firecrawl_claude/eval_*.json | python3 -m json.tool | head -50

# Verify it contains:
# - "overall_quality_score": <number between 0-100>
# - "hallucination_count": <number>
# - "evaluations": [array of 25 items]
```

**Step 7.4: Review benchmark report**
```bash
# Read the latest comparison report
cat test_results/benchmark_report_*.md

# Should show:
# - 6 combinations (tavily×2, jina×2, firecrawl×2)
# - Comparison table with quality scores
# - Performance metrics for each
# - Cost analysis
```

**Step 7.5: Verify Firecrawl performance**

**Expected results for Firecrawl:**
- **Quality Score:** 73-78 (should beat Jina's 72.6)
- **Average Time:** 7-10 seconds (similar to Jina)
- **Cost per Query:** ~$0.016 (Firecrawl $0.004 + LLM cost)
- **Hallucinations:** 0-1 (should be minimal)

**Key comparisons:**
- Firecrawl vs Jina: Firecrawl should have +2-5 points in quality
- Firecrawl vs Tavily: Firecrawl should have better completeness
- Firecrawl_Claude vs Firecrawl_GPT4: Claude should be +6-8 points higher

---

### Phase 8: Error Handling and Troubleshooting

**Common issues and solutions:**

#### Issue 1: "Firecrawl API key not found"
**Error:**
```
ValueError: Firecrawl API key not found. Please set FIRECRAWL_API_KEY environment variable.
```
**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify key is set
grep FIRECRAWL_API_KEY .env

# If missing, add it:
echo "FIRECRAWL_API_KEY=fc-your-key-here" >> .env

# Restart containers
docker-compose restart api
```

#### Issue 2: "Module 'firecrawl' not found"
**Error:**
```
ModuleNotFoundError: No module named 'firecrawl'
```
**Solution:**
```bash
# Rebuild Docker container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify installation
docker-compose exec api pip list | grep firecrawl
```

#### Issue 3: "Firecrawl requires a URL context"
**Error:**
```
ValueError: Firecrawl requires a URL context. Please provide a URL to scrape.
```
**Solution:**
- This is expected behavior - Firecrawl is a scraper, not a search tool
- Verify that `standard_questions.json` includes `"context"` field with URL
- Check: `cat config/test_suites/standard_questions.json | grep context`

#### Issue 4: Empty or poor quality results
**Symptoms:**
- Quality score < 50
- Many "No content retrieved" messages
**Solution:**
```bash
# Test Firecrawl API directly
docker-compose exec api python3 << 'EOF'
from firecrawl import FirecrawlApp
import os
client = FirecrawlApp(api_key=os.environ['FIRECRAWL_API_KEY'])
result = client.scrape_url('https://bizgenieai.com', params={'formats': ['markdown']})
print(f"Content length: {len(result.get('markdown', ''))}")
print(result.get('markdown', '')[:500])
EOF

# Should show markdown content
```

#### Issue 5: Slow performance (>15 seconds per query)
**Symptoms:**
- Average search time > 15 seconds
- Benchmark taking >10 minutes
**Solution:**
```bash
# Check if it's Firecrawl or LLM slowness
# Look at individual timing in results:
cat test_results/firecrawl_claude/results_*.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"Avg search time: {data['avg_search_time']:.2f}s\")
print(f\"Avg generation time: {data['avg_generation_time']:.2f}s\")
"

# If search time > 10s: Firecrawl API may be slow (check their status)
# If generation time > 10s: LLM is slow (expected for Claude Opus)
```

---

## 🎯 SUCCESS CRITERIA

After completing all phases, verify:

- [ ] ✅ `firecrawl-py>=0.0.16` added to `api/requirements.txt`
- [ ] ✅ `FIRECRAWL_API_KEY` added to `.env.example`
- [ ] ✅ New file `api/app/tools/firecrawl_tool.py` created (~200 lines)
- [ ] ✅ `scripts/run_evaluation.py` updated with Firecrawl import and logic
- [ ] ✅ `scripts/run_benchmark.sh` includes "firecrawl claude" and "firecrawl gpt4"
- [ ] ✅ Docker build completes without errors
- [ ] ✅ Single test runs successfully: `--mcp firecrawl --llm claude`
- [ ] ✅ Benchmark report shows 6 combinations (not just 4)
- [ ] ✅ Firecrawl quality score is competitive (>70)
- [ ] ✅ No Python import errors or exceptions
- [ ] ✅ Test results files created in correct directories
- [ ] ✅ Benchmark completes in <10 minutes

---

## 📊 FINAL DELIVERABLES

After successful implementation, you should have:

### Files Modified
1. ✅ `api/requirements.txt` - Added `firecrawl-py>=0.0.16`
2. ✅ `.env.example` - Added `FIRECRAWL_API_KEY=...`
3. ✅ `scripts/run_evaluation.py` - Added Firecrawl import and instantiation
4. ✅ `scripts/run_benchmark.sh` - Added 2 new Firecrawl combinations

### Files Created
5. ✅ `api/app/tools/firecrawl_tool.py` - Complete Firecrawl tool implementation (~200 lines)

### Test Results Generated
6. ✅ `test_results/firecrawl_claude/results_[TIMESTAMP].json`
7. ✅ `test_results/firecrawl_claude/eval_[TIMESTAMP].json`
8. ✅ `test_results/firecrawl_gpt4/results_[TIMESTAMP].json`
9. ✅ `test_results/firecrawl_gpt4/eval_[TIMESTAMP].json`
10. ✅ `test_results/benchmark_report_[TIMESTAMP].md` - Updated with 6 combinations

### Performance Metrics to Report
- Overall Quality Score (Firecrawl_Claude vs Jina_Claude)
- Average Search Time
- Total Cost per Query
- Hallucination Count
- Top 3 performing combinations

---

## 🎓 LEARNING OUTCOMES

After completing this implementation, the AI agent should understand:

1. **MCP Tool Pattern**: How to implement the MCPTool interface
2. **Integration Points**: Where tools are registered in the evaluation system
3. **API Integration**: How to wrap third-party SDKs into the framework
4. **Error Handling**: Proper validation and error messages
5. **Testing Strategy**: Single test → Full benchmark progression
6. **Docker Workflow**: Build → Deploy → Test cycle

---

## 📝 POST-IMPLEMENTATION TASKS

After Firecrawl is successfully implemented and tested:

### 1. Commit Changes
```bash
git add api/requirements.txt
git add .env.example
git add api/app/tools/firecrawl_tool.py
git add scripts/run_evaluation.py
git add scripts/run_benchmark.sh
git status
git commit -m "feat: Add Firecrawl MCP tool integration

- Add firecrawl-py SDK dependency
- Implement FirecrawlTool with full error handling
- Update evaluation script to support firecrawl option
- Add firecrawl combinations to benchmark suite
- Update environment template with FIRECRAWL_API_KEY

Expected improvement: +2-5 points quality over Jina_Claude"
```

### 2. Update Documentation
- [ ] Update README.md with Firecrawl description
- [ ] Add Firecrawl to architecture diagrams
- [ ] Document Firecrawl setup in Getting Started
- [ ] Add benchmark results to README

### 3. Share Results
- Create summary comparison showing:
  - Quality: Firecrawl_Claude vs Jina_Claude
  - Speed: Firecrawl_GPT4 vs Jina_GPT4
  - Cost: All 6 combinations ranked
  - Recommendation: Best overall combination

---

## 📋 ARCHITECTURE REFERENCE

### Current MCP Tool Interface

**Base Class:** `api/app/tools/base.py`
```python
class MCPTool(ABC):
    def __init__(self, config: dict)
    def search(question: str, context: str = None) -> SearchResult
    def get_info() -> dict
```

**SearchResult** dataclass:
- `content`: str (main content for LLM)
- `sources`: List[str] (URLs)
- `metadata`: dict (tool-specific data)
- `search_time`: float
- `search_cost`: float

### Tools Currently Implemented
1. **Jina AI Reader** - HTTP-based web scraper
2. **Tavily AI Search** - AI-powered search engine
3. **Firecrawl** (NEW) - Advanced web scraper with JS rendering

### Integration Pattern
1. Create tool class in `api/app/tools/[tool_name]_tool.py`
2. Implement `MCPTool` interface
3. Import in `scripts/run_evaluation.py`
4. Add to CLI choices
5. Add instantiation logic
6. Update benchmark combinations

---

## 🚀 SEMANTIC CACHE IMPLEMENTATION (PRIORITY AFTER FIRECRAWL)

**Objective:** Add hybrid semantic caching to measure and optimize real-world performance with ChromaDB

**Why Implement Caching:**
- ✅ **Realistic Performance Testing:** Simulates production scenario with repeated/similar queries
- ✅ **Cost Optimization:** 70-85% reduction in API costs for cached queries
- ✅ **Performance Measurement:** Enables accurate benchmarking of cache hit rates
- ✅ **Semantic Matching:** Handles question variations (paraphrasing)
- ✅ **Uses Existing Stack:** ChromaDB already running, no new dependencies

**Implementation Time:** 3-4 hours for an AI agent
**Complexity:** MEDIUM (semantic similarity, two-tier lookup)
**Prerequisites:** Firecrawl implementation completed

---

### Cache Architecture Overview

**Two-Tier Hybrid Cache Using ChromaDB:**

**Tier 1: Exact Match (Fast - 10-20ms)**
- Uses metadata filtering on `cache_key` hash
- Perfect for repeated identical questions
- Expected hit rate: 60-70% in tests, 40-50% in production

**Tier 2: Semantic Match (Slower - 30-50ms)**
- Uses vector similarity search with embeddings
- Handles paraphrased/similar questions
- Expected hit rate: 15-25% additional coverage
- Similarity threshold: 0.90 (configurable)

**Tier 3: Cache Miss (Slowest - 8000-10000ms)**
- Fresh API calls to MCP tool + LLM
- Store result in cache for future hits
- Expected: 15-20% of queries

**Combined Expected Performance:**
- Total hit rate: 75-85%
- Average response time: ~2-3s (vs 9-10s uncached)
- Cost reduction: 75-85%

---

### Phase 1: Create Semantic Cache Manager

**Objective:** Build the cache service that interfaces with ChromaDB

**Step 1.1: Create the cache manager file**

**File:** `api/app/services/semantic_cache.py` **(NEW FILE - use Write tool)**

**Full implementation (copy exactly):**

```python
"""
Semantic Cache Manager using ChromaDB

Implements two-tier caching:
1. Exact match (via metadata filtering) - Fast ~10-20ms
2. Semantic match (via vector similarity) - Slower ~30-50ms

Uses existing ChromaDB instance - no new dependencies!
"""
import hashlib
import json
import time
from typing import Optional, Dict, Tuple
from openai import OpenAI
import chromadb
from api.app.core.logging import get_logger

logger = get_logger("semantic_cache")


class SemanticCacheManager:
    """Hybrid cache using ChromaDB for exact and semantic matching"""

    def __init__(self,
                 chroma_host: str = "chromadb",
                 chroma_port: int = 8000,
                 embedding_model: str = "text-embedding-3-small",
                 semantic_threshold: float = 0.90):
        """
        Initialize semantic cache

        Args:
            chroma_host: ChromaDB host from docker-compose
            chroma_port: ChromaDB port (default 8000)
            embedding_model: OpenAI embedding model
            semantic_threshold: Min similarity for semantic match (0-1)
        """
        logger.info(f"Connecting to ChromaDB at {chroma_host}:{chroma_port}")
        self.chroma_client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port
        )

        # Create cache collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="search_cache",
            metadata={"description": "Semantic cache for search results"}
        )

        # OpenAI for embeddings
        import os
        self.openai_client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.embedding_model = embedding_model
        self.semantic_threshold = semantic_threshold

        # Statistics
        self.stats = {
            'exact_hits': 0,
            'semantic_hits': 0,
            'misses': 0,
            'total_queries': 0,
            'embedding_time': 0.0,
            'lookup_time': 0.0
        }

    def _generate_embedding(self, text: str) -> list:
        """Generate embedding vector"""
        start = time.time()
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        self.stats['embedding_time'] += time.time() - start
        return response.data[0].embedding

    def _make_cache_key(self, tool: str, question: str, context: str) -> str:
        """Create unique cache key"""
        combined = f"{tool}|{question}|{context}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def get_cached_search(self,
                         tool: str,
                         question: str,
                         context: str) -> Tuple[Optional[Dict], str, float]:
        """
        Get cached search with hybrid lookup

        Returns:
            (cached_data, match_type, lookup_time)
            match_type: 'exact', 'semantic', or 'miss'
        """
        start_time = time.time()
        self.stats['total_queries'] += 1

        # Generate embedding
        try:
            question_embedding = self._generate_embedding(question)
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return None, 'miss', time.time() - start_time

        cache_key = self._make_cache_key(tool, question, context)

        # TIER 1: Exact match
        try:
            exact_results = self.collection.query(
                query_embeddings=[question_embedding],
                where={"cache_key": cache_key},
                n_results=1
            )

            if exact_results['ids'][0]:
                cached_data = json.loads(exact_results['documents'][0][0])
                lookup_time = time.time() - start_time
                self.stats['exact_hits'] += 1
                self.stats['lookup_time'] += lookup_time

                logger.info(f"✅ EXACT hit ({lookup_time*1000:.1f}ms)")
                return cached_data, 'exact', lookup_time

        except Exception as e:
            logger.warning(f"Exact lookup failed: {e}")

        # TIER 2: Semantic match
        try:
            semantic_results = self.collection.query(
                query_embeddings=[question_embedding],
                where={"tool": tool, "context": context},
                n_results=3
            )

            if semantic_results['ids'][0]:
                for i, distance in enumerate(semantic_results['distances'][0]):
                    similarity = 1 - distance

                    if similarity >= self.semantic_threshold:
                        cached_data = json.loads(
                            semantic_results['documents'][0][i]
                        )
                        original_q = semantic_results['metadatas'][0][i]['question']
                        lookup_time = time.time() - start_time

                        self.stats['semantic_hits'] += 1
                        self.stats['lookup_time'] += lookup_time

                        logger.info(
                            f"🔍 SEMANTIC hit ({lookup_time*1000:.1f}ms, "
                            f"sim={similarity:.2%})\n"
                            f"   Original: {original_q}\n"
                            f"   Current:  {question}"
                        )

                        cached_data['_cache_metadata'] = {
                            'match_type': 'semantic',
                            'similarity': similarity,
                            'original_question': original_q
                        }
                        return cached_data, 'semantic', lookup_time

        except Exception as e:
            logger.warning(f"Semantic lookup failed: {e}")

        # TIER 3: Miss
        lookup_time = time.time() - start_time
        self.stats['misses'] += 1
        self.stats['lookup_time'] += lookup_time
        logger.info(f"❌ Cache miss ({lookup_time*1000:.1f}ms)")

        return None, 'miss', lookup_time

    def store_search_result(self,
                           tool: str,
                           question: str,
                           context: str,
                           search_result: Dict):
        """Store search result in cache"""
        try:
            question_embedding = self._generate_embedding(question)
            cache_key = self._make_cache_key(tool, question, context)

            metadata = {
                "cache_key": cache_key,
                "tool": tool,
                "question": question,
                "context": context,
                "timestamp": time.time()
            }

            self.collection.add(
                embeddings=[question_embedding],
                documents=[json.dumps(search_result)],
                metadatas=[metadata],
                ids=[cache_key]
            )

            logger.info(f"💾 Cached: {question[:60]}...")

        except Exception as e:
            logger.error(f"Cache store failed: {e}")

    def get_stats(self) -> Dict:
        """Get cache performance stats"""
        total = self.stats['total_queries']
        if total == 0:
            return {
                **self.stats,
                'hit_rate': 0.0,
                'exact_rate': 0.0,
                'semantic_rate': 0.0
            }

        total_hits = self.stats['exact_hits'] + self.stats['semantic_hits']

        return {
            **self.stats,
            'hit_rate': total_hits / total,
            'exact_rate': self.stats['exact_hits'] / total,
            'semantic_rate': self.stats['semantic_hits'] / total,
            'miss_rate': self.stats['misses'] / total,
            'avg_lookup_time': self.stats['lookup_time'] / total,
            'avg_embedding_time': self.stats['embedding_time'] / total
        }

    def clear_cache(self):
        """Clear all cache"""
        self.chroma_client.delete_collection("search_cache")
        self.collection = self.chroma_client.get_or_create_collection(
            name="search_cache",
            metadata={"description": "Semantic cache for search results"}
        )
        logger.info("🗑️  Cache cleared")

    def get_cache_size(self) -> int:
        """Get cached item count"""
        return self.collection.count()
```

**Step 1.2: Verify file creation**
```bash
ls -la api/app/services/semantic_cache.py
# Should show ~250 lines

python3 -m py_compile api/app/services/semantic_cache.py
# Should compile without errors
```

---

### Phase 2: Integrate Cache into Evaluation Pipeline

**Objective:** Modify run_evaluation.py to use caching with optional enable/disable flag

**Step 2.1: Add cache import and initialization**

**File:** `scripts/run_evaluation.py`

**Add after line 17 (after other imports):**
```python
from api.app.services.semantic_cache import SemanticCacheManager
```

**Add argument for cache control (around line 28):**
```python
parser.add_argument("--cache", action="store_true",
                    help="Enable semantic caching (default: disabled)")
parser.add_argument("--cache-threshold", type=float, default=0.90,
                    help="Semantic similarity threshold (0-1, default: 0.90)")
```

**Initialize cache manager (after line 61, after judge init):**
```python
# Initialize Cache (optional)
cache_manager = None
if args.cache:
    print(f"Initializing semantic cache (threshold={args.cache_threshold})...")
    cache_manager = SemanticCacheManager(semantic_threshold=args.cache_threshold)
    print(f"Cache size: {cache_manager.get_cache_size()} items")
```

**Step 2.2: Wrap search with cache lookup**

**Replace lines 87-95 (search logic) with:**
```python
# Search (with optional caching)
start_search = time.time()
cache_hit = False
cache_type = 'miss'

try:
    # Try cache first if enabled
    if cache_manager:
        cached_result, cache_type, cache_lookup_time = cache_manager.get_cached_search(
            tool=args.mcp,
            question=question_text,
            context=target_url
        )

        if cached_result:
            # Cache hit - reconstruct SearchResult
            search_res = SearchResult(**cached_result)
            search_time = cache_lookup_time
            cache_hit = True
            print(f"   💾 Cache {cache_type.upper()} ({search_time*1000:.1f}ms)")
        else:
            # Cache miss - fetch fresh
            search_res = mcp_tool.search(question_text, context=target_url)
            search_time = time.time() - start_search

            # Store in cache
            cache_manager.store_search_result(
                tool=args.mcp,
                question=question_text,
                context=target_url,
                search_result=search_res.__dict__
            )
            print(f"   🔍 Fresh search ({search_time:.2f}s) - cached for future")
    else:
        # No caching - direct search
        search_res = mcp_tool.search(question_text, context=target_url)
        search_time = time.time() - start_search
        print(f"   ✓ Search found {len(search_res.sources)} sources ({search_time:.2f}s)")

except Exception as e:
    print(f"   ❌ Search failed: {e}")
    continue
```

**Step 2.3: Add cache metadata to results**

**Modify result_entry (around line 117):**
```python
result_entry = {
    "question_id": qid,
    "question": question_text,
    "answer": llm_res.answer,
    "sources": search_res.sources,
    "cache_hit": cache_hit,  # NEW
    "cache_type": cache_type,  # NEW
    "metrics": {
        "search_time": search_time,
        "gen_time": gen_time,
        "total_time": search_time + gen_time,
        "tokens": llm_res.tokens_used,
        "search_cost": getattr(search_res, 'search_cost', 0.0),
        "gen_cost": getattr(llm_res, 'generation_cost', 0.0)
    }
}
```

**Step 2.4: Print cache statistics at end**

**Add before line 145 (before "Execution complete"):**
```python
# Print cache statistics
if cache_manager:
    print("\n" + "="*60)
    print("📊 CACHE PERFORMANCE STATISTICS")
    print("="*60)

    stats = cache_manager.get_stats()
    print(f"Total Queries:     {stats['total_queries']}")
    print(f"Exact Hits:        {stats['exact_hits']} ({stats['exact_rate']:.1%})")
    print(f"Semantic Hits:     {stats['semantic_hits']} ({stats['semantic_rate']:.1%})")
    print(f"Cache Misses:      {stats['misses']} ({stats['miss_rate']:.1%})")
    print(f"Overall Hit Rate:  {stats['hit_rate']:.1%}")
    print(f"Avg Lookup Time:   {stats['avg_lookup_time']*1000:.1f}ms")
    print(f"Cache Size:        {cache_manager.get_cache_size()} items")
    print("="*60)
```

---

### Phase 3: Create Focused Cache Testing Script

**Objective:** Build dedicated test to measure cache performance in isolation

**Step 3.1: Create cache test script**

**File:** `scripts/test_cache_performance.py` **(NEW FILE)**

```python
"""
Cache Performance Testing Script

Tests cache behavior with:
1. Exact match performance
2. Semantic similarity matching
3. Cold vs warm cache comparison
4. Cache hit rate analysis
"""
import sys
import os
import json
import time
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from api.app.services.semantic_cache import SemanticCacheManager
from api.app.tools.jina_tool import JinaTool


def test_exact_matching():
    """Test 1: Exact match performance"""
    print("\n" + "="*60)
    print("TEST 1: Exact Match Performance")
    print("="*60)

    cache = SemanticCacheManager()
    cache.clear_cache()

    tool = JinaTool({"api_key_env": "JINA_API_KEY"})
    question = "What services does BizGenie provide?"
    context = "https://bizgenieai.com"

    # Run 1: Cache miss (cold)
    print("\n[Run 1] Cold cache...")
    start = time.time()
    result, match_type, lookup_time = cache.get_cached_search("jina", question, context)
    print(f"Result: {match_type}, Time: {lookup_time*1000:.1f}ms")

    if match_type == 'miss':
        # Fetch and store
        search_res = tool.search(question, context)
        cache.store_search_result("jina", question, context, search_res.__dict__)
        print(f"Stored in cache")

    # Run 2: Cache hit (warm - exact)
    print("\n[Run 2] Warm cache (exact match)...")
    start = time.time()
    result, match_type, lookup_time = cache.get_cached_search("jina", question, context)
    print(f"Result: {match_type}, Time: {lookup_time*1000:.1f}ms")

    assert match_type == 'exact', "Should be exact match!"
    assert lookup_time < 0.1, "Should be <100ms!"

    print("\n✅ Exact matching works! Speed: {:.1f}ms".format(lookup_time*1000))


def test_semantic_matching():
    """Test 2: Semantic similarity matching"""
    print("\n" + "="*60)
    print("TEST 2: Semantic Similarity Matching")
    print("="*60)

    cache = SemanticCacheManager(semantic_threshold=0.85)
    cache.clear_cache()

    tool = JinaTool({"api_key_env": "JINA_API_KEY"})
    context = "https://bizgenieai.com"

    # Original question
    original_q = "What services does BizGenie provide to businesses?"
    search_res = tool.search(original_q, context)
    cache.store_search_result("jina", original_q, context, search_res.__dict__)
    print(f"Cached original: {original_q}")

    # Similar questions (paraphrased)
    similar_questions = [
        "What does BizGenie offer to companies?",  # High similarity
        "Tell me about BizGenie's services",       # High similarity
        "BizGenie service offerings?",             # Medium similarity
        "What can BizGenie do?",                   # Medium similarity
        "How much does BizGenie cost?"             # Low similarity (should miss)
    ]

    print("\nTesting similar questions:")
    for q in similar_questions:
        result, match_type, lookup_time = cache.get_cached_search("jina", q, context)

        if match_type == 'semantic':
            metadata = result.get('_cache_metadata', {})
            similarity = metadata.get('similarity', 0)
            print(f"  ✅ {q}")
            print(f"     Match: {match_type}, Similarity: {similarity:.2%}, "
                  f"Time: {lookup_time*1000:.1f}ms")
        else:
            print(f"  ❌ {q}")
            print(f"     Match: {match_type} (expected semantic)")

    stats = cache.get_stats()
    print(f"\nSemantic hit rate: {stats['semantic_rate']:.1%}")


def test_cache_scaling():
    """Test 3: Cache scaling with multiple queries"""
    print("\n" + "="*60)
    print("TEST 3: Cache Scaling (25 Questions)")
    print("="*60)

    cache = SemanticCacheManager()
    cache.clear_cache()

    # Load standard questions
    project_root = Path(__file__).parent.parent
    questions_path = project_root / "config/test_suites/standard_questions.json"

    with open(questions_path) as f:
        questions = json.load(f)

    tool = JinaTool({"api_key_env": "JINA_API_KEY"})
    context = "https://bizgenieai.com"

    print("\n[Round 1] Cold cache - all misses expected")
    round1_times = []
    for q in questions[:5]:  # Test with 5 questions
        result, match_type, lookup_time = cache.get_cached_search(
            "jina", q["question"], context
        )

        if match_type == 'miss':
            search_res = tool.search(q["question"], context)
            cache.store_search_result("jina", q["question"], context,
                                     search_res.__dict__)

        round1_times.append(lookup_time)

    stats1 = cache.get_stats()
    print(f"Hit rate: {stats1['hit_rate']:.1%}")
    print(f"Avg time: {sum(round1_times)/len(round1_times)*1000:.1f}ms")

    print("\n[Round 2] Warm cache - all hits expected")
    round2_times = []
    for q in questions[:5]:
        result, match_type, lookup_time = cache.get_cached_search(
            "jina", q["question"], context
        )
        round2_times.append(lookup_time)

    stats2 = cache.get_stats()
    print(f"Hit rate: {stats2['hit_rate']:.1%}")
    print(f"Avg time: {sum(round2_times)/len(round2_times)*1000:.1f}ms")

    # Calculate speedup
    speedup = sum(round1_times) / sum(round2_times)
    print(f"\n🚀 Speedup: {speedup:.1f}x faster with cache!")


def test_production_simulation():
    """Test 4: Simulate production workload"""
    print("\n" + "="*60)
    print("TEST 4: Production Workload Simulation")
    print("="*60)

    cache = SemanticCacheManager()
    cache.clear_cache()

    # Simulate user queries with repetition and variation
    user_queries = [
        # User 1: Asks about services (repeated)
        ("User1", "What does BizGenie do?"),
        ("User1", "What services does BizGenie offer?"),  # Similar

        # User 2: Asks about pricing
        ("User2", "How much does BizGenie cost?"),
        ("User2", "What are the pricing plans?"),  # Similar

        # User 3: Repeats user 1's question (exact)
        ("User3", "What does BizGenie do?"),  # Should hit cache

        # User 4: New unique question
        ("User4", "Does BizGenie integrate with Salesforce?"),

        # User 5: Repeats pricing (exact)
        ("User5", "How much does BizGenie cost?"),  # Should hit cache
    ]

    tool = JinaTool({"api_key_env": "JINA_API_KEY"})
    context = "https://bizgenieai.com"

    print("\nSimulating user queries:")
    for user, question in user_queries:
        result, match_type, lookup_time = cache.get_cached_search(
            "jina", question, context
        )

        if match_type == 'miss':
            search_res = tool.search(question, context)
            cache.store_search_result("jina", question, context,
                                     search_res.__dict__)

        print(f"  [{user}] {question[:40]}...")
        print(f"    → {match_type.upper()} ({lookup_time*1000:.1f}ms)")

    stats = cache.get_stats()
    print(f"\nProduction Stats:")
    print(f"  Total queries: {stats['total_queries']}")
    print(f"  Hit rate: {stats['hit_rate']:.1%}")
    print(f"  Exact: {stats['exact_rate']:.1%}, Semantic: {stats['semantic_rate']:.1%}")


if __name__ == "__main__":
    print("\n🧪 SEMANTIC CACHE PERFORMANCE TESTING")
    print("="*60)

    try:
        test_exact_matching()
        test_semantic_matching()
        test_cache_scaling()
        test_production_simulation()

        print("\n" + "="*60)
        print("✅ ALL CACHE TESTS PASSED!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
```

**Step 3.2: Run cache tests**
```bash
# Run focused cache tests
docker-compose exec api python3 scripts/test_cache_performance.py

# Expected output:
# - Test 1: <100ms cache hits
# - Test 2: 60-80% semantic matching
# - Test 3: 10-50x speedup on round 2
# - Test 4: 40-60% hit rate in production simulation
```

---

### Phase 4: Update Benchmark Report Generator

**Objective:** Add cache performance section to comparison reports

**File:** `scripts/generate_comparison_report.py`

**Step 4.1: Add cache metrics calculation**

**Add this function after existing metric functions:**
```python
def calculate_cache_metrics(results_data: dict) -> dict:
    """Calculate cache performance metrics from results"""

    if 'results' not in results_data:
        return None

    results = results_data['results']

    # Count cache hits/misses
    exact_hits = sum(1 for r in results if r.get('cache_type') == 'exact')
    semantic_hits = sum(1 for r in results if r.get('cache_type') == 'semantic')
    misses = sum(1 for r in results if r.get('cache_type') == 'miss')
    total = len(results)

    if total == 0:
        return None

    # Calculate timing benefits
    cached_times = [r['metrics']['search_time'] for r in results
                   if r.get('cache_hit', False)]
    fresh_times = [r['metrics']['search_time'] for r in results
                  if not r.get('cache_hit', False)]

    avg_cached_time = sum(cached_times) / len(cached_times) if cached_times else 0
    avg_fresh_time = sum(fresh_times) / len(fresh_times) if fresh_times else 0
    speedup = avg_fresh_time / avg_cached_time if avg_cached_time > 0 else 1

    # Calculate cost savings
    cached_cost = sum(r['metrics'].get('search_cost', 0) for r in results
                     if r.get('cache_hit', False))
    fresh_cost = sum(r['metrics'].get('search_cost', 0) for r in results
                    if not r.get('cache_hit', False))
    total_saved = fresh_cost * (exact_hits + semantic_hits) / max(misses, 1)

    return {
        'total_queries': total,
        'exact_hits': exact_hits,
        'semantic_hits': semantic_hits,
        'misses': misses,
        'hit_rate': (exact_hits + semantic_hits) / total,
        'exact_rate': exact_hits / total,
        'semantic_rate': semantic_hits / total,
        'avg_cached_time': avg_cached_time,
        'avg_fresh_time': avg_fresh_time,
        'speedup_factor': speedup,
        'cost_saved': total_saved
    }
```

**Step 4.2: Add cache section to report**

**Add to report generation (after main comparison table):**
```python
# Add cache performance section if cache was used
cache_section = "\n## 🚀 Cache Performance Analysis\n\n"
cache_data = []

for combo in combinations:
    tool, llm = combo.split('_')
    results_file = f"test_results/{tool}_{llm}/results_{timestamp}.json"

    try:
        with open(results_file) as f:
            data = json.load(f)
            cache_metrics = calculate_cache_metrics(data)

            if cache_metrics:
                cache_data.append({
                    'combination': combo,
                    **cache_metrics
                })
    except:
        continue

if cache_data:
    # Create cache comparison table
    cache_section += "| Combination | Hit Rate | Exact | Semantic | Speedup | Time Saved |\n"
    cache_section += "|-------------|----------|-------|----------|---------|------------|\n"

    for cd in cache_data:
        cache_section += (
            f"| {cd['combination']} | "
            f"{cd['hit_rate']:.1%} | "
            f"{cd['exact_rate']:.1%} | "
            f"{cd['semantic_rate']:.1%} | "
            f"{cd['speedup_factor']:.1f}x | "
            f"{cd['avg_fresh_time']-cd['avg_cached_time']:.2f}s |\n"
        )

    # Add insights
    best_hit_rate = max(cache_data, key=lambda x: x['hit_rate'])
    cache_section += f"\n**Best Cache Performance:** {best_hit_rate['combination']} "
    cache_section += f"({best_hit_rate['hit_rate']:.1%} hit rate)\n\n"

    cache_section += "**Key Insights:**\n"
    cache_section += f"- Average hit rate across all combinations: "
    cache_section += f"{sum(cd['hit_rate'] for cd in cache_data)/len(cache_data):.1%}\n"
    cache_section += f"- Cached queries are {best_hit_rate['speedup_factor']:.1f}x faster\n"
    cache_section += f"- Semantic matching adds {sum(cd['semantic_rate'] for cd in cache_data)/len(cache_data):.1%} additional coverage\n"

    # Add to report
    report_content += cache_section
else:
    cache_section += "*Cache was not enabled for this benchmark run.*\n"
    cache_section += "*Run with `--cache` flag to measure caching performance.*\n\n"
    report_content += cache_section
```

---

### Phase 5: Testing Strategy

**Objective:** Comprehensive cache performance validation

**Test 1: Cache Disabled (Baseline)**
```bash
# Clear any existing cache
docker-compose exec api python3 -c "from api.app.services.semantic_cache import SemanticCacheManager; c = SemanticCacheManager(); c.clear_cache()"

# Run without cache
docker-compose exec api python3 scripts/run_evaluation.py --mcp jina --llm claude

# Record baseline metrics:
# - Total time: ~243s
# - Avg search time: ~9.7s
# - Total cost: ~$0.36
```

**Test 2: Cache Enabled - First Run (Cold Cache)**
```bash
# Run with cache (first time)
docker-compose exec api python3 scripts/run_evaluation.py --mcp jina --llm claude --cache

# Expected results:
# - Hit rate: 0% (all misses)
# - Total time: ~250s (slightly slower due to cache writes + embedding generation)
# - Cache size: 25 items stored
```

**Test 3: Cache Enabled - Second Run (Warm Cache)**
```bash
# Run again with same questions
docker-compose exec api python3 scripts/run_evaluation.py --mcp jina --llm claude --cache

# Expected results:
# - Exact hit rate: 100% (all 25 questions)
# - Semantic hit rate: 0%
# - Total time: ~65s (73% faster!)
# - Avg cached lookup: 10-20ms
# - Cost saved: ~$0.15 (only LLM + embedding costs)
```

**Test 4: Semantic Matching Test**
```bash
# Create variant questions file
cat > config/test_suites/variant_questions.json << 'EOF'
[
  {"id": "v1", "question": "Tell me what BizGenie does"},
  {"id": "v2", "question": "BizGenie services overview?"},
  {"id": "v3", "question": "What can BizGenie help with?"}
]
EOF

# Run with variants
docker-compose exec api python3 scripts/run_evaluation.py \
  --mcp jina --llm claude --cache \
  --questions config/test_suites/variant_questions.json

# Expected results:
# - Exact hit rate: 0%
# - Semantic hit rate: 60-90% (2-3 questions match originals)
# - Shows semantic matching working
```

**Test 5: Full Benchmark with Cache**
```bash
# Run full benchmark with caching
docker-compose exec api bash scripts/run_benchmark.sh --cache

# Generate report with cache metrics
docker-compose exec api python3 scripts/generate_comparison_report.py

# Expected report sections:
# - Standard comparison table
# - NEW: Cache Performance Analysis table
# - Shows hit rates per combination
# - Shows time/cost savings
```

---

### Phase 6: Success Criteria

After implementing semantic cache, verify:

**Functionality:**
- [ ] ✅ Cache manager connects to ChromaDB successfully
- [ ] ✅ Exact match returns results in <50ms
- [ ] ✅ Semantic match works with similarity threshold
- [ ] ✅ Cache statistics track hits/misses correctly
- [ ] ✅ run_evaluation.py --cache flag works
- [ ] ✅ Cache survives container restarts (persisted in ChromaDB volume)

**Performance:**
- [ ] ✅ First run (cold cache): 0% hit rate, ~250s total time
- [ ] ✅ Second run (warm cache): 100% exact hit rate, ~65s total time (73% faster)
- [ ] ✅ Semantic matching: 60-90% hit rate on paraphrased questions
- [ ] ✅ Avg cached lookup: 10-30ms
- [ ] ✅ Avg fresh fetch: 8000-10000ms
- [ ] ✅ Speedup factor: 10-50x for cached queries

**Reporting:**
- [ ] ✅ Cache stats printed after each run
- [ ] ✅ Benchmark report includes cache metrics section
- [ ] ✅ Comparison table shows hit rates per combination
- [ ] ✅ Report identifies best cache performer

**Testing:**
- [ ] ✅ test_cache_performance.py runs successfully
- [ ] ✅ All 4 cache tests pass
- [ ] ✅ Production simulation shows realistic hit rates

---

### Phase 7: Expected Performance Results

**Baseline (No Cache):**
```
25 questions × 9.7s avg = 243s total
Cost: $0.36 total
```

**With Cache (Second Run):**
```
25 questions × 0.02s cached = 0.5s search time
25 questions × 6.5s LLM = 162.5s LLM time
Total: ~163s (33% faster than baseline)
Cost: $0.18 (50% cheaper - only LLM costs, no MCP tool costs)
```

**With Cache (Production - 70% hit rate):**
```
18 cached × 0.02s = 0.36s
7 fresh × 9.7s = 67.9s
Total search: 68.3s (vs 243s uncached)
Speedup: 72% faster
Cost saved: 70% of MCP tool costs
```

---

### Phase 8: Troubleshooting

**Issue 1: ChromaDB Connection Failed**
```bash
# Check ChromaDB is running
docker-compose ps | grep chromadb
# Should show "Up"

# Check ChromaDB logs
docker-compose logs chromadb

# Restart if needed
docker-compose restart chromadb
```

**Issue 2: Embeddings Too Slow**
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Monitor embedding time
# Should be 30-100ms per question
# If >500ms, check network/API status
```

**Issue 3: Low Semantic Hit Rate**
```bash
# Adjust threshold (lower = more matches)
python3 scripts/run_evaluation.py --mcp jina --llm claude \
  --cache --cache-threshold 0.85  # Default is 0.90

# Test different thresholds:
# 0.95 = Very strict (only near-identical questions)
# 0.90 = Balanced (recommended)
# 0.85 = Permissive (more semantic matches)
# 0.80 = Very permissive (may match unrelated questions)
```

**Issue 4: Cache Not Persisting**
```bash
# Check ChromaDB volume
docker volume ls | grep chromadb

# Verify persistence
docker-compose exec chromadb ls -la /chroma/chroma

# If missing, recreate volume:
docker-compose down -v
docker-compose up -d
```

---

## 📚 APPENDIX: Additional Tools (Optional Future Implementations)

These tools can be added AFTER Firecrawl is successfully implemented and tested.

---

### Appendix A: Exa AI - Neural Search Engine (Status: PAUSED)

**⚠️ WARNING: Exa has known indexing issues with BizGenie site. Do NOT implement until resolved.**

**Type:** Hybrid Neural Search + Content Retrieval  
**SDK:** `exa_py>=1.0.0`  
**Cost:** ~$0.008/search  
**Docs:** https://docs.exa.ai/sdks/python-sdk-specification

**Why Paused:**
- BizGenie (bizgenieai.com) not indexed in Exa's neural search database
- Returns 0 results for queries
- Requires site to be in Exa's index or using `get_contents()` with direct URLs

**Architecture:**
- Step 1: Neural search (semantic, not keyword-based)
- Step 2: Fetch full content for top results
- Step 3: Return combined content from multiple pages

**Quick Implementation Reference:**
```python
from exa_py import Exa

class ExaTool(MCPTool):
    def search(self, question: str, context: str = None) -> SearchResult:
        # Neural search
        results = self.client.search(
            query=question,
            num_results=5,
            include_domains=["bizgenieai.com"]
        )
        
        # Get full content
        if results.results:
            ids = [r.id for r in results.results]
            contents = self.client.get_contents(ids=ids, text=True)
            # Combine and return
```

**When to Implement:**
1. After confirming BizGenie is indexed in Exa
2. OR after testing `get_contents()` with direct URLs works
3. OR as fallback to other tools if main searches fail

---

### Appendix B: Crawl4AI - Open Source Scraper (Status: NOT STARTED)

**Type:** Free, Open-Source LLM-Optimized Web Scraper  
**SDK:** `Crawl4AI>=0.7.7`  
**Cost:** FREE (self-hosted)  
**Docs:** https://docs.crawl4ai.com/

**Why Last:**
- Most complex (async API in sync codebase)
- Requires Playwright browser installation
- Needs Docker modifications
- But FREE (major cost advantage)

**Complexity Considerations:**
- Async/await pattern requires wrapper
- Large Docker image (includes browser)
- Longer build times
- More dependencies

**Quick Implementation Reference:**
```python
import asyncio
from crawl4ai import AsyncWebCrawler

class Crawl4AITool(MCPTool):
    def search(self, question: str, context: str = None) -> SearchResult:
        # Sync wrapper for async code
        content = asyncio.run(self._async_scrape(context))
        return SearchResult(
            content=content,
            sources=[context],
            search_cost=0.0  # FREE!
        )
    
    async def _async_scrape(self, url: str) -> str:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return result.markdown
```

**Additional Setup Required:**
1. Add to `api/requirements.txt`:
   ```
   Crawl4AI>=0.7.7
   playwright>=1.40.0
   ```

2. Update `api/Dockerfile`:
   ```dockerfile
   RUN playwright install chromium
   RUN playwright install-deps
   ```

**When to Implement:**
- After Firecrawl is fully tested
- If cost reduction is needed
- If you need free alternative to paid scrapers

---

## 🔗 Quick Reference Links

**Firecrawl (PRIMARY IMPLEMENTATION):**
- Docs: https://docs.firecrawl.dev/sdks/python
- PyPI: https://pypi.org/project/firecrawl-py/
- API Keys: https://firecrawl.dev

**Exa AI (OPTIONAL - PAUSED):**
- Docs: https://docs.exa.ai/sdks/python-sdk-specification
- GitHub: https://github.com/exa-labs/exa-py
- Website: https://exa.ai

**Crawl4AI (OPTIONAL - FUTURE):**
- Docs: https://docs.crawl4ai.com/
- GitHub: https://github.com/unclecode/crawl4ai
- PyPI: https://pypi.org/project/Crawl4AI/

---

## 📞 CONTACT & SUPPORT

**For AI Agent Implementing This:**

If you encounter issues:
1. Check the **Phase 8: Error Handling** section above
2. Verify all SUCCESS CRITERIA checkboxes
3. Review Docker logs: `docker-compose logs api`
4. Test Firecrawl API directly (troubleshooting commands provided)
5. Ask the user for clarification if needed

**For Human User:**

- Firecrawl Support: https://firecrawl.dev/support
- Project Issues: Create GitHub issue in repo
- Questions: Refer to README.md and ARCHITECTURE.md

---

## 📝 REVISION HISTORY

- **2025-12-01:** Complete rewrite focusing on Firecrawl as primary implementation
  - Moved Exa to appendix (indexing issues)
  - Added comprehensive step-by-step guide for AI agents
  - Added detailed error handling and troubleshooting
  - Added validation and testing procedures
  - Included full Firecrawl tool implementation code

- **Previous:** Original plan had Exa as Phase 1 (deprecated)

---

**END OF IMPLEMENTATION PLAN**

**Next Action for AI Agent:** Begin with Phase 1 (Add Firecrawl Dependency) and follow steps sequentially.
