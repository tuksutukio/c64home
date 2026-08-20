"""Byte-oriented LZSS matching cbm-joy's planned 6502 decompressor format.

Stream = [2-byte LE uncompressed length][token groups]
Each group = 1 control byte (8 flag bits, LSB-first) + up to 8 tokens.
Flag bit 1 -> literal byte follows.
Flag bit 0 -> match follows: [offset][length], distance = offset+1 (1-256),
length = length byte directly (2-255). Decompression stops once the
length-prefixed byte count is produced.
"""
import sys

WINDOW = 256
MIN_MATCH = 2
MAX_MATCH = 255

def find_longest_match(data, pos):
    best_len, best_dist = 0, 0
    start = max(0, pos - WINDOW)
    for cand in range(start, pos):
        length = 0
        while (pos + length < len(data)
               and length < MAX_MATCH
               and data[cand + length] == data[pos + length]):
            # allow overlap: cand+length may reach into [pos, pos+length)
            length += 1
        if length > best_len:
            best_len, best_dist = length, pos - cand
    return best_len, best_dist

def compress(data):
    out = bytearray(len(data).to_bytes(2, "little"))
    pos = 0
    tokens = []  # list of ('lit', byte) or ('match', dist, length)
    while pos < len(data):
        length, dist = find_longest_match(data, pos)
        if length >= MIN_MATCH:
            tokens.append(("match", dist, length))
            pos += length
        else:
            tokens.append(("lit", data[pos]))
            pos += 1

    i = 0
    while i < len(tokens):
        group = tokens[i:i + 8]
        flags = 0
        body = bytearray()
        for bit, tok in enumerate(group):
            if tok[0] == "lit":
                flags |= (1 << bit)
                body.append(tok[1])
            else:
                _, dist, length = tok
                body.append(dist - 1)
                body.append(length)
        out.append(flags)
        out.extend(body)
        i += 8
    return bytes(out)

def decompress(comp):
    orig_len = comp[0] | (comp[1] << 8)
    out = bytearray()
    p = 2
    while len(out) < orig_len:
        flags = comp[p]; p += 1
        for bit in range(8):
            if len(out) >= orig_len:
                break
            if flags & (1 << bit):
                out.append(comp[p]); p += 1
            else:
                dist = comp[p] + 1; length = comp[p + 1]; p += 2
                for _ in range(length):
                    out.append(out[-dist])
    return bytes(out)

def to_asm(data, label):
    lines = [f"{label}:"]
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        lines.append("        .byte " + ",".join(f"${b:02X}" for b in chunk))
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    path = sys.argv[1]
    data = open(path, "rb").read()
    comp = compress(data)
    rt = decompress(comp)
    assert rt == data, "round-trip mismatch!"
    print(f"{path}: {len(data)} -> {len(comp)} bytes "
          f"({100*len(comp)/len(data):.1f}%), round-trip OK", file=sys.stderr)

    if len(sys.argv) > 2 and sys.argv[2] == "--asm":
        label = sys.argv[3]
        print(to_asm(comp, label))
