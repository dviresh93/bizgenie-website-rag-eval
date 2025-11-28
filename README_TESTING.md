# RAG System Testing Framework - Simple Guide

## What This Does

Tests different combinations of tools to find the best one for your chatbot:
- **MCP Servers**: Jina, Tavily, Firecrawl (data retrieval)
- **LLMs**: GPT-4, Claude (answer generation)
- **Baseline**: NotebookLLM (quality ground truth)

**Goal**: Answer "Which combination is best?" with data.

---

## Quick Start (3 Steps)

### Step 1: Collect NotebookLLM Baseline (One-time, 2-3 hours)

```bash
# 1. Open NotebookLLM (https://notebooklm.google.com/)
# 2. Add your website content
# 3. Run script to record responses

python scripts/collect_notebookllm_baseline.py

# This asks you to:
# - Ask each of 25 questions to NotebookLLM
# - Paste the responses
# - Record sources and timing
```

**Output**: `test_results/ground_truth/notebookllm_baseline.json`

### Step 2: Test Your Configurations (30 min each)

```bash
# Make sure services running
docker-compose up -d

# Test each configuration
python scripts/run_evaluation.py --config jina_gpt4
python scripts/run_evaluation.py --config tavily_gpt4
python scripts/run_evaluation.py --config jina_claude
python scripts/run_evaluation.py --config tavily_claude
```

**What happens**:
- Indexes website
- Asks all 25 questions
- Measures speed, cost, quality
- Saves results

**Output**: `test_results/{config_name}/results.json`

### Step 3: See Which Is Best (Instant)

```bash
python scripts/generate_comparison_report.py
cat test_results/comparison_report.txt
```

**Output**: Clear winner + recommendations

---

## What You Get

### Simple Text Report

```
Winner: tavily_gpt4 (Score: 84.2/100)

Rankings:
  #1  tavily_gpt4    84.2    Best quality (88.5)
  #2  jina_gpt4      81.3    Fastest (2.3s)
  #3  tavily_claude  79.8    Good balance
  #4  jina_claude    77.5    Cheapest ($0.020)

Recommendations:
  • Customer-facing chatbot → tavily_gpt4 (best quality)
  • Internal knowledge base → jina_claude (lowest cost)
  • High-volume queries     → jina_gpt4 (fastest)
```

That's it. You know which to use.

---

## How It Works

### Scoring (Simplified)

Each configuration gets scored 0-100 based on:

1. **Answer Quality (40%)**: How good are the answers?
   - Compare to NotebookLLM baseline
   - Manual review of accuracy, completeness

2. **Performance (30%)**: How fast and cheap?
   - Response time
   - Cost per query
   - Error rate

3. **Similarity (30%)**: How close to NotebookLLM?
   - Automated: BLEU score, semantic similarity
   - Shows if answers match baseline quality

**Higher score = better overall**

### What Gets Measured

**Indexing Phase** (MCP Server):
- Time to index website
- Pages retrieved
- Cost

**Query Phase** (LLM):
- Response time per question
- Tokens used
- Cost per query
- Answer quality

**Comparison**:
- How close to NotebookLLM (baseline)
- Overall score

---

## Adding New Tools (Optional)

### Want to test a new MCP server or LLM?

**1. Create plugin file**: `api/app/plugins/data_retrieval/your_plugin.py`

**2. Implement interface**:
```python
class YourPlugin(DataRetrievalPlugin):
    def fetch_url(self, url: str) -> StandardDocument:
        # Your code here
        pass
```

**3. Add to config**: `config/configs.yaml`
```yaml
your_config:
  data_retrieval:
    plugin: "your_plugin"
  llm:
    plugin: "gpt4"
```

**4. Test**:
```bash
python scripts/run_evaluation.py --config your_config
python scripts/generate_comparison_report.py
```

Framework automatically includes it!

---

## Files Structure

```
website-rag/
├── README_TESTING.md              ← This file (read this!)
│
├── config/
│   └── test_suites/
│       └── standard_questions.json  ← 25 test questions
│
├── scripts/
│   ├── collect_notebookllm_baseline.py  ← Step 1
│   ├── run_evaluation.py                ← Step 2
│   └── generate_comparison_report.py    ← Step 3
│
└── test_results/                   ← Generated results
    ├── ground_truth/
    │   └── notebookllm_baseline.json
    ├── {config_name}/results.json
    └── comparison_report.txt
```

---

## Manual Review (Important)

After automated tests, **manually review** a sample of answers:

1. Open `test_results/{config_name}/results.json`
2. Read 5-10 answers
3. Score based on:
   - ✓ Accurate?
   - ✓ Complete?
   - ✓ Makes sense?
   - ✓ No hallucinations?

Update the scores in the JSON if needed.

---

## Common Commands

```bash
# Collect baseline (once)
python scripts/collect_notebookllm_baseline.py

# Test a config
python scripts/run_evaluation.py --config jina_gpt4

# Skip re-indexing (faster re-runs)
python scripts/run_evaluation.py --config jina_gpt4 --skip-indexing

# Compare all results
python scripts/generate_comparison_report.py

# View report
cat test_results/comparison_report.txt
```

---

## Decision Guide

### How to Choose

**Scenario 1**: Customer-facing chatbot
- **Priority**: Quality
- **Choose**: Highest quality score (likely tavily_gpt4)
- **Accept**: Higher cost

**Scenario 2**: Internal knowledge base
- **Priority**: Cost
- **Choose**: Lowest cost (likely jina_claude)
- **Accept**: Slightly lower quality

**Scenario 3**: High-volume queries
- **Priority**: Speed
- **Choose**: Fastest response time (likely jina_gpt4)
- **Accept**: Medium quality

**Scenario 4**: Balanced
- **Priority**: Overall score
- **Choose**: Highest overall score
- **Balance**: All factors

---

## Success Criteria

A configuration is **production-ready** if:
- Overall Score ≥ 80
- No critical errors
- Acceptable quality (manual review)
- Meets your speed/cost requirements

---

## Troubleshooting

**"No baseline file found"**
→ Run `python scripts/collect_notebookllm_baseline.py` first

**"API connection refused"**
→ Run `docker-compose up -d`

**"API key not set"**
→ Check `.env` file has all keys

---

## That's It!

Three steps:
1. Collect NotebookLLM baseline
2. Test configurations
3. Read comparison report

You'll know exactly which tool combination to use.

---

## Advanced (Optional)

For detailed information:
- Complex scoring: See `EVALUATION_RUBRIC.md`
- Performance details: See `PERFORMANCE_ANALYSIS.md`
- Plugin development: See `ADDING_NEW_PLUGINS.md`

But for most uses, **this guide is enough**.
