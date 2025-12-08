import os
import sys
import json
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use concrete RAG evaluator
from template.rag_feasibility_evaluator import FeasibilityRAGEvaluator
from Evaluation_utils.test_idea import raw_idea, concerns
from Evaluation_utils.eval_feasibility import semantic_match_scores, compare_coverage_via_llm

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using RAGEvaluationTemplate
# ==============================================================================

def rag_pipeline_with_retrieval_system(user_query: str, embeddings_dir: str, retrieval_system=None) -> t.List[str]:
    """
    Generate feasibility concerns using RAG pipeline.
    Refactored with Template Method Pattern: Uses concrete FeasibilityRAGEvaluator.
    """
    evaluator = FeasibilityRAGEvaluator(embeddings_dir)
    return evaluator.generate_evaluation(user_query)

def generate_feasibility_evaluation(idea_text: str, embeddings_dir: str, retrieval_system=None) -> t.List[str]:
    """
    Generate feasibility concerns using RAG.
    Refactored with Template Method Pattern: Uses concrete evaluator.
    """
    evaluator = FeasibilityRAGEvaluator(embeddings_dir)
    return evaluator.generate_evaluation(idea_text)

def main():
    """
    Main function for RAG feasibility evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    print("[1/3] Generating LLM concerns (using Evidence Retrieval System) ...") 
    # Set embeddings directory
    embeddings_dir = 'RAG_baseline_review_sentence'
    
    # Use Template Method Pattern for generation
    evaluator = FeasibilityRAGEvaluator(embeddings_dir)
    gen_concerns = evaluator.generate_evaluation(raw_idea)
    print(f"Generated count: {len(gen_concerns)}")
    print(gen_concerns)

    print("[2/3] Semantic vector matching evaluation ...")
    # Differentiated functionality: semantic matching evaluation
    semantic_result = semantic_match_scores(concerns, gen_concerns)
    print(json.dumps({
        "generated_concerns": gen_concerns,
        "semantic_match": semantic_result
    }, ensure_ascii=False, indent=2))

    print("[3/3] Original concern comparison ...")
    # Differentiated functionality: LLM-based coverage comparison
    final = compare_coverage_via_llm(concerns, gen_concerns)
    print(final)

if __name__ == "__main__":
    main()
