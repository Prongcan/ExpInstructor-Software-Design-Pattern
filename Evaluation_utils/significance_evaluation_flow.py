"""
Significance evaluation flow using Template Method Pattern.
Refactored with Template Method Pattern.
"""

import typing as t
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Evaluation_utils.base_evaluation_flow import BaseEvaluationFlow
from Evaluation_utils.eval_significance import generate_significance_score


class SignificanceEvaluationFlow(BaseEvaluationFlow):
    """
    Significance evaluation flow implementation.
    Refactored with Template Method Pattern.
    """
    
    def get_evaluation_type(self) -> str:
        """Return the evaluation type."""
        return "Significance"
    
    def create_agent(self):
        """Create and return the agent instance."""
        # Import here to avoid circular dependency
        from Evaluation_significance.ins_model import create_custom_agent
        return create_custom_agent()
    
    def build_prompt(self, idea_text: str) -> str:
        """Build the evaluation prompt for significance assessment."""
        # Import here to avoid circular dependency
        from Evaluation_significance.ins_model import build_agent_user_prompt
        return build_agent_user_prompt(idea_text)
    
    def process_evaluation_result(self, evaluation_result: str) -> str:
        """
        Process the raw evaluation result into structured format.
        Refactored with Template Method Pattern.
        """
        if evaluation_result.startswith("ERROR"):
            return evaluation_result
        
        if not evaluation_result or evaluation_result.strip() == "":
            return "ERROR: Agent did not return valid result"
        
        return evaluation_result
    
    def perform_additional_scoring(self, processed_result: str, idea_text: str) -> t.Dict[str, t.Any]:
        """
        Perform GPT-based significance scoring.
        Refactored with Template Method Pattern.
        """
        print("\n[2/3] Using GPT model to evaluate score ...")
        
        if processed_result.startswith("ERROR"):
            return {"gpt_score": "ERROR: Cannot score due to evaluation failure"}
        
        # Use existing significance scoring strategy
        gpt_score_result = generate_significance_score(processed_result)
        
        if gpt_score_result and not gpt_score_result.startswith("ERROR"):
            print(f"\nGPT scoring result:")
            print(gpt_score_result)
            return {"gpt_score": gpt_score_result}
        else:
            print("GPT scoring failed")
            return {"gpt_score": "ERROR: GPT scoring failed"}
    
    def format_final_result(self, processed_result: str, additional_scores: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """
        Format the final significance evaluation result.
        Refactored with Template Method Pattern.
        """
        result = {
            "evaluation_type": "significance",
            "evaluation_text": processed_result,
            "gpt_score": additional_scores.get("gpt_score", "Not available"),
            "status": "success" if not processed_result.startswith("ERROR") else "failed"
        }
        
        # Print results for backward compatibility
        if not processed_result.startswith("ERROR"):
            print(f"\nSignificance evaluation completed successfully:")
            print(processed_result)
        else:
            print(f"\nSignificance evaluation failed: {processed_result}")
        
        return result
    
    def pre_execution_hook(self) -> None:
        """Custom preprocessing for significance evaluation."""
        print("[1/3] Generating significance evaluation via Agent ...")


def main() -> None:
    """
    Main function using Template Method Pattern.
    Refactored with Template Method Pattern.
    """
    from Evaluation_utils.test_idea import raw_idea
    
    # Use the template method pattern
    flow = SignificanceEvaluationFlow()
    result = flow.run(raw_idea)
    
    # Return result for potential further processing
    return result


if __name__ == "__main__":
    main()
