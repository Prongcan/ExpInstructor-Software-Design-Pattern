"""
Instructor Agent Evaluation Template using Template Method Pattern.
Abstract base class for all Instructor Agent-based evaluations.

Defines the algorithm skeleton for Agent evaluation while allowing subclasses
to customize specific evaluation behaviors.
"""

import os
import sys
import json
import typing as t
from abc import ABC, abstractmethod

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from langchain_core.messages import HumanMessage


class InstructorEvaluationTemplate(ABC):
    """
    Abstract base class for Instructor Agent-based evaluations using Template Method Pattern.
    
    Defines the algorithm skeleton for Agent evaluation:
    1. Initialize agent (dynamic import based on evaluation type)
    2. Build agent prompt (with dynamic import + fallback logic) 
    3. Execute agent with comprehensive tool call tracking
    4. Process agent result based on evaluation type
    
    Subclasses must implement the abstract methods to customize evaluation behavior.
    """
    
    def __init__(self, evaluation_type: str):
        """
        Initialize Instructor evaluation template.
        
        Args:
            evaluation_type: Type of evaluation ("feasibility", "novelty", "significance")
        """
        self.evaluation_type = evaluation_type.lower()
        self._agent = None  # Lazy initialization
    
    # =============== Abstract Methods to be implemented by subclasses ===============
    
    @abstractmethod
    def get_evaluation_prompt(self) -> str:
        """Get evaluation-specific prompt template. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def initialize_agent(self):
        """Initialize and return evaluation-specific agent. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def build_agent_prompt(self, idea_text: str) -> str:
        """Build evaluation-specific agent prompt. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def process_result(self, raw_response: str) -> t.Union[str, t.List[str]]:
        """Process agent result into final format. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def handle_error(self, error: Exception) -> t.Union[str, t.List[str]]:
        """Handle agent evaluation errors. Must be implemented by subclasses."""
        pass
    def _initialize_agent(self):
        """Initialize agent using subclass implementation."""
        if self._agent is None:
            self._agent = self.initialize_agent()
    
    def generate_evaluation_via_agent(self, agent, idea_text: str) -> t.Union[str, t.List[str]]:
        """
        Template method for Instructor Agent evaluation.
        Defines the algorithm skeleton for agent-based evaluation.
        This method receives an external agent instance.
        
        Args:
            agent: The initialized agent
            idea_text: Research idea text to evaluate
            
        Returns:
            For feasibility: List of concerns
            For others: Evaluation text string
        """
        try:
            # Step 1: Build agent prompt (includes dynamic imports + fallback logic)
            prompt = self.build_agent_prompt(idea_text)
            
            # Step 2: Execute agent with comprehensive tool call tracking
            agent_response = self._execute_agent_with_tracking(agent, prompt)
            
            # Step 3: Process agent result based on evaluation type
            return self.process_result(agent_response)
            
        except Exception as e:
            return self.handle_error(e)
    

    # =============== Alternative Template Method (for unified API) ===============
    
    def generate_evaluation(self, idea_text: str) -> t.Union[str, t.List[str]]:
        """
        Alternative template method that handles agent initialization internally.
        Used by the unified API function.
        """
        try:
            # Step 1: Initialize agent (dynamic import + lazy loading)
            self._initialize_agent()
            
            # Step 2-3: Use the main template method  
            return self.generate_evaluation_via_agent(self._agent, idea_text)
            
        except Exception as e:
            return self.handle_error(e)
    
    def _execute_agent_with_tracking(self, agent, prompt: str) -> str:
        """
        Execute agent with unified tool call tracking logic.
        Refactored with Template Method Pattern: Eliminates repetitive agent execution code.
        """
        input_message = HumanMessage(content=prompt)

        # Unified agent execution variables (这些变量在所有ins_single.py中完全相同)
        final_text = ""
        step_count = 0
        tool_call_count = 0
        tool_calls_details = []
        
        print("=" * 80)
        print("Starting Agent tool call process")
        print("=" * 80)
        
        # Set step limit to 50 (这个配置在所有文件中相同)
        config = {"recursion_limit": 50}
        for step in agent.stream({"messages": [input_message]}, config=config, stream_mode="values"):
            step_count += 1
            print(f"\n=== Step {step_count} ===")
            
            if step.get("messages"):
                last_message = step["messages"][-1]
                print(f"Message type: {type(last_message).__name__}")
                
                # Print message content (逻辑在所有文件中相同)
                if last_message.content:
                    print(f"Message content: {last_message.content}")
                    final_text = last_message.content
                
                # Check for tool calls (逻辑在所有文件中完全相同)
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    tool_call_count += len(last_message.tool_calls)
                    print(f"🔧 Tool call count: {len(last_message.tool_calls)}")
                    
                    for i, tool_call in enumerate(last_message.tool_calls):
                        tool_name = tool_call['name']
                        tool_args = tool_call['args']
                        tool_id = tool_call.get('id', f'tool_call_{i+1}')
                        
                        print(f"  Tool call {i+1}: {tool_name}")
                        print(f"    Tool ID: {tool_id}")
                        print(f"    Args: {json.dumps(tool_args, ensure_ascii=False, indent=4)}")
                        
                        # Record tool call details (逻辑完全相同)
                        tool_calls_details.append({
                            'step': step_count,
                            'tool_name': tool_name,
                            'tool_id': tool_id,
                            'args': tool_args,
                            'timestamp': f"Step {step_count}"
                        })
                
                # Check for tool results (逻辑在所有文件中完全相同)
                if hasattr(last_message, 'tool_call_id') and last_message.tool_call_id:
                    print(f"🔧 Tool result (ID: {last_message.tool_call_id}):")
                    if last_message.content:
                        # Limit output length to avoid overly long output
                        result_content = last_message.content
                        if len(result_content) > 1000:
                            print(f"    Result preview: {result_content[:1000]}...")
                            print(f"    [Result truncated, total length: {len(result_content)} chars]")
                        else:
                            print(f"    Full result: {result_content}")
                        
                        # Update tool call details (逻辑完全相同)
                        for detail in tool_calls_details:
                            if detail['tool_id'] == last_message.tool_call_id:
                                detail['result'] = result_content
                                break
            
            print("-" * 50)
        
        # Print statistics (所有文件中的统计逻辑完全相同)
        print("\n" + "=" * 80)
        print("Agent execution completed - Statistics")
        print("=" * 80)
        print(f"Total steps: {step_count}")
        print(f"Total tool calls: {tool_call_count}")
        
        # Print tool call statistics (统计逻辑完全相同)
        tool_stats = {}
        for detail in tool_calls_details:
            tool_name = detail['tool_name']
            if tool_name not in tool_stats:
                tool_stats[tool_name] = 0
            tool_stats[tool_name] += 1
        
        print("\nTool call statistics:")
        for tool_name, count in tool_stats.items():
            print(f"  {tool_name}: {count} times")
        
        # Print detailed records of all tool calls (详细记录逻辑完全相同)
        print("\n" + "=" * 80)
        print("All tool call detailed records")
        print("=" * 80)
        for i, detail in enumerate(tool_calls_details, 1):
            print(f"\nTool call #{i}:")
            print(f"  Step: {detail['timestamp']}")
            print(f"  Tool name: {detail['tool_name']}")
            print(f"  Tool ID: {detail['tool_id']}")
            print(f"  Args: {json.dumps(detail['args'], ensure_ascii=False, indent=4)}")
            if 'result' in detail:
                result = detail['result']
                if len(result) > 500:
                    print(f"  Result: {result[:500]}...")
                    print(f"  [Result truncated, total length: {len(result)} chars]")
                else:
                    print(f"  Result: {result}")
            else:
                print(f"  Result: [No result obtained]")
        
        print("\n" + "=" * 80)
        print("Final Agent Output")
        print("=" * 80)
        print(final_text)
        
        return final_text
    
