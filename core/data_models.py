# bzy_modified: Data models for Facade layer
"""
Data structures for evaluation inputs and outputs.

These dataclasses define the interface between the Facade layer (Layer 5)
and the underlying design pattern layers (Layers 1-4).
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class EvaluationMethod(Enum):
    """Supported evaluation methods."""
    INSTRUCTOR = "instructor"
    GPT = "gpt"
    RAG = "rag"


class EvaluationType(Enum):
    """Types of evaluations supported by the system."""
    FEASIBILITY = "feasibility"
    FEASIBILITY_SCORE = "feasibility_score"
    NOVELTY = "novelty"
    SIGNIFICANCE = "significance"


@dataclass
class IdeaContext:
    """Context information for an idea being evaluated."""
    idea_id: str
    title: str
    description: str
    paper_id: Optional[str] = None
    review_id: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate context after initialization."""
        if not self.idea_id or not self.idea_id.strip():
            raise ValueError("idea_id must not be empty")
        if not self.title or not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description or not self.description.strip():
            raise ValueError("description must not be empty")


@dataclass
class EvaluationInput:
    """Input specification for a single evaluation."""
    idea: IdeaContext
    evaluation_type: EvaluationType
    evaluation_method: EvaluationMethod
    model_config: Optional[Dict[str, Any]] = None  # Provider-specific config
    retrieval_config: Optional[Dict[str, Any]] = None  # Ranking strategy config
    
    def __post_init__(self):
        """Validate input after initialization."""
        if not self.idea:
            raise ValueError("idea must not be None")
        if not self.idea.idea_id or not self.idea.idea_id.strip():
            raise ValueError("idea_id must not be empty")
        if not self.idea.title or not self.idea.title.strip():
            raise ValueError("idea title must not be empty")
        if not self.idea.description or not self.idea.description.strip():
            raise ValueError("idea description must not be empty")


@dataclass
class EvaluationResult:
    """Result from a single evaluation."""
    evaluation_input: EvaluationInput
    success: bool
    evaluation_text: Optional[str] = None
    score: Optional[Union[int, float]] = None
    coverage_analysis: Optional[Dict[str, Any]] = None  # For feasibility evaluations
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_scored(self) -> bool:
        """Check if evaluation has a numeric score."""
        return self.score is not None and not self.error_message


@dataclass
class BatchEvaluationInput:
    """Input specification for batch evaluation."""
    ideas: List[IdeaContext]
    evaluation_type: EvaluationType
    evaluation_method: EvaluationMethod
    model_config: Optional[Dict[str, Any]] = None
    retrieval_config: Optional[Dict[str, Any]] = None
    batch_size: int = 5  # Process N ideas in parallel
    
    def __post_init__(self):
        """Validate batch input."""
        if not self.ideas:
            raise ValueError("ideas list must not be empty")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        
        for idea in self.ideas:
            if not idea.idea_id or not idea.title or not idea.description:
                raise ValueError(f"All ideas must have id, title, and description: {idea}")


@dataclass
class BatchEvaluationResult:
    """Results from batch evaluation."""
    batch_input: BatchEvaluationInput
    results: List[EvaluationResult]
    total_success: int
    total_failed: int
    execution_time_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total = len(self.results)
        return (self.total_success / total * 100) if total > 0 else 0.0
