#!/bin/bash

# Benchmark Suite Runner (Internal)
# This script is designed to run INSIDE the docker container.

echo "========================================================"
echo "🚀 STARTING FULL RAG BENCHMARK SUITE (INTERNAL)"
echo "========================================================"
echo "Working directory: $(pwd)"

# Create logs directory
# Ensure we are in workspace or absolute path
LOG_DIR="/workspace/test_results/logs"
mkdir -p "$LOG_DIR"

echo "Logs will be saved to $LOG_DIR"
echo ""

# Define combinations to test
# Added Exa combinations
declare -a combinations=(
    "tavily claude"
    "tavily gpt4"
    "jina claude"
    "jina gpt4"
)

# Start all combinations in parallel
pids=()
log_files=()

for combo in "${combinations[@]}"; do
    set -- $combo
    MCP=$1
    LLM=$2
    LOG_FILE="$LOG_DIR/${MCP}_${LLM}.log"
    
    # Clear old log
    > "$LOG_FILE"

    echo "🧪 Starting: $MCP + $LLM"

    # Run python directly (we are already inside container)
    python3 scripts/run_evaluation.py --mcp $MCP --llm $LLM > "$LOG_FILE" 2>&1 &

    pids+=($!)
    log_files+=("$LOG_FILE")
done

echo ""
echo "All 6 evaluations running. Monitoring progress..."
echo "------------------------------------------------"

# Monitor loop
while true; do
    running_count=0
    output_lines=""
    
    for i in "${!pids[@]}"; do
        pid=${pids[$i]}
        combo=${combinations[$i]}
        logfile=${log_files[$i]}
        
        # Check if process is still running
        if kill -0 $pid 2>/dev/null; then
            running_count=$((running_count + 1))
            # Get last line of log (tail might fail if file empty)
            if [ -f "$logfile" ]; then
                last_line=$(tail -n 1 "$logfile" 2>/dev/null | cut -c1-80) 
            else
                last_line="Initializing..."
            fi
            output_lines+="${combo}: ${last_line}..\n"
        else
            output_lines+="${combo}: ✅ Completed (or Failed - check log)\n"
        fi
    done

    # Clear screen section (simple implementation)
    # Adjust cursor move for 6 lines
    printf "\033[7A"
    printf "$output_lines"
    
    if [ $running_count -eq 0 ]; then
        break
    fi
    
    sleep 2
done

echo ""
echo "------------------------------------------------"
echo "All processes finished."
echo ""

echo "========================================================"
echo "📊 GENERATING FINAL COMPARISON REPORT"
echo "========================================================"

python3 scripts/generate_comparison_report.py

echo ""
echo "✅ Done! Review the report above."