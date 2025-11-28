#!/bin/bash

# Benchmark Suite Runner (Parallelized)
# Runs all key combinations of MCP Tools and LLMs in parallel.

echo "========================================================"
echo "🚀 STARTING FULL RAG BENCHMARK SUITE (PARALLEL MODE)"
echo "========================================================"
echo "Running all 4 combinations in parallel..."
echo "This will take approximately 3-5 minutes."
echo ""

# Create temporary directory for logs
mkdir -p test_results/logs

# Define combinations to test
declare -a combinations=(
    "tavily claude"
    "tavily gpt4"
    "jina claude"
    "jina gpt4"
)

# Start all combinations in parallel
pids=()
for combo in "${combinations[@]}"; do
    set -- $combo
    MCP=$1
    LLM=$2

    echo "🧪 Starting: $MCP + $LLM (background)"

    # Run in background and save PID
    python3 scripts/run_evaluation.py --mcp $MCP --llm $LLM \
        > test_results/logs/${MCP}_${LLM}.log 2>&1 &

    pids+=($!)
done

echo ""
echo "All 4 evaluations running in parallel..."
echo "PIDs: ${pids[@]}"
echo ""

# Wait for all processes and track results
failed=0
for i in "${!pids[@]}"; do
    set -- ${combinations[$i]}
    MCP=$1
    LLM=$2

    echo "⏳ Waiting for $MCP + $LLM (PID: ${pids[$i]})..."

    if wait ${pids[$i]}; then
        echo "✅ Finished: $MCP + $LLM"
    else
        echo "❌ Failed: $MCP + $LLM (check test_results/logs/${MCP}_${LLM}.log)"
        failed=$((failed + 1))
    fi
done

echo ""
echo "========================================================"
echo "📊 GENERATING FINAL COMPARISON REPORT"
echo "========================================================"

if [ $failed -gt 0 ]; then
    echo "⚠️  Warning: $failed combination(s) failed"
    echo "   Check log files in test_results/logs/"
    echo ""
fi

python3 scripts/generate_comparison_report.py

echo ""
echo "✅ Done! Review the report above."
echo "   Logs saved to: test_results/logs/"
