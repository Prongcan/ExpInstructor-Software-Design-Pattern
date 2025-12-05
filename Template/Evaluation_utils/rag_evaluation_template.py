"""
RAG Evaluation Template using Template Method Pattern.
Refactored with Template Method Pattern.

Unified template for all RAG-based evaluation single files.
Eliminates repetitive code across Evaluation_feasibility/RAG_single.py, 
Evaluation_novelty/RAG_single.py, Evaluation_significance/RAG_single.py, 
Evaluation_feasibility_score/RAG_single.py
"""

import os
import sys
import json
import time
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from service.llm_factory import get_chat_client
from RAG_baseline_review_sentence.retrieval_system import EvidenceRetrievalSystem


class RAGEvaluationTemplate:
    """
    Template class for RAG-based evaluations.
    Refactored with Template Method Pattern: Eliminates repetitive RAG evaluation code.
    """
    
    def __init__(self, evaluation_type: str, embeddings_dir: str = 'RAG_baseline_review_sentence'):
        """
        Initialize RAG evaluation template.
        Refactored with Template Method Pattern.
        
        Args:
            evaluation_type: Type of evaluation ("feasibility", "novelty", "significance", "feasibility_score")
            embeddings_dir: Directory containing RAG embeddings
        """
   
        self.evaluation_type = evaluation_type.lower()
        self.embeddings_dir = embeddings_dir
        self._chat_client = get_chat_client()  # Refactored with Factory Method Pattern
        self._retrieval_system = None  # Lazy initialization
        self._evaluation_prompts = self._get_evaluation_prompts()
        
    def _initialize_retrieval_system(self):
        if self._retrieval_system is None:
            print("[🔧 Initializing] Evidence Retrieval System...")
            self._retrieval_system = EvidenceRetrievalSystem(self.embeddings_dir)
            
            # Display statistics
            stats = self._retrieval_system.get_statistics()
            print(f"[📊 Stats] Total evidence embeddings: {stats['total_embeddings']}, Papers: {stats['total_papers']}")
        
        return self._retrieval_system
    
    def _get_evaluation_prompts(self) -> dict:
        """Get evaluation prompts for different evaluation types. Refactored with Template Method Pattern."""
        return {
            "feasibility": """You are a rigorous peer-reviewer.
Task: Critically evaluate the given idea/proposal and GENERATE potential 'concerns'
(risks, issues, limitations, feasibility doubts, missing evaluations, ethical/compliance risks).
Do NOT extract phrases from the text verbatim; instead, propose concerns based on your assessment.
Output Policy (STRICT):
- Return ONLY a JSON array of strings, starting with '[' and ending with ']'.
- Each item must be a single-line short sentence (no line breaks).
- Do NOT include any code fences, markdown, comments, labels, or extra text.
- No leading bullets, numbering, or trailing commas inside items.
- Aim for 8-12 high-quality, non-duplicative items covering: methodology, data, feasibility, evaluation, ethics/compliance, novelty, scalability.""",
            
            "novelty": """You are a professional evaluator focusing on the novelty of the idea.
I will provide you with an academic idea. Your task is to evaluate only its level of innovation.
Please focus exclusively on the novelty and originality of the idea (analyze the problems of idea and the innovativeness of its methods) 
(how new, unique, or creative it is compared to existing research or conventional approaches in the field).
Your response should:
Be concise and academic in tone.
Avoid discussing feasibility, impact, or methodology.
Provide a clear judgment on the innovation level with your serious analysis and reasoning.""",
            
            "significance": """You are a professional evaluator focusing on the **Significance** of the idea.
I will provide you with an academic idea. Your task is to evaluate only its level of **Significance**.
Please focus exclusively on the **importance and potential impact** of the idea (analyze the **magnitude of the problem** the idea addresses and the **value of the contribution** it makes to the field or to society).
(how important the problem is, how much the solution/finding contributes to the field's advancement, or its potential to lead to new research directions or practical applications).
Your response should:
Be concise and academic in tone.
Avoid discussing feasibility, innovation (novelty), or specific implementation methodology.
Provide a clear judgment on the significance level with your serious analysis and reasoning.""",
            
            "feasibility_score": """You are an expert peer reviewer specializing in research feasibility assessment.

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
        }
    
    def generate_rag_evaluation(self, idea_text: str) -> t.Union[str, t.List[str]]:
        """
        Generate evaluation using unified RAG template.
        Refactored with Template Method Pattern: Unified RAG generation logic for all evaluation types.
        
        Args:
            idea_text: Research idea text to evaluate
            
        Returns:
            For feasibility: List of concerns
            For others: Evaluation text string
        """
        try:
            # Step 1: Initialize retrieval system
            retrieval_system = self._initialize_retrieval_system()
            
            # Step 2: Extract keywords and retrieve evidence
            evidence_sentences = self._retrieve_evidence(idea_text, retrieval_system)
            
            # Step 3: Build evaluation prompt with evidence
            prompt = self._build_rag_prompt(idea_text, evidence_sentences)
            
            # Step 4: Generate evaluation using LLM
            content = self._chat_client.chat(prompt)
            
            # Step 5: Process result based on evaluation type
            if self.evaluation_type == "feasibility":
                return self._extract_concerns_from_result(content)
            else:
                return self._validate_and_return_text(content)
                
        except Exception as e:
            if self.evaluation_type == "feasibility":
                return []
            else:
                return f"ERROR: Failed to generate {self.evaluation_type} evaluation - {str(e)}"
    
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
        """Build RAG evaluation prompt with evidence. Refactored with Template Method Pattern."""
        context = "\n\n".join(evidence_sentences)
        base_prompt = self._evaluation_prompts[self.evaluation_type]
        
        if self.evaluation_type == "feasibility":
            prompt = (
                base_prompt
                + f"\n\nBelow are evidence sentences retrieved from reviews based on your query:\n\n{context}\n\n"
                + f"Please generate concerns based on these evidence sentences and your professional knowledge for the following question:\n{idea_text}\n\n"
                + "Return JSON array only."
            )
        elif self.evaluation_type == "novelty":
            prompt = (
                base_prompt
                + f"\n\nBelow are evidence sentences retrieved from reviews based on your query:\n{context}\n\n"
                + f"Please generate concerns based on these evidence sentences and your professional knowledge for the following question:\n{idea_text}\n\n"
                + "Output Policy (STRICT):\n"
                + "- Return a text evaluating innovation (which should include reasonable reasons) based on the evidence sentences.\n"
                + "- Please evaluate the innovativeness of the idea clearly and emphatically."
            )
        elif self.evaluation_type == "significance":
            prompt = (
                base_prompt
                + f"\n\nBelow are evidence sentences retrieved from reviews based on your query:\n{context}\n\n"
                + f"Please generate a significance evaluation based on these evidence sentences and your professional knowledge for the following question:\n{idea_text}\n\n"
                + "Output Policy (STRICT):\n"
                + "- Return a text evaluating **significance** (which should include reasonable reasons) based on the evidence sentences.\n"
                + "- Please evaluate the **significance** of the idea clearly and emphatically.\n\n"
                + 'Return a JSON object with a single key "significance_evaluation" containing the text.'
            )
        elif self.evaluation_type == "feasibility_score":
            prompt = (
                f"{base_prompt}\n\n"
                + f"Research Idea:\n{idea_text}\n\n"
                + f"Below are evidence sentences retrieved from reviews:\n{context}\n\n"
                + "Please provide a thorough, professional assessment focusing on the feasibility aspects."
            )
        else:
            # Fallback
            prompt = f"{base_prompt}\n\nIdea: {idea_text}\n\nEvidence:\n{context}"
        
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