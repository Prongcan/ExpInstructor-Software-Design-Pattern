import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use concrete RAG evaluator
from template.rag_significance_evaluator import SignificanceRAGEvaluator
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_significance import generate_significance_score

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using RAGEvaluationTemplate
# ==============================================================================

def rag_pipeline_with_retrieval_system(user_query: str, embeddings_dir: str, retrieval_system=None) -> str:
    """
    Generate significance evaluation using RAG pipeline.
    Refactored with Template Method Pattern: Uses concrete SignificanceRAGEvaluator.
    """
    evaluator = SignificanceRAGEvaluator(embeddings_dir)
    return evaluator.generate_evaluation(user_query)

def generate_significance_evaluation(idea_text: str, embeddings_dir: str, retrieval_system=None) -> str:
    """
    Generate significance evaluation using RAG.
    Refactored with Template Method Pattern: Uses concrete evaluator.
    """
    evaluator = SignificanceRAGEvaluator(embeddings_dir)
    return evaluator.generate_evaluation(idea_text)

def main() -> str:
    """
    Main function for RAG significance evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    embeddings_dir = 'RAG_baseline_review_sentence'
    print("\n[1/2] Generating significance evaluation using RAG process...")
    # Use Template Method Pattern for generation
    evaluator = SignificanceRAGEvaluator(embeddings_dir)
    significance_result = evaluator.generate_evaluation(raw_idea)

    # Use GPT to score the evaluation result - Differentiated functionality
    print("\n[2/2] Using GPT model to evaluate score...")
    gpt_score_result = generate_significance_score(significance_result)
    if gpt_score_result and not gpt_score_result.startswith("ERROR"):
        print(f"\nGPT score result:")
        print(gpt_score_result)
    else:
        print("GPT scoring failed")
    
    return significance_result

if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 60)
    print("RAG significance evaluation completed!")
    print("=" * 60)
