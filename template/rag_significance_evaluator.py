"""
RAG Significance Evaluator - Concrete Implementation
Template Method Pattern: Concrete subclass for significance evaluation using RAG.
"""

import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from template.abstract.rag_evaluation_template import RAGEvaluationTemplate


class SignificanceRAGEvaluator(RAGEvaluationTemplate):
    """
    Concrete RAG evaluator for significance assessment.
    Template Method Pattern: Implements significance-specific evaluation logic.
    """
    
    def __init__(self, embeddings_dir: str = 'RAG_baseline_review_sentence'):
        """Initialize significance RAG evaluator."""
        super().__init__("significance", embeddings_dir)
    
    def get_evaluation_prompt(self) -> str:
        """Get significance-specific evaluation prompt."""
        return """You are a professional evaluator focusing on the **Significance** of the idea.
I will provide you with an academic idea. Your task is to evaluate only its level of **Significance**.
Please focus exclusively on the **importance and potential impact** of the idea (analyze the **magnitude of the problem** the idea addresses and the **value of the contribution** it makes to the field or to society).
(how important the problem is, how much the solution/finding contributes to the field's advancement, or its potential to lead to new research directions or practical applications).
Your response should:
Be concise and academic in tone.
Avoid discussing feasibility, innovation (novelty), or specific implementation methodology.
Provide a clear judgment on the significance level with your serious analysis and reasoning."""
    
    def process_result(self, content: str) -> str:
        """Process significance evaluation result as text."""
        return self._validate_and_return_text(content)
    
    def handle_error(self, error: Exception) -> str:
        """Handle errors by returning error message."""
        return f"ERROR: Failed to generate significance evaluation - {str(error)}"
    
    def _build_rag_prompt(self, idea_text: str, evidence_sentences: t.List[str]) -> str:
        """Build significance-specific RAG prompt."""
        context = "\n\n".join(evidence_sentences)
        base_prompt = self.get_evaluation_prompt()
        
        prompt = (
            base_prompt
            + f"\n\nBelow are evidence sentences retrieved from reviews based on your query:\n\n{context}\n\n"
            + f"Please generate a significance evaluation based on these evidence sentences and your professional knowledge for the following question:\n{idea_text}\n\n"
            + "Output Policy (STRICT):\n"
            + "- Return a text evaluating **significance** (which should include reasonable reasons) based on the evidence sentences.\n"
            + "- Please evaluate the **significance** of the idea clearly and emphatically.\n\n"
            + 'Return a JSON object with a single key "significance_evaluation" containing the text.'
        )
        
        return prompt
