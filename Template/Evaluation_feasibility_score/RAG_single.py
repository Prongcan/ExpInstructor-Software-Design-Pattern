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
    create_feasibility_score_evaluator
)
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_feasibility_score import generate_feasibility_score

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using RAGEvaluationTemplate
# ==============================================================================

def rag_pipeline_with_retrieval_system(user_query: str, embeddings_dir: str, retrieval_system=None) -> str:
    """
    Generate feasibility score evaluation using RAG pipeline.
    Refactored with Template Method Pattern: Uses unified RAGEvaluationTemplate.
    """
    evaluator = RAGEvaluationTemplate("feasibility_score", embeddings_dir)
    return evaluator.generate_rag_evaluation(user_query)

def generate_feasibility_evaluation(idea_text: str, embeddings_dir: str, retrieval_system=None) -> str:
    """
    Generate feasibility score evaluation using RAG.
    Refactored with Template Method Pattern: Uses unified API.
    """
    return generate_rag_evaluation(idea_text, "feasibility_score", embeddings_dir)

def main() -> str:
    """
    Main function for RAG feasibility score evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    embeddings_dir = 'RAG_baseline_review_sentence'
    
    print("[1/2] Generating feasibility evaluation text ...")
    # Use Template Method Pattern for generation
    result = generate_rag_evaluation(raw_idea, "feasibility_score", embeddings_dir)
    print(result)
    
    # Use eval_feasibility_score.py to score the evaluation result - Differentiated functionality
    print("\n[2/2] Using eval_feasibility_score.py to evaluate score ...")
    
    # Directly use evaluation text (no formatting needed)
    score_result = generate_feasibility_score(result)
    if score_result and not score_result.startswith("ERROR"):
        print(f"\nScoring result:")
        print(score_result)
    else:
        print("Scoring failed")
    
    return result

if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 60)
    print("RAG feasibility score evaluation completed!")
    print("=" * 60)
