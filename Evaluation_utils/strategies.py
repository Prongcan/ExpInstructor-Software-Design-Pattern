"""
Scoring and Coverage Comparison Strategies

Refactored with Strategy Pattern (Layer 4).

This module provides:
1. ScoringStrategy: Abstract base for scoring evaluation texts
2. CoverageCompareStrategy: Abstract base for comparing coverage between original and generated concerns
3. Concrete implementations:
   - LLMScoringStrategy: Uses LLM for scoring (feasibility, novelty, significance)
   - LLMCoverageCompareStrategy: Uses LLM for coverage comparison
   - EmbeddingCoverageCompareStrategy: Uses embedding vectors for coverage comparison
"""

import json
import typing as t
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from service.interfaces import IChatClient, IEmbeddingClient


# ============================================================================
# Abstract Strategy Interfaces
# ============================================================================

class ScoringStrategy(ABC):
    """
    Abstract strategy for scoring evaluation texts.
    
    Different implementations can use LLM, rule-based, or hybrid approaches.
    """
    
    @abstractmethod
    def score(self, evaluation_text: str) -> str:
        """
        Score an evaluation text.
        
        Args:
            evaluation_text: The evaluation text to score
            
        Returns:
            Score result (may be raw text with score embedded, or structured format)
        """
        pass


class CoverageCompareStrategy(ABC):
    """
    Abstract strategy for comparing coverage between original and generated concerns.
    
    Different implementations can use LLM semantic matching, embedding similarity, etc.
    """
    
    @abstractmethod
    def compare(
        self,
        original: List[str],
        generated: List[str]
    ) -> Tuple[Dict, Optional[str]]:
        """
        Compare coverage of generated concerns against original concerns.
        
        Args:
            original: List of original (gold standard) concerns
            generated: List of generated concerns
            
        Returns:
            Tuple of (coverage_result_dict, raw_response_string)
            coverage_result_dict should have structure:
            {
                "per_item": [
                    {
                        "original": str,
                        "covered": bool,
                        "matched_indices": List[int],
                        "reason": str
                    }
                ],
                "summary": {
                    "covered_count": int,
                    "total": int,
                    "coverage_ratio": float
                }
            }
        """
        pass


# ============================================================================
# Concrete Scoring Strategies
# ============================================================================

