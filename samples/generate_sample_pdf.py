"""
Zero-dependency PDF Generator
Generates a valid, parseable sample PDF resume for testing without requiring reportlab or external binaries.
"""

import os


def generate_minimal_pdf(output_path: str, text_content: str):
    """
    Constructs a standard conforming PDF 1.4 file containing raw text stream.
    """
    # Clean text to single-line escaped strings for PDF Tj operators
    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
    
    stream_content = "BT\n/F1 12 Tf\n50 750 Td\n14 TL\n"
    for line in lines:
        # Escape parenthesis and backslashes
        safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_content += f"({safe_line}) '\n"
    stream_content += "ET"

    stream_bytes = stream_content.encode("latin-1", errors="ignore")
    stream_len = len(stream_bytes)

    objects = []
    
    # 1: Catalog
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    # 2: Pages
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    # 3: Page
    objects.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n")
    # 4: Stream
    objects.append(f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode("latin-1") + stream_bytes + b"\nendstream\nendobj\n")
    # 5: Font
    objects.append(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    # Assemble PDF with xref table
    pdf_bytes = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []

    for obj in objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj)

    xref_offset = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for offset in offsets:
        pdf_bytes.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    pdf_bytes.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1"))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Generated Sample PDF: {output_path} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    sample_txt_path = os.path.join(os.path.dirname(__file__), "sample_resume_software_engineer.txt")
    with open(sample_txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    out_pdf = os.path.join(os.path.dirname(__file__), "sample_resume_cloud_engineer.pdf")
    generate_minimal_pdf(out_pdf, text)
