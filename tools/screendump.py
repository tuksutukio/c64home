#!/usr/bin/env python3
"""Dump the C64 text screen over WiFi via ru64 peek (no video stream needed,
since Ultimate64 firmware disallows video/audio streaming over WiFi)."""
import argparse
import subprocess
import sys
import tempfile

SCREEN_ADDR = 0x0400
SCREEN_BYTES = 1000
COLS = 40


def decode(b):
    if b == 0:
        return "@"
    if 1 <= b <= 26:
        return chr(ord("A") + b - 1)
    if 32 <= b <= 63:
        return chr(b)
    return "."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="Ultimate64 IP or hostname")
    parser.add_argument("--ru64", default="ru64", help="path to ru64 binary")
    parser.add_argument(
        "--keep-blank", action="store_true", help="also print blank rows"
    )
    args = parser.parse_args()

    with tempfile.NamedTemporaryFile(suffix=".bin") as tmp:
        subprocess.run(
            [
                args.ru64,
                args.host,
                "peek",
                hex(SCREEN_ADDR),
                "-n",
                str(SCREEN_BYTES),
                "-o",
                tmp.name,
            ],
            check=True,
        )
        data = tmp.read()

    text = "".join(decode(b) for b in data)
    for row in range(SCREEN_BYTES // COLS):
        line = text[row * COLS : (row + 1) * COLS].rstrip()
        if line.strip() or args.keep_blank:
            print(f"{row:2d}: {line}")


if __name__ == "__main__":
    sys.exit(main())
