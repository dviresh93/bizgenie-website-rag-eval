# Getting Started with RAG System Testing

## Quick Start Guide

This guide will walk you through evaluating your RAG system configurations against NotebookLLM baseline.

---

## Overview

You now have:
- ✅ **TEST_PLAN.md** - Complete test methodology and rubric
- ✅ **EVALUATION_RUBRIC.md** - Quick scoring reference
- ✅ **standard_questions.json** - 25 test questions across 5 categories
- ✅ **collect_notebookllm_baseline.py** - Script to record NotebookLLM responses
- ✅ **run_evaluation.py** - Script to test your configurations

---

## Step-by-Step Workflow

### Phase 1: Establish Ground Truth (2-3 hours)

#### Step 1.1: Set up NotebookLLM

1. Visit https://notebooklm.google.com/
2. Click "New notebook"
3. Add sources:
   - Option A: Add URLs directly (paste website URLs)
   - Option B: Copy-paste content from website
4. Wait for NotebookLLM to process and index content
5. Test with a sample question to ensure it's working

#### Step 1.2: Collect Baseline Responses

```bash
cd /home/virus/Documents/repo/bizgenie/website-rag

# Run the baseline collection script
python scripts/collect_notebookllm_baseline.py
```

**What this does:**
- Loads all 25 questions from `standard_questions.json`
- Shows you each question one by one
- You ask NotebookLLM and paste the response
- Script records answers, sources, and response times
- Saves to `test_results/ground_truth/notebookllm_baseline.json`

**Time estimate:** ~2-3 hours (5-7 minutes per question)

#### Step 1.3: Review Baseline

Open `test_results/ground_truth/notebookllm_baseline.json` and verify:
- All questions have responses
- Response quality looks good
- Sources are recorded

---

### Phase 2: Test Your Configurations (30-60 min per config)

#### Step 2.1: Ensure Services Running

```bash
cd /home/virus/Documents/repo/bizgenie/website-rag

# Start all services
docker-compose up -d

# Check API is running
curl http://localhost:8000/health

# Check ChromaDB is running
curl http://localhost:8001/api/v1/heartbeat
```

#### Step 2.2: Set API Keys

Create/update `.env` file:
```bash
cp .env.example .env
nano .env  # Add your API keys
```

Required keys:
- `OPENAI_API_KEY` - For embeddings and GPT-4
- `ANTHROPIC_API_KEY` - For Claude
- `JINA_API_KEY` - For Jina (optional, works without)
- `TAVILY_API_KEY` - For Tavily (if testing)

#### Step 2.3: Run Evaluation for Configuration 1

```bash
# Test: Jina + GPT-4
python scripts/run_evaluation.py --config jina_gpt4

# What happens:
# 1. Indexes bizgenieai.com using Jina plugin
# 2. Asks all 25 questions using GPT-4
# 3. Compares answers to NotebookLLM baseline
# 4. Saves results to test_results/jina_gpt4/results.json
```

**Time estimate:** ~30-60 minutes

#### Step 2.4: Run Evaluation for Configuration 2

```bash
# Test: Tavily + GPT-4
python scripts/run_evaluation.py --config tavily_gpt4
```

#### Step 2.5: Run Evaluation for Configuration 3

```bash
# Test: Jina + Claude
python scripts/run_evaluation.py --config jina_claude
```

#### Step 2.6: Run Evaluation for Configuration 4

```bash
# Test: Tavily + Claude
python scripts/run_evaluation.py --config tavily_claude
```

---

### Phase 3: Manual Review (1-2 hours per config)

#### Why Manual Review?

Automated metrics (BLEU, semantic similarity) are helpful but not perfect. Manual review ensures:
- Factual accuracy
- Answer quality
- Source attribution
- No hallucinations

#### How to Do Manual Review

For each configuration's `results.json`:

1. Open the file: `test_results/{config_name}/results.json`
2. For each question/answer pair:
   - Read the question
   - Read the answer
   - Compare to NotebookLLM baseline
   - Score using EVALUATION_RUBRIC.md

**Example Manual Review:**

```json
{
  "question_id": "q001",
  "question": "What is BizGenie?",
  "answer": "BizGenie is an AI automation platform...",

  "evaluation": {
    "manual_ratings": {
      "accuracy": 28,        // 0-30 points
      "completeness": 22,    // 0-25 points
      "relevance": 15,       // 0-15 points
      "coherence": 14,       // 0-15 points
      "source_attribution": 12  // 0-15 points
    },
    "ux_ratings": {
      "readability": 5,      // 1-5 scale
      "actionability": 3,    // 1-5 scale
      "trustworthiness": 4,  // 1-5 scale
      "completeness": 4      // 1-5 scale
    }
  }
}
```

3. Update the `manual_ratings` and `ux_ratings` sections
4. Calculate `answer_quality_score` = sum of manual_ratings (0-100)
5. Save the file

