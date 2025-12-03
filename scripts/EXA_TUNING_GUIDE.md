# Exa.ai Tuning & Testing Guide

This guide helps you test different Exa.ai configurations to optimize search results for BizGenie.

## Quick Start

### Basic Test (All Configurations)
```bash
docker-compose exec api python3 scripts/test_exa_tuning.py
```

### Test Specific Configuration
```bash
# Test neural search only
docker-compose exec api python3 scripts/test_exa_tuning.py --config neural_basic

# Test with answer generation
docker-compose exec api python3 scripts/test_exa_tuning.py --config neural_extended --generate-answers
```

### Test Fewer Questions (Faster)
```bash
docker-compose exec api python3 scripts/test_exa_tuning.py --questions 3
```

## Available Configurations

The script tests 5 different configurations:

| Configuration | Type | Results | Domain Filter | Description |
|---------------|------|---------|---------------|-------------|
| `neural_basic` | neural | 5 | bizgenieai.com | Recommended starting point |
| `neural_extended` | neural | 10 | bizgenieai.com | More comprehensive results |
| `keyword_basic` | keyword | 5 | bizgenieai.com | Traditional keyword search |
| `auto_search` | auto | 5 | bizgenieai.com | Let Exa decide search type |
| `neural_no_domain` | neural | 5 | None | No domain filter (might find more) |

## Output Files

Results are saved to `test_results/exa_tuning/`:

- `exa_test_TIMESTAMP.json` - Raw test results with all data
- `exa_report_TIMESTAMP.md` - Human-readable comparison report

## Understanding Results

### Success Metrics
- **Success Rate**: How many questions returned results
- **Avg Results**: Average number of results per question
- **Avg Time**: Average search time
- **Total Results**: Total results across all questions

### Example Output
```
📋 TESTING: NEURAL_BASIC
Settings: type=neural, num_results=5, domains=['bizgenieai.com']

[1/5] Testing: What core services does BizGenie provide...
    ✅ Found 3 results in 1.2s

📊 Summary for neural_basic:
   Success Rate: 5/5 (100.0%)
   Total Results Found: 18
   Avg Search Time: 1.15s
```

## Tweaking Configurations

Edit `scripts/test_exa_tuning.py` and modify the `EXA_CONFIGS` dictionary:

```python
"my_custom_config": {
    "type": "neural",              # or "keyword" or "auto"
    "num_results": 10,             # How many results to fetch
    "include_domains": ["bizgenieai.com"],  # Domain filter
    "text": True,                  # Get full text content
    "start_published_date": "2024-01-01",  # Optional date filter
    "description": "My custom test configuration"
}
```

Then run:
```bash
docker-compose exec api python3 scripts/test_exa_tuning.py --config my_custom_config
```

## Common Issues & Solutions

### Issue: "No results found" (0 results for all questions)

**Possible Causes:**
1. Site not indexed by Exa yet
2. Domain filter too restrictive
3. Content not crawlable

**Solutions to Try:**
```bash
# Try without domain filter
docker-compose exec api python3 scripts/test_exa_tuning.py --config neural_no_domain

# Check if site is indexed at all
# Add this to the script to check specific URL:
# exa_client.search("bizgenieai.com", type="neural", num_results=1)
```

### Issue: Poor quality results

**Solutions:**
1. Try `neural_extended` for more results
2. Use `auto_search` to let Exa pick best mode
3. Adjust `num_results` higher (10-20)

### Issue: Results not relevant to questions

**Solutions:**
1. Include question context in search query
2. Try keyword search instead of neural
3. Add more specific domain filters

## Sharing Results with Exa.ai Team

When reporting issues to Exa.ai:

1. **Run comprehensive test:**
```bash
docker-compose exec api python3 scripts/test_exa_tuning.py --generate-answers
```

2. **Include these files in your report:**
   - `test_results/exa_tuning/exa_report_TIMESTAMP.md`
   - `test_results/exa_tuning/exa_test_TIMESTAMP.json`

3. **Key information to share:**
   - Target website: `bizgenieai.com`
   - Site launch date: [Add date if known]
   - Expected vs actual result counts
   - Specific configuration that should work but doesn't
   - Comparison with other tools (Jina, Tavily, Firecrawl)

## Example Report Email to Exa Team

```
Subject: BizGenie Domain Search Results - Need Guidance

Hi Exa Team,

We're evaluating Exa.ai for our RAG system but getting inconsistent results
for our target domain (bizgenieai.com).

Test Results:
- Configuration: neural_basic (neural search, 5 results, domain filter)
- Questions tested: 5
- Success rate: 2/5 (40%)
- Average results when successful: 2.5

Expected: 5/5 questions should return 3-5 results each
Actual: Only getting results for 2 questions, and only 2-3 results per question

Comparison with competitors:
- Jina Reader: 5/5 success, 5+ results per question
- Tavily: 5/5 success, 4-5 results per question

Questions:
1. Is bizgenieai.com fully indexed in your system?
2. What's the best configuration for single-domain searches?
3. Are there any domain-specific settings we should enable?

Attached: Full test results (JSON + report)

Thanks!
```

## Advanced Usage

### Add Custom Questions

Edit the `TEST_QUESTIONS` list in `scripts/test_exa_tuning.py`:

```python
TEST_QUESTIONS = [
    "Your custom question 1",
    "Your custom question 2",
    # ... add more
]
```

### Test Multiple Domains

```python
"multi_domain": {
    "type": "neural",
    "num_results": 10,
    "include_domains": ["bizgenieai.com", "competitor1.com", "competitor2.com"],
    "text": True,
    "description": "Compare across multiple domains"
}
```

### Add Date Filters

```python
"recent_only": {
    "type": "neural",
    "num_results": 5,
    "start_published_date": "2024-11-01",  # Only recent content
    "include_domains": ["bizgenieai.com"],
    "text": True,
    "description": "Only recent content from Nov 2024+"
}
```

## Next Steps After Testing

1. **If results are good:** Add Exa back to main benchmark
   ```bash
   # Edit scripts/run_benchmark.sh and add:
   # "exa claude"
   # "exa gpt4"
   ```

2. **If results need improvement:** Work with Exa team using reports

3. **If site not indexed:** Request indexing or wait for crawl cycle

## Support

- Exa.ai Docs: https://docs.exa.ai/
- API Reference: https://docs.exa.ai/reference/
- Contact: [Your Exa.ai contact email]
