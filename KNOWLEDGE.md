# c64home knowledge base

Accumulated facts, gotchas, and patterns from doing real 6502 dev against a
physical Ultimate64 over WiFi. Meant to outlive any single example in this
repo — durable reference for future C64/Ultimate64 projects, not just this
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

### Mechanism: `findings-<unix-timestamp>.md`

Stop-gap, manual, and deliberately low-infrastructure — a way to collect
useful experience without building actual process for a personal-scale
setup. If you're working in a sibling project and want to hand findings
back: write them, raw and unfiltered, to a new file in *this* repo's root
named `findings-<unix-timestamp>.md` (e.g. `findings-1787181006.md`),
one file per drop. Include enough context to be useful standalone (source
project name, what you were building, and ideally a rough steer on where
each finding likely belongs — KNOWLEDGE.md vs. C64-REFERENCE.md vs.
6502-OPCODES.md vs. CC65-TOOLCHAIN.md vs. `lib/`, and how
confident/reusable each one seems) — the actual review and merge
decision still happens on the receiving end, this just saves that
session some triage.

**This includes proactively flagging actual reusable code, not just
facts/gotchas** — a working routine or tool, not just a write-up about
one (see `lib/`'s own README for what's landed there so far, and why:
real effort that took real debugging isn't worth regenerating from
scratch for every spin-off). Point at the file(s) in your own project
rather than pasting the code inline; whoever reviews the finding reads
it directly from there.

**What not to send**, to save both sides the triage:
- Anything already in KNOWLEDGE.md, C64-REFERENCE.md, the other reference
  files or `lib/`. Grep them first. If something's there but wrong, or only
  web-sourced and you found a c64doc source, that's worth sending.
- Pure confirmations ("the Makefile pattern still works", "source X had
  what I needed"). Report only what broke or was missing.
- Code from trial/throwaway projects (e.g. `france`, a c64doc test) as a
  `lib/` candidate. Flag code from real projects; Antti decides which
  projects are trials.
- Findings about c64doc's lookup workflow do belong here (c64home relays
  them to `../c64doc/CLAUDE.md`).

Whoever's next doing housekeeping on this repo (told explicitly to check
— there's no automated trigger, by design, see the discussion this
convention came out of) reads any `findings-*.md` present, sanitizes and
merges what's genuinely reusable per the guidance above, and **deletes
the file once its contents have been absorbed** (merged or deliberately
discarded) — it's a staging area, not an archive; nothing should
accumulate here long-term. The timestamp exists so multiple drops don't
collide and so provenance/ordering is obvious at a glance, not for any
deeper reason.

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

  **`petcat` is also useful the other direction — decoding a screen-RAM
  dump into readable text**, not just tokenizing/detokenizing BASIC:
  `petcat -text -2 -nc` renders a **screen-code** dump as text, but only
  after converting screen codes to PETSCII first, using the table in
  C64-REFERENCE.md's "PETSCII vs. screen codes" section (feeding raw
  screen-RAM bytes to petcat directly produces garbage — it expects
  PETSCII, not screen codes). Practical recipe: mask off the
  reverse-video bit (bit 7 — same glyph, just inverted color) before
  conversion; the unambiguous screen-code range (`$00`-`$3F`, covering
  letters/digits/space/punctuation) converts exactly via the documented
  table; the ambiguous range (`$40`+, graphics-vs-lowercase depending on
  which charset ROM image is active, unknowable from the dump alone) is
  safe to placeholder out for a "does this scene contain readable text"
  check, since real letters/words only ever show up in the unambiguous
  range anyway. This is how a message typed into a mostly-graphical test
  scene got found and read back after the fact, over WiFi, with no video
  streaming involved. (Downstream: `cbm-joy`.)

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
- `ru64 <host> reset` — remote reset, confirmed working over WiFi. Also the
  quickest way to silence a looping SID program.
- `ru64 --help` lists more (`reboot`, `poweroff`, `pause`/`resume`, `play`
  for SID/MOD files, …). They're known and deliberately not documented here
  until a project actually needs one; no need to report them as findings.

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

### `peek` is not ground truth for live/volatile hardware state

