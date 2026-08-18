# cc65 → Ultimate64 wireless dev pipe

A minimal, direct pipeline for writing C/6502-asm code, compiling it with
[cc65](https://cc65.github.io/), and beaming the result over WiFi to a real
[Ultimate64 Elite II](https://ultimate64.com/) for execution — no SD card
shuffling, no cables.

## Toolchain

- **cc65** — 6502 cross C compiler/assembler/linker suite. Installed via
  Homebrew: `brew install cc65`. Provides `cl65` (the all-in-one driver used
  here), `cc65`, `ca65`, `ld65`.
- **[`ru64`](https://github.com/mlund/ultimate64)** — Rust CLI that talks to
  the Ultimate64's REST API over the network (`run`, `mount`, `peek`,
  `poke`, `reset`, ...). Installed via `cargo install ultimate64`. Requires
  a Rust toolchain (`rustup`, installed via `brew install rustup` +
  `rustup toolchain install stable` — Homebrew's `rustup` formula is
  keg-only, so `/opt/homebrew/opt/rustup/bin` must be on `PATH`).

Both are already set up on this machine. `ru64` lands in `~/.cargo/bin`.

## Layout

```
src/            C/asm sources
build/          build output (.prg etc), gitignored
tools/          helper scripts (screendump.py, see below)
Makefile        build + deploy targets
```

## Usage

```sh
make                              # compile src/hello.c -> build/hello.prg
make run                          # build, then send + run it on the Ultimate64 over WiFi
make run PRG=build/irq_border.prg # build/run a different example (see src/)
make info                         # query the Ultimate64 (firmware/model), sanity check connectivity
make screen                       # read back the C64 text screen over WiFi (see below)
make clean
```

The target device defaults to `ULTIMATE_HOST` in the `Makefile`. Override
per-invocation or via env var:

```sh
make run ULTIMATE_HOST=192.168.1.165
```

`PRG` picks which example to build/run; it defaults to `build/hello.prg`. A
`src/%.c` pattern rule builds C sources with the default `c64.cfg` (full C
runtime, entry point `_main`); a `src/%.s` pattern rule builds pure-assembly
sources with `c64-asm.cfg -u __EXEHDR__` instead (BASIC "SYS" header, no C
runtime, entry point is just the start of the `CODE` segment) — see
`src/irq_border.s` for an example and why plain-asm needs a different
config than C.

**Gotcha:** with `-t c64`, cc65's charset translation maps *lowercase*
source letters to the PETSCII codes that render as uppercase on screen (the
normal C64 convention) — uppercase source letters map to the shifted
graphics range instead. Write string literals in lowercase.

## Closing the debugging loop over WiFi

The Ultimate64 firmware explicitly **disallows video/audio streaming over
WiFi** — only over the Ethernet LAN port (documented in the official
[WiFi how-to](https://1541u-documentation.readthedocs.io/en/latest/howto/wifi.html)).
That means `ru64 screenshot` does not work on a WiFi-only setup like this
one — the underlying VIC stream is unicast/multicast UDP video and is
blocked at the firmware level for WiFi.

Instead, `tools/screendump.py` reads the C64's text screen RAM
(`$0400`–`$07E7`) directly over the same unicast REST connection `ru64 run`
already uses (`ru64 peek`), decodes the screen-code bytes to ASCII, and
prints non-blank rows. This works over WiFi and is enough to verify a
program's text output without needing a cable. Wired to `make screen`.

## Known-good state

- `src/hello.c` — a `printf` smoke test — built, deployed, and run on real
  Ultimate64 hardware over WiFi; output confirmed via `make screen`.
- `src/irq_border.s` — plain 6502 asm, no C runtime. Prints a message, then
  hooks the KERNAL RAM IRQ vector (`$0314`/`$0315`) with a handler that does
  `inc $d020` (border color) and chains to the stock KERNAL IRQ continuation
  (`$ea31`) so keyboard scanning/jiffy clock/cursor blink keep working.
  Deployed and confirmed on real hardware: polling `$d020` via `ru64 peek`
  after the program returns to `READY.` shows it incrementing on its own,
  proving the hook outlives the program that installed it.

Toolchain and network path are both verified working end to end for both
C and pure-assembly programs.
