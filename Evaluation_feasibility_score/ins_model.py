import os
import sys
import json
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from Retrive_Generate.graph_retrieval_system import GraphRetrievalSystem
from service.llm_factory import get_chat_client  # Refactored with Factory Method Pattern
from Evaluation_feasibility.retrieval_active_object import RetrievalActiveObject

# Lazy initialization of graph retrieval system
graph_file = "result_v2/all_graphs_cleaned.json"
retrieval_system = None
_retrieval_system_lock = threading.Lock()
_chat_client = get_chat_client()  # Refactored with Factory Method Pattern

def get_retrieval_system():
    """Get graph retrieval system instance (lazy initialization, thread-safe)"""
    global retrieval_system
    if retrieval_system is None:
        with _retrieval_system_lock:
            # Double-check locking pattern
            if retrieval_system is None:
                print("Initializing graph retrieval system...")
                
                # Preload BGE-M3 model to ensure it's only loaded once
                try:
                    from service.BGE_M3 import preload_model
                    preload_model("BAAI/bge-m3")
                except ImportError:
                    print("BGE-M3 preload failed, will use ChatGPT embedding")
                
                # Don't build index first, only load graph data
                retrieval_system = GraphRetrievalSystem(graph_file, build_index_immediately=False)
                print("Graph data loaded, starting to build index...")
                # Delay building index so embedding model is only loaded once
                retrieval_system.build_index()
                print("Graph retrieval system initialization completed")
    return retrieval_system

@tool
def search_similar_node_and_edge(
    node_query: str, 
    node_k: int = 5,
    edge_query: str = "",
    edge_k: int = 5
) -> str:
    """
    Comprehensive search for nodes and edges using Active Object Pattern.
    ... (保留原有的 docstring) ...
    """
    try:
        # 1. 获取 Active Object 实例 (Singleton)
        # 这取代了直接 import requests 和硬编码 URL
        retrieval_ao = RetrievalActiveObject()
        
        # 2. 构造请求 Payload
        payload = {
            "node_query": node_query,
            "node_k": node_k,
            "edge_query": edge_query,
            "edge_k": edge_k
        }
        
        # 3. [Active Object 核心] 提交任务并获得 Future
        # 这里不会阻塞，请求只是被放入了队列
        print(f"[Tool] Submitting retrieval task for '{node_query}' via Active Object...")
        future_result = retrieval_ao.submit_task(payload)
        
        # 4. 获取结果
        # 注意：虽然 LangChain Tool 最终需要同步返回字符串，但我们已经解耦了调用和执行。
        # 在更复杂的异步 Agent 架构中，这里可以 await future。
        # 这里为了配合 requests 库和当前架构，我们使用 .result() 等待。
        data = future_result.result(timeout=65) # 设置稍微宽裕的超时
        
        # --- 以下逻辑保持不变 (LLM Re-ranking) ---
        if "result" in data:
            results = data["result"]
            # Call LLM for final re-ranking and summarization
            prompt = f"""
            You are a helpful assistant. 
            Sort these graph results by combined node and edge similarity and provide a summary.
            The user's request: find evidence about entity [{node_query}] and relation [{edge_query}] related to feasibility evaluation.
            Results: {str(results)}
            
            Please:
            1. Sort the results by combined node and edge similarity (highest first)
            2. Analyze if the results contain information that closely matches the query
            3. Provide a natural language summary that analyzes:
            - Relevance assessment: How well do the results match the query? Are they highly relevant, moderately relevant, or mostly irrelevant?
            - Feasibility insights: Based on the results, what do they suggest about the feasibility, implementation challenges, or effectiveness of related methods?
            - Overall insights: What do these results collectively suggest about the research domain, common challenges, or established patterns?
            
            Write a comprehensive summary that naturally explains what the retrieved results reveal about the query topic and the existing knowledge base.
            
            Output JSON with the same structure as the input results, but add a "summary" field at the end containing the analysis.
            
            """
            print("LLM re-ranking and summarization in progress...")
            chat_simple = _chat_client.chat(prompt)  

            return chat_simple
        elif "error" in data:
            return f"Service error: {data['error']}"
        else:
            return "Unknown error"
            
    except Exception as e:
        return f"Failed to call service via Active Object: {str(e)}"
  
