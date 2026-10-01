import os
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

class DocumentPage:
    def __init__(self, page_number: int, content: str, metadata: Dict[str, Any] = None):
        self.page_number = page_number
        self.content = content.strip()
        self.metadata = metadata or {}

class MultiFormatExtractor:
    """Extracts text and tabular data from PDF, TXT, MD, CSV, JSON files."""
    
    @staticmethod
    def extract_from_file(file_path: Path) -> List[DocumentPage]:
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return MultiFormatExtractor.extract_pdf(file_path)
        elif ext in [".txt", ".md", ".markdown"]:
            return MultiFormatExtractor.extract_text(file_path)
        elif ext == ".csv":
            return MultiFormatExtractor.extract_csv(file_path)
        elif ext == ".json":
            return MultiFormatExtractor.extract_json(file_path)
        else:
            # Fallback to plain text attempt
            return MultiFormatExtractor.extract_text(file_path)

    @staticmethod
    def extract_pdf(file_path: Path) -> List[DocumentPage]:
        pages = []
        try:
            reader = PdfReader(str(file_path))
            total_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                # Clean up repeated whitespace while preserving paragraph breaks
                clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
                clean_text = "\n".join(clean_lines)
                if clean_text:
                    pages.append(DocumentPage(
                        page_number=idx + 1,
                        content=clean_text,
                        metadata={
                            "total_pages": total_pages,
                            "file_type": "pdf"
                        }
                    ))
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF '{file_path.name}': {str(e)}")
        return pages

    @staticmethod
    def extract_text(file_path: Path) -> List[DocumentPage]:
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            content = file_path.read_text(encoding="latin-1", errors="replace")
        
        clean_text = content.strip()
        return [DocumentPage(page_number=1, content=clean_text, metadata={"file_type": file_path.suffix.lower()})]

    @staticmethod
    def extract_csv(file_path: Path) -> List[DocumentPage]:
        """Converts CSV tables into markdown-formatted tabular representations."""
        pages = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            if not rows:
                return []
                
            header = rows[0]
            # Convert to markdown table format
            md_lines = ["| " + " | ".join(header) + " |"]
            md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
            for row in rows[1:]:
                # Pad row if incomplete
                padded = row + [""] * (len(header) - len(row))
                md_lines.append("| " + " | ".join(padded[:len(header)]) + " |")
            
            content = f"# Table Data: {file_path.name}\n\n" + "\n".join(md_lines)
            pages.append(DocumentPage(page_number=1, content=content, metadata={"file_type": "csv", "total_rows": len(rows)}))
        except Exception as e:
            raise RuntimeError(f"Error parsing CSV '{file_path.name}': {str(e)}")
        return pages

    @staticmethod
    def extract_json(file_path: Path) -> List[DocumentPage]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            formatted = json.dumps(data, indent=2)
            content = f"# Structured JSON Specification: {file_path.name}\n```json\n{formatted}\n```"
            return [DocumentPage(page_number=1, content=content, metadata={"file_type": "json"})]
        except Exception as e:
            raise RuntimeError(f"Error parsing JSON '{file_path.name}': {str(e)}")
