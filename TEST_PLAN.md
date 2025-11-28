# RAG System Test Plan & Evaluation Rubric

## Overview

**Goal**: Systematically evaluate different tool combinations to determine the optimal configuration for a customer support chatbot.

**Ground Truth**: NotebookLLM responses serve as our baseline for quality comparison.

**Approach**: Compare different data retrieval tools (Jina, Tavily, Firecrawl) and LLM plugins (Claude, GPT-4) against NotebookLLM's performance.

---

## Test Methodology

### Phase 1: Establish Ground Truth with NotebookLLM

**Step 1: Prepare NotebookLLM**
1. Visit [NotebookLLM](https://notebooklm.google.com/)
2. Create a new notebook for "BizGenie Website Evaluation"
3. Add sources:
   - Upload website URLs (https://bizgenieai.com and key pages)
   - Let NotebookLLM index the content
4. Wait for processing to complete

**Step 2: Create Standard Question Set**
- Develop 20-30 questions covering different difficulty levels
- Questions should span different types (factual, reasoning, comparison, procedural)
- Save questions in `config/test_suites/standard_questions.json`

**Step 3: Collect NotebookLLM Baseline Responses**
- Ask each question to NotebookLLM
- Record responses, sources cited, and response time
- Save to `test_results/ground_truth/notebookllm_baseline.json`
- Include screenshots if helpful

### Phase 2: Test Each Configuration

For each configuration (e.g., `jina_gpt4`, `tavily_claude`):
1. Index the same website content
2. Ask the same standard questions
3. Collect responses and metrics
4. Store results in `test_results/{config_name}/`

### Phase 3: Compare Results

Use the evaluation rubric (below) to score each configuration against NotebookLLM baseline.

---

## Standard Question Set Design

### Question Categories

#### Category 1: Factual Questions (Easy)
*Questions with clear, verifiable answers*

Examples:
- "What is BizGenie?"
- "What services does BizGenie offer?"
- "Where is BizGenie located?"
- "What industries does BizGenie serve?"

**Evaluation Focus**: Accuracy, completeness

#### Category 2: Reasoning Questions (Medium)
*Questions requiring synthesis of information*

Examples:
- "How does BizGenie's automation differ from traditional solutions?"
- "What are the benefits of using BizGenie's AI services?"
- "Why should a business choose BizGenie over competitors?"

**Evaluation Focus**: Coherence, logical reasoning, context understanding

#### Category 3: Comparison Questions (Medium-Hard)
*Questions requiring comparing multiple concepts*

Examples:
- "What's the difference between BizGenie's basic and premium plans?"
- "How do BizGenie's services compare for small vs large businesses?"
- "Compare the features of different service tiers"

**Evaluation Focus**: Accuracy, completeness, clarity

#### Category 4: Procedural Questions (Medium)
*How-to questions*

Examples:
- "How do I get started with BizGenie?"
- "What's the process for implementing BizGenie's automation?"
- "How can I contact BizGenie support?"

**Evaluation Focus**: Completeness of steps, actionability

#### Category 5: Edge Cases (Hard)
*Questions that might not have clear answers*

Examples:
- "What are the limitations of BizGenie's AI?"
- "When should I NOT use BizGenie?"
- "What happens if BizGenie's service goes down?"

**Evaluation Focus**: Handling uncertainty, appropriate caveats

---

## Evaluation Rubric

### Primary Metrics

#### 1. Answer Quality Score (0-100)

**Compared to NotebookLLM baseline:**

| Score Range | Description | Criteria |
|-------------|-------------|----------|
| 90-100 | Excellent | Matches or exceeds NotebookLLM quality. Accurate, complete, well-structured. |
| 75-89 | Good | Minor differences from NotebookLLM. Mostly accurate with small omissions. |
| 60-74 | Acceptable | Noticeable quality gap. Missing some details or minor inaccuracies. |
| 40-59 | Poor | Significant quality issues. Incomplete or contains inaccuracies. |
| 0-39 | Very Poor | Incorrect, hallucinated, or completely off-topic. |

**Scoring Components:**

1. **Accuracy (30 points)**
   - 30: Factually correct, no errors
   - 20: Mostly correct, minor errors
   - 10: Several errors
   - 0: Major errors or hallucinations

2. **Completeness (25 points)**
   - 25: Covers all relevant aspects
   - 18: Covers most aspects, minor omissions
   - 10: Missing significant information
   - 0: Incomplete or superficial answer

3. **Relevance (15 points)**
   - 15: Directly answers the question
   - 10: Mostly relevant, some tangents
   - 5: Partially relevant
   - 0: Off-topic or doesn't address question

4. **Coherence (15 points)**
   - 15: Well-structured, logical flow
   - 10: Generally coherent, minor issues
   - 5: Disorganized or hard to follow
   - 0: Incoherent

5. **Source Attribution (15 points)**
   - 15: Accurate sources, properly cited
   - 10: Sources present but not detailed
   - 5: Vague or missing sources
   - 0: No source attribution

#### 2. Similarity to NotebookLLM Score (0-100)

**Automated Metrics:**

1. **BLEU Score** (0-100)
   - Measures n-gram overlap with NotebookLLM response
   - Higher = more similar wording

2. **Semantic Similarity** (0-100)
   - Cosine similarity of embeddings
   - Higher = more similar meaning

3. **Coverage Score** (0-100)
   - % of key facts from NotebookLLM answer present
   - Requires manual fact extraction or automated NER

**Combined Similarity Score:**
```
Similarity = (BLEU * 0.3) + (Semantic * 0.4) + (Coverage * 0.3)
```

#### 3. Performance Metrics

| Metric | Measurement | Target | Weight |
|--------|-------------|--------|--------|
| **Response Time** | Seconds from query to answer | < 3s | 20% |
| **Cost per Query** | USD per question answered | < $0.05 | 15% |
| **Retrieval Accuracy** | Relevant chunks retrieved | > 80% | 25% |
| **Error Rate** | % of queries that fail | < 2% | 20% |
| **Token Efficiency** | Tokens used vs answer quality | Optimize | 20% |

#### 4. User Experience Metrics

| Aspect | Rating (1-5) | Description |
|--------|--------------|-------------|
| **Readability** | 1-5 | How easy is the answer to understand? |
| **Actionability** | 1-5 | Can user take action based on answer? |
| **Trustworthiness** | 1-5 | Does answer inspire confidence? |
| **Completeness** | 1-5 | Does it fully address the question? |

**UX Score** = Average of 4 aspects × 20 = 0-100 scale

---

## Comprehensive Scoring Formula

### Overall Configuration Score

```
Overall Score =
  (Answer Quality Score × 0.40) +
  (Similarity to NotebookLLM × 0.25) +
  (Performance Score × 0.20) +
  (UX Score × 0.15)
```

### Performance Score Calculation

```
Performance Score =
  (Response Time Score × 0.20) +
  (Cost Efficiency Score × 0.15) +
  (Retrieval Accuracy × 0.25) +
  (Reliability Score × 0.20) +
  (Token Efficiency × 0.20)
```

Where each component is normalized to 0-100:
- **Response Time Score**: `100 - (actual_time / max_acceptable_time * 100)` capped at 0
- **Cost Efficiency Score**: `100 - (actual_cost / max_acceptable_cost * 100)` capped at 0
- **Retrieval Accuracy**: `% relevant chunks × 100`
- **Reliability Score**: `(100 - error_rate_percent)`
- **Token Efficiency**: `(quality_score / tokens_used × 1000)` normalized to 100

---

## Test Execution Workflow

### Step 1: Prepare Test Environment

```bash
# Navigate to project
cd /home/virus/Documents/repo/bizgenie/website-rag

# Ensure all services running
docker-compose up -d

# Verify ChromaDB
curl http://localhost:8001/api/v1/heartbeat

# Set API keys in .env
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export JINA_API_KEY=...
export TAVILY_API_KEY=...
```

### Step 2: Create Ground Truth

```bash
# Manually collect NotebookLLM responses
# Use: scripts/collect_notebookllm_baseline.py (to be created)
```

### Step 3: Run Tests for Each Configuration

```bash
# Test Configuration 1: Jina + GPT-4
python scripts/run_evaluation.py --config jina_gpt4

# Test Configuration 2: Tavily + GPT-4
python scripts/run_evaluation.py --config tavily_gpt4

# Test Configuration 3: Jina + Claude
python scripts/run_evaluation.py --config jina_claude

# Test Configuration 4: Tavily + Claude
python scripts/run_evaluation.py --config tavily_claude
```

### Step 4: Generate Comparison Report

```bash
# Compare all configurations
python scripts/generate_comparison_report.py --output test_results/comparison_report.html
```

---

## Test Data Structures

### Standard Questions File
`config/test_suites/standard_questions.json`

```json
{
  "test_suite_name": "BizGenie Customer Support QA",
  "version": "1.0",
  "created_date": "2025-01-15",
  "source_url": "https://bizgenieai.com",
  "questions": [
    {
      "id": "q001",
      "category": "factual",
      "difficulty": "easy",
      "question": "What is BizGenie?",
      "expected_keywords": ["AI", "automation", "business"],
      "expected_facts": [
        "BizGenie provides AI automation services",
        "Helps businesses automate processes"
      ]
    },
    {
      "id": "q002",
      "category": "reasoning",
      "difficulty": "medium",
      "question": "How does BizGenie's automation help small businesses?",
      "expected_keywords": ["efficiency", "cost", "time"],
      "requires_synthesis": true
    }
  ]
}
```

### NotebookLLM Baseline File
`test_results/ground_truth/notebookllm_baseline.json`

```json
{
  "baseline_name": "NotebookLLM",
  "created_date": "2025-01-15",
  "source_notebook": "BizGenie Website Evaluation",
  "responses": [
    {
      "question_id": "q001",
      "question": "What is BizGenie?",
      "answer": "BizGenie is an AI-powered automation platform...",
      "sources": [
        {
          "title": "BizGenie Homepage",
          "url": "https://bizgenieai.com",
          "snippet": "..."
        }
      ],
      "response_time_seconds": 2.1,
      "word_count": 87,
      "manual_quality_rating": 5
    }
  ]
}
```

### Configuration Test Results File
`test_results/{config_name}/results.json`

```json
{
  "config_name": "jina_gpt4",
  "test_run_id": "run_2025_01_15_001",
  "timestamp": "2025-01-15T10:30:00Z",
  "configuration": {
    "data_retrieval": "jina",
    "llm": "gpt4",
    "embedding": "text-embedding-3-small"
  },
  "indexing_metrics": {
    "total_time_seconds": 45.2,
    "pages_indexed": 15,
    "total_chunks": 234,
    "total_cost": 0.12
  },
  "query_results": [
    {
      "question_id": "q001",
      "question": "What is BizGenie?",
      "answer": "BizGenie is an AI automation platform...",
      "sources": [
        {
          "url": "https://bizgenieai.com",
          "chunk_id": "chunk_42",
          "relevance_score": 0.89
        }
      ],
      "metrics": {
        "response_time_seconds": 2.3,
        "tokens_used": 456,
        "cost": 0.023,
        "chunks_retrieved": 5
      },
      "evaluation": {
        "answer_quality_score": 85,
        "similarity_to_baseline": {
          "bleu_score": 0.42,
          "semantic_similarity": 0.87,
          "coverage_score": 0.90,
          "combined": 78
        },
        "manual_ratings": {
          "accuracy": 28,
          "completeness": 22,
          "relevance": 14,
          "coherence": 13,
          "source_attribution": 12
        },
        "ux_ratings": {
          "readability": 4,
          "actionability": 3,
          "trustworthiness": 5,
          "completeness": 4
        }
      }
    }
  ],
  "aggregate_metrics": {
    "avg_answer_quality": 85.3,
    "avg_similarity_to_baseline": 76.8,
    "avg_response_time": 2.4,
    "avg_cost_per_query": 0.024,
    "error_rate": 0.0,
    "overall_score": 81.2
  }
}
```

---

## Comparison Report Format

### HTML Report Structure

```
BizGenie RAG Evaluation Report
Generated: 2025-01-15

┌─────────────────────────────────────────────┐
│ EXECUTIVE SUMMARY                           │
├─────────────────────────────────────────────┤
│ Winner: Tavily + GPT-4                      │
│ Overall Score: 84.2                         │
│ Reason: Best accuracy-cost balance          │
└─────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ CONFIGURATION RANKINGS                                       │
├────────┬──────────────┬───────┬──────────┬──────┬───────────┤
│ Rank   │ Config       │ Score │ Quality  │ Cost │ Speed     │
├────────┼──────────────┼───────┼──────────┼──────┼───────────┤
│ #1     │ tavily_gpt4  │ 84.2  │ 88.5     │ $0.04│ 2.8s      │
│ #2     │ jina_gpt4    │ 81.3  │ 85.1     │ $0.02│ 2.3s      │
│ #3     │ tavily_claude│ 79.8  │ 86.2     │ $0.03│ 3.1s      │
│ #4     │ jina_claude  │ 77.5  │ 82.3     │ $0.02│ 2.5s      │
├────────┴──────────────┴───────┴──────────┴──────┴───────────┤
│ Baseline: NotebookLLM                                        │
│ Quality: 92.0 | Cost: $0.00 | Speed: 2.1s                   │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ DETAILED ANALYSIS                           │
├─────────────────────────────────────────────┤
│                                             │
│ Answer Quality vs NotebookLLM:             │
│ ████████████████████░░░ 88.5% (tavily_gpt4)│
│ █████████████████░░░░░░ 85.1% (jina_gpt4)  │
│                                             │
│ Cost Efficiency:                            │
│ ████████████████████░░░ jina_gpt4 ($0.02)  │
│ ██████████████████░░░░░ tavily_gpt4 ($0.04)│
│                                             │
│ Speed:                                      │
│ ████████████████████░░░ jina_gpt4 (2.3s)   │
│ ██████████████████░░░░░ tavily_gpt4 (2.8s) │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ RECOMMENDATIONS                             │
├─────────────────────────────────────────────┤
│                                             │
│ ✓ Use tavily_gpt4 for:                     │
│   • Customer-facing chatbot (quality)       │
│   • Complex queries requiring accuracy      │
│                                             │
│ ✓ Use jina_gpt4 for:                       │
│   • Internal knowledge base (cost)          │
│   • High-volume queries                     │
│                                             │
│ ✗ Avoid:                                    │
│   • jina_claude showed hallucination        │
│     issues on 3 questions                   │
└─────────────────────────────────────────────┘
```

---

## Success Criteria

### Minimum Viable Test

A configuration is considered **acceptable** if:
- ✅ Overall Score ≥ 75
- ✅ Answer Quality Score ≥ 70
- ✅ Similarity to NotebookLLM ≥ 65
- ✅ Error Rate < 5%
- ✅ No hallucinations on factual questions

### Production-Ready Criteria

A configuration is **production-ready** if:
- ✅ Overall Score ≥ 80
- ✅ Answer Quality Score ≥ 80
- ✅ Similarity to NotebookLLM ≥ 75
- ✅ Error Rate < 2%
- ✅ Response Time < 3s (95th percentile)
- ✅ No critical failures in edge cases

---

## Test Execution Timeline

### Week 1: Setup & Ground Truth
- **Day 1-2**: Set up NotebookLLM, create question set
- **Day 3-4**: Collect NotebookLLM baseline responses
- **Day 5**: Create evaluation scripts

### Week 2: Configuration Testing
- **Day 1**: Test jina_gpt4
- **Day 2**: Test tavily_gpt4
- **Day 3**: Test jina_claude
- **Day 4**: Test tavily_claude
- **Day 5**: Collect manual ratings

### Week 3: Analysis & Reporting
- **Day 1-2**: Calculate all metrics
- **Day 3**: Generate comparison report
- **Day 4**: Identify winner and edge cases
- **Day 5**: Document findings and recommendations

---

## Next Steps

1. **Review this test plan** - Does it align with your goals?
2. **Create question set** - I can help generate 20-30 questions
3. **Set up NotebookLLM** - Collect baseline responses
4. **Build evaluation scripts** - Automate metric collection
5. **Run tests** - Execute evaluation workflow
6. **Analyze results** - Determine optimal configuration

Would you like me to:
1. Generate the standard question set now?
2. Create the evaluation scripts (`run_evaluation.py`, `generate_comparison_report.py`)?
3. Design the data collection templates?
4. Set up the test infrastructure?
