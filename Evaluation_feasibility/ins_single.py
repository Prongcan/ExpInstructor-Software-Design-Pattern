import os
import sys
import json
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use concrete feasibility evaluator
from template.ins_feasibility_evaluator import FeasibilityInstructorEvaluator
from Evaluation_utils.test_idea import raw_idea, concerns

try:
    # Try relative import first (when imported as module)
    from .ins_model import create_custom_agent, build_agent_user_prompt
except ImportError:
    # Fall back to absolute import (when run directly)
    from ins_model import create_custom_agent, build_agent_user_prompt

from Evaluation_utils.eval_feasibility import semantic_match_scores, compare_coverage_via_llm

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using concrete FeasibilityInstructorEvaluator
# ==============================================================================

def generate_concerns_via_agent(agent, idea_text: str) -> t.List[str]:
    """
    Generate feasibility concerns using Agent.
    Refactored with Template Method Pattern: Uses concrete FeasibilityInstructorEvaluator.
    """
    evaluator = FeasibilityInstructorEvaluator()
    return evaluator.generate_evaluation_via_agent(agent, idea_text)

def generate_concerns_for_idea(idea_text: str) -> t.List[str]:
    """
    Generate feasibility concerns for an idea.
    Refactored with Template Method Pattern: Uses concrete evaluator.
    """
    evaluator = FeasibilityInstructorEvaluator()
    return evaluator.generate_evaluation(idea_text)

def main():
    """
    Main function for feasibility evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/3] Generating LLM concerns via Agent ...")
    # Use Template Method Pattern for generation
    gen_concerns = generate_concerns_for_idea(raw_idea)
    print(f"Generated count: {len(gen_concerns)}")
    print(gen_concerns)

    print("[2/3] Semantic vector matching evaluation ...")
    # Differentiated functionality: semantic matching evaluation
    semantic_result = semantic_match_scores(concerns, gen_concerns)
    print(json.dumps({
        "generated_concerns": gen_concerns,
        "semantic_match": semantic_result
    }, ensure_ascii=False, indent=2))

    print("[3/3] Original concern comparison ...")
    # Differentiated functionality: LLM-based coverage comparison
    final = compare_coverage_via_llm(concerns, gen_concerns)
    print(final)

if __name__ == "__main__":
    main()