# ============= Factory Functions for Different Evaluation Types =============
# Create specific evaluator instances using concrete subclasses

def create_feasibility_evaluator():
    """Create Instructor feasibility evaluator using concrete subclass."""
    from ..ins_feasibility_evaluator import FeasibilityInstructorEvaluator
    return FeasibilityInstructorEvaluator()

def create_novelty_evaluator():
    """Create Instructor novelty evaluator using concrete subclass."""
    from ..ins_novelty_evaluator import NoveltyInstructorEvaluator
    return NoveltyInstructorEvaluator()

def create_significance_evaluator():
    """Create Instructor significance evaluator using concrete subclass."""
    from ..ins_significance_evaluator import SignificanceInstructorEvaluator
    return SignificanceInstructorEvaluator()

def create_score_evaluator():
    """Create Instructor score evaluator using concrete subclass."""
    from ..ins_score_evaluator import ScoreInstructorEvaluator
    return ScoreInstructorEvaluator()


# ============= Unified API Functions =============
# Factory function to create appropriate evaluator based on type

def generate_agent_evaluation(idea_text: str, evaluation_type: str) -> t.Union[str, t.List[str]]:
    """
    Unified Instructor Agent evaluation function using concrete subclasses.
    
    Args:
        idea_text: Research idea text to evaluate
        evaluation_type: Type of evaluation ("feasibility", "novelty", "significance", "feasibility_score")
        
    Returns:
        For feasibility: List of concerns
        For others: Evaluation text string
    """
    if evaluation_type == "feasibility":
        evaluator = create_feasibility_evaluator()
    elif evaluation_type == "novelty":
        evaluator = create_novelty_evaluator()
    elif evaluation_type == "significance":
        evaluator = create_significance_evaluator()
    elif evaluation_type == "feasibility_score":
        evaluator = create_score_evaluator()
    else:
        raise ValueError(f"Unsupported evaluation type: {evaluation_type}")
    
    return evaluator.generate_evaluation(idea_text)

