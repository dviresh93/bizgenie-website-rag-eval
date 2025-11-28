# Evaluation Metrics for Agentic Real-time Search

**Last Updated**: 2025-01-26

---

## Metrics Comparison: Static RAG vs Agentic Search

### ❌ OLD METRICS (Static RAG - No longer applicable)

**Indexing Phase (REMOVED):**
- ❌ Time to index website
- ❌ Number of pages indexed
- ❌ Cost of indexing
- ❌ Storage size in ChromaDB
- ❌ Chunking quality
- ❌ Embedding quality

**Query Phase (OLD):**
- Vector retrieval accuracy
- Retrieval time (ChromaDB lookup)
- Number of chunks retrieved
- LLM response time
- Answer quality
- Cost per query (LLM only)

**Total evaluation time**: ~30 min per config (index once + 25 queries)

---

### ✅ NEW METRICS (Agentic Real-time Search)

**No Indexing Phase** - All metrics are per-query

**Per-Query Metrics:**

#### 1. Agent Behavior Metrics (NEW!)
- **Tool Usage Pattern**
  - Which tools did agent choose? (Jina, Tavily, both, neither)
  - Number of tool calls per query
  - Tool selection appropriateness (did it choose the right tool?)
  - Multi-tool coordination (used multiple tools effectively?)

- **Agent Reasoning Quality**
  - Did agent identify need for search?
  - Search query formulation quality
  - Iterative refinement (did agent search again if needed?)
  - Decision to stop (agent knew when it had enough info)

#### 2. Search Quality Metrics (NEW!)
- **Search Relevance**
  - Did search return relevant content?
  - Content coverage (found all needed info?)
  - Source quality (authoritative sources?)
  - Freshness (current information?)

- **Search Efficiency**
  - Time per search operation
  - Number of searches needed
  - Search result utilization (% of search results used in answer)

#### 3. Performance Metrics (UPDATED)
- **Latency Breakdown**
  - Total response time
  - Search time (sum of all tool calls)
  - LLM time (sum of all agent iterations)
  - Agent overhead (thinking time between tools)
  - Time per iteration

- **Cost Breakdown**
  - Search tool costs (Jina free, Tavily paid)
  - LLM costs (per token, per iteration)
  - Total cost per query
  - Cost per tool call
  - Cost efficiency (cost vs quality ratio)

#### 4. Answer Quality Metrics (SIMILAR but context-aware)
- **Accuracy**
  - Factual correctness
  - Up-to-date information (real-time benefit)
  - No hallucinations
  - Comparison to NotebookLLM baseline

- **Completeness**
  - Addressed all parts of question
  - Sufficient detail
  - Used information from all tool calls

- **Source Attribution**
  - Clear source citations
  - Source URLs provided
  - Traceability to tool calls

#### 5. Reliability Metrics (NEW!)
- **Error Handling**
  - Tool call failures
  - Graceful degradation
  - Retry behavior
  - Fallback strategies

- **Consistency**
  - Same question → similar tool usage?
  - Same question → consistent quality?
  - Variance across runs

---

## Detailed Metric Definitions

### 1. Agent Decision Quality Score (0-100)

Evaluates how well the agent used its tools:

```python
agent_decision_score = (
    tool_selection_appropriateness * 0.40 +  # Right tools for the task?
    search_query_quality * 0.30 +             # Well-formulated queries?
    iteration_efficiency * 0.20 +             # Not too many/few iterations?
    multi_tool_coordination * 0.10            # Used tools together well?
)
```

**Evaluation criteria:**

- **Tool Selection (40%)**
  - 100: Perfect tool choice (e.g., Tavily for broad search, Jina for specific URL)
  - 70: Suboptimal but works (e.g., Jina when Tavily would be better)
  - 0: Wrong tool or no tools when needed

- **Search Query Quality (30%)**
  - 100: Query perfectly captures information need
  - 70: Query is adequate but could be better
  - 0: Query is irrelevant or poorly formed

- **Iteration Efficiency (20%)**
  - 100: Optimal number of iterations (2-3 for complex questions)
  - 70: Too many iterations (>5) or too few (1 for complex question)
  - 0: Excessive iterations (>10) or gave up too early

- **Multi-tool Coordination (10%)**
  - 100: Used multiple tools strategically (e.g., Jina for specific URL, then Tavily for context)
  - 70: Used multiple tools but redundantly
  - 0: Should have used multiple tools but didn't

---

### 2. Search Quality Score (0-100)

Evaluates the quality of information retrieved:

```python
search_quality_score = (
    relevance * 0.40 +        # Found relevant content?
    coverage * 0.30 +          # Found all needed info?
    source_quality * 0.20 +    # Authoritative sources?
    freshness * 0.10           # Current information?
)
```

