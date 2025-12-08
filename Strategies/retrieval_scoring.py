"""
Strategy Pattern implementations for ranking and scoring.
Refactored with Strategy Pattern.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import math
import json
import re


# ============================================================================
# Retrieval Ranking Strategies
# ============================================================================

class RetrievalRankingStrategy(ABC):
    """Abstract strategy for ranking retrieval candidates."""
    
    @abstractmethod
    def rank_nodes(
        self, 
        query_vec: List[float], 
        candidate_vectors: List[List[float]], 
        candidate_names: List[str],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rank nodes by similarity to query vector.
        
        Args:
            query_vec: Query embedding vector
            candidate_vectors: List of candidate node embedding vectors
            candidate_names: List of candidate node names (same order as vectors)
            k: Number of top results to return
            
        Returns:
            List of dicts with "node" and "similarity" keys, sorted by similarity descending
        """
        pass
    
    @abstractmethod
    def rank_edges(
        self,
        query_vec: List[float],
        candidate_vectors: List[List[float]],
        candidate_triplets: List[Tuple],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rank edges by similarity to query vector.
        
        Args:
            query_vec: Query embedding vector
            candidate_vectors: List of candidate edge embedding vectors
            candidate_triplets: List of (source, target, attrs) tuples
            k: Number of top results to return
            
        Returns:
            List of dicts with edge info and similarity scores
        """
        pass


class CosineSimilarityRankingStrategy(RetrievalRankingStrategy):
    """Default strategy using cosine similarity for ranking."""
    
    def rank_nodes(
        self, 
        query_vec: List[float], 
        candidate_vectors: List[List[float]], 
        candidate_names: List[str],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank nodes using cosine similarity."""
        if not candidate_vectors or not candidate_names:
            return []
        
        query_norm = sum(a * a for a in query_vec) ** 0.5
        if query_norm == 0:
            return []
        
        similarities = []
        for idx, vec in enumerate(candidate_vectors):
            vec_norm = sum(a * a for a in vec) ** 0.5
            if vec_norm == 0:
                similarity = 0.0
            else:
                dot_product = sum(a * b for a, b in zip(query_vec, vec))
                similarity = dot_product / (query_norm * vec_norm)
            
            similarities.append({
                "node": candidate_names[idx],
                "similarity": similarity
            })
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:k]
    
    def rank_edges(
        self,
        query_vec: List[float],
        candidate_vectors: List[List[float]],
        candidate_triplets: List[Tuple],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank edges using cosine similarity."""
        if not candidate_vectors or not candidate_triplets:
            return []
        
        query_norm = sum(a * a for a in query_vec) ** 0.5
        if query_norm == 0:
            return []
        
        similarities = []
        for idx, vec in enumerate(candidate_vectors):
            vec_norm = sum(a * a for a in vec) ** 0.5
            if vec_norm == 0:
                similarity = 0.0
            else:
                dot_product = sum(a * b for a, b in zip(query_vec, vec))
                similarity = dot_product / (query_norm * vec_norm)
            
            source, target, attrs = candidate_triplets[idx]
            similarities.append({
                "source": source,
                "target": target,
                "relationship": attrs.get('relationship', ''),
                "evidence": attrs.get('evidence', ''),
                "similarity": similarity,
                "paper_id": attrs.get('paper_id', ''),
                "review_id": attrs.get('review_id', '')
            })
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:k]


class BM25RankingStrategy(RetrievalRankingStrategy):
    """Strategy using BM25 scoring for ranking (keyword-based)."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Args:
            k1: BM25 k1 parameter (term frequency saturation)
            b: BM25 b parameter (length normalization)
        """
        self.k1 = k1
        self.b = b
        self._cosine_strategy = CosineSimilarityRankingStrategy()
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return text.lower().split()
    
    def _bm25_score(self, query_tokens: List[str], doc_tokens: List[str], avg_doc_len: float) -> float:
        """Compute BM25 score."""
        score = 0.0
        doc_len = len(doc_tokens)
        
        # Term frequency in document
        tf = {}
        for token in doc_tokens:
            tf[token] = tf.get(token, 0) + 1
        
        for query_token in query_tokens:
            if query_token in tf:
                freq = tf[query_token]
                # BM25 formula
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * (doc_len / avg_doc_len))
                score += numerator / denominator
        
        return score
    
    def rank_nodes(
        self, 
        query_vec: List[float], 
        candidate_vectors: List[List[float]], 
        candidate_names: List[str],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rank nodes using BM25 (keyword-based) combined with vector similarity.
        Falls back to cosine similarity if text matching is not possible.
        """
        # For node names, use a simple BM25-like scoring based on name overlap
        # Note: This is a simplified version; full BM25 would need document content
        query_tokens = self._tokenize(" ".join([str(query_vec[:5])]))  # Use first few dimensions as proxy
        
        # Fallback to cosine similarity for now
        # (Full BM25 would require access to original node text content)
        return self._cosine_strategy.rank_nodes(query_vec, candidate_vectors, candidate_names, k)
    
    def rank_edges(
        self,
        query_vec: List[float],
        candidate_vectors: List[List[float]],
        candidate_triplets: List[Tuple],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rank edges using BM25 (keyword-based) combined with vector similarity.
        Falls back to cosine similarity if text matching is not possible.
        """
        # Fallback to cosine similarity for now
        # (Full BM25 would require access to original edge text content)
        return self._cosine_strategy.rank_edges(query_vec, candidate_vectors, candidate_triplets, k)


class HybridRankingStrategy(RetrievalRankingStrategy):
    """Strategy combining multiple ranking methods (e.g., BM25 + cosine + LLM)."""
    
    def __init__(
        self, 
        strategies: List[RetrievalRankingStrategy],
        weights: Optional[List[float]] = None
    ):
        """
        Args:
            strategies: List of ranking strategies to combine
            weights: Weights for each strategy (default: equal weights)
        """
        self.strategies = strategies
        self.weights = weights or [1.0 / len(strategies)] * len(strategies)
        
        if len(self.strategies) != len(self.weights):
            raise ValueError("Number of strategies must match number of weights")
    
    def _merge_rankings(
        self, 
        rankings: List[List[Dict[str, Any]]], 
        k: int
    ) -> List[Dict[str, Any]]:
        """Merge multiple rankings using weighted scores."""
        # Collect all unique items
        all_items = {}
        
        for strategy_idx, ranking in enumerate(rankings):
            weight = self.weights[strategy_idx]
            for rank_idx, item in enumerate(ranking):
                # Get item identifier
                item_id = item.get("node") or f"{item.get('source')}_{item.get('target')}"
                
                if item_id not in all_items:
                    all_items[item_id] = {
                        "item": item,
                        "weighted_score": 0.0,
                        "count": 0
                    }
                
                # Add weighted score (inverse rank)
                score = item.get("similarity", 0.0)
                all_items[item_id]["weighted_score"] += weight * score
                all_items[item_id]["count"] += 1
        
        # Sort by weighted score
        sorted_items = sorted(
            all_items.values(),
            key=lambda x: x["weighted_score"],
            reverse=True
        )
        
        # Return top-k with updated similarity scores
        result = []
        for item_data in sorted_items[:k]:
            item = item_data["item"].copy()
            item["similarity"] = item_data["weighted_score"] / item_data["count"]
            result.append(item)
        
        return result
    
    def rank_nodes(
        self, 
        query_vec: List[float], 
        candidate_vectors: List[List[float]], 
        candidate_names: List[str],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank nodes using hybrid strategy."""
        rankings = []
        for strategy in self.strategies:
            ranking = strategy.rank_nodes(query_vec, candidate_vectors, candidate_names, k * 2)
            rankings.append(ranking)
        
        return self._merge_rankings(rankings, k)
    
    def rank_edges(
        self,
        query_vec: List[float],
        candidate_vectors: List[List[float]],
        candidate_triplets: List[Tuple],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank edges using hybrid strategy."""
        rankings = []
        for strategy in self.strategies:
            ranking = strategy.rank_edges(query_vec, candidate_vectors, candidate_triplets, k * 2)
            rankings.append(ranking)
        
        return self._merge_rankings(rankings, k)


class LLMRerankStrategy(RetrievalRankingStrategy):
    """Strategy using LLM for reranking after initial cosine similarity."""
    
    def __init__(self, chat_client, initial_k: int = 50):
        """
        Args:
            chat_client: IChatClient instance for LLM reranking
            initial_k: Number of candidates to retrieve before LLM reranking
        """
        self.chat_client = chat_client
        self.initial_k = initial_k
        self._cosine_strategy = CosineSimilarityRankingStrategy()
    
    def rank_nodes(
        self, 
        query_vec: List[float], 
        candidate_vectors: List[List[float]], 
        candidate_names: List[str],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank nodes using cosine similarity, then LLM reranking."""
        # First get more candidates using cosine similarity
        initial_results = self._cosine_strategy.rank_nodes(
            query_vec, candidate_vectors, candidate_names, k=self.initial_k
        )
        
        if len(initial_results) <= k:
            return initial_results
        
        # Prepare prompt for LLM reranking
        candidates_text = "\n".join([
            f"{i+1}. {result['node']} (similarity: {result['similarity']:.4f})"
            for i, result in enumerate(initial_results)
        ])
        
        prompt = f"""You are a retrieval ranking expert. Given a query and candidate nodes, 
select the top {k} most relevant nodes.

Query context: [Semantic search for knowledge entities]

Candidates:
{candidates_text}

Please return ONLY a JSON array of the top {k} node names (in order of relevance), 
like: ["node1", "node2", ...]
"""
        
        try:
            response = self.chat_client.chat(prompt)
            # Parse JSON response (simplified - may need more robust parsing)
            import json
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                ranked_names = json.loads(json_match.group())
                # Map back to similarity scores
                name_to_result = {r['node']: r for r in initial_results}
                reranked = [
                    name_to_result[name] for name in ranked_names 
                    if name in name_to_result
                ]
                return reranked[:k]
        except Exception as e:
            print(f"LLM reranking failed: {e}, falling back to cosine similarity")
        
        # Fallback to cosine similarity
        return initial_results[:k]
    
    def rank_edges(
        self,
        query_vec: List[float],
        candidate_vectors: List[List[float]],
        candidate_triplets: List[Tuple],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank edges using cosine similarity, then LLM reranking."""
        # First get more candidates using cosine similarity
        initial_results = self._cosine_strategy.rank_edges(
            query_vec, candidate_vectors, candidate_triplets, k=self.initial_k
        )
        
        if len(initial_results) <= k:
            return initial_results
        
        # Prepare prompt for LLM reranking
        candidates_text = "\n".join([
            f"{i+1}. {result['source']} --[{result['relationship']}]--> {result['target']}\n"
            f"   Evidence: {result['evidence'][:100]}... (similarity: {result['similarity']:.4f})"
            for i, result in enumerate(initial_results)
        ])
        
        prompt = f"""You are a retrieval ranking expert. Given a query and candidate edges, 
select the top {k} most relevant edges.

Query context: [Semantic search for knowledge relationships]

Candidates:
{candidates_text}

Please return ONLY a JSON array of indices (0-based) of the top {k} edges, 
like: [0, 3, 5, ...]
"""
        
        try:
            response = self.chat_client.chat(prompt)
            import json
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                ranked_indices = json.loads(json_match.group())
                reranked = [initial_results[i] for i in ranked_indices if 0 <= i < len(initial_results)]
                return reranked[:k]
        except Exception as e:
            print(f"LLM reranking failed: {e}, falling back to cosine similarity")
        
        # Fallback to cosine similarity
        return initial_results[:k]


# ============================================================================
# Scoring Strategies
# ============================================================================

class ScoringStrategy(ABC):
    """Abstract strategy for scoring evaluations."""
    
    @abstractmethod
    def score(self, evaluation_text: str) -> str:
        """
        Generate a score based on evaluation text.
        
        Args:
            evaluation_text: The evaluation text to score
            
        Returns:
            Score result (format depends on implementation)
        """
        pass


class NoveltyScoringStrategy(ScoringStrategy):
    """Strategy for scoring novelty evaluations."""
    
    def __init__(self, chat_client):
        self.chat_client = chat_client
        self._system_prompt = """You are a precise scorer. I will provide you with a professional evaluation of an academic idea,
and you need to give a novelty score based on this evaluation. The novelty score depends on the attitude of the evaluation.
If the evaluation is positive, the novelty score should be high; if the evaluation is negative, the novelty score should be low.
Please note that the novelty score ranges from 1 to 10, where 1 indicates the lowest novelty and 10 indicates the highest novelty.
Here are some examples(Some specific method or idea is replaced with Method A, Method B, Method C, etc.):

Example 1 (Low score case, score 1):
Evaluation: "The proposed method is not very different from Method A (Research A, 2023), Method B (Research B, 2023), and Method C (Research C, 2024). Especially, Method B also has an evaluation step in the pipeline, but on the node level."
Analysis: This evaluation clearly states that the proposed method is very similar to multiple existing works, with almost no novelty.
Score: 1

Example 2 (Low score case, score 2):
Evaluation: "Method X is a paper that already exists, focusing on a certain concept over multiple chains. It emphasizes divergent thinking rather than a linear thought structure concerning these inputs. Therefore, the proposed work does not appear to present novelty in terms of the prompt, the described structure, or the datasets on which it is tested on."
Analysis: The evaluation clearly states that related papers already exist, and the proposed work lacks novelty in multiple aspects.
Score: 2

Example 3 (Medium score case, score 6):
Evaluation: "Personally, I am not aware of similar works that describe a certain scenario where certain concepts are reversed. I do not find closely related works after a quick search using certain keywords. I'm fairly confident that the proposed approach is different from the existing works. After thinking further about the idea, I think it is similar to a certain method with some alternative approaches in the input prompt. However, I do not know similar papers off the top of my mind now."
Analysis: The evaluator acknowledges not finding similar works, but also mentions that it may be similar to some existing methods, showing a neutral attitude.
Score: 6

Example 4 (Medium-high score case, score 7):
Evaluation: "The proposed idea and framework of using a certain method with varied semantics, inspired by certain techniques from another field, which is clearly novel and makes major differences from all existing ideas. However, fundamentally, the notion of a certain approach by substituting similar concepts is very similar to existing studies, such as: (Research D, 2024). Therefore a score of 7 (between 6 and 8) is given."
Analysis: The evaluator believes some aspects are novel, but the core method is still similar to existing research, giving a medium-high score.
Score: 7

Example 5 (High score case, score 8):
Evaluation: "Combining Method A with Method B to improve a certain task for low-resource scenarios is a novel approach. While such hybrid methods have been explored in other contexts, their application to these specific forms is not widely covered, offering fresh insights and potential advancements in the field."
Analysis: The evaluator believes this is a novel method, and its application in this specific domain is new, showing a positive attitude.
Score: 8

Example 6 (High score case, score 10):
Evaluation: "While the framework of a certain method based on a certain technique is well known, the idea of trying to reach certain embedded concepts in models by bringing up pretty unrelated analogies about certain concepts in questions seems wildly novel! I would be very excited to see the results of this experiment."
Analysis: The evaluator uses strongly positive words such as "wildly novel" and "very excited", clearly expressing high recognition of the novelty.
Score: 10
"""
    
    def score(self, evaluation_text: str) -> str:
        """Score novelty evaluation."""
        prompt = (
            self._system_prompt
            + "\n\n"
            + "So now please start scoring formally: give me a score between 1 and 10 based on the following evaluation: \n\n"
            + evaluation_text.strip()
            + "\n\nPlease return an analysis of the evaluation and the final scoring result. "
            + "IMPORTANT: You must format your response with the score clearly marked at the end. "
            + "Use the exact format: 'Score: X' where X is an integer between 1 and 10. "
            + "For example, if your score is 7, end your response with 'Score: 7'."
        )
        try:
            return self.chat_client.chat(prompt)
        except Exception as e:
            return f"ERROR: {e}"


class FeasibilityScoringStrategy(ScoringStrategy):
    """Strategy for scoring feasibility evaluations."""
    
    def __init__(self, chat_client):
        self.chat_client = chat_client
        self._system_prompt = """You are a precise scorer. I will provide you with a professional peer review evaluation of an academic idea,
and you need to give a feasibility score based on this evaluation. Feasibility means whether the idea is easy to implement and execute and whether the idea is effective.
The feasibility score depends on how feasible and executable the idea is according to the evaluation.
Please note that the feasibility score ranges from 1 to 10, where 1 indicates the lowest feasibility and 10 indicates the highest feasibility.

IMPORTANT: The score should reflect the degree of feasibility and effectiveness as demonstrated in the evaluation text. You should judge the score based on:
1. The overall tone and assessment: Positive evaluations indicating high feasibility and effectiveness should lead to higher scores, while negative evaluations indicating significant challenges should lead to lower scores.
2. Implementation feasibility: Comments about ease of implementation, straightforward methods, available datasets, and clear execution plans should increase the score.
3. Effectiveness concerns: Concerns about whether the method will work, comparisons with baselines, and potential limitations should decrease the score.
4. Resource requirements: Comments about computational requirements, data collection challenges, and manual efforts should decrease the score.

Here are some examples based on real evaluation data:

Example 1 (Low-medium score case, score 4.5):
Evaluation: "The hardest part is data curation, but the evaluation set used in the paper would be a valuable contribution to the literature. The scope of the project needs to be clearly defined..."
Analysis: The evaluation acknowledges some positive aspects (evaluation set contribution, straightforward implementation) but identifies significant challenges: unclear scope definition, difficult data collection, fundamental limitations in predicting semantic change, and doubts about the core method's effectiveness.
Score: 4.5

Example 2 (Medium score case, score 5.0):
Evaluation: "I imagine step (2) in the proposed idea would be a little challenging in execution. Manual efforts would perhaps be involved..."
Analysis: The evaluation identifies specific execution challenges, including manual work requirements and dataset alignment issues. However, it acknowledges that implementation is straightforward with available datasets.
Score: 5.0

Example 3 (High score case, score 7.0):
Evaluation: "feasible as only tracking the intermediate status. intuitively thinking this should works. The experiments are fairly easy to implement..."
Analysis: The evaluation indicates the method is feasible with easy implementation, clear components, and a reasonable timeline.
Score: 7.0
"""
    
    def score(self, evaluation_text: str) -> str:
        """Score feasibility evaluation."""
        prompt = (
            self._system_prompt
            + "\n\n"
            + "So now please start scoring formally: give me a score between 1 and 10 based on the following peer review evaluation: \n\n"
            + "Evaluation: " + evaluation_text.strip()
            + "\n\nPlease return an analysis of the evaluation and the final scoring result. "
            + "IMPORTANT: You must format your response with the score clearly marked at the end. "
            + "Use the exact format: 'Score: X' where X is a number between 1 and 10 (can be a decimal like 4.5, 7.75, etc.). "
            + "For example, if your score is 7, end your response with 'Score: 7'. If your score is 7.5, end with 'Score: 7.5'."
        )
        try:
            return self.chat_client.chat(prompt)
        except Exception as e:
            return f"ERROR: {e}"


class SignificanceScoringStrategy(ScoringStrategy):
    """Strategy for scoring significance evaluations."""
    
    def __init__(self, chat_client):
        self.chat_client = chat_client
        self._system_prompt = """You are a precise scorer. I will provide you with a professional evaluation of an academic idea,
and you need to give a significance score based on this evaluation. The significance score depends on the attitude of the evaluation.
If the evaluation is positive, the significance score should be high; if the evaluation is negative, the significance score should be low.
Please note that the significance score ranges from 1 to 10, where 1 indicates the lowest significance and 10 indicates the highest significance.
Here are some examples(Some specific method or idea is replaced with Method A, Method B, Method C, etc.):

Example 1 (Low score case, score 1):
Evaluation: "The idea is simple and straightforward, but I don't think it makes sense to me, as I explained in the previous sections."
Analysis: The reviewer expresses clear skepticism and a lack of conceptual understanding or confidence in the idea. There is no indication of potential interest or novelty. The tone is dismissive and final, typical of very low excitement.
Score: 1

Example 2 (Low–medium score case, score 2):
Evaluation: "The idea has been addressed by other papers, and the difference is marginal. I don't have any new (expected) conclusion learned from this proposal, thus not excited."
Analysis: The reviewer acknowledges that the idea exists but sees little originality or learning value. Some effort is recognized, but the contribution is incremental and uninspiring.
Score: 2

Example 3 (Medium score case, score 3):
Evaluation: "Just not an interesting area in my opinion. Scope is too narrow to be impactful and existing non-prompting methods will do much better."
Analysis: The reviewer finds the idea unexciting but not completely without merit. The main reason for the moderate score is lack of broad impact rather than poor quality. There is some room for exploration, but it's not seen as a strong direction.
Score: 3

Example 4 (Medium–high score case, score 5):
Evaluation: "The approach could be useful for certain applications, though it may not be methodologically novel. It might still help understand bias mitigation effects in large models."
Analysis: The reviewer sees limited novelty but acknowledges practical potential. There is moderate enthusiasm due to possible usefulness, though not groundbreaking.
Score: 5

Example 5 (High score case, score 6):
Evaluation: "The trained models and methodology could be useful for specific systems. While not entirely novel, it shows practical direction and interesting potential."
Analysis: The reviewer is positive and sees genuine value and possible future utility, though the contribution is not revolutionary. The tone is constructive and moderately excited.
Score: 6

Example 6 (Very high score case, score 7–8):
Evaluation: "I think XXX are quite hard to process, so if it works, the proposed method would be very useful. This is a smart way to tackle an urgent challenge."
Analysis: The reviewer shows clear enthusiasm and recognizes strong relevance and potential impact. They believe the approach addresses an important open problem, leading to high excitement.
Score: 8
"""
    
    def score(self, evaluation_text: str) -> str:
        """Score significance evaluation."""
        prompt = (
            self._system_prompt
            + "\n\n"
            + "So now please start scoring formally: give me a score between 1 and 10 based on the following evaluation: \n\n"
            + evaluation_text.strip()
            + "\n\nPlease return an analysis of the evaluation and the final scoring result. "
            + "IMPORTANT: You must format your response with the score clearly marked at the end. "
            + "Use the exact format: 'Score: X' where X is an integer between 1 and 10. "
            + "For example, if your score is 7, end your response with 'Score: 7'."
        )
        try:
            return self.chat_client.chat(prompt)
        except Exception as e:
            return f"ERROR: {e}"


# ============================================================================
# Coverage Comparison Strategies
# ============================================================================

class CoverageCompareStrategy(ABC):
    """Abstract strategy for comparing coverage between original and generated concerns."""
    
    @abstractmethod
    def compare(
        self, 
        original: List[str], 
        generated: List[str]
    ) -> Tuple[Dict[str, Any], str]:
        """
        Compare coverage of original concerns in generated concerns.
        
        Args:
            original: List of original (gold standard) concerns
            generated: List of generated concerns
            
        Returns:
            Tuple of (result_dict, raw_response_string)
        """
        pass


class LLMCoverageCompareStrategy(CoverageCompareStrategy):
    """Strategy using LLM for coverage comparison."""
    
    def __init__(self, chat_client):
        self.chat_client = chat_client
        self._system_prompt = """You are a precise evaluator. You are currently dealing with the opinions of two reviewers, 'original' (gold) and 'generated' (model output).
Your task is to explain whether each point in the gold standard has been reflected in the "generated" content.

Now decide for each ORIGINAL item whether it is covered by any GENERATED item under a RELAXED criterion:
- Mark as covered if the overall meaning is similar, paraphrased, or broadly aligned (approximate semantic similarity),
  If two or more generated concerns jointly express one concern, it is also considered covered. But don't be too loose.

Thinking and reasoning Requirement (STRICT):
- Process ORIGINAL concerns sequentially, one-by-one.
- For each ORIGINAL item, carefully check all GENERATED items and determine matches.
- Perform your reasoning internally.
- Only include a concise, one-sentence justification in the "reason" field per item.

Output Policy (STRICT):
- Return ONLY a JSON object, starting with '{' and ending with '}'.
- Keys must be exactly: per_item (array), summary (object).
- Each per_item element: {"original": string, "covered": bool, "matched_indices": [int], "reason": string}.
- summary: {"covered_count": int, "total": int, "coverage_ratio": number}.
- Do NOT include code fences, markdown, comments, or extra explanatory text.
"""
    
    def compare(
        self, 
        original: List[str], 
        generated: List[str]
    ) -> Tuple[Dict[str, Any], str]:
        """Compare coverage using LLM."""
        import json
        
        user_prompt = (
            "Original concerns (gold):\n"
            + json.dumps(original, ensure_ascii=False)
            + "\n\nGenerated concerns:\n"
            + json.dumps(generated, ensure_ascii=False)
            + "\n\nReturn JSON only."
        )
        
        try:
            content = self.chat_client.chat(self._system_prompt + "\n\n" + user_prompt)
        except Exception as e:
            return {
                "per_item": [
                    {"original": o, "covered": False, "matched_indices": [], "reason": f"evaluator error: {e}"}
                    for o in original
                ],
                "summary": {"covered_count": 0, "total": len(original), "coverage_ratio": 0.0}
            }, f"ERROR: {e}"
        
        try:
            obj = json.loads(content)
            return obj, content
        except Exception:
            fallback = {
                "per_item": [
                    {"original": o, "covered": False, "matched_indices": [], "reason": "fallback-no-parse"}
                    for o in original
                ],
                "summary": {"covered_count": 0, "total": len(original), "coverage_ratio": 0.0}
            }
            return fallback, content


class EmbeddingCoverageCompareStrategy(CoverageCompareStrategy):
    """Strategy using embedding similarity for coverage comparison."""
    
    def __init__(self, embedding_client, similarity_threshold: float = 0.7):
        """
        Args:
            embedding_client: IEmbeddingClient instance
            similarity_threshold: Minimum cosine similarity to consider as covered
        """
        self.embedding_client = embedding_client
        self.similarity_threshold = similarity_threshold
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x*y for x, y in zip(a, b))
        na = math.sqrt(sum(x*x for x in a))
        nb = math.sqrt(sum(y*y for y in b))
        if na == 0.0 or nb == 0.0:
            return 0.0
        return dot / (na * nb)
    
    def compare(
        self, 
        original: List[str], 
        generated: List[str]
    ) -> Tuple[Dict[str, Any], str]:
        """Compare coverage using embedding similarity."""
        import json
        
        if not generated:
            return {
                "per_item": [
                    {"original": o, "covered": False, "matched_indices": [], "reason": "no generated concerns"}
                    for o in original
                ],
                "summary": {"covered_count": 0, "total": len(original), "coverage_ratio": 0.0}
            }, ""
        
        # Get embeddings
        try:
            emb_gen = self.embedding_client.embed_texts(generated)
            emb_ori = self.embedding_client.embed_texts(original) if original else []
        except Exception as e:
            return {
                "per_item": [
                    {"original": o, "covered": False, "matched_indices": [], "reason": f"embedding error: {e}"}
                    for o in original
                ],
                "summary": {"covered_count": 0, "total": len(original), "coverage_ratio": 0.0}
            }, f"ERROR: {e}"
        
        # Compare each original with all generated
        per_item = []
        covered_count = 0
        
        for oi, o_text in enumerate(original):
            if not emb_ori:
                per_item.append({
                    "original": o_text,
                    "covered": False,
                    "matched_indices": [],
                    "reason": "no original embeddings"
                })
                continue
            
            o_vec = emb_ori[oi]
            matches = []
            best_score = 0.0
            
            for gi, g_vec in enumerate(emb_gen):
                similarity = self._cosine_similarity(o_vec, g_vec)
                if similarity >= self.similarity_threshold:
                    matches.append(gi)
                if similarity > best_score:
                    best_score = similarity
            
            covered = len(matches) > 0
            if covered:
                covered_count += 1
            
            reason = f"best similarity: {best_score:.4f}" if best_score > 0 else "no matches above threshold"
            
            per_item.append({
                "original": o_text,
                "covered": covered,
                "matched_indices": matches,
                "reason": reason
            })
        
        summary = {
            "covered_count": covered_count,
            "total": len(original),
            "coverage_ratio": covered_count / len(original) if original else 0.0
        }
        
        result = {"per_item": per_item, "summary": summary}
        return result, json.dumps(result, ensure_ascii=False)
