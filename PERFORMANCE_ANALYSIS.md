# Performance Analysis Guide

## Overview

This document explains how we measure and compare the **performance** of different tools:
- **Data Retrieval Tools** (MCP Servers): Jina, Tavily, Firecrawl
- **LLMs**: Claude, GPT-4

**Note**: NotebookLLM is ONLY used as ground truth for answer quality. We don't measure its performance.

---

## Performance Metrics by Component

### 1. Data Retrieval Performance (MCP Servers)

**When Measured**: During the **indexing phase**

**What We Measure**:

| Metric | Description | How It's Collected | Why It Matters |
|--------|-------------|-------------------|----------------|
| **Indexing Time** | Time to fetch and process all pages | API returns `total_time_seconds` | Speed of content extraction |
| **Pages Indexed** | Number of pages successfully retrieved | API returns `documents_processed` | Coverage of website |
| **Total Chunks** | Number of text chunks created | API returns `total_chunks` | Content granularity |
| **Indexing Cost** | API costs for retrieval | API returns `total_cost` | Economic efficiency |
| **Content Quality** | Word count, completeness | Analyzed from stored content | Data quality |
| **Error Rate** | % of pages that failed | Count failures / total attempts | Reliability |

**Where It's Stored**:
```json
// In test_results/{config_name}/results.json
{
  "indexing_metrics": {
    "total_time_seconds": 45.2,
    "pages_indexed": 15,
    "total_chunks": 234,
    "total_cost": 0.12,
    "error_rate": 0.0,
    "avg_words_per_page": 850
  }
}
```

---

### 2. Query Performance (Retrieval + LLM Combined)

**When Measured**: During the **query phase** (asking questions)

**What We Measure**:

| Metric | Description | How It's Collected | Why It Matters |
|--------|-------------|-------------------|----------------|
| **Response Time** | Total time from question to answer | Measured by evaluation script | User experience |
| **LLM Tokens Used** | Tokens consumed by LLM | API returns `tokens_used` | LLM efficiency |
| **Query Cost** | API costs per question | Calculated from tokens | Economic efficiency |
| **Chunks Retrieved** | Number of context chunks | API returns `chunks_retrieved` | Retrieval efficiency |
| **Retrieval Accuracy** | % of relevant chunks | Manual review + distance scores | Retrieval quality |

**Where It's Stored**:
```json
// In test_results/{config_name}/results.json
{
  "query_results": [
    {
      "question_id": "q001",
      "metrics": {
        "response_time_seconds": 2.3,
        "tokens_used": 456,
        "cost": 0.023,
        "chunks_retrieved": 5,
        "avg_chunk_relevance": 0.85
      }
    }
  ]
}
```

---

### 3. LLM-Specific Performance

**How to Isolate LLM Performance**:

Since query performance includes both retrieval + LLM, to compare LLMs fairly:

| Metric | How to Measure | Comparison |
|--------|----------------|------------|
| **LLM Speed** | Compare response_time for same retrieval plugin | jina_gpt4 vs jina_claude |
| **LLM Cost** | Compare tokens_used and cost | GPT-4 vs Claude pricing |
| **LLM Quality** | Compare answer_quality_score | Which LLM gives better answers |
| **Token Efficiency** | quality_score / tokens_used | Which LLM is more efficient |

**Example Comparison**:
```
Configuration A: jina_gpt4
- Response Time: 2.3s
- Tokens: 450
- Cost: $0.023
- Quality: 85/100

Configuration B: jina_claude  (same retrieval, different LLM)
- Response Time: 2.5s
- Tokens: 420
- Cost: $0.020
- Quality: 82/100

Conclusion: GPT-4 is faster and higher quality, Claude is cheaper
```

---

## Comparison Framework

### A. Comparing Data Retrieval Tools (MCP Servers)

To isolate retrieval tool performance, **use the same LLM**:

**Example: Jina vs Tavily (both with GPT-4)**

