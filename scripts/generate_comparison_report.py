"""
Generate comprehensive comparison report from evaluation results.
Shows which MCP tool + LLM combination performs best across all metrics.
"""
import glob
import json
import os
import time

def load_all_results(results_dir: str) -> dict:
    """Load both evaluation and results files for each combination"""
    combinations = {}

    # Find all subdirectories (jina_claude, tavily_gpt4, etc.)
    subdirs = [d for d in os.listdir(results_dir)
               if os.path.isdir(os.path.join(results_dir, d))]

    for combo_name in subdirs:
        combo_path = os.path.join(results_dir, combo_name)

        # Load latest eval file
        eval_files = sorted(glob.glob(f"{combo_path}/eval_*.json"), reverse=True)
        # Load latest results file
        results_files = sorted(glob.glob(f"{combo_path}/results_*.json"), reverse=True)

        if eval_files and results_files:
            try:
                with open(eval_files[0], 'r') as f:
                    eval_data = json.load(f)
                with open(results_files[0], 'r') as f:
                    results_data = json.load(f)

                combinations[combo_name] = {
                    'evaluations': eval_data,
                    'results': results_data
                }
            except Exception as e:
                print(f"Warning: Could not load {combo_name}: {e}")

    return combinations

def analyze_combination(combo_name: str, evaluations: list, results: list) -> dict:
    """Analyze complete metrics for a combination"""
    if not evaluations or not results:
        return {}

    # Merge eval and results by question_id
    merged = {}
    for e in evaluations:
        qid = e.get('question_id')
        merged[qid] = {'eval': e}

    for r in results:
        qid = r.get('question_id')
        if qid in merged:
            merged[qid]['result'] = r

    # Calculate quality metrics
    quality_scores = []
    accuracy_scores = []
    completeness_scores = []
    clarity_scores = []
    helpfulness_scores = []
    hallucinations = 0

    for qid, data in merged.items():
        if 'eval' in data:
            e = data['eval']
            quality_scores.append(e.get('overall_quality', 0))
            accuracy_scores.append(e.get('accuracy', 0))
            completeness_scores.append(e.get('completeness', 0))
            clarity_scores.append(e.get('clarity', 0))
            helpfulness_scores.append(e.get('helpfulness', 0))

            if e.get('verdict') == 'HALLUCINATION' or e.get('hallucination', False):
                hallucinations += 1

    # Calculate performance metrics
    search_times = []
    gen_times = []
    total_times = []
    tokens_used = []

    for qid, data in merged.items():
        if 'result' in data:
            r = data['result']
            metrics = r.get('metrics', {})
            search_times.append(metrics.get('search_time', 0))
            gen_times.append(metrics.get('gen_time', 0))
            total_times.append(metrics.get('total_time', 0))
            tokens_used.append(metrics.get('tokens', 0))

    # Calculate cost estimates (rough estimates based on typical pricing)
    # Jina: ~$0.002/search, Tavily: ~$0.012/search
    # Claude: ~$3/$15 per 1M tokens (input/output), GPT-4: ~$5/$15 per 1M tokens

    is_jina = 'jina' in combo_name.lower()
    is_claude = 'claude' in combo_name.lower()

    avg_search_cost = 0.002 if is_jina else 0.012
    avg_gen_cost_per_token = (3 + 15) / 2000000 if is_claude else (5 + 15) / 2000000  # Rough average

    avg_tokens = sum(tokens_used) / len(tokens_used) if tokens_used else 0
    avg_gen_cost = avg_tokens * avg_gen_cost_per_token
    avg_total_cost = avg_search_cost + avg_gen_cost

    # Quality distribution
    excellent = sum(1 for s in quality_scores if s >= 80)
    good = sum(1 for s in quality_scores if 60 <= s < 80)
    fair = sum(1 for s in quality_scores if 40 <= s < 60)
    poor = sum(1 for s in quality_scores if s < 40)

    # Top/bottom questions
    q_scores = [(qid, merged[qid]['eval'].get('overall_quality', 0))
                for qid in merged if 'eval' in merged[qid]]
    q_scores.sort(key=lambda x: x[1], reverse=True)
    top_questions = q_scores[:3] if len(q_scores) >= 3 else q_scores
    bottom_questions = q_scores[-3:] if len(q_scores) >= 3 else []

    return {
        'name': combo_name,
        'total_questions': len(merged),

        # Quality metrics
        'avg_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
        'avg_accuracy': sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0,
        'avg_completeness': sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0,
        'avg_clarity': sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0,
        'avg_helpfulness': sum(helpfulness_scores) / len(helpfulness_scores) if helpfulness_scores else 0,
        'hallucinations': hallucinations,

        # Performance metrics
        'avg_search_time': sum(search_times) / len(search_times) if search_times else 0,
        'avg_gen_time': sum(gen_times) / len(gen_times) if gen_times else 0,
        'avg_total_time': sum(total_times) / len(total_times) if total_times else 0,
        'min_total_time': min(total_times) if total_times else 0,
        'max_total_time': max(total_times) if total_times else 0,

        # Cost metrics
        'avg_search_cost': avg_search_cost,
        'avg_gen_cost': avg_gen_cost,
        'avg_total_cost': avg_total_cost,
        'total_cost_25q': avg_total_cost * len(merged),

        # Reliability metrics
        'avg_tokens': avg_tokens,
        'excellent_count': excellent,
        'good_count': good,
        'fair_count': fair,
        'poor_count': poor,
        'top_questions': top_questions,
        'bottom_questions': bottom_questions,
    }

