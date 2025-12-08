"""
GPT Evaluation Template using Template Method Pattern.
Abstract base class for all GPT-based evaluations.

Defines the algorithm skeleton for GPT evaluation while allowing subclasses
to customize specific evaluation behaviors.
"""

import os
import sys
import typing as t
from abc import ABC, abstractmethod

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from LLM_service.llm_factory import get_chat_client


class GPTEvaluationTemplate(ABC):
    """
    Abstract base class for GPT-based evaluations using Template Method Pattern.
    
    Defines the algorithm skeleton for GPT evaluation:
    1. Build evaluation prompt (system prompt + idea + task instruction) 
    2. Execute LLM call
    3. Process and format result based on evaluation type
    
    Subclasses must implement the abstract methods to customize evaluation behavior.
    """
    
    def __init__(self, evaluation_type: str):
        """
        Initialize GPT evaluation template.
        Refactored with Template Method Pattern.
        
        Args:
            evaluation_type: Type of evaluation ("feasibility", "novelty", "significance")
        """
        self.evaluation_type = evaluation_type.lower()
        self._chat_client = get_chat_client()  # Refactored with Factory Method Pattern
        
    # =============== Abstract Methods to be implemented by subclasses ===============
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get evaluation-specific system prompt. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_task_instruction(self) -> str:
        """Get evaluation-specific task instruction. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def process_result(self, raw_response: str) -> t.Union[str, t.Tuple[t.List[str], str]]:
        """Process evaluation result into final format. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def handle_error(self, error: Exception) -> t.Union[str, t.Tuple[t.List[str], str]]:
        """Handle evaluation errors. Must be implemented by subclasses."""
        pass
    
    def generate_evaluation(self, idea_text: str) -> t.Union[str, t.Tuple[t.List[str], str]]:
        """
        Template method for GPT evaluation.
        Defines the algorithm skeleton for simple LLM evaluation.
        
        Args:
            idea_text: Research idea text to evaluate
            
        Returns:
            For feasibility: Tuple of (concerns_list, raw_response)
            For others: Evaluation text string
        """
        try:
            # Step 1: Build evaluation prompt (system prompt + idea + task instruction)
            prompt = self._build_prompt(idea_text)
            
            # Step 2: Execute LLM call
            raw_response = self._chat_client.chat(prompt)
            
            # Step 3: Process and format result based on evaluation type
            return self.process_result(raw_response)
            
        except Exception as e:
            return self.handle_error(e)
    
    def _build_prompt(self, idea_text: str) -> str:
        """Build evaluation prompt by combining system prompt, idea, and task instruction."""
        system_prompt = self.get_system_prompt()
        task_instruction = self.get_task_instruction()
        
        prompt = (
            system_prompt
            + "\n\n"
            + "Idea to review:\n\n"
            + idea_text.strip()
            + "\n\n"
            + task_instruction
        )
        
        return prompt
    


# ============= Factory Functions for Different Evaluation Types =============
# Create specific evaluator instances using concrete subclasses

def create_feasibility_evaluator():
    """Create GPT feasibility evaluator using concrete subclass."""
    from ..gpt_feasibility_evaluator import FeasibilityGPTEvaluator
    return FeasibilityGPTEvaluator()

def create_novelty_evaluator():
    """Create GPT novelty evaluator using concrete subclass."""
    from ..gpt_novelty_evaluator import NoveltyGPTEvaluator
    return NoveltyGPTEvaluator()

def create_significance_evaluator():
    """Create GPT significance evaluator using concrete subclass.""" 
    from ..gpt_significance_evaluator import SignificanceGPTEvaluator
    return SignificanceGPTEvaluator()

def create_score_evaluator():
    """Create GPT score evaluator using concrete subclass."""
    from ..gpt_score_evaluator import ScoreGPTEvaluator
    return ScoreGPTEvaluator()


# ============= Unified API Functions =============
# Factory function to create appropriate evaluator based on type

def generate_gpt_evaluation(idea_text: str, evaluation_type: str) -> t.Union[str, t.Tuple[t.List[str], str]]:
    """
    Unified GPT evaluation function using concrete subclasses.
    
    Args:
        idea_text: Research idea text to evaluate
        evaluation_type: Type of evaluation ("feasibility", "novelty", "significance", "feasibility_score")
        
    Returns:
        For feasibility: Tuple of (concerns_list, raw_response)
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