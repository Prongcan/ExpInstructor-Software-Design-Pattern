"""
Score GPT Evaluator - Concrete implementation for feasibility score evaluation.
Only implements score-specific differences from the base template.
"""

import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from .abstract.gpt_evaluation_template import GPTEvaluationTemplate


class ScoreGPTEvaluator(GPTEvaluationTemplate):
    """
    Concrete GPT evaluator for feasibility score assessment.
    Only overrides the parts that differ from other evaluation types.
    """
    
    def __init__(self):
        """Initialize score GPT evaluator."""
        super().__init__("feasibility_score")
    
    def get_system_prompt(self) -> str:
        """Get feasibility score-specific system prompt."""
        return """You are an expert peer reviewer with extensive experience in research feasibility assessment. 
Your task is to provide a comprehensive feasibility evaluation of research ideas."""
    
    def get_task_instruction(self) -> str:
        """Get feasibility score-specific task instruction."""
        return "Write a comprehensive peer review evaluation text discussing the feasibility, implementation challenges, effectiveness, and any concerns about this idea. Write in a natural, flowing style as if you are providing feedback to the authors."
    
    def process_result(self, raw_response: str) -> str:
        """Process feasibility score evaluation result."""
        return raw_response
    
    def handle_error(self, error: Exception) -> str:
        """Handle feasibility score evaluation errors."""
        return f"ERROR: {error}"
