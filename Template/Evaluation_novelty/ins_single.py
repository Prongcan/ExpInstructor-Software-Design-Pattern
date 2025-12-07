import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use unified InstructorEvaluationTemplate
from Evaluation_utils.ins_evaluation_template import (
    InstructorEvaluationTemplate,
    generate_agent_evaluation,
    create_novelty_evaluator
)
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_novelty import generate_novelty_score

try:
    # Try relative import first (when imported as module)
    from .ins_model import create_custom_agent
except ImportError:
    # Fall back to absolute import (when run directly)
    from ins_model import create_custom_agent

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using InstructorEvaluationTemplate
# ==============================================================================

def generate_novelty_evaluation_via_agent(agent, idea_text: str) -> str:
    """
    Generate novelty evaluation using Agent.
    Refactored with Template Method Pattern: Uses unified InstructorEvaluationTemplate.
    """
    evaluator = InstructorEvaluationTemplate("novelty")
    return evaluator.generate_evaluation_via_agent(agent, idea_text)

def generate_novelty_evaluation(idea_text: str) -> str:
    """
    Generate novelty evaluation for an idea.
    Refactored with Template Method Pattern: Uses unified API.
    """
    return generate_agent_evaluation(idea_text, "novelty")

def main() -> str:
    """
    Main function for novelty evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/2] Generating novelty evaluation via Agent ...")
    # Use unified template for generation  
    result = generate_agent_evaluation(raw_idea, "novelty")
    print(result)
    
    # Use GPT to score the evaluation result - Differentiated functionality
    print("\n[2/2] Using GPT model to evaluate score ...")
    gpt_score_result = generate_novelty_score(result)
    if gpt_score_result and not gpt_score_result.startswith("ERROR"):
        print(f"\nGPT scoring result:")
        print(gpt_score_result)
    else:
        print("GPT scoring failed")
    
    return result

if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 60)
    print("Novelty evaluation completed!")
    print("=" * 60)
