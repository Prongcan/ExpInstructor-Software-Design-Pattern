# bzy_modified: Example usage of EvaluationFacade
"""
Example demonstrating how to use the EvaluationFacade layer.

This shows the unified interface provided by the Facade pattern,
which coordinates all underlying design pattern layers.
"""

import sys
from pathlib import Path

# Setup path
PROJECT_ROOT = str(Path(__file__).parent.parent)
sys.path.insert(0, PROJECT_ROOT)

from core import EvaluationFacade, EvaluationInput, IdeaContext, BatchEvaluationInput
from core.data_models import EvaluationType, EvaluationMethod


def example_single_evaluation():
    """
    Example 1: Single idea evaluation using Facade.
    
    Demonstrates:
    - Creating an IdeaContext
    - Using Facade to evaluate feasibility, novelty, significance
    - Accessing results in unified format
    """
    print("=" * 80)
    print("Example 1: Single Idea Evaluation")
    print("=" * 80)
    
    # Initialize Facade
    facade = EvaluationFacade()
    
    # Create idea context
    idea = IdeaContext(
        idea_id="idea_001",
        title="Neural Prompt Optimization for Few-Shot Learning",
        description="""
        This work proposes a method to optimize neural prompts for few-shot learning tasks.
        The key innovation is using gradient-based optimization on prompt embeddings rather
        than discrete prompt text, enabling end-to-end training of prompt templates.
        
        The method combines:
        1. Continuous prompt embedding representation
        2. Gradient-based optimization through backpropagation
        3. Few-shot meta-learning framework
        
        We test on classification and NLI tasks, showing 3-5% improvement over discrete prompts.
        """,
        paper_id="2024_arxiv_12345",
        review_id="review_001"
    )
    
    print(f"\nIdea: {idea.title}")
    print(f"ID: {idea.idea_id}")
    
    # Example 1a: Evaluate feasibility
    print("\n--- Evaluating Feasibility ---")
    try:
        result = facade.evaluate_feasibility(idea, EvaluationMethod.INSTRUCTOR)
        if result.success:
            print(f"✓ Success")
            print(f"  Evaluation length: {len(result.evaluation_text)} chars")
            if result.coverage_analysis:
                print(f"  Coverage: {result.coverage_analysis['summary']}")
        else:
            print(f"✗ Failed: {result.error_message}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    # Example 1b: Evaluate novelty
    print("\n--- Evaluating Novelty ---")
    try:
        result = facade.evaluate_novelty(idea, EvaluationMethod.INSTRUCTOR)
        if result.success:
            print(f"✓ Success")
            print(f"  Evaluation length: {len(result.evaluation_text)} chars")
        else:
            print(f"✗ Failed: {result.error_message}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    # Example 1c: Evaluate significance
    print("\n--- Evaluating Significance ---")
    try:
        result = facade.evaluate_significance(idea, EvaluationMethod.INSTRUCTOR)
        if result.success:
            print(f"✓ Success")
            print(f"  Evaluation length: {len(result.evaluation_text)} chars")
        else:
            print(f"✗ Failed: {result.error_message}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    # Example 1d: Evaluate feasibility with score
    print("\n--- Evaluating Feasibility (with Score) ---")
    try:
        result = facade.evaluate_feasibility_score(idea, EvaluationMethod.INSTRUCTOR)
        if result.success:
            print(f"✓ Success")
            if result.score is not None:
                print(f"  Feasibility Score: {result.score}/10")
            else:
                print(f"  Score extraction failed (evaluation generated but no score)")
        else:
            print(f"✗ Failed: {result.error_message}")
    except Exception as e:
        print(f"  Exception: {e}")


def example_batch_evaluation():
    """
    Example 2: Batch evaluation of multiple ideas.
    
    Demonstrates:
    - Creating multiple IdeaContext objects
    - Using Facade for batch processing
    - Analyzing batch results
    """
    print("\n" + "=" * 80)
    print("Example 2: Batch Idea Evaluation")
    print("=" * 80)
    
    # Initialize Facade
    facade = EvaluationFacade()
    
    # Create multiple ideas
    ideas = [
        IdeaContext(
            idea_id="idea_batch_001",
            title="Multi-Modal Fusion for Dialogue Understanding",
            description="Proposes combining text, audio, and visual modalities for dialogue systems.",
            paper_id="2024_arxiv_001"
        ),
        IdeaContext(
            idea_id="idea_batch_002",
            title="Efficient Fine-tuning via Adapter Modules",
            description="Uses small adapter modules for efficient model fine-tuning on downstream tasks.",
            paper_id="2024_arxiv_002"
        ),
        IdeaContext(
            idea_id="idea_batch_003",
            title="Cross-Lingual Knowledge Transfer",
            description="Transfers knowledge across languages using multilingual embeddings.",
            paper_id="2024_arxiv_003"
        ),
    ]
    
    # Create batch input
    batch_input = BatchEvaluationInput(
        ideas=ideas,
        evaluation_type=EvaluationType.NOVELTY,
        evaluation_method=EvaluationMethod.INSTRUCTOR,
        batch_size=3
    )
    
    print(f"\nBatch Input:")
    print(f"  Total ideas: {len(batch_input.ideas)}")
    print(f"  Evaluation type: {batch_input.evaluation_type.value}")
    print(f"  Method: {batch_input.evaluation_method.value}")
    
    # Execute batch evaluation
    print("\n--- Executing Batch Evaluation ---")
    try:
        batch_result = facade.batch_evaluate(batch_input)
        
        print(f"\nBatch Results:")
        print(f"  Total executed: {len(batch_result.results)}")
        print(f"  Success: {batch_result.total_success}")
        print(f"  Failed: {batch_result.total_failed}")
        print(f"  Success rate: {batch_result.success_rate:.1f}%")
        print(f"  Execution time: {batch_result.execution_time_seconds:.2f}s")
        
        # Show per-idea results
        print(f"\nPer-idea Results:")
        for i, result in enumerate(batch_result.results, 1):
            status = "✓" if result.success else "✗"
            print(f"  {i}. {status} {result.evaluation_input.idea.idea_id}")
            if not result.success:
                print(f"     Error: {result.error_message}")
    
    except Exception as e:
        print(f"  Batch evaluation failed: {e}")


def example_custom_method():
    """
    Example 3: Using different evaluation methods (GPT, RAG, etc).
    
    Demonstrates:
    - Switching between different evaluation methods
    - Same Facade interface for all methods
    """
    print("\n" + "=" * 80)
    print("Example 3: Different Evaluation Methods")
    print("=" * 80)
    
    # Initialize Facade
    facade = EvaluationFacade()
    
    # Create idea
    idea = IdeaContext(
        idea_id="idea_method_test",
        title="Retrieval-Augmented Generation for Knowledge-Intensive Tasks",
        description="Combines dense and sparse retrieval for improved QA performance.",
        paper_id="2024_arxiv_999"
    )
    
    # Try different methods
    methods = [
        EvaluationMethod.INSTRUCTOR,
        EvaluationMethod.GPT,
        EvaluationMethod.RAG
    ]
    
    print(f"\nIdea: {idea.title}")
    print(f"\nTrying different evaluation methods:")
    
    for method in methods:
        print(f"\n  --- Method: {method.value} ---")
        try:
            result = facade.evaluate_feasibility(idea, method)
            if result.success:
                print(f"    ✓ Success")
                print(f"      Method: {result.metadata.get('method', 'unknown')}")
            else:
                print(f"    ✗ Failed: {result.error_message}")
        except Exception as e:
            print(f"    Exception: {e}")


def example_facade_architecture():
    """
    Example 4: Explain Facade architecture.
    
    Demonstrates the design pattern layers coordinated by Facade.
    """
    print("\n" + "=" * 80)
    print("Example 4: Facade Architecture Overview")
    print("=" * 80)
    
    print("""
    The EvaluationFacade coordinates multiple design pattern layers:
    
    Layer 5 (Facade - Unified Entry Point)
    │
    ├─→ Layer 3 (Template Method)
    │   ├─ InstructorEvaluationTemplate
    │   ├─ GPTEvaluationTemplate
    │   └─ RAGEvaluationTemplate
    │
    ├─→ Layer 4 (Strategy - Scoring)
    │   ├─ NoveltyScoringStrategy
    │   ├─ FeasibilityScoringStrategy
    │   └─ SignificanceScoringStrategy
    │
    ├─→ Layer 4 (Strategy - Coverage)
    │   ├─ LLMCoverageCompareStrategy
    │   └─ EmbeddingCoverageCompareStrategy
    │
    └─→ Layer 1 (Factory + Adapter)
        ├─ ChatFactory (creates LLM clients)
        └─ EmbeddingFactory (creates embedding clients)
    
    Benefits of Facade Pattern:
    1. Simplifies client interface - one EvaluationFacade instead of many classes
    2. Decouples clients from layer complexity
    3. Coordinates multiple design patterns transparently
    4. Enables layer evolution without changing external API
    5. Provides unified result format (EvaluationResult, BatchEvaluationResult)
    """)


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "EvaluationFacade Examples - Design Pattern Layer 5".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Run examples (comment out as needed)
    try:
        # example_single_evaluation()
        print("\n[SKIPPED] Example 1: Single evaluation (requires functional LLM clients)")
    except Exception as e:
        print(f"\nExample 1 error: {e}")
    
    try:
        # example_batch_evaluation()
        print("[SKIPPED] Example 2: Batch evaluation (requires functional LLM clients)")
    except Exception as e:
        print(f"\nExample 2 error: {e}")
    
    try:
        # example_custom_method()
        print("[SKIPPED] Example 3: Custom methods (requires functional LLM clients)")
    except Exception as e:
        print(f"\nExample 3 error: {e}")
    
    try:
        example_facade_architecture()
    except Exception as e:
        print(f"\nExample 4 error: {e}")
    
    print("\n" + "=" * 80)
    print("Note: Examples 1-3 are skipped to avoid API calls.")
    print("You can uncomment them to test with working LLM clients.")
    print("=" * 80 + "\n")