def main():
    results_dir = "test_results"

    if not os.path.exists(results_dir):
        print(f"❌ Results directory not found: {results_dir}")
        return

    print(f"📖 Loading evaluation results from {results_dir}...")
    combinations = load_all_results(results_dir)

    if not combinations:
        print("❌ No evaluation results found.")
        return

    print(f"   Found {len(combinations)} combinations\n")

    # Analyze each combination
    summary = []
    for combo_name, data in combinations.items():
        print(f"   Analyzing {combo_name}...")
        metrics = analyze_combination(
            combo_name,
            data['evaluations'],
            data['results']
        )
        if metrics:
            summary.append(metrics)

    # Sort by quality score
    summary.sort(key=lambda x: x['avg_quality'], reverse=True)

    # Generate Report
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    report_lines = []

    report_lines.append(f"# MCP Tool + LLM Comparison Report\n")
    report_lines.append(f"*Generated: {timestamp}*\n\n")

    # Overall Rankings
    report_lines.append("## 🏆 Overall Rankings\n\n")
    report_lines.append("| Rank | Combination | Quality | Total Cost | Total Time | Search Time | Gen Time | Halluc. |\n")
    report_lines.append("|------|-------------|---------|------------|------------|-------------|----------|---------|")

    for i, combo in enumerate(summary, 1):
        report_lines.append(
            f"\n| {i} | **{combo['name']}** | "
            f"{combo['avg_quality']:.1f} | "
            f"${combo['avg_total_cost']:.4f} | "
            f"{combo['avg_total_time']:.2f}s | "
            f"{combo['avg_search_time']:.2f}s | "
            f"{combo['avg_gen_time']:.2f}s | "
            f"{combo['hallucinations']} |"
        )

    # Tool Architecture Analysis
    report_lines.append("\n\n## 🔍 Tool Architecture Analysis\n")

    # Categorize tools
    jina_combos = [c for c in summary if 'jina' in c['name'].lower()]
    tavily_combos = [c for c in summary if 'tavily' in c['name'].lower()]

    report_lines.append("\n### MCP Tool Comparison: Search Engine vs Web Scraper\n\n")

    report_lines.append("**Jina AI Reader** = Web Scraper/Content Extractor\n")
    report_lines.append("- Extracts clean content from specific URLs\n")
    report_lines.append("- Converts HTML to structured markdown\n")
    report_lines.append("- Returns full page content from target domain\n")
    report_lines.append("- Best for: Deep single-site content extraction\n\n")

    report_lines.append("**Tavily AI Search** = AI-Powered Search Engine\n")
    report_lines.append("- Actively searches web for relevant content\n")
    report_lines.append("- Uses AI to rank and curate results\n")
    report_lines.append("- Returns multiple sources with relevance scores\n")
    report_lines.append("- Best for: Multi-source research, fresh data\n\n")

    # Performance reasoning
    if jina_combos and tavily_combos:
        avg_jina_quality = sum(c['avg_quality'] for c in jina_combos) / len(jina_combos)
        avg_tavily_quality = sum(c['avg_quality'] for c in tavily_combos) / len(tavily_combos)
        avg_jina_cost = sum(c['avg_total_cost'] for c in jina_combos) / len(jina_combos)
        avg_tavily_cost = sum(c['avg_total_cost'] for c in tavily_combos) / len(tavily_combos)
        avg_jina_time = sum(c['avg_search_time'] for c in jina_combos) / len(jina_combos)
        avg_tavily_time = sum(c['avg_search_time'] for c in tavily_combos) / len(tavily_combos)

        report_lines.append("### Why Performance Differs\n\n")

        # Quality reasoning
        if avg_jina_quality > avg_tavily_quality:
            diff = avg_jina_quality - avg_tavily_quality
            report_lines.append(f"**Quality: Jina {avg_jina_quality:.1f} vs Tavily {avg_tavily_quality:.1f} (+{diff:.1f})**\n")
            report_lines.append("- Domain-specific questions benefit from full page content extraction\n")
            report_lines.append("- Jina scrapes bizgenieai.com directly → complete, accurate information\n")
            report_lines.append("- Tavily returns web snippets → may miss context or return off-topic results\n")
            report_lines.append("- For known domains, scrapers > search engines for quality\n\n")
        else:
            diff = avg_tavily_quality - avg_jina_quality
            report_lines.append(f"**Quality: Tavily {avg_tavily_quality:.1f} vs Jina {avg_jina_quality:.1f} (+{diff:.1f})**\n")
            report_lines.append("- Multi-source questions benefit from search engine ranking\n")
            report_lines.append("- Tavily finds best sources across web → better coverage\n")
            report_lines.append("- For broad questions, search engines > scrapers\n\n")

        # Cost reasoning
        cost_diff = avg_tavily_cost - avg_jina_cost
        report_lines.append(f"**Cost: Jina ${avg_jina_cost:.4f} vs Tavily ${avg_tavily_cost:.4f} ({cost_diff/avg_jina_cost*100:.0f}% difference)**\n")
        report_lines.append(f"- Jina: ~$0.002/search (or free tier) - simple URL fetch\n")
        report_lines.append(f"- Tavily: ~$0.012/search - AI-powered web crawling and ranking\n")
        report_lines.append(f"- Tavily costs {cost_diff/avg_jina_cost:.1f}x more due to search infrastructure\n\n")

        # Speed reasoning
        if avg_tavily_time < avg_jina_time:
            diff = avg_jina_time - avg_tavily_time
            report_lines.append(f"**Speed: Tavily {avg_tavily_time:.2f}s vs Jina {avg_jina_time:.2f}s (-{diff:.2f}s)**\n")
            report_lines.append("- Search engines cache and pre-index content → faster retrieval\n")
            report_lines.append("- Web scrapers fetch+parse HTML in real-time → slower\n\n")
        else:
            diff = avg_tavily_time - avg_jina_time
            report_lines.append(f"**Speed: Jina {avg_jina_time:.2f}s vs Tavily {avg_tavily_time:.2f}s (-{diff:.2f}s)**\n")
            report_lines.append("- Both tools are similarly fast for this use case\n\n")

    # LLM comparison
    claude_combos = [c for c in summary if 'claude' in c['name'].lower()]
    gpt4_combos = [c for c in summary if 'gpt4' in c['name'].lower()]

    if claude_combos and gpt4_combos:
        avg_claude_quality = sum(c['avg_quality'] for c in claude_combos) / len(claude_combos)
        avg_gpt4_quality = sum(c['avg_quality'] for c in gpt4_combos) / len(gpt4_combos)
        avg_claude_gen_time = sum(c['avg_gen_time'] for c in claude_combos) / len(claude_combos)
        avg_gpt4_gen_time = sum(c['avg_gen_time'] for c in gpt4_combos) / len(gpt4_combos)

        report_lines.append("### LLM Comparison: Claude vs GPT-4\n\n")

        if avg_claude_quality > avg_gpt4_quality:
            diff = avg_claude_quality - avg_gpt4_quality
            report_lines.append(f"**Quality: Claude {avg_claude_quality:.1f} vs GPT-4 {avg_gpt4_quality:.1f} (+{diff:.1f})**\n")
            report_lines.append("- Claude shows better reasoning and fewer hallucinations\n")
        elif avg_gpt4_quality > avg_claude_quality:
            diff = avg_gpt4_quality - avg_claude_quality
            report_lines.append(f"**Quality: GPT-4 {avg_gpt4_quality:.1f} vs Claude {avg_claude_quality:.1f} (+{diff:.1f})**\n")
            report_lines.append("- GPT-4 shows better performance for this use case\n")

        if avg_gpt4_gen_time < avg_claude_gen_time:
            diff = avg_claude_gen_time - avg_gpt4_gen_time
            report_lines.append(f"**Speed: GPT-4 {avg_gpt4_gen_time:.2f}s vs Claude {avg_claude_gen_time:.2f}s (-{diff:.2f}s faster)**\n")
            report_lines.append("- GPT-4 generally has faster inference time\n\n")
        else:
            diff = avg_gpt4_gen_time - avg_claude_gen_time
            report_lines.append(f"**Speed: Claude {avg_claude_gen_time:.2f}s vs GPT-4 {avg_gpt4_gen_time:.2f}s (-{diff:.2f}s faster)**\n\n")

    # Detailed Metrics
    report_lines.append("\n## 📊 Detailed Metrics\n")

    for combo in summary:
        report_lines.append(f"\n### {combo['name'].upper()}\n")

        report_lines.append(f"\n**Quality Breakdown:**\n")
        report_lines.append(f"- Average Overall Quality: {combo['avg_quality']:.1f}/100\n")
        report_lines.append(f"- Average Accuracy: {combo['avg_accuracy']:.1f}/100\n")
        report_lines.append(f"- Average Completeness: {combo['avg_completeness']:.1f}/100\n")
        report_lines.append(f"- Average Clarity: {combo['avg_clarity']:.1f}/100\n")
        report_lines.append(f"- Average Helpfulness: {combo['avg_helpfulness']:.1f}/100\n")

        report_lines.append(f"\n**Performance:**\n")
        report_lines.append(f"- Avg Search Latency: {combo['avg_search_time']:.2f}s\n")
        report_lines.append(f"- Avg Generation Latency: {combo['avg_gen_time']:.2f}s\n")
        report_lines.append(f"- Avg Total Latency: {combo['avg_total_time']:.2f}s\n")
        report_lines.append(f"- Fastest query: {combo['min_total_time']:.2f}s\n")
        report_lines.append(f"- Slowest query: {combo['max_total_time']:.2f}s\n")

        report_lines.append(f"\n**Cost:**\n")
        report_lines.append(f"- Avg Search Cost: ${combo['avg_search_cost']:.4f}/query\n")
        report_lines.append(f"- Avg Generation Cost: ${combo['avg_gen_cost']:.4f}/query\n")
        report_lines.append(f"- Avg Total Cost: ${combo['avg_total_cost']:.4f}/query\n")
        report_lines.append(f"- Total for {combo['total_questions']} queries: ${combo['total_cost_25q']:.2f}\n")

        report_lines.append(f"\n**Reliability:**\n")
        report_lines.append(f"- Hallucinations: {combo['hallucinations']}/{combo['total_questions']} ")
        report_lines.append(f"({'✅ EXCELLENT' if combo['hallucinations'] == 0 else '⚠️ WARNING' if combo['hallucinations'] <= 2 else '❌ HIGH'})\n")
        report_lines.append(f"- Avg tokens used: {combo['avg_tokens']:.0f}/query\n")

        report_lines.append(f"\n**Quality Distribution:**\n")
        report_lines.append(f"- Excellent (80-100): {combo['excellent_count']} questions\n")
        report_lines.append(f"- Good (60-79): {combo['good_count']} questions\n")
        report_lines.append(f"- Fair (40-59): {combo['fair_count']} questions\n")
        report_lines.append(f"- Poor (0-39): {combo['poor_count']} questions\n")

        if combo['top_questions']:
            top_str = ", ".join([f"{q[0]} ({q[1]:.0f})" for q in combo['top_questions']])
            report_lines.append(f"\n**Top scoring questions:** {top_str}\n")

        if combo['bottom_questions']:
            bottom_str = ", ".join([f"{q[0]} ({q[1]:.0f})" for q in combo['bottom_questions']])
            report_lines.append(f"**Low scoring questions:** {bottom_str}\n")

    # Comparative Analysis
    report_lines.append("\n## 📈 Comparative Analysis\n")

    report_lines.append("\n### Quality Comparison\n")
    best_quality = max(summary, key=lambda x: x['avg_quality'])
    best_accuracy = max(summary, key=lambda x: x['avg_accuracy'])
    best_completeness = max(summary, key=lambda x: x['avg_completeness'])
    best_clarity = max(summary, key=lambda x: x['avg_clarity'])
    report_lines.append(f"- Highest quality: **{best_quality['name']}** ({best_quality['avg_quality']:.1f})\n")
    report_lines.append(f"- Most accurate: **{best_accuracy['name']}** ({best_accuracy['avg_accuracy']:.1f})\n")
    report_lines.append(f"- Most complete: **{best_completeness['name']}** ({best_completeness['avg_completeness']:.1f})\n")
    report_lines.append(f"- Clearest answers: **{best_clarity['name']}** ({best_clarity['avg_clarity']:.1f})\n")

    report_lines.append("\n### Speed Comparison\n")
    fastest_search = min(summary, key=lambda x: x['avg_search_time'])
    fastest_gen = min(summary, key=lambda x: x['avg_gen_time'])
    fastest_total = min(summary, key=lambda x: x['avg_total_time'])
    report_lines.append(f"- Fastest search: **{fastest_search['name']}** ({fastest_search['avg_search_time']:.2f}s)\n")
    report_lines.append(f"- Fastest generation: **{fastest_gen['name']}** ({fastest_gen['avg_gen_time']:.2f}s)\n")
    report_lines.append(f"- Fastest total: **{fastest_total['name']}** ({fastest_total['avg_total_time']:.2f}s)\n")

    report_lines.append("\n### Cost Comparison\n")
    cheapest_search = min(summary, key=lambda x: x['avg_search_cost'])
    cheapest_gen = min(summary, key=lambda x: x['avg_gen_cost'])
    cheapest_total = min(summary, key=lambda x: x['avg_total_cost'])
    report_lines.append(f"- Cheapest search: **{cheapest_search['name']}** (${cheapest_search['avg_search_cost']:.4f})\n")
    report_lines.append(f"- Cheapest generation: **{cheapest_gen['name']}** (${cheapest_gen['avg_gen_cost']:.4f})\n")
    report_lines.append(f"- Cheapest total: **{cheapest_total['name']}** (${cheapest_total['avg_total_cost']:.4f})\n")

    report_lines.append("\n### Reliability Comparison\n")
    zero_halluc = [c for c in summary if c['hallucinations'] == 0]
    if zero_halluc:
        report_lines.append(f"- Zero hallucinations: **{', '.join([c['name'] for c in zero_halluc])}**\n")
    most_reliable = min(summary, key=lambda x: x['hallucinations'])
    report_lines.append(f"- Most reliable: **{most_reliable['name']}** ({most_reliable['hallucinations']} hallucinations)\n")

    # Recommendations
    report_lines.append("\n## 🎯 Recommendations\n")

    best_overall = summary[0]
    report_lines.append(f"\n### 🏆 BEST OVERALL: {best_overall['name'].upper()}\n")
    report_lines.append(f"- Highest quality ({best_overall['avg_quality']:.1f}/100)\n")
    report_lines.append(f"- Hallucinations: {best_overall['hallucinations']}\n")
    report_lines.append(f"- Cost: ${best_overall['avg_total_cost']:.4f}/query\n")
    report_lines.append(f"- Speed: {best_overall['avg_total_time']:.2f}s/query\n")
    report_lines.append(f"- **Use when:** Quality and reliability matter most\n")

    if fastest_total['name'] != best_overall['name']:
        report_lines.append(f"\n### ⚡ BEST FOR SPEED: {fastest_total['name'].upper()}\n")
        report_lines.append(f"- Fastest total time ({fastest_total['avg_total_time']:.2f}s)\n")
        report_lines.append(f"- Quality: {fastest_total['avg_quality']:.1f}/100\n")
        report_lines.append(f"- **Use when:** Speed is critical, slight quality trade-off acceptable\n")

    if cheapest_total['name'] != best_overall['name']:
        report_lines.append(f"\n### 💰 BEST VALUE: {cheapest_total['name'].upper()}\n")
        report_lines.append(f"- Lowest cost (${cheapest_total['avg_total_cost']:.4f}/query)\n")
        report_lines.append(f"- Quality: {cheapest_total['avg_quality']:.1f}/100\n")
        report_lines.append(f"- **Use when:** Budget-conscious but need decent quality\n")

    report_lines.append("\n---\n")
    report_lines.append("*Report generated by BizGenie AI Evaluation Framework*\n")

    # Print and save
    report_content = "".join(report_lines)
    print("\n" + "="*60)
    print(report_content)
    print("="*60)

    filename = f"benchmark_report_{time.strftime('%Y%m%d-%H%M%S')}.md"
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w') as f:
        f.write(report_content)

    print(f"\n📄 Report saved to: {filepath}")

if __name__ == "__main__":
    main()
