"""
RAG Novelty Evaluator - Concrete Implementation
Template Method Pattern: Concrete subclass for novelty evaluation using RAG.
"""

import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Template.abstract.rag_evaluation_template import RAGEvaluationTemplate


class NoveltyRAGEvaluator(RAGEvaluationTemplate):
    """
    Concrete RAG evaluator for novelty assessment.
    Template Method Pattern: Implements novelty-specific evaluation logic.
    """
    
    def __init__(self, embeddings_dir: str = 'Retrive_Generate', retrieval_system=None):
        """Initialize novelty RAG evaluator."""
        super().__init__("novelty", embeddings_dir, retrieval_system)
    
    def get_evaluation_prompt(self) -> str:
        """Get novelty-specific evaluation prompt."""
        return """You are a professional evaluator focusing on the novelty of the idea.
I will provide you with an academic idea. Your task is to evaluate only its level of innovation.
Please focus exclusively on the novelty and originality of the idea (analyze the problems of idea and the innovativeness of its methods) 
(how new, unique, or creative it is compared to existing research or conventional approaches in the field).
Your response should:
Be concise and academic in tone.
Avoid discussing feasibility, impact, or methodology.
Provide a clear judgment on the innovation level with your serious analysis and reasoning."""
    
    def process_result(self, content: str) -> str:
        """Process novelty evaluation result into text."""
        return self._validate_and_return_text(content)
    
    def handle_error(self, error: Exception) -> str:
        """Handle errors by returning error message."""
        return f"ERROR: Failed to generate novelty evaluation - {str(error)}"
    
    def _build_rag_prompt(self, idea_text: str, evidence_sentences: t.List[str]) -> str:
        """Build novelty-specific RAG prompt."""
        context = "\n\n".join(evidence_sentences)
        base_prompt = self.get_evaluation_prompt()
        
        prompt = (
            base_prompt
            + f"\n\nBelow are evidence sentences retrieved from reviews based on your query:\n\n{context}\n\n"
            + f"Please generate concerns based on these evidence sentences and your professional knowledge for the following question:\n{idea_text}\n\n"
            + "Output Policy (STRICT):\n"
            + "- Return a text evaluating innovation (which should include reasonable reasons) based on the evidence sentences.\n"
            + "- Please evaluate the innovativeness of the idea clearly and emphatically."
        )
        
        return prompt
