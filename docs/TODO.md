# TODO

**Last Updated**: 2025-01-28

---

## 🎯 Project Goal

Evaluate which **MCP Tool + LLM combination** performs best for answering questions about BizGenie.

**Framework**: User-controlled evaluation (NOT agentic)
- User picks MCP tool (Jina/Tavily) + LLM (Claude/GPT-4)
- System runs real-time search + answer generation
- Measure quality, cost, speed, hallucination rate
- Compare all 4 combinations and recommend best

---

## 📋 Implementation Tasks

### ✅ Repository Cleanup (COMPLETED)
- [x] Remove 23MB intro.mp4
- [x] Remove 16 outdated documentation files
- [x] Remove old test results (keep only latest runs)
- [x] Reduce from 47MB → 25MB, 22 docs → 3 docs

### 🔧 Code Simplification (TODO - For Implementation Agent)

#### 1. Simplify `scripts/ai_judge.py`
**Current problem**: Complex baseline comparison with flawed "found more" logic

**What to do**:
- Remove `load_baseline()` method entirely
- Remove `_is_no_info_answer()` method
- Update `evaluate_answer()` to remove baseline comparison
- Simplify prompt to evaluate **absolute quality only** (no Answer B comparison)
- Evaluate on: accuracy, completeness, clarity, helpfulness (0-100 each)
- Add hallucination detection (check if answer makes unsupported claims)
- Return: `{accuracy, completeness, clarity, helpfulness, overall_quality, has_hallucination}`

**New evaluation criteria**:
```
1. ACCURACY (0-100): Is the information factually correct?
2. COMPLETENESS (0-100): Does it fully answer the question?
3. CLARITY (0-100): Is it clear and readable?
4. HELPFULNESS (0-100): Is it useful to the user?
5. HALLUCINATION CHECK: Does it make unsupported claims?
```

#### 2. Simplify `scripts/run_evaluation.py`
**Current problem**: References baseline, complex result structure

**What to do**:
- Remove all baseline-related code
- Remove `--baseline` argument
- Keep simple flow: load questions → search → generate → save results
- Result structure:
```python
{
  "question_id": "q1",
  "question": "...",
  "answer": "...",
  "sources": [...],
  "metrics": {
    "search_time": 1.2,
    "search_cost": 0.001,
    "generation_time": 2.3,
    "generation_cost": 0.015,
    "total_time": 3.5,
    "total_cost": 0.016,
    "tokens": 1500
  }
}
```

#### 3. Simplify `scripts/generate_comparison_report.py`
**Current problem**: Complex baseline comparison metrics, confusing "found more" percentages

