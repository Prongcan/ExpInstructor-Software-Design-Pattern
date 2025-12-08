import os
import json
import time
import typing as t
import sys
from dataclasses import dataclass

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use concrete feasibility evaluator
from template.gpt_feasibility_evaluator import FeasibilityGPTEvaluator
from Evaluation_utils.test_idea import raw_idea, concerns
from Evaluation_utils.eval_feasibility import semantic_match_scores, compare_coverage_via_llm


def generate_concerns_for_idea(idea_text: str) -> t.Tuple[t.List[str], str]:
    """
    Generate concerns for feasibility evaluation.
    Refactored with Template Method Pattern: Now uses concrete FeasibilityGPTEvaluator.
    """
    # Refactored with Template Method Pattern: Use concrete evaluator subclass
    evaluator = FeasibilityGPTEvaluator()
    return evaluator.generate_evaluation(idea_text)


def main() -> None:
    """
    Main function for GPT feasibility evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/3] Generating LLM concerns ...")
    # Use Template Method Pattern for generation
    gen_concerns, raw_resp_idea = generate_concerns_for_idea(raw_idea)
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
