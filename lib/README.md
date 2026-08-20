# lib/ — reusable code for C64/Ultimate64 projects

Actual **code**, not just write-ups — real effort that took a debugging
pass or two to get right, archived here so spin-off projects reuse it
instead of rebuilding it from scratch. For the *concepts* behind these
(why the copy loop has to run forward, how `$D018` double-buffering
works, etc.) see [`KNOWLEDGE.md`](../KNOWLEDGE.md) and
[`C64-REFERENCE.md`](../C64-REFERENCE.md) — this file is about the code
itself: what each piece does, its interface, and how to pull it into a
project.

Grouped by **reusable unit** (a dev-side tool and its target-side 6502
code stay together when they're two halves of one thing), not by which
machine each piece runs on. Everything here originated in the `cbm-joy`
side project and was verified end to end on real hardware there before
being archived — see each entry's provenance note.

## `lzss/` — byte-oriented LZSS compression for C64 assets

For assets like screen/color RAM dumps (~1000 bytes, heavy on repeated
runs): compresses character-graphics screens to roughly 15-35% of raw
size, near-solid color RAM to ~3%. Format and full technique writeup:
`KNOWLEDGE.md`'s "LZSS compression for C64 assets" section.

- **`lzss.py`** — dev-machine compressor (Python, no dependencies). Runs
  on your Mac, not the C64 — compression cost doesn't matter here.
  ```sh
  python3 lib/lzss/lzss.py input.bin                    # compress, report ratio, self-verify round-trip
  python3 lib/lzss/lzss.py input.bin --asm my_label      # also emit ca65 .byte lines, ready to embed
  ```
  Also usable as a library: `compress(data: bytes) -> bytes`,
  `decompress(comp: bytes) -> bytes`, `to_asm(data, label) -> str`.
- **`lzss.s`** — the 6502 decompressor. Hand-written asm, not C, because
  decompression speed is the actual performance path (compression only
  ever runs once, on the dev machine). Reuses cc65's own zero-page
  scratch pointers (`ptr1`-`ptr3` via `zeropage.inc`) rather than
  declaring new ones — see `CC65-TOOLCHAIN.md`'s zero-page section for
  why that's necessary, not optional. C interface (globals, not
  stack-passed args — deliberately sidesteps cc65's calling convention):
  ```c
  extern unsigned int lzss_src, lzss_dst;
  extern void lzss_decompress(void);
  lzss_src = (unsigned)compressed_data; lzss_dst = dest_address;
  lzss_decompress();
  ```
  Correctly handles overlapping matches (distance < length, e.g. a long
  run of one repeated byte) via a forward-order copy loop — the file's
  own header comment explains why a backward/`BPL`-countdown loop (the
  usual fast 6502 idiom) is wrong here specifically.

**To use in a new project**: copy both files in (`lzss.s` into your
`src/`, `lzss.py` into your `tools/`), assemble `lzss.s` alongside your
own `.s`/`.c` files, capture/author your asset, run `lzss.py --asm` on
it, `.include` the resulting `.s` file, and call `lzss_decompress()` per
the C interface above (or call it from asm directly, same global
convention).

**Provenance**: `cbm-joy`, first built to close the "design a screen
live on hardware, capture it" idea (see `KNOWLEDGE.md`'s "Contributing
back" history, `findings-1787187937.md`).

## `blit/` — fast fixed-1000-byte 6502 block copy

`fast_copy1000`: copies exactly 1000 bytes (a full screen or color RAM
page) from one buffer to another as fast as straight-line 6502 code
reasonably can — Y-register page-wraparound addressing, so only the
pointers' high bytes need incrementing (once per 256 bytes) rather than a
16-bit increment-with-carry on every byte. Not LZSS-specific — generic
for any known-1000-byte-size buffer-to-buffer move.

```c
extern unsigned int copy_src, copy_dst;
extern void fast_copy1000(void);
copy_src = ...; copy_dst = ...; fast_copy1000();
```

Same C-interface-via-globals convention as `lzss.s`, same zero-page
pointer reuse. Wrap the call in `SEI()`/`CLI()` (cc65's `<6502.h>`) if
you need its duration deterministic against the KERNAL's ~60Hz IRQ.

**Not (yet) generalized to other sizes** — 1000 is hardcoded (3 pages +
a 232-byte tail) because it's the one size that actually recurs (a C64
screen or color-RAM page). If a project needs a different fixed size,
the loop shape itself is simple to hand-adapt; see `KNOWLEDGE.md`'s "Fast
fixed-size 6502 block copy" section for the general technique rather
than building a parameterized-length variant speculatively.

**Provenance**: `cbm-joy`, built for the color-RAM blit half of its
screen-swap (see `blit.s`'s own header comment for why: decompressing
straight into live `$0400`/`$D800` tears, decompress off-screen then
blit fast instead).

## `sprite2asm/` — text-grid sprite authoring

**`sprite2asm.py`** — converts a hand-authored 24×21 `.`/`*` text grid
(the actual standard VIC-II sprite dimensions: 3 bytes/row × 21 rows =
63 bytes) into ca65 `.byte` lines for a monochrome sprite. `*` = lit
pixel, `.` = transparent.

```sh
python3 lib/sprite2asm/sprite2asm.py my_sprite.txt > my_sprite.s
```

Easy to eyeball, diff, and version-control sprite art as plain text
instead of hand-computing bit patterns. A same-shape "reversed" frame
(e.g. for a fire-button toggle) is just `tr '.*' '*.'` on the source
grid — no separate tooling needed. See `KNOWLEDGE.md`'s
"Sprite-authoring workflow" section for the full technique, including a
pointer to the 64-byte-alignment linker-config requirement for the
resulting sprite data (`KNOWLEDGE.md`'s "cc65 build configs" section).

**Provenance**: `cbm-joy` (`findings-1787181006.md`).

## `examples/`

- **`double_buffer_demo.c`** — the intended usage pattern for `lzss/` +
  `blit/` together: decompress two screen/color pairs off-screen, then
  swap between them tear-free via a single `$D018` write (screen) plus a
  `SEI`/`CLI`-wrapped blit (color, which has no hardware double-buffer —
  see `KNOWLEDGE.md`). **Template, not a drop-in program** — it declares
  `extern` placeholders for compressed asset data
  (`comp_screen_a`/`comp_color_a`/...) that your project supplies via
  `lzss.py --asm`, not artwork this library ships. Adapted from
  `cbm-joy/src/test_lzss.c`, where this pattern was first built and
  verified end to end on real hardware.
