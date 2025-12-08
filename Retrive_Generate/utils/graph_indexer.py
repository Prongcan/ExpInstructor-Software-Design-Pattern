from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import networkx as nx
from .embedding_manager import EmbeddingManager

class GraphIndex:
    """
    Data class to hold graph indices and embeddings.
    """
    def __init__(self):
        # Keyword indices
        self.entity_index: Dict[str, str] = {}
        self.relationship_index: Dict[str, List[Tuple]] = defaultdict(list)
        self.evidence_index: Dict[str, List[Tuple]] = defaultdict(list)
        
        # Metadata for vector search
        self.entity_names: List[str] = []
        self.edge_triplets: List[Tuple] = []
        
        # Embeddings
        self.entity_embeddings: Optional[List[List[float]]] = None
        self.edge_embeddings: Optional[List[List[float]]] = None

class GraphIndexer:
    """
    Responsible for building indices and embeddings from a graph.
    Separates the indexing logic from the retrieval system.
    """
    
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager

    def build_index(self, G: nx.DiGraph) -> GraphIndex:
        """
        Builds the search index and generates/loads embeddings.
        """
        index = GraphIndex()
        
        entity_texts = []
        edge_texts = []
        
        # Build entity index
        for node in G.nodes():
            index.entity_index[node.lower()] = node
            index.entity_names.append(node)
            # Entity description text for embedding
            entity_texts.append(f"ENTITY: {node}")
        
        # Build relationship index
        for source, target, attrs in G.edges(data=True):
            rel = attrs.get('relationship', '')
            evidence = attrs.get('evidence', '')
            
            index.relationship_index[rel.lower()].append((source, target, attrs))
            index.evidence_index[evidence.lower()].append((source, target, attrs))
            
            # Edge description text for embedding
            triplet_text = f"EDGE: {source} --[{rel}]--> {target}. EVIDENCE: {evidence}"
            edge_texts.append(triplet_text)
            index.edge_triplets.append((source, target, attrs))

        # Build vector indexes using EmbeddingManager
        # This handles caching and batch generation
        index.entity_embeddings, index.edge_embeddings = self.embedding_manager.get_or_build_embeddings(
            entity_texts,
            edge_texts
        )
        
        return index
