"""
Factory method style: separate factories for chat and embedding clients.
Refactored with Factory Method Pattern.
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable, Optional, Sequence, Union

from .interfaces import IChatClient, IEmbeddingClient
from .llm_adapters import BGEAdapter, ChatGPTAdapter, DeepSeekAdapter


# Registered product creators
CHAT_CREATORS: Dict[str, Callable[[], IChatClient]] = {
    "chatgpt": lambda: ChatGPTAdapter(chat_model="gpt-4o"),
    "deepseek": lambda: DeepSeekAdapter(model="deepseek-reasoner"),
    # future: "gemini": lambda: GeminiAdapter(...),
}

EMBEDDING_CREATORS: Dict[str, Callable[[], IEmbeddingClient]] = {
    "bge": lambda: BGEAdapter(model_name="BAAI/bge-m3"),
    "chatgpt": lambda: ChatGPTAdapter(embedding_model="text-embedding-3-small"),
    # future: "gemini-embed": lambda: GeminiEmbeddingAdapter(...),
}

DEFAULT_CHAT_PRIORITY: Sequence[str] = ("chatgpt", "deepseek", "openai")
DEFAULT_EMBEDDING_PRIORITY: Sequence[str] = ("bge", "chatgpt", "openai")


_CHAT_CACHE: Dict[tuple[str, ...], IChatClient] = {}
_EMBED_CACHE: Dict[tuple[str, ...], IEmbeddingClient] = {}


PriorityInput = Union[str, Iterable[str], None]


def _normalize_priority(
    preferred: PriorityInput,
    default_order: Sequence[str],
    registry: Dict[str, Callable[[], object]],
) -> tuple[str, ...]:
    """Merge user preference with defaults, drop duplicates, keep registered keys only."""
    raw: Iterable[str]
    if preferred is None:
        raw = default_order
    elif isinstance(preferred, str):
        raw = (preferred, *default_order)
    else:
        raw = tuple(preferred) + tuple(default_order)

    seen: set[str] = set()
    ordered: list[str] = []
    for item in raw:
        key = str(item).strip().lower()
        if not key or key in seen or key not in registry:
            continue
        seen.add(key)
        ordered.append(key)

    return tuple(ordered)


class ChatFactory:
    """Create chat clients based on provider priority."""

    def __init__(self, priority: Iterable[str]):
        self.priority = [p.lower() for p in priority]
        if not self.priority:
            raise ValueError("ChatFactory requires a non-empty priority list.")
        self._cache: Dict[str, IChatClient] = {}

    def create(self) -> IChatClient:
        last_error: Optional[Exception] = None
        for provider in self.priority:
            if provider in self._cache:
                return self._cache[provider]
            creator = CHAT_CREATORS.get(provider)
            if not creator:
                continue
            try:
                client = creator()
                self._cache[provider] = client
                return client
            except Exception as exc:
                last_error = exc
                print(f"[ChatFactory] Skip provider '{provider}': {exc}")
                continue
        raise RuntimeError(f"No chat client available; last error: {last_error}")


class EmbeddingFactory:
    """Create embedding clients based on provider priority."""

    def __init__(self, priority: Iterable[str]):
        self.priority = [p.lower() for p in priority]
        if not self.priority:
            raise ValueError("EmbeddingFactory requires a non-empty priority list.")
        self._cache: Dict[str, IEmbeddingClient] = {}

    def create(self) -> IEmbeddingClient:
        last_error: Optional[Exception] = None
        for provider in self.priority:
            if provider in self._cache:
                return self._cache[provider]
            creator = EMBEDDING_CREATORS.get(provider)
            if not creator:
                continue
            try:
                client = creator()
                self._cache[provider] = client
                return client
            except Exception as exc:
                last_error = exc
                print(f"[EmbeddingFactory] Skip provider '{provider}': {exc}")
                continue
        raise RuntimeError(f"No embedding client available; last error: {last_error}")


def get_chat_client(preferred: PriorityInput = None) -> IChatClient:
    """
    Convenience accessor for a chat client using the shared registry-based factory.
    `preferred` can be a provider name or iterable to set priority (e.g., "deepseek").
    """
    priority = _normalize_priority(preferred, DEFAULT_CHAT_PRIORITY, CHAT_CREATORS)
    if not priority:
        raise RuntimeError("No valid chat providers configured.")

    cache_key = tuple(priority)
    if cache_key not in _CHAT_CACHE:
        _CHAT_CACHE[cache_key] = ChatFactory(priority).create()
    return _CHAT_CACHE[cache_key]


def get_embedding_client(preferred: PriorityInput = None) -> IEmbeddingClient:
    """
    Convenience accessor for an embedding client using the shared registry-based factory.
    `preferred` can be a provider name or iterable to set priority (e.g., "bge").
    """
    priority = _normalize_priority(preferred, DEFAULT_EMBEDDING_PRIORITY, EMBEDDING_CREATORS)
    if not priority:
        raise RuntimeError("No valid embedding providers configured.")

    cache_key = tuple(priority)
    if cache_key not in _EMBED_CACHE:
        _EMBED_CACHE[cache_key] = EmbeddingFactory(priority).create()
    return _EMBED_CACHE[cache_key]
