"""
Template Method Pattern for evaluation flows.
Refactored with Template Method Pattern.
"""

from __future__ import annotations

import json
import typing as t
from abc import ABC, abstractmethod

# Import dependencies
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from langchain_core.messages import HumanMessage


class BaseEvaluationFlow(ABC):
    """
    Abstract base class for evaluation flows using Template Method Pattern.
    Refactored with Template Method Pattern.
    
    This class defines the common evaluation algorithm skeleton while allowing
    subclasses to override specific steps.
    """
    
    def __init__(self):
        self.step_count = 0
        self.tool_call_count = 0
        self.tool_calls_details = []
        self.final_text = ""
    
    # Template Method - defines the algorithm skeleton
    def run(self, idea_text: str) -> t.Dict[str, t.Any]:
        """
        Template method defining the evaluation flow skeleton.
        Refactored with Template Method Pattern.
        
        Args:
            idea_text: Research idea text to evaluate
            
        Returns:
            Dict containing evaluation results
        """
        print("=" * 80)
        print(f"Starting {self.get_evaluation_type()} evaluation flow")
        print("=" * 80)
        
        # Step 1: Initialize (hook method)
        agent = self.create_agent()
        prompt = self.build_prompt(idea_text)
        
        # Step 2: Execute evaluation (template method with hooks)
        self.pre_execution_hook()
        evaluation_result = self.execute_agent_evaluation(agent, prompt, idea_text)
        self.post_execution_hook()
        
        # Step 3: Process results (hook method)
        processed_result = self.process_evaluation_result(evaluation_result)
        
        # Step 4: Additional scoring (hook method - optional)
        additional_scores = self.perform_additional_scoring(processed_result, idea_text)
        
        # Step 5: Format final output (hook method)
        final_result = self.format_final_result(processed_result, additional_scores)
        
        print("=" * 80)
        print(f"{self.get_evaluation_type()} evaluation completed")
        print("=" * 80)
        
        return final_result
    
    # Hook methods - to be overridden by subclasses
    @abstractmethod
    def get_evaluation_type(self) -> str:
        """Return the type of evaluation (e.g., 'Feasibility', 'Novelty')."""
        pass
    
    @abstractmethod
    def create_agent(self):
        """Create and return the agent instance."""
        pass
    
    @abstractmethod
    def build_prompt(self, idea_text: str) -> str:
        """Build the evaluation prompt for the given idea text."""
        pass
    
    @abstractmethod
    def process_evaluation_result(self, evaluation_result: str) -> t.Any:
        """Process the raw evaluation result into structured format."""
        pass
    
    def perform_additional_scoring(self, processed_result: t.Any, idea_text: str) -> t.Dict[str, t.Any]:
        """
        Perform additional scoring/comparison (optional hook).
        Default implementation returns empty dict.
        """
        return {}
    
    @abstractmethod
    def format_final_result(self, processed_result: t.Any, additional_scores: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """Format the final result for output."""
        pass
    
    # Hook methods with default implementations
    def pre_execution_hook(self) -> None:
        """Called before agent execution. Override for custom preprocessing."""
        pass
    
    def post_execution_hook(self) -> None:
        """Called after agent execution. Override for custom postprocessing."""
        pass
    
    def get_recursion_limit(self) -> int:
        """Return the recursion limit for agent execution. Override to customize."""
        return 50
    
    def should_print_detailed_logs(self) -> bool:
        """Return whether to print detailed execution logs. Override to customize."""
        return True
    
    # Template method implementation - common agent execution logic
    def execute_agent_evaluation(self, agent, prompt: str, idea_text: str) -> str:
        """
        Execute agent evaluation with common logging and error handling.
        This is a template method implementation that shouldn't be overridden.
        """
        input_message = HumanMessage(content=prompt)
        
        # Reset tracking variables
        self.step_count = 0
        self.tool_call_count = 0
        self.tool_calls_details = []
        self.final_text = ""
        
        print("=" * 80)
        print("Starting Agent tool call process")
        print("=" * 80)
        
        config = {"recursion_limit": self.get_recursion_limit()}
        
        try:
            for step in agent.stream({"messages": [input_message]}, config=config, stream_mode="values"):
                self.step_count += 1
                
                if self.should_print_detailed_logs():
                    print(f"\n=== Step {self.step_count} ===")
                
                if step.get("messages"):
                    last_message = step["messages"][-1]
                    
                    if self.should_print_detailed_logs():
                        print(f"Message type: {type(last_message).__name__}")
                    
                    # Update final text
                    if last_message.content:
                        if self.should_print_detailed_logs():
                            print(f"Message content: {last_message.content}")
                        self.final_text = last_message.content
                    
                    # Handle tool calls
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        self.tool_call_count += len(last_message.tool_calls)
                        
                        if self.should_print_detailed_logs():
                            print(f"🔧 Tool call count: {len(last_message.tool_calls)}")
                        
                        for i, tool_call in enumerate(last_message.tool_calls):
                            tool_name = tool_call['name']
                            tool_args = tool_call['args']
                            tool_id = tool_call.get('id', f'tool_call_{i+1}')
                            
                            if self.should_print_detailed_logs():
                                print(f"  Tool call {i+1}: {tool_name}")
                                print(f"    Tool ID: {tool_id}")
                                print(f"    Args: {json.dumps(tool_args, ensure_ascii=False, indent=4)}")
                            
                            self.tool_calls_details.append({
                                'step': self.step_count,
                                'tool_name': tool_name,
                                'tool_id': tool_id,
                                'args': tool_args,
                                'timestamp': f"Step {self.step_count}"
                            })
                    
                    # Handle tool results
                    if hasattr(last_message, 'tool_call_id') and last_message.tool_call_id:
                        if self.should_print_detailed_logs():
                            print(f"🔧 Tool result (ID: {last_message.tool_call_id}):")
                        
                        if last_message.content:
                            result_content = last_message.content
                            
                            if self.should_print_detailed_logs():
                                if len(result_content) > 1000:
                                    print(f"    Result preview: {result_content[:1000]}...")
                                    print(f"    [Result truncated, total length: {len(result_content)} chars]")
                                else:
                                    print(f"    Full result: {result_content}")
                            
                            # Update tool call details
                            for detail in self.tool_calls_details:
                                if detail['tool_id'] == last_message.tool_call_id:
                                    detail['result'] = result_content
                                    break
                
                if self.should_print_detailed_logs():
                    print("-" * 50)
            
            # Print execution statistics
            self._print_execution_statistics()
            
            # Validate result
            if not self.final_text or self.final_text.strip() == "":
                return "ERROR: Agent did not return valid result"
            
            if self.final_text.startswith("ERROR"):
                return self.final_text
            
            return self.final_text
            
        except Exception as e:
            error_msg = f"ERROR: Agent execution failed: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _print_execution_statistics(self) -> None:
        """Print detailed execution statistics."""
        if not self.should_print_detailed_logs():
            return
            
        print("\n" + "=" * 80)
        print("Agent execution completed - Statistics")
        print("=" * 80)
        print(f"Total steps: {self.step_count}")
        print(f"Total tool calls: {self.tool_call_count}")
        
        # Tool call statistics
        tool_stats = {}
        for detail in self.tool_calls_details:
            tool_name = detail['tool_name']
            if tool_name not in tool_stats:
                tool_stats[tool_name] = 0
            tool_stats[tool_name] += 1
        
        print("\nTool call statistics:")
        for tool_name, count in tool_stats.items():
            print(f"  {tool_name}: {count} times")
        
        # Detailed tool call records
        print("\n" + "=" * 80)
        print("All tool call detailed records")
        print("=" * 80)
        for i, detail in enumerate(self.tool_calls_details, 1):
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
        print(self.final_text)
