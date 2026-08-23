"""
Zero-dependency PNG Icon Generator for Chrome Extension
Creates crisp gradient lightning badge icons (16x16, 48x48, 128x128).
"""

import struct
import zlib
import os


def create_png(width, height, output_path):
    raw_data = bytearray()
    
    for y in range(height):
        raw_data.append(0)  # Filter byte: 0 (None)
        for x in range(width):
            # Normalized coordinates (0 to 1)
            nx = x / width
            ny = y / height
            
            # Distance from center
            cx, cy = 0.5, 0.5
            dist = ((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5

            if dist > 0.46:
                # Transparent outside circle/rounded rect
                raw_data.extend([0, 0, 0, 0])
            else:
                # Background gradient: Blue (#1f6feb) to Cyan (#58a6ff)
                r = int(31 + (88 - 31) * nx)
                g = int(111 + (166 - 111) * ny)
                b = int(235 + (255 - 235) * nx)
                
                # Lightning bolt shape in center
                # Rough polygon check for lightning bolt
                is_bolt = False
                bx, by = (nx - 0.5) * 2, (ny - 0.5) * 2  # -1 to +1
                
                # Top half triangle of lightning
                if (-0.3 <= bx <= 0.3) and (-0.5 <= by <= 0.1) and (by > -1.5 * bx - 0.3):
                    is_bolt = True
                # Bottom half triangle of lightning
                if (-0.2 <= bx <= 0.4) and (-0.1 <= by <= 0.5) and (by < -1.5 * bx + 0.3):
                    is_bolt = True

                if is_bolt:
                    # White/yellow lightning bolt
                    raw_data.extend([255, 255, 255, 255])
                else:
                    raw_data.extend([r, g, b, 255])

    # PNG Signature
    png = b"\x89PNG\r\n\x1a\n"
    
    # IHDR Chunk
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xffffffff
    png += struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

    # IDAT Chunk
    compressed_data = zlib.compress(bytes(raw_data), level=9)
    idat_crc = zlib.crc32(b"IDAT" + compressed_data) & 0xffffffff
    png += struct.pack(">I", len(compressed_data)) + b"IDAT" + compressed_data + struct.pack(">I", idat_crc)

    # IEND Chunk
    iend_crc = zlib.crc32(b"IEND") & 0xffffffff
    png += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(png)
    print(f"Generated PNG: {output_path} ({width}x{height})")


if __name__ == "__main__":
    icon_dir = os.path.join(os.path.dirname(__file__), "..", "extension", "icons")
    create_png(16, 16, os.path.join(icon_dir, "icon16.png"))
    create_png(48, 48, os.path.join(icon_dir, "icon48.png"))
    create_png(128, 128, os.path.join(icon_dir, "icon128.png"))
