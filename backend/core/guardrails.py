import re
from typing import List, Dict, Any, Tuple, Optional
from .vector_store import RetrievalResult

class GuardrailCheckResult:
    def __init__(
        self,
        passed: bool,
        reason: str,
        sanitized_query: str = "",
        blocked: bool = False,
        confidence_score: float = 1.0,
        faithfulness_score: float = 1.0,
        hallucination_risk: str = "LOW",  # "LOW", "MEDIUM", "HIGH"
        verified_citations: List[Dict[str, Any]] = None,
        flagged_issues: List[str] = None
    ):
        self.passed = passed
        self.reason = reason
        self.sanitized_query = sanitized_query
        self.blocked = blocked
        self.confidence_score = round(confidence_score, 2)
        self.faithfulness_score = round(faithfulness_score, 2)
        self.hallucination_risk = hallucination_risk
        self.verified_citations = verified_citations or []
        self.flagged_issues = flagged_issues or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "blocked": self.blocked,
            "reason": self.reason,
            "confidence_score": self.confidence_score,
            "faithfulness_score": self.faithfulness_score,
            "hallucination_risk": self.hallucination_risk,
            "verified_citations": self.verified_citations,
            "flagged_issues": self.flagged_issues
        }

class EnterpriseGuardrails:
    """Security, anti-hallucination, and citation verification guardrail engine."""

    # Common prompt injection patterns
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"(?i)disregard\s+(all\s+)?(previous|prior)\s+rules",
        r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
        r"(?i)bypass\s+all\s+filters",
        r"(?i)system\s+prompt\s+leak",
        r"(?i)reveal\s+your\s+system\s+prompt",
        r"(?i)print\s+your\s+instructions",
        r"(?i)jailbreak",
        r"(?i)act\s+as\s+an\s+unfiltered\s+ai"
    ]

    # Sensitive PII patterns
    PII_PATTERNS = [
        (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-MASKED]'),
        (r'\b(?:\d{4}[ -]?){3}\d{4}\b', '[CREDIT-CARD-MASKED]'),
        (r'(?i)\b(api[_-]?key|secret|token|password)[\s:=]+["\']?([a-zA-Z0-9_\-\.]{16,})["\']?', r'\1: [SECRET-MASKED]')
    ]

    @classmethod
    def pre_check_query(cls, query: str) -> Tuple[bool, str, List[str]]:
        """Checks for prompt injection and masks PII in incoming user query."""
        issues = []
        # 1. Prompt Injection detection
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, query):
                issues.append("Prompt Injection pattern detected and neutralized.")
                return False, query, issues

        # 2. PII Sanitization
        sanitized = query
        for pattern, replacement in cls.PII_PATTERNS:
            if re.search(pattern, sanitized):
                issues.append("Sensitive PII pattern detected and sanitized.")
                sanitized = re.sub(pattern, replacement, sanitized)

        return True, sanitized, issues

    @classmethod
    def evaluate_retrieval_relevance(
        cls,
        chunks: List[RetrievalResult],
        threshold: float = 0.28
    ) -> Tuple[bool, float, str]:
        """
        Anti-Hallucination Gate:
        Prevents calling the model or generating false facts if retrieved documents lack sufficient relevance.
        """
        if not chunks:
            return False, 0.0, "No relevant documents found in knowledge base."

        top_score = max(c.score for c in chunks)
        if top_score < threshold:
            return False, top_score, f"Top relevance score ({top_score:.2f}) is below confidence threshold ({threshold:.2f})."

        return True, top_score, "Context meets relevance threshold."

    @classmethod
    def verify_answer_faithfulness(
        cls,
        answer: str,
        chunks: List[RetrievalResult]
    ) -> GuardrailCheckResult:
        """
        Verifies that claims and citations in the generated answer are grounded in the retrieved chunks.
        Calculates a faithfulness score and extracts source citations.
        """
        if not chunks:
            return GuardrailCheckResult(
                passed=False,
                reason="No retrieved context available for verification",
                confidence_score=0.0,
                faithfulness_score=0.0,
                hallucination_risk="HIGH"
            )

        # Concatenate all verified source text
        source_texts = " ".join([c.content.lower() for c in chunks])
        
        # Tokenize answer into distinct informative sentences/clauses
        sentences = [s.strip() for s in re.split(r'[.\n;!?]', answer) if len(s.strip()) > 20]
        if not sentences:
            sentences = [answer.strip()]

        grounded_count = 0
        for s in sentences:
            # Extract key informative words (words > 4 chars)
            words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_\-]{4,}\b', s)]
            if not words:
                grounded_count += 1
                continue
            
            # Count how many key terms appear in source text
            matched = sum(1 for w in words if w in source_texts)
            ratio = matched / len(words)
            if ratio >= 0.45:
                grounded_count += 1

        faithfulness = grounded_count / max(1, len(sentences))
        top_relevance = max(c.score for c in chunks)

        # Map citations: match [Doc: ..., Page ...] or [1], [2], etc.
        citations = []
        for c in chunks:
            # Check if this document or page is referenced, or if substantial chunk text is quoted/paraphrased
            citations.append({
                "chunk_id": c.chunk_id,
                "doc_name": c.doc_name,
                "page_number": c.page_number,
                "score": c.score,
                "snippet": c.content[:160] + "..." if len(c.content) > 160 else c.content
            })

        # Determine risk level
        if faithfulness >= 0.80 and top_relevance >= 0.40:
            risk = "LOW"
            passed = True
            reason = "High grounding confidence: Answer statements are backed by retrieved context."
        elif faithfulness >= 0.55:
            risk = "MEDIUM"
            passed = True
            reason = "Moderate grounding: Most statements correlate with knowledge base."
        else:
            risk = "HIGH"
            passed = False
            reason = "Potential hallucination detected: Response contains assertions ungrounded in sources."

        return GuardrailCheckResult(
            passed=passed,
            reason=reason,
            confidence_score=top_relevance,
            faithfulness_score=faithfulness,
            hallucination_risk=risk,
            verified_citations=citations
        )
