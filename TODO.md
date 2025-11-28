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
- Focus on **4 simple metrics**: Quality, Cost, Speed, Hallucinations
- Report structure:
```markdown
# MCP Tool + LLM Comparison Report

## 🏆 Overall Rankings
| Rank | Combination    | Quality | Cost/Query | Speed  | Halluc. |
|------|----------------|---------|------------|--------|---------|
| 1    | jina_claude    | 85.2    | $0.024     | 3.2s   | 0       |
| 2    | tavily_claude  | 82.1    | $0.031     | 2.8s   | 1       |
...

## 📊 Detailed Metrics

### JINA_CLAUDE
- Average Quality: 85.2/100
- Average Cost: $0.024/query
- Average Speed: 3.2s/query
- Hallucinations: 0/25 questions

Top scoring questions: q1 (95), q3 (92), q4 (90)
Low scoring questions: q15 (45), q18 (52)

### TAVILY_CLAUDE
...

## ✅ Recommendation
**Best Overall**: JINA_CLAUDE
- Highest quality (85.2/100)
- Zero hallucinations
- Acceptable cost ($0.024/query)
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
1. **Quality Score** (0-100): AI judge rates accuracy, completeness, clarity, helpfulness
2. **Cost** ($/query): Search cost + LLM generation cost
3. **Speed** (seconds): Search time + generation time
4. **Hallucination Rate**: Questions where AI made unsupported claims

### Success Criteria
- Quality score > 80/100 (excellent)
- Zero or minimal hallucinations
- Cost < $0.05/query (acceptable for business use)
- Speed < 5s/query (acceptable UX)

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
