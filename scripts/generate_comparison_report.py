"""
Generate comparison report from evaluation results
Shows which MCP tool + LLM combination performs best
"""
import glob
import json
import os
import time
from collections import defaultdict


def load_evaluation_results(results_dir: str) -> list:
    """Load all evaluation JSON files"""
    pattern = f"{results_dir}/*/eval_*.json"
    eval_files = glob.glob(pattern)

    all_results = []
    for filepath in eval_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                all_results.append({
                    "filepath": filepath,
                    "data": data
                })
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")

    return all_results


def analyze_combination(evaluations: list) -> dict:
    """Analyze evaluation results for metrics"""

    if not evaluations:
        return {}

    # Aggregate scores
    scores = [e.get("overall_quality", 0) for e in evaluations]
    verdicts = [e.get("verdict", "UNKNOWN") for e in evaluations]
    found_more = [e.get("found_more_than_baseline", False) for e in evaluations]
    
    baseline_has_info = [e.get("baseline_has_info", True) for e in evaluations]

    # Count verdicts
    verdict_counts = {}
    for v in verdicts:
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    # Separate questions by baseline info availability
    no_info_questions = [e for e in evaluations if e.get("baseline_has_info") is False]
    has_info_questions = [e for e in evaluations if e.get("baseline_has_info") is not False]

    return {
        "total_questions": len(evaluations),
        "avg_score": sum(scores) / len(scores) if scores else 0,

        # Search power metrics (no info questions)
        "no_info_count": len(no_info_questions),
        "found_more_count": sum(found_more),
        "found_more_pct": (sum(found_more) / len(no_info_questions) * 100) if no_info_questions else 0,

        # Quality metrics (has info questions)
        "has_info_count": len(has_info_questions),

        # Verdict breakdown
        "verdict_counts": verdict_counts,
        "hallucinations": verdict_counts.get("HALLUCINATION", 0),
        "better_than_baseline": verdict_counts.get("BETTER_THAN_BASELINE", 0),
        "matches_baseline": verdict_counts.get("MATCHES_BASELINE", 0),
        "tie_no_info": verdict_counts.get("TIE_NO_INFO", 0)
    }


def main():
    results_dir = "test_results"

    if not os.path.exists(results_dir):
        print(f"❌ Results directory not found: {results_dir}")
        return

    print(f"📖 Loading evaluation results from {results_dir}...")
    all_data = load_evaluation_results(results_dir)

    if not all_data:
        print("❌ No evaluation results found.")
        print(f"   Looking for pattern: {results_dir}/*/eval_*.json")
        return

    print(f"   Found {len(all_data)} evaluation files\n")

    # Group by combination
    combinations = {}
    for result in all_data:
        data = result["data"]
        filepath = result["filepath"]
        parts = filepath.split("/")
        
        if len(parts) >= 2:
            combo_name = parts[-2]
            if combo_name not in combinations:
                combinations[combo_name] = []
            combinations[combo_name].extend(data if isinstance(data, list) else [data])

    if not combinations:
        print("❌ Could not parse evaluation results")
        return

    # Analyze each combination
    summary = []
    for combo_name, evaluations in combinations.items():
        metrics = analyze_combination(evaluations)
        parts = combo_name.split("_")
        mcp_tool = parts[0] if len(parts) > 0 else "unknown"
        llm_model = parts[1] if len(parts) > 1 else "unknown"

        summary.append({
            "name": combo_name,
            "mcp": mcp_tool,
            "llm": llm_model,
            **metrics
        })

    summary.sort(key=lambda x: x["avg_score"], reverse=True)

    # Generate Report Content in Markdown
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    report_lines = []
    report_lines.append(f"# MCP Tool + LLM Comparison Report ({timestamp})\n")

    # Overall Rankings
    report_lines.append("## 📊 Overall Rankings\n")
    report_lines.append("| # | Combination | Score | Found More | Halluc. |\n")
    report_lines.append("|---|-------------|-------|------------|---------|\n")

    for i, combo in enumerate(summary, 1):
        found_more_str = f"{combo['found_more_count']}/{combo['no_info_count']}" if combo['no_info_count'] > 0 else "N/A"
        report_lines.append(f"| {i} | {combo['name']} | {combo['avg_score']:.1f} | {found_more_str} | {combo['hallucinations']} |\n")

    # Detailed Breakdown
    report_lines.append("\n## 📝 Detailed Breakdown\n")

    for combo in summary:
        report_lines.append(f"\n### {combo['name'].upper()}\n")
        report_lines.append(f"- **Average Score**: {combo['avg_score']:.1f}/100\n")
        report_lines.append(f"\n**Search Power (questions where baseline had NO info):**\n")
        report_lines.append(f"  - Total 'no info' questions: {combo['no_info_count']}\n")
        report_lines.append(f"  - Found MORE than baseline: **{combo['found_more_count']} ({combo['found_more_pct']:.1f}%)** 🎯\n")
        report_lines.append(f"  - Tied with baseline (both found no info): {combo['tie_no_info']}\n")

        report_lines.append(f"\n**Quality (questions where baseline HAD info):**\n")
        report_lines.append(f"  - Total 'has info' questions: {combo['has_info_count']}\n")
        report_lines.append(f"  - Better than baseline: {combo['better_than_baseline']}\n")
        report_lines.append(f"  - Matches baseline: {combo['matches_baseline']}\n")

        report_lines.append(f"\n**Reliability:**\n")
        report_lines.append(f"  - Hallucinations: **{combo['hallucinations']}** ({'⚠️ HIGH' if combo['hallucinations'] > 2 else '✅ LOW' })\n")

    # Recommendations
    report_lines.append("\n## ✨ Recommendations\n")

    if summary:
        best_overall = summary[0]
        report_lines.append(f"\n**🏆 BEST OVERALL: {best_overall['name'].upper()}**\n")
        report_lines.append(f"   - Score: {best_overall['avg_score']:.1f}/100\n")
        
        search_candidates = [s for s in summary if s['no_info_count'] > 0]
        if search_candidates:
            best_search = max(search_candidates, key=lambda x: x['found_more_pct'])
            if best_search['name'] != best_overall['name']:
                report_lines.append(f"\n**🔍 BEST SEARCH POWER: {best_search['name'].upper()}**\n")
                report_lines.append(f"   - Found more: {best_search['found_more_pct']:.1f}%\n")

        most_reliable = min(summary, key=lambda x: x['hallucinations'])
        if most_reliable['hallucinations'] < best_overall['hallucinations']:
            report_lines.append(f"\n**✅ MOST RELIABLE (Least Hallucinations): {most_reliable['name'].upper()}**\n")
            report_lines.append(f"   - Hallucinations: {most_reliable['hallucinations']}\n")
    else:
        report_lines.append("No benchmark data available to make recommendations.\n")
    
    report_lines.append("\n---\n")
    report_lines.append("Report generated by the BizGenie AI Evaluation Framework.\n")


    # Combine and Print
    report_content = "".join(report_lines)
    print(report_content)

    # Save to file
    filename = f"benchmark_report_{time.strftime('%Y%m%d-%H%M%S')}.md"
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w') as f:
        f.write(report_content)
    
    print(f"\n📄 Report saved to: {filepath}")

if __name__ == "__main__":
    main()