```
┌─────────────────────────────────────────────────────────────┐
│ Data Retrieval Comparison                                   │
├──────────────┬──────────────────┬──────────────────────────┤
│ Metric       │ jina_gpt4        │ tavily_gpt4              │
├──────────────┼──────────────────┼──────────────────────────┤
│ INDEXING PHASE (MCP Server Performance)                     │
├──────────────┼──────────────────┼──────────────────────────┤
│ Index Time   │ 45.2s            │ 62.3s                    │
│ Pages Found  │ 15               │ 18                       │
│ Index Cost   │ $0.00 (free)     │ $0.18                    │
│ Content Qual │ 850 words/page   │ 920 words/page           │
│ Error Rate   │ 0%               │ 0%                       │
├──────────────┼──────────────────┼──────────────────────────┤
│ QUERY PHASE (Should be similar since same LLM)              │
├──────────────┼──────────────────┼──────────────────────────┤
│ Resp Time    │ 2.3s             │ 2.8s                     │
│ Retrieval    │ 5 chunks, 80% rel│ 5 chunks, 90% rel        │
│ Answer Qual  │ 85/100           │ 88/100                   │
├──────────────┴──────────────────┴──────────────────────────┤
│ WINNER: Tavily - Better content quality and retrieval       │
│ TRADE-OFF: Costs $0.18, slower indexing                     │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight**: Compare indexing metrics + retrieval accuracy to evaluate MCP servers.

---

### B. Comparing LLMs

To isolate LLM performance, **use the same retrieval tool**:

**Example: GPT-4 vs Claude (both with Jina)**

```
┌─────────────────────────────────────────────────────────────┐
│ LLM Comparison                                              │
├──────────────┬──────────────────┬──────────────────────────┤
│ Metric       │ jina_gpt4        │ jina_claude              │
├──────────────┼──────────────────┼──────────────────────────┤
│ INDEXING PHASE (Should be identical - same MCP server)      │
├──────────────┼──────────────────┼──────────────────────────┤
│ Index Time   │ 45.2s            │ 45.2s                    │
│ Pages Found  │ 15               │ 15                       │
│ Index Cost   │ $0.00            │ $0.00                    │
├──────────────┼──────────────────┼──────────────────────────┤
│ QUERY PHASE (LLM Performance)                               │
├──────────────┼──────────────────┼──────────────────────────┤
│ Resp Time    │ 2.3s             │ 2.5s                     │
│ Tokens Used  │ 450              │ 420                      │
│ Query Cost   │ $0.023           │ $0.020                   │
│ Answer Qual  │ 85/100           │ 82/100                   │
│ Token Effic  │ 0.189 qual/token │ 0.195 qual/token         │
├──────────────┴──────────────────┴──────────────────────────┤
│ WINNER: GPT-4 - Faster, higher quality                      │
│ TRADE-OFF: Costs 15% more per query                         │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight**: Compare response time, tokens, cost, and quality to evaluate LLMs.

---

## Aggregate Performance Scores

### Formula for Performance Score (0-100)

```python
Performance Score =
  (Response Time Score × 0.20) +
  (Cost Efficiency Score × 0.15) +
  (Retrieval Accuracy × 0.25) +
  (Reliability Score × 0.20) +
  (Token Efficiency × 0.20)
```

### Component Calculations

**1. Response Time Score**
```python
target_time = 3.0  # seconds
score = max(0, 100 - (actual_time / target_time * 100))

Examples:
- 1.0s → 66.7/100
- 2.0s → 33.3/100
- 3.0s → 0/100
```

**2. Cost Efficiency Score**
```python
target_cost = 0.05  # $ per query
score = max(0, 100 - (actual_cost / target_cost * 100))

Examples:
- $0.01 → 80/100
- $0.025 → 50/100
- $0.05 → 0/100
```

**3. Retrieval Accuracy**
```python
# % of retrieved chunks that are relevant
score = (relevant_chunks / total_chunks) * 100

Examples:
- 5/5 relevant → 100/100
- 4/5 relevant → 80/100
- 3/5 relevant → 60/100
```

**4. Reliability Score**
```python
score = (1 - error_rate) * 100

Examples:
- 0% errors → 100/100
- 2% errors → 98/100
- 5% errors → 95/100
```

**5. Token Efficiency**
```python
# Normalize to 0-100 scale
efficiency = answer_quality_score / tokens_used * 1000
score = min(100, efficiency)

Examples:
- Quality 85, Tokens 450 → 189 → 100/100
- Quality 75, Tokens 600 → 125 → 100/100
- Quality 50, Tokens 800 → 62.5 → 62.5/100
```

---

## Example: Full Performance Analysis

### Scenario: Testing 4 Configurations

```
Config 1: jina_gpt4
Config 2: tavily_gpt4
Config 3: jina_claude
Config 4: tavily_claude
```

### Collected Metrics

```
┌──────────────┬───────────┬────────────┬──────────────┬──────────────┐
│              │ jina_gpt4 │ tavily_gpt4│ jina_claude  │ tavily_claude│
├──────────────┼───────────┼────────────┼──────────────┼──────────────┤
│ INDEXING                                                            │
├──────────────┼───────────┼────────────┼──────────────┼──────────────┤
│ Time (s)     │    45.2   │    62.3    │    45.2      │    62.3      │
│ Cost ($)     │    0.00   │    0.18    │    0.00      │    0.18      │
│ Pages        │    15     │    18      │    15        │    18        │
│ Chunks       │   234     │   289      │   234        │   289        │
├──────────────┼───────────┼────────────┼──────────────┼──────────────┤
│ QUERY (Avg of 25 questions)                                         │
├──────────────┼───────────┼────────────┼──────────────┼──────────────┤
│ Resp Time(s) │    2.3    │    2.8     │    2.5       │    3.0       │
│ Tokens       │   450     │   460      │   420        │   430        │
│ Cost ($)     │   0.023   │   0.024    │   0.020      │   0.021      │
│ Quality      │   85      │   88       │   82         │   85         │
│ Retrieval %  │   80%     │   90%      │   80%        │   90%        │
│ Error Rate   │   0%      │   0%       │   2%         │   0%         │
├──────────────┼───────────┼────────────┼──────────────┼──────────────┤
│ PERFORMANCE SCORE                                                   │
├──────────────┼───────────┼────────────┼──────────────┼──────────────┤
│ Resp Time    │   76.7    │   63.3     │   70.0       │   60.0       │
│ Cost Eff     │   54.0    │   52.0     │   60.0       │   58.0       │
│ Retrieval    │   80.0    │   90.0     │   80.0       │   90.0       │
│ Reliability  │  100.0    │  100.0     │   98.0       │  100.0       │
│ Token Eff    │  100.0    │  100.0     │  100.0       │  100.0       │
├──────────────┼───────────┼────────────┼──────────────┼──────────────┤
│ OVERALL PERF │   82.1    │   81.1     │   81.6       │   81.6       │
└──────────────┴───────────┴────────────┴──────────────┴──────────────┘
```

