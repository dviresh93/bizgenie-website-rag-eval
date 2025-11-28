import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add api to path to import tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from api.app.tools.jina_tool import JinaTool
from api.app.tools.tavily_tool import TavilyTool
from api.app.llm.claude_llm import ClaudeLLM
from api.app.llm.gpt4_llm import GPT4LLM
from scripts.ai_judge import AIJudge

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Run RAG Evaluation")
    parser.add_argument("--mcp", required=True, choices=["jina", "tavily"], help="MCP Tool to test")
    parser.add_argument("--llm", required=True, choices=["claude", "gpt4"], help="LLM to test")
    parser.add_argument("--questions", default="config/test_suites/standard_questions.json")
    args = parser.parse_args()

    # Path adjustments - Absolute paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) # /workspace/ or /home/.../website-rag/ 
    
    questions_path = os.path.join(project_root, args.questions)
    
    # Initialize Tool
    print(f"Initializing {args.mcp}...")
    if args.mcp == "jina":
        mcp_tool = JinaTool({"api_key_env": "JINA_API_KEY"})
    else:
        mcp_tool = TavilyTool({"api_key_env": "TAVILY_API_KEY", "config": {"search_depth": "advanced"}})

    # Initialize LLM
    print(f"Initializing {args.llm}...")
    if args.llm == "claude":
        llm_config = {
            "api_key_env": "ANTHROPIC_API_KEY",
            "config": {"model": "claude-3-opus-20240229"}
        }
        llm = ClaudeLLM(llm_config)
    else:
        llm_config = {
            "api_key_env": "OPENAI_API_KEY",
            "config": {"model": "gpt-4-turbo-preview"}
        }
        llm = GPT4LLM(llm_config)

    # Initialize Judge
    judge = AIJudge()

    # Load Questions
    try:
        with open(questions_path, 'r') as f:
            questions = json.load(f)
    except Exception as e:
        print(f"Error loading questions: {e}")
        print(f"Questions Path: {questions_path}")
        return

    results = []
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    print(f"\nStarting evaluation: {args.mcp} + {args.llm}")
    print("="*50)

    target_url = "https://bizgenieai.com/"

    for q in questions:
        qid = q["id"]
        question_text = q["question"]
        
        print(f"Processing {qid}: {question_text}")

        # 1. Search
        try:
            search_res = mcp_tool.search(question_text, context=target_url)
        except Exception as e:
            print(f"  Search failed: {e}")
            continue

        # 2. Generate
        system_prompt = (
            f"You are an expert customer support representative for {target_url}. "
            "Your goal is to provide accurate, helpful answers primarily based on the information "
            "retrieved from this website."
        )
        
        history = [{"role": "user", "content": question_text}]

        try:
            llm_res = llm.generate(history, search_res.content, system_prompt=system_prompt)
        except Exception as e:
            print(f"  Generation failed: {e}")
            continue

        # 3. Evaluate (Absolute Quality)
        print("  Evaluating with AI Judge...")
        
        # We evaluate the system answer directly. 
        # Since we removed baseline, we pass just the system answer and sources.
        scores = judge.evaluate_answer(
            question=question_text,
            system_answer=llm_res.answer,
            system_sources=search_res.sources
        )

        # Store result
        result_entry = {
            "question_id": qid,
            "question": question_text,
            "answer": llm_res.answer,
            "sources": search_res.sources,
            "metrics": {
                "search_time": search_res.search_time,
                "gen_time": llm_res.generation_time,
                "total_time": search_res.search_time + llm_res.generation_time,
                "tokens": llm_res.tokens_used,
                "search_cost": getattr(search_res, 'search_cost', 0.0),
                "gen_cost": getattr(llm_res, 'generation_cost', 0.0)
            },
            "scores": scores
        }
        results.append(result_entry)
        print(f"  Score: {scores.get('overall_quality', 0):.1f}/100")

    # Save Results
    output_dir = os.path.join(project_root, "test_results", f"{args.mcp}_{args.llm}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results.json (raw data)
    results_file = os.path.join(output_dir, f"results_{timestamp}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Save eval.json (scores) - mimicking the structure expected by generate_report
    # Ideally we'd just save one file, but generate_report expects 'eval_*.json'
    # with specific structure. Let's save 'eval_*.json' containing the scored results.
    eval_file = os.path.join(output_dir, f"eval_{timestamp}.json")
    
    # Adapt results to eval structure if needed, but 'results' list already contains 'scores'
    # generated by AIJudge. So we can just save 'results' as the eval file too, 
    # or better, save a simplified list of evaluations.
    # AIJudge.evaluate_batch used to return a list of evaluation dicts.
    # Here 'scores' IS the evaluation dict for one question.
    # Let's extract the evaluation dicts and save them.
    
    evaluations = []
    for r in results:
        ev = r["scores"]
        # Add metadata expected by report generator
        ev["question_id"] = r["question_id"]
        ev["question"] = r["question"]
        # Add verdict logic if not present in scores
        if "verdict" not in ev:
            score = ev.get("overall_quality", 0)
            if ev.get("hallucination"):
                ev["verdict"] = "HALLUCINATION"
            elif score >= 80:
                ev["verdict"] = "EXCELLENT"
            elif score >= 60:
                ev["verdict"] = "GOOD"
            elif score >= 40:
                ev["verdict"] = "FAIR"
            else:
                ev["verdict"] = "POOR"
        evaluations.append(ev)

    with open(eval_file, 'w') as f:
        json.dump(evaluations, f, indent=2)

    print("="*50)
    print(f"Execution & Evaluation complete.")
    print(f"Results: {results_file}")
    print(f"Evaluations: {eval_file}")

if __name__ == "__main__":
    main()
