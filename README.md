# cc65 → Ultimate64 wireless dev pipe

A minimal, direct pipeline for writing C/6502-asm code, compiling it with
[cc65](https://cc65.github.io/), and beaming the result over WiFi to a real
Ultimate64 for execution — no SD card shuffling, no cables.

For accumulated gotchas, reference facts, and patterns (cc65 build configs,
PETSCII/charset quirks, the IRQ-hooking pattern, WiFi streaming
limitations, ...) — including things not specific to any one example here
— see **[KNOWLEDGE.md](KNOWLEDGE.md)**. That file is meant to keep growing
and to be useful to future cc65/Ultimate64 projects, not just this repo.

## Toolchain

- **cc65** — `brew install cc65`. Provides `cl65`, `cc65`, `ca65`, `ld65`.
- **[`ru64`](https://github.com/mlund/ultimate64)** — `cargo install
  ultimate64` (needs a Rust toolchain). Talks to the Ultimate64's REST API
  over the network (`run`, `mount`, `peek`, `poke`, `reset`, ...).

Both are already set up on this machine — see KNOWLEDGE.md for the PATH
caveats that came up installing them.

## Layout

```
src/            C/asm sources
build/          build output (.prg etc), gitignored
tools/          helper scripts: screendump.py, select-u64.sh, u64-hosts.txt
Makefile        build + deploy targets
KNOWLEDGE.md    accumulated reference notes (see above)
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
make run ULTIMATE_HOST=192.168.1.64
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
different linker configs, and `src/irq_border.s` for an example.

## Known-good state

- `src/hello.c` — a `printf` smoke test — built, deployed, and run on real
  Ultimate64 hardware over WiFi; output confirmed via `make screen`.
- `src/irq_border.s` — plain 6502 asm, no C runtime. Prints a message, then
  hooks the KERNAL RAM IRQ vector to increment the border color on every
  IRQ (see KNOWLEDGE.md for the pattern). Deployed and confirmed on real
  hardware: polling `$d020` via `ru64 peek` after the program returns to
  `READY.` shows it incrementing on its own, proving the hook outlives the
  program that installed it.
- `ru64 reset` confirmed working remotely over WiFi.

Toolchain and network path are both verified working end to end for both
C and pure-assembly programs, against a real Ultimate64.