class LLMScoringStrategy(ScoringStrategy):
    """
    LLM-based scoring strategy.
    
    Uses LLM to score evaluation texts. Supports different score types:
    - Feasibility score (1-10, decimal)
    - Novelty score (1-10, integer)
    - Significance score (1-10, integer)
    """
    
    # System prompts for different score types
    FEASIBILITY_SYSTEM_PROMPT = """You are a precise scorer. I will provide you with a professional peer review evaluation of an academic idea,
and you need to give a feasibility score based on this evaluation. Feasibility means whether the idea is easy to implement and execute and whether the idea is effective.
The feasibility score depends on how feasible and executable the idea is according to the evaluation.
Please note that the feasibility score ranges from 1 to 10, where 1 indicates the lowest feasibility and 10 indicates the highest feasibility.

IMPORTANT: The score should reflect the degree of feasibility and effectiveness as demonstrated in the evaluation text. You should judge the score based on:
1. The overall tone and assessment: Positive evaluations indicating high feasibility and effectiveness should lead to higher scores, while negative evaluations indicating significant challenges should lead to lower scores.
2. Implementation feasibility: Comments about ease of implementation, straightforward methods, available datasets, and clear execution plans should increase the score.
3. Effectiveness concerns: Concerns about whether the method will work, comparisons with baselines, and potential limitations should decrease the score.
4. Resource requirements: Comments about computational requirements, data collection challenges, and manual efforts should decrease the score.

Here are some examples based on real evaluation data from Stanford_comments_with_ideas_with_scores.json with full review comments (all_comments) and their corresponding average scores:

Example 1 (Low-medium score case, score 4.5):
Evaluation: "The hardest part is data curation, but the evaluation set used in the paper would be a valuable contribution to the literature. The scope of the project needs to be clearly defined so that only a specific kind of \"vernacular\" is being studied, otherwise collecting data will be tough. I just don't think frontier LLMs have any trouble with the kind of modern language shown in the examples. Furthermore, we can't reliably predict semantic change so I don't think this will even work if e.g. you use a 2020-trained LM on language from 2040. The only solution would be some kind of RAG, expert prompting, or continued pretraining. Making the model guess what semantic change has happened is just not going to work. I am not sure how hard it is to construct such a graph. But it seems to be a quite straightforward method to implement. The experimental setup and experiments does not seem to be difficulty to manage as well. I don't feel this will work well compared to just include the explanations of the phrases in prompts."
Analysis: The evaluation acknowledges some positive aspects (evaluation set contribution, straightforward implementation) but identifies significant challenges: unclear scope definition, difficult data collection, fundamental limitations in predicting semantic change, and doubts about the core method's effectiveness. These concerns indicate moderate feasibility with substantial challenges.
Score: 4.5

Example 2 (Medium score case, score 5.0):
Evaluation: "I imagine step (2) in the proposed idea would be a little challenging in execution. Manual efforts would perhaps be involved to generate the 'polarity reversed' world descriptions, or a combination of automation and manual validation would be required to ensure the quality of these descriptions. Also, the example illustrated in the proposed idea does not come from the datasets mentioned in Step 1. This will likely cause extra planning steps to finalize how the prompting technique would be applied to each of the individual datasets. The example shown in the proposed idea already has a strong baseline that does not show explicit gender stereotype. In contrast, the proposed method could offer counter-factual explanations or arguments because of the \"stereotype inversion.\" This makes me feel the proposed idea does not address the fairness problem in LLMs better than existing safety guardrails. Very easy to implement: requires no model training, datasets are widely available. The prompts seem easy to template as well. I would expect this to work reasonably well since a variety of prompt-based approaches have been shown to work well on this sort of task. However, I'm skeptical that this prompt-based approach would significantly outperform existing prompt-based approaches. It shouldn't be hard to implement this ideas since it is very straightforward. This idea does not make sense to me at all. Why would reversing the stereotype could help to reduce the bias? It simply creates another kinds of bias."
Analysis: The evaluation identifies specific execution challenges, including manual work requirements and dataset alignment issues. There are also concerns about the method's effectiveness compared to existing approaches. However, it acknowledges that implementation is straightforward with available datasets. These factors indicate moderate feasibility with some concerns about both implementation and effectiveness.
Score: 5.0

Example 3 (Medium score case, score 5.25):
Evaluation: "The significant feasibility problem for this proposal is it depends too much on the performance of the proposed method, and in the field of uncertainty quantification, due to the black-box nature of model (the usage of GPT-3.5/4 gets this situation even worse), it is hard to say whether we can get an ideal uncertainty measurement that can perform well in the evaluation setup proposed. So there might be many re-routings, and it is hard to tell whether any of them would work. The big issue for the effectiveness of the proposed method is that, it asserts very strong assumptions on downstream tasks, such as there must exist only two extremes, or at least two extremes are complicated enough for quantifying uncertainty. This is definitely not true. Think about multi-choice QA, emotion detection, etc. In these tasks, there are far more than two extremes, and even a spectrum of extremes. We also do not know how the model understand the task -- so it might be unfair for the model uncertainty quantification by using human priors that there are only two extremes. Also, this proposal assumes that the model can place its own output under two extremes well -- it is hard to say, as it may not even understand what it generates (\"Generative AI paradox\"). Most of the proposal seems straightforward and quick to execute (straightforward prompting and some generally simple analysis). I'm docking feasibility since they mention wanting to compare to human uncertainty ratings (which, as proposed, seems to be of limited utility, but that's besides the point). Depending on how they'd go about this, involving humans could significantly increase their timeline. I could be misunderstanding, but I have a hard time imagining this would work well. It seems like the poles will only be useful if they're actually relevant to the question and if they encourage the model to use a piece of information that it actually \"knows\" and isn't already relying on. In their Paris example, being a \"major global city\" may be a good sign that a city is a capital, but would a model that doesn't \"know\" that Paris is a capital \"know\" that it is a major city? I'd be concerned that the model's ability to pick a good axis and to put their answer on the axis would correlate with the model's ability to \"understand\" the scenario and quantify its uncertainty in the baseline setting. It also seems like multiple axes/poles would be necessary to really get a good sense of the answer. London is also a \"major global city\" but clearly not the capital of France."
Analysis: The evaluation identifies significant feasibility and effectiveness concerns. While the basic proposal seems straightforward to execute, there are fundamental doubts about whether the method can work well, with concerns about strong assumptions, model understanding, and the core approach. These factors indicate moderate feasibility with substantial effectiveness concerns.
Score: 5.25

Example 4 (Medium-high score case, score 6.17):
Evaluation: "The structure is clear and the implementation of the LLM pipeline is not very heavy. One caveat is that in the proposal it mentioned a specialist is needed to manually verify if the identified defect is actually an issue in the SRS document. The domain-specific expertise required can make it less feasible for a typical CS PhD not in the domain. I think by breaking down a long document into sections, and focusing on each of the independent sections separately, the method will highly likely decrease the difficulty for LLMs to understand the texts (as there are less concepts, relationship, etc). And it can be expected to see a positive improvement on the tasks. That being said, recently released LLMs have very long context lengths. For example Claude-3.5-sonnet has 200K context lengths. I wonder how big the difference will be if we just input the whole document, generate the defect questions, and verify them. The approach itself is fairly straightforward. You can draw upon existing synthetic pipeline approaches and even reuse existing codebases towards SRS. The idea itself is fairly likely to succeed. The application space is constrained towards SRS and each of the sections within the document. Therefore, the LM can likely handle documents and specifics of the domain through in-context learning or fine-tuning. The idea is straightforward to implement. Since they have have abundant OpenAI / Anthropic API access, generating queries on defects with LLMs is not a problem. The only potential difficulty is whether there are enough human resources to label the ground truths. It may be a bit challenging to find people with sufficient expertise on SRS to do the labeling. Converting SRS Document defects detection prompts into yes/no questions on sections of the document does not fundamentally change the way of applying LLMs on this problem. It is too simple and does not have any specific designs such as planning or states tracking or finetuning to enhance LLMs ability. Constructing the questions by sections is also unlikely to work better than existing conventional approaches like RAG. Overall, this idea is unlikely to work well, even in the specific scenarios of SRS Document defects detection."
Analysis: The evaluation indicates the basic components are feasible (clear structure, straightforward implementation, available APIs), but raises concerns about specialist requirements, potential limitations compared to simpler approaches, and doubts about effectiveness. Overall, the project seems feasible but with uncertainty about effectiveness.
Score: 6.17

Example 5 (High score case, score 7.0):
Evaluation: "feasible as only tracking the intermediate status. intuitively thinking this should works. The experiments are fairly easy to implement. They can be broken into separate components around tool use (e.g. compilers), multi-turn reasoning, unit test generation and evaluation, and more. Most code approaches right now also use multi-turn approaches and unit tests. However, not many of them integrate tool use and, when they do, it isn't that good. By make it iterative and allowing the models to \"hill climb\" through the use of a continuous state, it could significantly improve performance. This seems to be a prompting focused project and therefore shouldn't require more intricate code like model training. I therefore think that one to two months is a very feasible timeline. Based on the related paper I cited above, I wouldn't be surprised if this method improved performance on several benchmarks. However, I'd expect other methods, like actually executing the code instead of having the LLM simulate the execution, might work much better."
Analysis: The evaluation indicates the method is feasible with easy implementation, clear components, and a reasonable timeline. While there are some concerns about effectiveness compared to other methods, the overall feasibility is high with positive expectations about performance improvements.
Score: 7.0

Example 6 (High score case, score 7.25):
Evaluation: "No issue with the execution. A lot of previous work have approached this problem in a very similar way, so it would have similar performance. Additionally, if a model hallucinates on the CoT step, evaluating each CoT might also hallucinate, which is harmful to entire pipeline This is a highly feasible experiment especially with the existing dataset and the existing approach already been completed by another paper and so I do think it is highly feasible and straightforward to implement the idea and run the experiments. The idea should somewhat work because as it has been shown in the previous paper the idea does somewhat work but it suffers from the same issue as do things like multiple looping structures where if we can't verify whether the first three strings that are generated make sense or not then the chain of thought wouldn't necessarily make sense because it is all interlinked in a loop like structure even if it has three loops that are running concurrently with each other."
Analysis: The evaluation explicitly states there are no execution issues and that the experiment is highly feasible with existing datasets and approaches. While there are some concerns about hallucination and verification, these are effectiveness concerns rather than feasibility barriers. The project is clearly executable with positive expectations.
Score: 7.25
"""

    NOVELTY_SYSTEM_PROMPT = """You are a precise scorer. I will provide you with a professional evaluation of an academic idea,
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

    SIGNIFICANCE_SYSTEM_PROMPT = """You are a precise scorer. I will provide you with a professional evaluation of an academic idea,
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
    
    def __init__(
        self,
        chat_client: IChatClient,
        score_type: str = "feasibility"
    ):
        """
        Initialize LLM scoring strategy.
        
        Args:
            chat_client: Chat client for LLM calls
            score_type: Type of score ("feasibility", "novelty", "significance")
        """
        self.chat_client = chat_client
        self.score_type = score_type.lower()
        
        # Select appropriate system prompt
        if self.score_type == "feasibility":
            self.system_prompt = self.FEASIBILITY_SYSTEM_PROMPT
            self.score_format = "decimal"  # Can be decimal like 4.5, 7.75
        elif self.score_type == "novelty":
            self.system_prompt = self.NOVELTY_SYSTEM_PROMPT
            self.score_format = "integer"  # Integer only
        elif self.score_type == "significance":
            self.system_prompt = self.SIGNIFICANCE_SYSTEM_PROMPT
            self.score_format = "integer"  # Integer only
        else:
            raise ValueError(f"Unsupported score type: {score_type}")
    
    def score(self, evaluation_text: str) -> str:
        """
        Score evaluation text using LLM.
        
        Args:
            evaluation_text: The evaluation text to score
            
        Returns:
            Raw LLM response containing score analysis and score
        """
        if self.score_type == "feasibility":
            prompt = (
                self.system_prompt
                + "\n\n"
                + "So now please start scoring formally: give me a score between 1 and 10 based on the following peer review evaluation: \n\n"
                + "Evaluation: " + evaluation_text.strip()
                + "\n\nPlease return an analysis of the evaluation and the final scoring result. "
                + "IMPORTANT: You must format your response with the score clearly marked at the end. "
                + "Use the exact format: 'Score: X' where X is a number between 1 and 10 (can be a decimal like 4.5, 7.75, etc.). "
                + "For example, if your score is 7, end your response with 'Score: 7'. If your score is 7.5, end with 'Score: 7.5'."
            )
        else:  # novelty or significance
            prompt = (
                self.system_prompt
                + "\n\n"
                + "So now please start scoring formally: give me a score between 1 and 10 based on the following evaluation: \n\n"
                + evaluation_text.strip()
                + "\n\nPlease return an analysis of the evaluation and the final scoring result. "
                + "IMPORTANT: You must format your response with the score clearly marked at the end. "
                + "Use the exact format: 'Score: X' where X is an integer between 1 and 10. "
                + "For example, if your score is 7, end your response with 'Score: 7'."
            )
        
        try:
            content = self.chat_client.chat(prompt)
            return content
        except Exception as e:
            return f"ERROR: {e}"


