import os
import sys

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use concrete significance evaluator
from Template.ins_significance_evaluator import SignificanceInstructorEvaluator
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_significance import generate_significance_score

try:
    # Try relative import first (when imported as module)
    from .ins_model import create_custom_agent
except ImportError:
    # Fall back to absolute import (when run directly)
    from ins_model import create_custom_agent

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using concrete SignificanceInstructorEvaluator
# ==============================================================================

def generate_significance_evaluation_via_agent(agent, idea_text: str) -> str:
    """
    Generate significance evaluation using Agent.
    Refactored with Template Method Pattern: Uses concrete SignificanceInstructorEvaluator.
    """
    evaluator = SignificanceInstructorEvaluator()
    return evaluator.generate_evaluation_via_agent(agent, idea_text)

def generate_significance_evaluation(idea_text: str) -> str:
    """
    Generate significance evaluation for an idea.
    Refactored with Template Method Pattern: Uses concrete evaluator.
    """
    evaluator = SignificanceInstructorEvaluator()
    return evaluator.generate_evaluation(idea_text)

def main() -> str:
    """
    Main function for significance evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/2] Generating significance evaluation via Agent...")
    # Use concrete evaluator for generation
    result = generate_significance_evaluation(raw_idea)
    print(result)
    
    # Use GPT to score the evaluation result - Differentiated functionality  
    print("\n[2/2] Using GPT model to evaluate score...")
    gpt_score_result = generate_significance_score(result)
    if gpt_score_result and not gpt_score_result.startswith("ERROR"):
        print(f"\nGPT score result:")
        print(gpt_score_result)
    else:
        print("GPT scoring failed")
    
    return result

if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 60)
    print("Significance evaluation completed!")
    print("=" * 60)
