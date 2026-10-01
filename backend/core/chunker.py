import re
import uuid
import time
from typing import List, Dict, Any
from .extractor import DocumentPage

class TextChunk:
    def __init__(
        self,
        chunk_id: str,
        doc_id: str,
        doc_name: str,
        page_number: int,
        chunk_index: int,
        content: str,
        metadata: Dict[str, Any] = None
    ):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.doc_name = doc_name
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.content = content.strip()
        self.char_count = len(self.content)
        self.token_estimate = max(1, len(self.content) // 4)
        self.metadata = metadata or {}
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "doc_name": self.doc_name,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "char_count": self.char_count,
            "token_estimate": self.token_estimate,
            "metadata": self.metadata,
            "created_at": self.created_at
        }

class RecursiveSmartChunker:
    """Smart recursive text chunker preserving paragraphs, lists, and tables."""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        if not separators:
            # Base case: split by character limit
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

        sep = separators[0]
        remaining_seps = separators[1:]
        
        parts = text.split(sep)
        chunks = []
        current_chunk = []
        current_len = 0

        for part in parts:
            part_len = len(part) + len(sep)
            if current_len + part_len <= self.chunk_size:
                current_chunk.append(part)
                current_len += part_len
            else:
                if current_chunk:
                    merged = sep.join(current_chunk).strip()
                    if merged:
                        chunks.append(merged)
                
                # If a single part exceeds chunk size, split it with next separator
                if len(part) > self.chunk_size:
                    sub_chunks = self._split_text(part, remaining_seps)
                    chunks.extend(sub_chunks)
                    current_chunk = []
                    current_len = 0
                else:
                    current_chunk = [part]
                    current_len = part_len

        if current_chunk:
            merged = sep.join(current_chunk).strip()
            if merged:
                chunks.append(merged)

        # Apply overlap between chunks if needed
        overlapped_chunks = []
        for i, c in enumerate(chunks):
            if i > 0 and self.chunk_overlap > 0:
                prev_tail = chunks[i - 1][-self.chunk_overlap:]
                combined = prev_tail + " ... " + c
                overlapped_chunks.append(combined)
            else:
                overlapped_chunks.append(c)

        return overlapped_chunks if overlapped_chunks else [text]

    def chunk_document_pages(
        self,
        doc_id: str,
        doc_name: str,
        pages: List[DocumentPage]
    ) -> List[TextChunk]:
        all_chunks = []
        chunk_idx = 0

        for page in pages:
            raw_text = page.content.strip()
            if not raw_text:
                continue
                
            raw_chunks = self._split_text(raw_text, self.separators)
            for c_text in raw_chunks:
                clean_text = c_text.strip()
                if len(clean_text) < 15:  # Skip tiny fragments
                    continue
                
                c_id = f"{doc_id}_p{page.page_number}_c{chunk_idx}"
                chunk = TextChunk(
                    chunk_id=c_id,
                    doc_id=doc_id,
                    doc_name=doc_name,
                    page_number=page.page_number,
                    chunk_index=chunk_idx,
                    content=clean_text,
                    metadata=page.metadata
                )
                all_chunks.append(chunk)
                chunk_idx += 1

        return all_chunks
