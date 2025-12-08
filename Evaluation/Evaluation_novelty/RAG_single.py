import os
import sys

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use concrete RAG evaluator
from Template.rag_novelty_evaluator import NoveltyRAGEvaluator
from Evaluation_utils.test_idea import raw_idea
from Evaluation_utils.eval_novelty import generate_novelty_score

# ==============================================================================
# Refactored with Template Method Pattern: Unified functions using RAGEvaluationTemplate
# ==============================================================================

def rag_pipeline_with_retrieval_system(user_query: str, embeddings_dir: str, retrieval_system=None) -> str:
    """
    Generate novelty evaluation using RAG pipeline.
    Refactored with Template Method Pattern: Uses concrete NoveltyRAGEvaluator.
    """
    evaluator = NoveltyRAGEvaluator(embeddings_dir, retrieval_system=retrieval_system)
    return evaluator.generate_evaluation(user_query)

def generate_novelty_evaluation(idea_text: str, embeddings_dir: str, retrieval_system=None) -> str:
    """
    Generate novelty evaluation using RAG.
    Refactored with Template Method Pattern: Uses concrete evaluator.
    """
    evaluator = NoveltyRAGEvaluator(embeddings_dir, retrieval_system=retrieval_system)
    return evaluator.generate_evaluation(idea_text)

def main() -> str:
    """
    Main function for RAG novelty evaluation with complete workflow.
    Uses Template Method Pattern for generation + differentiated evaluation logic.
    """
    embeddings_dir = 'Retrive_Generate'
    print("\n[1/2] Using RAG pipeline to generate novelty evaluation ...")
    # Use Template Method Pattern for generation
    evaluator = NoveltyRAGEvaluator(embeddings_dir)
    novelty_result = evaluator.generate_evaluation(raw_idea)

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
