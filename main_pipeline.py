"""
ExpInstructor Unified Workflow Pipeline

This script demonstrates the complete workflow of the ExpInstructor system,
integrating the three main components via their Facades:
1. Knowledge Graph Construction (GraphConstructionFacade)
2. Retrieval & Scoring (RetrievalFacade)
3. Idea Evaluation (EvaluationFacade)
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core import (
    GraphConstructionFacade, GraphConstructionInput,
    RetrievalFacade, RetrievalInput, RetrievalType,
    EvaluationFacade, EvaluationInput, IdeaContext, 
    EvaluationMethod, EvaluationType
)

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("MainPipeline")

def main():
    print("\n" + "="*80)
    print("ExpInstructor Unified Workflow Pipeline")
    print("="*80)

    # ---------------------------------------------------------
    # Phase 1: Knowledge Graph Construction
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("Phase 1: Knowledge Graph Construction")
    print("="*40)
    
    # Sample Review Data (Simulating input from ICLR dataset)
    review_input = GraphConstructionInput(
        paper_id="ICLR_2024_DEMO",
        review_id="R1",
        review_content={
            "strengths": "The proposed Graph Neural Network architecture introduces a novel attention mechanism that significantly improves performance on dynamic graphs.",
            "weaknesses": "The evaluation lacks comparison with recent baselines like GraphSAGE and GATv2. The ablation study is insufficient.",
            "suggestions": "Include experiments on larger datasets (e.g., OGB) and compare with GraphSAGE. Add an ablation study on the attention head count."
        }
    )
    
    logger.info("Initializing GraphConstructionFacade...")
    graph_facade = GraphConstructionFacade()
    
    logger.info(f"Constructing graph for review {review_input.review_id}...")
    
    # In a real scenario, we would call:
    # graph_result = graph_facade.construct_graph_from_review(review_input)
    
    # For demonstration purposes, we'll simulate a successful result to avoid LLM costs/latency
    print(">> [Simulation] Calling LLM to extract entities and relationships...")
    print(">> [Simulation] Extracted entities: 'Graph Neural Network', 'Attention Mechanism', 'Dynamic Graphs', 'GraphSAGE'")
    print(">> [Simulation] Extracted relationships: 'Graph Neural Network' --improves--> 'Dynamic Graphs'")
    
    print("Graph construction completed successfully (Simulated).")
    
    # ---------------------------------------------------------
    # Phase 2: Retrieval & Scoring
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("Phase 2: Retrieval & Scoring System")
    print("="*40)
    
    logger.info("Initializing RetrievalFacade...")
    # Uses default graph path: result_v2/all_graphs_cleaned.json
    # Ensure this file exists or the facade handles it gracefully
    try:
        retrieval_facade = RetrievalFacade() 
        
        query = "Graph Neural Networks evaluation"
        print(f"Executing Smart Search for: '{query}'")
        
        retrieval_input = RetrievalInput(
            query=query,
            retrieval_type=RetrievalType.SMART,
            top_k=3
        )
        
        # Uncomment to run actual retrieval if the graph file exists and environment is set up
        # retrieval_result = retrieval_facade.retrieve(retrieval_input)
        # if retrieval_result.success:
        #     print(f"Found {len(retrieval_result.entities)} entities and {len(retrieval_result.relationships)} relationships.")
        # else:
        #     print(f"Retrieval failed: {retrieval_result.error_message}")
        
        print(">> [Simulation] Retrieval System ready. Skipping actual query to avoid loading large models.")
        
    except Exception as e:
        logger.warning(f"Retrieval system initialization skipped: {e}")

    # ---------------------------------------------------------
    # Phase 3: Idea Evaluation
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("Phase 3: Idea Evaluation")
    print("="*40)
    
    idea_context = IdeaContext(
        idea_id="IDEA_001",
        title="Adaptive GNN for Dynamic Graphs",
        description="A new Graph Neural Network architecture that adapts to changing graph structures in real-time using attention mechanisms."
    )
    
    logger.info("Initializing EvaluationFacade...")
    eval_facade = EvaluationFacade()
    
    print(f"Evaluating idea: {idea_context.title}")
    print("Method: RAG (Retrieval Augmented Generation)")
    print("Type: Feasibility Analysis")
    
    # Note: EvaluationInput structure in evaluation_facade.py might differ slightly from data_models.py
    # based on the read file content. Let's use the method provided by the facade.
    
    # The facade has specific methods like evaluate_feasibility which wrap the input creation
    try:
        # Using the facade's convenience method
        # eval_result = eval_facade.evaluate_feasibility(
        #     idea=idea_context,
        #     method=EvaluationMethod.RAG
        # )
        
        print(">> [Simulation] Calling RAG Evaluation Template...")
        print(">> [Simulation] Retrieving context from Graph Retrieval System...")
        print(">> [Simulation] Generating evaluation report via LLM...")
        print(">> [Simulation] Evaluation Result: The idea is feasible but requires addressing scalability concerns...")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")

    print("\n" + "="*80)
    print("Workflow Completed")
    print("="*80)

if __name__ == "__main__":
    main()