The screen-RAM workaround above is reliable because screen RAM is
*settled* data by the time you peek it (the program already finished
writing it). That reliability does **not** extend to peeking a
live-changing hardware register (e.g. CIA1 `$DC00`, joystick/keyboard
input) to diagnose timing-sensitive behavior — an external REST `peek` is
asynchronous relative to the running 6502 and isn't guaranteed to reflect
what the 6502's own `LDA` sees moment-to-moment. A downstream project
(`cbm-joy`) chased an apparently-flickering joystick-port-2 fire reading
this way and it was a dead end. **The fix wasn't more peeking**: have the
*running program itself* snapshot the volatile byte into a fixed screen
cell every frame — that write is now settled data by the time anything
peeks it, same as any other screen-RAM read. Doing that revealed the
real cause: the joystick's own autofire circuit was genuinely pulsing the
switch on/off while held — not a code or CIA-register-sharing bug at all.
General lesson: to observe live hardware state reliably over this WiFi
pipeline, have the C64 program record it into RAM first; don't peek the
volatile register directly.

**Extension, for when you also can't operate the physical input device**
(e.g. iterating from a machine that isn't at the C64): compile a second
build where the input source is swapped at compile time (`#ifdef`/`-D`)
for a small deterministic function that scripts a known sequence of
inputs over time. Combined with an on-screen debug readout (as above),
this reproduces and isolates an input/logic bug via `ru64 peek` alone —
no human or physical hardware interaction needed — and cleanly separates
"bug in the input-reading path" from "bug in the logic that consumes it."
A downstream project (`cbm-joy`) used this to prove a CIA1 read path was
fine and isolate a bug to acceleration math instead.

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

### Custom linker configs for 64-byte-aligned data (e.g. sprites) need `fill = yes`, or the output file silently corrupts

Sprite bitmap data must start on a 64-byte boundary (the sprite pointer
at `$07F8`+ is a single byte = block address / 64). The clean way with
cc65: extend the stock `c64.cfg` with a dedicated `MEMORY` area at a
fixed, already-64-aligned address (e.g. `$2000`), and give the bitmap
data its own segment (`align = $40`) loaded there. Cap the preceding
area's declared `size` so it ends exactly where the new one begins (e.g.
`size = $2000 - __HEADER_LAST__`), so `ld65` hard-errors on overlap
instead of silently corrupting if the program ever grows too large.

**The gotcha**: a `.prg` is just `[2-byte load address][bytes]`, written
sequentially with no per-byte addressing. If the preceding area's
*actual* content ends well before the next area's fixed start address,
and that memory area doesn't have `fill = yes`, `ld65` does **not** pad
the output file to bridge the gap — the link succeeds, the symbol table
has the "correct" address for the aligned data, but the actual bytes land
at the wrong file offset and thus the wrong memory address at runtime,
while every reference to them still points at the *intended* address
(which on real hardware contains unrelated leftover RAM). Symptom: the
program runs fine, no crash, but whatever lives in the gapped area (e.g.
a sprite) renders as garbage. Diagnosable via `ru64 peek` of actual vs.
expected bytes, or by checking the `.prg` file size against the expected
address span. **Fix**: add `fill = yes` to that `MEMORY` area (default
fill byte `$00`; override with `fillval`). Confirmed via the official
ld65 docs: `fill`/`fillval` exist exactly for this, and also apply to
gaps left by `.align`/`.res`. Downstream project: `cbm-joy` (first mixed
C/asm build in that project, added a joystick-driven sprite).

**Related trap**: `ld65` config files (`.cfg`) use `#` for comments, not
`;` — `;` is a *ca65 assembly-source* comment marker, and using it in a
linker config produces an error like `Block identifier expected` rather
than a helpful "wrong comment character" message. Easy to reach for `;`
out of habit right after writing `.s` files.

## cc65 (2.19) codegen bug: signed ternary fed straight into `+=` on an `int` struct field

```c
/* buggy */
a->pos += pos_dir ? accel[a->hold] : -accel[a->hold];
```

where `accel[]` is `unsigned char[]` and `a->pos` is `int`. This can
**silently produce wildly wrong results** — not a crash, not a compiler
warning, just an incorrect number. Disassembly showed the negative
branch correctly computes a full 16-bit two's-complement negation of the
(zero-extended) `unsigned char` via cc65's `negax` runtime helper, but
the subsequent `+=`-into-`pos` codegen only adds the negated value's
*low* byte and unconditionally increments `pos`'s high byte on carry — a
pattern that's only valid for the positive branch (where the implicit
high byte genuinely is 0). Net effect: instead of decrementing, `pos`
jumps by roughly +256 minus the intended step. Concretely: `pos=139`,
`accel[hold]=1`, the "negative" branch produced `pos=394` instead of
`138`.

**Fix**: compute the signed delta into its own separate `int` local
first, rather than feeding the ternary straight into `+=`:

```c
int delta = accel[a->hold];
if (!pos_dir) delta = -delta;
a->pos += delta;
```

