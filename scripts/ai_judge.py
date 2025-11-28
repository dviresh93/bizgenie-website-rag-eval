import anthropic
import os
import json
import sys
import time
import re
from typing import Dict, List, Optional

class AIJudge:
    """AI-as-judge for answer quality evaluation"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not found for AIJudge")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def load_baseline(self, baseline_file: str) -> Dict:
        """Parses the filled baseline.md file into a dictionary."""
        if not os.path.exists(baseline_file):
            raise FileNotFoundError(f"Baseline file not found at {baseline_file}")

        with open(baseline_file, 'r') as f:
            content = f.read()

        baseline = {}
        # Regex to find blocks starting with "## qX" or "## **qX" 
        question_blocks = re.findall(r'## \**q(\d+).*?\n(.*?)(?=\n## \**q|\Z)', content, re.DOTALL)

        for q_id, block_content in question_blocks:
            full_id = f"q{q_id}"
            
            # Extract Answer part
            # Look for "**Answer**:" or just take the text if formatting is loose
            answer_match = re.search(r'\*\*Answer\*\*:(.*?)(?=\n\*\*|\Z)', block_content, re.DOTALL)
            if answer_match:
                answer_text = answer_match.group(1).strip()
            else:
                # Fallback: try to guess where answer starts (e.g. after question line)
                # The block_content captured by regex starts AFTER the ## header line.
                # It usually contains "**Question**: ...". We want what comes after that.
                parts = block_content.split("**Answer**:")
                if len(parts) > 1:
                    answer_text = parts[1].strip()
                else:
                    # Just take everything as answer if no marker found
                    answer_text = block_content.strip()

            # Clean up extra *** or markers
            answer_text = answer_text.replace("***", "").strip()
            
            # Check if baseline has substantive info
            has_info = not self._is_no_info_answer(answer_text)

            baseline[full_id] = {
                "answer": answer_text,
                "has_info": has_info
            }
        return baseline

    def _is_no_info_answer(self, answer: str) -> bool:
        """Check if baseline answer indicates no information available"""
        no_info_patterns = [
            "information not available",
            "not publicly listed",
            "not publicly available",
            "not publicly detailed",
            "not mentioned in publicly available",
            "specific information about.*is not",
        ]
        answer_lower = answer.lower()
        return any(re.search(pattern, answer_lower) for pattern in no_info_patterns)

    def evaluate_answer(
        self,
        question: str,
        our_answer: str,
        baseline_answer: str,
        our_sources: list = None,
        baseline_sources: list = None,
        retries: int = 3
    ) -> dict:
        """
        Compare our answer to baseline. Includes retry logic for rate limits.
        """

        prompt = f"""You are an expert evaluator comparing an AI Agent's response against a Ground Truth baseline.

QUESTION:
{question}

ANSWER A (System Under Test - AI Support Agent):
{our_answer}

ANSWER B (Ground Truth Baseline - Factual Reference):
{baseline_answer}

**EVALUATION INSTRUCTIONS:**
You must grade Answer A based on how well it conveys the facts present in Answer B.

**CRITICAL:** Answer A is acting as a helpful Customer Support Representative (using "we", polite tone). Answer B is a neutral fact sheet. **DO NOT** penalize Answer A for its style, tone, or persona. Only evaluate whether the *information* it provides is factually consistent with Answer B.

Please evaluate on the following criteria:

1. **ACCURACY (0-100)**: Is the information in Answer A factually correct based *only* on the Ground Truth (Answer B)? (Ignore missing details here, focus on contradictions).
2. **COMPLETENESS (0-100)**: Does Answer A cover the key facts mentioned in the Ground Truth? (e.g. If baseline lists 3 features, does Agent mention them?)
3. **CLARITY (0-100)**: Is Answer A clear, readable, and helpful to a user?
4. **HELPFULNESS (0-100)**: Does the answer effectively address the user's intent?

Respond ONLY with a valid JSON object. Do not add markdown formatting or explanations outside the JSON.
{{
  "accuracy": <score>,
  "completeness": <score>,
  "clarity": <score>,
  "helpfulness": <score>,
  "reasoning": "<brief explanation of why you gave these scores>"
}}"""

        for attempt in range(retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                content = response.content[0].text.strip()
                # Basic cleanup if model adds markdown
                if content.startswith("```json"):
                    content = content.split("```json")[1]
                if content.endswith("```"):
                    content = content.split("```")[0]
                
                result = json.loads(content)

                # Calculate overall quality
                result["overall_quality"] = (
                    result["accuracy"] * 0.40 +
                    result["completeness"] * 0.30 +
                    result["clarity"] * 0.15 +
                    result["helpfulness"] * 0.15
                )

                return result

            except anthropic.RateLimitError:
                wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s...
                print(f"   ⚠️ Rate limit hit. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            except Exception as e:
                print(f"   ⚠️ AI Judge Error (Attempt {attempt+1}): {e}")
                if attempt == retries - 1:
                    return {
                        "accuracy": 0,
                        "completeness": 0,
                        "clarity": 0,
                        "helpfulness": 0,
                        "overall_quality": 0,
                        "reasoning": f"Evaluation failed after retries: {str(e)}"
                    }
                time.sleep(1)

    def evaluate_batch(
        self,
        results_file: str,
        baseline_file: str,
        output_file: str
    ):
        """
        Evaluate a batch of system results against baseline
        """
        # Load baseline
        print(f"📖 Loading baseline from {baseline_file}...")
        baseline_data = self.load_baseline(baseline_file)
        
        # Load system results
        print(f"📖 Loading system results from {results_file}...")
        with open(results_file) as f:
            system_results = json.load(f)

        evaluations = []

        for i, result in enumerate(system_results, 1):
            q_id = f"q{result['question_id']}" if not str(result['question_id']).startswith('q') else result['question_id']

            print(f"\n[{i}/{len(system_results)}] Evaluating {q_id}...")

            # Get baseline for this question
            baseline = baseline_data.get(q_id)
            if not baseline:
                print(f"   ⚠️  No baseline found for {q_id}, skipping")
                continue

            # Evaluate
            evaluation = self.evaluate_answer(
                question=result["question"],
                our_answer=result["answer"],
                baseline_answer=baseline["answer"]
            )

            # Add metadata
            evaluation["question_id"] = q_id
            evaluation["question"] = result["question"]
            
            # Determine verdict
            score = evaluation.get("overall_quality", 0)
            if score >= 80:
                verdict = "EXCELLENT"
            elif score >= 60:
                verdict = "GOOD"
            elif score >= 40:
                verdict = "FAIR"
            else:
                verdict = "POOR"
            
            evaluation["verdict"] = verdict
            
            # Check "Found More" logic
            # If baseline has NO info but we got a good score (>=60), we found more.
            if not baseline["has_info"] and score >= 60:
                evaluation["found_more_than_baseline"] = True
                print(f"   🎉 Found MORE info than baseline!")
            else:
                evaluation["found_more_than_baseline"] = False

            evaluations.append(evaluation)

            # Print result
            print(f"   Score: {score:.1f}/100 ({verdict})")
            
            # Sleep to avoid rate limits
            time.sleep(1)

        # Save evaluations
        with open(output_file, 'w') as f:
            json.dump(evaluations, f, indent=2)

        print(f"\n✅ Evaluation complete! Saved to {output_file}")