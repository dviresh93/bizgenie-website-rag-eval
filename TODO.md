# TODO

**Last Updated**: 2025-01-26

---

## 🚨 CRITICAL: Architecture Clarification

**DISCOVERED**: Current implementation is WRONG for our use case!

**Problem**:
- Built static RAG (pre-index → query ChromaDB)
- We need **real-time search evaluation framework**

**What We're Actually Building**:
- **NOT** an agentic system where LLM decides which tools to use
- **YES** a testing framework where USER picks MCP tool + LLM via dropdowns
- Goal: Evaluate which MCP tool + LLM combination performs best
- Use case: User picks Tavily + Claude → system uses those exact components

**Impact**:
- Simpler than agentic approach
- Two dropdowns: [MCP Tool] + [LLM Model]
- Real-time search per query (no indexing)
- Metrics compare MCP tools and LLMs
- ChromaDB not needed (unless caching later)

---

## Current Work (PRIORITIZED)

### Phase 1: Core Architecture Redesign 🔴 CRITICAL
- [x] Clarify architecture (evaluation framework, not agentic) (DONE)
- [x] Document architecture in ARCHITECTURE_CORRECTED.md (DONE)
- [x] Document metrics in EVALUATION_METRICS_FINAL.md (DONE)
- [ ] Implement MCPTool base class
  - search(question, context) method
  - get_info() for tool metadata
  - Update base.py
- [ ] Implement JinaTool (MCPTool)
  - Real-time search using Jina MCP
  - Returns SearchResult
- [ ] Implement TavilyTool (MCPTool)
  - Real-time search using Tavily API
  - Returns SearchResult
- [ ] Implement LLM base class
  - generate(question, context) method
  - get_info() for model metadata
  - Update base.py
- [ ] Implement ClaudeLLM
  - Generate answers using Claude
  - Returns LLMResponse
- [ ] Implement GPT4LLM
  - Generate answers using GPT-4
  - Returns LLMResponse
- [ ] Update API endpoints
  - Remove `/index` endpoint entirely
  - Update `/query` to accept mcp_tool + llm_model
  - Update `/components` to return available tools + models
- [ ] Update UI
  - Two dropdowns: MCP Tool + LLM Model
  - Remove indexing UI
  - Display metrics breakdown (search + llm separate)

### Phase 2: Testing Framework Update
- [ ] Update run_evaluation.py
  - Remove indexing phase
  - Add real-time search per query
  - Measure search time separately
- [ ] Update generate_comparison_report.py
  - Remove indexing metrics
  - Add search quality metrics
  - Focus on per-query performance
- [ ] Keep collect_notebookllm_baseline.py as-is
  - Already does real-time search
  - Matches our new approach!

### Phase 3: Testing & Validation
- [ ] Test Tavily + GPT4 combo (real-time)
- [ ] Test Jina + GPT4 combo (real-time)
- [ ] Test Tavily + Claude combo (real-time)
- [ ] Collect NotebookLLM baseline
- [ ] Compare all results
- [ ] Pick winner

---

## Documentation Cleanup (Lower Priority)
- [ ] Move extra docs to `docs/advanced/`
  - TEST_PLAN.md (needs updating for real-time)
  - EVALUATION_RUBRIC.md
  - PERFORMANCE_ANALYSIS.md
  - Others...
- [ ] Update README_TESTING.md for real-time approach
- [ ] Update main README.md

---

## Completed ✅

- [x] Create testing framework scripts
- [x] Create 25 test questions
- [x] Create comparison report generator
- [x] Create documentation (too much!)
- [x] Realize we over-documented 😅

---

## Notes

**Key insight from today**: We created 13 docs when we needed 1-2. Keep it simple!

**Main goal**: Test different tool combinations and pick the best one.

**Files that matter**:
- README_TESTING.md - main guide
- 3 scripts (collect baseline, run evaluation, generate report)
- standard_questions.json - test questions

Everything else = optional reference material.
