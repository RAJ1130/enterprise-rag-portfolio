import os
import shutil
import uuid
import time
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from core.config import settings, DOCUMENTS_DIR, SAMPLES_DIR, VECTOR_DB_DIR
from core.extractor import MultiFormatExtractor
from core.chunker import RecursiveSmartChunker
from core.embeddings import get_embedder
from core.vector_store import get_shared_vector_store

router = APIRouter(prefix="/api/documents", tags=["documents"])

vector_store = get_shared_vector_store()


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    results = []
    chunker = RecursiveSmartChunker(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)

    for file in files:
        safe_filename = Path(file.filename).name
        doc_id = str(uuid.uuid4())[:8] + "_" + safe_filename
        dest_path = DOCUMENTS_DIR / doc_id

        # Save file to disk
        try:
            with open(dest_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save {safe_filename}: {str(e)}")

        file_size = dest_path.stat().st_size

        try:
            # 1. Multi-format extraction
            pages = MultiFormatExtractor.extract_from_file(dest_path)
            if not pages:
                raise ValueError("No readable text could be extracted from document.")

            # 2. Smart Chunking
            chunks = chunker.chunk_document_pages(doc_id=doc_id, doc_name=safe_filename, pages=pages)
            if not chunks:
                raise ValueError("Text was too short or could not produce valid chunks.")

            # 3. Vector Store Ingestion
            vector_store.add_document(
                doc_id=doc_id,
                doc_name=safe_filename,
                chunks=chunks,
                meta={
                    "filename": safe_filename,
                    "file_size": file_size,
                    "page_count": len(pages),
                    "chunk_count": len(chunks),
                    "upload_time": time.time(),
                    "file_type": dest_path.suffix.lower()
                }
            )

            results.append({
                "doc_id": doc_id,
                "doc_name": safe_filename,
                "page_count": len(pages),
                "chunk_count": len(chunks),
                "file_size": file_size,
                "status": "indexed"
            })
        except Exception as e:
            # Cleanup on failure
            if dest_path.exists():
                dest_path.unlink()
            results.append({
                "doc_id": doc_id,
                "doc_name": safe_filename,
                "status": "failed",
                "error": str(e)
            })

    return {"uploaded": results, "total_docs": len(vector_store.list_documents())}


@router.get("")
def list_documents():
    docs = vector_store.list_documents()
    formatted = []
    for d in docs:
        formatted.append({
            "doc_id": d["doc_id"],
            "doc_name": d["doc_name"],
            "chunk_count": d.get("chunk_count", 0),
            "page_count": d.get("metadata", {}).get("page_count", 1),
            "file_size": d.get("metadata", {}).get("file_size", 0),
            "upload_time": d.get("created_at", 0),
            "file_type": d.get("metadata", {}).get("file_type", "txt")
        })
    # Sort newest first
    formatted.sort(key=lambda x: x["upload_time"], reverse=True)
    return {"documents": formatted, "count": len(formatted)}


@router.get("/{doc_id}/chunks")
def get_document_chunks(doc_id: str):
    chunks = vector_store.get_document_chunks(doc_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document chunks not found.")
    return {"doc_id": doc_id, "chunks": chunks, "count": len(chunks)}


@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    # Remove file if exists
    doc_path = DOCUMENTS_DIR / doc_id
    if doc_path.exists():
        doc_path.unlink()

    vector_store.delete_document(doc_id)
    return {"status": "deleted", "doc_id": doc_id}


@router.post("/load-sample")
def load_sample_documents():
    """Ingests enterprise sample files into the knowledge base."""
    loaded = []
    chunker = RecursiveSmartChunker(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)

    sample_files = list(SAMPLES_DIR.glob("*.*"))
    for file_path in sample_files:
        if file_path.suffix.lower() not in [".pdf", ".md", ".txt", ".csv", ".json"]:
            continue

        doc_id = "sample_" + file_path.name
        dest_path = DOCUMENTS_DIR / doc_id
        shutil.copy2(file_path, dest_path)

        try:
            pages = MultiFormatExtractor.extract_from_file(dest_path)
            chunks = chunker.chunk_document_pages(doc_id=doc_id, doc_name=file_path.name, pages=pages)
            vector_store.add_document(
                doc_id=doc_id,
                doc_name=file_path.name,
                chunks=chunks,
                meta={
                    "filename": file_path.name,
                    "file_size": dest_path.stat().st_size,
                    "page_count": len(pages),
                    "chunk_count": len(chunks),
                    "upload_time": time.time(),
                    "file_type": file_path.suffix.lower(),
                    "is_sample": True
                }
            )
            loaded.append({
                "doc_name": file_path.name,
                "pages": len(pages),
                "chunks": len(chunks)
            })
        except Exception as e:
            print(f"Error loading sample {file_path.name}: {e}")

    return {
        "status": "success",
        "loaded_samples": loaded,
        "total_documents": len(vector_store.list_documents())
    }
