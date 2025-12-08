import os
import sys
# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use concrete score evaluator
from Template.gpt_score_evaluator import ScoreGPTEvaluator
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_feasibility_score import generate_feasibility_score


def generate_feasibility_evaluation(idea_text: str) -> str:
    """
    Generate complete peer review evaluation text using concrete ScoreGPTEvaluator.
    Refactored with Template Method Pattern: Uses concrete evaluator subclass.
    """
    # Refactored with Template Method Pattern: Use concrete evaluator subclass
    evaluator = ScoreGPTEvaluator()
    result = evaluator.generate_evaluation(idea_text)
    # For feasibility_score, we expect a string result directly
    return result if isinstance(result, str) else ""


def main() -> None:
    """
    Main function for GPT feasibility score evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/2] Generating feasibility evaluation text ...")
    # Use Template Method Pattern for generation
    result = generate_feasibility_evaluation(raw_idea)
    print(result)
    
    # Use eval_feasibility_score.py to score the evaluation result - Differentiated functionality
    print("\n[2/2] Using eval_feasibility_score.py to evaluate score ...")
    
    # Directly use evaluation text (no formatting needed)
    score_result = generate_feasibility_score(result)
    if score_result and not score_result.startswith("ERROR"):
        print(f"\nScoring result:")
        print(score_result)
    else:
        print("Scoring failed")


if __name__ == "__main__":
    main()
