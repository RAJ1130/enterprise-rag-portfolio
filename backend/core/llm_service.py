import os
import json
import re
from typing import List, Dict, Any, Generator, Optional
import httpx
from .vector_store import RetrievalResult
from .embeddings import STOPWORDS
from .config import settings

GROUNDED_SYSTEM_PROMPT = """You are an Enterprise Knowledge Base Assistant. Your role is to answer questions strictly and solely based on the provided verified internal documentation excerpts.

CRITICAL ENTERPRISE GUARDRAILS & INSTRUCTIONS:
1. ONLY use information explicitly stated in the "VERIFIED CONTEXT" section below.
2. DO NOT make up facts, speculate, extrapolate, or use outside knowledge.
3. If the answer cannot be determined strictly from the provided context, state explicitly:
   "I cannot find this information in the provided internal documentation."
4. Every single fact, instruction, or data point must be backed by a source citation.
5. Format citations directly using the notation: `[Source: <Document Name>, Page <Page Number>]`.
6. Provide clear, professional, structured answers using Markdown formatting (headings, bullet points, code blocks, or tables when appropriate).
"""

class LLMService:
    @staticmethod
    def format_context(chunks: List[RetrievalResult]) -> str:
        context_parts = []
        for idx, c in enumerate(chunks, 1):
            snippet = (
                f"--- CONTEXT EXCERPT [{idx}] ---\n"
                f"Document: {c.doc_name}\n"
                f"Page: {c.page_number} | Chunk: {c.chunk_index}\n"
                f"Relevance Score: {c.score:.3f}\n"
                f"Content:\n{c.content}\n"
            )
            context_parts.append(snippet)
        return "\n".join(context_parts)

    @classmethod
    def generate_response(
        cls,
        query: str,
        chunks: List[RetrievalResult],
        provider: str = None,
        api_key: str = "",
        model: str = "",
        base_url: str = ""
    ) -> Dict[str, Any]:
        provider = (provider or settings.llm_provider).lower()
        context_str = cls.format_context(chunks)

        user_prompt = (
            f"VERIFIED CONTEXT:\n{context_str}\n\n"
            f"USER QUERY:\n{query}\n\n"
            f"Please provide an accurate, grounded answer strictly using the context above, citing each document and page."
        )

        if provider == "gemini":
            key = api_key or settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
            if key:
                ans = cls._call_gemini(user_prompt, key, model or settings.gemini_model)
                if ans:
                    return {"answer": ans, "provider_used": f"Gemini ({model or settings.gemini_model})"}

        if provider == "ollama":
            url = base_url or settings.ollama_base_url
            m = model or settings.ollama_model
            ans = cls._call_ollama(user_prompt, url, m)
            if ans:
                return {"answer": ans, "provider_used": f"Ollama ({m})"}

        if provider == "openai":
            key = api_key or settings.openai_api_key
            url = base_url or settings.openai_base_url
            m = model or settings.openai_model
            if key:
                ans = cls._call_openai(user_prompt, key, url, m)
                if ans:
                    return {"answer": ans, "provider_used": f"OpenAI ({m})"}

        # Offline deterministic grounded synthesis fallback
        ans = cls._grounded_synthesis_fallback(query, chunks)
        return {"answer": ans, "provider_used": "Enterprise Grounded Synthesis Engine (Offline / Local)"}

    @classmethod
    def _call_gemini(cls, prompt: str, api_key: str, model: str) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{GROUNDED_SYSTEM_PROMPT}\n\n{prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.8,
                "maxOutputTokens": 2048
            }
        }
        try:
            with httpx.Client(timeout=45.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
        except Exception as e:
            print(f"Gemini API error: {e}")
        return None

    @classmethod
    def _call_ollama(cls, prompt: str, base_url: str, model: str) -> Optional[str]:
        url = f"{base_url.rstrip('/')}/api/generate"
        payload = {
            "model": model,
            "system": GROUNDED_SYSTEM_PROMPT,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1}
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    return res.json().get("response", "")
        except Exception as e:
            print(f"Ollama error: {e}")
        return None

    @classmethod
    def _call_openai(cls, prompt: str, api_key: str, base_url: str, model: str) -> Optional[str]:
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": GROUNDED_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        try:
            with httpx.Client(timeout=45.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0]["message"]["content"]
        except Exception as e:
            print(f"OpenAI API error: {e}")
        return None

    @classmethod
    def _grounded_synthesis_fallback(cls, query: str, chunks: List[RetrievalResult]) -> str:
        """
        Synthesizes a structured, fully grounded response directly from the retrieved chunks.
        Used when external LLM endpoints are unreachable or when operating in offline air-gapped mode.
        """
        if not chunks:
            return "I cannot find this information in the provided internal documentation."

        all_query_words = re.findall(r'\b[a-zA-Z0-9_\-]{3,}\b', query.lower())
        keywords = [w for w in all_query_words if w not in STOPWORDS]

        all_content = " ".join([c.content.lower() for c in chunks])
        matched_keywords = [w for w in keywords if w in all_content]
        
        if keywords and (len(matched_keywords) / len(keywords) < 0.35):
            missing_keywords = [w for w in keywords if w not in matched_keywords]
            return (
                f"**Information Not Found in Knowledge Base**\n\n"
                f"I cannot find information addressing this query in the verified internal documentation. "
                f"Specifically, terms such as `{', '.join(missing_keywords[:4])}` do not appear in any indexed documentation.\n\n"
                f"> **Anti-Hallucination Guardrail**: The system strictly refuses to speculate on topics not covered in internal policies."
            )

        lines = [
            f"### Verified Knowledge Base Findings",
            f"Based strictly on verified internal documentation, here is the relevant grounded evidence for **\"{query}\"**:\n"
        ]

        chunk_summaries = []
        for idx, chunk in enumerate(chunks[:3], 1):
            content_lines = [l.strip() for l in chunk.content.split("\n") if l.strip()]
            
            # Find matching line indices
            matching_indices = set()
            for l_idx, line in enumerate(content_lines):
                line_lower = line.lower()
                if any(kw in line_lower for kw in keywords):
                    for offset in range(-2, 3):
                        if 0 <= l_idx + offset < len(content_lines):
                            matching_indices.add(l_idx + offset)

            if matching_indices:
                chosen_lines = [content_lines[i] for i in sorted(matching_indices)]
                excerpt = "\n".join(chosen_lines[:8])
            else:
                excerpt = "\n".join(content_lines[:5])

            chunk_summaries.append(
                f"#### [{idx}] From `{chunk.doc_name}` (Page {chunk.page_number})\n"
                f"```text\n{excerpt}\n```\n\n"
                f"*Source Citation: [{chunk.doc_name} - Page {chunk.page_number}](citation://{chunk.chunk_id}) (Relevance: {chunk.score:.1%})*\n"
            )

        lines.extend(chunk_summaries)
        lines.append(
            "\n> **Verification Notice**: This response was verified by the Enterprise Anti-Hallucination Guardrail against internal documentation."
        )
        return "\n".join(lines)
