import json
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple
from tqdm import tqdm

# Adjust path to import from LLM_service
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from LLM_service.llm_factory import get_embedding_client
from LLM_service.llm_adapters import BGEAdapter
from LLM_service.interfaces import IEmbeddingClient

class EmbeddingManager:
    """
    Manages embedding generation, caching, and retrieval.
    Refactored from GraphRetrievalSystem to adhere to Single Responsibility Principle.
    """
    def __init__(self, batch_size: int = 256):
        self.batch_size = batch_size
        self._embed_client: Optional[IEmbeddingClient] = None
        self.bge_m3_available = False
        self._ensure_client()

    def _ensure_client(self):
        """Ensure the embedding client is initialized."""
        if self._embed_client is None:
            self._embed_client = get_embedding_client()
            self.bge_m3_available = isinstance(self._embed_client, BGEAdapter)

    def embed_texts(self, texts: list[str], model: str = "BAAI/bge-m3") -> list[list[float]]:
        """
        Generate embeddings for a list of texts.
        """
        self._ensure_client()
        return self._embed_client.embed_texts(texts, model=model)

    def get_or_build_embeddings(self, entity_texts: List[str], edge_texts: List[str], model_name: str = 'BAAI/bge-m3') -> Tuple[Optional[List[List[float]]], Optional[List[List[float]]]]:
        """
        Build or load semantic embeddings for entities and edges.
        Checks cache first, generates if missing.
        """
        if not entity_texts and not edge_texts:
            return None, None
        
        self._ensure_client()
        
        # Try loading from cache
        cache_dir, ent_path, edge_path, meta_path = self._cache_paths(model_name)
        signature = self._compute_signature(entity_texts, edge_texts)
        
        entity_embeddings = None
        edge_embeddings = None

        try:
            if ent_path.exists() and edge_path.exists() and meta_path.exists():
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                if meta.get('model_name') == model_name and meta.get('signature') == signature:
                    # Load cached embeddings
                    if entity_texts:
                        with open(ent_path, 'r', encoding='utf-8') as f:
                            entity_embeddings = json.load(f)
                    if edge_texts:
                        with open(edge_path, 'r', encoding='utf-8') as f:
                            edge_embeddings = json.load(f)
                    print(f"Loaded embedding cache: {cache_dir}")
                    return entity_embeddings, edge_embeddings
        except Exception:
            # Ignore corrupted cache and rebuild
            pass

        # Recompute and save the cache
        try:
            if entity_texts:
                print(f"Generating embeddings for {len(entity_texts)} entities...")
                # Use a larger batch size for BGE-M3 to maximize GPU usage
                batch_size = self.batch_size if self.bge_m3_available else 100
                entity_embeddings = self._batch_embed_texts(entity_texts, model_name, batch_size=batch_size)
            
            if edge_texts:
                print(f"Generating embeddings for {len(edge_texts)} edges...")
                batch_size = self.batch_size if self.bge_m3_available else 100
                edge_embeddings = self._batch_embed_texts(edge_texts, model_name, batch_size=batch_size)

            cache_dir.mkdir(parents=True, exist_ok=True)
            if entity_embeddings is not None:
                with open(ent_path, 'w', encoding='utf-8') as f:
                    json.dump(entity_embeddings, f, ensure_ascii=False)
            if edge_embeddings is not None:
                with open(edge_path, 'w', encoding='utf-8') as f:
                    json.dump(edge_embeddings, f, ensure_ascii=False)
            
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'model_name': model_name,
                    'signature': signature,
                    'entity_count': len(entity_texts),
                    'edge_count': len(edge_texts)
                }, f, ensure_ascii=False, indent=2)
            print(f"Generated and cached embeddings: {cache_dir}")
        except Exception as e:
            print(f"Failed to generate/save embeddings: {e}")
            return None, None

        return entity_embeddings, edge_embeddings

    def _compute_signature(self, entity_texts: List[str], edge_texts: List[str]) -> str:
        """
        Compute a signature of the current graph content based on node and edge text hashes.
        """
        h = hashlib.sha1()
        h.update(f"N:{len(entity_texts)} E:{len(edge_texts)}".encode('utf-8'))
        # Sample to avoid huge memory usage
        for txt in entity_texts[:5000]:
            h.update(txt.encode('utf-8', errors='ignore'))
        for txt in edge_texts[:20000]:
            h.update(txt.encode('utf-8', errors='ignore'))
        return h.hexdigest()

    def _cache_paths(self, model_name: str):
        """
        Return the cache directory and file paths.
        """
        model_hash = hashlib.sha1(model_name.encode('utf-8')).hexdigest()[:12]
        base_dir = Path(__file__).resolve().parent / '.embeddings' / model_hash
        ent_path = base_dir / 'entities.json'
        edge_path = base_dir / 'edges.json'
        meta_path = base_dir / 'meta.json'
        return base_dir, ent_path, edge_path, meta_path

    def _batch_embed_texts(self, texts: List[str], model: str, batch_size: int = 100) -> List[List[float]]:
        """
        Batch embeddings to avoid API limits.
        """
        if not texts:
            return []
        
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        pbar = tqdm(total=len(texts), desc="Generating embeddings", unit="text", 
                   bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
        
        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                try:
                    # Filter empty or overly long texts
                    filtered_batch = []
                    for text in batch:
                        if text and len(text.strip()) > 0 and len(text) < 8000:  # OpenAI limit
                            filtered_batch.append(text.strip())
                        else:
                            filtered_batch.append("empty")
                    
                    if filtered_batch:
                        batch_embeddings = self.embed_texts(filtered_batch, model=model)
                        all_embeddings.extend(batch_embeddings)
                    else:
                        # Placeholder zero vectors
                        embedding_dim = 1024 if self.bge_m3_available else 1536
                        all_embeddings.extend([[0.0] * embedding_dim] * len(batch))
                    
                    pbar.update(len(batch))
                    pbar.set_postfix({'batch': f"{batch_num}/{total_batches}"})
                    
                    # Rate limiting for non-local models
                    if not self.bge_m3_available or not model.startswith("BAAI/bge-m3"):
                        time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Batch {batch_num} failed: {e}")
                    embedding_dim = 1024 if self.bge_m3_available else 1536
                    all_embeddings.extend([[0.0] * embedding_dim] * len(batch))
                    pbar.update(len(batch))
        
        finally:
            pbar.close()
        
        return all_embeddings
