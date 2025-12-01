# Implementation Plan: Adding New MCP Tools (Exa, Firecrawl, Crawl4AI)

**Date:** 2025-12-01
**Status:** Ready for Implementation
**Revised Order:** Exa AI → Firecrawl → Crawl4AI
**Goal:** Expand evaluation framework from 4 combinations (2 tools × 2 LLMs) to 10 combinations (5 tools × 2 LLMs)

---

## ⚠️ IMPORTANT: Implementation Order

**PRIORITY 1: Exa AI** (Implement First)
- Reason: Most unique (hybrid neural search + content extraction)
- Highest potential to beat current winner (Jina_Claude)
- Different architecture from existing tools

**PRIORITY 2: Firecrawl** (Implement Second)
- Reason: Better scraper than Jina
- Easier to implement after Exa

**PRIORITY 3: Crawl4AI** (Implement Last/Optional)
- Reason: Free but most complex (async handling)
- Can be done separately if time constrained

---

## 📋 Quick Reference for Another AI Assistant

**If you're implementing this, follow these phases in order:**

### ✅ Phase 1: Exa AI (Do This First)
1. Add `exa_py>=1.0.0` to `api/requirements.txt`
2. Add `EXA_API_KEY=...` to `.env.example`
3. Create NEW FILE: `api/app/tools/exa_tool.py` (complete code provided in Phase 1)
4. Update `scripts/run_evaluation.py`:
   - Add import: `from api.app.tools.exa_tool import ExaTool`
   - Add "exa" to choices list
   - Add elif block for exa instantiation
5. Update `scripts/run_benchmark.sh`: Add "exa claude" and "exa gpt4" to combinations array
6. Test: `docker-compose exec api python3 scripts/run_evaluation.py --mcp exa --llm claude`

### ✅ Phase 2: Firecrawl (Do This Second)
1. Add `firecrawl-py>=4.10.0` to `api/requirements.txt`
2. Add `FIRECRAWL_API_KEY=...` to `.env.example`
3. Create NEW FILE: `api/app/tools/firecrawl_tool.py` (complete code provided in Phase 2)
4. Update `scripts/run_evaluation.py`:
   - Add import: `from api.app.tools.firecrawl_tool import FirecrawlTool`
   - Add "firecrawl" to choices list
   - Add elif block for firecrawl instantiation
5. Update `scripts/run_benchmark.sh`: Add "firecrawl claude" and "firecrawl gpt4" to combinations array
6. Test: `docker-compose exec api python3 scripts/run_evaluation.py --mcp firecrawl --llm claude`

### ⚠️ Phase 3: Crawl4AI (Optional - More Complex)
- See Phase 3 section below for async handling details
- Requires Docker modifications
- Can be skipped if time constrained

---

## 📋 Current Architecture Analysis

### Existing Structure

**Tools Currently Implemented:**
1. **Jina AI Reader** (`api/app/tools/jina_tool.py`) - Web scraper
2. **Tavily AI Search** (`api/app/tools/tavily_tool.py`) - Search engine

**Base Interface** (`api/app/tools/base.py`):
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

### Integration Points

1. **Tool Import** (`scripts/run_evaluation.py` lines 11-12):
   - Direct imports: `from api.app.tools.jina_tool import JinaTool`

2. **CLI Argument Parsing** (line 23):
   - `choices=["jina", "tavily"]`

3. **Tool Instantiation** (lines 36-39):
   - If/else logic to create tool instance

4. **Benchmark Script** (`scripts/run_benchmark.sh` lines 20-25):
   - Hardcoded combinations array

5. **Dependencies** (`api/requirements.txt`):
   - `tavily-python>=0.3.0` (only Tavily has SDK)
   - Jina uses direct HTTP requests

---

## 🎯 Tools to Add

### 1. Firecrawl (Priority: HIGH)
**Type:** Advanced Web Scraper
**Why:** Better scraping than Jina, handles JavaScript-heavy sites

**API Details:**
- **SDK:** `firecrawl-py` (latest: 4.10.0)
- **Install:** `pip install firecrawl-py`
- **Pricing:** Paid API (~$0.003-0.005/scrape estimated)
- **Auth:** API key required (`FIRECRAWL_API_KEY`)
- **Docs:** https://docs.firecrawl.dev/sdks/python

