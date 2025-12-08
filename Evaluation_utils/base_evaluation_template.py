"""
Base Evaluation Template using Template Method Pattern.
Abstract base class for all evaluation templates (GPT, RAG, Instructor Agent).

This base class defines ONLY the algorithm skeleton (execution steps).
It does NOT import or depend on any concrete implementations.
"""

from abc import ABC, abstractmethod
import typing as t

class BaseEvaluationTemplate(ABC):
    """
    Abstract base class for all evaluation templates.
    Defines ONLY the algorithm skeleton (execution steps) without concrete implementation.
    
    Template Method Pattern: This class defines the steps, subclasses implement the details.
    """
    
    def __init__(self, evaluation_type: str):
        """
        Initialize base evaluation template.
        
        Args:
            evaluation_type: Type of evaluation ("feasibility", "novelty", "significance", "feasibility_score")
        """
        self.evaluation_type = evaluation_type.lower()
        self.initialize_components()
    
    # =============== Template Method - ONLY Algorithm Skeleton ===============
    
    def evaluate(self, idea_text: str) -> t.Union[str, t.List[str], t.Tuple[t.List[str], str]]:
        """
        Template Method: Defines ONLY the evaluation algorithm steps.
        Contains NO concrete implementation - only the execution sequence.
        
        Algorithm Skeleton:
        1. Prepare evaluation context
        2. Build evaluation prompt 
        3. Execute evaluation
        4. Process and format result
        5. Handle any errors
        
        Args:
            idea_text: Research idea text to evaluate
            
        Returns:
            Evaluation result (format defined by subclass implementation)
        """
        try:
            # Step 1: Prepare evaluation context (let subclass decide what this means)
            self.prepare_evaluation_context(idea_text)
            
            # Step 2: Build evaluation prompt (subclass defines how)
            prompt = self.build_evaluation_prompt(idea_text)
            
            # Step 3: Execute evaluation (subclass defines the engine/method)
            raw_result = self.execute_evaluation(idea_text, prompt)
            
            # Step 4: Process result (subclass defines the processing logic)
            processed_result = self.process_evaluation_result(raw_result)
            
            # Step 5: Format final output (subclass defines the format)
            return self.format_final_result(processed_result)
            
        except Exception as e:
            # Error handling step (subclass defines error handling strategy)
            return self.handle_evaluation_error(e)
    
    # =============== Abstract Methods - ALL Concrete Steps Must Be Implemented ===============
    
    @abstractmethod
    def initialize_components(self):
        """
        Step: Initialize evaluation components.
        Subclass defines what components are needed (LLM client, agents, retrieval systems, etc.)
        """
        pass
    
    @abstractmethod
    def prepare_evaluation_context(self, idea_text: str):
        """
        Step: Prepare evaluation context.
        Subclass defines what preparation is needed before evaluation.
        
        Args:
            idea_text: Research idea text
        """
        pass
    
    @abstractmethod
    def build_evaluation_prompt(self, idea_text: str) -> str:
        """
        Step: Build evaluation prompt.
        Subclass defines how to construct the prompt for their specific engine.
        
        Args:
            idea_text: Research idea text
            
        Returns:
            Formatted prompt string
        """
        pass
    
    @abstractmethod
    def execute_evaluation(self, idea_text: str, prompt: str) -> t.Any:
        """
        Step: Execute the evaluation.
        Subclass defines the evaluation execution strategy (GPT call, Agent execution, RAG retrieval+generation).
        
        Args:
            idea_text: Research idea text
            prompt: Formatted prompt
            
        Returns:
            Raw evaluation result (type depends on implementation)
        """
        pass
    
    @abstractmethod 
    def process_evaluation_result(self, raw_result: t.Any) -> t.Any:
        """
        Step: Process raw evaluation result.
        Subclass defines how to process and clean up the raw result.
        
        Args:
            raw_result: Raw result from execute_evaluation
            
        Returns:
            Processed result (type depends on implementation)
        """
        pass
    
    @abstractmethod
    def format_final_result(self, processed_result: t.Any) -> t.Union[str, t.List[str], t.Tuple[t.List[str], str]]:
        """
        Step: Format final result.
        Subclass defines the final output format based on evaluation type and engine.
        
        Args:
            processed_result: Processed result from process_evaluation_result
            
        Returns:
            Final formatted result
        """
        pass
    
    @abstractmethod
    def handle_evaluation_error(self, error: Exception) -> t.Union[str, t.List[str]]:
        """
        Step: Handle evaluation errors.
        Subclass defines error handling strategy.
        
        Args:
            error: Exception that occurred during evaluation
            
        Returns:
            Error response (format depends on implementation)
        """
        pass
    
    # =============== Utility Methods - Only Basic Information Access ===============
    
    def get_evaluation_type(self) -> str:
        """Get the evaluation type."""
        return self.evaluation_type
    
    def is_feasibility_evaluation(self) -> bool:
        """Check if this is a feasibility evaluation."""
        return self.evaluation_type == "feasibility"
    
    def __str__(self) -> str:
        """String representation of the evaluator."""
        return f"{self.__class__.__name__}(evaluation_type='{self.evaluation_type}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()

# =============== End of Base Template Class ===============
# 
# Note: Factory functions should be implemented OUTSIDE this file
# to avoid circular imports. The base class should not know about
# its concrete implementations.
#
# Proper usage:
# 1. Import BaseEvaluationTemplate in your concrete classes
# 2. Create factory functions in a separate factory module
# 3. Or create factories in the concrete template files themselves
