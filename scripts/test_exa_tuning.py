#!/usr/bin/env python3
"""
Standalone Exa.ai Evaluation & Tuning Script

This script helps test different Exa.ai configurations to optimize results.
Use this to experiment with settings and share findings with the Exa.ai team.

Usage:
    python3 scripts/test_exa_tuning.py

    # Or test specific configuration
    python3 scripts/test_exa_tuning.py --config neural --results 10
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from exa_py import Exa
from api.app.llm.claude_llm import ClaudeLLM

# Test questions about BizGenie
TEST_QUESTIONS = [
    "What core services does BizGenie provide to businesses?",
    "How does BizGenie differentiate itself from other AI automation tools?",
    "What is the primary mission or goal of BizGenie?",
    "Does BizGenie offer features for managing appointments or bookings?",
    "Can BizGenie agents be customized to match a specific brand voice or script?",
]

# Configurations to test
EXA_CONFIGS = {
    "neural_basic": {
        "type": "neural",
        "num_results": 5,
        "include_domains": ["bizgenieai.com"],
        "text": True,
        "description": "Basic neural search limited to bizgenieai.com"
    },
    "neural_extended": {
        "type": "neural",
        "num_results": 10,
        "include_domains": ["bizgenieai.com"],
        "text": True,
        "description": "Extended neural search with more results"
    },
    "keyword_basic": {
        "type": "keyword",
        "num_results": 5,
        "include_domains": ["bizgenieai.com"],
        "text": True,
        "description": "Keyword-based search"
    },
    "auto_search": {
        "type": "auto",
        "num_results": 5,
        "include_domains": ["bizgenieai.com"],
        "text": True,
        "description": "Auto mode - Exa decides search type"
    },
    "neural_no_domain": {
        "type": "neural",
        "num_results": 5,
        "text": True,
        "start_published_date": "2024-01-01",
        "description": "Neural search without domain restriction (might find more)"
    },
}


def test_exa_search(exa_client, question, config):
    """Test a single search with given configuration"""
    print(f"\n  Testing: {question[:60]}...")

    start_time = time.time()
    try:
        # Prepare search parameters
        search_params = {
            "query": question,
            "num_results": config.get("num_results", 5),
            "type": config.get("type", "neural"),
            "text": config.get("text", True)
        }

        # Add optional parameters
        if config.get("include_domains"):
            search_params["include_domains"] = config["include_domains"]
        if config.get("start_published_date"):
            search_params["start_published_date"] = config["start_published_date"]

        # Execute search
        response = exa_client.search_and_contents(**search_params)

        search_time = time.time() - start_time
        results = response.results

        # Extract info
        result_data = {
            "question": question,
            "num_results": len(results),
            "search_time": search_time,
            "success": True,
            "results": []
        }

        for res in results:
            result_data["results"].append({
                "title": res.title or "No title",
                "url": res.url,
                "text_length": len(res.text) if res.text else 0,
                "text_preview": res.text[:200] + "..." if res.text and len(res.text) > 200 else res.text or ""
            })

        print(f"    ✅ Found {len(results)} results in {search_time:.2f}s")
        return result_data

    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        return {
            "question": question,
            "success": False,
            "error": str(e),
            "search_time": time.time() - start_time
        }


def generate_answer(llm, question, search_content):
    """Generate answer using LLM"""
    try:
        messages = [{"role": "user", "content": question}]
        system_prompt = "You are a helpful assistant. Answer the question based on the provided context."

        response = llm.generate(messages, search_content, system_prompt)
        return response.content, response.gen_time
    except Exception as e:
        return f"Error generating answer: {e}", 0


def main():
    parser = argparse.ArgumentParser(description="Test and tune Exa.ai search configurations")
    parser.add_argument("--config", choices=list(EXA_CONFIGS.keys()) + ["all"],
                       default="all", help="Configuration to test (default: all)")
    parser.add_argument("--questions", type=int, default=5,
                       help="Number of questions to test (default: 5)")
    parser.add_argument("--generate-answers", action="store_true",
                       help="Also generate and show answers using Claude")
    args = parser.parse_args()

    # Initialize Exa client
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        print("❌ Error: EXA_API_KEY environment variable not set")
        sys.exit(1)

    exa_client = Exa(api_key=api_key)

    # Initialize Claude if needed
    llm = None
    if args.generate_answers:
        llm = ClaudeLLM({
            "api_key_env": "ANTHROPIC_API_KEY",
            "config": {"model": "claude-3-opus-20240229"}
        })

    # Select configurations to test
    configs_to_test = {args.config: EXA_CONFIGS[args.config]} if args.config != "all" else EXA_CONFIGS

    # Select questions
    questions = TEST_QUESTIONS[:args.questions]

    print("=" * 80)
    print("🔬 EXA.AI TUNING & EVALUATION")
    print("=" * 80)
    print(f"\nTarget Site: bizgenieai.com")
    print(f"Questions: {len(questions)}")
    print(f"Configurations: {len(configs_to_test)}")
    print(f"Generate Answers: {'Yes' if args.generate_answers else 'No'}")
    print()

    # Results storage
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "configurations_tested": len(configs_to_test),
        "questions_tested": len(questions),
        "results": {}
    }

    # Test each configuration
    for config_name, config in configs_to_test.items():
        print(f"\n{'='*80}")
        print(f"📋 TESTING: {config_name.upper()}")
        print(f"Description: {config['description']}")
        print(f"Settings: type={config.get('type')}, num_results={config.get('num_results')}, domains={config.get('include_domains', 'None')}")
        print(f"{'='*80}")

        config_results = {
            "config": config,
            "questions": []
        }

        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}]", end=" ")
            result = test_exa_search(exa_client, question, config)

            # Generate answer if requested
            if args.generate_answers and result.get("success"):
                print(f"    🤖 Generating answer...")
                # Combine all text from results
                context = "\n\n".join([r["text_preview"] for r in result["results"] if r.get("text_preview")])
                answer, gen_time = generate_answer(llm, question, context)
                result["answer"] = answer
                result["gen_time"] = gen_time
                print(f"    ✅ Answer generated in {gen_time:.2f}s")

            config_results["questions"].append(result)

        all_results["results"][config_name] = config_results

        # Summary for this config
        successful = sum(1 for r in config_results["questions"] if r.get("success"))
        total_results = sum(r.get("num_results", 0) for r in config_results["questions"] if r.get("success"))
        avg_time = sum(r.get("search_time", 0) for r in config_results["questions"]) / len(questions)

        print(f"\n📊 Summary for {config_name}:")
        print(f"   Success Rate: {successful}/{len(questions)} ({successful/len(questions)*100:.1f}%)")
        print(f"   Total Results Found: {total_results}")
        print(f"   Avg Search Time: {avg_time:.2f}s")

    # Save results
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = "test_results/exa_tuning"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/exa_test_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*80}")
    print(f"✅ EVALUATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nResults saved to: {output_file}")

    # Generate comparison report
    generate_comparison_report(all_results, output_dir, timestamp)

    print(f"\n💡 Next Steps:")
    print(f"   1. Review the results in: {output_file}")
    print(f"   2. Check the comparison report: {output_dir}/exa_report_{timestamp}.md")
    print(f"   3. Share findings with Exa.ai team if results aren't satisfactory")
    print(f"   4. Try adjusting configurations in this script and re-run")


def generate_comparison_report(results, output_dir, timestamp):
    """Generate a markdown report comparing configurations"""
    report_file = f"{output_dir}/exa_report_{timestamp}.md"

    lines = []
    lines.append("# Exa.ai Configuration Testing Report\n")
    lines.append(f"**Generated:** {results['timestamp']}")
    lines.append(f"**Configurations Tested:** {results['configurations_tested']}")
    lines.append(f"**Questions Tested:** {results['questions_tested']}\n")
    lines.append("---\n")

    # Overall Comparison
    lines.append("## Configuration Comparison\n")
    lines.append("| Configuration | Success Rate | Avg Results | Avg Time | Total Results |")
    lines.append("|---------------|--------------|-------------|----------|---------------|")

    for config_name, config_data in results["results"].items():
        questions = config_data["questions"]
        successful = sum(1 for q in questions if q.get("success"))
        total_q = len(questions)
        success_rate = f"{successful}/{total_q} ({successful/total_q*100:.0f}%)"

        avg_results = sum(q.get("num_results", 0) for q in questions if q.get("success")) / max(successful, 1)
        avg_time = sum(q.get("search_time", 0) for q in questions) / total_q
        total_results = sum(q.get("num_results", 0) for q in questions if q.get("success"))

        lines.append(f"| {config_name} | {success_rate} | {avg_results:.1f} | {avg_time:.2f}s | {total_results} |")

    lines.append("\n---\n")

    # Detailed Results
    lines.append("## Detailed Results by Configuration\n")

    for config_name, config_data in results["results"].items():
        lines.append(f"### {config_name}\n")
        lines.append(f"**Description:** {config_data['config']['description']}\n")
        lines.append(f"**Settings:**")
        lines.append(f"- Type: {config_data['config'].get('type')}")
        lines.append(f"- Num Results: {config_data['config'].get('num_results')}")
        lines.append(f"- Domains: {config_data['config'].get('include_domains', 'None')}\n")

        for i, question_result in enumerate(config_data["questions"], 1):
            lines.append(f"#### Question {i}: {question_result['question']}\n")

            if question_result.get("success"):
                lines.append(f"- **Status:** ✅ Success")
                lines.append(f"- **Results Found:** {question_result['num_results']}")
                lines.append(f"- **Search Time:** {question_result['search_time']:.2f}s")

                if question_result.get("results"):
                    lines.append(f"- **Top Result:** {question_result['results'][0]['title']}")
                    lines.append(f"- **URL:** {question_result['results'][0]['url']}")
                    lines.append(f"- **Content Preview:** {question_result['results'][0]['text_preview'][:150]}...")

                if question_result.get("answer"):
                    lines.append(f"\n**Generated Answer:**")
                    lines.append(f"{question_result['answer'][:300]}...")
            else:
                lines.append(f"- **Status:** ❌ Failed")
                lines.append(f"- **Error:** {question_result.get('error')}")

            lines.append("")

        lines.append("---\n")

    # Recommendations
    lines.append("## Recommendations\n")
    lines.append("Based on the test results:\n")

    # Find best config
    best_config = None
    best_score = 0

    for config_name, config_data in results["results"].items():
        questions = config_data["questions"]
        successful = sum(1 for q in questions if q.get("success"))
        total_results = sum(q.get("num_results", 0) for q in questions if q.get("success"))
        score = successful * 100 + total_results

        if score > best_score:
            best_score = score
            best_config = config_name

    if best_config:
        lines.append(f"1. **Best Configuration:** {best_config}")
        lines.append(f"2. **Why:** Highest success rate and result count")

    lines.append(f"\n### Issues to Report to Exa.ai Team:\n")
    lines.append("- [ ] Site indexing status for bizgenieai.com")
    lines.append("- [ ] Best configuration for single-domain searches")
    lines.append("- [ ] Expected result count for new/small sites")
    lines.append("- [ ] Alternative approaches if site not indexed\n")

    # Write report
    with open(report_file, 'w') as f:
        f.write("\n".join(lines))

    print(f"   Report generated: {report_file}")


if __name__ == "__main__":
    main()