**Key Features:**
```python
from firecrawl import Firecrawl
client = Firecrawl(api_key="fc-YOUR_API_KEY")

# Scrape single URL
result = client.scrape(
    url='https://bizgenieai.com',
    formats=['markdown', 'html']
)
# Returns: {'markdown': '...', 'html': '...', 'metadata': {...}}

# Can also crawl entire sites (not needed for our use case)
```

**Implementation Notes:**
- Similar to Jina (URL scraping)
- Better markdown conversion
- Handles dynamic JavaScript content
- Returns structured metadata

---

### 2. Exa AI (Priority: HIGH)
**Type:** Neural Search Engine + Content Retrieval (Hybrid)
**Why:** Best of both worlds - AI search + full content extraction

**API Details:**
- **SDK:** `exa_py`
- **Install:** `pip install exa_py`
- **Pricing:** Paid (~$0.005-0.010/search estimated)
- **Auth:** API key required (`EXA_API_KEY`)
- **Docs:** https://docs.exa.ai/sdks/python-sdk-specification

**Key Features:**
```python
from exa_py import Exa
client = Exa(api_key="your-api-key")

# Neural search
results = client.search(
    "What services does BizGenie offer?",
    num_results=5,
    include_domains=["bizgenieai.com"]
)

# Get full content
contents = client.get_contents(
    ids=[result.id for result in results],
    text=True  # Get full text content
)
# Returns: SearchResult with full page content + relevance scores
```

**Implementation Notes:**
- Hybrid approach: neural search + content extraction
- Uses embeddings for semantic understanding
- Can restrict to specific domains
- Returns both snippets AND full content
- May outperform both Jina (better search) and Tavily (full content)

---

### 3. Crawl4AI (Priority: MEDIUM)
**Type:** Open-source LLM-optimized Web Scraper
**Why:** FREE alternative, specifically designed for LLMs

**API Details:**
- **SDK:** `Crawl4AI`
- **Install:** `pip install Crawl4AI`
- **Pricing:** FREE (open-source, self-hosted)
- **Auth:** None required
- **Docs:** https://docs.crawl4ai.com/

**Key Features:**
```python
from crawl4ai import AsyncWebCrawler

async def scrape():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://bizgenieai.com")
        return result.markdown  # Clean markdown output

# Synchronous version also available
from crawl4ai import WebCrawler
crawler = WebCrawler()
result = crawler.run(url="https://bizgenieai.com")
```

**Implementation Notes:**
- Built on Playwright (handles JavaScript)
- Optimized markdown output for LLMs
- FREE (major cost advantage)
- May require Docker for full features
- Async architecture (need to handle in sync evaluation script)

---

## 🛠️ Implementation Strategy

### Phase 1: Add Exa AI (Estimated: 3-4 hours) ⭐ START HERE

**Why First:** Most unique approach (neural search + full content), highest potential to beat Jina_Claude

**Files to Modify:**

**STEP 1: Add Dependency**

1. **File:** `api/requirements.txt`
   **Action:** Add this line at the end of the file
   ```
   exa_py>=1.0.0
   ```

**STEP 2: Add API Key to Environment Template**

2. **File:** `.env.example`
   **Location:** After line 7 (after OPENAI_API_KEY)
   **Action:** Add this line
   ```
   EXA_API_KEY=your_exa_api_key_here
   ```

**STEP 3: Create Exa Tool Implementation**

