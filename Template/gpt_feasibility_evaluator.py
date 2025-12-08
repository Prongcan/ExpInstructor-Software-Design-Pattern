"""
Feasibility GPT Evaluator - Concrete implementation for feasibility evaluation.
Only implements feasibility-specific differences from the base template.
"""

import os
import sys
import json
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from .abstract.gpt_evaluation_template import GPTEvaluationTemplate


class FeasibilityGPTEvaluator(GPTEvaluationTemplate):
    """
    Concrete GPT evaluator for feasibility assessment.
    Only overrides the parts that differ from other evaluation types.
    """
    
    def __init__(self):
        """Initialize feasibility GPT evaluator.""" 
        super().__init__("feasibility")
    
    def get_system_prompt(self) -> str:
        """Get feasibility-specific system prompt."""
        return """You are a rigorous peer-reviewer.
Task: Critically evaluate the given idea/proposal and GENERATE potential 'concerns' of feasibility
(feasibility, feasibility doubts, missing evaluations).
Do NOT extract phrases from the text verbatim; instead, propose concerns based on your assessment.
Output Policy (STRICT):
- Return ONLY a JSON array of strings, starting with '[' and ending with ']'.
- Each item must be a single-line short sentence (no line breaks).
- Do NOT include any code fences, markdown, comments, labels, or extra text.
- No leading bullets, numbering, or trailing commas inside items.
- Aim for 8-12 high-quality, non-duplicative items covering: feasibility, feasibility doubts, missing evaluations."""
    
    def get_task_instruction(self) -> str:
        """Get feasibility-specific task instruction."""
        return "Return JSON array only."
    
    def process_result(self, raw_response: str) -> t.Tuple[t.List[str], str]:
        """Process feasibility evaluation result into concerns list."""
        try:
            parsed = json.loads(raw_response)
            if isinstance(parsed, list):
                concerns_llm = [str(x).strip() for x in parsed if str(x).strip()]
                return concerns_llm, raw_response
            else:
                concerns_llm = self._fallback_parse_list(raw_response)
                return concerns_llm, raw_response
        except Exception:
            concerns_llm = self._fallback_parse_list(raw_response)
            return concerns_llm, raw_response
    
    def handle_error(self, error: Exception) -> t.Tuple[t.List[str], str]:
        """Handle feasibility evaluation errors."""
        return [], f"ERROR: {error}"
    
    def _fallback_parse_list(self, content: str) -> t.List[str]:
        """Fallback parsing for malformed JSON."""
        lines = content.strip().split('\n')
        concerns = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                # Remove common prefixes
                import re
                line = re.sub(r'^[-*•]\s*', '', line)
                line = re.sub(r'^\d+\.\s*', '', line)
                concerns.append(line)
        return concerns
