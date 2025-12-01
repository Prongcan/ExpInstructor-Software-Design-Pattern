"""
Concrete adapters over provider SDKs.
Refactored with Adapter Pattern.
"""

from __future__ import annotations

from typing import List, Optional

from service import ChatGPT
from service import deepseek as deepseek_module

from .interfaces import IChatClient, IEmbeddingClient


class ChatGPTAdapter(IChatClient, IEmbeddingClient):
    """Adapter for OpenAI ChatGPT."""

    def __init__(self, chat_model: str = "gpt-4o", embedding_model: str = "text-embedding-3-small"):
        self.chat_model = chat_model
        self.embedding_model = embedding_model

    def chat(self, prompt: str, *, pdf_url: Optional[str] = None, model: Optional[str] = None) -> str:
        # Refactored with Adapter Pattern
        target_model = model or self.chat_model
        if pdf_url:
            return ChatGPT.chat(prompt, pdf_url, model=target_model)
        return ChatGPT.chat_simple(prompt, model=target_model)

    def embed_texts(self, texts: List[str], *, model: Optional[str] = None) -> List[List[float]]:
        # Refactored with Adapter Pattern
        target_model = model or self.embedding_model
        return ChatGPT.embed_texts(texts, model=target_model)


class DeepSeekAdapter(IChatClient):
    """Adapter for DeepSeek chat models."""

    def __init__(self, model: str = "deepseek-reasoner"):
        self.model = model

    def chat(self, prompt: str, *, pdf_url: Optional[str] = None, model: Optional[str] = None) -> str:
        # Refactored with Adapter Pattern
        _ = pdf_url  # DeepSeek adapter currently ignores file input
        target_model = model or self.model
        return deepseek_module.chat_deepseek(prompt if model is None else f"[{target_model}] {prompt}")


class BGEAdapter(IEmbeddingClient):
    """Adapter for BGE-M3 embeddings."""

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model_name = model_name

    def embed_texts(self, texts: List[str], *, model: Optional[str] = None) -> List[List[float]]:
        # Refactored with Adapter Pattern
        target_model = model or self.model_name
        from service.BGE_M3 import embed_texts as bge_embed_texts

        return bge_embed_texts(texts, model_name=target_model)
