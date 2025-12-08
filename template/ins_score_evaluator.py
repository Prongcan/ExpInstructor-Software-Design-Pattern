"""
Score Instructor Evaluator - Concrete implementation for feasibility score evaluation.
Only implements score-specific differences from the base template.
"""

import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from .abstract.ins_evaluation_template import InstructorEvaluationTemplate


class ScoreInstructorEvaluator(InstructorEvaluationTemplate):
    """
    Concrete Instructor evaluator for feasibility score assessment.
    Only overrides the parts that differ from other evaluation types.
    """
    
    def __init__(self):
        """Initialize score instructor evaluator."""
        super().__init__("feasibility_score")
    
    def get_evaluation_prompt(self) -> str:
        """Get feasibility score-specific evaluation prompt.""" 
        return """
You are an expert academic reviewer specializing in comprehensive research feasibility assessment.

Task: Evaluate the feasibility of the following research idea and provide a detailed scoring assessment.

Research Idea:
{raw_idea}

Please provide a comprehensive feasibility evaluation with detailed analysis and scoring.
"""
    
    def initialize_agent(self):
        """Initialize feasibility score-specific agent."""
        from Evaluation_feasibility_score.ins_model import create_custom_agent
        return create_custom_agent()
    
    def build_agent_prompt(self, idea_text: str) -> str:
        """Build feasibility score-specific agent prompt."""
        try:
            from Evaluation_feasibility_score.ins_model import build_agent_user_prompt
            return build_agent_user_prompt(idea_text)
        except ImportError:
            return self.get_evaluation_prompt().format(raw_idea=idea_text)
    
    def process_result(self, raw_response: str) -> str:
        """Process feasibility score evaluation result."""
        if not raw_response or not isinstance(raw_response, str):
            return f"ERROR: Invalid feasibility score evaluation result"
        
        # Basic validation: result should be non-empty and meaningful
        if len(raw_response.strip()) < 50:
            return f"ERROR: Feasibility score evaluation too short or empty"
        
        return raw_response.strip()
    
    def handle_error(self, error: Exception) -> str:
        """Handle feasibility score evaluation errors."""
        return f"ERROR: Failed to generate feasibility score evaluation - {str(error)}"
