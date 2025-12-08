import networkx as nx
from typing import Dict, List, Any

class GraphPresenter:
    """
    Handles the presentation layer for the Graph Retrieval System.
    Responsible for formatting and displaying results to the console.
    """

    @staticmethod
    def display_search_results(results: Dict[str, Any]):
        """
        Display search results
        """
        print(f"\n=== Search results: '{results['query']}' ===")
        
        if results.get('entities'):
            print(f"\nFound {len(results['entities'])} related entities:")
            for entity in results['entities'][:5]:  # Show only the first five
                print(f"  • {entity}")
        
        if results.get('relationships'):
            print(f"\nFound {len(results['relationships'])} related relationships:")
            for source, target, attrs in results['relationships'][:3]:  # Show only the first three
                print(f"  • {source} --[{attrs.get('relationship', '')}]--> {target}")
        
        if results.get('evidence'):
            print(f"\nFound {len(results['evidence'])} related evidence snippets:")
            for source, target, attrs in results['evidence'][:3]:  # Show only the first three
                evidence = attrs.get('evidence', '')[:100]
                print(f"  • {evidence}...")
        
        if results.get('suggestions'):
            print(f"\nSuggested entities:")
            for suggestion in results['suggestions']:
                print(f"  • {suggestion['entity']} ({suggestion['connections']} connections)")
    
    @staticmethod
    def display_entity_info(info: Dict[str, Any]):
        """
        Display entity information
        """
        if 'error' in info:
            print(f"Error: {info['error']}")
            return
        
        print(f"\n=== Entity: {info['entity']} ===")
        print(f"Total connections: {info['total_connections']}")
        
        if info.get('outgoing_relationships'):
            print(f"\nOutgoing relationships ({len(info['outgoing_relationships'])}):")
            for rel in info['outgoing_relationships']:
                print(f"  → {rel['target']} ({rel['relationship']})")
                print(f"    Evidence: {rel['evidence'][:100]}...")
        
        if info.get('incoming_relationships'):
            print(f"\nIncoming relationships ({len(info['incoming_relationships'])}):")
            for rel in info['incoming_relationships']:
                print(f"  ← {rel['source']} ({rel['relationship']})")
                print(f"    Evidence: {rel['evidence'][:100]}...")
    
    @staticmethod
    def display_paths(paths: List[List[str]]):
        """
        Display paths
        """
        if not paths:
            print("No paths found")
            return
        
        print(f"\nFound {len(paths)} paths:")
        for i, path in enumerate(paths[:5]):  # Show only the first five
            print(f"  Path {i+1}: {' -> '.join(path)}")
    
    @staticmethod
    def display_related_entities(entity: str, related: List[str]):
        """
        Display related entities
        """
        print(f"\n=== Related entities for {entity} ===")
        if not related:
            print("No related entities found")
            return
        
        print(f"Found {len(related)} related entities:")
        for i, rel_entity in enumerate(related[:10]):  # Show only the first ten
            print(f"  {i+1}. {rel_entity}")

    @staticmethod
    def display_search_node_and_edge(results: List[Dict[str, Any]]):
        """
        Display combined node-edge search results
        """
        if not results:
            print("No related results found")
            return
        
        print(f"\n=== Node-edge-node search results ===")
        print(f"Found {len(results)} related results:")
        
        for i, result in enumerate(results[:10]):  # Show only the first ten
            print(f"\nResult {i+1}:")
            print(f"  Source node: {result['source_node']}")
            print(f"  Target node: {result['target_node']}")
            print(f"  Relationship: {result['edge']}")
            print(f"  Evidence: {result['evidence']}")
            print(f"  Node similarity: {result['node_similarity']:.4f}")
            print(f"  Edge similarity: {result['edge_similarity']:.4f}")
            if result.get('paper_id'):
                print(f"  Paper ID: {result['paper_id']}")
            if result.get('review_id'):
                print(f"  Review ID: {result['review_id']}")
    
    @staticmethod
    def show_stats(G: nx.DiGraph):
        """
        Display graph statistics
        """
        print(f"\n=== Graph statistics ===")
        print(f"Nodes: {G.number_of_nodes()}")
        print(f"Edges: {G.number_of_edges()}")
        print(f"Weakly connected components: {nx.number_weakly_connected_components(G)}")
        
        # Node degree stats
        degrees = dict(G.degree())
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"\nMost connected nodes:")
        for node, degree in top_nodes:
            print(f"  {node}: {degree} connections")
