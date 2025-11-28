# Evaluation Metrics: MCP Tool + LLM Testing Framework

**Last Updated**: 2025-01-26

---

## Goal: Identify Best MCP Tool + LLM Combination

We test all combinations to answer:
1. **Which MCP tool finds the best information?**
2. **Which LLM generates the best answers?**
3. **Which combination works best together?**
4. **What's the best choice for our use case?** (quality vs cost vs speed)

---

## Test Matrix

We test every combination:

|           | Claude | GPT-4 | Gemini |
|-----------|--------|-------|--------|
| **Tavily**    | Test   | Test  | Test   |
| **Jina**      | Test   | Test  | Test   |
| **Firecrawl** | Test   | Test  | Test   |

Each combination tested with **25 standard questions**.

---

## Metrics Per Query

### 1. MCP Tool Metrics
Measures search effectiveness:

**Search Performance:**
- `mcp_search_time`: How long search took (seconds)
- `mcp_cost`: Cost of search operation
- `mcp_sources_count`: Number of sources returned

**Search Quality (Manual Review):**
- `search_relevance`: Are results relevant to question? (0-100)
- `search_coverage`: Found all needed information? (0-100)
- `search_source_quality`: Authoritative sources? (0-100)

**Search Quality Score:**
```python
search_quality = (
    search_relevance * 0.50 +
    search_coverage * 0.30 +
    search_source_quality * 0.20
)
```

---

### 2. LLM Metrics
Measures answer generation:

**Generation Performance:**
- `llm_time`: How long LLM took (seconds)
- `llm_cost`: Cost of LLM generation
- `llm_tokens`: Tokens consumed

**Answer Quality (Manual Review):**
- `answer_accuracy`: Factually correct? (0-100)
- `answer_completeness`: Fully answers question? (0-100)
- `answer_clarity`: Clear and well-written? (0-100)
- `source_attribution`: Cites sources properly? (0-100)

**Answer Quality Score:**
```python
answer_quality = (
    answer_accuracy * 0.40 +
    answer_completeness * 0.30 +
    answer_clarity * 0.20 +
    source_attribution * 0.10
)
```

---

### 3. Combined Metrics
Measures overall performance:

**Total Performance:**
- `total_time`: mcp_search_time + llm_time
- `total_cost`: mcp_cost + llm_cost

**Baseline Comparison:**
- `similarity_to_notebookllm`: How close to NotebookLLM answer? (0-1)
  - BLEU score (30%)
  - Semantic similarity (40%)
  - Coverage comparison (30%)

**Overall Score:**
```python
overall_score = (
    answer_quality * 0.40 +           # Most important
    search_quality * 0.25 +            # Search matters
    performance_score * 0.20 +         # Speed/cost
    similarity_to_baseline * 0.15      # Baseline comparison
)
```

**Performance Score:**
```python
# Speed score: Target <5s
if total_time < 3:
    speed = 100
elif total_time < 5:
    speed = 90
elif total_time < 10:
    speed = 70
else:
    speed = 50

# Cost score: Target <$0.05
if total_cost < 0.02:
    cost = 100
elif total_cost < 0.05:
    cost = 80
else:
    cost = 50

performance_score = (speed + cost) / 2
```

---

## Aggregated Metrics (Per Combination)

After running 25 questions on a combination:

### Summary Statistics
- `avg_search_quality`: Average search quality score
- `avg_answer_quality`: Average answer quality score
- `avg_overall_score`: Average overall score
- `avg_time`: Average response time
- `avg_cost`: Average cost per query
- `error_rate`: Percentage of queries with errors

### MCP Tool Isolation
Compare same MCP tool across different LLMs:

```
Tavily performance:
  - With Claude: search_quality = 88
  - With GPT-4: search_quality = 88
  - With Gemini: search_quality = 88

Average Tavily search quality: 88
```

This isolates how good **Tavily** is at search.

### LLM Isolation
Compare same LLM across different MCP tools:

```
Claude performance:
  - With Tavily results: answer_quality = 89
  - With Jina results: answer_quality = 85
  - With Firecrawl results: answer_quality = 83

Average Claude answer quality: 85.7
```

This isolates how good **Claude** is at answering.

### Combination Synergy
Some combinations work better together:

