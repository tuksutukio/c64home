# cc65 toolchain quick reference

The cc65 toolchain's own syntax/APIs — ca65 assembler directives and the
cc65 C library. For raw 6502/C64 hardware facts see
**[C64-REFERENCE.md](C64-REFERENCE.md)**; for gotchas/discoveries specific
to this repo's own work (build configs, the IRQ pattern, charset quirks)
see **[KNOWLEDGE.md](KNOWLEDGE.md)** — this file is syntax lookup only, not
narrative.

## ca65 assembler directives

Verified against the actual manual
([doc/ca65.sgml](https://github.com/cc65/cc65/blob/master/doc/ca65.sgml) in
the cc65 repo), not reconstructed from memory. Covers what's actually
likely to get reached for — see `src/irq_border.s` in this repo for a real
example already using `.segment` and `.byte`.

### Segments and program structure

| Directive | Does | Example |
|---|---|---|
| `.segment "NAME"` | Switch output to a named segment (up to 254/object file). Shortcuts exist: `.code`/`.data`/`.rodata`/`.bss`/`.zeropage` for the common ones. | `.segment "CODE"` |
| `.proc name .endproc` | Define a named, scoped block — like a label but with its own local-symbol scope (avoids name clashes between routines). | `.proc irq_handler` ... `.endproc` |
| `.scope name .endscope` | Generic nested scope, not tied to a routine (unlike `.proc`, doesn't imply "this is a subroutine"). | `.scope Foo` ... `.endscope` |
| `.local name` | Declare a symbol local to the enclosing macro expansion (avoids label clashes across multiple invocations of the same macro). | `.local loop` |
| `.org addr` | Set an absolute program counter. Rarely needed with cc65's linker-driven configs (`c64.cfg`/`c64-asm.cfg`) since segment placement handles addressing — mainly relevant for raw/standalone assembly outside cc65's usual linked workflow. | `.org $c000` |

### Data allocation

| Directive | Does | Example |
|---|---|---|
| `.byte` (or `.byt`) | Emit one or more bytes; also accepts string literals (subject to `-t`/`.charmap` translation, see below). | `.byte "hi", 13, 0` |
| `.word` | Emit one or more 16-bit little-endian words. | `.word $c000, label` |
| `.dbyt` | Emit one or more 16-bit **big-endian** words (rare; some KERNAL tables want this byte order). | `.dbyt $1234` |
| `.dword` | Emit one or more 32-bit little-endian values. | `.dword $12345678` |
| `.addr` | Like `.word`, semantically "this is an address" (mainly documentation intent; some tooling distinguishes it from `.word`). | `.addr routine` |
| `.res n[, fill]` | Reserve `n` bytes of (default zero-filled) storage without emitting explicit data — for BSS-style uninitialized space. | `buffer: .res 256` |

### Import/export/include

| Directive | Does | Example |
|---|---|---|
| `.export name` | Make a symbol visible to the linker for other modules (or, for a `c64-asm.cfg`-style build, this is how a pure-asm C-runtime entry point like `_main` gets exposed — see KNOWLEDGE.md). | `.export _main` |
| `.exportzp name` | Same, but for a zero-page symbol. | `.exportzp ptr` |
| `.import name` | Pull in a symbol defined in another module/the runtime library. | `.import _main` |
| `.importzp name` | Same, for a zero-page symbol. | `.importzp ptr` |
| `.include "file"` | Textually include another source file (headers, shared constants). | `.include "c64.inc"` |

### Constants and conditionals

| Directive | Does | Example |
|---|---|---|
| `.define name val` (or `.undefine`) | Text-substitution macro, like C's `#define`/`#undef`. cc65's own docs recommend avoiding it where `.set`/constants suffice — it shares C `#define`'s foot-guns. | `.define SCREEN $0400` |
| `.set name = val` | Assign a value to a **numeric variable** (re-assignable, unlike a plain label/constant). | `.set count = count + 1` |
| `.if` / `.ifdef` / `.ifndef` / `.else` / `.endif` | Standard conditional assembly, evaluated at assemble time. | `.ifdef DEBUG` ... `.endif` |

### Macros

| Directive | Does | Example |
|---|---|---|
| `.macro name [params] .endmacro` | Classic parameterized macro; expands inline at each invocation. | `.macro inc16 addr` ... `.endmacro` |
| `.repeat count[, var] .endrep` | Repeat the enclosed block `count` times at assemble time; if given, `var` is replaced by the current iteration (0-based) inside the body. Commonly used *inside* a `.macro` for unrolled/generated code. | `.repeat 4, I` ... `.byte I` ... `.endrep` |
| `.exitmacro` | Bail out of the current macro expansion early. | — |
| `.delmacro` | Delete a previously-defined `.macro`. | `.delmacro inc16` |

### Structs, enums, assertions

| Directive | Does | Example |
|---|---|---|
| `.struct name ... .endstruct` | Define a C-struct-like layout of field offsets (doesn't allocate storage itself — use with `.tag` or manual offsets). | `.struct Point x .byte` `y .byte` `.endstruct` |
| `.enum [name] ... .endenum` | Define a set of named integer constants, auto-incrementing unless given explicit values. | `.enum` `RED` `GREEN` `BLUE` `.endenum` |
| `.assert expr, action[, msg]` | Assemble-time assertion; `action` is typically `error` or `warning` if `expr` is false. Useful for catching e.g. a table exceeding an expected size. | `.assert * <= $2000, error` |

### Character/string translation

| Directive | Does | Example |
|---|---|---|
| `.charmap src, dst` | Remap one source character code (0-255) to one output byte for subsequent `.byte`/`.asciiz` strings — overrides the default `-t <target>` translation table for that character. This is the mechanism *behind* the lowercase/uppercase PETSCII swap on `-t c64` we hit already (see KNOWLEDGE.md); use `.charmap` if you need to override it for a specific character rather than relying on cc65's default table. | `.charmap $41, $61  ; map 'A' to 'a'` |
| `.pushcharmap` / `.popcharmap` | Save/restore the current charmap state (e.g. around a block that needs different translation than the surrounding code). | — |

### CPU selection — relevant for undocumented opcodes

| Directive | Does | Example |
|---|---|---|
| `.setcpu "6502X"` | Switch the instruction set ca65 accepts. Plain `"6502"` (the default) only assembles **documented** opcodes — assembling any undocumented/illegal 6502 opcode (once that reference table gets added here) requires `.setcpu "6502X"` first, or ca65 rejects it as an error. Other values: `6502`, `6502DTV`, `65SC02`, `65C02`, `65816`, `4510`, `45GS02`, `HuC6280`, `m740`. | `.setcpu "6502X"` |

## cc65 C library quick reference

Verified against the actual headers in
[cc65/include](https://github.com/cc65/cc65/tree/master/include) (fetched
directly, not summarized from a blog) — `conio.h`, `6502.h`, `peekpoke.h`,
`c64.h`, `_vic2.h`, `_sid.h`, `_6526.h`.

### `<conio.h>` — direct console I/O

Faster than stdio since it writes screen memory directly; no text-window
support (whole-screen only).

| Function | Does |
|---|---|
| `clrscr()` | Clear screen, cursor to top-left |
| `gotoxy(x,y)` / `gotox(x)` / `gotoy(y)` | Move cursor |
| `wherex()` / `wherey()` | Read cursor position |
| `cputc(c)` / `cputcxy(x,y,c)` | Output one char (at position) |
| `cputs(s)` / `cputsxy(x,y,s)` | Output a string (at position) |
| `cprintf(fmt, ...)` | `printf`-style, direct screen output |
| `cgetc()` | Blocking read of one key |
| `kbhit()` | Non-blocking "is a key waiting?" |
| `cpeekc()` / `cpeekcolor()` / `cpeekrevers()` | Read char/color/reverse-flag at cursor without moving it |
| `textcolor(c)` / `bgcolor(c)` / `bordercolor(c)` | Set text/background/border color; each **returns the old value** |
| `revers(onoff)` | Toggle reverse-video text; returns old setting |
| `cursor(onoff)` | Toggle the blinking input cursor; returns old setting |
| `chline(len)` / `cvline(len)` | Draw a horizontal/vertical line of screen-line-drawing chars |
| `cclear(len)` | Clear part of the current line (writes spaces) |
| `screensize(&x,&y)` | Get screen dimensions (40×25 on C64) |

### `<6502.h>` — CPU-level access

| Item | Does |
|---|---|
| `getcpu()` | Detect actual CPU (`CPU_6502`, `CPU_65C02`, `CPU_65816`, ... — useful since cc65 targets more than the plain 6502) |
| `SEI()` / `CLI()` / `BRK()` | Inline-asm macros for the raw instructions |
| `struct regs { a,x,y,flags; unsigned pc; }` + `_sys(&r)` | Call an arbitrary machine-language routine, passing/receiving registers |
| `set_brk(handler)` / `reset_brk()` | Install/remove a C-level `BRK` handler; register values available via `brk_a`/`brk_x`/`brk_y`/`brk_sr`/`brk_pc` |
| `set_irq(handler, stack, size)` / `reset_irq()` | Install/remove a **C-level** IRQ handler (returns `IRQ_HANDLED`/`IRQ_NOT_HANDLED`). Higher-level alternative to the raw `$0314`/`$0315` vector hook we used in `src/irq_border.s` — that asm approach chains to KERNAL directly and stays pure-asm/no-runtime; `set_irq` is the C-runtime-dependent equivalent, worth knowing both exist. |

### `<peekpoke.h>` — BASIC-style memory access from C

Trivial macros, but exactly what you want for quick register pokes without
pointer-cast boilerplate:

```c
#define POKE(addr,val)   (*(unsigned char*)(addr) = (val))
#define POKEW(addr,val)  (*(unsigned*)(addr) = (val))
#define PEEK(addr)       (*(unsigned char*)(addr))
#define PEEKW(addr)      (*(unsigned*)(addr))
```

e.g. `POKE(0xD020, 0);` to set the border color — same effect as our asm
example's `inc $d020`, just from C.

### `<c64.h>` — struct-style hardware register access

Alternative to raw addresses (as tabulated in C64-REFERENCE.md): `c64.h`
exposes `VIC`, `SID`, `CIA1`, `CIA2` as typed structs over the same
addresses, so `VIC.bordercolor = 0` works instead of `POKE(0xD020, 0)`.
Field names (from the real headers, not guessed):

- **`VIC`** (`struct __vic2` @ `$D000`): `spr0_x`/`spr0_y` .. `spr7_x`/`spr7_y` (or `spr_pos[8].x`/`.y`), `spr_hi_x`, `ctrl1`, `rasterline`, `strobe_x`/`strobe_y` (light pen), `spr_ena`, `ctrl2`, `spr_exp_y`, `addr` (screen/charset pointers), `irr`/`imr` (interrupt status/enable — our `$D019`/`$D01A`), `spr_bg_prio`, `spr_mcolor`, `spr_exp_x`, `spr_coll`, `spr_bg_coll`, `bordercolor`, `bgcolor0`-`bgcolor3`, `spr_mcolor0`/`spr_mcolor1`, `spr0_color`-`spr7_color`.
- **`SID`** (`struct __sid` @ `$D400`): `v1`/`v2`/`v3` (each a `struct __sid_voice`), `flt_freq`, `flt_ctrl`, `amp` (volume), `ad1`/`ad2` (paddle ADC), `noise`, `read3` (voice 3 oscillator readback).
- **`CIA1`/`CIA2`** (`struct __6526` @ `$DC00`/`$DD00`): `pra`/`prb`, `ddra`/`ddrb`, `ta_lo`/`ta_hi`, `tb_lo`/`tb_hi`, `tod_10`/`tod_sec`/`tod_min`/`tod_hour`, `sdr`, `icr`, `cra`/`crb`.

Also in `c64.h`: `COLOR_*` constants (`COLOR_BLACK` `0x00` through `COLOR_GRAY3` `0x0F`, matching the palette order in C64-REFERENCE.md), `CH_F1`-`CH_F8` (function-key char codes), `JOY_*_MASK` bits for `joy_read()`, `COLOR_RAM` (`$D800` as `unsigned char*`), and `get_ostype()` (detect KERNAL ROM revision — e.g. would return a real value even under JiffyDOS, since JiffyDOS preserves standard entry points; untested by us specifically though).

## See also

6502/6510 opcode reference (documented + undocumented/illegal, including
which `.setcpu "6502X"` unlocks) is in **[6502-OPCODES.md](6502-OPCODES.md)**.
