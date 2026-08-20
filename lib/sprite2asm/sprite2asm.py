#!/usr/bin/env python3
"""Convert a 24x21 '.'/'*' text grid into ca65 .byte lines for a VIC-II
monochrome sprite (3 bytes/row x 21 rows = 63 bytes). '*' = lit pixel (bit
set), '.' = transparent (bit clear). Usage: sprite2asm.py sprite1.txt
"""
import sys

def convert(path):
    with open(path) as f:
        rows = [line.rstrip("\n") for line in f if line.strip()]

    if len(rows) != 21:
        sys.exit(f"{path}: expected 21 rows, got {len(rows)}")
    for r in rows:
        if len(r) != 24:
            sys.exit(f"{path}: expected 24 columns, got {len(r)}: {r!r}")

    lines = []
    for row in rows:
        row_bytes = []
        for byte_i in range(3):
            byte = 0
            for bit_i in range(8):
                ch = row[byte_i * 8 + bit_i]
                if ch == "*":
                    byte |= 0x80 >> bit_i
                elif ch != ".":
                    sys.exit(f"{path}: unexpected char {ch!r} in {row!r}")
            row_bytes.append(byte)
        lines.append("        .byte " + ",".join(f"${b:02X}" for b in row_bytes))
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <sprite.txt>")
    print(convert(sys.argv[1]))