This reliably produces correct code. Not yet root-caused further (unknown
whether `-O` matters, or whether it's specific to a struct-field target
vs. a plain local `int`) — worth avoiding on sight regardless: any
`int_lvalue += cond ? unsigned_char_expr : -unsigned_char_expr` shape is
a real cc65 2.19 pitfall, not a one-off. Found via `cbm-joy` (a
joystick-driven sprite's acceleration math).

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
- **The actual fix when a C program needs the uppercase+graphics charset
  back** (crt0 having already switched to lowercase before `main()`
  runs): send PETSCII `$8E` ("switch to uppercase+graphics") back via the
  KERNAL's own `CHROUT`, using cc65's `<cbm.h>` wrapper —
  `cbm_k_bsout(0x8E);`. Confirmed via `ru64 peek` that this correctly
  flips `$D018`'s CB bits back to the uppercase/graphics ROM image
  (`$15` vs. lowercase's `$16`, same VM — see C64-REFERENCE.md's `$D018`
  entry). Prefer this KERNAL-call wrapper over poking `$D018`'s CB bits
  directly, to stay on the well-tested official path rather than
  re-deriving the exact bit pattern by hand. (Downstream: `cbm-joy`.)

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

## Sprite-authoring workflow: text grid → ca65 bytes, pointer-swap for animation

Hand-author sprite bitmaps as plain-text 24×21 grids (`.` = 0, `*` = 1,
one file per sprite/frame) — easy to eyeball, diff, and version-control.
Convert to ca65 `.byte` sprite data with a small script (bit 7 = leftmost
pixel of each 8-px group, MSB-first packing — the universal C64 sprite
byte convention). A same-shape "reversed" frame for e.g. a fire-button
toggle is just `tr '.*' '*.'` on the source grid.

At runtime, swap between two precomputed, 64-byte-aligned bitmap blocks
by rewriting the one-byte sprite pointer (`$07F8`+ = block address / 64)
rather than recomputing pixels — same zero-cost mechanism as
animation-frame swapping generally (see the linker-config section above
for getting sprite data 64-byte-aligned in the first place). Sprites have
no equivalent of character mode's bit-7 reverse-video trick (that only
works because the char ROM has separate pre-baked mirror glyphs) — for
sprites, precomputed alternate bitmaps + pointer swap is the standard
substitute. Downstream project: `cbm-joy`.

## LZSS compression for C64 assets, with a working 6502 decompressor

Closes the "design a screen live on hardware, read it back, compress it"
idea noted in README.md's "Next up" (commit `d680663`) — done and working
end to end on real hardware by `cbm-joy`: screen hand-drawn on
`u64elite`'s keyboard, peeked back over WiFi, compressed, embedded in a
build, decompressed and redisplayed, verified byte-for-byte via `ru64
peek`.

**Format**: for C64 assets (screen/color RAM dumps, ~1000 bytes each,
heavy on repeated runs), a byte-oriented LZSS variant strikes the right
balance — cheap to decode on 6502 (no bit-level match/offset packing,
just a per-token flag bit) while still compressing character-graphics
screens to roughly 15-35% of raw size and near-solid color RAM to ~3%.
`[2-byte LE uncompressed length][token groups]`. Each group = 1 control
byte (8 flag bits, LSB-first) + up to 8 tokens. Flag bit `1` = 1 literal
byte follows. Flag bit `0` = a 2-byte match follows: `[offset][length]`,
distance = `offset+1` (1-256, fits the whole window in one byte), length
= the `length` byte directly (2-255). Decompression stops once the
length-prefixed byte count is produced (trailing unused flag bits in the
final control byte are simply never read). Compression cost doesn't
matter (runs once, on the dev machine) — a brute-force longest-match
search over the whole 256-byte window is fine for ~1-2KB assets.
Reference implementation with round-trip self-verification:
`cbm-joy/tools/lzss.py` (also emits ca65 `.byte` lines via `--asm
<label>`).