@tool
def get_original_review_text(paper_id: Annotated[str, "Paper ID"], review_id: Annotated[str, "Review ID"]) -> str:
    """
    Retrieve original review text from iclr2024_simple.json based on paper_id and review_id
    
    Args:
        paper_id: The paper ID to search for
        review_id: The review ID to search for
    
    Returns:
        Original review text including summary, strengths, weakness, and suggestions
    """
    try:
        # Load the JSON file
        with open("data/ICLR/iclr2024_simple.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Search for matching paper_id and review_id
        for entry in data:
            if entry.get("paper_id") == paper_id:
                # Find matching review_id
                for review in entry.get("review_contents", []):
                    if review.get("review_id") == review_id:
                        content = review.get("content", {})
                        
                        result = f"Found original review text for Paper ID: {paper_id}, Review ID: {review_id}\n"
                        result += "=" * 80 + "\n"
                        result += "ORIGINAL REVIEW CONTENT:\n"
                        result += "-" * 50 + "\n"
                        
                        if content.get("strengths"):
                            result += f"STRENGTHS:\n{content['strengths']}\n\n"
                        if content.get("weakness"):
                            result += f"WEAKNESS:\n{content['weakness']}\n\n"
                        if content.get("suggestions"):
                            result += f"SUGGESTIONS:\n{content['suggestions']}\n\n"
                        
                        return result
        
        return f"No review found for Paper ID: {paper_id}, Review ID: {review_id}"
        
    except Exception as e:
        return f"Error retrieving review text: {str(e)}"

def build_agent_user_prompt(research_idea: str) -> str:
    """
    Build agent user prompt for generating complete peer review evaluation text
    """
    return f"""
You are a rigorous peer-reviewer evaluating the feasibility of an academic research idea.
Task: Critically evaluate the given idea/proposal and write a comprehensive peer review evaluation text.

Your response should:
- Be a continuous, natural text similar to a peer review comment (like "all_comments" in academic reviews)
- Discuss feasibility, implementation challenges, effectiveness, and potential issues
- Be concise and academic in tone
- Provide a balanced evaluation covering both positive aspects and concerns
- Include your assessment of:
  * How easy or difficult it is to implement the idea
  * Whether the experimental setup is feasible
  * Whether the method is likely to work effectively
  * Any resource requirements or challenges
  * Comparison with existing approaches if relevant
- Write in a natural, flowing style as if you are providing feedback to the authors

You can use two tools to understand how existing methods address this problem, what are the positive and negative characteristics of the method proposed in the idea, what are the characteristics of the dataset: search_similar_node_and_edge and get_original_review_text.

You **MUST** perform at least 15 tool calls (including at least 5 get_original_review_text calls) before providing the final evaluation text.

Iteration & Tool Scheduling:
- Prefer making only 1 tool call per step; absolutely no more than 2 in any single step.
- If multiple queries are needed, split them into multiple steps/rounds to collect evidence gradually.
- After each tool result, briefly reflect and plan the next single tool call.

Idea to be evaluated:
{research_idea}

Write a comprehensive peer review evaluation text discussing the feasibility, implementation challenges, effectiveness, and any concerns about this idea. Write in a natural, flowing style as if you are providing feedback to the authors.
"""


def create_custom_agent():
    """
    Create custom Agent for feasibility evaluation
    """
    # Set OpenAI API key
    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
    
    # Initialize ChatGPT-4o model
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.9
    )
    
    # Define tool list
    tools = [
        search_similar_node_and_edge,
        get_original_review_text
    ]
    
    # Create Agent with enhanced parameters
    agent = create_react_agent(
        model=model, 
        tools=tools,
        prompt="""
You are a rigorous peer-reviewer evaluating the feasibility of an academic research idea.
Task: Critically evaluate the given idea/proposal and write a comprehensive peer review evaluation text.

Your response should:
- Be a continuous, natural text similar to a peer review comment (like "all_comments" in academic reviews)
- Discuss feasibility, implementation challenges, effectiveness, and potential issues
- Be concise and academic in tone
- Provide a balanced evaluation covering both positive aspects and concerns
- Include your assessment of:
  * How easy or difficult it is to implement the idea
  * Whether the experimental setup is feasible
  * Whether the method is likely to work effectively
  * Any resource requirements or challenges
  * Comparison with existing approaches if relevant
- Write in a natural, flowing style as if you are providing feedback to the authors

You can use two tools to understand how existing methods address this problem, what are the positive and negative characteristics of the method proposed in the idea, what are the characteristics of the dataset: search_similar_node_and_edge and get_original_review_text.

1. Tool Usage Specifications (Key Supplement for Edge Query)
1.1 search_similar_node_and_edge (Search Similar Nodes and Edges)
The core function of this tool is to retrieve information related to knowledge entities (nodes) and their relationships/evaluations (edges). You should systematically explore different entities mentioned in the research idea and query them separately.

**Entity Discovery Strategy:**
- Extract ALL distinct knowledge entities from the research idea (e.g., for "LLM improving dialect recognition", extract "LLM", "dialect", "recognition", "speech recognition", "language processing" etc.)
- Query each entity separately with different node_query values
- Use multiple search rounds to cover different aspects and entities

**Edge Query Design Rules:**
node_query: Enter a specific knowledge entity (e.g., "Large Language Models", "Graph Neural Networks", "dialect recognition", "speech processing", "machine learning models").
edge_query: Enter ONLY predicate phrases WITHOUT including the entity name. Use generic relationship expressions:
- For positive effects: "can improve", "helps", "enhances", "strengthens", "boosts", "optimizes"
- For negative effects: "has limitations", "faces challenges", "has shortcomings", "struggles with", "prone to errors"
- For relationships: "is related to", "depends on", "influences", "causes"

**Examples:**
- WRONG: edge_query = "LLM improves dialect recognition" (contains entity)
- CORRECT: edge_query = "can improve recognition" (pure predicate)
- For "LLM improving dialect recognition" idea, query:
  * node_query="LLM", edge_query="can improve recognition"
  * node_query="dialect", edge_query="difficult to recognize"
  * node_query="speech recognition", edge_query="faces challenges"

1.2 get_original_review_text (Get Original Review Text)
This tool is used to retrieve full-text or key segments of academic reviews/papers. When calling it, you must ensure that the retrieved content is highly relevant to the feasibility evaluation you want to provide later — it should directly involve the feasibility, implementation challenges, limitations, or potential problems of the research idea, rather than irrelevant background information.

2. Strict Tool Call Requirements
You MUST perform at least 15 tool calls before providing the final evaluation text. Among them, at least 5 calls must be to get_original_review_text (to ensure you have sufficient review evidence to support your evaluation).
Do not provide the final evaluation text until you have completed at least 15 tool calls.
For search_similar_node_and_edge, use different combinations of node_query and edge_query (covering both positive and negative information orientations related to the research idea) to collect comprehensive evidence — avoid repeating the same query, as this will lead to incomplete information collection.
For get_original_review_text, each call must target a review/paper that directly discusses the feasibility, implementation challenges, or effectiveness concerns of the research idea.

Iteration & Tool Scheduling:
- Prefer making only 1 tool call per step; absolutely no more than 2 in any single step.
- If multiple queries are needed, split them into multiple steps/rounds to collect evidence gradually.
- After each tool result, briefly reflect and plan the next single tool call.
""",
        version="v2"
    )
    
    return agent
