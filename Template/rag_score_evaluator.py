"""
RAG Feasibility Score Evaluator - Concrete Implementation
Template Method Pattern: Concrete subclass for feasibility score evaluation using RAG.
"""

import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Template.abstract.rag_evaluation_template import RAGEvaluationTemplate


class ScoreRAGEvaluator(RAGEvaluationTemplate):
    """
    Concrete RAG evaluator for feasibility score assessment.
    Template Method Pattern: Implements feasibility score-specific evaluation logic.
    """
    
    def __init__(self, embeddings_dir: str = 'Retrive_Generate', retrieval_system=None):
        """Initialize feasibility score RAG evaluator."""
        super().__init__("feasibility_score", embeddings_dir, retrieval_system)
    
    def get_evaluation_prompt(self) -> str:
        """Get feasibility score-specific evaluation prompt."""
        return """You are an expert peer reviewer specializing in research feasibility assessment.

Task: Evaluate the feasibility of the following research idea and provide a comprehensive assessment.

Please provide a detailed feasibility evaluation covering:
1. **Technical Feasibility**: Can this research be technically implemented with current technology?
2. **Resource Requirements**: What resources would be needed?
3. **Methodological Feasibility**: Are the proposed methods practically viable?
4. **Data Availability**: Is the required data accessible?
5. **Timeline Assessment**: Is the research timeline realistic?
6. **Risk Analysis**: What are the main risks and challenges?
7. **Infrastructure Needs**: What infrastructure would be required?
8. **Expertise Requirements**: What level of expertise is needed?

Please provide a thorough, professional assessment focusing on the feasibility aspects."""
    
    def process_result(self, content: str) -> str:
        """Process feasibility score evaluation result as text."""
        return self._validate_and_return_text(content)
    
    def handle_error(self, error: Exception) -> str:
        """Handle errors by returning error message."""
        return f"ERROR: Failed to generate feasibility score evaluation - {str(error)}"
