# bzy_modified: Facade pattern layer implementation
"""
Evaluation Facade: Orchestrates multiple design pattern layers.

This facade provides a unified interface for conducting idea evaluations.
It coordinates between:
- Layer 1: AbstractFactory + Adapter (LLM clients)
- Layer 2: Strategy (Retrieval ranking)
- Layer 3: Template Method (Evaluation flow)
- Layer 4: Strategy (Scoring and coverage comparison)

Responsibilities:
1. Accept evaluation requests in unified format (EvaluationInput)
2. Route to appropriate Template Method based on evaluation type
3. Apply Strategy patterns for scoring and coverage analysis
4. Return results in unified format (EvaluationResult)
"""

import time
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = str(Path(__file__).parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.data_models import (
    EvaluationInput, EvaluationResult, BatchEvaluationInput,
    BatchEvaluationResult, EvaluationType, EvaluationMethod, IdeaContext
)

logger = logging.getLogger(__name__)


class EvaluationFacade:
    """
    Unified facade for conducting idea evaluations.
    
    Orchestrates multiple design pattern layers to provide a simple,
    consistent interface for evaluation operations.
    """
    
    # Mapping of evaluation types to their Template Method classes
    TEMPLATE_CLASSES = None  # Lazy loaded
    
    def __init__(self):
        """Initialize facade with factory clients."""
        # Create factory instances for LLM clients
        try:
            from LLM_service.llm_factory import ChatFactory, EmbeddingFactory, DEFAULT_CHAT_PRIORITY, DEFAULT_EMBEDDING_PRIORITY
            self.chat_factory = ChatFactory(DEFAULT_CHAT_PRIORITY)
            self.embedding_factory = EmbeddingFactory(DEFAULT_EMBEDDING_PRIORITY)
        except Exception as e:
            logger.warning(f"Failed to initialize factories: {e}")
            self.chat_factory = None
            self.embedding_factory = None
        
        # Cache for Template Method instances
        self._template_cache: Dict[str, Any] = {}
        
        logger.info("EvaluationFacade initialized")
    
    def _get_template(
        self,
        method: EvaluationMethod,
        evaluation_type: EvaluationType
    ) -> Any:
        """
        Get or create a Template Method instance for the given method and type.
        
        Args:
            method: Evaluation method (INSTRUCTOR, GPT, RAG)
            evaluation_type: Type of evaluation (FEASIBILITY, NOVELTY, etc.)
            
        Returns:
            Template Method instance ready for evaluation
        """
        # Lazy load template classes
        if EvaluationFacade.TEMPLATE_CLASSES is None:
            try:
                from Template.abstract.ins_evaluation_template import InstructorEvaluationTemplate
                from Template.abstract.gpt_evaluation_template import GPTEvaluationTemplate
                from Template.abstract.rag_evaluation_template import RAGEvaluationTemplate
                
                EvaluationFacade.TEMPLATE_CLASSES = {
                    EvaluationMethod.INSTRUCTOR: InstructorEvaluationTemplate,
                    EvaluationMethod.GPT: GPTEvaluationTemplate,
                    EvaluationMethod.RAG: RAGEvaluationTemplate,
                }
            except Exception as e:
                raise RuntimeError(f"Failed to load template classes: {e}")
        
        cache_key = f"{method.value}_{evaluation_type.value}"
        
        if cache_key not in self._template_cache:
            template_class = EvaluationFacade.TEMPLATE_CLASSES.get(method)
            if not template_class:
                raise ValueError(f"Unsupported evaluation method: {method}")
            
            template = template_class(evaluation_type.value)
            self._template_cache[cache_key] = template
            logger.debug(f"Created template for {cache_key}")
        
        return self._template_cache[cache_key]
    
    def evaluate_feasibility(
        self,
        idea: IdeaContext,
        method: EvaluationMethod = EvaluationMethod.INSTRUCTOR
    ) -> EvaluationResult:
        """
        Evaluate feasibility of an idea.
        
        Args:
            idea: IdeaContext with idea details
            method: Evaluation method (default: INSTRUCTOR)
            
        Returns:
            EvaluationResult with evaluation text and coverage analysis
        """
        evaluation_input = EvaluationInput(
            idea=idea,
            evaluation_type=EvaluationType.FEASIBILITY,
            evaluation_method=method
        )
        
        return self._execute_evaluation(evaluation_input)
    
    def evaluate_novelty(
        self,
        idea: IdeaContext,
        method: EvaluationMethod = EvaluationMethod.INSTRUCTOR
    ) -> EvaluationResult:
        """
        Evaluate novelty of an idea.
        
        Args:
            idea: IdeaContext with idea details
            method: Evaluation method (default: INSTRUCTOR)
            
        Returns:
            EvaluationResult with evaluation text (no scoring in this method)
        """
        evaluation_input = EvaluationInput(
            idea=idea,
            evaluation_type=EvaluationType.NOVELTY,
            evaluation_method=method
        )
        
        return self._execute_evaluation(evaluation_input)
    
    def evaluate_significance(
        self,
        idea: IdeaContext,
        method: EvaluationMethod = EvaluationMethod.INSTRUCTOR
    ) -> EvaluationResult:
        """
        Evaluate significance of an idea.
        
        Args:
            idea: IdeaContext with idea details
            method: Evaluation method (default: INSTRUCTOR)
            
        Returns:
            EvaluationResult with evaluation text (no scoring in this method)
        """
        evaluation_input = EvaluationInput(
            idea=idea,
            evaluation_type=EvaluationType.SIGNIFICANCE,
            evaluation_method=method
        )
        
        return self._execute_evaluation(evaluation_input)
    
    def evaluate_feasibility_score(
        self,
        idea: IdeaContext,
        method: EvaluationMethod = EvaluationMethod.INSTRUCTOR
    ) -> EvaluationResult:
        """
        Evaluate and score feasibility of an idea.
        
        This generates an evaluation and then applies FeasibilityScoringStrategy
        to produce a numeric score (1-10).
        
        Args:
            idea: IdeaContext with idea details
            method: Evaluation method (default: INSTRUCTOR)
            
        Returns:
            EvaluationResult with evaluation text and numeric score
        """
        evaluation_input = EvaluationInput(
            idea=idea,
            evaluation_type=EvaluationType.FEASIBILITY_SCORE,
            evaluation_method=method
        )
        
        return self._execute_evaluation(evaluation_input)
    
    def _execute_evaluation(self, evaluation_input: EvaluationInput) -> EvaluationResult:
        """
        Execute a single evaluation.
        
        Core orchestration logic:
        1. Get Template Method for the specified method type
        2. Execute evaluation template (Layer 3)
        3. Apply Scoring/Coverage Strategies if needed (Layer 4)
        4. Return result in unified format
        
        Args:
            evaluation_input: EvaluationInput specification
            
        Returns:
            EvaluationResult with evaluation outcomes
        """
        try:
            # Get Template Method instance (Layer 3)
            template = self._get_template(
                evaluation_input.evaluation_method,
                evaluation_input.evaluation_type
            )
            
            # Construct idea text for evaluation
            idea_text = self._format_idea_text(evaluation_input.idea)
            
            # Execute Template Method to generate evaluation
            logger.debug(f"Executing template for {evaluation_input.evaluation_type.value}")
            evaluation_result = template.generate_evaluation(idea_text)
            
            # Parse result based on evaluation type
            if evaluation_input.evaluation_type == EvaluationType.FEASIBILITY:
                # Feasibility returns tuple: (concerns_list, raw_response)
                if isinstance(evaluation_result, tuple):
                    concerns, raw_response = evaluation_result
                    evaluation_text = raw_response
                    # Extract original concerns from additional_info if available
                    original_concerns = None
                    if evaluation_input.idea.additional_info:
                        original_concerns = evaluation_input.idea.additional_info.get(
                            "concerns"
                        ) or evaluation_input.idea.additional_info.get(
                            "original_concerns"
                        )
                    # Use coverage comparison strategy if original concerns are available
                    coverage_analysis = self._analyze_coverage(
                        concerns,
                        original_concerns=original_concerns,
                        strategy=evaluation_input.model_config.get("coverage_strategy", "llm")
                        if evaluation_input.model_config else "llm"
                    )
                else:
                    evaluation_text = evaluation_result
                    coverage_analysis = None
            else:
                evaluation_text = evaluation_result
                coverage_analysis = None
            
            # Apply Scoring Strategy if needed (Layer 4)
            score = None
            if evaluation_input.evaluation_type in [
                EvaluationType.FEASIBILITY_SCORE,
                EvaluationType.NOVELTY,
                EvaluationType.SIGNIFICANCE
            ]:
                score = self._score_evaluation(
                    evaluation_text,
                    evaluation_input.evaluation_type
                )
            
            return EvaluationResult(
                evaluation_input=evaluation_input,
                success=True,
                evaluation_text=evaluation_text,
                score=score,
                coverage_analysis=coverage_analysis,
                metadata={"method": evaluation_input.evaluation_method.value}
            )
        
        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            return EvaluationResult(
                evaluation_input=evaluation_input,
                success=False,
                error_message=str(e),
                metadata={"method": evaluation_input.evaluation_method.value}
            )
    
    def _format_idea_text(self, idea: IdeaContext) -> str:
        """
        Format idea context into text for template evaluation.
        
        Args:
            idea: IdeaContext with idea details
            
        Returns:
            Formatted idea text
        """
        text = f"Title: {idea.title}\n\nDescription: {idea.description}"
        
        if idea.additional_info:
            for key, value in idea.additional_info.items():
                text += f"\n{key}: {value}"
        
        return text
    
    def _score_evaluation(
        self,
        evaluation_text: str,
        evaluation_type: EvaluationType
    ) -> Optional[Union[int, float]]:
        """
        Apply Scoring Strategy based on evaluation type (Layer 4).
        
        Args:
            evaluation_text: Generated evaluation text
            evaluation_type: Type of evaluation
            
        Returns:
            Numeric score or None if scoring failed
        """
        try:
            if not self.chat_factory:
                logger.warning("Chat factory not available for scoring")
                return None
            
            chat_client = self.chat_factory.create()
            
            # Lazy import strategies
            try:
                from Strategies.evaluation_strategies import (
                    NoveltyScoringStrategy,
                    FeasibilityScoringStrategy,
                    SignificanceScoringStrategy
                )
            except Exception as e:
                logger.warning(f"Failed to import scoring strategies: {e}")
                return None
            
            if evaluation_type == EvaluationType.FEASIBILITY_SCORE:
                strategy = FeasibilityScoringStrategy(chat_client)
            elif evaluation_type == EvaluationType.NOVELTY:
                strategy = NoveltyScoringStrategy(chat_client)
            elif evaluation_type == EvaluationType.SIGNIFICANCE:
                strategy = SignificanceScoringStrategy(chat_client)
            else:
                return None
            
            # Get score from strategy
            score_result = strategy.score(evaluation_text)
            
            # Parse score from result
            return self._extract_score(score_result)
        
        except Exception as e:
            logger.warning(f"Scoring failed: {e}")
            return None
    
    def _extract_score(self, score_result: str) -> Optional[Union[int, float]]:
        """
        Extract numeric score from strategy result text.
        
        Expected format: "... Score: X" where X is int or float.
        
        Args:
            score_result: Raw result from scoring strategy
            
        Returns:
            Numeric score or None if extraction failed
        """
        import re
        
        try:
            # Look for "Score: X" pattern
            match = re.search(r'Score:\s*([\d.]+)', score_result)
            if match:
                score_str = match.group(1)
                # Try parsing as float, then int
                if '.' in score_str:
                    return float(score_str)
                else:
                    return int(score_str)
        except Exception as e:
            logger.warning(f"Failed to extract score: {e}")
        
        return None
    
    def _analyze_coverage(
        self,
        concerns: List[str],
        original_concerns: Optional[List[str]] = None,
        strategy: Optional[str] = "llm"
    ) -> Dict[str, Any]:
        """
        Analyze coverage of concerns using CoverageCompareStrategy (Layer 4).
        
        If original_concerns is provided, compares generated concerns against them.
        Otherwise, returns a simple summary of generated concerns.
        
        Args:
            concerns: List of generated concerns from feasibility evaluation
            original_concerns: Optional list of original (gold standard) concerns to compare against
            strategy: Strategy to use ("llm" or "embedding")
            
        Returns:
            Coverage analysis result
        """
        if not concerns:
            return {"per_item": [], "summary": {"covered_count": 0, "total": 0}}
        
        # If no original concerns provided, return simple summary
        if not original_concerns:
            return {
                "per_item": [{"concern": c} for c in concerns],
                "summary": {
                    "covered_count": len(concerns),
                    "total": len(concerns)
                }
            }
        
        # Use CoverageCompareStrategy to compare
        try:
            if strategy == "embedding":
                if not self.embedding_factory:
                    logger.warning("Embedding factory not available, falling back to LLM")
                    strategy = "llm"
                else:
                    embedding_client = self.embedding_factory.create()
                    from Strategies.evaluation_strategies import EmbeddingCoverageCompareStrategy
                    compare_strategy = EmbeddingCoverageCompareStrategy(embedding_client)
                    coverage_result, _ = compare_strategy.compare(original_concerns, concerns)
                    return coverage_result
            
            # Default to LLM strategy
            if not self.chat_factory:
                logger.warning("Chat factory not available for coverage comparison")
                return {
                    "per_item": [{"concern": c} for c in concerns],
                    "summary": {
                        "covered_count": len(concerns),
                        "total": len(concerns)
                    }
                }
            
            chat_client = self.chat_factory.create()
            from Strategies.evaluation_strategies import LLMCoverageCompareStrategy
            compare_strategy = LLMCoverageCompareStrategy(chat_client)
            coverage_result, _ = compare_strategy.compare(original_concerns, concerns)
            return coverage_result
            
        except Exception as e:
            logger.warning(f"Coverage comparison failed: {e}, returning simple summary")
            return {
                "per_item": [{"concern": c} for c in concerns],
                "summary": {
                    "covered_count": len(concerns),
                    "total": len(concerns)
                }
            }
    
    def batch_evaluate(
        self,
        batch_input: BatchEvaluationInput
    ) -> BatchEvaluationResult:
        """
        Evaluate a batch of ideas.
        
        Args:
            batch_input: Batch evaluation specification with list of ideas
            
        Returns:
            BatchEvaluationResult with results for all ideas
        """
        start_time = time.time()
        results: List[EvaluationResult] = []
        
        logger.info(f"Starting batch evaluation of {len(batch_input.ideas)} ideas")
        
        for idea in batch_input.ideas:
            try:
                evaluation_input = EvaluationInput(
                    idea=idea,
                    evaluation_type=batch_input.evaluation_type,
                    evaluation_method=batch_input.evaluation_method
                )
                result = self._execute_evaluation(evaluation_input)
                results.append(result)
                logger.debug(f"Completed evaluation for idea {idea.idea_id}")
            
            except Exception as e:
                logger.error(f"Failed to evaluate idea {idea.idea_id}: {e}")
                result = EvaluationResult(
                    evaluation_input=EvaluationInput(
                        idea=idea,
                        evaluation_type=batch_input.evaluation_type,
                        evaluation_method=batch_input.evaluation_method
                    ),
                    success=False,
                    error_message=str(e)
                )
                results.append(result)
        
        execution_time = time.time() - start_time
        total_success = sum(1 for r in results if r.success)
        total_failed = len(results) - total_success
        
        batch_result = BatchEvaluationResult(
            batch_input=batch_input,
            results=results,
            total_success=total_success,
            total_failed=total_failed,
            execution_time_seconds=execution_time
        )
        
        logger.info(
            f"Batch evaluation complete: {total_success} succeeded, "
            f"{total_failed} failed in {execution_time:.2f}s"
        )
        
        return batch_result
