import json
import networkx as nx

class GraphLoader:
    """
    Handles loading of graph data from files.
    Refactored from GraphRetrievalSystem to adhere to Single Responsibility Principle.
    """
    
    @staticmethod
    def load_graph(graph_file: str) -> nx.DiGraph:
        """
        Load graph data from JSON. Supports two formats:
        1) { "nodes": [...], "edges": [...] }
        2) [ { "paper_id": "...", "review_id": "...", "edges": [ {...}, ... ] }, ... ]
        """
        G = nx.DiGraph()
        
        with open(graph_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        def add_edge_record(src_name, tgt_name, rel, evd, edge_meta=None):
            # Ensure nodes exist
            if not G.has_node(src_name):
                G.add_node(src_name, type='entity')
            if not G.has_node(tgt_name):
                G.add_node(tgt_name, type='entity')
            # Add the edge
            attrs = {
                "relationship": rel or "",
                "evidence": evd or "",
            }
            if edge_meta:
                attrs.update(edge_meta)
            G.add_edge(src_name, tgt_name, **attrs)

        # Case 1: legacy format
        if isinstance(data, dict) and "nodes" in data and "edges" in data:
            for node in data["nodes"]:
                G.add_node(node.get("name", node.get("id", "")),
                                id=node.get("id", ""),
                                type=node.get("type", "entity"))
            for edge in data["edges"]:
                add_edge_record(
                    edge.get("source"), edge.get("target"),
                    edge.get("relationship"), edge.get("evidence"),
                    {"edge_id": edge.get("id", "")}
                )

        # Case 2: all_graphs.json format (list where each entry has edges)
        elif isinstance(data, list):
            for item_idx, item in enumerate(data):
                paper_id = item.get("paper_id", "")
                review_id = item.get("review_id", "")
                edges_raw = item.get("edges", [])
                # Support edges defined as a list or a single dict
                if isinstance(edges_raw, dict):
                    edges_iter = [edges_raw]
                elif isinstance(edges_raw, list):
                    edges_iter = edges_raw
                else:
                    edges_iter = []
                for edge_idx, e in enumerate(edges_iter):
                    add_edge_record(
                        e.get("source_name"), e.get("target_name"),
                        e.get("relationship"), e.get("evidence"),
                        {
                            "edge_id": f"{paper_id}:{review_id}:{edge_idx}",
                            "paper_id": paper_id,
                            "review_id": review_id
                        }
                    )
        else:
            raise ValueError("Unsupported graph data format")

        print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return G
