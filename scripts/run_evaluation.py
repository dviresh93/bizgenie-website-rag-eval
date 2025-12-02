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
from api.app.tools.exa_tool import ExaTool
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
    elif args.mcp == "tavily":
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

    system_results = []
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    print(f"\n🚀 Starting evaluation run: {args.mcp} + {args.llm}")
    print("="*50)

    target_url = "https://bizgenieai.com/"

    # --- PHASE 1: EXECUTION ---
    for i, q in enumerate(questions, 1):
        qid = q["id"]
        question_text = q["question"]
        
        print(f"\n[{i}/{len(questions)}] Processing {qid}: {question_text}")

        # 1. Search
        start_search = time.time()
        try:
            search_res = mcp_tool.search(question_text, context=target_url)
            search_time = time.time() - start_search
            print(f"   ✓ Search found {len(search_res.sources)} sources ({search_time:.2f}s)")
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
            continue

        # 2. Generate
        start_gen = time.time()
        
        system_prompt = (
            f"You are an expert customer support representative for {target_url}. "
            "Your goal is to provide accurate, helpful answers primarily based on the information "
            "retrieved from this website."
        )
        
        history = [{"role": "user", "content": question_text}]

        try:
            llm_res = llm.generate(history, search_res.content, system_prompt=system_prompt)
            gen_time = time.time() - start_gen
            print(f"   ✓ Answer generated ({gen_time:.2f}s)")
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            continue

        # Store result
        result_entry = {
            "question_id": qid,
            "question": question_text,
            "answer": llm_res.answer,
            "sources": search_res.sources,
            "metrics": {
                "search_time": search_time,
                "gen_time": gen_time,
                "total_time": search_time + gen_time,
                "tokens": llm_res.tokens_used,
                # Add costs here for reporting
                "search_cost": getattr(search_res, 'search_cost', 0.0),
                "gen_cost": getattr(llm_res, 'generation_cost', 0.0)
            }
        }
        system_results.append(result_entry)

    # Save System Results
    output_dir = os.path.join(project_root, "test_results", f"{args.mcp}_{args.llm}")
    os.makedirs(output_dir, exist_ok=True)
    results_file = os.path.join(output_dir, f"results_{timestamp}.json")
    eval_file = os.path.join(output_dir, f"eval_{timestamp}.json")
    
    with open(results_file, 'w') as f:
        json.dump(system_results, f, indent=2)

    print("\n" + "="*60)
    print(f"✅ Execution complete. Results saved to {results_file}")
    print("="*60)

    # --- PHASE 2: EVALUATION ---
    print(f"\n⚖️  Starting AI Judge Evaluation...")
    
    try:
        judge.evaluate_batch(
            results_file=results_file,
            output_file=eval_file
        )
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
