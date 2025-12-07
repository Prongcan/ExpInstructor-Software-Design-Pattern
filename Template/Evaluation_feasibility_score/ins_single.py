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
    create_feasibility_score_evaluator
)
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_feasibility_score import generate_feasibility_score

try:
    # Try relative import first (when imported as module)
    from .ins_model import create_custom_agent, build_agent_user_prompt
except ImportError:
    # Fall back to absolute import (when run directly)
    from ins_model import create_custom_agent, build_agent_user_prompt

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using InstructorEvaluationTemplate
# ==============================================================================

def generate_novelty_evaluation_via_agent(agent, idea_text: str) -> str:
    """
    Generate feasibility score evaluation using Agent.
    Refactored with Template Method Pattern: Uses unified InstructorEvaluationTemplate.
    
    Note: Function name kept as 'novelty' for backward compatibility, 
    but actually performs feasibility_score evaluation.
    """
    evaluator = InstructorEvaluationTemplate("feasibility_score")
    return evaluator.generate_evaluation_via_agent(agent, idea_text)

def generate_novelty_evaluation(idea_text: str) -> str:
    """
    Generate feasibility score evaluation for an idea.
    Refactored with Template Method Pattern: Uses unified API.
    
    Note: Function name kept as 'novelty' for backward compatibility,
    but actually performs feasibility_score evaluation.
    """
    return generate_agent_evaluation(idea_text, "feasibility_score")

def main() -> str:
    """
    Main function for feasibility score evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/2] Generating feasibility evaluation text ...")
    # Use Template Method Pattern for generation
    result = generate_agent_evaluation(raw_idea, "feasibility_score")
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
    
    return result

if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 60)
    print("Feasibility score evaluation completed!")
    print("=" * 60)
    print("=" * 60)
