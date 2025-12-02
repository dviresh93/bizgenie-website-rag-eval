"""
AI-as-Judge Evaluation Script (Simplified)
Evaluates system answers based on absolute quality metrics.
No baseline comparison required.
"""

import json
import os
import time
import re
from typing import Dict, List, Optional
from anthropic import Anthropic
from pydantic import BaseModel, Field, ValidationError # Import BaseModel and Field

# Define a Pydantic model for the expected JSON output from the AI Judge
class JudgeResult(BaseModel):
    accuracy: int = Field(..., ge=0, le=100)
    completeness: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    helpfulness: int = Field(..., ge=0, le=100)
    hallucination: bool
    reasoning: str
    overall_quality: float = 0.0 # Add this field to the Pydantic model

class AIJudge:
    """
    AI-as-Judge evaluator that scores answers on absolute quality.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialize AI Judge
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not found for AIJudge")
        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def evaluate_answer(
        self,
        question: str,
        system_answer: str,
        system_sources: List[str],
        retries: int = 3
    ) -> JudgeResult: # Change return type to JudgeResult
        """
        Evaluate answer quality using AI judge.
        """
        
        sources_text = "\n".join(f"- {src}" for src in system_sources) if system_sources else "No sources provided"

        prompt = f"""You are an expert evaluator grading an AI Support Agent's response.

QUESTION:
{question}

SYSTEM ANSWER (To be graded):
{system_answer}

SYSTEM SOURCES:
{sources_text}

**EVALUATION INSTRUCTIONS:**
Grade the answer on a 0-100 scale for each criteria. Be strict but fair.

1. **ACCURACY (0-100)**: Is the information factually plausible and consistent? (If sources are provided, does the answer align with them? If no sources, does it sound hallucinated?)
2. **COMPLETENESS (0-100)**: Does the answer fully address the user's question?
3. **CLARITY (0-100)**: Is the answer clear, readable, and well-structured?
4. **HELPFULNESS (0-100)**: Is the tone appropriate (polite, professional) and the content useful?
5. **HALLUCINATION CHECK (Yes/No)**: Does the answer make specific claims (numbers, features) that are NOT supported by the provided sources? (If no sources are provided but the answer claims specific facts, mark as potential hallucination).

Respond ONLY with a valid JSON object:
{{
  "accuracy": <score>,
  "completeness": <score>,
  "clarity": <score>,
  "helpfulness": <score>,
  "hallucination": true/false,
  "reasoning": "<brief explanation>"
}}"""

        for attempt in range(retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )

                content = response.content[0].text.strip()
                
                # Robust JSON extraction using regex
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON object found in LLM response.")
                
                # Parse with Pydantic for validation
                judge_result = JudgeResult.model_validate_json(json_str)

                # Calculate overall quality
                # Weighted average: Accuracy (40%), Completeness (30%), Clarity (15%), Helpfulness (15%)
                judge_result.overall_quality = ( # Add overall_quality as dynamic attribute
                    judge_result.accuracy * 0.40 +
                    judge_result.completeness * 0.30 +
                    judge_result.clarity * 0.15 +
                    judge_result.helpfulness * 0.15
                )
                
                # Penalty for hallucination
                if judge_result.hallucination:
                    judge_result.overall_quality *= 0.5 # Severe penalty

                return judge_result

            except (ValueError, ValidationError, Exception) as e: # Catch Pydantic validation errors
                print(f"   ⚠️ AI Judge Error (Attempt {attempt+1}): {e}")
                print(f"   [DEBUG] Content attempted to parse:\n{content}\n[END DEBUG]\n")
                if attempt == retries - 1:
                    # Return a default JudgeResult on persistent failure
                    return JudgeResult(
                        accuracy=0, completeness=0, clarity=0, helpfulness=0,
                        hallucination=True, reasoning=f"Evaluation failed: {str(e)}"
                    )
                time.sleep(2)

    def evaluate_batch(self, results_file: str, output_file: str):
        """
        Evaluate a batch of system results.
        """
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

            # Convert JudgeResult Pydantic model to dict for JSON serialization
            evaluation_dict = evaluation.model_dump()
            
            # Add metadata
            evaluation_dict["question_id"] = q_id
            evaluation_dict["question"] = result["question"]
            
            # Determine verdict based on score
            score = evaluation.overall_quality # Access attribute directly
            if evaluation.hallucination: # Access attribute directly
                verdict = "HALLUCINATION"
            elif score >= 80:
                verdict = "EXCELLENT"
            elif score >= 60:
                verdict = "GOOD"
            elif score >= 40:
                verdict = "FAIR"
            else:
                verdict = "POOR"
            
            evaluation_dict["verdict"] = verdict
            evaluations.append(evaluation_dict)

            print(f"   Score: {score:.1f}/100 ({verdict})")
            # Rate limiting
            time.sleep(1)

        # Save evaluations
        with open(output_file, 'w') as f:
            json.dump(evaluations, f, indent=2)

        print(f"\n✅ Evaluation complete! Saved to {output_file}")