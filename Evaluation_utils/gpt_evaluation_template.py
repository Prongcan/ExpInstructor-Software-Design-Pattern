"""
GPT Evaluation Template using Template Method Pattern.
Refactored with Template Method Pattern.

Unified template for all GPT-based evaluation single files.
Eliminates repetitive code across Evaluation_feasibility/GPT_single.py, 
Evaluation_novelty/GPT_single.py, Evaluation_significance/GPT_single.py
"""

import os
import sys
import json
import typing as t

# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from service.llm_factory import get_chat_client


class GPTEvaluationTemplate:
    """
    Template class for GPT-based evaluations.
    Refactored with Template Method Pattern: Eliminates repetitive GPT evaluation code.
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
        self._system_prompts = self._get_system_prompts()
        self._task_instructions = self._get_task_instructions()
        
    def _get_system_prompts(self) -> dict:
        """Get system prompts for different evaluation types. Refactored with Template Method Pattern."""
        return {
            "feasibility": """You are a rigorous peer-reviewer.
Task: Critically evaluate the given idea/proposal and GENERATE potential 'concerns' of feasibility
(feasibility, feasibility doubts, missing evaluations).
Do NOT extract phrases from the text verbatim; instead, propose concerns based on your assessment.
Output Policy (STRICT):
- Return ONLY a JSON array of strings, starting with '[' and ending with ']'.
- Each item must be a single-line short sentence (no line breaks).
- Do NOT include any code fences, markdown, comments, labels, or extra text.
- No leading bullets, numbering, or trailing commas inside items.
- Aim for 8-12 high-quality, non-duplicative items covering: feasibility, feasibility doubts, missing evaluations.""",
            
            "novelty": """You are a professional evaluator focusing on the novelty of the idea.
I will provide you with an academic idea. Your task is to evaluate only its level of novelty.
Please focus exclusively on the originality and innovation of the idea — how new, creative, or unprecedented it is compared to existing research or conventional approaches in the field.
Your response should:
Be concise and academic in tone.
Avoid discussing feasibility, significance, or methodology.
Provide a clear judgment on the novelty level with your serious analysis and reasoning.""",
            
            "significance": """You are a professional evaluator focusing on the significance of the idea.
I will provide you with an academic idea. Your task is to evaluate only its level of significance.
Please focus exclusively on the importance, scope, and potential impact of the idea — how meaningful, influential, or valuable it would be compared to existing research or conventional approaches in the field.
Your response should:
Be concise and academic in tone.
Avoid discussing feasibility, novelty, or methodology.
Provide a clear judgment on the significance level with your serious analysis and reasoning.""",
            
            "feasibility_score": """You are an expert peer reviewer with extensive experience in research feasibility assessment. 
Your task is to provide a comprehensive feasibility evaluation of research ideas."""
        }
    
    def _get_task_instructions(self) -> dict:
        """Get task instructions for different evaluation types. Refactored with Template Method Pattern.""" 
        return {
            "feasibility": "Return JSON array only.",
            "novelty": "Return a text evaluating novelty (which should include reasonable reasons).",
            "significance": "Return a text evaluating significance (which should include reasonable reasons).",
            "feasibility_score": "Write a comprehensive peer review evaluation text discussing the feasibility, implementation challenges, effectiveness, and any concerns about this idea. Write in a natural, flowing style as if you are providing feedback to the authors."
        }
    
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

# ============= Factory Functions for Different Evaluation Types =============
# Refactored with Template Method Pattern: Factory functions to create specific evaluators

def create_feasibility_evaluator() -> GPTEvaluationTemplate:
    """Create GPT feasibility evaluator. Refactored with Template Method Pattern."""
    return GPTEvaluationTemplate("feasibility")

def create_novelty_evaluator() -> GPTEvaluationTemplate:
    """Create GPT novelty evaluator. Refactored with Template Method Pattern."""
    return GPTEvaluationTemplate("novelty")

def create_significance_evaluator() -> GPTEvaluationTemplate:
    """Create GPT significance evaluator. Refactored with Template Method Pattern."""
    return GPTEvaluationTemplate("significance")

def create_feasibility_score_evaluator() -> GPTEvaluationTemplate:
    """Create GPT feasibility scoring evaluator. Refactored with Template Method Pattern."""
    return GPTEvaluationTemplate("feasibility_score")


# ============= Unified API Functions =============
# Refactored with Template Method Pattern: Unified API for all GPT evaluations

def generate_gpt_evaluation(idea_text: str, evaluation_type: str) -> t.Union[str, t.Tuple[t.List[str], str]]:
    """
    Unified GPT evaluation function.
    Refactored with Template Method Pattern: Single function replaces all individual generate_xxx_evaluation functions.
    
    Args:
        idea_text: Research idea text to evaluate
        evaluation_type: Type of evaluation ("feasibility", "novelty", "significance", "feasibility_score")
        
    Returns:
        For feasibility: Tuple of (concerns_list, raw_response)
        For others: Evaluation text string
    """
    evaluator = GPTEvaluationTemplate(evaluation_type)
    return evaluator.generate_evaluation(idea_text)