# BizGenie AI - MCP Tool + LLM Evaluation Framework

A modular evaluation framework for testing different **MCP (Model Context Protocol) tools** and **LLMs** to find the best combination for answering questions about BizGenie services.

## 🎯 What This Framework Does

Tests **4 combinations** of search tools and LLMs:
- **Jina AI Reader** + **Claude 3.5 Sonnet**
- **Jina AI Reader** + **GPT-4 Turbo**
- **Tavily AI Search** + **Claude 3.5 Sonnet**
- **Tavily AI Search** + **GPT-4 Turbo**

**Measures 19 metrics** including:
- Quality (accuracy, completeness, clarity, helpfulness)
- Speed (search latency, generation latency, total time)
- Cost (search cost, generation cost, total cost)
- Reliability (hallucinations, token usage)

**Generates comprehensive reports** showing which combination performs best for your use case.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone git@github.com:dviresh93/bizgenie-website-rag-eval.git
cd bizgenie-website-rag-eval

# Set up API keys
cp .env.example .env
# Edit .env and add your keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-...
#   JINA_API_KEY=...
#   TAVILY_API_KEY=...
```

### 2. Run Evaluations

```bash
# Run all 4 combinations (takes ~10 minutes)
python scripts/run_evaluation.py --mcp jina --llm claude
python scripts/run_evaluation.py --mcp jina --llm gpt4
python scripts/run_evaluation.py --mcp tavily --llm claude
python scripts/run_evaluation.py --mcp tavily --llm gpt4
```

### 3. Generate Report

```bash
# Compare all combinations
python scripts/generate_comparison_report.py
```

**Output:** Comprehensive markdown report in `test_results/benchmark_report_[timestamp].md`

## 📊 Sample Report Output

```
🏆 Overall Rankings
| Rank | Combination    | Quality | Total Cost | Total Time | Search Time | Gen Time | Halluc. |
|------|----------------|---------|------------|------------|-------------|----------|---------|
| 1    | jina_claude    | 85.2    | $0.0144    | 9.71s      | 0.57s       | 9.14s    | 0       |
| 2    | tavily_claude  | 82.1    | $0.0192    | 7.15s      | 0.37s       | 6.78s    | 1       |

🎯 Recommendations
BEST OVERALL: JINA_CLAUDE
- Highest quality (85.2/100)
- Zero hallucinations
- Use when: Quality and reliability matter most

⚡ BEST FOR SPEED: TAVILY_GPT4
- Fastest total time (4.7s)
- Use when: Speed is critical
```

## 📁 Repository Structure

```
website-rag/
├── README.md              # This file
├── ARCHITECTURE.md        # System design documentation
├── TODO.md               # Implementation checklist
│
├── .env.example          # API keys template
├── scripts/              # Evaluation scripts
│   ├── run_evaluation.py              # Run tests
│   ├── ai_judge.py                    # AI quality evaluator
│   └── generate_comparison_report.py  # Report generator
│
├── config/
│   └── test_suites/
│       └── standard_questions.json    # 25 test questions
│
├── api/                  # Tool implementations
│   ├── app/tools/        # MCP tool implementations (Jina, Tavily)
│   └── app/llm/          # LLM implementations (Claude, GPT-4)
│
└── test_results/         # Generated reports and data
```

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture
- **[TODO.md](TODO.md)** - Development checklist and implementation guide

## 🧪 How It Works

1. **Test Questions:** Framework asks 25 questions about BizGenie services
2. **Real-time Search:** Each MCP tool searches bizgenieai.com for relevant information
3. **Answer Generation:** LLM generates answer based on search results
4. **AI Judge Evaluation:** Separate AI judges answer quality (accuracy, completeness, clarity, helpfulness)
5. **Metrics Collection:** Tracks search time, generation time, cost, token usage
6. **Comprehensive Report:** Shows which combination performs best across all metrics

## 🎯 Evaluation Metrics

### Quality Metrics (6)
- Overall Quality Score (0-100)
- Accuracy, Completeness, Clarity, Helpfulness
- Hallucination Detection

### Performance Metrics (4)
- Search Latency, Generation Latency, Total Latency
- Fastest/Slowest Query Range

### Cost Metrics (5)
- Search Cost, Generation Cost, Total Cost
- Total Cost for 25 Queries
- Most/Least Expensive Query

### Reliability Metrics (4)
- Failed Queries, Token Usage
- Answer Length, Quality Distribution

## 🔧 Prerequisites

- Python 3.11+
- API Keys:
  - **Anthropic API** (for Claude)
  - **OpenAI API** (for GPT-4)
  - **Jina AI API** (optional - free tier available)
  - **Tavily API** (for search)

## 💡 Use Cases

**Choose the best combination for your needs:**
- **Quality-focused:** Use jina_claude (highest accuracy, zero hallucinations)
- **Speed-focused:** Use tavily_gpt4 (fastest total time)
- **Budget-focused:** Use jina_claude (lowest cost per query)
- **Balance:** Compare all metrics in the report

## 🚧 Advanced Usage

### Custom Test Questions

Edit `config/test_suites/standard_questions.json` to add your own questions:

```json
{
  "id": "q26",
  "question": "Your custom question here",
  "category": "custom",
  "difficulty": "medium"
}
```

### Run Single Combination

```bash
python scripts/run_evaluation.py --mcp jina --llm claude
```

### Compare Specific Runs

The framework automatically uses the latest results. To compare specific runs, check `test_results/` directory.

## 📈 Performance Tips

- **Faster testing:** Run combinations in parallel (separate terminals)
- **Cost optimization:** Use Jina (free tier) instead of Tavily ($0.012/search)
- **Quality optimization:** Use Claude for fewer hallucinations
- **Speed optimization:** Use GPT-4 for faster generation

## 🐛 Troubleshooting

### Issue: No API key found

**Fix:** Ensure `.env` file exists with valid API keys:
```bash
cp .env.example .env
# Edit .env and add your actual keys
```

### Issue: Rate limit errors

**Fix:** Add delays between runs or use different API keys for parallel testing.

### Issue: Empty or incomplete reports

**Fix:** Ensure all 4 combinations have completed successfully. Check `test_results/` for eval and results files.

## 📊 Current Results

Latest benchmark report available at: `test_results/benchmark_report_[latest].md`

**Key Findings:**
- Jina + Claude: Highest quality (72.6/100), zero hallucinations
- Tavily + GPT-4: Fastest speed (4.7s average)
- Jina combinations: Lower cost ($0.014 vs $0.019)
- All combinations: Zero hallucinations on current test set

## 🗺️ Roadmap

- [x] Core evaluation framework
- [x] Jina + Tavily MCP tools
- [x] Claude + GPT-4 LLMs
- [x] AI-as-judge evaluation
- [x] Comprehensive metrics (19 total)
- [ ] Web UI for running evaluations
- [ ] More MCP tools (Firecrawl, Exa, etc.)
- [ ] More LLMs (Gemini, Mistral, etc.)
- [ ] Custom evaluation criteria

## 💡 Credits

Built with:
- [Anthropic Claude](https://www.anthropic.com/claude) - LLM and AI judge
- [OpenAI GPT-4](https://openai.com/) - LLM
- [Jina AI Reader](https://jina.ai/reader) - Web content extraction
- [Tavily AI](https://tavily.com/) - AI search engine
- [Python](https://python.org/) - Framework language

---

**Made with ❤️ for BizGenie AI**
