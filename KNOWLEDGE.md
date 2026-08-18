# cc65 / Ultimate64 knowledge base

Accumulated facts, gotchas, and patterns from doing real 6502 dev against a
physical Ultimate64 over WiFi. Meant to outlive any single example in this
repo — durable reference for future cc65/Ultimate64 projects, not just this
one. Add to it whenever something non-obvious gets discovered again.

## Toolchain

- **cc65**: `brew install cc65`. Gives `cl65` (driver), `cc65`, `ca65`,
  `ld65`.
- **[`ru64`](https://github.com/mlund/ultimate64)**: Rust CLI wrapping the
  Ultimate64 REST API. `cargo install ultimate64` (binary is named `ru64`,
  not `ultimate64`). Needs a Rust toolchain.
- Homebrew's `rustup` formula is keg-only and does **not** provide
  `rustup-init` — use `rustup toolchain install stable` directly. Neither
  `/opt/homebrew/opt/rustup/bin` nor `~/.cargo/bin` are on `PATH` by
  default via this install path; both need adding to shell rc manually
  (no `~/.cargo/env` gets created the way official rustup-init would do
  it).

## Ultimate64 network control

- The underlying mechanism is officially called the **Ultimate Command
  Interface (UCI)** — a raw TCP protocol on port 64, also mapped onto an
  HTTP REST API (`/v1/...`). Docs:
  https://1541u-documentation.readthedocs.io/en/latest/
- `ru64 <host> run foo.prg` — DMA-loads and autostarts a .prg. Works over
  WiFi (plain unicast HTTP).
- `ru64 <host> peek <addr> -n <len> [-o file]` — reads memory over the same
  unicast REST path. Works over WiFi. This is the main debugging primitive
  available on a WiFi-only setup (see below).
- `ru64 <host> reset` — remote reset, confirmed working over WiFi.

### Video/audio streaming is Ethernet-only — screenshot doesn't work over WiFi

Official docs state plainly: **"WiFi cannot be used for streaming video and
audio. This is only available on the LAN port."**
(https://1541u-documentation.readthedocs.io/en/latest/howto/wifi.html)

This is a firmware-level restriction, not a bug in any client tool.
Consequences:
- `ru64 screenshot` will fail on a WiFi-only Ultimate64 no matter what —
  it depends on the VIC UDP video stream.
- The REST endpoint that would start that stream
  (`PUT /v1/streams/video:start?ip=...`) itself returns
  `500 {"errors":["No Operational Network Interface"]}` over WiFi.
- The released `ultimate64` crate (0.5.5, as of 2026-08) doesn't even
  expose a `stream` subcommand — that only exists on the unreleased `main`
  branch on GitHub, and it wouldn't help here anyway since the limitation
  is at the firmware/hardware level, not the client.

**Workaround**: read C64 **screen RAM** directly via `ru64 peek` instead of
video streaming. `tools/screendump.py` peeks `$0400`, 1000 bytes, and
decodes screen codes to ASCII:
- `0` → `@`
- `1..26` → `A`..`Z` (screen codes 1-26 render as uppercase letters in
  *either* charset mode, see below)
- `32..63` → same byte value as ASCII (space through `?`, digits and most
  punctuation are shared between screen code and ASCII/PETSCII in this
  range)
- anything else → not decoded (falls in the graphics/lowercase range,
  charset-mode dependent)

This is good enough to verify a program's text output end-to-end over
WiFi without ever needing a cable.

## cc65 build configs: C runtime vs pure assembly

`cl65 -t c64` picks a *character set translation* (see below) but the
**linker config** is what determines whether the C runtime is involved:

- **`c64.cfg`** (default) — expects `crt0.o` (the C startup code) to be
  linked in. Program entry point is a symbol named `_main` (C name
  mangling convention: `.export _main` in asm, or an actual C `main()`).
  `crt0.s`'s `init` routine does setup work including disabling BASIC ROM
  during execution and re-enabling it on exit, then eventually
  `jmp _main` (via `callmain`). Use this for anything with a `.c` file, or
  pure-asm code that's fine depending on the C runtime.
- **`c64-asm.cfg`** — for pure assembly with **no** C runtime. No `_main`
  needed; program entry is just the start of the `CODE` segment. Doesn't
  disable BASIC ROM, doesn't touch the charset. Needs
  `-u __EXEHDR__` added to get a small BASIC "`SYS`" header prepended so
  the .prg can be DMA-loaded/autostarted the same way a C-linked binary
  can; without `-u __EXEHDR__` the file has no BASIC stub and won't
  autorun via `RUN`/DMA-load autostart.

  Official cc65 doc reference:
  ```
  cl65 -o file.prg -u __EXEHDR__ -t c64 -C c64-asm.cfg source.s
  ```

Trying to build a pure-asm `.s` file against the *default* `c64.cfg`
produces linker errors like `Segment 'STARTUP' does not exist` and
`Start address of memory area 'BSS' is not constant` — that's the tell
that crt0 isn't linked in and you need `c64-asm.cfg` instead.

## PETSCII / charset gotchas

- **Case-swap on `-t c64`**: cc65's character-set translation for the c64
  target maps *lowercase* letters in ca65/C source to the PETSCII codes
  that render as **uppercase** on screen (the normal C64 convention).
  Uppercase letters in source map to the **shifted/graphics** range
  instead, which renders as garbage/graphic glyphs, not the intended
  letters. **Write string literals in lowercase** for normal-looking
  uppercase C64 text output.
- **Charset *mode* (upper/graphics vs upper/lowercase) differs between C
  and pure-asm builds**: `crt0.s`'s `init` sends PETSCII control code
  `14` ("switch to lowercase charset") via `BSOUT` before calling
  `_main`. A pure-asm program built against `c64-asm.cfg` skips crt0
  entirely, so it never sends that code and the machine stays in its
  post-reset default (uppercase + graphics) charset. This only affects
  the `$40`-`$5F` screen-code range (graphics vs. lowercase glyphs) — it
  does *not* affect how letters (screen codes 1-26) render, since those
  render as uppercase in either mode.

## IRQ hooking pattern (well-behaved, chains to KERNAL)

To hook the hardware IRQ without breaking keyboard scanning / jiffy clock
/ cursor blink, install on the **RAM vector** the KERNAL jumps through
(`$0314`/`$0315`, "CINV"), not the hardware vector (`$FFFE`/`$FFFF`):

```asm
sei
lda #<my_handler
sta $0314
lda #>my_handler
sta $0315
cli

my_handler:
    inc $d020      ; do your thing -- INC on a memory address touches no
                    ; registers, so no save/restore is needed here
    jmp $ea31       ; chain to the stock KERNAL IRQ continuation, which
                     ; itself pulls A/X/Y (pushed by the KERNAL's $FF48
                     ; entry stub before it JMP'd through $0314) and does
                     ; the final RTI
```

Why this specific shape works:
- `$FF48` (hardware vector target in KERNAL ROM) pushes A/X/Y, then does
  `JMP ($0314)` — a *jump*, not a call, so whatever's at `$0314`/`$0315`
  is responsible for eventually restoring registers and executing `RTI`.
- `$EA31` is the KERNAL's stock continuation: services the CIA1 timer
  IRQ, updates the jiffy clock, scans the keyboard, updates cursor blink,
  then pulls A/X/Y and does `RTI`.
- Because `INC` on an absolute memory address doesn't touch A/X/Y (and
  the flags it does touch don't matter — the real status flags get
  restored from the stack at the final `RTI`, not from whatever's live
  when you `jmp $ea31`), a one-instruction hook body is enough.
- JiffyDOS (this machine's installed ROM replacement, confirmed via boot
  banner: "JIFFYDOS V6.01") preserves standard KERNAL entry points
  including `$ea31` for compatibility, so this works unmodified.

Verification technique used: after deploying and letting the program
return to `READY.`, poll `$d020` a few times a second via `ru64 peek` —
watching the value change on its own (with no program actively running)
proves the hook is live and outlives the program that installed it.

## Host selection convention (this repo)

No Ultimate64 IP is hardcoded anywhere committed to git — there are two
physical units on this LAN and which one is "current" is picked
per-session, not fixed. See `tools/u64-hosts.txt` (name → IP map),
`tools/select-u64.sh <name>` (writes the pick to the gitignored
`.ultimate_host` statefile), and the Makefile's `check-host`/`host`
targets. `ULTIMATE_HOST=<ip>` on the command line overrides for one
invocation without touching the saved selection.