**Measurement:**

- **Relevance**: Manual review - does retrieved content match question?
- **Coverage**: Did search find all information needed for complete answer?
- **Source Quality**: Are sources authoritative? (e.g., official site vs random blog)
- **Freshness**: Is information current? (matters for pricing, features, etc.)

---

### 3. Performance Score (0-100)

Evaluates speed and cost:

```python
performance_score = (
    speed_score * 0.50 +      # Faster is better
    cost_score * 0.30 +        # Cheaper is better
    reliability_score * 0.20   # Fewer errors is better
)
```

**Speed Score:**
```python
# Baseline: 5 seconds acceptable, <3 excellent, >10 poor
if total_time < 3:
    speed_score = 100
elif total_time < 5:
    speed_score = 90 - (total_time - 3) * 10
elif total_time < 10:
    speed_score = 70 - (total_time - 5) * 10
else:
    speed_score = max(0, 20 - (total_time - 10) * 2)
```

**Cost Score:**
```python
# Baseline: $0.05/query acceptable, <$0.02 excellent, >$0.10 poor
if cost < 0.02:
    cost_score = 100
elif cost < 0.05:
    cost_score = 90 - (cost - 0.02) * 333
elif cost < 0.10:
    cost_score = 70 - (cost - 0.05) * 400
else:
    cost_score = max(0, 20 - (cost - 0.10) * 100)
```

**Reliability Score:**
```python
error_rate = errors / total_queries
reliability_score = max(0, 100 - (error_rate * 500))
```

---

### 4. Overall Score (0-100)

Weighted combination of all metrics:

```python
overall_score = (
    answer_quality * 0.40 +        # Most important
    agent_decision_quality * 0.25 + # Agentic behavior matters
    search_quality * 0.20 +         # Search effectiveness
    performance * 0.15              # Speed/cost/reliability
)
```

---

## What We're Actually Comparing

### Configuration Types

**OLD Comparison (Static RAG):**
```
Config 1: Jina (indexing) + GPT-4 (generation)
Config 2: Tavily (indexing) + GPT-4 (generation)
Config 3: Jina (indexing) + Claude (generation)
```

**NEW Comparison (Agentic):**
```
Config 1: Claude Agent + [Jina tool]
Config 2: Claude Agent + [Tavily tool]
Config 3: Claude Agent + [Jina + Tavily tools]
Config 4: GPT-4 Agent + [Jina tool]
Config 5: GPT-4 Agent + [Tavily tool]
Config 6: GPT-4 Agent + [Jina + Tavily tools]
```

**Key difference**: Now testing **agent + tool combinations**, not just pipeline components

---

## Example Test Results Format

### OLD Format (Static RAG)
```json
{
  "config": "jina_gpt4",
  "indexing_metrics": {
    "time": 45.2,
    "pages": 15,
    "cost": 0.12
  },
  "query_metrics": {
    "avg_response_time": 2.3,
    "avg_cost": 0.02,
    "answer_quality": 85
  }
}
```

### NEW Format (Agentic)
```json
{
  "config": "claude_jina_tavily",
  "query": "What services does BizGenie offer?",
  "agent_behavior": {
    "tools_used": ["jina_search", "tavily_search"],
    "tool_calls": [
      {
        "iteration": 1,
        "tool": "jina_search",
        "query": "BizGenie services site:bizgenieai.com",
        "time": 1.8,
        "cost": 0.00,
        "result_quality": 90
      },
      {
        "iteration": 2,
        "tool": "tavily_search",
        "query": "BizGenie AI automation pricing",
        "time": 2.1,
        "cost": 0.01,
        "result_quality": 85
      }
    ],
    "iterations": 2,
    "reasoning_quality": 88,
    "tool_selection_score": 92
  },
  "performance": {
    "total_time": 5.2,
    "search_time": 3.9,
    "llm_time": 1.3,
    "total_cost": 0.032,
    "tokens_used": 1250
  },
  "answer_quality": {
    "accuracy": 95,
    "completeness": 90,
    "source_attribution": 100,
    "comparison_to_baseline": 0.88
  },
  "overall_score": 89
}
```

---

## Key Metrics to Track Per Configuration

### Summary Metrics (Aggregated over 25 questions)

| Metric | Description | Target |
|--------|-------------|--------|
| **Overall Score** | Weighted score (0-100) | ≥ 85 |
| **Answer Quality** | Accuracy + completeness | ≥ 90 |
| **Agent Decision Quality** | Tool usage effectiveness | ≥ 80 |
| **Search Quality** | Relevance + coverage | ≥ 85 |
| **Avg Response Time** | Total time per query | < 5s |
| **Avg Cost** | Total cost per query | < $0.05 |
| **Error Rate** | % queries with errors | < 2% |
| **Tool Usage Pattern** | Which tools used | Varies |
| **Avg Iterations** | Agent loops per query | 2-3 |

