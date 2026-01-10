"""
GPT-based feasibility evaluation flow using Template Method Pattern.
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
from service.llm_factory import get_chat_client


class GPTFeasibilityEvaluationFlow(BaseEvaluationFlow):
    """
    GPT-based feasibility evaluation flow implementation.
    Refactored with Template Method Pattern.
    """
    
    def __init__(self):
        super().__init__()
        self._chat_client = get_chat_client()  # Refactored with Factory Method Pattern
        self._system_prompt = """
You are a rigorous peer-reviewer.
Task: Critically evaluate the given idea/proposal and GENERATE potential 'concerns' of feasibility
(feasibility, feasibility doubts, missing evaluations).
Do NOT extract phrases from the text verbatim; instead, propose concerns based on your assessment.
Output Policy (STRICT):
- Return ONLY a JSON array of strings, starting with '[' and ending with ']'.
- Each item must be a single-line short sentence (no line breaks).
- Do NOT include any code fences, markdown, comments, labels, or extra text.
- No leading bullets, numbering, or trailing commas inside items.
- Aim for 8-12 high-quality, non-duplicative items covering: feasibility, feasibility doubts, missing evaluations.
"""
    
    def get_evaluation_type(self) -> str:
        """Return the evaluation type."""
        return "GPT Feasibility"
    
    def create_agent(self):
        """GPT doesn't need an agent, return the chat client."""
        return self._chat_client
    
    def build_prompt(self, idea_text: str) -> str:
        """Build the evaluation prompt for GPT-based feasibility assessment."""
        return (
            self._system_prompt
            + "\n\n"
            + "Idea to review:\n\n"
            + idea_text.strip()
            + "\n\nReturn JSON array only."
        )
    
    def execute_agent_evaluation(self, agent, prompt: str, idea_text: str) -> str:
        """
        Override the agent execution for GPT-based evaluation.
        Refactored with Template Method Pattern.
        """
        print("=" * 80)
        print("Starting GPT evaluation process")
        print("=" * 80)
        
        try:
            content = agent.chat(prompt)  # Refactored with Factory Method Pattern
            print(f"GPT Response: {content}")
            return content
        except Exception as e:
            error_msg = f"ERROR: GPT evaluation failed: {str(e)}"
            print(error_msg)
            return error_msg
    
    def process_evaluation_result(self, evaluation_result: str) -> t.List[str]:
        """
        Process the GPT response into a list of concerns.
        Refactored with Template Method Pattern.
        """
        if evaluation_result.startswith("ERROR"):
            return []
        
        return self._extract_json_from_gpt_response(evaluation_result)
    
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
        Format the final GPT feasibility evaluation result.
        Refactored with Template Method Pattern.
        """
        result = {
            "evaluation_type": "gpt_feasibility",
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
        """Custom preprocessing for GPT feasibility evaluation."""
        print("[1/3] Generate concerns via GPT ...")
    
    def should_print_detailed_logs(self) -> bool:
        """GPT evaluation doesn't need detailed logs."""
        return False
    
    def _extract_json_from_gpt_response(self, text: str) -> t.List[str]:
        """
        Extract JSON array from GPT response with fallback parsing.
        """
        # Try to parse as direct JSON first
        try:
            result = json.loads(text.strip())
            if isinstance(result, list):
                return [str(item).strip() for item in result if str(item).strip()]
        except json.JSONDecodeError:
            pass
        
        # Look for JSON array pattern
        json_match = re.search(r'\[([^\]]*(?:\][^\]]*)*)\]', text)
        if json_match:
            try:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                if isinstance(result, list):
                    return [str(item).strip() for item in result if str(item).strip()]
            except json.JSONDecodeError:
                pass
        
        # Fallback: extract lines that look like list items
        return self._fallback_parse_list(text)
    
    def _fallback_parse_list(self, text: str) -> t.List[str]:
        """Fallback parsing for non-JSON responses."""
        lines = [ln.strip(" -*\t") for ln in text.splitlines()]
        items = [ln for ln in lines if ln and not ln.startswith(('```', 'json'))]
        return items[:12]  # Limit to reasonable number


def main() -> None:
    """
    Main function using Template Method Pattern for GPT evaluation.
    Refactored with Template Method Pattern.
    """
    from Evaluation_utils.test_idea import raw_idea
    
    # Use the template method pattern with GPT
    flow = GPTFeasibilityEvaluationFlow()
    result = flow.run(raw_idea)
    
    # Return result for potential further processing
    return result


if __name__ == "__main__":
    main()
