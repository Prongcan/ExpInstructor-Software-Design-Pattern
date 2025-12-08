"""
RAG Feasibility Evaluator - Concrete Implementation
Template Method Pattern: Concrete subclass for feasibility evaluation using RAG.
"""

import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Template.abstract.rag_evaluation_template import RAGEvaluationTemplate


class FeasibilityRAGEvaluator(RAGEvaluationTemplate):
    """
    Concrete RAG evaluator for feasibility assessment.
    Template Method Pattern: Implements feasibility-specific evaluation logic.
    """
    
    def __init__(self, embeddings_dir: str = 'Retrive_Generate', retrieval_system=None):
        """Initialize feasibility RAG evaluator."""
        super().__init__("feasibility", embeddings_dir, retrieval_system)
    
    def get_evaluation_prompt(self) -> str:
        """Get feasibility-specific evaluation prompt."""
        return """You are a rigorous peer-reviewer.
Task: Critically evaluate the given idea/proposal and GENERATE potential 'concerns'
(risks, issues, limitations, feasibility doubts, missing evaluations, ethical/compliance risks).
Do NOT extract phrases from the text verbatim; instead, propose concerns based on your assessment.
Output Policy (STRICT):
- Return ONLY a JSON array of strings, starting with '[' and ending with ']'.
- Each item must be a single-line short sentence (no line breaks).
- Do NOT include any code fences, markdown, comments, labels, or extra text.
- No leading bullets, numbering, or trailing commas inside items.
- Aim for 8-12 high-quality, non-duplicative items covering: methodology, data, feasibility, evaluation, ethics/compliance, novelty, scalability."""
    
    def process_result(self, content: str) -> t.List[str]:
        """Process feasibility evaluation result into concerns list."""
        return self._extract_concerns_from_result(content)
    
    def handle_error(self, error: Exception) -> t.List[str]:
        """Handle errors by returning empty list."""
        print(f"ERROR in feasibility evaluation: {str(error)}")
        return []
    
    def _build_rag_prompt(self, idea_text: str, evidence_sentences: t.List[str]) -> str:
        """Build feasibility-specific RAG prompt."""
        context = "\n\n".join(evidence_sentences)
        base_prompt = self.get_evaluation_prompt()
        
        prompt = (
            base_prompt
            + f"\n\nBelow are evidence sentences retrieved from reviews based on your query:\n\n{context}\n\n"
            + f"Please generate concerns based on these evidence sentences and your professional knowledge for the following question:\n{idea_text}\n\n"
            + "Return JSON array only."
        )
        
        return prompt
