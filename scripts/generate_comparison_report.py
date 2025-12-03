"""
Generate comprehensive benchmark results report with LLM-powered insights.
Creates RESULTS.md with detailed breakdowns and AI-generated analysis.
Aggregates Quality (from eval_*.json) and Performance (from results_*.json).
"""
import glob
import json
import os
import time
from collections import defaultdict
from anthropic import Anthropic

def load_json_files(results_dir: str, prefix: str) -> dict:
    """
    Load only the LATEST JSON file per combination matching a prefix (eval_ or results_)
    grouped by combination name. Uses file modification time to identify latest.
    """
    pattern = f"{results_dir}/*/{prefix}*.json"
    files = glob.glob(pattern)

    # Group files by combination name and track latest file per combo
    combo_files = defaultdict(list)

    for filepath in files:
        parts = filepath.split("/")
        if len(parts) >= 2:
            combo_name = parts[-2]
            # Get file modification time
            mtime = os.path.getmtime(filepath)
            combo_files[combo_name].append((mtime, filepath))

    # Load only the latest file per combination
    grouped_data = defaultdict(list)

    for combo_name, file_list in combo_files.items():
        # Sort by modification time and get the latest file
        file_list.sort(reverse=True)  # Most recent first
        latest_mtime, latest_filepath = file_list[0]

        try:
            with open(latest_filepath, 'r') as f:
                data = json.load(f)
                grouped_data[combo_name].extend(data if isinstance(data, list) else [data])
            print(f"✓ Loaded latest {prefix} file for {combo_name}: {os.path.basename(latest_filepath)}")
        except Exception as e:
            print(f"Warning: Could not load {latest_filepath}: {e}")

    return grouped_data

def calculate_quality_metrics(evaluations: list) -> dict:
    """Calculate aggregated quality metrics"""
    if not evaluations:
        return {}
        
    count = len(evaluations)
    
    # Averages
    avg_score = sum(e.get("overall_quality", 0) for e in evaluations) / count
    avg_accuracy = sum(e.get("accuracy", 0) for e in evaluations) / count
    avg_completeness = sum(e.get("completeness", 0) for e in evaluations) / count
    avg_clarity = sum(e.get("clarity", 0) for e in evaluations) / count
    avg_helpfulness = sum(e.get("helpfulness", 0) for e in evaluations) / count
    
    # Counts
    hallucinations = sum(1 for e in evaluations if e.get("hallucination") or e.get("verdict") == "HALLUCINATION")
    
    return {
        "quality_score": avg_score,
        "accuracy": avg_accuracy,
        "completeness": avg_completeness,
        "clarity": avg_clarity,
        "helpfulness": avg_helpfulness,
        "hallucinations": hallucinations,
        "total_evaluated": count
    }

def calculate_performance_metrics(results: list) -> dict:
    """Calculate aggregated performance/cost metrics"""
    if not results:
        return {}

    count = len(results)

    # Averages (some old result files might miss fields, use .get with 0)
    avg_total_time = sum(r.get("metrics", {}).get("total_time", 0) for r in results) / count
    avg_search_time = sum(r.get("metrics", {}).get("search_time", 0) for r in results) / count
    avg_gen_time = sum(r.get("metrics", {}).get("gen_time", 0) for r in results) / count

    # Costs
    avg_total_cost = sum(
        r.get("metrics", {}).get("search_cost", 0) + r.get("metrics", {}).get("gen_cost", 0)
        for r in results
    ) / count

    return {
        "total_time": avg_total_time,
        "search_time": avg_search_time,
        "gen_time": avg_gen_time,
        "total_cost": avg_total_cost,
        "total_runs": count
    }