**Time estimate:** ~1-2 hours per configuration (3-5 min per question)

---

### Phase 4: Generate Comparison Report (Future Enhancement)

*This script will be created next to automate comparison*

```bash
# Generate HTML comparison report
python scripts/generate_comparison_report.py --output test_results/comparison_report.html
```

**What it will show:**
- Side-by-side configuration comparison
- Winner identification
- Detailed metrics breakdown
- Recommendations

---

## What Each Score Means

### Overall Configuration Score

```
Overall Score =
  (Answer Quality × 0.40) +
  (Similarity to NotebookLLM × 0.25) +
  (Performance × 0.20) +
  (UX Score × 0.15)
```

### Interpretation

| Score | Rating | Decision |
|-------|--------|----------|
| 90-100 | Excellent | Exceeds NotebookLLM, production-ready |
| 80-89 | Very Good | Comparable to NotebookLLM, production-ready |
| 70-79 | Good | Acceptable for production |
| 60-69 | Fair | Consider improvements |
| < 60 | Poor | Not recommended |

---

## Example: Complete Test Session

```bash
# Day 1: Ground Truth (2-3 hours)
# ================================
cd ~/Documents/repo/bizgenie/website-rag

# 1. Set up NotebookLLM with bizgenieai.com content
# 2. Run baseline collection
python scripts/collect_notebookllm_baseline.py
# (Follow prompts, ask each question to NotebookLLM)


# Day 2: Test Configurations (3-4 hours)
# =======================================

# Start services
docker-compose up -d

# Test config 1: Jina + GPT-4
python scripts/run_evaluation.py --config jina_gpt4
# Wait ~30 min

# Test config 2: Tavily + GPT-4
python scripts/run_evaluation.py --config tavily_gpt4
# Wait ~30 min

# Test config 3: Jina + Claude
python scripts/run_evaluation.py --config jina_claude
# Wait ~30 min


# Day 3: Manual Review (4-6 hours)
# =================================

# Review each configuration
nano test_results/jina_gpt4/results.json
# Score each answer using EVALUATION_RUBRIC.md

nano test_results/tavily_gpt4/results.json
# Score each answer

nano test_results/jina_claude/results.json
# Score each answer


# Day 4: Analysis
# ===============

# Compare results manually or generate report
python scripts/generate_comparison_report.py  # (to be created)

# Review comparison_report.html
# Identify winner
# Document findings
```

---

## Files Created

### Test Plan & Documentation
- `TEST_PLAN.md` - Complete methodology and rubric
- `EVALUATION_RUBRIC.md` - Quick scoring reference
- `GETTING_STARTED_WITH_TESTING.md` - This file

### Test Data
- `config/test_suites/standard_questions.json` - 25 test questions

### Scripts
- `scripts/collect_notebookllm_baseline.py` - Collect ground truth
- `scripts/run_evaluation.py` - Run configuration tests

### Results (Generated)
- `test_results/ground_truth/notebookllm_baseline.json`
- `test_results/{config_name}/results.json`
- `test_results/comparison_report.html` (future)

---

## Customization

### Add More Questions

Edit `config/test_suites/standard_questions.json`:
```json
{
  "id": "q026",
  "category": "factual",
  "difficulty": "easy",
  "question": "Your custom question?",
  "expected_keywords": ["keyword1", "keyword2"]
}
```

### Test Different URLs

```bash
python scripts/run_evaluation.py \
  --config jina_gpt4 \
  --url https://example.com
```

### Skip Indexing (Re-run on Same Index)

```bash
python scripts/run_evaluation.py \
  --config jina_gpt4 \
  --skip-indexing
```

---

## Troubleshooting

### "Baseline file not found"
**Solution:** Run `python scripts/collect_notebookllm_baseline.py` first

### "API connection refused"
**Solution:** Ensure services running: `docker-compose up -d`

### "API key not set"
**Solution:** Check `.env` file has all required keys

### "Questions file not found"
**Solution:** Ensure you're in the `website-rag` directory

---

## Next Steps After Testing

Once you've completed testing all configurations:

1. **Analyze Results**
   - Which configuration scored highest?
   - What's the cost vs quality tradeoff?
   - Any configurations with critical failures?

2. **Make Decision**
   - Choose production configuration
   - Consider backup configuration
   - Document rationale

3. **Optimize**
   - Tune chunk size if needed
   - Adjust retrieval parameters
   - Improve prompts

4. **Deploy**
   - Configure production environment
   - Set up monitoring
   - Create user documentation

---

## Questions?

Refer to:
- `TEST_PLAN.md` for detailed methodology
- `EVALUATION_RUBRIC.md` for scoring guidance
- `README.md` for system architecture
- `IMPLEMENTATION.md` for technical details

---

**You're all set! Start with Phase 1: Collecting NotebookLLM baseline responses.**