3. **File:** `api/app/tools/exa_tool.py` **(CREATE NEW FILE)**
   **Action:** Create this entire file with the following content
   ```python
   import os
   import time
   from urllib.parse import urlparse
   from exa_py import Exa
   from api.app.tools.base import MCPTool, SearchResult
   from api.app.core.logging import get_logger

   logger = get_logger("exa_tool")

   class ExaTool(MCPTool):
       """Exa AI Neural Search + Content Extraction MCP tool"""

       def __init__(self, config: dict):
           super().__init__(config)
           self.api_key = os.environ.get(config.get("api_key_env", "EXA_API_KEY"))
           if not self.api_key:
               raise ValueError("Exa API key is required")
           self.client = Exa(api_key=self.api_key)

       def search(self, question: str, context: str = None) -> SearchResult:
           """
           Perform neural search using Exa, then retrieve full content.
           Combines search ranking with full page content extraction.
           """
           start_time = time.time()

           # Extract domain from context if provided
           include_domains = []
           if context:
               try:
                   parsed = urlparse(context)
                   domain = parsed.netloc.replace("www.", "")
                   if domain:
                       include_domains.append(domain)
                       logger.info(f"Restricting Exa search to domain: {domain}")
               except Exception as e:
                   logger.warning(f"Could not parse context URL '{context}': {e}")

           logger.info(f"Searching Exa with query: {question}")

           try:
               # Step 1: Neural search to find relevant pages
               search_results = self.client.search(
                   query=question,
                   num_results=5,
                   include_domains=include_domains if include_domains else None
               )

               logger.info(f"Exa search returned {len(search_results.results)} results")

               # Step 2: Get full content for search results
               if search_results.results:
                   ids = [r.id for r in search_results.results]
                   contents = self.client.get_contents(ids=ids, text=True)

                   # Combine all content
                   content_parts = []
                   sources = []
                   for item in contents.results:
                       content_parts.append(f"Source: {item.title if hasattr(item, 'title') else 'No title'}\nURL: {item.url}\n\n{item.text}\n")
                       sources.append(item.url)

                   content = "\n---\n".join(content_parts)
                   logger.info(f"Retrieved content from {len(sources)} sources")
               else:
                   content = ""
                   sources = []
                   logger.warning("No search results found")

           except Exception as e:
               logger.error(f"Exa search failed: {e}")
               raise

           search_time = time.time() - start_time

           return SearchResult(
               content=content,
               sources=sources,
               metadata={"tool": "exa", "query": question, "count": len(sources)},
               search_time=search_time,
               search_cost=0.008  # Estimated
           )

       def get_info(self) -> dict:
           return {
               "name": "Exa AI",
               "cost_per_search": 0.008,
               "capabilities": ["neural_search", "content_extraction", "hybrid"]
           }
   ```

**STEP 4: Update Evaluation Script**

4. **File:** `scripts/run_evaluation.py`

   **4a. Add Import** (After line 12)
   **Find this section:**
   ```python
   from api.app.tools.jina_tool import JinaTool
   from api.app.tools.tavily_tool import TavilyTool
   ```
   **Add this line after it:**
   ```python
   from api.app.tools.exa_tool import ExaTool
   ```

   **4b. Update CLI Choices** (Line 23)
   **Find:**
   ```python
   parser.add_argument("--mcp", required=True, choices=["jina", "tavily"], help="MCP Tool to test")
   ```
   **Replace with:**
   ```python
   parser.add_argument("--mcp", required=True, choices=["jina", "tavily", "exa"], help="MCP Tool to test")
   ```

   **4c. Add Tool Instantiation** (After line 39)
   **Find this section:**
   ```python
   if args.mcp == "jina":
       mcp_tool = JinaTool({"api_key_env": "JINA_API_KEY"})
   else:
       mcp_tool = TavilyTool({"api_key_env": "TAVILY_API_KEY", "config": {"search_depth": "advanced"}})
   ```
   **Replace with:**
   ```python
   if args.mcp == "jina":
       mcp_tool = JinaTool({"api_key_env": "JINA_API_KEY"})
   elif args.mcp == "tavily":
       mcp_tool = TavilyTool({"api_key_env": "TAVILY_API_KEY", "config": {"search_depth": "advanced"}})
   elif args.mcp == "exa":
       mcp_tool = ExaTool({"api_key_env": "EXA_API_KEY"})
   else:
       raise ValueError(f"Unknown MCP tool: {args.mcp}")
   ```

**STEP 5: Update Benchmark Script**

5. **File:** `scripts/run_benchmark.sh`
   **Find:** (Lines 20-25)
   ```bash
   declare -a combinations=(
       "tavily claude"
       "tavily gpt4"
       "jina claude"
       "jina gpt4"
   )
   ```
   **Replace with:**
   ```bash
   declare -a combinations=(
       "tavily claude"
       "tavily gpt4"
       "jina claude"
       "jina gpt4"
       "exa claude"
       "exa gpt4"
   )
   ```

**STEP 6: Test Exa Implementation**

6. **Testing Commands:**
   ```bash
   # Install dependencies
   docker-compose down
   docker-compose build
   docker-compose up -d

   # Add EXA_API_KEY to your .env file first!

   # Test single run
   docker-compose exec api python3 scripts/run_evaluation.py --mcp exa --llm claude

   # If successful, test with GPT-4
   docker-compose exec api python3 scripts/run_evaluation.py --mcp exa --llm gpt4

   # Run full benchmark (all 6 combinations)
   docker-compose exec api bash scripts/run_benchmark.sh
   ```

