"""
Novelty Instructor Evaluator - Concrete implementation for novelty evaluation.
Only implements novelty-specific differences from the base template.
"""

import os
import sys

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from .abstract.ins_evaluation_template import InstructorEvaluationTemplate


class NoveltyInstructorEvaluator(InstructorEvaluationTemplate):
    """
    Concrete Instructor evaluator for novelty assessment.
    Only overrides the parts that differ from other evaluation types.
    """
    
    def __init__(self):
        """Initialize novelty instructor evaluator."""
        super().__init__("novelty")
    
    def get_evaluation_prompt(self) -> str:
        """Get novelty-specific evaluation prompt."""
        return """
You are an expert academic reviewer specializing in research novelty assessment.

Task: Evaluate the novelty of the following research idea and provide a comprehensive assessment.

Research Idea:
{raw_idea}

Please provide a detailed novelty evaluation covering:
1. **Originality Assessment**: How original is this idea compared to existing work?
2. **Innovation Level**: What new insights, methods, or approaches does it introduce?
3. **Differentiation**: How does it differ from current state-of-the-art solutions?
4. **Creative Aspects**: What creative or unconventional elements does it contain?
5. **Knowledge Contribution**: What new knowledge would this research contribute to the field?
6. **Technical Novelty**: Are there novel technical approaches or methodologies?
7. **Conceptual Novelty**: Does it introduce new concepts or frameworks?
8. **Practical Novelty**: Are there novel applications or use cases?

Please provide a thorough, professional assessment focusing on the novelty aspects of this research idea.
"""
    
    def initialize_agent(self):
        """Initialize novelty-specific agent."""
        from Evaluation.Evaluation_novelty.ins_model import create_custom_agent
        return create_custom_agent()
    
    def build_agent_prompt(self, idea_text: str) -> str:
        """Build novelty-specific agent prompt."""
        try:
            from Evaluation.Evaluation_novelty.ins_model import build_agent_user_prompt
            return build_agent_user_prompt(idea_text)
        except ImportError:
            return self.get_evaluation_prompt().format(raw_idea=idea_text)
    
    def process_result(self, raw_response: str) -> str:
        """Process novelty evaluation result."""
        if not raw_response or not isinstance(raw_response, str):
            return f"ERROR: Invalid novelty evaluation result"
        
        # Basic validation: result should be non-empty and meaningful
        if len(raw_response.strip()) < 50:
            return f"ERROR: Novelty evaluation too short or empty"
        
        return raw_response.strip()
    
    def handle_error(self, error: Exception) -> str:
        """Handle novelty evaluation errors."""
        return f"ERROR: Failed to generate novelty evaluation - {str(error)}"
