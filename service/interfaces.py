"""
Core protocol definitions for chat and embedding clients.
Refactored with Factory Method Pattern and Adapter Pattern.
"""

from __future__ import annotations

from typing import List, Protocol, runtime_checkable


@runtime_checkable
class IChatClient(Protocol):
    """Chat client interface."""

    def chat(self, prompt: str, *, pdf_url: str | None = None, model: str | None = None) -> str:
        """Return a single string response for the given prompt."""


@runtime_checkable
class IEmbeddingClient(Protocol):
    """Embedding client interface."""

    def embed_texts(self, texts: List[str], *, model: str | None = None) -> List[List[float]]:
        """Return embeddings in the same order as the input texts."""