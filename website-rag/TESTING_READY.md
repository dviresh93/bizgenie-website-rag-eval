# Testing Your BizGenie AI Chatbot

You are now fully set up to test your real-time AI chatbot's performance. Follow these steps to generate a baseline, run evaluations, and compare results.

---

## Step 0: Ensure Services Are Running

Make sure your Docker containers are up and healthy.

```bash
cd website-rag
docker-compose up -d --build
docker-compose ps
```
(You should see 'Up' status for `api` and `chromadb`.)

---

## Step 1: Prepare Your Baseline (Ground Truth)

You need to tell the AI Judge what the "correct" answers are.

1.  **Open the baseline file**:
    `website-rag/test_results/ground_truth/baseline.md`
    
    **(If you haven't already, fill this file completely with answers from Perplexity AI or your expert knowledge for all 25 questions.)**

2.  **Perplexity AI Usage Tip**:
    *   Start a new Perplexity chat.
    *   Paste the system prompt from `website-rag/perplexity_system_prompt.txt`.
    *   Then, paste the questions from your `baseline.md` (or `config/test_suites/standard_questions.json`) one by one into Perplexity.
    *   Copy Perplexity's answers and paste them into your `baseline.md` under the `**Answer**:` section for each question.

---

## Step 2: Run Automated Evaluations

Execute the evaluation script for each combination you want to test. This will run all 25 questions and generate a detailed result file.

**Important**: Ensure your API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `TAVILY_API_KEY`, `JINA_API_KEY`) are correctly set in your `website-rag/.env` file.

### Example: Testing Tavily + Claude

```bash
docker-compose exec api python3 scripts/run_evaluation.py --mcp tavily --llm claude
```

### Example: Testing Jina + GPT-4

```bash
docker-compose exec api python3 scripts/run_evaluation.py --mcp jina --llm gpt4
```

### Example: Testing Tavily + GPT-4

```bash
docker-compose exec api python3 scripts/run_evaluation.py --mcp tavily --llm gpt4
```

### Example: Testing Jina + Claude

```bash
docker-compose exec api python3 scripts/run_evaluation.py --mcp jina --llm claude
```

*(Run these commands for all combinations you wish to compare. Each command will take several minutes to complete as it makes live API calls.)*

---

## Step 3: Generate the Comparison Report

Once you've run evaluations for at least two combinations, generate the final report to see their aggregated performance.

```bash
docker-compose exec api python3 scripts/generate_comparison_report.py
```

This will print a ranked leaderboard to your console, showing which combinations perform best on average for quality and speed.

---

## Step 4: Review Detailed Logs and Results

*   **API Logs**:
    `docker-compose logs -f api` (for live output)
    `website-rag/api/app/logs/rag_system.log` (for full history on host)
*   **Individual Results**:
    Look in `website-rag/test_results/{mcp}_{llm}/` for JSON files containing the detailed outcomes for each question.

---

**You are now fully equipped to play with, test, and evaluate your BizGenie AI Chatbot!**
