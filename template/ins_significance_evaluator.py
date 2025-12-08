"""
Significance Instructor Evaluator - Concrete implementation for significance evaluation.
Only implements significance-specific differences from the base template.
"""

import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from .abstract.ins_evaluation_template import InstructorEvaluationTemplate


class SignificanceInstructorEvaluator(InstructorEvaluationTemplate):
    """
    Concrete Instructor evaluator for significance assessment.
    Only overrides the parts that differ from other evaluation types.
    """
    
    def __init__(self):
        """Initialize significance instructor evaluator."""
        super().__init__("significance")
    
    def get_evaluation_prompt(self) -> str:
        """Get significance-specific evaluation prompt."""
        return """
You are an expert academic reviewer specializing in research significance assessment.

Task: Evaluate the significance of the following research idea and provide a comprehensive assessment.

Research Idea:
{raw_idea}

Please provide a detailed significance evaluation covering:
1. **Impact Assessment**: What potential impact could this research have on the field?
2. **Scientific Importance**: How important is this research for advancing scientific knowledge?
3. **Practical Significance**: What practical applications or real-world benefits could result?
4. **Theoretical Contribution**: How significant is the theoretical advancement this research offers?
5. **Societal Impact**: What broader societal implications or benefits might this research have?
6. **Economic Significance**: Are there potential economic benefits or commercial applications?
7. **Long-term Value**: What is the long-term significance and lasting value of this research?
8. **Field Advancement**: How much could this research advance or transform the field?

Please provide a thorough, professional assessment focusing on the significance aspects of this research idea.
"""
    
    def initialize_agent(self):
        """Initialize significance-specific agent."""
        from Evaluation_significance.ins_model import create_custom_agent
        return create_custom_agent()
    
    def build_agent_prompt(self, idea_text: str) -> str:
        """Build significance-specific agent prompt."""
        try:
            from Evaluation_significance.ins_model import build_agent_user_prompt
            return build_agent_user_prompt(idea_text)
        except ImportError:
            return self.get_evaluation_prompt().format(raw_idea=idea_text)
    
    def process_result(self, raw_response: str) -> str:
        """Process significance evaluation result."""
        if not raw_response or not isinstance(raw_response, str):
            return f"ERROR: Invalid significance evaluation result"
        
        # Basic validation: result should be non-empty and meaningful
        if len(raw_response.strip()) < 50:
            return f"ERROR: Significance evaluation too short or empty"
        
        return raw_response.strip()
    
    def handle_error(self, error: Exception) -> str:
        """Handle significance evaluation errors."""
        return f"ERROR: Failed to generate significance evaluation - {str(error)}"
