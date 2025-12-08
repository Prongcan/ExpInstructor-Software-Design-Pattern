"""
Significance GPT Evaluator - Concrete implementation for significance evaluation.
Only implements significance-specific differences from the base template.
"""

import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from .abstract.gpt_evaluation_template import GPTEvaluationTemplate


class SignificanceGPTEvaluator(GPTEvaluationTemplate):
    """
    Concrete GPT evaluator for significance assessment.
    Only overrides the parts that differ from other evaluation types.
    """
    
    def __init__(self):
        """Initialize significance GPT evaluator."""
        super().__init__("significance")
    
    def get_system_prompt(self) -> str:
        """Get significance-specific system prompt."""
        return """You are a professional evaluator focusing on the significance of the idea.
I will provide you with an academic idea. Your task is to evaluate only its level of significance.
Please focus exclusively on the importance, scope, and potential impact of the idea — how meaningful, influential, or valuable it would be compared to existing research or conventional approaches in the field.
Your response should:
Be concise and academic in tone.
Avoid discussing feasibility, novelty, or methodology.
Provide a clear judgment on the significance level with your serious analysis and reasoning."""
    
    def get_task_instruction(self) -> str:
        """Get significance-specific task instruction."""
        return "Return a text evaluating significance (which should include reasonable reasons)."
    
    def process_result(self, raw_response: str) -> str:
        """Process significance evaluation result."""
        return raw_response
    
    def handle_error(self, error: Exception) -> str:
        """Handle significance evaluation errors."""
        return f"ERROR: {error}"
