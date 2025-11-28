"""
AI-as-Judge Evaluation Script (Pydantic Structured Output)
Evaluates system answers based on absolute quality metrics using Tool Use.
"""

import json
import os
import time
from typing import Dict, List, Optional
from anthropic import Anthropic
from pydantic import BaseModel, Field

class EvaluationResult(BaseModel):
    """Structured evaluation result schema"""
    accuracy: int = Field(..., description="Score 0-100 for factual accuracy")
    completeness: int = Field(..., description="Score 0-100 for completeness")
    clarity: int = Field(..., description="Score 0-100 for clarity")
    helpfulness: int = Field(..., description="Score 0-100 for helpfulness")
    hallucination: bool = Field(..., description="True if the answer contains unsupported claims")
    reasoning: str = Field(..., description="Brief explanation of the scores")

class AIJudge:
    """
    AI-as-Judge evaluator using Anthropic Tool Use for structured output.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not found for AIJudge")
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        
        # Define the tool schema from Pydantic model
        self.tool_schema = {
            "name": "submit_evaluation",
            "description": "Submit the evaluation scores for the AI answer.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "accuracy": {"type": "integer", "description": "Score 0-100 for factual accuracy"},
                    "completeness": {"type": "integer", "description": "Score 0-100 for completeness"},
                    "clarity": {"type": "integer", "description": "Score 0-100 for clarity"},
                    "helpfulness": {"type": "integer", "description": "Score 0-100 for helpfulness"},
                    "hallucination": {"type": "boolean", "description": "True if answer contains unsupported claims"},
                    "reasoning": {"type": "string", "description": "Brief explanation"}
                },
                "required": ["accuracy", "completeness", "clarity", "helpfulness", "hallucination", "reasoning"]
            }
        }

    def evaluate_answer(
        self,
        question: str,
        system_answer: str,
        system_sources: List[str],
        retries: int = 3
    ) -> dict:
        
        sources_text = "\n".join(f"- {src}" for src in system_sources) if system_sources else "No sources provided"

        prompt = f"""You are an expert evaluator grading an AI Support Agent's response.

QUESTION:
{question}

SYSTEM ANSWER (To be graded):
{system_answer}

SYSTEM SOURCES:
{sources_text}

**INSTRUCTIONS:**
Evaluate the answer and use the 'submit_evaluation' tool to report your scores.
Be strict but fair. Focus on whether the answer is supported by the sources.
"""

        for attempt in range(retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                    tools=[self.tool_schema],
                    tool_choice={"type": "tool", "name": "submit_evaluation"}
                )

                # Extract tool input
                if response.content and response.content[0].type == 'tool_use':
                    tool_input = response.content[0].input
                else:
                    # Handle case where model might have output text before tool use
                    tool_use = next((block for block in response.content if block.type == 'tool_use'), None)
                    if tool_use:
                        tool_input = tool_use.input
                    else:
                        raise ValueError("Model did not use the evaluation tool")

                # Validate with Pydantic (optional but good practice)
                eval_data = EvaluationResult(**tool_input).dict()

                # Calculate overall quality
                eval_data["overall_quality"] = (
                    eval_data["accuracy"] * 0.40 +
                    eval_data["completeness"] * 0.30 +
                    eval_data["clarity"] * 0.15 +
                    eval_data["helpfulness"] * 0.15
                )
                
                if eval_data["hallucination"]:
                    eval_data["overall_quality"] *= 0.5

                return eval_data

            except Exception as e:
                print(f"   ⚠️ AI Judge Error (Attempt {attempt+1}): {e}")
                if attempt == retries - 1:
                    return {
                        "accuracy": 0, "completeness": 0, "clarity": 0, "helpfulness": 0,
                        "hallucination": False, "overall_quality": 0, 
                        "reasoning": f"Evaluation failed: {str(e)}"
                    }
                time.sleep(2)

    def evaluate_batch(self, results_file: str, output_file: str):
        print(f"📖 Loading system results from {results_file}...")
        with open(results_file) as f:
            system_results = json.load(f)

        evaluations = []

        for i, result in enumerate(system_results, 1):
            q_id = result["question_id"]
            print(f"\n[{i}/{len(system_results)}] Evaluating {q_id}...")

            evaluation = self.evaluate_answer(
                question=result["question"],
                system_answer=result["answer"],
                system_sources=result.get("sources", [])
            )

            evaluation["question_id"] = q_id
            evaluation["question"] = result["question"]
            
            score = evaluation.get("overall_quality", 0)
            if evaluation.get("hallucination"):
                verdict = "HALLUCINATION"
            elif score >= 80:
                verdict = "EXCELLENT"
            elif score >= 60:
                verdict = "GOOD"
            elif score >= 40:
                verdict = "FAIR"
            else:
                verdict = "POOR"
            
            evaluation["verdict"] = verdict
            evaluations.append(evaluation)

            print(f"   Score: {score:.1f}/100 ({verdict})")
            time.sleep(1)

        with open(output_file, 'w') as f:
            json.dump(evaluations, f, indent=2)

        print(f"\n✅ Evaluation complete! Saved to {output_file}")
