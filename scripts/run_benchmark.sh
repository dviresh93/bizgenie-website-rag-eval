#!/bin/bash

# Benchmark Suite Runner
# Runs all key combinations of MCP Tools and LLMs against the baseline.

echo "========================================================"
echo "🚀 STARTING FULL RAG BENCHMARK SUITE"
echo "========================================================"
echo "This will take approximately 10-15 minutes depending on API latency."
echo "Ensuring all services are up..."

# Define combinations to test
declare -a combinations=(
    "tavily claude"
    "tavily gpt4"
    "jina claude"
    "jina gpt4"
)

for combo in "${combinations[@]}"; do
    set -- $combo
    MCP=$1
    LLM=$2
    
    echo ""
    echo "--------------------------------------------------------"
    echo "🧪 Testing Combination: $MCP + $LLM"
    echo "--------------------------------------------------------"
    
    python3 scripts/run_evaluation.py --mcp $MCP --llm $LLM
    
    if [ $? -eq 0 ]; then
        echo "✅ Finished $MCP + $LLM"
    else
        echo "❌ Failed $MCP + $LLM"
        # Continue to next even if one fails
    fi
    
    # Small pause to be nice to APIs
    sleep 2
done

echo ""
echo "========================================================"
echo "📊 GENERATING FINAL COMPARISON REPORT"
echo "========================================================"

python3 scripts/generate_comparison_report.py

echo ""
echo "Done! Review the report above."
