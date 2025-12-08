"""
Novelty GPT Evaluator - Concrete implementation for novelty evaluation.
Inherits from GPTEvaluationTemplate and customizes novelty-specific behavior.
"""

import os
import sys

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from .abstract.gpt_evaluation_template import GPTEvaluationTemplate


class NoveltyGPTEvaluator(GPTEvaluationTemplate):
    """
    Concrete GPT evaluator for novelty assessment.
    Specializes in evaluating innovation and originality.
    """
    
    def __init__(self):
        """Initialize novelty GPT evaluator."""
        super().__init__("novelty")
    
    def get_system_prompt(self) -> str:
        """Get novelty-specific system prompt."""
        return """You are a professional evaluator focusing on the novelty of the idea.
I will provide you with an academic idea. Your task is to evaluate only its level of novelty.
Please focus exclusively on the originality and innovation of the idea — how new, creative, or unprecedented it is compared to existing research or conventional approaches in the field.
Your response should:
Be concise and academic in tone.
Avoid discussing feasibility, significance, or methodology.
Provide a clear judgment on the novelty level with your serious analysis and reasoning."""
    
    def get_task_instruction(self) -> str:
        """Get novelty-specific task instruction."""
        return "Return a text evaluating novelty (which should include reasonable reasons)."
    
    def process_result(self, raw_response: str) -> str:
        """Process novelty evaluation result."""
        if not raw_response or not isinstance(raw_response, str):
            return "ERROR: Invalid novelty evaluation result"
        
        # Basic validation: result should be non-empty and meaningful
        if len(raw_response.strip()) < 50:
            return "ERROR: Novelty evaluation too short or empty"
        
        return raw_response.strip()
    
    def handle_error(self, error: Exception) -> str:
        """Handle novelty evaluation errors."""
        return f"ERROR: Failed to generate novelty evaluation - {str(error)}"
