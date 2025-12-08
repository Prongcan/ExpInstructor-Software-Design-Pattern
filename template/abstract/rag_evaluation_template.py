"""
RAG Evaluation Template using Template Method Pattern.
Abstract Base Class for RAG-based evaluations.

Defines the template method algorithm for RAG evaluation with abstract methods
that must be implemented by concrete subclasses for each evaluation type.
"""

import os
import sys
import json
import time
import typing as t
from abc import ABC, abstractmethod

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from service.llm_factory import get_chat_client
from RAG_baseline_review_sentence.retrieval_system import EvidenceRetrievalSystem


class RAGEvaluationTemplate(ABC):
    """
    Abstract base class for RAG-based evaluations.
    Template Method Pattern: Defines algorithm skeleton with abstract methods.
    """
    
    def __init__(self, evaluation_type: str, embeddings_dir: str = 'RAG_baseline_review_sentence'):
        """
        Initialize RAG evaluation template.
        Template Method Pattern: Common initialization logic.
        
        Args:
            evaluation_type: Type of evaluation ("feasibility", "novelty", "significance", "feasibility_score")
            embeddings_dir: Directory containing RAG embeddings
        """
   
        self.evaluation_type = evaluation_type.lower()
        self.embeddings_dir = embeddings_dir
        self._chat_client = get_chat_client()  # Factory Method Pattern
        self._retrieval_system = None  # Lazy initialization
    
    # Abstract methods that must be implemented by concrete subclasses
    @abstractmethod
    def get_evaluation_prompt(self) -> str:
        """Get evaluation-specific prompt. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def process_result(self, content: str) -> t.Union[str, t.List[str]]:
        """Process evaluation result. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def handle_error(self, error: Exception) -> t.Union[str, t.List[str]]:
        """Handle evaluation errors. Must be implemented by subclasses."""
        pass
        
    def _initialize_retrieval_system(self):
        if self._retrieval_system is None:
            print("[🔧 Initializing] Evidence Retrieval System...")
            self._retrieval_system = EvidenceRetrievalSystem(self.embeddings_dir)
            
            # Display statistics
            stats = self._retrieval_system.get_statistics()
            print(f"[📊 Stats] Total evidence embeddings: {stats['total_embeddings']}, Papers: {stats['total_papers']}")
        
        return self._retrieval_system
    
    def generate_evaluation(self, idea_text: str) -> t.Union[str, t.List[str]]:
        """
        Template method defining the RAG evaluation algorithm.
        Template Method Pattern: Defines the skeleton of the algorithm.
        
        Args:
            idea_text: Research idea text to evaluate
            
        Returns:
            Evaluation result (format depends on concrete implementation)
        """
        try:
            # Step 1: Initialize retrieval system
            retrieval_system = self._initialize_retrieval_system()
            
            # Step 2: Extract keywords and retrieve evidence
            evidence_sentences = self._retrieve_evidence(idea_text, retrieval_system)
            
            # Step 3: Build evaluation prompt with evidence (uses abstract method)
            prompt = self._build_rag_prompt(idea_text, evidence_sentences)
            
            # Step 4: Generate evaluation using LLM
            content = self._chat_client.chat(prompt)
            
            # Step 5: Process result (delegated to concrete subclass)
            return self.process_result(content)
                
        except Exception as e:
            # Error handling (delegated to concrete subclass)
            return self.handle_error(e)
    
    def _get_keywords(self, idea_text: str) -> t.List[str]:
        """Extract search keywords from idea text. Refactored with Template Method Pattern."""
        system_prompt = (
            "You are a research idea evaluator. I will provide you with an academic idea, and you need to output 10 keywords for searching related evidence sentences.\n"
            "The output format should be a comma-separated list of keywords.\n"
            "Only return keywords, no explanations."
        )
        full_prompt = f"{system_prompt}\nAcademic Idea: {idea_text}"
        keywords_text = self._chat_client.chat(full_prompt)
        print(f"[🔍 Keywords] {keywords_text}")
        return [kw.strip() for kw in keywords_text.split(",") if kw.strip()]
    
    def _search_evidence_with_retrieval_system(self, keywords: t.List[str], retrieval_system, top_k=5) -> t.List[str]:
        """Search for evidence using retrieval system. Refactored with Template Method Pattern."""
        all_results = []
        
        for i, keyword in enumerate(keywords, 1):
            print(f"[🔍 Searching evidence] Keyword {i}/{len(keywords)}: '{keyword}'")
            
            try:
                # Semantic search using the retrieval system
                results = retrieval_system.cosine_similarity_search(keyword, top_k=top_k)
                
                keyword_results = []
                for result in results:
                    entry = f"📘 Paper ID: {result['paper_id']} | Review ID: {result['review_id']} | Similarity: {result['similarity']:.3f}\n"
                    entry += f"{result['evidence']}\n"
                    keyword_results.append(entry)
                
                all_results.extend(keyword_results)
                print(f"[📄 Found] {len(keyword_results)} evidence sentences for '{keyword}'")
                
                # Add a short delay to avoid potential rate limits
                if i < len(keywords):
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"[❌ Error] Failed to search '{keyword}': {e}")
                continue
        
        # Deduplicate (based on evidence_id)
        seen_evidence = set()
        unique_results = []
        for result in all_results:
            # Extract evidence_id (from Paper ID and Review ID combination)
            paper_id = result.split('|')[0].strip().replace('📘 Paper ID: ', '')
            review_id = result.split('|')[1].strip().replace('Review ID: ', '')
            evidence_id = f"{paper_id}_{review_id}"
            if evidence_id not in seen_evidence:
                seen_evidence.add(evidence_id)
                unique_results.append(result)
        
        print(f"[📊 Summary] Total: {len(all_results)} evidence sentences, Unique: {len(unique_results)} evidence sentences")
        return unique_results
    
    def _retrieve_evidence(self, idea_text: str, retrieval_system, max_attempts=10) -> t.List[str]:
        """Retrieve evidence with retry logic. Refactored with Template Method Pattern."""
        # Extract keywords
        keywords = self._get_keywords(idea_text)
        
        # Retrieve evidence results (loop until results found)
        attempt = 1
        
        while attempt <= max_attempts:
            evidence_sentences = self._search_evidence_with_retrieval_system(keywords, retrieval_system, top_k=5)
            print(f"[📚 Attempt {attempt}] Found {len(evidence_sentences)} evidence sentences:")
            
            if len(evidence_sentences) > 0:
                # Found results, output evidence information
                for i, evidence in enumerate(evidence_sentences, 1):
                    first_line = evidence.split('\n')[0]
                    print(f"  {i}. {first_line}")
                print()
                
                # Print retrieved results details
                print(f"\n{'='*80}")
                print("Retrieved Evidence Sentences Details")
                print(f"{'='*80}")
                for i, evidence in enumerate(evidence_sentences, 1):
                    print(f"\n--- Evidence {i} ---")
                    print(evidence)
                    print("-" * 50)
                
                return evidence_sentences
            else:
                # No results found, regenerate keywords
                print("  ⏳ No evidence sentences found, regenerating keywords...")
                keywords = self._get_keywords(idea_text)
                print(f"[🔍 Regenerated Keywords] {keywords}")
                attempt += 1
                
                if attempt <= max_attempts:
                    print(f"  🔄 Retrying... (attempt {attempt}/{max_attempts})")
                else:
                    print("  ❌ Max attempts reached, proceeding with empty results")
                    print()
                time.sleep(2)
        
        return []
    
    def _build_rag_prompt(self, idea_text: str, evidence_sentences: t.List[str]) -> str:
        """Build RAG evaluation prompt with evidence. Template Method Pattern."""
        context = "\n\n".join(evidence_sentences)
        base_prompt = self.get_evaluation_prompt()  # Use abstract method
        
        # Standard RAG prompt structure - subclasses can override if needed
        prompt = (
            f"{base_prompt}\n\n"
            f"Below are evidence sentences retrieved from reviews based on your query:\n\n{context}\n\n"
            f"Research Idea:\n{idea_text}\n\n"
            f"Please generate evaluation based on these evidence sentences and your professional knowledge."
        )
        
        return prompt
    
    def _extract_concerns_from_result(self, result: str) -> t.List[str]:
        """Extract concerns for feasibility evaluation. Refactored with Template Method Pattern."""
        if not result or not isinstance(result, str):
            return []
        
        try:
            # First try to parse directly
            if result.strip().startswith('[') and result.strip().endswith(']'):
                return json.loads(result.strip())
            
            # Try to find JSON array in the result text
            import re
            json_match = re.search(r'\[.*?\]', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback: split by lines and clean up
        lines = result.strip().split('\n')
        concerns = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                # Remove common prefixes
                line = re.sub(r'^[-*•]\s*', '', line)
                line = re.sub(r'^\d+\.\s*', '', line)
                concerns.append(line)
        
        return concerns[:12]  # Limit to 12 concerns as specified in prompt
    
    def _validate_and_return_text(self, result: str) -> str:
        """Validate and return evaluation text. Refactored with Template Method Pattern."""
        if not result or not isinstance(result, str):
            return f"ERROR: Invalid {self.evaluation_type} evaluation result"
        
        # Basic validation: result should be non-empty and meaningful
        if len(result.strip()) < 50:
            return f"ERROR: {self.evaluation_type.title()} evaluation too short or empty"
        
        return result.strip()


# ============= Factory Functions for Different Evaluation Types =============
# Refactored with Template Method Pattern: Factory functions to create specific RAG evaluators

def create_feasibility_evaluator(embeddings_dir: str = 'RAG_baseline_review_sentence') -> RAGEvaluationTemplate:
    """Create RAG feasibility evaluator. Refactored with Template Method Pattern."""
    return RAGEvaluationTemplate("feasibility", embeddings_dir)

def create_novelty_evaluator(embeddings_dir: str = 'RAG_baseline_review_sentence') -> RAGEvaluationTemplate:
    """Create RAG novelty evaluator. Refactored with Template Method Pattern."""
    return RAGEvaluationTemplate("novelty", embeddings_dir)

def create_significance_evaluator(embeddings_dir: str = 'RAG_baseline_review_sentence') -> RAGEvaluationTemplate:
    """Create RAG significance evaluator. Refactored with Template Method Pattern."""
    return RAGEvaluationTemplate("significance", embeddings_dir)

def create_feasibility_score_evaluator(embeddings_dir: str = 'RAG_baseline_review_sentence') -> RAGEvaluationTemplate:
    """Create RAG feasibility scoring evaluator. Refactored with Template Method Pattern."""
    return RAGEvaluationTemplate("feasibility_score", embeddings_dir)


# ============= Unified API Functions =============
# Refactored with Template Method Pattern: Unified API for all RAG evaluations

def generate_rag_evaluation(idea_text: str, evaluation_type: str, embeddings_dir: str = 'RAG_baseline_review_sentence') -> t.Union[str, t.List[str]]:
    """
    Unified RAG evaluation function.
    Refactored with Template Method Pattern: Single function replaces all individual generate_xxx_evaluation functions.
    
    Args:
        idea_text: Research idea text to evaluate
        evaluation_type: Type of evaluation ("feasibility", "novelty", "significance", "feasibility_score")
        embeddings_dir: Directory containing RAG embeddings
        
    Returns:
        For feasibility: List of concerns
        For others: Evaluation text string
    """
    evaluator = RAGEvaluationTemplate(evaluation_type, embeddings_dir)
    return evaluator.generate_rag_evaluation(idea_text)