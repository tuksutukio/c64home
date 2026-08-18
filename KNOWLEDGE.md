# cc65 / Ultimate64 knowledge base

Accumulated facts, gotchas, and patterns from doing real 6502 dev against a
physical Ultimate64 over WiFi. Meant to outlive any single example in this
repo — durable reference for future cc65/Ultimate64 projects, not just this
one. Add to it whenever something non-obvious gets discovered again.

For static hardware facts (memory map, KERNAL routines, register layouts,
BASIC tokens, PETSCII/screen codes) rather than things we discovered the
hard way, see **[C64-REFERENCE.md](C64-REFERENCE.md)**. For the 6502/6510
instruction set (documented + undocumented), see
**[6502-OPCODES.md](6502-OPCODES.md)**. For ca65/cc65 syntax (assembler
directives, C library functions), see
**[CC65-TOOLCHAIN.md](CC65-TOOLCHAIN.md)**.

## Contributing back from other projects

If a future project elsewhere on this machine hits a cc65/ca65/ru64/
Ultimate64/C64 quirk and works out the fix, write it back here — this repo
is meant to accumulate that, not just be read from. But be selective:
only append findings that are genuinely **reusable and non-obvious** (would
save real time for a *different* project hitting the same thing), not
every one-off specific to that project's own file layout or bug. Merge
into the relevant existing section rather than appending to the end, and
check whether something similar is already documented before adding a new
entry — the goal is fast orientation for a new session, which an
indiscriminate log of every side-step would defeat. If a section ever
gets genuinely unwieldy, that's the signal to split it into its own file
(the way C64-REFERENCE.md already got split out) — not something to
pre-empt before it actually happens.

## Research process notes (writing/extending the reference docs)

**WebFetch's page-summarization can silently drop or invert table rows on
large reference pages — treat a surprising result as a signal to
double-check, not as fact.** Bit us twice building
C64-REFERENCE.md/6502-OPCODES.md: (1) a summarized fetch of the
devili.iki.fi PRG transcription reported `SETLFS`'s `A`/`X` registers
swapped from the well-established convention — resolved by fetching the
raw page text directly (bypassing summarization) and cross-checking
against sta.c64.org, which confirmed the summarizer's page had a genuine
OCR/transcription error, not us; (2) a summarized fetch of oxyron.de's
undocumented-opcode page claimed the single-byte NOPs
(`$1A`/`$3A`/`$5A`/`$7A`/`$DA`/`$FA`) don't exist — flatly wrong, caught
because it contradicted well-known 6502 lore, confirmed via a follow-up
search. Both times the fix was the same: when a fetched fact contradicts
strong prior knowledge or "smells" surprising, re-fetch raw / cross-check
a second independent source before trusting it, rather than propagating
it into a reference doc other sessions will act on.

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
- **`ru64`/`petcat` PATH additions live in `~/.zshrc`, which zsh only
  sources for *interactive* shells — but `cl65`/`ca65`/`ld65` are
  unaffected by this**, and the distinction matters enough to get right:
  - `cl65` comes from Homebrew, which registers `/opt/homebrew/bin`
    system-wide via `/etc/paths.d/homebrew`. That gets picked up by
    macOS's `path_helper`, invoked from `/etc/zprofile` — which zsh
    sources for **login** shells, interactive or not. So `cl65` survives
    in any login shell (a plain `zsh -lc '...'`, and many
    script/CI/agent-harness invocation styles are login shells even
    though non-interactive).
  - `ru64` (`~/.cargo/bin`) and `petcat` (VICE app bundle path) are added
    **only** in `~/.zshrc`, which requires **interactive** regardless of
    login status — so they go missing in *any* non-interactive shell, a
    much more commonly-hit gap than the `cl65` case. Confirmed
    independently by a downstream project attempting to drive this
    pipeline non-interactively (initially over-generalized to "cl65 too,"
    which direct testing here didn't bear out — corrected).
  - A shell that's **neither** login **nor** interactive (e.g. a bare
    `zsh -c '...'` with no inherited environment) loses everything,
    `cl65` included — worth knowing this case exists even though it's
    rarer than the interactive-only gap above.

  Either source `~/.zshrc` explicitly first, or use absolute paths
  (`~/.cargo/bin/ru64`, `/Applications/VICE-GTK3-<version>/bin/petcat`) —
  `cl65` typically doesn't need this treatment, but doesn't hurt to be
  explicit if the invocation context is unknown.

  **A step deeper, and worth flagging prominently — a Makefile's own
  `export PATH := ...` can silently fail to fix this on macOS's stock
  GNU Make.** macOS ships GNU Make **3.81**. For a recipe line containing
  **no shell metacharacters** (no `;`, `|`, `&&`, ...) — e.g. a plain
  `cl65 -t c64 -o build/foo.prg src/foo.c` — Make 3.81 skips spawning a
  shell entirely and `execve()`s the command directly, doing its own
  `PATH` search that does **not** see a same-Makefile `export PATH :=
  ...` reassignment. `make -p` will confirm the variable is correctly set
  internally, which makes this look fixed when it isn't — the tell is
  `cl65: No such file or directory` despite that. `.ONESHELL:` does not
  help here either; it only exists from GNU Make 3.82 onward and is a
  silent no-op on 3.81. **Fix**: end every recipe line that depends on the
  exported `PATH` with a trailing `;` (or any shell metacharacter) to
  force Make to route it through a real shell instead of `execve`-ing it
  directly. Confirmed by a downstream project (reproduced in isolation
  with a minimal test Makefile, then verified full pipeline — all three
  language builds, `make host`, a live `make info` round-trip to real
  hardware — works from a fully stripped `env -i HOME=$HOME
  PATH=/usr/bin:/bin make ...` with nothing pre-sourced) and independently
  reproduced here the same way before this repo's own `Makefile` was
  updated to apply it (`export PATH := ...` at the top, trailing `;` on
  every `cl65`/`ru64`/`petcat`-invoking recipe line).
