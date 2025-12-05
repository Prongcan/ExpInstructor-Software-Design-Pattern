import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from service.llm_factory import get_chat_client  # Refactored with Factory Method Pattern
from service.strategies import NoveltyScoringStrategy  # Refactored with Strategy Pattern

# Refactored with Strategy Pattern: use scoring strategy
_scoring_strategy = NoveltyScoringStrategy(get_chat_client())


def generate_novelty_score(evaluation_text: str) -> str:
    """
    Generate novelty score using scoring strategy.
    Refactored with Strategy Pattern.
    """
    return _scoring_strategy.score(evaluation_text)