**Expected Output:**
- Should see "Exa search returned X results"
- Should generate eval and results files in `test_results/exa_claude/` and `test_results/exa_gpt4/`
- Benchmark report should now show 6 combinations

---

### Phase 2: Add Firecrawl (Estimated: 2-3 hours)

**Why Second:** Advanced scraper, likely to beat Jina, easier after implementing Exa

**Files to Modify:**

**STEP 1: Add Dependency**

1. **File:** `api/requirements.txt`
   **Action:** Add this line at the end of the file
   ```
   firecrawl-py>=4.10.0
   ```

**STEP 2: Add API Key to Environment Template**

2. **File:** `.env.example`
   **Location:** After EXA_API_KEY line
   **Action:** Add this line
   ```
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   ```

**STEP 3: Create Firecrawl Tool Implementation**

3. **File:** `api/app/tools/firecrawl_tool.py` **(CREATE NEW FILE)**
   **Action:** Create this entire file with the following content
   ```python
   import os
   import time
   from firecrawl import FirecrawlApp
   from api.app.tools.base import MCPTool, SearchResult
   from api.app.core.logging import get_logger

   logger = get_logger("firecrawl_tool")

   class FirecrawlTool(MCPTool):
       """Firecrawl Advanced Web Scraper MCP tool"""

       def __init__(self, config: dict):
           super().__init__(config)
           self.api_key = os.environ.get(config.get("api_key_env", "FIRECRAWL_API_KEY"))
           if not self.api_key:
               raise ValueError("Firecrawl API key is required")
           self.client = FirecrawlApp(api_key=self.api_key)

       def search(self, question: str, context: str = None) -> SearchResult:
           """
           Scrape content using Firecrawl.
           Firecrawl is a scraper, requires direct URL context.
           """
           start_time = time.time()

           # Firecrawl is a scraper, needs direct URL
           if not context or not context.startswith("http"):
               raise ValueError("Firecrawl requires a URL context")

           logger.info(f"Scraping with Firecrawl: {context}")

           try:
               result = self.client.scrape_url(
                   url=context,
                   params={'formats': ['markdown']}
               )

               content = result.get('markdown', '')
               sources = [context]

               logger.info(f"Firecrawl scrape successful. Content length: {len(content)}")

           except Exception as e:
               logger.error(f"Firecrawl scrape failed: {e}")
               raise

           search_time = time.time() - start_time

           return SearchResult(
               content=content,
               sources=sources,
               metadata={"tool": "firecrawl", "url": context},
               search_time=search_time,
               search_cost=0.004  # Estimated
           )

       def get_info(self) -> dict:
           return {
               "name": "Firecrawl",
               "cost_per_search": 0.004,
               "capabilities": ["scrape", "javascript_rendering", "advanced_parsing"]
           }
   ```

**STEP 4: Update Evaluation Script**

4. **File:** `scripts/run_evaluation.py`

   **4a. Add Import** (After the ExaTool import)
   **Add this line:**
   ```python
   from api.app.tools.firecrawl_tool import FirecrawlTool
   ```

   **4b. Update CLI Choices** (Line 23)
   **Find:**
   ```python
   parser.add_argument("--mcp", required=True, choices=["jina", "tavily", "exa"], help="MCP Tool to test")
   ```
   **Replace with:**
   ```python
   parser.add_argument("--mcp", required=True, choices=["jina", "tavily", "exa", "firecrawl"], help="MCP Tool to test")
   ```

   **4c. Add Tool Instantiation**
   **Find the elif chain and add this before the else:**
   ```python
   elif args.mcp == "firecrawl":
       mcp_tool = FirecrawlTool({"api_key_env": "FIRECRAWL_API_KEY"})
   ```

**STEP 5: Update Benchmark Script**

5. **File:** `scripts/run_benchmark.sh`
   **Find:**
   ```bash
   declare -a combinations=(
       "tavily claude"
       "tavily gpt4"
       "jina claude"
       "jina gpt4"
       "exa claude"
       "exa gpt4"
   )
   ```
   **Replace with:**
   ```bash
   declare -a combinations=(
       "tavily claude"
       "tavily gpt4"
       "jina claude"
       "jina gpt4"
       "exa claude"
       "exa gpt4"
       "firecrawl claude"
       "firecrawl gpt4"
   )
   ```