---

## Analysis Questions to Answer

### Q1: Which MCP Server is Better?

**Compare**: jina_gpt4 vs tavily_gpt4

| Factor | Winner | Reason |
|--------|--------|--------|
| Speed | Jina | 45s vs 62s indexing, 2.3s vs 2.8s query |
| Cost | Jina | Free vs $0.18 + $0.24/query |
| Quality | Tavily | 88/100 vs 85/100 answer quality |
| Retrieval | Tavily | 90% vs 80% relevant chunks |

**Conclusion**: Tavily = better quality, Jina = faster & cheaper

### Q2: Which LLM is Better?

**Compare**: jina_gpt4 vs jina_claude

| Factor | Winner | Reason |
|--------|--------|--------|
| Speed | GPT-4 | 2.3s vs 2.5s |
| Cost | Claude | $0.020 vs $0.023 per query |
| Quality | GPT-4 | 85/100 vs 82/100 |
| Reliability | GPT-4 | 0% vs 2% error rate |

**Conclusion**: GPT-4 = better overall, Claude = cheaper

### Q3: What's the Best Configuration?

**Decision Matrix**:

```
High Quality Needed → tavily_gpt4
  - Best answer quality (88/100)
  - Highest retrieval accuracy (90%)
  - Trade-off: Most expensive

Balanced → jina_gpt4
  - Good quality (85/100)
  - Fastest (2.3s)
  - Free indexing
  - Trade-off: Lower retrieval accuracy

Budget Conscious → jina_claude
  - Acceptable quality (82/100)
  - Cheapest ($0.020/query)
  - Free indexing
  - Trade-off: Slower, 2% errors
```

---

## Data Collection During Testing

### Automatic Collection

The `run_evaluation.py` script automatically collects:

1. **Indexing Metrics** - When calling `/api/v1/index`
   ```python
   index_result = {
       "documents_processed": 15,
       "total_chunks": 234,
       "total_cost": 0.12,
       "time_taken": 45.2
   }
   ```

2. **Query Metrics** - When calling `/api/v1/query`
   ```python
   query_result = {
       "answer": "...",
       "tokens_used": 450,
       "response_time": 2.3,
       "retrieval_stats": {
           "chunks_retrieved": 5,
           "distances": [0.2, 0.3, 0.4, 0.5, 0.6]
       }
   }
   ```

### Manual Collection

You need to manually score:
- Answer quality (accuracy, completeness, etc.)
- Retrieval relevance (are chunks actually relevant?)

---

## Visualization (Future Enhancement)

Create comparison charts:

```
Response Time Comparison
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
jina_gpt4     ████████████████░░░░ 2.3s
tavily_gpt4   ███████████████████░ 2.8s
jina_claude   █████████████████░░░ 2.5s
tavily_claude ████████████████████ 3.0s

Cost Comparison
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
jina_gpt4     ████████████░░░░░░░░ $0.023
tavily_gpt4   █████████████░░░░░░░ $0.024
jina_claude   ██████████░░░░░░░░░░ $0.020
tavily_claude ███████████░░░░░░░░░ $0.021

Quality Comparison
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
jina_gpt4     █████████████████░░░ 85/100
tavily_gpt4   ████████████████████ 88/100
jina_claude   ████████████████░░░░ 82/100
tavily_claude █████████████████░░░ 85/100
```

---

## Summary: What Gets Measured

### Data Retrieval Tools (Jina, Tavily, Firecrawl)
✅ Indexing speed
✅ Indexing cost
✅ Content coverage (pages found)
✅ Content quality (words per page)
✅ Retrieval accuracy (% relevant chunks)
✅ Error rate

### LLMs (GPT-4, Claude)
✅ Response time
✅ Token usage
✅ Query cost
✅ Answer quality (manual scoring)
✅ Token efficiency
✅ Error rate

### Combined System
✅ Overall score (quality + performance + UX)
✅ Cost-benefit ratio
✅ Production readiness

---

**NotebookLLM is ONLY used for answer quality baseline, not performance comparison.**