# Convenience classes for specific score types
class FeasibilityScoringStrategy(LLMScoringStrategy):
    """Scoring strategy specifically for feasibility scores."""
    
    def __init__(self, chat_client: IChatClient):
        super().__init__(chat_client, score_type="feasibility")


class NoveltyScoringStrategy(LLMScoringStrategy):
    """Scoring strategy specifically for novelty scores."""
    
    def __init__(self, chat_client: IChatClient):
        super().__init__(chat_client, score_type="novelty")


class SignificanceScoringStrategy(LLMScoringStrategy):
    """Scoring strategy specifically for significance scores."""
    
    def __init__(self, chat_client: IChatClient):
        super().__init__(chat_client, score_type="significance")


# ============================================================================
# Concrete Coverage Comparison Strategies
# ============================================================================

class LLMCoverageCompareStrategy(CoverageCompareStrategy):
    """
    LLM-based coverage comparison strategy.
    
    Uses LLM to semantically compare original and generated concerns,
    determining which original concerns are covered by generated ones.
    """
    
    COMPARE_SYSTEM_PROMPT = """You are a precise evaluator. You are currently dealing with the opinions of two reviewers, 'original' (gold) and 'generated' (model output).
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
    
    def __init__(self, chat_client: IChatClient):
        """
        Initialize LLM coverage comparison strategy.
        
        Args:
            chat_client: Chat client for LLM calls
        """
        self.chat_client = chat_client
    
    def compare(
        self,
        original: List[str],
        generated: List[str]
    ) -> Tuple[Dict, Optional[str]]:
        """
        Compare coverage using LLM.
        
        Args:
            original: List of original (gold standard) concerns
            generated: List of generated concerns
            
        Returns:
            Tuple of (coverage_result_dict, raw_response_string)
        """
        user_prompt = (
            "Original concerns (gold):\n"
            + json.dumps(original, ensure_ascii=False)
            + "\n\nGenerated concerns:\n"
            + json.dumps(generated, ensure_ascii=False)
            + "\n\nReturn JSON only."
        )
        
        try:
            content = self.chat_client.chat(
                self.COMPARE_SYSTEM_PROMPT + "\n\n" + user_prompt
            )
        except Exception as e:
            fallback_result = {
                "per_item": [
                    {
                        "original": o,
                        "covered": False,
                        "matched_indices": [],
                        "reason": f"evaluator error: {e}"
                    }
                    for o in original
                ],
                "summary": {
                    "covered_count": 0,
                    "total": len(original),
                    "coverage_ratio": 0.0
                }
            }
            return fallback_result, f"ERROR: {e}"
        
        try:
            obj = json.loads(content)
            return obj, content
        except Exception:
            fallback_result = {
                "per_item": [
                    {
                        "original": o,
                        "covered": False,
                        "matched_indices": [],
                        "reason": "fallback-no-parse"
                    }
                    for o in original
                ],
                "summary": {
                    "covered_count": 0,
                    "total": len(original),
                    "coverage_ratio": 0.0
                }
            }
            return fallback_result, content


class EmbeddingCoverageCompareStrategy(CoverageCompareStrategy):
    """
    Embedding-based coverage comparison strategy.
    
    Uses embedding vectors and cosine similarity to match generated concerns
    to original concerns. This is a lightweight alternative to LLM-based comparison.
    """
    
    def __init__(
        self,
        embedding_client: IEmbeddingClient,
        model: Optional[str] = None,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize embedding coverage comparison strategy.
        
        Args:
            embedding_client: Embedding client for vector embeddings
            model: Embedding model name (None to use adapter's default)
            similarity_threshold: Minimum cosine similarity to consider a match
        """
        self.embedding_client = embedding_client
        # If model is None, let the adapter decide (it will use its default)
        self.model = model
        self.similarity_threshold = similarity_threshold
    
    def _cosine_similarity(
        self,
        a: List[float],
        b: List[float]
    ) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0.0 or nb == 0.0:
            return 0.0
        return dot / (na * nb)
    
    def compare(
        self,
        original: List[str],
        generated: List[str]
    ) -> Tuple[Dict, Optional[str]]:
        """
        Compare coverage using embedding similarity.
        
        Args:
            original: List of original (gold standard) concerns
            generated: List of generated concerns
            
        Returns:
            Tuple of (coverage_result_dict, raw_response_string)
        """
        if not original:
            return {
                "per_item": [],
                "summary": {
                    "covered_count": 0,
                    "total": 0,
                    "coverage_ratio": 0.0
                }
            }, None
        
        if not generated:
            return {
                "per_item": [
                    {
                        "original": o,
                        "covered": False,
                        "matched_indices": [],
                        "reason": "no generated concerns"
                    }
                    for o in original
                ],
                "summary": {
                    "covered_count": 0,
                    "total": len(original),
                    "coverage_ratio": 0.0
                }
            }, None
        
        # Get embeddings
        try:
            emb_original = self.embedding_client.embed_texts(original, model=self.model)
            emb_generated = self.embedding_client.embed_texts(generated, model=self.model)
        except Exception as e:
            fallback_result = {
                "per_item": [
                    {
                        "original": o,
                        "covered": False,
                        "matched_indices": [],
                        "reason": f"embedding error: {e}"
                    }
                    for o in original
                ],
                "summary": {
                    "covered_count": 0,
                    "total": len(original),
                    "coverage_ratio": 0.0
                }
            }
            return fallback_result, f"ERROR: {e}"
        
        # Match each original concern to generated concerns
        per_item = []
        covered_count = 0
        
        for oi, o_text in enumerate(original):
            o_vec = emb_original[oi]
            matches = []
            best_score = 0.0
            best_indices = []
            
            for gi, g_vec in enumerate(emb_generated):
                similarity = self._cosine_similarity(o_vec, g_vec)
                if similarity >= self.similarity_threshold:
                    matches.append((gi, similarity))
            
            # Sort matches by similarity (descending)
            matches.sort(key=lambda x: x[1], reverse=True)
            
            if matches:
                best_score = matches[0][1]
                best_indices = [idx for idx, _ in matches]
                covered = True
                covered_count += 1
                reason = f"matched with similarity {best_score:.3f}"
            else:
                covered = False
                reason = f"no match above threshold {self.similarity_threshold}"
            
            per_item.append({
                "original": o_text,
                "covered": covered,
                "matched_indices": best_indices,
                "reason": reason
            })
        
        coverage_ratio = covered_count / len(original) if original else 0.0
        
        result = {
            "per_item": per_item,
            "summary": {
                "covered_count": covered_count,
                "total": len(original),
                "coverage_ratio": coverage_ratio
            }
        }
        
        return result, None

