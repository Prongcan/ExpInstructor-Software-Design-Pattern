"""
Facade for graph construction operations.

This module provides a unified interface for constructing knowledge graphs
from review data, coordinating the necessary strategies.
"""

import logging
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.data_models import GraphConstructionInput, GraphConstructionResult
from Strategies.graph_construction import GraphExtractionStrategy, GPTGraphExtractionStrategy

logger = logging.getLogger(__name__)

class GraphConstructionFacade:
    """
    Facade for graph construction.
    
    Simplifies the process of extracting knowledge graphs from reviews
    by hiding the complexity of strategy selection and execution.
    """
    
    def __init__(self):
        # In a more complex setup, we might use a factory here
        self._strategy: GraphExtractionStrategy = GPTGraphExtractionStrategy()
        
    def construct_graph_from_review(self, input_data: GraphConstructionInput) -> GraphConstructionResult:
        """
        Construct a graph from a single review.
        
        Args:
            input_data: The input data containing review content.
            
        Returns:
            The result containing the constructed graph.
        """
        return self._strategy.extract_graph(input_data)
    
    def batch_construct_graphs(self, inputs: List[GraphConstructionInput], max_workers: int = 5) -> List[GraphConstructionResult]:
        """
        Construct graphs from multiple reviews in parallel.
        
        Args:
            inputs: List of input data.
            max_workers: Number of parallel threads.
            
        Returns:
            List of results.
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_input = {
                executor.submit(self.construct_graph_from_review, inp): inp 
                for inp in inputs
            }
            
            for future in as_completed(future_to_input):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    inp = future_to_input[future]
                    logger.error(f"Error processing {inp.paper_id}-{inp.review_id}: {e}")
                    results.append(GraphConstructionResult(
                        input_data=inp,
                        success=False,
                        error_message=str(e)
                    ))
                    
        return results