**STEP 6: Test Firecrawl Implementation**

6. **Testing Commands:**
   ```bash
   # Rebuild with new dependency
   docker-compose down
   docker-compose build
   docker-compose up -d

   # Add FIRECRAWL_API_KEY to your .env file first!

   # Test single run
   docker-compose exec api python3 scripts/run_evaluation.py --mcp firecrawl --llm claude

   # If successful, test with GPT-4
   docker-compose exec api python3 scripts/run_evaluation.py --mcp firecrawl --llm gpt4

   # Run full benchmark (all 8 combinations)
   docker-compose exec api bash scripts/run_benchmark.sh
   ```

**Expected Output:**
- Should see "Firecrawl scrape successful"
- Should generate eval and results files in `test_results/firecrawl_claude/` and `test_results/firecrawl_gpt4/`
- Benchmark report should now show 8 combinations

---

### Phase 3: Add Crawl4AI (Estimated: 4-5 hours - More Complex)

**Challenges:**
- Async API but evaluation script is sync
- May need Docker setup
- FREE but more setup complexity

**Files to Modify:**

1. **`api/requirements.txt`**
   ```
   ADD: Crawl4AI>=0.7.7
   ADD: playwright>=1.40.0  # Dependency
   ```

2. **`api/Dockerfile`** (May need update)
   ```dockerfile
   # Install Playwright browsers
   RUN playwright install chromium
   RUN playwright install-deps
   ```

3. **`api/app/tools/crawl4ai_tool.py`** (NEW FILE)
   ```python
   import os
   import time
   import asyncio
   from crawl4ai import AsyncWebCrawler
   from api.app.tools.base import MCPTool, SearchResult
   from api.app.core.logging import get_logger

   class Crawl4AITool(MCPTool):
       def __init__(self, config: dict):
           super().__init__(config)
           # No API key needed - open source

       def search(self, question: str, context: str = None) -> SearchResult:
           start_time = time.time()

           if not context or not context.startswith("http"):
               raise ValueError("Crawl4AI requires a URL context")

           try:
               # Run async code in sync context
               content = asyncio.run(self._async_scrape(context))
               sources = [context]

           except Exception as e:
               logger.error(f"Crawl4AI scrape failed: {e}")
               raise

           search_time = time.time() - start_time

           return SearchResult(
               content=content,
               sources=sources,
               metadata={"tool": "crawl4ai", "url": context},
               search_time=search_time,
               search_cost=0.0  # FREE!
           )

       async def _async_scrape(self, url: str) -> str:
           async with AsyncWebCrawler() as crawler:
               result = await crawler.arun(url=url)
               return result.markdown

       def get_info(self) -> dict:
           return {
               "name": "Crawl4AI",
               "cost_per_search": 0.0,
               "capabilities": ["scrape", "javascript_rendering", "llm_optimized"]
           }
   ```

4. **Update same files as previous phases**

---

## 📊 Expected Combinations After Implementation

| # | MCP Tool | LLM | Type | Cost/Query |
|---|----------|-----|------|------------|
| 1 | Jina | Claude | Scraper | $0.0144 |
| 2 | Jina | GPT-4 | Scraper | $0.0143 |
| 3 | Tavily | Claude | Search | $0.0192 |
| 4 | Tavily | GPT-4 | Search | $0.0187 |
| 5 | **Firecrawl** | Claude | Scraper | **$0.0164** |
| 6 | **Firecrawl** | GPT-4 | Scraper | **$0.0163** |
| 7 | **Exa** | Claude | Hybrid | **$0.0204** |
| 8 | **Exa** | GPT-4 | Hybrid | **$0.0203** |
| 9 | **Crawl4AI** | Claude | Scraper | **$0.0124** |
| 10 | **Crawl4AI** | GPT-4 | Scraper | **$0.0123** |

**Expected Winners:**
- **Quality:** Exa_Claude or Firecrawl_Claude (better content extraction)
- **Speed:** Exa_GPT4 (optimized search + fast LLM)
- **Cost:** Crawl4AI_GPT4 (free scraping)

---

## 🚨 Risks & Considerations