```
Tavily + Claude: 89 (higher than expected!)
Tavily alone: 88
Claude alone: 85.7

Synergy bonus: +2.3 points
```

---

## Evaluation Report Format

### Per-Query Result
```json
{
  "question_id": "q001",
  "question": "What services does BizGenie offer?",
  "combination": {
    "mcp_tool": "tavily",
    "llm_model": "claude"
  },

  "mcp_metrics": {
    "search_time": 1.8,
    "search_cost": 0.01,
    "sources_count": 5,
    "search_relevance": 92,
    "search_coverage": 88,
    "search_source_quality": 90,
    "search_quality_score": 90.4
  },

  "llm_metrics": {
    "generation_time": 1.2,
    "generation_cost": 0.022,
    "tokens_used": 850,
    "answer_accuracy": 95,
    "answer_completeness": 90,
    "answer_clarity": 92,
    "source_attribution": 100,
    "answer_quality_score": 93.3
  },

  "combined_metrics": {
    "total_time": 3.0,
    "total_cost": 0.032,
    "similarity_to_notebookllm": 0.88,
    "overall_score": 91.2
  },

  "answer": "BizGenie offers...",
  "sources": ["url1", "url2"]
}
```

### Comparison Report
```
========================================
MCP TOOL + LLM EVALUATION REPORT
========================================
Test Date: 2025-01-26
Questions: 25
Baseline: NotebookLLM

----------------------------------------
OVERALL RANKINGS
----------------------------------------
#1  tavily + claude     91.2  (Best overall)
#2  tavily + gpt4       88.5
#3  jina + claude       85.3
#4  jina + gpt4         83.7
#5  firecrawl + claude  82.1
#6  firecrawl + gpt4    79.8

----------------------------------------
MCP TOOL RANKINGS (Averaged)
----------------------------------------
#1  Tavily      89.9  (Best search quality)
#2  Jina        84.5  (Fastest, cheapest)
#3  Firecrawl   81.0

Tool Details:
  Tavily:
    - Avg search quality: 89.9
    - Avg search time: 2.1s
    - Avg cost: $0.012/query
    - Error rate: 1%

  Jina:
    - Avg search quality: 84.5
    - Avg search time: 1.5s
    - Avg cost: $0.00/query (FREE!)
    - Error rate: 3%

  Firecrawl:
    - Avg search quality: 81.0
    - Avg search time: 3.2s
    - Avg cost: $0.025/query
    - Error rate: 2%

----------------------------------------
LLM RANKINGS (Averaged)
----------------------------------------
#1  Claude      88.2  (Best answer quality)
#2  GPT-4       84.0  (Good balance)
#3  Gemini      78.5

LLM Details:
  Claude:
    - Avg answer quality: 88.2
    - Avg generation time: 1.3s
    - Avg cost: $0.022/query
    - Tokens/query: 850

  GPT-4:
    - Avg answer quality: 84.0
    - Avg generation time: 1.1s
    - Avg cost: $0.018/query
    - Tokens/query: 720

  Gemini:
    - Avg answer quality: 78.5
    - Avg generation time: 0.9s
    - Avg cost: $0.008/query
    - Tokens/query: 650

----------------------------------------
RECOMMENDATIONS
----------------------------------------

✅ BEST QUALITY (Customer-facing chatbot)
   Combination: Tavily + Claude
   - Overall score: 91.2/100
   - Answer quality: 93.3/100
   - Cost: $0.034/query
   - Speed: 3.0s average

💰 BEST VALUE (Internal tool)
   Combination: Jina + GPT-4
   - Overall score: 83.7/100
   - Answer quality: 84.0/100
   - Cost: $0.018/query (47% cheaper!)
   - Speed: 2.6s average

⚡ BEST SPEED (High-volume queries)
   Combination: Jina + Gemini
   - Overall score: 78.2/100
   - Answer quality: 78.5/100
   - Cost: $0.008/query
   - Speed: 2.4s average (fastest!)

🎯 OUR RECOMMENDATION
   Combination: Tavily + Claude
   Reason: Best overall quality for customer chatbot.
           Cost acceptable for value provided.

========================================
```

---

## Testing Workflow

### 1. Collect NotebookLLM Baseline (Once)
```bash
python scripts/collect_notebookllm_baseline.py
```
- Ask all 25 questions to NotebookLLM
- Record answers, sources, timing
- Saves to: `test_results/ground_truth/notebookllm_baseline.json`