**6502 decompressor gotcha — overlapping matches need a *forward* copy
loop**: the natural/fast 6502 idiom for copying N bytes is a backward
countdown (`ldy #N-1` / `dey` / `bpl`), since it avoids a separate
counter compare. This is **wrong** for LZ-style matches where distance <
length (e.g. distance=1, length=200 for "repeat the last byte 200
times") — each newly-written destination byte is itself a valid source
for a later byte in the *same* copy, and only forward order (low index
to high) produces that correctly; backward order reads still-
uninitialized destination bytes and corrupts the output. Long same-byte
runs are exactly the common case for screen/color RAM (background-color
or blank-cell regions), so this isn't an edge case to skip — it's hit
immediately on real data. Correct shape: `ldy #0` / `lda (src),y` / `sta
(dst),y` / `iny` / `cpy length` / `bne loop`, then a single 16-bit
pointer/remaining-count adjustment by the full match length afterward
(not per-byte), to keep the common case fast despite the per-byte
compare.

## VIC-II screen-pointer double buffering: instant, tear-free screen swaps (character grid only — color RAM has no equivalent)

Decompressing straight into the live `$0400`/`$D800` causes visible
tearing (VIC-II is scanning it out while the CPU is mid-write); even a
raw block-move-to-live-memory approach (see the fast-copy technique
below) is faster than decompressing live but still can't outrun the
raster beam for a full ~1000-byte screen, so it still tears slightly.

**Full fix for the character grid** (not color): `$D018`'s upper bits
pick which of several possible screen-matrix locations the VIC treats as
"live" (see C64-REFERENCE.md's `$D018` entry for the exact bit layout
and worked examples). Decompress the *next* screen into a second,
currently-inactive valid screen location, then swap which one is
displayed with a single `$D018` write — genuinely instant, nothing for
the raster beam to catch mid-update.

- **Avoid bank-relative `$1000`-`$1FFF` for screen-matrix placement**
  when the VIC is in bank 0 or bank 2 — that range shows the built-in
  character-generator ROM to the VIC regardless of underlying RAM
  content on real hardware (a well-known VIC-II quirk). Not yet confirmed
  whether the shadow applies per access-type (only CB-selected character
  fetches) or per raw address range (any VIC access, including
  VM-selected screen-matrix fetches) — `cbm-joy` didn't need to resolve
  that ambiguity, just picked a screen location outside the range
  entirely (`$2400`). Worth pinning down precisely if this becomes a
  recurring technique.
- 16 possible `$D018` screen locations exist per 16KB VIC bank (`$0000`,
  `$0400`, ... `$3C00`, each `$400` apart); minus the 4 in the char-ROM
  shadow range, minus whatever the program's own code/data/sprites
  occupy, there's comfortably room for several simultaneous screen
  buffers in one bank (e.g. pre-staging all 4 directional-neighbor
  screens for a non-scrolling 2D game — an idea worth revisiting, not yet
  built).
- **Color RAM has no equivalent double-buffer in hardware** — it's a
  single physical 1000-nibble SRAM chip, always at `$D800`, no bank/
  pointer to flip. Any actual color change on screen-swap still needs a
  real copy, no matter how many screen-matrix buffers are pre-staged —
  the one part of a screen transition that can still show minor tearing.

Downstream project: `cbm-joy`.

### Fast fixed-size 6502 block copy (e.g. the color-RAM blit above, or any known-size buffer-to-buffer move)

Standard shape for copying N bytes where N > 255: Y-register
page-wraparound addressing (`ldy #0` / `lda (ptr1),y` / `sta (ptr2),y` /
`iny` / `bne loop`) so only the pointers' *high* bytes need incrementing
— once per 256 bytes — rather than a 16-bit increment-with-carry-branch
on every single byte. For a fixed 1000-byte copy: 3 full 256-byte pages
via that loop, then a final 232-byte tail with a plain `cpy #232` bound.
Wrapping the actual live-memory copy in `SEI`/`CLI` (cc65: `<6502.h>`'s
`SEI()`/`CLI()` macros, see CC65-TOOLCHAIN.md) keeps its duration
deterministic by preventing the KERNAL's ~60Hz IRQ (keyboard scan etc.)
from stretching it out mid-copy with unrelated work.

## Host selection convention (this repo)

No Ultimate64 IP is hardcoded anywhere committed to git — there are two
physical units on this LAN and which one is "current" is picked
per-session, not fixed. See `tools/u64-hosts.txt` (name → IP map),
`tools/select-u64.sh <name>` (writes the pick to the gitignored
`.ultimate_host` statefile), and the Makefile's `check-host`/`host`
targets. `ULTIMATE_HOST=<ip>` on the command line overrides for one
invocation without touching the saved selection.

### Using this from another project

This repo (`~/src/cbm/c64home`) is meant to stay the single source of truth
for the device list — sibling projects under `~/src/cbm/` should
reference `../c64home/tools/select-u64.sh` and
`tools/u64-hosts.txt` by relative path rather than copying them, so there's one
place to add a device or fix a bug. Each project's own `Makefile`/build layout will naturally be
project-specific regardless, and can still read whatever `.ultimate_host`
statefile it wants (own copy, or point at this repo's) — the two aren't
coupled. If a project ever needs the selector itself to behave
differently, fork a local copy then; these are small scripts, so that's a
cheap, reversible decision to defer rather than commit to upfront.
