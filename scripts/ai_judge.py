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
    ) -> dict:
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
                # Cleanup markdown
                if content.startswith("```json"):
                    content = content.split("```json")[1]
                if content.endswith("```"):
                    content = content.split("```")[0]
                
                try:
                    result = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"\n[DEBUG] JSON Decode Error. Content received:\n{content}\n[END DEBUG]\n")
                    raise e

                # Calculate overall quality
                # Weighted average: Accuracy (40%), Completeness (30%), Clarity (15%), Helpfulness (15%)
                result["overall_quality"] = (
                    result["accuracy"] * 0.40 +
                    result["completeness"] * 0.30 +
                    result["clarity"] * 0.15 +
                    result["helpfulness"] * 0.15
                )
                
                # Penalty for hallucination
                if result.get("hallucination"):
                    result["overall_quality"] *= 0.5 # Severe penalty

                return result

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

            # Add metadata
            evaluation["question_id"] = q_id
            evaluation["question"] = result["question"]
            
            # Determine verdict based on score
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
            # Rate limiting
            time.sleep(1)

        # Save evaluations
        with open(output_file, 'w') as f:
            json.dump(evaluations, f, indent=2)

        print(f"\n✅ Evaluation complete! Saved to {output_file}")