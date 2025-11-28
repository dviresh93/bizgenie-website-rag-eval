# 🧪 BizGenie RAG Testing Framework

This document explains how we evaluate the performance, quality, and reliability of our AI Chatbot.

---

## 1. The Evaluation Philosophy

We do not rely on simple keyword matching. Instead, we use an **"AI-as-a-Judge"** approach to grade answers semantically, just like a human QA engineer would.

### What we test
We evaluate different combinations of **Retrieval Tools** (Search) and **LLMs** (Reasoning) to find the best "Brain" for our bot.
*   **Tools:** Tavily vs. Jina
*   **Models:** Claude 3.5 vs. GPT-4

### The Metrics (Rubric)
Our AI Judge (Claude 3 Opus) grades every answer on a 0-100 scale based on 5 criteria:

1.  **Accuracy (40%)**: Is the answer factually correct based on the retrieved context?
2.  **Completeness (30%)**: Did it answer *all* parts of the user's question?
3.  **Clarity (15%)**: Is it easy to read and professional?
4.  **Helpfulness (15%)**: Did it actually solve the user's problem?
5.  **Hallucination Check (Critical)**:
    *   We verify if specific claims (numbers, features) are supported by the source text.
    *   *If unsupported claims are found, the score is slashed by 50%.*

---

## 2. Test Structure

### The Input Data
*   **File:** `config/test_suites/standard_questions.json`
*   **Content:** 25 curated questions covering:
    *   Core Services
    *   Technical Integrations
    *   Pricing & Support
    *   Edge Cases / "Trick" Questions

### The Pipeline
When you run the benchmark, the system does this for **each question**:

1.  **Search Phase:** The selected Tool (e.g., Tavily) searches the live web or reads the target URL.
2.  **Generation Phase:** The selected LLM (e.g., Claude) generates an answer using *only* that found context.
3.  **Evaluation Phase:** A separate "Judge" LLM reads the Question, the Answer, and the Context. It produces a JSON report card.

---

## 3. How to Run Tests

### A. Full Benchmark (Recommended)
Runs all 4 combinations and generates a comparative leaderboard.

```bash
docker-compose exec api bash scripts/run_benchmark.sh
```

### B. Individual Debug Run
Run a single specific combination to debug an issue.

```bash
docker-compose exec api python3 scripts/run_evaluation.py --mcp jina --llm claude
```

---

## 4. Analyzing Results

After a run, check the report at:
`website-rag/test_results/benchmark_report_TIMESTAMP.md`

### Key Signals
*   **High Quality (>80):** Safe for production.
*   **High Hallucinations (>2):** **DANGER.** The model is guessing. Check the individual JSON logs to see why (usually missing context).
*   **Slow Speed (>10s):** Bad UX. Consider switching to a faster model (GPT-4) or tool (Tavily).

---

## 5. Project Structure

*   `scripts/run_evaluation.py`: The engine. Orchestrates Search -> Generate -> Grade.
*   `scripts/ai_judge.py`: The brain. Contains the prompts and logic for grading.
*   `scripts/generate_comparison_report.py`: The analyst. Aggregates JSON files into a readable table.
