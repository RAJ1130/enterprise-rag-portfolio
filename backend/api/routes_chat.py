import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from core.config import settings, VECTOR_DB_DIR
from core.vector_store import get_shared_vector_store
from core.guardrails import EnterpriseGuardrails
from core.llm_service import LLMService

router = APIRouter(prefix="/api/chat", tags=["chat"])

vector_store = get_shared_vector_store()


class ChatRequest(BaseModel):
    query: str
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    top_k: Optional[int] = None
    similarity_threshold: Optional[float] = None
    doc_filter: Optional[str] = None
    strict_guardrails: Optional[bool] = True

class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    confidence_score: float
    faithfulness_score: float
    hallucination_risk: str
    guardrail_report: Dict[str, Any]
    provider_used: str
    latency_ms: int

@router.post("", response_model=ChatResponse)
def query_rag(req: ChatRequest):
    start_time = time.time()
    raw_query = req.query.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Guardrail Pre-Check: Prompt Injection & PII Sanitization
    passed_pre_check, sanitized_query, issues = EnterpriseGuardrails.pre_check_query(raw_query)
    
    if not passed_pre_check and req.strict_guardrails:
        latency = int((time.time() - start_time) * 1000)
        return ChatResponse(
            query=raw_query,
            answer="**Security Policy Violation**: Your query triggered an Enterprise Security Guardrail (Potential Prompt Injection attempt detected). The request has been blocked for enterprise compliance.",
            citations=[],
            retrieved_chunks=[],
            confidence_score=0.0,
            faithfulness_score=0.0,
            hallucination_risk="HIGH",
            guardrail_report={
                "pre_check_passed": False,
                "issues": issues,
                "blocked": True,
                "reason": "Prompt injection pattern detected."
            },
            provider_used="Security Guardrail",
            latency_ms=latency
        )

    # 2. Vector Retrieval with Hybrid Dense + BM25 Search
    top_k = req.top_k or settings.top_k
    threshold = req.similarity_threshold if req.similarity_threshold is not None else settings.similarity_threshold
    
    retrieved = vector_store.search(
        query=sanitized_query,
        top_k=top_k,
        similarity_threshold=threshold,
        doc_filter=req.doc_filter,
        hybrid=settings.hybrid_search
    )

    # 3. Anti-Hallucination Relevance Gate
    relevance_passed, top_score, rel_reason = EnterpriseGuardrails.evaluate_retrieval_relevance(
        retrieved, threshold=threshold
    )

    if not relevance_passed and req.strict_guardrails:
        latency = int((time.time() - start_time) * 1000)
        return ChatResponse(
            query=raw_query,
            answer=(
                "**No Grounded Knowledge Available**: Based solely on verified internal documentation, "
                f"there is insufficient documented evidence to answer this question accurately (Top relevance: {top_score:.1%}, threshold: {threshold:.1%}).\n\n"
                "To maintain strict zero-hallucination compliance, the model will not speculate or make assumptions. "
                "Please verify the document is uploaded or refine your search keywords."
            ),
            citations=[],
            retrieved_chunks=[c.to_dict() for c in retrieved],
            confidence_score=top_score,
            faithfulness_score=0.0,
            hallucination_risk="HIGH",
            guardrail_report={
                "pre_check_passed": True,
                "issues": issues,
                "relevance_gate_passed": False,
                "reason": rel_reason
            },
            provider_used="Anti-Hallucination Guardrail",
            latency_ms=latency
        )

    # 4. LLM Generation
    llm_result = LLMService.generate_response(
        query=sanitized_query,
        chunks=retrieved,
        provider=req.provider or settings.llm_provider,
        api_key=req.api_key or settings.gemini_api_key,
        model=req.model or settings.gemini_model,
        base_url=req.base_url or settings.ollama_base_url
    )
    answer = llm_result["answer"]
    provider_used = llm_result["provider_used"]

    # 5. Faithfulness & Citation Verification
    faith_result = EnterpriseGuardrails.verify_answer_faithfulness(answer, retrieved)

    latency = int((time.time() - start_time) * 1000)

    return ChatResponse(
        query=raw_query,
        answer=answer,
        citations=faith_result.verified_citations,
        retrieved_chunks=[c.to_dict() for c in retrieved],
        confidence_score=faith_result.confidence_score,
        faithfulness_score=faith_result.faithfulness_score,
        hallucination_risk=faith_result.hallucination_risk,
        guardrail_report={
            "pre_check_passed": True,
            "issues": issues,
            "relevance_gate_passed": True,
            "faithfulness_passed": faith_result.passed,
            "reason": faith_result.reason
        },
        provider_used=provider_used,
        latency_ms=latency
    )


@router.get("/sample-prompts")
def get_sample_prompts():
    """Returns grounded sample prompts based on enterprise documents."""
    return {
        "prompts": [
            {
                "category": "Portfolio & Resume",
                "prompt": "What are Mummalar Raj's technical skills, education, and internship experience?",
                "doc": "Mummalar_Raj_Resume.pdf"
            },
            {
                "category": "Projects",
                "prompt": "What projects has Mummalar Raj built and what technologies were used?",
                "doc": "Mummalar_Raj_Resume.md"
            },
            {
                "category": "IT Security Policy",
                "prompt": "What are the mandatory password hygiene standards and rotation schedule in the security policy?",
                "doc": "Enterprise_Security_and_Access_Control_Policy.pdf"
            },
            {
                "category": "API Gateway Specs",
                "prompt": "What are the rate limits and burst allowances for the Enterprise Tier in the API gateway?",
                "doc": "Cloud_Infrastructure_API_Gateway_Specification.md"
            },
            {
                "category": "Zero-Hallucination Test",
                "prompt": "What is the corporate pet policy for bringing dogs to the office?",
                "doc": "Out-of-Scope (Should Refuse)"
            }
        ]
    }