**What to do**:
- Remove all baseline comparison logic
- Remove "found more" and "has_info" calculations
- Show **comprehensive metrics** (we have the data, let's use it!)
- Report structure:
```markdown
# MCP Tool + LLM Comparison Report

## 🏆 Overall Rankings
| Rank | Combination    | Quality | Total Cost | Total Time | Search Time | Gen Time | Halluc. |
|------|----------------|---------|------------|------------|-------------|----------|---------|
| 1    | jina_claude    | 85.2    | $0.024     | 3.2s       | 1.1s        | 2.1s     | 0       |
| 2    | tavily_claude  | 82.1    | $0.031     | 2.8s       | 0.9s        | 1.9s     | 1       |
| 3    | jina_gpt4      | 84.5    | $0.035     | 2.9s       | 1.1s        | 1.8s     | 0       |
| 4    | tavily_gpt4    | 81.0    | $0.042     | 2.5s       | 0.9s        | 1.6s     | 2       |

## 📊 Detailed Metrics

### JINA_CLAUDE
**Quality Breakdown:**
- Average Overall Quality: 85.2/100
- Average Accuracy: 88/100
- Average Completeness: 84/100
- Average Clarity: 92/100
- Average Helpfulness: 87/100

**Performance:**
- Avg Search Latency: 1.1s (Jina MCP tool)
- Avg Generation Latency: 2.1s (Claude LLM)
- Avg Total Latency: 3.2s
- Fastest query: 2.1s (q5)
- Slowest query: 5.8s (q22)

**Cost:**
- Avg Search Cost: $0.002/query (Jina API)
- Avg Generation Cost: $0.022/query (Claude API)
- Avg Total Cost: $0.024/query
- Total for 25 queries: $0.60
- Most expensive query: $0.045 (q12, 2500 tokens)

**Reliability:**
- Hallucinations: 0/25 questions (✅ EXCELLENT)
- Failed queries: 0/25
- Avg tokens used: 1450/query
- Avg answer length: 320 characters

**Quality Distribution:**
- Excellent (80-100): 18 questions
- Good (60-79): 5 questions
- Fair (40-59): 2 questions
- Poor (0-39): 0 questions

**Top scoring questions:** q1 (95), q3 (92), q4 (90)
**Low scoring questions:** q15 (45), q18 (52)

### TAVILY_CLAUDE
[Same detailed breakdown]

## 📈 Comparative Analysis

### Quality Comparison
- Highest quality: JINA_CLAUDE (85.2)
- Most accurate: JINA_CLAUDE (88.0 accuracy)
- Most complete: JINA_GPT4 (86.0 completeness)
- Clearest answers: JINA_CLAUDE (92.0 clarity)

### Speed Comparison
- Fastest search: TAVILY (0.9s avg)
- Fastest generation: GPT4 (1.7s avg)
- Fastest total: TAVILY_GPT4 (2.5s)
- Speed/Quality champion: JINA_CLAUDE (85.2 quality, 3.2s)

### Cost Comparison
- Cheapest search: JINA ($0.002/query)
- Cheapest generation: CLAUDE ($0.022/query)
- Cheapest total: JINA_CLAUDE ($0.024/query)
- Most expensive: TAVILY_GPT4 ($0.042/query)

### Reliability Comparison
- Zero hallucinations: JINA_CLAUDE, JINA_GPT4
- Fewest hallucinations: JINA_CLAUDE, JINA_GPT4 (0)
- Most hallucinations: TAVILY_GPT4 (2)

## 🎯 Recommendations

**🏆 BEST OVERALL: JINA_CLAUDE**
- Highest quality (85.2/100)
- Zero hallucinations
- Lowest cost ($0.024/query)
- Acceptable speed (3.2s)
- **Use when: Quality and reliability matter most**

**⚡ BEST FOR SPEED: TAVILY_GPT4**
- Fastest total time (2.5s)
- Good quality (81.0/100)
- **Use when: Speed is critical, slight quality trade-off acceptable**

**💰 BEST VALUE: JINA_CLAUDE**
- Lowest cost per query ($0.024)
- Highest quality (85.2)
- **Use when: Budget-conscious but need high quality**

**🔍 BEST SEARCH TOOL: TAVILY**
- Faster search (0.9s vs 1.1s)
- More expensive ($0.012 vs $0.002 search cost)
- **Use when: Real-time freshness matters**

**🤖 BEST LLM: CLAUDE**
- Higher quality scores
- Zero hallucinations
- Slightly slower than GPT4
- **Use when: Accuracy and reliability critical**
```

#### 4. Update Documentation

**Update README.md**:
- Clear quick start (3 steps)
- Explain what it tests (4 combinations)
- Show sample results
- Link to ARCHITECTURE.md for details

**Keep ARCHITECTURE.md**:
- Already correct (user-controlled evaluation framework)
- Add metrics section (quality/cost/speed/hallucination)

**Keep TODO.md**:
- This file (implementation checklist)

---

## 🧪 Testing Plan (Simplified Approach)

### Test Questions
- **Source**: `config/test_suites/standard_questions.json`
- **Count**: 25 questions about BizGenie
- **Status**: ✅ Approved, use as-is

### Combinations to Test
1. **jina_claude**: Jina AI Reader + Claude 3.5 Sonnet
2. **jina_gpt4**: Jina AI Reader + GPT-4 Turbo
3. **tavily_claude**: Tavily AI Search + Claude 3.5 Sonnet
4. **tavily_gpt4**: Tavily AI Search + GPT-4 Turbo

### Evaluation Process
```bash
# 1. Run evaluation for each combination
python scripts/run_evaluation.py --mcp jina --llm claude
python scripts/run_evaluation.py --mcp jina --llm gpt4
python scripts/run_evaluation.py --mcp tavily --llm claude
python scripts/run_evaluation.py --mcp tavily --llm gpt4

# 2. AI judge evaluates quality (absolute, no baseline)
python scripts/ai_judge.py test_results/jina_claude/results_*.json

# 3. Generate comparison report
python scripts/generate_comparison_report.py
```

### Metrics Measured

**Quality Metrics:**
1. **Overall Quality Score** (0-100): Weighted average of accuracy, completeness, clarity, helpfulness
2. **Accuracy** (0-100): Factual correctness
3. **Completeness** (0-100): How thoroughly question is answered
4. **Clarity** (0-100): Readability and structure
5. **Helpfulness** (0-100): Usefulness to end user
6. **Hallucination Rate**: Count of questions where AI made unsupported claims

**Performance Metrics:**
7. **Search Latency** (seconds): Time for MCP tool to fetch data
8. **Generation Latency** (seconds): Time for LLM to generate answer
9. **Total Latency** (seconds): Search + generation time
10. **Fastest/Slowest Query**: Latency range across questions

**Cost Metrics:**
11. **Search Cost** ($/query): MCP tool API cost per query
12. **Generation Cost** ($/query): LLM API cost per query
13. **Total Cost** ($/query): Combined cost per query
14. **Total Cost for 25 queries**: Full test suite cost
15. **Most/Least Expensive Query**: Cost range

**Reliability Metrics:**
16. **Failed Queries**: Count of errors/timeouts
17. **Token Usage**: Average tokens per query
18. **Answer Length**: Average character count
19. **Quality Distribution**: Breakdown by score ranges (excellent/good/fair/poor)

### Success Criteria
- Quality score > 80/100 (excellent)
- Accuracy > 85/100 (trustworthy)
- Zero or minimal hallucinations (< 2/25)
- Cost < $0.05/query (acceptable for business use)
- Total latency < 5s/query (acceptable UX)
- Search latency < 2s (responsive search)
- Generation latency < 3s (responsive LLM)

---

## 📦 Current Repository Structure

```
website-rag/
├── README.md                    # Main documentation
├── ARCHITECTURE.md              # System design
├── TODO.md                      # This file (implementation checklist)
│
├── .env.example                 # API keys template
├── docker-compose.yml           # Infrastructure setup
│
├── api/                         # Backend implementation
│   ├── app/
│   │   ├── tools/               # MCP tool implementations
│   │   │   ├── base.py
│   │   │   ├── jina_tool.py
│   │   │   └── tavily_tool.py
│   │   ├── llm/                 # LLM implementations
│   │   │   ├── base.py
│   │   │   ├── claude_llm.py
│   │   │   └── gpt4_llm.py
│   │   └── core/                # Utilities
│   │       ├── logging.py
│   │       └── prompts.py
│
├── scripts/                     # Evaluation scripts
│   ├── run_evaluation.py        # Run tests (NEEDS SIMPLIFICATION)
│   ├── ai_judge.py              # Quality eval (NEEDS SIMPLIFICATION)
│   └── generate_comparison_report.py  # Report (NEEDS SIMPLIFICATION)
│
├── config/
│   ├── configs.yaml             # System config
│   └── test_suites/
│       └── standard_questions.json  # Test questions (25 questions)
│
└── test_results/                # Latest test runs only
    ├── jina_claude/
    │   ├── results_20251128-015603.json
    │   └── eval_20251128-015603.json
    ├── jina_gpt4/
    ├── tavily_claude/
    ├── tavily_gpt4/
    └── benchmark_report_20251128-022600.md
```

---

## 🚀 Next Steps for Implementation Agent

1. **Simplify ai_judge.py** (~100 lines, remove baseline complexity)
2. **Simplify run_evaluation.py** (remove baseline args/code)
3. **Simplify generate_comparison_report.py** (quality/cost/speed/hallucination only)
4. **Update README.md** (clear 3-step quick start)
5. **Test everything works** (run all 4 combinations)
6. **Review final report** (should be simple, readable, actionable)

---

## ✅ Completed

- [x] Architecture clarification (user-controlled evaluation framework)
- [x] Test questions created (25 questions in standard_questions.json)
- [x] Repository cleanup (47MB → 25MB, 22 docs → 3 docs)
- [x] Remove baseline complexity (decided on absolute quality evaluation)
- [x] Define simplified metrics (quality/cost/speed/hallucination)

---

## 📝 Key Decisions Made

**Simplification Decisions**:
- ✅ NO baseline comparison needed (absolute quality evaluation)
- ✅ NO "found more than baseline" metric (overcomplicated)
- ✅ Keep all 25 test questions as-is (good coverage)
- ✅ Focus on 4 metrics: quality, cost, speed, hallucination
- ✅ Simple report format (rankings + detailed breakdown + recommendation)

**Testing Approach**:
- Real-time search (no pre-indexing)
- User-controlled (not agentic - user picks tool+LLM)
- 4 combinations tested
- AI-as-judge for quality evaluation
- Automated cost/speed measurement
