# Performance Measurement Quick Reference

## What Gets Measured and When

```
┌─────────────────────────────────────────────────────────────┐
│                    INDEXING PHASE                           │
│              (Measures MCP Server Performance)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Website URL → [MCP Server] → ChromaDB                      │
│                     ↓                                       │
│              Measure These:                                 │
│              • Indexing Time                                │
│              • Pages Retrieved                              │
│              • Indexing Cost                                │
│              • Content Quality                              │
│              • Error Rate                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     QUERY PHASE                             │
│         (Measures Retrieval + LLM Performance)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Question → [Retrieval] → [LLM] → Answer                    │
│                 ↓            ↓                              │
│           Retrieval:      LLM:                              │
│           • Chunks        • Tokens Used                     │
│           • Relevance     • Response Time                   │
│                           • Cost                            │
│                           • Answer Quality                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Comparison Strategy

### To Compare MCP Servers (Jina vs Tavily)

**Use the SAME LLM for both**

```
Test 1: jina_gpt4      ← Jina + GPT-4
Test 2: tavily_gpt4    ← Tavily + GPT-4
        ↓
Compare indexing metrics + retrieval accuracy
```

**What to Compare:**
- Indexing speed
- Indexing cost
- Pages found
- Retrieval accuracy
- Content quality

---

### To Compare LLMs (GPT-4 vs Claude)

**Use the SAME MCP Server for both**

```
Test 1: jina_gpt4      ← Jina + GPT-4
Test 2: jina_claude    ← Jina + Claude
        ↓
Compare query metrics + answer quality
```

**What to Compare:**
- Response time
- Tokens used
- Query cost
- Answer quality
- Token efficiency

---

## Example Test Matrix

```
┌──────────────────────────────────────────────────────────┐
│  Test 4 Configurations (2 MCP × 2 LLMs)                  │
├────────────┬─────────────────┬───────────────────────────┤
│            │     GPT-4       │        Claude             │
├────────────┼─────────────────┼───────────────────────────┤
│   Jina     │  jina_gpt4      │    jina_claude            │
│            │  Config 1       │    Config 3               │
├────────────┼─────────────────┼───────────────────────────┤
│  Tavily    │  tavily_gpt4    │    tavily_claude          │
│            │  Config 2       │    Config 4               │
└────────────┴─────────────────┴───────────────────────────┘

Comparisons:
→ Horizontal: Compare MCP servers (same LLM)
↓ Vertical: Compare LLMs (same MCP server)
```

---

## Stored Performance Data

### Indexing Metrics (Per Configuration)

**File**: `test_results/{config_name}/results.json`

```json
{
  "indexing_metrics": {
    "total_time_seconds": 45.2,     ← MCP Server speed
    "pages_indexed": 15,             ← MCP Server coverage
    "total_chunks": 234,             ← Chunking result
    "total_cost": 0.12,              ← MCP Server cost
    "error_rate": 0.0                ← MCP Server reliability
  }
}
```

### Query Metrics (Per Question)

**File**: `test_results/{config_name}/results.json`

```json
{
  "query_results": [
    {
      "question_id": "q001",
      "metrics": {
        "response_time_seconds": 2.3,  ← Total time (retrieval + LLM)
        "tokens_used": 456,            ← LLM token usage
        "cost": 0.023,                 ← LLM cost
        "chunks_retrieved": 5,         ← Retrieval count
        "avg_chunk_relevance": 0.85    ← Retrieval quality
      }
    }
  ]
}
```

---

## NotebookLLM's Role

```
┌─────────────────────────────────────────────────────────┐
│  NotebookLLM is NOT measured for performance!           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  It's ONLY used as:                                     │
│  ✓ Ground truth for answer quality                     │
│  ✓ Baseline for comparison                             │
│                                                         │
│  We DON'T measure:                                      │
│  ✗ NotebookLLM speed                                   │
│  ✗ NotebookLLM cost                                    │
│  ✗ NotebookLLM performance                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Decision Tree

```
Which configuration is FASTEST?
→ Compare: response_time_seconds
→ Winner: Lowest average time

Which configuration is CHEAPEST?
→ Compare: indexing_cost + (query_cost × expected_queries)
→ Winner: Lowest total cost

Which configuration is BEST QUALITY?
→ Compare: answer_quality_score
→ Winner: Highest quality score

Which configuration is MOST RELIABLE?
→ Compare: error_rate
→ Winner: Lowest error rate

Which configuration is BEST OVERALL?
→ Use: overall_score formula
→ Winner: Highest overall score
```

---

## Performance Score Formula

```python
Performance Score (0-100) =
  Response Time Score    × 20%  ← Speed
+ Cost Efficiency Score  × 15%  ← Economics
+ Retrieval Accuracy     × 25%  ← Quality of retrieval
+ Reliability Score      × 20%  ← Error rate
+ Token Efficiency       × 20%  ← LLM efficiency
```

---

## Real Example

### Scenario: Testing 2 Configurations

**Configuration A: jina_gpt4**
```
Indexing: 45s, $0, 15 pages
Query Avg: 2.3s, 450 tokens, $0.023
Quality: 85/100
Retrieval: 80% relevant
Errors: 0%
```

**Configuration B: tavily_gpt4**
```
Indexing: 62s, $0.18, 18 pages
Query Avg: 2.8s, 460 tokens, $0.024
Quality: 88/100
Retrieval: 90% relevant
Errors: 0%
```

### Analysis

**Speed Winner**: Jina (2.3s vs 2.8s)
**Cost Winner**: Jina ($0 vs $0.18 indexing)
**Quality Winner**: Tavily (88 vs 85)
**Retrieval Winner**: Tavily (90% vs 80%)

**Overall Winner**: Depends on priority!
- Need best quality? → **Tavily**
- Need lowest cost? → **Jina**
- Need fastest? → **Jina**

---

## Data Collection Checklist

### Automatic (Script Collects)
- ✅ Indexing time
- ✅ Indexing cost
- ✅ Pages indexed
- ✅ Response time
- ✅ Tokens used
- ✅ Query cost
- ✅ Chunks retrieved

### Manual (You Evaluate)
- ✅ Answer quality score
- ✅ Retrieval relevance (are chunks actually relevant?)
- ✅ Content quality assessment

---

## Files to Review for Performance

1. **Indexing performance**:
   - Look at: `indexing_metrics` section
   - Compare: Different MCP servers

2. **LLM performance**:
   - Look at: `metrics` per question
   - Compare: Different LLMs with same MCP server

3. **Overall performance**:
   - Look at: `aggregate_metrics` section
   - Compare: All configurations

---

**Bottom Line**:
- MCP Server performance = Indexing metrics + Retrieval accuracy
- LLM performance = Response time + Tokens + Cost + Quality
- NotebookLLM = Quality baseline only, not measured for performance
