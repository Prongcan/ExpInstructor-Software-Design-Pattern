"""
Instructor Agent Evaluation Template using Template Method Pattern.
Refactored with Template Method Pattern.

Unified template for all Instructor Agent-based evaluation single files.
Eliminates repetitive code across Evaluation_feasibility/ins_single.py, 
Evaluation_novelty/ins_single.py, Evaluation_significance/ins_single.py

"""

import os
import sys
import json
import typing as t
import re

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from langchain_core.messages import HumanMessage


class InstructorEvaluationTemplate:
    """
    Template class for Instructor Agent-based evaluations.
    Refactored with Template Method Pattern: Eliminates repetitive Agent evaluation code.
    """
    
    def __init__(self, evaluation_type: str):
        """
        Initialize Instructor evaluation template.
        Refactored with Template Method Pattern.
        
        Args:
            evaluation_type: Type of evaluation ("feasibility", "novelty", "significance")
        """
        self.evaluation_type = evaluation_type.lower()
        self._agent = None  # Lazy initialization
        self._evaluation_prompts = self._get_evaluation_prompts()
        
    def _get_evaluation_prompts(self) -> dict:
        """Get evaluation prompts for different evaluation types. Refactored with Template Method Pattern."""
        return {
            "feasibility": """
You are an expert academic reviewer specializing in research feasibility assessment.

Task: Evaluate the feasibility of the following research idea and provide a comprehensive assessment.

Research Idea:
{raw_idea}

Please provide a detailed feasibility evaluation covering:
1. **Technical Feasibility**: Can this research be technically implemented with current technology?
2. **Resource Requirements**: What resources (time, funding, equipment, personnel) would be needed?
3. **Methodological Feasibility**: Are the proposed methods and approaches practically viable?
4. **Data Availability**: Is the required data accessible and available for this research?
5. **Timeline Assessment**: Is the research timeline realistic and achievable?
6. **Risk Analysis**: What are the main risks and challenges that could affect feasibility?
7. **Infrastructure Needs**: What infrastructure or facilities would be required?
8. **Expertise Requirements**: What level of expertise and skills are needed to execute this research?

Please provide a thorough, professional assessment focusing on the feasibility aspects of this research idea.
""",
            
            "novelty": """
You are an expert academic reviewer specializing in research novelty assessment.

Task: Evaluate the novelty of the following research idea and provide a comprehensive assessment.

Research Idea:
{raw_idea}

Please provide a detailed novelty evaluation covering:
1. **Originality Assessment**: How original is this idea compared to existing work?
2. **Innovation Level**: What new insights, methods, or approaches does it introduce?
3. **Differentiation**: How does it differ from current state-of-the-art solutions?
4. **Creative Aspects**: What creative or unconventional elements does it contain?
5. **Knowledge Contribution**: What new knowledge would this research contribute to the field?
6. **Technical Novelty**: Are there novel technical approaches or methodologies?
7. **Conceptual Novelty**: Does it introduce new concepts or frameworks?
8. **Practical Novelty**: Are there novel applications or use cases?

Please provide a thorough, professional assessment focusing on the novelty aspects of this research idea.
""",
            
            "significance": """
You are an expert academic reviewer specializing in research significance assessment.

Task: Evaluate the significance of the following research idea and provide a comprehensive assessment.

Research Idea:
{raw_idea}

Please provide a detailed significance evaluation covering:
1. **Impact Assessment**: What potential impact could this research have on the field?
2. **Scientific Importance**: How important is this research for advancing scientific knowledge?
3. **Practical Significance**: What practical applications or real-world benefits could result?
4. **Theoretical Contribution**: How significant is the theoretical advancement this research offers?
5. **Societal Impact**: What broader societal implications or benefits might this research have?
6. **Economic Significance**: Are there potential economic benefits or commercial applications?
7. **Long-term Value**: What is the long-term significance and lasting value of this research?
8. **Field Advancement**: How much could this research advance or transform the field?

Please provide a thorough, professional assessment focusing on the significance aspects of this research idea.
"""
        }
    def _initialize_agent(self):
        """Initialize agent based on evaluation type. Refactored with Template Method Pattern."""
        if self._agent is None:
            try:
                # Dynamic import based on evaluation type
                if self.evaluation_type == "feasibility":
                    from Evaluation_feasibility.ins_model import create_custom_agent
                elif self.evaluation_type == "novelty":
                    from Evaluation_novelty.ins_model import create_custom_agent
                elif self.evaluation_type == "significance":
                    from Evaluation_significance.ins_model import create_custom_agent
                elif self.evaluation_type == "feasibility_score":
                    from Evaluation_feasibility_score.ins_model import create_custom_agent
                else:
                    raise ValueError(f"Unsupported evaluation type: {self.evaluation_type}")
                
                self._agent = create_custom_agent()
            except ImportError as e:
                raise ImportError(f"Failed to import agent for {self.evaluation_type}: {e}")
    
    def generate_evaluation_via_agent(self, agent, idea_text: str) -> t.Union[str, t.List[str]]:
        """
        Generate evaluation using unified Agent template with tool call tracking.
        Refactored with Template Method Pattern: Unified Agent execution logic for all evaluation types.
        
        Args:
            agent: The initialized agent
            idea_text: Research idea text to evaluate
            
        Returns:
            For feasibility: List of concerns
            For others: Evaluation text string
        """
        try:
            # Build prompt based on evaluation type
            prompt = self._build_agent_prompt(idea_text)
            
            # Execute agent with unified streaming logic
            final_text = self._execute_agent_with_tracking(agent, prompt)
            
            # Process result based on evaluation type
            if self.evaluation_type == "feasibility":
                return self._extract_concerns_from_result(final_text)
            else:
                return self._validate_and_return_text(final_text)
                
        except Exception as e:
            if self.evaluation_type == "feasibility":
                return []
            else:
                return f"ERROR: Failed to generate {self.evaluation_type} evaluation - {str(e)}"
    
    def _build_agent_prompt(self, idea_text: str) -> str:
        """Build agent prompt based on evaluation type. Refactored with Template Method Pattern."""
        # For agent-based evaluation, we can use the evaluation prompt template
        # or get the prompt from build_agent_user_prompt if available
        try:
            # Try to use the specific prompt builder for each evaluation type
            if self.evaluation_type == "feasibility":
                from Evaluation_feasibility.ins_model import build_agent_user_prompt
            elif self.evaluation_type == "novelty":
                from Evaluation_novelty.ins_model import build_agent_user_prompt
            elif self.evaluation_type == "significance":
                from Evaluation_significance.ins_model import build_agent_user_prompt
            elif self.evaluation_type == "feasibility_score":
                from Evaluation_feasibility_score.ins_model import build_agent_user_prompt
            else:
                # Fallback to generic prompt
                return self._evaluation_prompts[self.evaluation_type].format(raw_idea=idea_text)
            
            return build_agent_user_prompt(idea_text)
            
        except ImportError:
            # Fallback to generic prompt template
            return self._evaluation_prompts[self.evaluation_type].format(raw_idea=idea_text)
    
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
    
    def generate_evaluation(self, idea_text: str) -> t.Union[str, t.Tuple[t.List[str], str]]:
        """
        Generate evaluation using unified GPT template.
        Refactored with Template Method Pattern: Unified generation logic for all evaluation types.
        
        Args:
            idea_text: Research idea text to evaluate
            
        Returns:
            For feasibility: Tuple of (concerns_list, raw_response)
            For others: Evaluation text string
        """
        try:
            # Build prompt using Template Method
            prompt = self._build_prompt(idea_text)
            
            # Generate evaluation using GPT
            content = self._chat_client.chat(prompt)  # Refactored with Factory Method Pattern
            
            # Process result based on evaluation type
            if self.evaluation_type == "feasibility":
                return self._process_feasibility_result(content)
            else:
                return content
                
        except Exception as e:
            if self.evaluation_type == "feasibility":
                return [], f"ERROR: {e}"
            else:
                return f"ERROR: {e}"
    
    def _build_prompt(self, idea_text: str) -> str:
        """Build evaluation prompt. Refactored with Template Method Pattern."""
        system_prompt = self._system_prompts.get(self.evaluation_type, "")
        task_instruction = self._task_instructions.get(self.evaluation_type, "")
        
        prompt = (
            system_prompt
            + "\n\n"
            + "Idea to review:\n\n"
            + idea_text.strip()
            + "\n\n"
            + task_instruction
        )
        
        return prompt
    
    def _process_feasibility_result(self, content: str) -> t.Tuple[t.List[str], str]:
        """Process feasibility evaluation result. Refactored with Template Method Pattern."""
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                concerns_llm = [str(x).strip() for x in parsed if str(x).strip()]
                return concerns_llm, content
            else:
                concerns_llm = self._fallback_parse_list(content)
                return concerns_llm, content
        except Exception:
            concerns_llm = self._fallback_parse_list(content)
            return concerns_llm, content
    
    def _fallback_parse_list(self, content: str) -> t.List[str]:
        """Fallback parsing for malformed JSON. Refactored with Template Method Pattern."""
        lines = content.strip().split('\n')
        concerns = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith(']'):
                # Remove common prefixes
                line = line.lstrip('- ').lstrip('* ').lstrip('+ ')
                if line:
                    concerns.append(line)
        return concerns[:12]  # Limit to reasonable number
    
    def run_main(self, raw_idea: str) -> dict:
        """
        Main function using Template Method Pattern.
        Refactored with Template Method Pattern: Unified main logic for all GPT evaluations.
        
        Args:
            raw_idea: Raw idea text to evaluate
            
        Returns:
            Agent evaluation result
        """
        # Use unified template directly
        return self.generate_agent_evaluation(raw_idea)


    def _extract_concerns_from_result(self, result: str) -> t.List[str]:
        """Extract concerns for feasibility evaluation. Refactored with Template Method Pattern."""
        if not result or not isinstance(result, str):
            return []
        
        # For Agent results, may be nested JSON or direct JSON array
        try:
            # First try to parse directly
            if result.strip().startswith('[') and result.strip().endswith(']'):
                return json.loads(result.strip())
            
            # Try to find JSON array in the result text
            import re
            json_match = re.search(r'\[.*?\]', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback: split by lines and clean up
        lines = result.strip().split('\n')
        concerns = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                # Remove common prefixes
                line = re.sub(r'^[-*•]\s*', '', line)
                line = re.sub(r'^\d+\.\s*', '', line)
                concerns.append(line)
        
        return concerns[:12]  # Limit to 12 concerns as specified in prompt
    
    def _validate_and_return_text(self, result: str) -> str:
        """Validate and return evaluation text. Refactored with Template Method Pattern."""
        if not result or not isinstance(result, str):
            return f"ERROR: Invalid {self.evaluation_type} evaluation result"
        
        # Basic validation: result should be non-empty and meaningful
        if len(result.strip()) < 50:
            return f"ERROR: {self.evaluation_type.title()} evaluation too short or empty"
        
        return result.strip()


# ============= Factory Functions for Different Evaluation Types =============
# Refactored with Template Method Pattern: Factory functions to create specific evaluators

def create_feasibility_evaluator() -> InstructorEvaluationTemplate:
    """Create Agent feasibility evaluator. Refactored with Template Method Pattern."""
    return InstructorEvaluationTemplate("feasibility")

def create_novelty_evaluator() -> InstructorEvaluationTemplate:
    """Create Agent novelty evaluator. Refactored with Template Method Pattern."""
    return InstructorEvaluationTemplate("novelty")

def create_significance_evaluator() -> InstructorEvaluationTemplate:
    """Create Agent significance evaluator. Refactored with Template Method Pattern."""
    return InstructorEvaluationTemplate("significance")

def create_feasibility_score_evaluator() -> InstructorEvaluationTemplate:
    """Create Agent feasibility scoring evaluator. Refactored with Template Method Pattern."""
    return InstructorEvaluationTemplate("feasibility_score")


# ============= Unified API Functions =============
# Refactored with Template Method Pattern: Unified API for all Agent evaluations

def generate_agent_evaluation(idea_text: str, evaluation_type: str) -> t.Union[str, t.List[str]]:
    """
    Unified Agent evaluation function.
    Refactored with Template Method Pattern: Single function replaces all individual generate_xxx_evaluation functions.
    
    Args:
        idea_text: Research idea text to evaluate
        evaluation_type: Type of evaluation ("feasibility", "novelty", "significance", "feasibility_score")
        
    Returns:
        For feasibility: List of concerns
        For others: Evaluation text string
    """
    evaluator = InstructorEvaluationTemplate(evaluation_type)
    evaluator._initialize_agent()
    return evaluator.generate_evaluation_via_agent(evaluator._agent, idea_text)