### 1. API Key Management
- **Risk:** Need 3 more API keys (Firecrawl, Exa, Crawl4AI doesn't need one)
- **Mitigation:** Update .env.example, add to documentation

### 2. Cost Increase
- **Risk:** Testing 10 combinations = 2.5x more API calls
- **Cost:** ~$0.40 per full benchmark (25 questions × 10 combinations × $0.0016 avg)
- **Mitigation:**
  - Run smaller test suite (10 questions) initially
  - Make tools optional with CLI flags

### 3. Async/Sync Mismatch (Crawl4AI)
- **Risk:** Crawl4AI uses async, our script is sync
- **Mitigation:** Use `asyncio.run()` wrapper (shown in code above)

### 4. Docker Build Time
- **Risk:** Installing Playwright browsers increases Docker image size
- **Mitigation:**
  - Only install if Crawl4AI is being used
  - Use multi-stage Docker build

### 5. Benchmark Time
- **Risk:** 4 combinations take 3-5 min → 10 combinations take 7-12 min
- **Mitigation:**
  - Keep parallel execution
  - Consider running overnight for full suite

### 6. Report Complexity
- **Risk:** 10 combinations harder to compare
- **Mitigation:**
  - Update report generator to group by tool type (scrapers vs search)
  - Add filtering options

---

## 🎯 Implementation Order (UPDATED)

### **Phase 1: Exa AI (Start Here)** ⭐
- **Time:** 3-4 hours
- **Complexity:** MEDIUM (new hybrid approach)
- **Value:** VERY HIGH (best of both worlds - neural search + content)
- **Cost:** Higher ($0.008/query)
- **Why First:** Most unique, highest potential to beat current winner

### **Phase 2: Firecrawl**
- **Time:** 2-3 hours
- **Complexity:** LOW (similar to Jina)
- **Value:** HIGH (likely to beat Jina)
- **Cost:** Manageable ($0.004/query)
- **Why Second:** Easier after Exa, clear improvement over Jina

### **Phase 3: Crawl4AI (Optional)**
- **Time:** 4-5 hours
- **Complexity:** HIGH (async, Docker setup)
- **Value:** HIGH (free cost advantage)
- **Cost:** FREE
- **Why Last:** Most complex, can be done separately if time constrained

---

## 📝 Testing Plan

### Unit Testing (Per Tool)
```bash
# Test each tool independently
docker-compose exec api python3 scripts/run_evaluation.py --mcp firecrawl --llm claude
docker-compose exec api python3 scripts/run_evaluation.py --mcp exa --llm claude
docker-compose exec api python3 scripts/run_evaluation.py --mcp crawl4ai --llm claude
```

### Integration Testing
```bash
# Run mini benchmark (5 questions, all tools)
docker-compose exec api bash scripts/run_benchmark.sh
```

### Full Benchmark
```bash
# Run complete 25 questions × 10 combinations
docker-compose exec api bash scripts/run_benchmark.sh
```

---

## 📚 Documentation Updates Needed

1. **README.md**
   - Update "4 combinations" → "10 combinations"
   - Add new tool descriptions
   - Update prerequisites (API keys)
   - Update sample results

2. **TESTING.md**
   - Add new tool architectures
   - Update performance expectations

3. **ARCHITECTURE.md**
   - Document tool selection criteria
   - Add tool comparison table

4. **.env.example**
   - Add FIRECRAWL_API_KEY
   - Add EXA_API_KEY

---

## ✅ Success Criteria

- [ ] All 3 new tools successfully integrated
- [ ] Benchmark script runs all 10 combinations without errors
- [ ] Report generator handles 10 combinations correctly
- [ ] Documentation updated
- [ ] At least 1 new tool beats Jina_Claude in quality
- [ ] Crawl4AI proves cost advantage (FREE)
- [ ] Full benchmark completes in < 15 minutes

---

## 🔗 References

**Firecrawl:**
- Docs: https://docs.firecrawl.dev/sdks/python
- PyPI: https://pypi.org/project/firecrawl-py/
- GitHub: https://github.com/mendableai/firecrawl-py

**Exa AI:**
- Docs: https://docs.exa.ai/sdks/python-sdk-specification
- GitHub: https://github.com/exa-labs/exa-py
- Website: https://exa.ai

**Crawl4AI:**
- Docs: https://docs.crawl4ai.com/
- GitHub: https://github.com/unclecode/crawl4ai
- PyPI: https://pypi.org/project/Crawl4AI/

---

**Next Step:** Review this plan, approve phases, and begin Phase 1 (Firecrawl) implementation.
