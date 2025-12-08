"""
Feasibility Instructor Evaluator - Concrete implementation for feasibility evaluation.
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

from .abstract.ins_evaluation_template import InstructorEvaluationTemplate


class FeasibilityInstructorEvaluator(InstructorEvaluationTemplate):
    """
    Concrete Instructor evaluator for feasibility assessment.
    Only overrides the parts that differ from other evaluation types.
    """
    
    def __init__(self):
        """Initialize feasibility instructor evaluator."""
        super().__init__("feasibility")
    
    def get_evaluation_prompt(self) -> str:
        """Get feasibility-specific evaluation prompt."""
        return """
You are an expert academic reviewer specializing in research feasibility assessment.

Task: Evaluate the feasibility of the following research idea and provide a comprehensive assessment.

Research Idea:
{raw_idea}

Please provide a detailed feasibility evaluation covering:
1. **Technical Feasibility**: Can this research be technically implemented with current technology?
2. **Resource Requirements**: What resources (time, funding, equipment, personnel) would be needed?
3. **Methodological Feasibility**: Are the proposed methods and approaches practically viable?
4. **Data Availability**: Is the required data accessible and available for this research?
5. **Timeline Assessment**: Is the research timeline realistic and achievable?
6. **Risk Analysis**: What are the main risks and challenges that could affect feasibility?
7. **Infrastructure Needs**: What infrastructure or facilities would be required?
8. **Expertise Requirements**: What level of expertise and skills are needed to execute this research?

Please provide a thorough, professional assessment focusing on the feasibility aspects of this research idea.
"""
    
    def initialize_agent(self):
        """Initialize feasibility-specific agent."""
        from Evaluation.Evaluation_feasibility.ins_model import create_custom_agent
        return create_custom_agent()
    
    def build_agent_prompt(self, idea_text: str) -> str:
        """Build feasibility-specific agent prompt."""
        try:
            from Evaluation.Evaluation_feasibility.ins_model import build_agent_user_prompt
            return build_agent_user_prompt(idea_text)
        except ImportError:
            return self.get_evaluation_prompt().format(raw_idea=idea_text)
    
    def process_result(self, raw_response: str) -> t.List[str]:
        """Process feasibility evaluation result into concerns list."""
        if not raw_response or not isinstance(raw_response, str):
            return []
        
        try:
            # First try to parse directly
            if raw_response.strip().startswith('[') and raw_response.strip().endswith(']'):
                return json.loads(raw_response.strip())
            
            # Try to find JSON array in the result text
            import re
            json_match = re.search(r'\[.*?\]', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback: split by lines and clean up
        lines = raw_response.strip().split('\n')
        concerns = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                # Remove common prefixes
                import re
                line = re.sub(r'^[-*•]\s*', '', line)
                line = re.sub(r'^\d+\.\s*', '', line)
                concerns.append(line)
        
        return concerns[:12]  # Limit to 12 concerns
    
    def handle_error(self, error: Exception) -> t.List[str]:
        """Handle feasibility evaluation errors."""
        return []
