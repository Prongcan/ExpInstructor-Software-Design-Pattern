import os
import json
import time
import typing as t
from dataclasses import dataclass

import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from service.llm_factory import get_chat_client, get_embedding_client  # Refactored with Factory Method Pattern
from service.strategies import LLMCoverageCompareStrategy, EmbeddingCoverageCompareStrategy  # Refactored with Strategy Pattern

# Refactored with Strategy Pattern: use coverage comparison strategies
_llm_coverage_strategy = LLMCoverageCompareStrategy(get_chat_client(preferred="deepseek"))
_embedding_coverage_strategy = EmbeddingCoverageCompareStrategy(get_embedding_client())


def compare_coverage_via_llm(original: t.List[str], generated: t.List[str]) -> t.Tuple[dict, str]:
    """
    Compare coverage using LLM strategy.
    Refactored with Strategy Pattern.
    """
    return _llm_coverage_strategy.compare(original, generated)


def cosine_similarity(a: t.List[float], b: t.List[float]) -> float:
    """Helper function for cosine similarity calculation."""
    import math
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def semantic_match_scores(original: t.List[str], generated: t.List[str], model: str = "text-embedding-3-small") -> dict:
    """
    Compute semantic match scores using embedding strategy.
    Refactored with Strategy Pattern: uses EmbeddingCoverageCompareStrategy internally.
    """
    if not generated:
        return {"per_generated": [], "summary": {"avg_best": 0.0, "max_best": 0.0}}

    # Use embedding strategy for comparison
    result, _ = _embedding_coverage_strategy.compare(original, generated)
    
    # Transform result to match expected format
    per_generated = []
    best_scores = []
    
    # Get embeddings for generated items
    from service.llm_factory import get_embedding_client
    embedding_client = get_embedding_client()
    emb_gen = embedding_client.embed_texts(generated, model=model)
    emb_ori = embedding_client.embed_texts(original, model=model) if original else []
    
    for gi, g_vec in enumerate(emb_gen):
        if not emb_ori:
            per_generated.append({"text": generated[gi], "best_match_index": -1, "best_score": 0.0})
            best_scores.append(0.0)
            continue
        scores = [cosine_similarity(g_vec, o_vec) for o_vec in emb_ori]
        best_idx = max(range(len(scores)), key=lambda i: scores[i])
        best = scores[best_idx]
        per_generated.append({"text": generated[gi], "best_match_index": best_idx, "best_score": best})
        best_scores.append(best)

    avg_best = sum(best_scores) / len(best_scores) if best_scores else 0.0
    max_best = max(best_scores) if best_scores else 0.0
    return {"per_generated": per_generated, "summary": {"avg_best": avg_best, "max_best": max_best}}
