import os
import sys
# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use unified GPT evaluation template
from Evaluation_utils.gpt_evaluation_template import generate_gpt_evaluation
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_feasibility_score import generate_feasibility_score


def generate_feasibility_evaluation(idea_text: str) -> str:
    """
    Generate complete peer review evaluation text using unified GPT template.
    Refactored with Template Method Pattern: Uses unified template instead of duplicated code.
    """
    # Refactored with Template Method Pattern: Use unified GPT evaluation template
    result = generate_gpt_evaluation(idea_text, "feasibility_score")
    # For feasibility_score, we expect a string result, not tuple
    if isinstance(result, tuple):
        return result[0] if result[0] else ""
    return result


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
