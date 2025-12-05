import os
import sys
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use unified RAGEvaluationTemplate
from Evaluation_utils.rag_evaluation_template import (
    RAGEvaluationTemplate,
    generate_rag_evaluation,
    create_novelty_evaluator
)
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_novelty import generate_novelty_score

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using RAGEvaluationTemplate
# ==============================================================================

def rag_pipeline_with_retrieval_system(user_query: str, embeddings_dir: str, retrieval_system=None) -> str:
    """
    Generate novelty evaluation using RAG pipeline.
    Refactored with Template Method Pattern: Uses unified RAGEvaluationTemplate.
    """
    evaluator = RAGEvaluationTemplate("novelty", embeddings_dir)
    return evaluator.generate_rag_evaluation(user_query)

def generate_novelty_evaluation(idea_text: str, embeddings_dir: str, retrieval_system=None) -> str:
    """
    Generate novelty evaluation using RAG.
    Refactored with Template Method Pattern: Uses unified API.
    """
    return generate_rag_evaluation(idea_text, "novelty", embeddings_dir)

def main() -> str:
    """
    Main function for RAG novelty evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    embeddings_dir = 'RAG_baseline_review_sentence'
    print("\n[1/2] Using RAG pipeline to generate novelty evaluation ...")
    # Use Template Method Pattern for generation
    novelty_result = generate_rag_evaluation(raw_idea, "novelty", embeddings_dir)

    # Use GPT to score the evaluation result - Differentiated functionality
    print("\n[2/2] Using GPT model to evaluate score ...")
    gpt_score_result = generate_novelty_score(novelty_result)
    if gpt_score_result and not gpt_score_result.startswith("ERROR"):
        print(f"\nGPT scoring result:")
        print(gpt_score_result)
    else:
        print("GPT scoring failed")
    
    return novelty_result

if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 60)
    print("RAG novelty evaluation completed!")
    print("=" * 60)
