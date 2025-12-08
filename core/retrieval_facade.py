"""
Facade for retrieval and scoring operations.

This module provides a unified interface for accessing the knowledge graph
retrieval system, hiding the complexity of the underlying graph engine.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.data_models import RetrievalInput, RetrievalResult, RetrievalType
from Retrive_Generate.graph_retrieval_system import GraphRetrievalSystem

logger = logging.getLogger(__name__)

class RetrievalFacade:
    """
    Facade for graph retrieval operations.
    
    Provides a simplified interface for:
    - Keyword search
    - Vector semantic search
    - Smart hybrid search
    - Path finding
    - Entity neighborhood exploration
    """
    
    def __init__(self, graph_path: Optional[str] = None):
        """
        Initialize the retrieval facade.
        
        Args:
            graph_path: Path to the graph JSON file. If None, uses default.
        """
        if graph_path is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent
            graph_path = str(project_root / "result_v2" / "all_graphs_cleaned.json")
            
        self.graph_path = graph_path
        self._system: Optional[GraphRetrievalSystem] = None
        
    @property
    def system(self) -> GraphRetrievalSystem:
        """Lazy initialization of the underlying system."""
        if self._system is None:
            logger.info(f"Initializing GraphRetrievalSystem with {self.graph_path}")
            # Note: We might want to make build_index_immediately=False if we want faster startup
            # but for a facade, we usually expect it to be ready.
            self._system = GraphRetrievalSystem(self.graph_path)
        return self._system

    def retrieve(self, input_data: RetrievalInput) -> RetrievalResult:
        """
        Perform a retrieval operation based on the input.
        
        Args:
            input_data: The retrieval parameters.
            
        Returns:
            The retrieval result.
        """
        try:
            if input_data.retrieval_type == RetrievalType.KEYWORD:
                return self._keyword_search(input_data)
            elif input_data.retrieval_type == RetrievalType.VECTOR:
                return self._vector_search(input_data)
            elif input_data.retrieval_type == RetrievalType.SMART:
                return self._smart_search(input_data)
            elif input_data.retrieval_type == RetrievalType.NEIGHBOR:
                return self._get_neighbors(input_data)
            elif input_data.retrieval_type == RetrievalType.PATH:
                return self._find_paths(input_data)
            else:
                return RetrievalResult(
                    query=input_data.query,
                    success=False,
                    error_message=f"Unsupported retrieval type: {input_data.retrieval_type}"
                )
        except Exception as e:
            logger.error(f"Retrieval failed: {e}", exc_info=True)
            return RetrievalResult(
                query=input_data.query,
                success=False,
                error_message=str(e)
            )

    def _keyword_search(self, input_data: RetrievalInput) -> RetrievalResult:
        raw_result = self.system.keyword_search(input_data.query)
        return self._format_result(input_data.query, raw_result)

    def _vector_search(self, input_data: RetrievalInput) -> RetrievalResult:
        # semantic_vector_search returns {query, top_entities, top_edges}
        raw_result = self.system.semantic_vector_search(input_data.query, top_k=input_data.top_k)
        
        # Normalize to standard format
        if "error" in raw_result:
             return RetrievalResult(
                query=input_data.query,
                success=False,
                error_message=raw_result["error"]
            )
            
        return RetrievalResult(
            query=input_data.query,
            success=True,
            entities=[{"name": e} for e in raw_result.get("top_entities", [])],
            relationships=[
                {"source": s, "target": t, **attrs} 
                for s, t, attrs in raw_result.get("top_edges", [])
            ],
            metadata={"type": "vector"}
        )

    def _smart_search(self, input_data: RetrievalInput) -> RetrievalResult:
        raw_result = self.system.smart_search(input_data.query, top_k=input_data.top_k)
        return self._format_result(input_data.query, raw_result)

    def _get_neighbors(self, input_data: RetrievalInput) -> RetrievalResult:
        if not input_data.entity_name:
             return RetrievalResult(
                query=input_data.query,
                success=False,
                error_message="Entity name required for neighbor search"
            )
            
        raw_result = self.system.get_entity_relationships(input_data.entity_name)
        
        if "error" in raw_result:
             return RetrievalResult(
                query=input_data.query,
                success=False,
                error_message=raw_result["error"]
            )
            
        # Format relationships
        relationships = []
        for rel in raw_result.get("outgoing_relationships", []):
            relationships.append({
                "source": input_data.entity_name,
                "target": rel["target"],
                "relation": rel["relationship"],
                "evidence": rel["evidence"],
                "direction": "outgoing"
            })
        for rel in raw_result.get("incoming_relationships", []):
            relationships.append({
                "source": rel["source"],
                "target": input_data.entity_name,
                "relation": rel["relationship"],
                "evidence": rel["evidence"],
                "direction": "incoming"
            })
            
        return RetrievalResult(
            query=input_data.query,
            success=True,
            entities=[{"name": input_data.entity_name}],
            relationships=relationships,
            metadata={"total_connections": raw_result.get("total_connections", 0)}
        )

    def _find_paths(self, input_data: RetrievalInput) -> RetrievalResult:
        if not input_data.entity_name or not input_data.target_entity:
             return RetrievalResult(
                query=input_data.query,
                success=False,
                error_message="Source (entity_name) and target (target_entity) required for path search"
            )
            
        paths = self.system.find_paths(
            input_data.entity_name, 
            input_data.target_entity, 
            max_length=input_data.max_hops
        )
        
        return RetrievalResult(
            query=f"{input_data.entity_name} -> {input_data.target_entity}",
            success=True,
            paths=paths,
            metadata={"count": len(paths)}
        )

    def _format_result(self, query: str, raw_result: Dict[str, Any]) -> RetrievalResult:
        """Helper to format standard search results."""
        if "error" in raw_result:
             return RetrievalResult(
                query=query,
                success=False,
                error_message=raw_result["error"]
            )
            
        # Extract entities
        entities = []
        for e in raw_result.get("entities", []):
            entities.append({"name": e})
            
        # Extract relationships
        relationships = []
        for r in raw_result.get("relationships", []):
            # Handle tuple format from NetworkX edges
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rel_data = {"source": r[0], "target": r[1]}
                if len(r) > 2:
                    rel_data.update(r[2] if isinstance(r[2], dict) else {"data": r[2]})
                relationships.append(rel_data)
            elif isinstance(r, dict):
                relationships.append(r)
                
        return RetrievalResult(
            query=query,
            success=True,
            entities=entities,
            relationships=relationships,
            metadata={"suggestions": raw_result.get("suggestions", [])}
        )
