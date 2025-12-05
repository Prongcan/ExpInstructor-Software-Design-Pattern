import os
import sys
# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use unified GPT evaluation template
from Evaluation_utils.gpt_evaluation_template import generate_gpt_evaluation
from Evaluation_utils.test_idea import raw_idea
from service.DistilBERT import build_novelty_classifier, predict_novelty_score
from Evaluation_utils.eval_novelty import generate_novelty_score


def generate_novelty_evaluation(idea_text: str) -> str:
    """
    Generate novelty evaluation using unified GPT template.
    Refactored with Template Method Pattern: Uses unified template instead of duplicated code.
    """
    # Refactored with Template Method Pattern: Use unified GPT evaluation template
    result = generate_gpt_evaluation(idea_text, "novelty")
    # For novelty, we expect a string result, not tuple
    if isinstance(result, tuple):
        return result[0] if result[0] else ""
    return result


def main() -> None:
    """
    Main function for GPT novelty evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/3] Generating novelty evaluation ...")
    # Use Template Method Pattern for generation
    result = generate_novelty_evaluation(raw_idea)
    print(result)
    
    # Use GPT to score the evaluation result - Differentiated functionality
    print("\n[2/3] Using GPT model to evaluate score ...")
    gpt_score_result = generate_novelty_score(result)
    if gpt_score_result and not gpt_score_result.startswith("ERROR"):
        print(f"\nGPT scoring result:")
        print(gpt_score_result)
    else:
        print("GPT scoring failed")
    
    # Use BERT model to score the evaluation result - Differentiated functionality
    print("\n[3/3] Using BERT model to evaluate score ...")
    classifier, device = build_novelty_classifier()
    if classifier is None:
        print("Warning: BERT model loading failed, skipping scoring step")
        return
    
    score_result = predict_novelty_score(classifier, result)
    if score_result:
        print(f"\nBERT scoring result:")
        print(f"  Novelty score: {score_result['predicted_score']}/10")
        print(f"  Confidence: {score_result['confidence']:.4f}")
    else:
        print("BERT scoring failed")


if __name__ == "__main__":
    main()