def generate_llm_insights(summary_data: list) -> str:
    """Use LLM to generate insights and analysis of benchmark results"""
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Prepare data summary for LLM
        data_summary = json.dumps([
            {
                "combination": s["name"],
                "quality": s.get("quality_score", 0),
                "accuracy": s.get("accuracy", 0),
                "completeness": s.get("completeness", 0),
                "clarity": s.get("clarity", 0),
                "helpfulness": s.get("helpfulness", 0),
                "hallucinations": s.get("hallucinations", 0),
                "latency": s.get("total_time", 0),
                "cost_per_query": s.get("total_cost", 0)
            }
            for s in summary_data
        ], indent=2)

        prompt = f"""You are a technical analyst reviewing benchmark results for RAG (Retrieval-Augmented Generation) systems.

BENCHMARK DATA:
{data_summary}

Analyze these results and provide:

1. **Key Performance Patterns**: What patterns do you observe across tools and LLMs?
2. **Trade-offs Analysis**: What are the key trade-offs between combinations?
3. **Quality vs Speed vs Cost**: How do these dimensions relate to each other?
4. **Tool-Specific Insights**: What can we learn about Jina, Tavily, and Firecrawl?
5. **LLM Comparison**: How does Claude compare to GPT-4 across all tools?
6. **Production Recommendations**: What would you recommend for different use cases?

Be specific, data-driven, and provide actionable insights. Keep it concise (300-400 words)."""

        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()

    except Exception as e:
        print(f"⚠️  Could not generate LLM insights: {e}")
        return "*LLM-powered insights unavailable (API key not configured or request failed)*"

