# c64home — C64/Ultimate64 wireless dev pipe

A minimal, direct pipeline for writing C/6502-asm/BASIC 2.0 code, compiling
or tokenizing it, and beaming the result over WiFi to a real Ultimate64 for
execution — no SD card shuffling, no cables.

This repo doubles as a reference base, meant to keep growing and to be
useful to future C64/Ultimate64 projects, not just this one:

- **[KNOWLEDGE.md](KNOWLEDGE.md)** — gotchas/discoveries specific to
  building this pipeline (cc65 build configs, PETSCII/charset quirks, the
  IRQ-hooking pattern, WiFi streaming limitations, ...).
- **[C64-REFERENCE.md](C64-REFERENCE.md)** — static C64 hardware facts:
  memory map, KERNAL routines, VIC-II/SID/CIA registers, BASIC V2 tokens,
  PETSCII/screen codes.
- **[6502-OPCODES.md](6502-OPCODES.md)** — full 6502/6510 instruction set,
  documented and undocumented/illegal opcodes.
- **[CC65-TOOLCHAIN.md](CC65-TOOLCHAIN.md)** — ca65 assembler directives
  and the cc65 C library (`conio.h`, `6502.h`, `c64.h`, ...) quick
  reference.
- **[lib/](lib/README.md)** — reusable *code*, not just write-ups (LZSS
  compression + 6502 decompressor, a fast block-copy routine, sprite
  text-grid authoring, a double-buffering usage example) for projects to
  actually pull in, not just read about.
- **[../c64doc](../c64doc/CLAUDE.md)**: separate repo, Antti's offline
  library of ~250 Commodore books/manuals/service docs (Programmer's
  Reference Guides, Mapping the 64, KERNAL/ROM disassemblies, 1541/DOS
  internals, Ultimate docs, schematics) with full-text search. Use it to
  verify or go beyond what's in the files above. Cite sources as
  `<doc-id> p.<PDF page>`. Only the catalog is in git, so on a machine
  without the offline copy you can see what exists but can't search it.

## Ground rules for sibling/sub-projects

If you're a Claude session working in a *different* project and were
pointed at this directory for general ground rules, read this first.

**This repo is the single source of truth for the shared C64/Ultimate64
toolchain, hardware reference, conventions, and reusable code — sibling
projects should treat it as read-only.** Don't edit `README.md`,
`KNOWLEDGE.md`, `C64-REFERENCE.md`, `6502-OPCODES.md`,
`CC65-TOOLCHAIN.md`, `tools/`, `lib/`, or anything else defined in this
repo directly, even if you're confident about a fix or addition —
including from a session physically capable of doing so. (Copying
`lib/`'s code *into your own project* to use it is exactly the point,
of course — "read-only" means don't edit the copies living here, not
"don't use them.") Housekeeping here is owned by whichever Claude session
is working *in this repo itself*; everywhere else contributes through one
channel only:

**Write raw, unfiltered findings to a new `findings-<unix-timestamp>.md`
file in this repo's root** (e.g. `findings-1787187937.md` — `date +%s`
for the timestamp). Include source project name, context, and ideally a
rough steer on where each finding likely belongs and how confident/
reusable it seems — the actual review, sanitizing, and merge decision
happens on this repo's side, that context just saves it some triage. See
KNOWLEDGE.md's "Contributing back" → "Mechanism" section for the full
convention (staging only, not an archive — the file gets deleted once
its contents are reviewed and absorbed, merged or deliberately
discarded).

Device selection (`tools/select-u64.sh`, `tools/u64-hosts.txt`) works the
same way: reference it by path from a sibling project's own Makefile
rather than copying it — see KNOWLEDGE.md's "Using this from another
project" section.

**Be proactive about flagging reusable code, not just bugs/gotchas.** If
something you built looks generic enough that a different project would
plausibly want it too — not just "here's a fact we learned," but "here's
a working piece of code" — say so explicitly in your findings report,
with a pointer to the file(s), even without being asked. That's exactly
what `lib/` (see above) is for, and it's expected to keep growing this
way. You don't need to judge whether it's *definitely* reusable enough
first — flag it and let the review on this side make that call, same as
any other finding.

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
lib/                reusable code for projects to pull in (see above)
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
- [ ] **Before anything here is aimed at the general public, review the
  practices adopted during this casual/personal-exploration phase** —
  they were fine for one person's own machine but weren't designed with
  outside users in mind. Known candidates worth a look when that day
  comes (not exhaustive, just what's obviously personal-machine-shaped
  right now): hardcoded absolute paths (`VICE-GTK3-3.9` version pin,
  `$HOME/.cargo/bin` assumptions) baked into the Makefile/tools rather
  than discovered/configured; `tools/u64-hosts.txt` holding this
  specific home network's device names/IPs; no LICENSE file; the
  `findings-<unix-timestamp>.md` contribution mechanism was explicitly
  designed for one person relaying between their own sessions, not
  multiple external contributors, and would need rethinking.
- [x] ~~Design whole character-graphics screens live on the actual
  hardware, read back over WiFi, compress for redisplay.~~ **Done** —
  built and verified end to end by `cbm-joy`: screen hand-drawn on
  `u64elite`'s keyboard, peeked back, compressed (byte-oriented LZSS),
  embedded in a build, decompressed and redisplayed, verified
  byte-for-byte via peek. See KNOWLEDGE.md's LZSS and VIC-II
  double-buffering sections.
- [ ] Make `petcat`/`ru64` easier to reach for future projects built on
  this pipeline. Both currently only end up on `PATH` via `~/.zshrc`-sourced
  shell config, or the `export PATH := ...` + trailing-`;`-per-recipe
  Makefile trick (see KNOWLEDGE.md's PATH section) — non-interactive
  shells and bare `make` don't pick either up automatically. Worth
  fixing for discoverability since `petcat`'s real purpose is general
  PETSCII/ASCII text interop, not just this repo's BASIC-listing use of
  it so far. No fix decided yet (a wrapper script? documenting the PATH
  requirement more prominently up front? something else?) — flagging to
  think about, not acting on yet.
- [x] ~~Archive reusable 6502/tooling code, not just its write-up.~~
  **Done** — see [`lib/`](lib/README.md): LZSS compression + 6502
  decompressor, fast fixed-1000-byte block copy, sprite text-grid
  authoring, and a double-buffering usage example, all copied in from
  `cbm-joy` and verified to still assemble/run correctly from their new
  location. Turned out no generalization pass was needed first — the
  code was already parameterized via C-facing globals for addresses, and
  the "hardcoded" bits (blit's 1000-byte size, sprite2asm's 24×21
  dimensions) are real, meaningful constants (a C64 screen/color-RAM
  page; the actual VIC-II sprite size), not cbm-joy-specific values that
  needed generalizing.
