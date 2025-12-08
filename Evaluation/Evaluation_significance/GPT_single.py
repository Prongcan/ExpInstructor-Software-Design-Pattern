import os
import sys
# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use concrete significance evaluator
from Template.gpt_significance_evaluator import SignificanceGPTEvaluator
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_significance import generate_significance_score


def generate_significance_evaluation(idea_text: str) -> str:
    """
    Generate significance evaluation using concrete SignificanceGPTEvaluator.
    Refactored with Template Method Pattern: Uses concrete evaluator subclass.
    """
    # Refactored with Template Method Pattern: Use concrete evaluator subclass
    evaluator = SignificanceGPTEvaluator()
    result = evaluator.generate_evaluation(idea_text)
    # For significance, we expect a string result directly
    return result if isinstance(result, str) else ""


def main() -> None:
    """
    Main function for GPT significance evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/2] Generating significance evaluation...")
    # Use Template Method Pattern for generation
    result = generate_significance_evaluation(raw_idea)
    print(result)
    
    # Use GPT to evaluate the result of the significance evaluation - Differentiated functionality
    print("\n[2/2] Using GPT model to evaluate score...")
    gpt_score_result = generate_significance_score(result)
    if gpt_score_result and not gpt_score_result.startswith("ERROR"):
        print(f"\nGPT score result:")
        print(gpt_score_result)
    else:
        print("GPT scoring failed")


if __name__ == "__main__":
    main()
