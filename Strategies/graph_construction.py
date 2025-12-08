"""
Strategy pattern for graph extraction.

This module defines the strategy interface and concrete implementations
for extracting knowledge graphs from text.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import json
import re
import logging

from core.data_models import GraphConstructionInput, GraphConstructionResult, GraphData, GraphNode, GraphEdge
from LLM_service.llm_factory import get_chat_client

logger = logging.getLogger(__name__)

class GraphExtractionStrategy(ABC):
    """Abstract base class for graph extraction strategies."""
    
    def extract_graph(self, input_data: GraphConstructionInput) -> GraphConstructionResult:
        """
        Template method for extracting graph from input data.
        """
        try:
            # 1. Prepare prompt
            review_text = self._compose_review_text(input_data.review_content)
            if not review_text:
                return GraphConstructionResult(
                    input_data=input_data,
                    success=False,
                    error_message="Empty review content"
                )
                
            prompt = self._create_prompt(review_text)
            
            # 2. Call LLM
            if not hasattr(self, 'client'):
                 raise NotImplementedError("Subclasses must define self.client")
            
            response = self.client.chat(prompt)
            
            # 3. Parse response
            graph_data = self._parse_response(response)
            
            if not graph_data:
                return GraphConstructionResult(
                    input_data=input_data,
                    success=False,
                    raw_response=response,
                    error_message="Failed to parse graph data from response"
                )
                
            return GraphConstructionResult(
                input_data=input_data,
                success=True,
                graph_data=graph_data,
                raw_response=response
            )
            
        except Exception as e:
            logger.error(f"Error in graph extraction: {e}")
            return GraphConstructionResult(
                input_data=input_data,
                success=False,
                error_message=str(e)
            )

    def _compose_review_text(self, content: Dict[str, str]) -> str:
        """Compose review text from parts. Common implementation."""
        text = ""
        if 'strengths' in content:
            text += f"Strengths: {content['strengths']}\n\n"
        if 'weakness' in content:
            text += f"Weakness: {content['weakness']}\n\n"
        if 'suggestions' in content:
            text += f"Suggestions: {content['suggestions']}\n\n"
        return text.strip()

    @abstractmethod
    def _create_prompt(self, review_text: str) -> str:
        """Create the extraction prompt."""
        pass

    @abstractmethod
    def _parse_response(self, response: str) -> Optional[GraphData]:
        """Parse JSON response into GraphData."""
        pass


class GPTGraphExtractionStrategy(GraphExtractionStrategy):
    """Graph extraction using GPT models."""
    
    def __init__(self):
        # Hardcoded to use GPT as requested
        self.client = get_chat_client("chatgpt")
        
    def _create_prompt(self, review_text: str) -> str:
        """Create the extraction prompt."""
        return f"""
        You are a professional academic evaluation experience extraction expert. 
        Please extract detailed and specific knowledge entities and experiential relationships from the following review text to construct an experiential relationship subgraph.
        Knowledge entities include but are not limited to questions, methods, concepts, theories, scenarios, and other professional terms and knowledge. Please do not use a simple word; it is better to enrich the semantic meaning of the entity based on the original evaluation by adding some adjectives. 
        Experience relations refer to, for example, "seems to be relatively good at improving... ability in xxx", "seems unable to be well achieved through... " and other similar evaluative relationship statements. Their characteristics are: they have certain positive or negative emotional evaluation information, and they have as detailed as possible semantic information of specific aspects. Nodes and edges must directly depend on the review. The original text is only for reference. Therefore, when each edge is constructed, there must be corresponding evidence.

        Please output the result in JSON format as follows:
        {{
            "nodes": [
                {{"id": "node1", "name": "entity name", "type": "concept/method/etc", "description": "detailed description"}}
            ],
            "edges": [
                {{"source": "node1", "target": "node2", "relation": "relation description", "description": "evidence from text"}}
            ]
        }}

        Review Text:
        {review_text}
        """

    def _parse_response(self, response: str) -> Optional[GraphData]:
        """Parse JSON response into GraphData."""
        try:
            # Extract JSON block
            json_pattern = r'```json\s*(.*?)\s*```'
            match = re.search(json_pattern, response, re.DOTALL)
            
            if match:
                json_str = match.group(1).strip()
            else:
                # Try to find raw JSON if no code blocks
                start = response.find('{')
                end = response.rfind('}')
                if start != -1 and end != -1:
                    json_str = response[start:end+1]
                else:
                    return None
            
            data = json.loads(json_str)
            
            nodes = []
            edges = []
            id_map = {} 
            
            raw_nodes = data.get('nodes', [])
            for n in raw_nodes:
                node = GraphNode(
                    id=n.get('id', str(len(nodes))),
                    name=n.get('name', 'Unknown'),
                    type=n.get('type', 'concept'),
                    description=n.get('description')
                )
                nodes.append(node)
                id_map[node.id] = node.name
            
            raw_edges = data.get('edges', [])
            for e in raw_edges:
                src_id = e.get('source')
                tgt_id = e.get('target')
                
                src_name = id_map.get(src_id, src_id)
                tgt_name = id_map.get(tgt_id, tgt_id)
                
                edge = GraphEdge(
                    source=src_name,
                    target=tgt_name,
                    relation=e.get('relation', 'related_to'),
                    description=e.get('description')
                )
                edges.append(edge)
                
            return GraphData(nodes=nodes, edges=edges)
            
        except Exception as e:
            logger.error(f"JSON parsing error: {e}")
            return None
