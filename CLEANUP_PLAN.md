# Repository Cleanup Plan

**Goal:** Simplify repository from 47MB with 25+ docs to clean, maintainable structure

**Date:** 2025-01-28

---

## 📊 Current State

### Documentation (25 files - TOO MANY!)
```
❌ DELETE - Outdated/Superseded:
- EVALUATION_METRICS_AGENTIC.md (old approach)
- IMPLEMENTATION.md (outdated architecture)
- PLAN.md (initial planning, completed)
- ANALYSIS.md (one-time analysis)
- SIMPLIFIED_FRAMEWORK.md (meta-discussion about docs)
- GETTING_STARTED_WITH_TESTING.md (duplicate info)
- README_TESTING.md (duplicate info)
- TEST_PLAN.md (overly detailed)
- EVALUATION_RUBRIC.md (too complex)
- PERFORMANCE_ANALYSIS.md (premature optimization)
- PERFORMANCE_QUICK_REF.md (not needed yet)
- FRAMEWORK_OVERVIEW.md (redundant)
- QUICK_START.md (redundant)
- ADDING_NEW_PLUGINS.md (premature)
- ANALYTICS_AND_INSIGHTS.md (not implemented)
- TESTING_READY.md (duplicate - exists in 2 places!)

✅ KEEP & CONSOLIDATE:
- README.md (main entry point)
- ARCHITECTURE_CORRECTED.md (rename to ARCHITECTURE.md)
- DEVELOPER_GUIDE.md (keep simplified version)
- TODO.md (active tracking)
```

### Test Results (20+ files)
```
❌ DELETE - Old Runs:
- All files from Nov 27 (keep only Nov 28 latest)
- eval_20251127-*.json (old)
- results_20251127-*.json (old)

✅ KEEP - Latest Run Only:
- test_results/jina_claude/eval_20251128-015603.json
- test_results/jina_claude/results_20251128-015603.json
- test_results/jina_gpt4/eval_20251128-020309.json
- test_results/jina_gpt4/results_20251128-020309.json
- test_results/tavily_claude/eval_20251128-014501.json
- test_results/tavily_claude/results_20251128-014501.json
- test_results/tavily_gpt4/eval_20251128-015109.json
- test_results/tavily_gpt4/results_20251128-015109.json
- test_results/ground_truth/baseline.md (DELETE - no longer needed)
- test_results/benchmark_report_*.md (latest only)
```

### Other Files
```
❌ DELETE:
- intro.mp4 (23MB - belongs in separate media repo or README link)
- perplexity_system_prompt.txt (obsolete, using simpler approach)
- website-rag/ subdirectory (duplicate files)
- tests/jina_output.md (old test outputs)
- tests/jina_output_2.md (old test outputs)

✅ KEEP:
- .env.example
- docker-compose.yml
- config/test_suites/standard_questions.json
- All code in api/, scripts/, ui/
```

---

## 🎯 Target Structure

```
website-rag/
├── README.md                          # Main entry point (simplified)
├── ARCHITECTURE.md                    # System design (consolidated)
├── TODO.md                            # Active tasks
│
├── .env.example                       # Config template
├── docker-compose.yml                 # Infrastructure
│
├── api/                               # Backend code
│   ├── app/
│   │   ├── tools/                     # MCP tool implementations
│   │   │   ├── base.py
│   │   │   ├── jina_tool.py
│   │   │   └── tavily_tool.py
│   │   ├── llm/                       # LLM implementations
│   │   │   ├── base.py
│   │   │   ├── claude_llm.py
│   │   │   └── gpt4_llm.py
│   │   └── core/                      # Core utilities
│   │       ├── logging.py
│   │       └── prompts.py
│
├── scripts/                           # Testing & evaluation
│   ├── run_evaluation.py              # Run tests (SIMPLIFIED)
│   ├── ai_judge.py                    # Quality evaluation (SIMPLIFIED)
│   └── generate_comparison_report.py  # Results report (SIMPLIFIED)
│
├── config/
│   ├── configs.yaml                   # System configuration
│   └── test_suites/
│       └── standard_questions.json    # Test questions
│
├── test_results/                      # Latest test runs only
│   ├── jina_claude/
│   │   ├── results_latest.json
│   │   └── eval_latest.json
│   ├── jina_gpt4/
│   ├── tavily_claude/
│   ├── tavily_gpt4/
│   └── comparison_report.md
│
└── ui/                                # Frontend (if needed)
    └── script.js
```

**Result:**
- 25 docs → 2 docs (README + ARCHITECTURE)
- 47MB → ~20MB (remove video)
- Clear, maintainable structure

---

## 📝 Consolidated Documentation