---

## Testing Workflow Changes

### OLD Workflow (Static)
```
1. Index website (30 min)
2. Run 25 queries (5 min)
3. Collect metrics
4. Switch to new config
5. Re-index website (30 min)
6. Run same 25 queries (5 min)
7. Compare results

Total: ~1.5 hours per config
```

### NEW Workflow (Agentic)
```
1. Configure agent + tools
2. Run 25 queries (agent searches in real-time)
   - Each query: agent decides → uses tools → answers
   - Collect per-query metrics
3. Switch to new agent/tool combo
4. Run same 25 queries
5. Compare results

Total: ~15-30 min per config (much faster!)
```

**Why faster?**
- No indexing phase
- Parallel possible (no dependencies)
- Real-time means no pre-processing

---

## Baseline: NotebookLLM Comparison

**Why NotebookLLM is perfect baseline:**
- NotebookLLM is also agentic (Gemini with search tools)
- Does real-time search like our system
- Good quality answers
- Fair comparison

**What we compare:**
1. **Answer Quality**: Our agent vs NotebookLLM
2. **Speed**: Our system vs NotebookLLM (we can measure)
3. **Cost**: Our system (we know) vs NotebookLLM (free but we'd estimate)
4. **Tool Usage**: Our agent's decisions vs NotebookLLM's decisions (inferred)

---

## New Questions We Can Answer

**OLD Evaluation could answer:**
- Which MCP server indexes better content?
- Which LLM generates better answers from static data?
- What's the cost/quality tradeoff?

**NEW Evaluation can answer:**
- **Which agent is smarter?** (Claude vs GPT-4 tool usage)
- **Which tool is more effective?** (Jina vs Tavily for real-time)
- **Should agent have multiple tools?** (Jina+Tavily vs single tool)
- **How does agent adapt?** (different questions → different tool patterns)
- **What's the quality/speed/cost sweet spot?** (with agent behavior)
- **How does our agent compare to NotebookLLM?** (both agentic)

---

## Example Insights We Can Get

### Insight 1: Agent Tool Selection Patterns
```
Easy factual questions:
  - Claude: 80% single Jina call
  - GPT-4: 60% single Tavily call

Complex multi-part questions:
  - Claude: 70% use both tools (Jina + Tavily)
  - GPT-4: 40% use both tools

Conclusion: Claude better at multi-tool coordination
```

### Insight 2: Cost vs Quality
```
Claude + Jina only:
  - Avg cost: $0.018
  - Avg quality: 82
  - Cost per quality point: $0.00022

Claude + Tavily only:
  - Avg cost: $0.045
  - Avg quality: 89
  - Cost per quality point: $0.00051

Claude + Both:
  - Avg cost: $0.038
  - Avg quality: 91
  - Cost per quality point: $0.00042

Conclusion: Both tools = best quality for reasonable cost
```

### Insight 3: Speed Analysis
```
Average response time breakdown:
  - Claude + Jina: 3.2s (search: 1.5s, LLM: 1.7s)
  - Claude + Tavily: 4.8s (search: 2.9s, LLM: 1.9s)
  - GPT-4 + Jina: 2.9s (search: 1.5s, LLM: 1.4s)

Conclusion: GPT-4 faster, Claude slightly better quality
```

---

## Summary: Key Metric Changes

| Aspect | Old Metrics | New Metrics |
|--------|-------------|-------------|
| **Indexing** | ✅ Critical | ❌ Not applicable |
| **Agent Behavior** | ❌ N/A | ✅ Critical (NEW) |
| **Search Quality** | ❌ N/A | ✅ Critical (NEW) |
| **Tool Selection** | ❌ Fixed | ✅ Dynamic (NEW) |
| **Iterations** | ❌ Single-pass | ✅ Multi-iteration (NEW) |
| **Cost Breakdown** | LLM only | Search + LLM + iterations |
| **Time Breakdown** | Retrieval + LLM | Search + LLM + agent overhead |
| **Comparison Basis** | Pipeline configs | Agent + tool combos |
| **Test Duration** | ~1.5hrs/config | ~20min/config |

---

## What This Means for Testing

**More metrics to track** but **faster to run**:
- More complex per-query data
- Agent behavior adds new dimension
- But no indexing phase = much faster overall

**Better insights**:
- Understand agent decision-making
- Compare agent intelligence (Claude vs GPT-4)
- Optimize tool combinations
- Real apples-to-apples with NotebookLLM

**Ready to implement?**
This evaluation framework is designed for agentic systems!
