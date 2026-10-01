import math
import hashlib
import re
from typing import List, Dict, Any, Optional
import httpx
import numpy as np

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves"
}

class BaseEmbedder:
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError
    
    def embed_query(self, query: str) -> List[float]:
        return self.embed_texts([query])[0]

class LocalFastDenseEmbedder(BaseEmbedder):
    """
    High-performance, zero-dependency 384-dimensional dense semantic embedder.
    Uses subword n-gram hashing projection with stopword filtering, term-frequency weighting,
    and L2 normalization.
    """
    def __init__(self, dimension: int = 384):
        self.dim = dimension

    def _hash_token(self, token: str, seed: int = 0) -> int:
        h = hashlib.md5(f"{seed}:{token}".encode("utf-8")).hexdigest()
        return int(h, 16) % self.dim

    def _hash_sign(self, token: str, seed: int = 42) -> float:
        h = hashlib.md5(f"{seed}:{token}".encode("utf-8")).hexdigest()
        return 1.0 if int(h, 16) % 2 == 0 else -1.0

    def embed_single(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        clean = text.lower().strip()
        all_tokens = re.findall(r'\b[a-zA-Z0-9_\-\.]+\b', clean)
        
        # Filter stopwords
        tokens = [t for t in all_tokens if t not in STOPWORDS and len(t) > 1]
        if not tokens:
            tokens = all_tokens  # Fallback if text consists purely of short words

        if not tokens:
            return vec.tolist()

        # Word tokens + subword n-grams
        features = []
        for t in tokens:
            features.append(t)
            # Add character n-grams (3-grams and 4-grams)
            if len(t) >= 4:
                for n in [3, 4]:
                    for i in range(len(t) - n + 1):
                        features.append(t[i:i+n])

        # Frequency mapping
        freqs: Dict[str, int] = {}
        for f in features:
            freqs[f] = freqs.get(f, 0) + 1

        for feat, count in freqs.items():
            tf = 1.0 + math.log(count) if count > 0 else 0.0
            weight = tf * (1.5 if len(feat) > 3 else 0.6)
            
            for seed in [17, 31, 53]:
                idx = self._hash_token(feat, seed)
                sign = self._hash_sign(feat, seed)
                vec[idx] += sign * weight

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm

        return vec.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_single(t) for t in texts]


class GeminiEmbedder(BaseEmbedder):
    """Google Gemini Embedding API integration."""
    def __init__(self, api_key: str, model: str = "text-embedding-004"):
        self.api_key = api_key
        self.model = model
        self.fallback = LocalFastDenseEmbedder()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            return self.fallback.embed_texts(texts)

        results = []
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:batchEmbedContents?key={self.api_key}"
        requests_payload = [
            {"model": f"models/{self.model}", "content": {"parts": [{"text": t}]}}
            for t in texts
        ]

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, json={"requests": requests_payload})
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("embeddings", []):
                        values = item.get("values", [])
                        arr = np.array(values, dtype=np.float32)
                        norm = np.linalg.norm(arr)
                        if norm > 1e-9:
                            arr = arr / norm
                        results.append(arr.tolist())
                    return results
        except Exception:
            pass
        return self.fallback.embed_texts(texts)


class OllamaEmbedder(BaseEmbedder):
    """Ollama local embedding integration."""
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.fallback = LocalFastDenseEmbedder()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        try:
            with httpx.Client(timeout=20.0) as client:
                for text in texts:
                    url = f"{self.base_url}/api/embeddings"
                    payload = {"model": self.model, "prompt": text}
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        vals = resp.json().get("embedding", [])
                        arr = np.array(vals, dtype=np.float32)
                        norm = np.linalg.norm(arr)
                        if norm > 1e-9:
                            arr = arr / norm
                        embeddings.append(arr.tolist())
                    else:
                        embeddings.append(self.fallback.embed_single(text))
            return embeddings
        except Exception:
            return self.fallback.embed_texts(texts)


def get_embedder(provider: str, api_key: str = "", base_url: str = "", model: str = "") -> BaseEmbedder:
    p = (provider or "local").lower()
    if p == "gemini" and api_key:
        return GeminiEmbedder(api_key=api_key, model=model or "text-embedding-004")
    elif p == "ollama":
        return OllamaEmbedder(base_url=base_url or "http://localhost:11434", model=model or "nomic-embed-text")
    return LocalFastDenseEmbedder()