### README.md (New Structure)
```markdown
# BizGenie AI - MCP Tool + LLM Evaluation Framework

Simple framework to evaluate MCP tools (Jina, Tavily) with LLMs (Claude, GPT-4).

## Quick Start
1. Setup: `cp .env.example .env` (add API keys)
2. Run: `python scripts/run_evaluation.py --mcp jina --llm claude`
3. Compare: `python scripts/generate_comparison_report.py`

## What It Does
- Tests MCP tool + LLM combinations
- Measures quality, cost, speed
- Detects hallucinations
- Recommends best combination

## Architecture
See ARCHITECTURE.md for details.

## Results
Latest benchmark: test_results/comparison_report.md
```

### ARCHITECTURE.md (Consolidated)
```markdown
# Architecture

## Overview
User-controlled evaluation framework:
- User picks MCP tool + LLM via CLI
- System runs real-time search + answer generation
- AI judge evaluates quality
- Report compares all combinations

## Components
[Base classes, MCP tools, LLMs, AI judge]

## Evaluation Flow
[Simple diagram]

## Metrics
- Quality: 0-100 (AI judge score)
- Cost: $/query
- Speed: seconds/query
- Safety: hallucination rate
```

---

## 🚀 Execution Plan

### Phase 1: Safe Backup (5 min)
```bash
# Create backup before cleanup
cd /home/virus/Documents/repo/bizgenie/
tar -czf website-rag-backup-20251128.tar.gz website-rag/
```

### Phase 2: Delete Outdated Docs (5 min)
```bash
cd website-rag/

# Remove 16 outdated documentation files
rm EVALUATION_METRICS_AGENTIC.md
rm IMPLEMENTATION.md
rm PLAN.md
rm ANALYSIS.md
rm SIMPLIFIED_FRAMEWORK.md
rm GETTING_STARTED_WITH_TESTING.md
rm README_TESTING.md
rm TEST_PLAN.md
rm EVALUATION_RUBRIC.md
rm PERFORMANCE_ANALYSIS.md
rm PERFORMANCE_QUICK_REF.md
rm FRAMEWORK_OVERVIEW.md
rm QUICK_START.md
rm ADDING_NEW_PLUGINS.md
rm ANALYTICS_AND_INSIGHTS.md
rm website-rag/TESTING_READY.md
rm TESTING_READY.md

# Rename to simpler name
mv ARCHITECTURE_CORRECTED.md ARCHITECTURE.md
mv EVALUATION_METRICS_FINAL.md docs/EVALUATION_METRICS.md  # Archive
mv DEVELOPER_GUIDE.md docs/DEVELOPER_GUIDE.md  # Archive
```

### Phase 3: Clean Test Results (5 min)
```bash
# Keep only latest test runs
cd test_results/

# Delete old runs
find . -name "*20251127*" -delete

# Delete baseline (no longer needed)
rm ground_truth/baseline.md
rmdir ground_truth

# Rename latest files for clarity
cd jina_claude/
mv eval_20251128-015603.json eval_latest.json
mv results_20251128-015603.json results_latest.json

# Repeat for other combinations...
```

### Phase 4: Remove Large Files (2 min)
```bash
# Remove 23MB video
rm intro.mp4

# Remove obsolete files
rm perplexity_system_prompt.txt
rm -rf website-rag/  # duplicate directory
rm -rf tests/  # old test outputs
```

### Phase 5: Simplify Code (30 min)
- Simplify ai_judge.py (remove baseline complexity)
- Update run_evaluation.py (quality-only approach)
- Update generate_comparison_report.py (simpler output)

### Phase 6: Update Documentation (20 min)
- Rewrite README.md (concise quick start)
- Update ARCHITECTURE.md (consolidated)
- Update TODO.md (current tasks only)

---

## 📏 Success Metrics

**Before:**
- Size: 47MB
- Docs: 25 files
- Complexity: High
- Clarity: Low

**After:**
- Size: ~20MB (57% reduction)
- Docs: 2 files (92% reduction)
- Complexity: Low
- Clarity: High

---

## ⚠️ Risks & Mitigation

**Risk 1:** Accidentally delete something important
- **Mitigation:** Create backup first (tar.gz)

**Risk 2:** Break working code
- **Mitigation:** Git commit before cleanup

**Risk 3:** Lose valuable documentation
- **Mitigation:** Archive in docs/ instead of delete

---

## 🎯 Next Actions

1. ✅ Review this plan
2. ⏸️  User approval to proceed
3. 🔄 Execute cleanup
4. 🔄 Simplify code
5. 🔄 Test everything still works
6. 🔄 Git commit clean state

**Ready to execute?**
