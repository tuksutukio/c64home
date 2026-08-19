# cc65 → Ultimate64 wireless dev pipe

A minimal, direct pipeline for writing C/6502-asm/BASIC 2.0 code, compiling
or tokenizing it, and beaming the result over WiFi to a real Ultimate64 for
execution — no SD card shuffling, no cables.

This repo doubles as a reference base, meant to keep growing and to be
useful to future cc65/Ultimate64 projects, not just this one:

- **[KNOWLEDGE.md](KNOWLEDGE.md)** — gotchas/discoveries specific to
  building this pipeline (cc65 build configs, PETSCII/charset quirks, the
  IRQ-hooking pattern, WiFi streaming limitations, ...) and where future
  projects should write their own findings back — either directly, or by
  dropping a `findings-<unix-timestamp>.md` file here for later review
  (see KNOWLEDGE.md's "Contributing back" section).
- **[C64-REFERENCE.md](C64-REFERENCE.md)** — static C64 hardware facts:
  memory map, KERNAL routines, VIC-II/SID/CIA registers, BASIC V2 tokens,
  PETSCII/screen codes.
- **[6502-OPCODES.md](6502-OPCODES.md)** — full 6502/6510 instruction set,
  documented and undocumented/illegal opcodes.
- **[CC65-TOOLCHAIN.md](CC65-TOOLCHAIN.md)** — ca65 assembler directives
  and the cc65 C library (`conio.h`, `6502.h`, `c64.h`, ...) quick
  reference.

## Toolchain

- **cc65** — `brew install cc65`. Provides `cl65`, `cc65`, `ca65`, `ld65`.
- **[`ru64`](https://github.com/mlund/ultimate64)** — `cargo install
  ultimate64` (needs a Rust toolchain). Talks to the Ultimate64's REST API
  over the network (`run`, `mount`, `peek`, `poke`, `reset`, ...).
- **`petcat`** — ships with [VICE](https://vice-emu.sourceforge.io/); used
  to tokenize plain-text BASIC 2.0 listings into a runnable `.prg`. No cc65
  involvement needed for BASIC at all.

Both cc65/ru64 and VICE (for `petcat`) are already set up on this machine
— see KNOWLEDGE.md for the PATH caveats that came up installing them.

## Layout

```
src/                C/asm/BASIC sources
build/              build output (.prg etc), gitignored
tools/              helper scripts: screendump.py, select-u64.sh, u64-hosts.txt
Makefile            build + deploy targets
KNOWLEDGE.md        accumulated gotchas/discoveries (see above)
C64-REFERENCE.md    static C64 hardware reference (see above)
6502-OPCODES.md     static 6502/6510 opcode reference (see above)
CC65-TOOLCHAIN.md   ca65/cc65 syntax quick reference (see above)
```

## Picking which Ultimate64 to target

No IP is hardcoded anywhere committed to git — there are two physical
units on the LAN and either might be in use for a given session:

```sh
tools/select-u64.sh u64elite   # or: u64c   (see tools/u64-hosts.txt)
make host                      # show the currently selected device
```

The pick is saved to a gitignored `.ultimate_host` statefile and stays in
effect across shells/tabs until you switch again. `make run`/`info`/
`screen` all read it automatically and error out with instructions if
nothing's been selected yet. Override for a single invocation without
touching the saved pick:

```sh
make run ULTIMATE_HOST=192.168.1.164
```

## Usage

```sh
make                              # compile src/hello.c -> build/hello.prg
make run                          # build, then send + run it on the Ultimate64 over WiFi
make run PRG=build/irq_border.prg # build/run a different example (see src/)
make info                         # query the Ultimate64 (firmware/model), sanity check connectivity
make screen                       # read back the C64 text screen over WiFi (see KNOWLEDGE.md)
make clean
```

`PRG` picks which example to build/run; defaults to `build/hello.prg`. A
`src/%.c` pattern rule builds C sources (full C runtime, `c64.cfg`); a
`src/%.s` pattern rule builds pure-assembly sources instead (`c64-asm.cfg
-u __EXEHDR__`, no C runtime) — see KNOWLEDGE.md for why they need
different linker configs, and `src/irq_border.s` for an example. A
`src/%.bas` pattern rule tokenizes plain-text BASIC 2.0 listings via
`petcat -w2` — see `src/hello_basic.bas`.

**Naming convention**: give each language variant of the same program a
**distinct basename** (`foo.c`, `foo_asm.s`, `foo_bas.bas` — not all named
`foo.*`). If two source files sharing a stem could both produce
`build/foo.prg` (e.g. `src/foo.c` and `src/foo.bas` both present), which
pattern rule wins is ambiguous/unpredictable — `make` doesn't arbitrate
that for you. This repo's own examples (`hello.c`, `hello_basic.bas`,
`irq_border.s`) happen to avoid the collision by luck (all different
stems already), so it isn't obvious from the reference examples alone —
worth being deliberate about if you ever want a C/asm/BASIC comparison of
the *same* program, which is a natural thing to want from this pipeline.

## Known-good state

- `src/hello.c` — a `printf` smoke test — built, deployed, and run on real
  Ultimate64 hardware over WiFi; output confirmed via `make screen`.
- `src/irq_border.s` — plain 6502 asm, no C runtime. Prints a message, then
  hooks the KERNAL RAM IRQ vector to increment the border color on every
  IRQ (see KNOWLEDGE.md for the pattern). Deployed and confirmed on real
  hardware: polling `$d020` via `ru64 peek` after the program returns to
  `READY.` shows it incrementing on its own, proving the hook outlives the
  program that installed it.
- `src/hello_basic.bas` — plain BASIC 2.0 listing, no compiler involved at
  all. `petcat -w2` tokenizes it straight to a `.prg`; deployed and
  confirmed on real hardware (a `FOR`/`NEXT` loop ran and printed 1-5
  correctly).
- `ru64 reset` confirmed working remotely over WiFi.
- Both physical units (`u64elite` at `192.168.1.165`, an Ultimate64 Elite
  II; `u64c` at `192.168.1.164`, a plain Ultimate 64) verified working
  end to end independently.

Toolchain and network path are both verified working end to end for C,
pure-assembly, and BASIC 2.0 programs, against real Ultimate64 hardware.

## Next up

- [ ] Test `.d64` disk image mounting (`ru64 mount`) — not tried yet, only
  `.prg` DMA-load/run so far.
