"""
Feasibility evaluation flow using Template Method Pattern.
Refactored with Template Method Pattern.
"""

import json
import re
import typing as t
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Evaluation_utils.base_evaluation_flow import BaseEvaluationFlow
from Evaluation_utils.eval_feasibility import semantic_match_scores, compare_coverage_via_llm
from Evaluation_utils.test_idea import concerns


class FeasibilityEvaluationFlow(BaseEvaluationFlow):
    """
    Feasibility evaluation flow implementation.
    Refactored with Template Method Pattern.
    """
    
    def get_evaluation_type(self) -> str:
        """Return the evaluation type."""
        return "Feasibility"
    
    def create_agent(self):
        """Create and return the agent instance."""
        # Import here to avoid circular dependency
        from Evaluation_feasibility.ins_model import create_custom_agent
        return create_custom_agent()
    
    def build_prompt(self, idea_text: str) -> str:
        """Build the evaluation prompt for feasibility assessment."""
        # Import here to avoid circular dependency
        from Evaluation_feasibility.ins_model import build_agent_user_prompt
        return build_agent_user_prompt(idea_text)
    
    def process_evaluation_result(self, evaluation_result: str) -> t.List[str]:
        """
        Process the raw evaluation result into a list of concerns.
        Refactored with Template Method Pattern.
        """
        if evaluation_result.startswith("ERROR"):
            return []
        
        return self._extract_first_json_array(evaluation_result)
    
    def perform_additional_scoring(self, processed_result: t.List[str], idea_text: str) -> t.Dict[str, t.Any]:
        """
        Perform semantic matching and coverage comparison.
        Refactored with Template Method Pattern.
        """
        print("[2/3] Semantic vector matching evaluation ...")
        
        # Semantic matching scores
        semantic_scores = semantic_match_scores(concerns, processed_result)
        
        print("[3/3] Original concern comparison ...")
        
        # Coverage comparison using LLM
        coverage_result = compare_coverage_via_llm(concerns, processed_result)
        
        return {
            "semantic_match": semantic_scores,
            "coverage_comparison": coverage_result
        }
    
    def format_final_result(self, processed_result: t.List[str], additional_scores: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """
        Format the final feasibility evaluation result.
        Refactored with Template Method Pattern.
        """
        result = {
            "evaluation_type": "feasibility",
            "generated_concerns": processed_result,
            "generated_count": len(processed_result),
            "semantic_match": additional_scores.get("semantic_match", {}),
            "coverage_comparison": additional_scores.get("coverage_comparison", "")
        }
        
        # Print formatted results for backward compatibility
        print(f"Generated count: {len(processed_result)}")
        print(json.dumps({
            "generated_concerns": processed_result,
            "semantic_match": additional_scores.get("semantic_match", {})
        }, ensure_ascii=False, indent=2))
        print(additional_scores.get("coverage_comparison", ""))
        
        return result
    
    def pre_execution_hook(self) -> None:
        """Custom preprocessing for feasibility evaluation."""
        print("[1/3] Generate concerns via Generator_v3 ...")
    
    def _extract_first_json_array(self, text: str) -> t.List[str]:
        """
        Extract the first JSON array from any text and parse it into a list of strings.
        Fault tolerance: return an empty list if extraction fails.
        """
        # 1) Directly find balanced [...]
        start = text.find("[")
        if start != -1:
            # Simple bracket counting
            depth = 0
            for i in range(start, len(text)):
                if text[i] == '[':
                    depth += 1
                elif text[i] == ']':
                    depth -= 1
                    if depth == 0:
                        try:
                            arr = json.loads(text[start:i+1])
                            if isinstance(arr, list):
                                return [str(x).strip() for x in arr if str(x).strip()]
                        except Exception:
                            pass
                        break

        # 2) Try to strip ```json ... ``` or ``` ... ``` blocks
        fence_match = re.search(r"```(?:json)?\n([\s\S]+?)```", text)
        if fence_match:
            inner = fence_match.group(1)
            return self._extract_first_json_array(inner)

        # 3) Fail and return empty list
        return []


def main() -> None:
    """
    Main function using Template Method Pattern.
    Refactored with Template Method Pattern.
    """
    from Evaluation_utils.test_idea import raw_idea
    
    # Use the template method pattern
    flow = FeasibilityEvaluationFlow()
    result = flow.run(raw_idea)
    
    # Return result for potential further processing
    return result


if __name__ == "__main__":
    main()