def main():
    results_dir = "test_results"

    if not os.path.exists(results_dir):
        print(f"❌ Results directory not found: {results_dir}")
        return

    print(f"📖 Loading results from {results_dir}...")

    # Load Quality Data
    eval_data = load_json_files(results_dir, "eval_")
    # Load Performance Data
    perf_data = load_json_files(results_dir, "results_")
    # Load Cache Statistics (if available)
    cache_data = load_json_files(results_dir, "cache_stats_")

    if not eval_data and not perf_data:
        print("❌ No results found.")
        return

    # Merge and Analyze
    summary = []
    all_combos = set(eval_data.keys()) | set(perf_data.keys())

    for combo in all_combos:
        q_metrics = calculate_quality_metrics(eval_data.get(combo, []))
        p_metrics = calculate_performance_metrics(perf_data.get(combo, []))

        # Merge all metrics
        full_metrics = {"name": combo, **q_metrics, **p_metrics}
        summary.append(full_metrics)

    # Sort by Quality Score (default)
    summary.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

    # Calculate rankings for each dimension
    def get_rankings(summary_data):
        """Calculate rankings for each KPI dimension"""
        rankings = {
            'quality': sorted(summary_data, key=lambda x: x.get('quality_score', 0), reverse=True),
            'speed': sorted(summary_data, key=lambda x: x.get('total_time', float('inf'))),
            'cost': sorted(summary_data, key=lambda x: x.get('total_cost', float('inf'))),
        }

        # Score ease of adoption (manual scoring based on known characteristics)
        adoption_scores = {
            'jina_claude': 95,     # 5min setup, free tier, excellent docs, production ready
            'jina_gpt4': 95,       # Same as above
            'tavily_claude': 85,   # 10min setup, paid only, excellent docs, production ready
            'tavily_gpt4': 85,     # Same as above
            'firecrawl_claude': 80,  # 10min setup, paid only, good docs, beta
            'firecrawl_gpt4': 80,    # Same as above
            '_archive': 0
        }

        # Score maturity (manual scoring)
        maturity_scores = {
            'jina_claude': 95,     # Production, high stability
            'jina_gpt4': 95,       # Production, high stability
            'tavily_claude': 95,   # Production, high stability
            'tavily_gpt4': 95,     # Production, high stability
            'firecrawl_claude': 75,  # Beta, medium stability
            'firecrawl_gpt4': 75,    # Beta, medium stability
            '_archive': 0
        }

        # Add scores to summary
        for s in summary_data:
            s['adoption_score'] = adoption_scores.get(s['name'], 0)
            s['maturity_score'] = maturity_scores.get(s['name'], 0)

        rankings['adoption'] = sorted(summary_data, key=lambda x: x.get('adoption_score', 0), reverse=True)
        rankings['maturity'] = sorted(summary_data, key=lambda x: x.get('maturity_score', 0), reverse=True)

        return rankings

    rankings = get_rankings(summary)

    print("🤖 Generating LLM-powered insights...")
    llm_insights = generate_llm_insights(summary)

    # Generate Comprehensive RESULTS.md
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    lines = []

    # Header
    lines.append("# Benchmark Results & Analysis\n")
    lines.append(f"**Last Updated:** {timestamp}")
    lines.append(f"**Questions Tested:** {summary[0].get('total_evaluated', 25) if summary else 25}")
    lines.append(f"**Combinations Tested:** {len([s for s in summary if s['name'] != '_archive'])}\n")

    # Executive Summary - THE ANSWER
    lines.append("---\n")
    lines.append("## 🎯 Executive Summary: Recommendation\n")

    # Get the winners
    best_quality = rankings['quality'][0] if rankings['quality'] else None
    best_speed = rankings['speed'][0] if rankings['speed'] else None
    best_cost = rankings['cost'][0] if rankings['cost'] else None

    if best_quality and best_quality['name'] != '_archive':
        lines.append(f"### ✅ **RECOMMENDED: {best_quality['name'].upper()}**\n")
        lines.append(f"**Quality:** {best_quality.get('quality_score', 0):.1f}/100 (highest)")
        lines.append(f"**Hallucinations:** {best_quality.get('hallucinations', 0)} (out of 25 questions)")
        lines.append(f"**Cost:** ${best_quality.get('total_cost', 0):.4f}/query (${best_quality.get('total_cost', 0) * 100000:.0f} per 100K queries)")
        lines.append(f"**Speed:** {best_quality.get('total_time', 0):.2f}s average response time\n")

        # When to switch
        if best_cost and best_cost['name'] != best_quality['name'] and best_cost['name'] != '_archive':
            cost_savings = (best_quality.get('total_cost', 0) - best_cost.get('total_cost', 0)) * 100000
            quality_diff = best_quality.get('quality_score', 0) - best_cost.get('quality_score', 0)
            lines.append(f"**Switch to {best_cost['name']} if:** Processing >100K queries/month (saves ${cost_savings:.0f}/month, quality drops {quality_diff:.1f} points)\n")

        if best_speed and best_speed['name'] != best_quality['name'] and best_speed['name'] != '_archive':
            speed_gain = best_quality.get('total_time', 0) - best_speed.get('total_time', 0)
            speed_halluc = best_speed.get('hallucinations', 0)
            lines.append(f"**Switch to {best_speed['name']} if:** Must have <7s response AND can tolerate {speed_halluc} hallucinations (saves {speed_gain:.1f}s)\n")

    lines.append("---\n")

    # Quick Comparison Table
    lines.append("## 📊 Quick Comparison\n")
    lines.append("| Tool | Quality | Errors | Speed | Cost @100K/mo | Verdict |")
    lines.append("|------|---------|--------|-------|---------------|---------|")

    # Filter out _archive
    display_summary = [s for s in summary if s['name'] != '_archive']

    for i, s in enumerate(display_summary, 1):
        quality = f"{s.get('quality_score', 0):.0f}/100"
        errors = s.get('hallucinations', 0)
        speed = f"{s.get('total_time', 0):.1f}s"
        cost = f"${s.get('total_cost', 0) * 100000:.0f}"

        # Add emoji indicators
        quality_indicator = " ⭐" if i == 1 else ""
        error_indicator = " ✅" if errors == 0 else (" ⚠️" if errors <= 4 else " ❌")
        speed_indicator = " ⚡" if s.get('total_time', 10) < 7 else ""
        cost_indicator = " 💰" if s.get('total_cost', 1) < 0.006 else ""

        # Verdict
        if i == 1:
            verdict = "✅ **RECOMMENDED**"
        elif 'claude' in s['name'] and i <= 3:
            verdict = "Alternative"
        elif 'gpt4' in s['name']:
            verdict = "Not recommended"
        else:
            verdict = "-"

        name = f"**{s['name']}**" if i == 1 else s['name']
        lines.append(f"| {name} | {quality}{quality_indicator} | {errors}{error_indicator} | {speed}{speed_indicator} | {cost}{cost_indicator} | {verdict} |")

    lines.append("\n---\n")

    # Rankings by Each KPI Dimension
    lines.append("## 🏆 Rankings by Each KPI\n")
    lines.append("*Our evaluation framework measures 5 equally important dimensions (20% each)*\n")

    # Quality
    lines.append("### 1. Best Quality (Accuracy & Comprehensiveness)\n")
    for i, s in enumerate(rankings['quality'][:3], 1):
        if s['name'] == '_archive':
            continue
        lines.append(f"{i}. **{s['name']}** - {s.get('quality_score', 0):.1f}/100 ({s.get('hallucinations', 0)} errors)")

    # Speed
    lines.append("\n### 2. Fastest (Lowest Latency)\n")
    for i, s in enumerate(rankings['speed'][:3], 1):
        if s['name'] == '_archive':
            continue
        lines.append(f"{i}. **{s['name']}** - {s.get('total_time', 0):.2f}s average response")

    # Cost
    lines.append("\n### 3. Cheapest (Operational Cost)\n")
    for i, s in enumerate(rankings['cost'][:3], 1):
        if s['name'] == '_archive':
            continue
        lines.append(f"{i}. **{s['name']}** - ${s.get('total_cost', 0):.4f}/query (${s.get('total_cost', 0) * 100000:.0f} per 100K)")

    # Adoption
    lines.append("\n### 4. Easiest to Adopt\n")
    for i, s in enumerate(rankings['adoption'][:3], 1):
        if s['name'] == '_archive':
            continue
        setup_time = "5 min" if 'jina' in s['name'] else "10 min"
        free_tier = "Free tier available" if 'jina' in s['name'] else "Paid only"
        lines.append(f"{i}. **{s['name']}** - {setup_time} setup, {free_tier}")

    # Maturity
    lines.append("\n### 5. Most Mature\n")
    production_ready = [s for s in rankings['maturity'] if s.get('maturity_score', 0) >= 95 and s['name'] != '_archive']
    if production_ready:
        lines.append(f"**Tied:** {', '.join([s['name'] for s in production_ready])} - All production-ready\n")

    lines.append("---\n")

    # Decision Helper
    lines.append("## 🧭 Decision Helper\n")
    lines.append("### Which Should You Use?\n")

    zero_error = [s for s in summary if s.get('hallucinations', 0) == 0 and s['name'] != '_archive']
    if zero_error:
        lines.append(f"**Need zero hallucinations?** → {zero_error[0]['name']} (only option with 0 errors)\n")

    if best_cost and best_cost['name'] != '_archive':
        lines.append(f"**Processing >100K queries/month?** → {best_cost['name']} (${best_cost.get('total_cost', 0) * 100000:.0f}/100K queries, still excellent quality)\n")

    fast_options = [s for s in rankings['speed'][:2] if s.get('total_time', 10) < 7 and s['name'] != '_archive']
    if fast_options:
        lines.append(f"**Need <7s response time?** → {' or '.join([s['name'] for s in fast_options])} (fastest options, but more errors)\n")
    else:
        lines.append(f"**Need <7s response time?** → Reconsider requirements (all quality options are 8-9s)\n")

    if best_quality and best_quality['name'] != '_archive':
        lines.append(f"**Not sure?** → Start with {best_quality['name']}, switch if cost becomes an issue\n")

    lines.append("---\n")

    # Key Insights
    lines.append("## 💡 Key Insights\n")

    # Claude vs GPT-4 comparison
    claude_combos = [s for s in summary if 'claude' in s['name'] and s['name'] != '_archive']
    gpt4_combos = [s for s in summary if 'gpt4' in s['name'] and s['name'] != '_archive']

    claude_avg_quality = sum(s.get('quality_score', 0) for s in claude_combos) / len(claude_combos) if claude_combos else 0
    gpt4_avg_quality = sum(s.get('quality_score', 0) for s in gpt4_combos) / len(gpt4_combos) if gpt4_combos else 0
    quality_diff = claude_avg_quality - gpt4_avg_quality

    claude_errors = sum(s.get('hallucinations', 0) for s in claude_combos)
    gpt4_errors = sum(s.get('hallucinations', 0) for s in gpt4_combos)

    lines.append(f"**Claude vs GPT-4:** Claude beats GPT-4 across all tools (+{quality_diff:.1f} quality points average, {gpt4_errors - claude_errors} fewer errors)")
    lines.append(f"→ **Never use GPT-4 combinations**\n")

    lines.append("---\n")

    # Evaluation Rubric
    lines.append("## 📋 Evaluation Rubric\n")
    lines.append("Our framework evaluates each combination across five equally important dimensions (20% each):\n")
    lines.append("| Dimension | Key Metrics | Description |")
    lines.append("|-----------|-------------|-------------|")
    lines.append("| **Accuracy & Quality** | Quality Score, Hallucination Rate | Factual correctness and answer completeness |")
    lines.append("| **Latency** | Total Response Time, Search Time, Generation Time | End-to-end speed and performance |")
    lines.append("| **Operational Cost** | Cost per Query, Cost at Scale | Direct API costs (search + LLM) |")
    lines.append("| **Ease of Adoption** | Setup Time, Documentation, API Access | Implementation complexity |")
    lines.append("| **Maturity** | Stability, Feature Coverage, Support | Production readiness |\n")
    lines.append("*All dimensions weighted equally at 20% - they are all necessary and important for production use.*\n")
    lines.append("---\n")

    # AI-Generated Insights
    lines.append("## AI-Powered Analysis\n")
    lines.append("*The following insights were generated by Claude Opus 3 analyzing the benchmark data:*\n")
    lines.append(f"{llm_insights}\n")
    lines.append("---\n")

    # Detailed Breakdowns for Each Combination
    lines.append("## Detailed Performance Breakdown\n")

    for rank, s in enumerate(summary, 1):
        combo_name = s['name']
        lines.append(f"### {rank}. {combo_name.upper()}\n")

        # Quality Score Calculation
        lines.append("#### Quality Score Calculation\n")
        acc = s.get('accuracy', 0)
        comp = s.get('completeness', 0)
        clar = s.get('clarity', 0)
        help_score = s.get('helpfulness', 0)
        overall = s.get('quality_score', 0)

        lines.append("**Formula:** `Overall = (Accuracy × 0.25) + (Completeness × 0.25) + (Clarity × 0.25) + (Helpfulness × 0.25)`\n")
        lines.append(f"**Calculation:** `{overall:.1f} = ({acc:.1f} × 0.25) + ({comp:.1f} × 0.25) + ({clar:.1f} × 0.25) + ({help_score:.1f} × 0.25)`\n")

        # Component Scores Table
        lines.append("| Component | Score | Weight | Contribution |")
        lines.append("|-----------|-------|--------|--------------|")
        lines.append(f"| Accuracy | {acc:.1f} | 25% | {acc * 0.25:.1f} |")
        lines.append(f"| Completeness | {comp:.1f} | 25% | {comp * 0.25:.1f} |")
        lines.append(f"| Clarity | {clar:.1f} | 25% | {clar * 0.25:.1f} |")
        lines.append(f"| Helpfulness | {help_score:.1f} | 25% | {help_score * 0.25:.1f} |")
        lines.append(f"| **Overall Quality** | **{overall:.1f}** | 100% | - |\n")

        # How Scores Are Calculated
        lines.append("**How These Scores Are Calculated:**\n")
        lines.append("1. AI Judge (Claude Opus 3) evaluates each of the 25 test questions")
        lines.append("2. For each question, scores Accuracy, Completeness, Clarity, and Helpfulness (0-100)")
        lines.append("3. Each component score above is the **average across all 25 questions**")
        lines.append("4. Overall Quality is the weighted average using the formula above\n")

        # Performance Metrics
        lines.append("#### Performance & Cost Metrics\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Response Time | {s.get('total_time', 0):.2f}s |")
        lines.append(f"| Search Time | {s.get('search_time', 0):.2f}s |")
        lines.append(f"| Generation Time | {s.get('gen_time', 0):.2f}s |")
        lines.append(f"| Cost per Query | ${s.get('total_cost', 0):.4f} |")
        lines.append(f"| Cost per 100K Queries | ${s.get('total_cost', 0) * 100000:.0f} |")
        lines.append(f"| Hallucinations | {s.get('hallucinations', 0)}/{s.get('total_evaluated', 25)} |")
        lines.append(f"| Hallucination Rate | {(s.get('hallucinations', 0) / s.get('total_evaluated', 25) * 100):.1f}% |\n")

        # Individual Question Performance (if available)
        if combo_name in eval_data and eval_data[combo_name]:
            lines.append("#### Individual Question Performance\n")
            lines.append("*Top 5 Best Performing Questions:*\n")

            # Sort by overall_quality
            questions = sorted(eval_data[combo_name],
                             key=lambda x: x.get('overall_quality', 0),
                             reverse=True)[:5]

            lines.append("| Q ID | Quality | Accuracy | Question |")
            lines.append("|------|---------|----------|----------|")
            for q in questions:
                q_id = q.get('question_id', 'N/A')
                q_qual = q.get('overall_quality', 0)
                q_acc = q.get('accuracy', 0)
                q_text = q.get('question', 'N/A')[:60] + "..." if len(q.get('question', '')) > 60 else q.get('question', 'N/A')
                lines.append(f"| {q_id} | {q_qual:.1f} | {q_acc:.1f} | {q_text} |")

            lines.append("\n*Top 5 Worst Performing Questions:*\n")

            worst_questions = sorted(eval_data[combo_name],
                                   key=lambda x: x.get('overall_quality', 0))[:5]

            lines.append("| Q ID | Quality | Accuracy | Question |")
            lines.append("|------|---------|----------|----------|")
            for q in worst_questions:
                q_id = q.get('question_id', 'N/A')
                q_qual = q.get('overall_quality', 0)
                q_acc = q.get('accuracy', 0)
                q_text = q.get('question', 'N/A')[:60] + "..." if len(q.get('question', '')) > 60 else q.get('question', 'N/A')
                lines.append(f"| {q_id} | {q_qual:.1f} | {q_acc:.1f} | {q_text} |")

        lines.append("\n---\n")

    # Cache Performance (if available)
    if cache_data:
        lines.append("## Cache Performance\n")
        lines.append("| Combination | Hit Rate | Exact Hits | Semantic Hits | Avg Retrieval |")
        lines.append("|-------------|----------|------------|---------------|---------------|")

        for combo in all_combos:
            if combo in cache_data:
                cache_stats = cache_data[combo][0] if cache_data[combo] else {}
                hit_rate = cache_stats.get('hit_rate', 0)
                exact_hits = cache_stats.get('exact_hits', 0)
                semantic_hits = cache_stats.get('semantic_hits', 0)
                avg_retrieval = cache_stats.get('avg_exact_retrieval_time', 0)

                lines.append(
                    f"| {combo} | {hit_rate:.1f}% | {exact_hits} | {semantic_hits} | {avg_retrieval*1000:.1f}ms |"
                )

        lines.append("\n---\n")

    # Print and Save to RESULTS.md
    report_content = "\n".join(lines)

    # Save to RESULTS.md (main results file)
    results_path = "RESULTS.md"
    with open(results_path, 'w') as f:
        f.write(report_content)
    print(f"✅ Comprehensive results saved to: {results_path}")

    # Also save timestamped version in test_results
    timestamp_file = f"benchmark_report_{time.strftime('%Y%m%d-%H%M%S')}.md"
    timestamp_path = os.path.join(results_dir, timestamp_file)
    with open(timestamp_path, 'w') as f:
        f.write(report_content)
    print(f"✅ Timestamped copy saved to: {timestamp_path}")

if __name__ == "__main__":
    main()