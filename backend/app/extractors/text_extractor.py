"""
Multi-format Raw Text Extractor
Extracts clean, structured text representations from PDF, DOCX, TXT, and JSON files.
Includes robust fallbacks so parsing succeeds even in constrained runtime environments.
"""

import io
import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from typing import Union, BinaryIO


class TextExtractor:
    @staticmethod
    def extract(file_input: Union[str, bytes, BinaryIO], filename: str = "") -> str:
        """
        Main entry point for extracting text from a file path, bytes, or file-like object.
        """
        # If file_input is a filepath string or raw text
        if isinstance(file_input, str):
            if not os.path.exists(file_input):
                # If it doesn't exist on disk, treat as raw text content unless it looks like a missing file path
                if "\n" in file_input or "|" in file_input or "@" in file_input or len(file_input) > 40 or not file_input.lower().endswith((".pdf", ".docx", ".txt", ".json", ".doc")):
                    return file_input
                raise FileNotFoundError(f"File not found: {file_input}")
            
            ext = os.path.splitext(file_input)[1].lower()
            with open(file_input, "rb") as f:
                content_bytes = f.read()
            return TextExtractor._extract_from_bytes(content_bytes, ext or filename)
        
        # If file_input is bytes
        elif isinstance(file_input, bytes):
            return TextExtractor._extract_from_bytes(file_input, filename)
        
        # If file_input is a file-like stream
        elif hasattr(file_input, "read"):
            content_bytes = file_input.read()
            return TextExtractor._extract_from_bytes(content_bytes, filename)
        
        raise ValueError(f"Unsupported file_input type: {type(file_input)}")

    @staticmethod
    def _extract_from_bytes(content: bytes, filename_or_ext: str) -> str:
        ext = os.path.splitext(filename_or_ext)[1].lower() if "." in filename_or_ext else filename_or_ext.lower()
        
        # PDF Extraction
        if ext in [".pdf", "pdf"] or content.startswith(b"%PDF"):
            return TextExtractor._extract_pdf(content)
        
        # DOCX Extraction
        elif ext in [".docx", "docx"] or (content.startswith(b"PK") and b"word/document.xml" in content):
            return TextExtractor._extract_docx(content)
        
        # JSON Ingestion
        elif ext in [".json", "json"]:
            try:
                parsed_json = json.loads(content.decode("utf-8", errors="ignore"))
                return json.dumps(parsed_json, indent=2)
            except Exception:
                return content.decode("utf-8", errors="ignore")
        
        # Plain text fallback (.txt, .md, etc.)
        else:
            return TextExtractor._extract_plaintext(content)

    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        extracted_text = []

        # Strategy 1: pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text(layout=True) or page.extract_text()
                    if text:
                        extracted_text.append(text)
            if extracted_text:
                return "\n\n".join(extracted_text)
        except ImportError:
            pass
        except Exception:
            pass

        # Strategy 2: pypdf / PyPDF2
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
            if extracted_text:
                return "\n\n".join(extracted_text)
        except ImportError:
            pass
        except Exception:
            pass

        # Strategy 3: PyMuPDF (fitz)
        try:
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                text = page.get_text()
                if text:
                    extracted_text.append(text)
            if extracted_text:
                return "\n\n".join(extracted_text)
        except ImportError:
            pass
        except Exception:
            pass

        # Strategy 4: Raw stream regex extraction fallback
        text_stream = content.decode("latin-1", errors="ignore")
        text_chunks = re.findall(r"\((.*?)\)[\s]*Tj", text_stream)
        if text_chunks:
            return " ".join(text_chunks)
        
        # Fallback to UTF-8/ASCII printable strings
        printable = "".join(chr(c) if 32 <= c <= 126 or c in [10, 13, 9] else " " for c in content)
        return re.sub(r"\s+", " ", printable).strip()

    @staticmethod
    def _extract_docx(content: bytes) -> str:
        # Strategy 1: python-docx
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)
            if paragraphs:
                return "\n".join(paragraphs)
        except ImportError:
            pass
        except Exception:
            pass

        # Strategy 2: Direct OpenXML extraction from zip stream (Zero external dependencies)
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                xml_content = z.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                paragraphs = []
                for p in tree.findall(".//w:p", namespaces):
                    texts = [t.text for t in p.findall(".//w:t", namespaces) if t.text]
                    if texts:
                        paragraphs.append("".join(texts))
                if paragraphs:
                    return "\n".join(paragraphs)
        except Exception:
            pass

        return TextExtractor._extract_plaintext(content)

    @staticmethod
    def _extract_plaintext(content: bytes) -> str:
        for encoding in ["utf-8", "utf-16", "latin-1", "windows-1252"]:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="ignore")
