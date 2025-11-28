# Quick Start: RAG Testing Framework

## TL;DR - Get Started in 5 Minutes

```bash
cd /home/virus/Documents/repo/bizgenie/website-rag

# 1. Collect NotebookLLM baseline (2-3 hours, one-time)
python scripts/collect_notebookllm_baseline.py

# 2. Test configurations (30 min each)
python scripts/run_evaluation.py --config jina_gpt4
python scripts/run_evaluation.py --config tavily_gpt4

# 3. Generate analytics (instant)
python scripts/generate_comparison_report.py

# 4. View results
cat test_results/comparison_report.txt
```

**Done! You now know which tool combination is best.**

---

## What This Framework Does

✅ **Tests** different combinations of MCP servers + LLMs
✅ **Measures** performance (speed, cost, quality)
✅ **Compares** against NotebookLLM baseline
✅ **Recommends** best configuration for your needs
✅ **Flexible** - easy to add new tools

---

## Your Questions Answered

### Q: How is performance recorded?
**A: Automatically!** When you run evaluations, all metrics (speed, cost, quality) are captured and saved to JSON files.

### Q: Do we get meaningful analytics?
**A: YES!** You get:
- Configuration rankings
- Component analysis (MCP vs LLM)
- Use case recommendations
- Cost projections
- Trade-off analysis

### Q: Can we pick the best tool combination?
**A: YES!** The report tells you:
- Winner overall
- Best for customer-facing
- Best for internal use
- Best for high-volume
- Best value for money

### Q: Can we add new tools easily?
**A: YES!** Adding a new MCP or LLM takes ~1 hour:
1. Create plugin file (30 min)
2. Add config (5 min)
3. Test (25 min)
4. Framework automatically includes it!

---

## Documentation Index

**Start Here:**
- `QUICK_START.md` ← You are here
- `GETTING_STARTED_WITH_TESTING.md` ← Step-by-step guide

**Understand the System:**
- `FRAMEWORK_OVERVIEW.md` ← Complete overview
- `TEST_PLAN.md` ← Full methodology

**Reference:**
- `EVALUATION_RUBRIC.md` ← Scoring guide
- `PERFORMANCE_ANALYSIS.md` ← How performance is measured
- `PERFORMANCE_QUICK_REF.md` ← Quick reference
- `ANALYTICS_AND_INSIGHTS.md` ← What analytics you get

**Extend the Framework:**
- `ADDING_NEW_PLUGINS.md` ← How to add new tools

---

## Example Output

```
================================================================================
RAG SYSTEM EVALUATION REPORT
================================================================================

WINNER: tavily_gpt4 (Score: 84.2/100)

CONFIGURATION RANKINGS
────────────────────────────────────────────────────────────
#1  tavily_gpt4    84.2    88.5 quality    2.8s    $0.0240
#2  jina_gpt4      81.3    85.1 quality    2.3s    $0.0230
#3  tavily_claude  79.8    86.2 quality    3.1s    $0.0210
#4  jina_claude    77.5    82.3 quality    2.5s    $0.0200

COMPONENT ANALYSIS
────────────────────────────────────────────────────────────
MCP Servers:
  tavily: 87.4 quality, slower, more expensive
  jina:   83.7 quality, faster, cheaper

LLMs:
  gpt4:   86.8 quality, faster, more expensive
  claude: 84.3 quality, slower, cheaper

RECOMMENDATIONS
────────────────────────────────────────────────────────────
✓ Customer-facing chatbot    → tavily_gpt4
✓ Internal knowledge base    → jina_claude
✓ High-volume queries        → jina_gpt4
✓ Balanced requirements      → tavily_gpt4
```

---

## File Structure

```
website-rag/
├── TEST_PLAN.md                    ← Complete test methodology
├── EVALUATION_RUBRIC.md            ← Scoring reference
├── QUICK_START.md                  ← This file
├── FRAMEWORK_OVERVIEW.md           ← Complete overview
├── ADDING_NEW_PLUGINS.md           ← How to extend
│
├── config/
│   ├── configs.yaml                ← Tool configurations
│   └── test_suites/
│       └── standard_questions.json ← 25 test questions
│
├── scripts/
│   ├── collect_notebookllm_baseline.py  ← Step 1
│   ├── run_evaluation.py                ← Step 2
│   └── generate_comparison_report.py    ← Step 3
│
└── test_results/                   ← Generated during testing
    ├── ground_truth/
    │   └── notebookllm_baseline.json
    ├── {config_name}/
    │   └── results.json
    └── comparison_report.txt
```

---

## Dependencies

Install once:
```bash
pip install requests nltk numpy scikit-learn
```

---

## Common Commands

```bash
# Collect baseline (one-time)
python scripts/collect_notebookllm_baseline.py

# Test a configuration
python scripts/run_evaluation.py --config jina_gpt4

# Test with different URL
python scripts/run_evaluation.py --config jina_gpt4 --url https://example.com

# Skip re-indexing
python scripts/run_evaluation.py --config jina_gpt4 --skip-indexing

# Generate comparison report
python scripts/generate_comparison_report.py

# Generate JSON report
python scripts/generate_comparison_report.py --format json --output results.json

# View report
cat test_results/comparison_report.txt
```

---

## Need Help?

**Check these docs:**
- Getting started issues? → `GETTING_STARTED_WITH_TESTING.md`
- Scoring questions? → `EVALUATION_RUBRIC.md`
- Performance questions? → `PERFORMANCE_ANALYSIS.md`
- Want to add new tools? → `ADDING_NEW_PLUGINS.md`

---

## What's Included

### ✅ Testing Framework
- Baseline collection script
- Evaluation runner
- Comparison generator
- 25 standard questions

### ✅ Complete Documentation
- 8 comprehensive guides
- Step-by-step instructions
- Code examples
- Reference materials

### ✅ Analytics System
- Automated performance recording
- Comprehensive comparisons
- Clear recommendations
- Decision support

### ✅ Flexible Architecture
- Easy to add MCP servers
- Easy to add LLMs
- No framework changes needed
- Plugin-based design

---

## Timeline

**Day 1: Setup (2-3 hours)**
- Collect NotebookLLM baseline responses

**Day 2: Testing (2-4 hours)**
- Test 2-4 configurations
- 30-60 min per configuration

**Day 3: Analysis (1 hour)**
- Generate comparison report
- Review results
- Make decision

**Total: ~1 week with manual review**

---

## Success Criteria

A configuration is **production-ready** if:
- ✅ Overall Score ≥ 80
- ✅ Answer Quality ≥ 80
- ✅ Similarity to NotebookLLM ≥ 75
- ✅ Error Rate < 2%
- ✅ No hallucinations

---

## Ready to Start?

```bash
# 1. Start here
python scripts/collect_notebookllm_baseline.py

# 2. Then test
python scripts/run_evaluation.py --config jina_gpt4

# 3. Get results
python scripts/generate_comparison_report.py
```

**That's it! You'll have data-driven recommendations for your RAG system.**

---

**Questions? Check the comprehensive docs or reach out!**