- **`petcat`** (BASIC tokenizer, for `.bas` → `.prg`): ships with
  [VICE](https://vice-emu.sourceforge.io/), not a separate package. On
  this machine it's a GUI app bundle, not a Homebrew install:
  `/Applications/VICE-GTK3-<version>/bin/petcat`. Tokenize a plain-text
  BASIC 2.0 listing with `petcat -w2 -o out.prg -- in.bas` (`-w2` = target
  BASIC v2 keywords, i.e. stock C64 BASIC). No cc65/compiler involvement
  needed for BASIC at all — write the listing as normal text (line
  numbers included), petcat handles tokenizing *and* the
  lowercase-source→uppercase-screen PETSCII conversion automatically, same
  convention as cc65's `-t c64` (see charset section below).

  **There is more than one `petcat` on this machine — use the VICE.app one
  above, not `~/cbm/bin/petcat`** (a stale, unrelated x86_64 binary
  leftover from an old 2021 setup; ignore/avoid it, not needed for
  anything here).

  Both copies are `com.apple.quarantine`-flagged (downloaded via Chrome
  at some point). **Any** quarantined executable — script or binary, this
  isn't specific to Mach-O binaries — triggers Gatekeeper's "cannot be
  opened, verify developer" dialog on its first execution ever; confirmed
  first-hand, this fired even for the VICE.app shell-script wrapper the
  first time it ran in this session. Once approved (clicking through the
  dialog, or via System Settings > Privacy & Security), macOS remembers
  that per-file and stays quiet on subsequent runs — the `xattr` flag can
  remain present even after approval, so its mere presence isn't a
  reliable signal of whether you'll be prompted again. To pre-empt the
  prompt entirely (e.g. before a first run in a fresh session/script
  context where no one's around to click through it):
  ```
  sudo xattr -d com.apple.quarantine /Applications/VICE-GTK3-<version>/bin/petcat
  ```
  (needs `sudo` — it's inside `/Applications`).

  **In a non-interactive context, the same root cause shows up differently
  and more confusingly**: a downstream project ran the quarantined
  `~/cbm/bin/petcat` (unsigned x86_64) non-interactively and got a silent
  `SIGKILL` (exit 137) with **no error message at all** — easy to
  misdiagnose as a Rosetta/architecture problem instead of Gatekeeper (that
  was the first, wrong guess). Same `xattr -d com.apple.quarantine` fix
  applies. Important nuance confirmed in that investigation: **the
  quarantine flag specifically is what triggers this, not merely being
  unsigned** — `~/.cargo/bin/ru64` (from `cargo install`) is also unsigned
  (`codesign -dv` reports "not signed at all" for it too, and `spctl -a
  -vv` reports it "rejected") but carries no quarantine xattr and runs
  fine. `spctl` reporting "rejected" alone is not, by itself, a sign
  something will fail to execute — only `com.apple.quarantine` being
  present is.

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

### Interactive testing over WiFi *is* possible — don't over-read the streaming limitation above

The video/audio streaming restriction above is specifically about the VIC
UDP stream (`ru64 screenshot`) — it does **not** mean WiFi is read-only or
non-interactive. `ru64 <host> type "<text>"` ("Emulate keyboard input")
emulates keystrokes — Unicode input, converted to PETSCII, typed into
whatever's running — and works fine over WiFi. Combined with the
screen-RAM `peek` readback above, this makes real interactive
testing possible end to end over WiFi: type a response into a running
program's input prompt, then peek screen RAM to confirm what it did with
it. Confirmed by a downstream project (typed a numeric answer into a
running program, read the result back via screen-RAM peek).

Usage note: send Enter as a literal `\n`, not `\r` — e.g.
`ru64 <host> type $'\n'` in bash. `\r` was tested and did not reliably
trigger the same behavior.

**Narrower gotcha, low recurrence**: if the receiving program reads input
via a raw KERNAL `CHRIN` loop in pure assembly (as opposed to BASIC's
`INPUT` or cc65 C's `stdio`/`fgets`, both confirmed correct), a `type`-sent
Enter doesn't reliably advance the screen editor's cursor to a fresh row
the way physically pressing Enter does — purely cosmetic (all actual input
parsing/output logic was unaffected in testing), but the first output line
after the prompt can land appended to the same row instead of a new one.
Root cause not diagnosed further since it's cosmetic and narrow (pure-asm
+ raw `CHRIN` + `ru64 type` specifically). Workaround: after your `CHRIN`
loop detects the CR (`13`), explicitly `lda #13 / jsr CHROUT` yourself
before printing anything else, rather than relying on the input path to
have already produced a newline.

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

### Using this from another project

This repo (`~/src/cc65`) is meant to stay the single source of truth for
the device list — new project directories elsewhere under `~/src/` should
reference `~/src/cc65/tools/select-u64.sh` and `tools/u64-hosts.txt` by
path rather than copying them, so there's one place to add a device or fix
a bug. Each project's own `Makefile`/build layout will naturally be
project-specific regardless, and can still read whatever `.ultimate_host`
statefile it wants (own copy, or point at this repo's) — the two aren't
coupled. If a project ever needs the selector itself to behave
differently, fork a local copy then; these are small scripts, so that's a
cheap, reversible decision to defer rather than commit to upfront.