Time: ~2-3 hours (manual process)

---

### 2. Test Each Combination (Automated)
```bash
# Test tavily + claude
python scripts/run_evaluation.py --mcp tavily --llm claude

# Test tavily + gpt4
python scripts/run_evaluation.py --mcp tavily --llm gpt4

# Test jina + claude
python scripts/run_evaluation.py --mcp jina --llm claude

# ... etc for all combinations
```

Per combination:
- Runs all 25 questions
- Collects metrics per query
- Compares to NotebookLLM baseline
- Saves to: `test_results/{mcp}_{llm}/results.json`

Time: ~15-20 min per combination

---

### 3. Generate Comparison Report
```bash
python scripts/generate_comparison_report.py
```
- Loads all combination results
- Computes rankings
- Identifies winner
- Saves to: `test_results/comparison_report.txt`

Time: Instant

---

### 4. Manual Quality Review (Sampling)
Pick 5-10 questions and manually review:
- Is the search result relevant?
- Is the answer accurate?
- Are sources cited correctly?
- How does it compare to NotebookLLM?

Update scores in results.json if needed.

Time: ~30 minutes

---

## Key Metrics Summary

| Metric Category | What It Measures | Used For |
|----------------|------------------|----------|
| **Search Quality** | How good is MCP tool at finding info | Rank MCP tools |
| **Answer Quality** | How good is LLM at generating answers | Rank LLMs |
| **Performance** | Speed + Cost | Practical constraints |
| **Overall Score** | Combined quality | Find best combination |
| **Tool Isolation** | MCP tool quality alone | Which MCP to use |
| **LLM Isolation** | LLM quality alone | Which LLM to use |
| **Synergy** | Combination bonus | Best pairings |

---

## Questions We Can Answer

### 1. Which MCP tool is best?
Compare average search quality across all LLMs:
```
Tavily: 89.9
Jina: 84.5
Firecrawl: 81.0

Winner: Tavily
```

### 2. Which LLM is best?
Compare average answer quality across all MCP tools:
```
Claude: 88.2
GPT-4: 84.0
Gemini: 78.5

Winner: Claude
```

### 3. Which combination is best?
Look at overall scores:
```
Tavily + Claude: 91.2

Winner: Tavily + Claude
```

### 4. What's the cost/quality tradeoff?
```
Highest quality: Tavily + Claude ($0.034, score: 91.2)
Best value: Jina + GPT-4 ($0.018, score: 83.7)
Cheapest: Jina + Gemini ($0.008, score: 78.2)

Pick based on priorities!
```

### 5. How do we compare to NotebookLLM?
```
NotebookLLM baseline quality: ~90/100

Tavily + Claude: 91.2 (BETTER!)
Tavily + GPT-4: 88.5 (slightly worse)
Jina + Claude: 85.3 (noticeably worse)

We can match or beat NotebookLLM!
```

---

## Adding New MCP Tool to Evaluation

### Step 1: Implement tool
```python
class NewTool(MCPTool):
    def search(self, question, context=None):
        # Implementation
        pass
```

### Step 2: Add to config
```yaml
mcp_tools:
  newtool:
    name: "New Tool"
    class: "NewTool"
```

### Step 3: Test it
```bash
python scripts/run_evaluation.py --mcp newtool --llm claude
python scripts/run_evaluation.py --mcp newtool --llm gpt4
```

### Step 4: Generate new report
```bash
python scripts/generate_comparison_report.py
```

Automatically includes new tool in rankings!

---

## Summary

**Simple, controlled testing:**
- User picks MCP tool + LLM (dropdowns)
- System uses exactly those components
- Measure search quality + answer quality separately
- Find best combination

**Clean metrics:**
- Search quality (MCP tool)
- Answer quality (LLM)
- Performance (speed + cost)
- Overall score (weighted combination)

**Clear output:**
- Ranked list of combinations
- Best MCP tool identified
- Best LLM identified
- Recommendation for use case

**Easy to extend:**
- Add new MCP tool → test with all LLMs
- Add new LLM → test with all MCP tools
- Framework handles everything

**Goal achieved:**
Find the best MCP tool + LLM combination for our chatbot!
