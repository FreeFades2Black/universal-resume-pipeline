"""
Universal Resume Pipeline - Command Line Interface (CLI)
Usage:
    python -m cli.resume_pipeline_cli resume.pdf --output resume_payload.json --pretty
    python -m cli.resume_pipeline_cli "raw text..." --output payload.json
"""

import sys
import os
import argparse
import json

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.extractors.pipeline import UniversalResumePipeline
from backend.app.extractors.text_extractor import TextExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Universal Resume Extraction & Normalization CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python -m cli.resume_pipeline_cli candidate_resume.pdf -o payload.json
  python -m cli.resume_pipeline_cli samples/sample_resume_software_engineer.txt --pretty
  python -m cli.resume_pipeline_cli resume.docx --prefer-llm --provider openai
"""
    )
    parser.add_argument(
        "input",
        help="Path to resume file (.pdf, .docx, .txt, .json) or raw text string"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path to save the normalized JSON payload",
        default=None
    )
    parser.add_argument(
        "--prefer-llm",
        action="store_true",
        help="Attempt LLM extraction if provider keys are configured"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "gemini", "ollama"],
        default=None,
        help="Specific LLM provider to use"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Format JSON output with 2-space indentation (default: True)"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output minified compact JSON"
    )

    args = parser.parse_args()

    pipeline = UniversalResumePipeline(
        prefer_llm=args.prefer_llm,
        default_provider=args.provider
    )

    filename = os.path.basename(args.input) if os.path.exists(args.input) else "direct_input.txt"
    
    try:
        # Attempt UTF-8 reconfiguration on Windows console if supported
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    try:
        payload = pipeline.process(
            file_input=args.input,
            filename=filename,
            override_provider=args.provider
        )

        indent = None if args.compact else 2
        json_output = payload.model_dump_json(indent=indent)

        if args.output:
            out_dir = os.path.dirname(args.output)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"[SUCCESS] Normalized resume saved to: {args.output}")
            print(f"[INFO] Extracted: {payload.personal_information.full_name or 'Candidate'}, "
                  f"{len(payload.work_history)} experiences, "
                  f"{len(payload.skills)} skills, "
                  f"{len(payload.education)} schools.")
        else:
            print("\n================ Universal Autofill Payload ================")
            print(json_output)
            print("============================================================\n")

    except Exception as e:
        print(f"[ERROR] Resume extraction failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
