# Quick Reference: Evaluation Rubric

## Scoring Cheat Sheet

### Answer Quality Score (0-100)

#### Component Breakdown
| Component | Max Points | What to Evaluate |
|-----------|------------|------------------|
| **Accuracy** | 30 | Factually correct? Any errors? |
| **Completeness** | 25 | Covers all aspects? Missing info? |
| **Relevance** | 15 | Directly answers question? |
| **Coherence** | 15 | Well-structured? Logical flow? |
| **Source Attribution** | 15 | Sources cited? Accurate? |
| **TOTAL** | **100** | |

#### Quick Rating Guide

**Accuracy (30 points)**
- 30 = Perfect, no errors
- 25 = Minor wording issue, facts correct
- 20 = Mostly correct, 1-2 minor errors
- 15 = Several minor errors
- 10 = Major error but some correct info
- 5 = Multiple major errors
- 0 = Completely wrong or hallucinated

**Completeness (25 points)**
- 25 = Comprehensive, nothing missing
- 20 = Covers main points, minor omissions
- 15 = Missing 1-2 important details
- 10 = Missing significant information
- 5 = Superficial, major gaps
- 0 = Barely addresses question

**Relevance (15 points)**
- 15 = Perfectly on-topic
- 12 = Mostly relevant, minor tangent
- 9 = Somewhat relevant, some off-topic
- 6 = Partially relevant
- 3 = Mostly off-topic
- 0 = Completely irrelevant

**Coherence (15 points)**
- 15 = Perfect structure, excellent flow
- 12 = Well-organized, easy to follow
- 9 = Generally coherent, minor issues
- 6 = Somewhat disorganized
- 3 = Hard to follow
- 0 = Incoherent or nonsensical

**Source Attribution (15 points)**
- 15 = Accurate sources, well-cited
- 12 = Good sources, could be more detailed
- 9 = Sources present but vague
- 6 = Minimal source information
- 3 = Very poor attribution
- 0 = No sources mentioned

---

## Similarity to NotebookLLM Score (0-100)

### Automated Components

**BLEU Score** (0-1)
- Measures word/phrase overlap
- Higher = more similar wording
- Multiply by 100 for percentage

**Semantic Similarity** (0-1)
- Cosine similarity of embeddings
- Higher = more similar meaning
- Multiply by 100 for percentage

**Coverage Score** (0-1)
- % of key facts from baseline present
- Count facts in baseline
- Count facts in answer
- Coverage = (matched_facts / baseline_facts)

**Combined Formula:**
```
Similarity = (BLEU × 0.3) + (Semantic × 0.4) + (Coverage × 0.3)
```

---

## Performance Metrics

### Response Time Score
```
Score = max(0, 100 - (actual_seconds / 3.0 × 100))
```
- 0s = 100 points
- 1.5s = 50 points
- 3.0s+ = 0 points

### Cost Efficiency Score
```
Score = max(0, 100 - (actual_cost / 0.05 × 100))
```
- $0.00 = 100 points
- $0.025 = 50 points
- $0.05+ = 0 points

### Retrieval Accuracy
```
Score = (relevant_chunks / total_chunks) × 100
```
- All relevant = 100 points
- Half relevant = 50 points

### Reliability Score
```
Score = 100 - (error_rate × 100)
```
- 0% errors = 100 points
- 5% errors = 95 points
- 10% errors = 90 points

---

## UX Ratings (1-5 scale)

### Readability
- 5 = Crystal clear, perfect grammar
- 4 = Easy to understand
- 3 = Understandable with minor issues
- 2 = Somewhat hard to follow
- 1 = Very difficult to understand

### Actionability
- 5 = User can immediately take action
- 4 = Clear next steps provided
- 3 = Some guidance, not complete
- 2 = Vague direction
- 1 = No actionable information

### Trustworthiness
- 5 = Complete confidence in answer
- 4 = Generally trustworthy
- 3 = Somewhat confident
- 2 = Questionable accuracy
- 1 = Not trustworthy

### Completeness
- 5 = Fully addresses all aspects
- 4 = Addresses most aspects
- 3 = Partial answer
- 2 = Minimal coverage
- 1 = Barely answers question

**UX Score Calculation:**
```
UX_Score = Average(Readability, Actionability, Trustworthiness, Completeness) × 20
```

---

## Overall Configuration Score

### Formula
```
Overall Score =
  (Answer Quality × 0.40) +
  (Similarity to NotebookLLM × 0.25) +
  (Performance × 0.20) +
  (UX Score × 0.15)
```

### Score Interpretation

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 90-100 | Excellent | Exceeds NotebookLLM in some areas |
| 80-89 | Very Good | Comparable to NotebookLLM |
| 70-79 | Good | Acceptable for production |
| 60-69 | Fair | Needs improvement |
| 50-59 | Poor | Not recommended |
| 0-49 | Very Poor | Major issues |

---

## Decision Matrix

### When to Use This Configuration

**Score ≥ 80 + Low Cost**
→ **Production-ready for high-volume use**

**Score ≥ 80 + High Quality (≥85)**
→ **Production-ready for customer-facing chatbot**

**Score 70-79**
→ **Acceptable for internal use or beta**

**Score < 70**
→ **Not recommended, needs work**

### Red Flags

❌ **Disqualify if:**
- Hallucinations on factual questions
- Error rate > 5%
- Missing sources on > 20% of questions
- Consistently lower quality than NotebookLLM

---

## Quick Evaluation Checklist

For each answer, ask:

**Accuracy:**
- [ ] All facts correct?
- [ ] No hallucinations?
- [ ] Matches ground truth?

**Completeness:**
- [ ] All key points covered?
- [ ] No major omissions?
- [ ] Comparable to NotebookLLM?

**Quality:**
- [ ] Well-written?
- [ ] Easy to understand?
- [ ] Properly formatted?

**Sources:**
- [ ] Sources cited?
- [ ] Sources accurate?
- [ ] Sources relevant?

**Performance:**
- [ ] Response time acceptable (< 3s)?
- [ ] Cost acceptable (< $0.05)?
- [ ] No errors?

---

## Tie-Breaker Rules

If two configurations have similar scores (< 3 point difference):

1. **Choose lower cost** if quality is similar
2. **Choose faster** if cost is similar
3. **Choose more reliable** (lower error rate) if close
4. **Choose better UX** (higher UX score) as final tiebreaker

---

## Example Scoring

**Question:** "What is BizGenie?"

**NotebookLLM Baseline:**
"BizGenie is an AI-powered automation platform that helps businesses streamline their operations through intelligent workflow automation and process optimization."

**Configuration Answer:**
"BizGenie is a business automation platform using AI to help companies automate their workflows."

**Scoring:**
- Accuracy: 28/30 (correct but less detailed)
- Completeness: 18/25 (missing "process optimization")
- Relevance: 15/15 (directly answers)
- Coherence: 15/15 (clear and concise)
- Source Attribution: 10/15 (vague source)
- **Answer Quality: 86/100**

- BLEU: 0.45
- Semantic Similarity: 0.92
- Coverage: 0.75
- **Similarity: 77/100**

- Response Time: 2.1s → 93/100
- Cost: $0.02 → 60/100
- Retrieval: 4/5 relevant → 80/100
- **Performance: 78/100**

- Readability: 5, Actionability: 3, Trust: 4, Complete: 4
- **UX Score: 80/100**

**Overall Score:**
```
(86 × 0.40) + (77 × 0.25) + (78 × 0.20) + (80 × 0.15) = 81.65
```

**Verdict:** ✅ Very Good - Production ready
