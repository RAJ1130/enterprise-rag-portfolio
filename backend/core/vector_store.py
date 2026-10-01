import os
import json
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from .chunker import TextChunk
from .embeddings import BaseEmbedder, STOPWORDS

class RetrievalResult:
    def __init__(
        self,
        chunk_id: str,
        doc_id: str,
        doc_name: str,
        page_number: int,
        chunk_index: int,
        content: str,
        score: float,
        dense_score: float = 0.0,
        bm25_score: float = 0.0,
        metadata: Dict[str, Any] = None
    ):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.doc_name = doc_name
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.content = content
        self.score = score
        self.dense_score = dense_score
        self.bm25_score = bm25_score
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "doc_name": self.doc_name,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "score": round(self.score, 4),
            "dense_score": round(self.dense_score, 4),
            "bm25_score": round(self.bm25_score, 4),
            "metadata": self.metadata
        }

class BM25Index:
    """In-memory BM25 index for lexical keyword ranking with stopword filtering."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: Dict[str, int] = {}
        self.avg_dl: float = 0.0
        self.doc_freq: Dict[str, int] = {}
        self.inverted_index: Dict[str, Dict[str, int]] = {}
        self.num_docs: int = 0

    def _tokenize(self, text: str) -> List[str]:
        raw = re.findall(r'\b[a-zA-Z0-9_\-\.]+\b', text.lower())
        return [t for t in raw if t not in STOPWORDS and len(t) > 1]

    def build(self, chunks: List[Dict[str, Any]]):
        self.doc_len.clear()
        self.doc_freq.clear()
        self.inverted_index.clear()
        self.num_docs = len(chunks)

        if self.num_docs == 0:
            self.avg_dl = 0.0
            return

        total_len = 0
        for chunk in chunks:
            c_id = chunk["chunk_id"]
            tokens = self._tokenize(chunk["content"])
            length = len(tokens)
            self.doc_len[c_id] = length
            total_len += length

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1

            for t, count in tf.items():
                if t not in self.inverted_index:
                    self.inverted_index[t] = {}
                self.inverted_index[t][c_id] = count
                self.doc_freq[t] = self.doc_freq.get(t, 0) + 1

        self.avg_dl = total_len / max(1, self.num_docs)

    def score(self, query: str) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        query_tokens = self._tokenize(query)
        if not query_tokens or self.num_docs == 0 or self.avg_dl == 0:
            return scores

        for q in query_tokens:
            if q not in self.inverted_index:
                continue
            df = self.doc_freq.get(q, 0)
            idf = math.log(1.0 + (self.num_docs - df + 0.5) / (df + 0.5))
            idf = max(0.1, idf)

            for c_id, tf in self.inverted_index[q].items():
                dl = self.doc_len.get(c_id, self.avg_dl)
                num = tf * (self.k1 + 1.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / self.avg_dl))
                term_score = idf * (num / denom)
                scores[c_id] = scores.get(c_id, 0.0) + term_score

        if scores:
            max_s = max(scores.values())
            if max_s > 0.5:
                for k in scores:
                    scores[k] = min(1.0, scores[k] / max_s)
            else:
                scores.clear()

        return scores


class EnterpriseVectorStore:
    """
    Persistent Hybrid Vector Database:
    - Dense vector cosine similarity index
    - Sparse BM25 lexical index
    - Reciprocal Rank Fusion (RRF) hybrid retrieval
    """
    def __init__(self, db_dir: Path, embedder: BaseEmbedder):
        self.db_dir = db_dir
        self.embedder = embedder
        self.chunks_file = db_dir / "chunks.json"
        self.vectors_file = db_dir / "vectors.npy"
        self.docs_metadata_file = db_dir / "documents_meta.json"
        
        self.chunks: List[Dict[str, Any]] = []
        self.chunk_id_to_idx: Dict[str, int] = {}
        self.vectors: Optional[np.ndarray] = None
        self.documents_meta: Dict[str, Dict[str, Any]] = {}
        self.bm25 = BM25Index()

        self._load()

    def _load(self):
        if self.chunks_file.exists():
            try:
                with open(self.chunks_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                self.chunk_id_to_idx = {c["chunk_id"]: idx for idx, c in enumerate(self.chunks)}
            except Exception:
                self.chunks = []
                self.chunk_id_to_idx = {}

        if self.vectors_file.exists() and len(self.chunks) > 0:
            try:
                self.vectors = np.load(str(self.vectors_file))
                if len(self.vectors) != len(self.chunks):
                    self._rebuild_vectors()
            except Exception:
                self._rebuild_vectors()
        elif len(self.chunks) > 0:
            self._rebuild_vectors()
        else:
            self.vectors = None

        if self.docs_metadata_file.exists():
            try:
                with open(self.docs_metadata_file, "r", encoding="utf-8") as f:
                    self.documents_meta = json.load(f)
            except Exception:
                self.documents_meta = {}

        self.bm25.build(self.chunks)

    def reload(self):
        self._load()

    def _save(self):
        with open(self.chunks_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
            
        with open(self.docs_metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.documents_meta, f, ensure_ascii=False, indent=2)

        if self.vectors is not None and len(self.vectors) > 0:
            np.save(str(self.vectors_file), self.vectors)
        elif self.vectors_file.exists():
            self.vectors_file.unlink()

        self.bm25.build(self.chunks)

    def _rebuild_vectors(self):
        if not self.chunks:
            self.vectors = None
            return
        texts = [c["content"] for c in self.chunks]
        embeddings = self.embedder.embed_texts(texts)
        self.vectors = np.array(embeddings, dtype=np.float32)
        np.save(str(self.vectors_file), self.vectors)

    def add_document(self, doc_id: str, doc_name: str, chunks: List[TextChunk], meta: Dict[str, Any] = None):
        self.delete_document(doc_id, save=False)

        new_chunk_dicts = [c.to_dict() for c in chunks]
        if not new_chunk_dicts:
            return

        texts = [c["content"] for c in new_chunk_dicts]
        new_vecs = self.embedder.embed_texts(texts)
        new_vecs_arr = np.array(new_vecs, dtype=np.float32)

        start_idx = len(self.chunks)
        for i, c in enumerate(new_chunk_dicts):
            self.chunk_id_to_idx[c["chunk_id"]] = start_idx + i
        self.chunks.extend(new_chunk_dicts)

        if self.vectors is None or len(self.vectors) == 0:
            self.vectors = new_vecs_arr
        else:
            self.vectors = np.vstack([self.vectors, new_vecs_arr])

        self.documents_meta[doc_id] = {
            "doc_id": doc_id,
            "doc_name": doc_name,
            "chunk_count": len(new_chunk_dicts),
            "created_at": new_chunk_dicts[0]["created_at"],
            "metadata": meta or {}
        }

        self._save()

    def delete_document(self, doc_id: str, save: bool = True):
        if doc_id not in self.documents_meta:
            matching = [idx for idx, c in enumerate(self.chunks) if c["doc_id"] == doc_id]
            if not matching:
                return

        indices_to_keep = [idx for idx, c in enumerate(self.chunks) if c["doc_id"] != doc_id]
        
        self.chunks = [self.chunks[i] for i in indices_to_keep]
        self.chunk_id_to_idx = {c["chunk_id"]: idx for idx, c in enumerate(self.chunks)}
        
        if self.vectors is not None and len(indices_to_keep) > 0:
            self.vectors = self.vectors[indices_to_keep]
        else:
            self.vectors = None

        self.documents_meta.pop(doc_id, None)

        if save:
            self._save()

    def search(
        self,
        query: str,
        top_k: int = 4,
        similarity_threshold: float = 0.30,
        doc_filter: Optional[str] = None,
        hybrid: bool = True,
        rrf_k: int = 60
    ) -> List[RetrievalResult]:
        if not self.chunks or self.vectors is None or len(self.vectors) == 0:
            return []

        # 1. Dense Vector Search (Cosine Similarity)
        q_vec = np.array(self.embedder.embed_query(query), dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 1e-9:
            q_vec = q_vec / q_norm

        dense_scores = np.dot(self.vectors, q_vec)
        
        # 2. Sparse BM25 Search
        bm25_scores = self.bm25.score(query) if hybrid else {}

        # 3. Extract meaningful tokens from query to check lexical overlap
        query_words = set(re.findall(r'\b[a-zA-Z0-9_\-\.]+\b', query.lower())) - STOPWORDS

        candidates = []
        for idx, chunk in enumerate(self.chunks):
            if doc_filter and chunk["doc_id"] != doc_filter:
                continue

            c_id = chunk["chunk_id"]
            d_score = float(dense_scores[idx])
            b_score = float(bm25_scores.get(c_id, 0.0))

            c_words = set(re.findall(r'\b[a-zA-Z0-9_\-\.]+\b', chunk["content"].lower()))
            overlap_count = len(query_words.intersection(c_words))
            overlap_ratio = overlap_count / max(1, len(query_words)) if query_words else 0.0

            candidates.append((chunk, d_score, b_score, overlap_ratio))

        if not candidates:
            return []

        scored_results = []
        for chunk, d_score, b_score, o_ratio in candidates:
            c_id = chunk["chunk_id"]
            if o_ratio > 0:
                blended_sim = 0.5 * max(0.0, d_score) + 0.3 * b_score + 0.2 * o_ratio
            else:
                blended_sim = 0.25 * max(0.0, d_score)

            scored_results.append(RetrievalResult(
                chunk_id=chunk["chunk_id"],
                doc_id=chunk["doc_id"],
                doc_name=chunk["doc_name"],
                page_number=chunk["page_number"],
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                score=blended_sim,
                dense_score=d_score,
                bm25_score=b_score,
                metadata=chunk.get("metadata", {})
            ))

        scored_results.sort(key=lambda x: x.score, reverse=True)
        filtered = [r for r in scored_results if r.score >= similarity_threshold]
        return filtered[:top_k]

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        return [c for c in self.chunks if c["doc_id"] == doc_id]

    def list_documents(self) -> List[Dict[str, Any]]:
        return list(self.documents_meta.values())

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self.documents_meta),
            "total_chunks": len(self.chunks),
            "vector_dimension": self.vectors.shape[1] if self.vectors is not None else 0,
            "index_status": "healthy"
        }

_shared_vector_store: Optional[EnterpriseVectorStore] = None

def get_shared_vector_store(db_dir: Path = None, embedder: BaseEmbedder = None) -> EnterpriseVectorStore:
    global _shared_vector_store
    if _shared_vector_store is None:
        if db_dir is None:
            from .config import VECTOR_DB_DIR
            db_dir = VECTOR_DB_DIR
        if embedder is None:
            from .embeddings import get_embedder
            from .config import settings
            embedder = get_embedder(settings.embedding_provider, api_key=settings.gemini_api_key)
        _shared_vector_store = EnterpriseVectorStore(db_dir, embedder)
    return _shared_vector_store
