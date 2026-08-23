"""
Universal Resume Parsing Pipeline Orchestrator
Coordinates file text extraction, parsing strategy selection (LLM vs Regex Normalizer),
and validation into the UniversalResumePayload.
"""

import time
from typing import Union, BinaryIO, Optional, Dict, Any
from .text_extractor import TextExtractor
from .regex_normalizer import RegexNormalizer
from .llm_parser import LLMParser
from ..models.schema import UniversalResumePayload


class UniversalResumePipeline:
    def __init__(self, prefer_llm: bool = True, default_provider: Optional[str] = None):
        self.prefer_llm = prefer_llm
        self.default_provider = default_provider

    def process(
        self,
        file_input: Union[str, bytes, BinaryIO],
        filename: str = "",
        override_provider: Optional[str] = None
    ) -> UniversalResumePayload:
        """
        Executes the end-to-end extraction and normalization pipeline.
        """
        start_time = time.time()
        
        # Step 1: Text Extraction
        raw_text = TextExtractor.extract(file_input, filename=filename)
        
        # Step 2: Structured Parsing
        payload = None
        engine_used = "regex_normalizer"
        
        if self.prefer_llm and LLMParser.is_available():
            provider = override_provider or self.default_provider
            payload = LLMParser.parse_with_llm(raw_text, provider=provider)
            if payload:
                engine_used = payload.metadata.get("parser_engine", "llm")
        
        # Fallback to Regex Heuristic Normalizer
        if not payload:
            payload = RegexNormalizer.normalize(
                raw_text,
                source_metadata={"source_filename": filename}
            )
            engine_used = "regex_normalizer"

        # Step 3: Provenance Metadata & Timing
        duration_ms = round((time.time() - start_time) * 1000, 2)
        payload.metadata.update({
            "source_filename": filename,
            "pipeline_version": "1.0.0",
            "parsing_duration_ms": duration_ms,
            "engine_used": engine_used,
            "prefer_llm": self.prefer_llm
        })

        return payload
