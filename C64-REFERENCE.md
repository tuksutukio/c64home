# Commodore 64 hardware reference

Static hardware facts — memory map, register layouts, BASIC tokens,
PETSCII/screen codes. This data doesn't change (the C64 is a fixed,
40+-year-old machine); it won't drift the way Ultimate64 firmware
behavior can. For things we discovered the hard way while building this
repo's pipeline (cc65 configs, IRQ hooking pattern, WiFi limitations,
toolchain gotchas), see **[KNOWLEDGE.md](KNOWLEDGE.md)** instead — this
file is lookup tables, not a narrative. For the 6502/6510 instruction set,
see **[6502-OPCODES.md](6502-OPCODES.md)**. For ca65/cc65 syntax, see
**[CC65-TOOLCHAIN.md](CC65-TOOLCHAIN.md)**.

## Memory map

| Range | Contents |
|---|---|
| `$0000`-`$00FF` | Zero page (see selected entries below) |
| `$0100`-`$01FF` | 6502 stack |
| `$0200`-`$02FF` | System RAM: I/O buffer, KERNAL file tables, keyboard buffer, screen/cursor state |
| `$0300`-`$033B` | KERNAL/BASIC RAM vectors (see table below) |
| `$033C`-`$03FB` | Tape I/O buffer (cassette buffer; free RAM if not using tape) |
| `$0400`-`$07E7` | Screen RAM — video matrix, 25 lines × 40 columns (1000 bytes used of 1024 allocated) |
| `$07F8`-`$07FF` | Sprite data pointers (for default screen RAM location) |
| `$0800`-`$9FFF` | Normal BASIC program space (start of BASIC text at `$0801`) |
| `$8000`-`$9FFF` | Cartridge ROM (low, 8 KB) if a cartridge is present |
| `$A000`-`$BFFF` | BASIC ROM (8 KB) — or RAM / cartridge ROM (high) depending on `$01` banking |
| `$C000`-`$CFFF` | Free RAM (4 KB), no ROM ever maps here |
| `$D000`-`$D3FF` | VIC-II registers (see below) |
| `$D400`-`$D7FF` | SID registers (see below) |
| `$D800`-`$DBE7` | Color RAM (nibbles; only low 4 bits meaningful) |
| `$DC00`-`$DCFF` | CIA 1 (keyboard matrix, joystick port 1/2, IRQ source) |
| `$DD00`-`$DDFF` | CIA 2 (serial bus, user port, NMI source) |
| `$DE00`-`$DFFF` | Reserved I/O expansion (cartridge-dependent) |
| `$E000`-`$FFFF` | KERNAL ROM (8 KB) — or RAM depending on `$01` banking |

Note `$D000`-`$DFFF` is banked: it holds I/O registers *or* the character
generator ROM *or* RAM, depending on the `$01` processor port bits below.

**Sources**: [C64 Programmer's Reference Guide, memory map](https://www.devili.iki.fi/Computers/Commodore/C64/Programmers_Reference/Chapter_5/page_311.html)

### Zero page — selected entries relevant to real work

| Addr | Label | Purpose |
|---|---|---|
| `$0000` | D6510 | 6510 data-direction register (which `$01` bits are outputs) |
| `$0001` | R6510 | 6510 I/O port — LORAM/HIRAM/CHAREN banking bits, datassette control (see below) |
| `$002B`-`$002C` | TXTTAB | Pointer: start of BASIC text |
| `$002D`-`$002E` | VARTAB | Pointer: start of BASIC variables |
| `$0090` | STATUS | KERNAL I/O status word (`ST`) |
| `$00A0`-`$00A2` | TIME | Real-time jiffy clock (~1/60 sec, `TI`/`TI$`) |
| `$00C5` | LSTX | Current key pressed |
| `$00C6` | NDX | Number of chars in keyboard buffer queue |
| `$00D1`-`$00D2` | PNT | Pointer: current screen line address |
| `$00D3` | PNTR | Cursor column on current line |
| `$00D6` | TBLX | Current cursor physical line number |

Full zero-page table (BASIC interpreter internals — floating point accumulator,
string stack, etc.) is in the source above; only the KERNAL/screen-relevant
subset is repeated here.

### `$01` processor port — ROM/RAM banking

Bits 0-2 (LORAM, HIRAM, CHAREN) control what's mapped where; bits 3-5
control the datassette motor/data lines. The three relevant to memory
banking:

| Bit | Name | Meaning when set (1) | Meaning when clear (0) |
|---|---|---|---|
| 0 | LORAM | BASIC ROM visible at `$A000`-`$BFFF` | RAM visible instead |
| 1 | HIRAM | KERNAL ROM visible at `$E000`-`$FFFF` | RAM visible instead |
| 2 | CHAREN | I/O registers visible at `$D000`-`$DFFF` | Character generator ROM visible instead |

This is exactly what cc65's `crt0.s` manipulates: it saves `$01`, clears
bit 0 (`AND #$F8; ORA #$06`) to bank out BASIC ROM while keeping
KERNAL+I/O enabled during program execution, then restores the original
value on exit. See KNOWLEDGE.md's cc65 build-config section.

**Source**: [Bank Switching, C64-Wiki](https://www.c64-wiki.com/wiki/Bank_Switching); [6510 Processor Port, C64 OS](https://www.c64os.com/post/6510procport)

### RAM vectors (`$0300`-`$033B`)

| Addr | Label | Purpose |
|---|---|---|
| `$0300`-`$0301` | IERROR | Print BASIC error message |
| `$0302`-`$0303` | IMAIN | BASIC warm start |
| `$0304`-`$0305` | ICRNCH | Tokenize BASIC text |
| `$0306`-`$0307` | IQPLOP | BASIC text LIST |
| `$0308`-`$0309` | IGONE | BASIC character dispatch |
| `$030A`-`$030B` | IEVAL | BASIC token evaluation |
| `$030C`-`$030F` | SAREG/SXREG/SYREG/SPREG | Saved 6502 A/X/Y/SP for `SYS` |
| `$0310`-`$0312` | USRPOK/USRADD | `USR()` function jump vector |
| **`$0314`-`$0315`** | **CINV** | **Hardware IRQ vector** — default `$EA31`. This is the one we hook (see KNOWLEDGE.md IRQ pattern). |
| `$0316`-`$0317` | CBINV | `BRK` instruction interrupt vector |
| `$0318`-`$0319` | NMINV | Non-maskable interrupt vector — default points into RESTORE-key handling |
| `$031A`-`$031B` | IOPEN | KERNAL OPEN vector |
| `$031C`-`$031D` | ICLOSE | KERNAL CLOSE vector |
| `$031E`-`$031F` | ICHKIN | KERNAL CHKIN vector |
| `$0320`-`$0321` | ICKOUT | KERNAL CHKOUT vector |
| `$0322`-`$0323` | ICLRCH | KERNAL CLRCHN vector |
| `$0324`-`$0325` | IBASIN | KERNAL CHRIN vector |
| `$0326`-`$0327` | IBSOUT | KERNAL CHROUT vector |
| `$0328`-`$0329` | ISTOP | KERNAL STOP vector |
| `$032A`-`$032B` | IGETIN | KERNAL GETIN vector |
| `$032C`-`$032D` | ICLALL | KERNAL CLALL vector |
| `$032E`-`$032F` | USRCMD | User-defined vector (unused by KERNAL) |
| `$0330`-`$0331` | ILOAD | KERNAL LOAD vector |
| `$0332`-`$0333` | ISAVE | KERNAL SAVE vector |

**Source**: same PRG memory-map page as above.

### Hardware interrupt vectors (top of address space, always ROM)

| Addr | Purpose | Default target |
|---|---|---|
| `$FFFA`-`$FFFB` | NMI vector | `$FE43` |
| `$FFFC`-`$FFFD` | RESET vector | `$FCE2` |
| `$FFFE`-`$FFFF` | IRQ/BRK vector | `$FF48` |

These live in KERNAL ROM and can't be changed (unless KERNAL ROM itself is
banked out) — that's *why* the RAM vectors above (`CINV` etc.) exist: the
ROM routine at `$FF48` pushes registers then does `JMP ($0314)`, handing
control to RAM so user programs can intercept it without touching ROM.

**Source**: [Interrupt, C64-Wiki](https://www.c64-wiki.com/wiki/Interrupt); [Internals of BRK/IRQ/NMI/RESET on a MOS 6502, pagetable.com](https://www.pagetable.com/?p=410)

## KERNAL routine jump table (`$FF81`-`$FFF3`)

All standard entry points are `JMP` stubs at fixed addresses (stable
across KERNAL ROM revisions/replacements, including the JiffyDOS ROM this
repo's hardware runs — see KNOWLEDGE.md).

| Routine | Addr | Function |
|---|---|---|
| CINT | `$FF81` | Initialize screen editor / VIC chip |
| IOINIT | `$FF84` | Initialize I/O devices |
| RAMTAS | `$FF87` | Initialize RAM, allocate/test memory |
| RESTOR | `$FF8A` | Restore default I/O vectors |
| VECTOR | `$FF8D` | Read/set vectored I/O (copy vector table) |
| SETMSG | `$FF90` | Control KERNAL kernal/error message display |
| SECOND | `$FF93` | Send secondary address after LISTEN |
| TKSA | `$FF96` | Send secondary address after TALK |
| MEMTOP | `$FF99` | Read/set top of memory |
| MEMBOT | `$FF9C` | Read/set bottom of memory |
| SCNKEY | `$FF9F` | Scan keyboard |
| SETTMO | `$FFA2` | Set timeout on serial bus |
| ACPTR | `$FFA5` | Input byte from serial port |
| CIOUT | `$FFA8` | Output byte to serial port |
| UNTLK | `$FFAB` | Command serial bus device to UNTALK |
| UNLSN | `$FFAE` | Command serial bus device to UNLISTEN |
| LISTEN | `$FFB1` | Command serial bus device to LISTEN |
| TALK | `$FFB4` | Command serial bus device to TALK |
| READST | `$FFB7` | Read I/O status word (`ST`) |
| SETLFS | `$FFBA` | Set logical file number, device, secondary address |
| SETNAM | `$FFBD` | Set filename |
| OPEN | `$FFC0` | Open a logical file (via vector `IOPEN`) |
| CLOSE | `$FFC3` | Close a logical file (via `ICLOSE`) |
| CHKIN | `$FFC6` | Open channel for input (via `ICHKIN`) |
| CHKOUT | `$FFC9` | Open channel for output (via `ICKOUT`) |
| CLRCHN | `$FFCC` | Close input/output channels, restore default (via `ICLRCH`) |
| **CHRIN** | **`$FFCF`** | **Input character from channel** (via `IBASIN`) |
| **CHROUT** | **`$FFD2`** | **Output character to channel** (via `IBSOUT`) — the routine our examples use |
| LOAD | `$FFD5` | Load RAM from a device (via `ILOAD`) |
| SAVE | `$FFD8` | Save RAM to a device (via `ISAVE`) |
| SETTIM | `$FFDB` | Set the jiffy clock |
| RDTIM | `$FFDE` | Read the jiffy clock |
| STOP | `$FFE1` | Scan the STOP key (via `ISTOP`) |
| GETIN | `$FFE4` | Get a character from the keyboard/input queue (via `IGETIN`) |
| CLALL | `$FFE7` | Close all files (via `ICLALL`) |
| UDTIM | `$FFEA` | Increment the jiffy clock |
| SCREEN | `$FFED` | Return X,Y screen organization (columns/rows) |
| PLOT | `$FFF0` | Read/set cursor X,Y position |
| IOBASE | `$FFF3` | Return base address of CIA I/O devices |

**Source**: [C64 Programmer's Reference Guide, User Callable KERNAL Routines](https://www.devili.iki.fi/Computers/Commodore/C64/Programmers_Reference/Chapter_5/page_272.html)

### Standard file I/O sequence and device numbers

Relevant once the `.d64` mounting TODO (see README.md) actually gets
tackled — reading/writing a real file on a mounted disk, not just DMA-load
of a `.prg`.

**Device numbers**:

| Number | Device |
|---|---|
| 0 | Keyboard |
| 1 | Datasette |
| 2 | RS-232 / modem |
| 3 | Screen |
| 4-5 | Printer |
| 8-15 | Disk drives (IEC serial bus) |

**Standard sequence** (register conventions verified against
[sta.c64.org's KERNAL function reference](https://sta.c64.org/cbm64krnfunc.html)
— note the widely-mirrored devili.iki.fi PRG transcription has the
`SETLFS` example comments transposed, `A`/`X` swapped; sta.c64.org and
general community consensus agree with the version below):

1. **`SETNAM`** (`$FFBD`) — `A` = filename length, `X`/`Y` = pointer to
   filename (low/high byte).
2. **`SETLFS`** (`$FFBA`) — `A` = logical file number (1-127, your choice,
   used as the handle for later calls), `X` = device number, `Y` =
   secondary address.
3. **`OPEN`** (`$FFC0`) — no register input; opens using the params set
   above.
4. **`CHKIN`** (`$FFC6`, to read) or **`CHKOUT`** (`$FFC9`, to write) —
   `X` = logical file number from step 2, redirects KERNAL input/output to
   that channel.
5. Read/write via **`CHRIN`**/**`CHROUT`** in a loop, checking `STATUS`
   (`$90`, via `READST` `$FFB7`) for end-of-file/error between calls.
6. **`CLOSE`** (`$FFC3`) — `A` = logical file number to close.
7. **`CLRCHN`** (`$FFCC`) — restore default input/output (keyboard/screen).

**Secondary address meanings** (relevant to step 2, disk device):
`0` = binary load, ignore file header, use `X`/`Y` from the `LOAD` call as
the load address; `1` = binary save, or load using the address embedded
in the file's own header (relocatable load); `2`-`14` = general-purpose
sequential read/write channel numbers (your choice, used for bookkeeping
if multiple files are open concurrently); `15` = command/control channel
(disk commands like `S0:filename` to scratch, `I0` to initialize, reading
the drive's error channel).

**Sources**: [SETLFS/SETNAM/OPEN, sta.c64.org KERNAL reference](https://sta.c64.org/cbm64krnfunc.html); [Device number, C64-Wiki](https://www.c64-wiki.com/wiki/Device_number)

## VIC-II registers (`$D000`-`$D02E`)

| Addr | Name | Purpose |
|---|---|---|
| `$D000`-`$D00F` | M0X/M0Y-M7X/M7Y | Sprite 0-7 X/Y coordinates (X is 8-bit; see `$D010` for MSBs) |
| `$D010` | MSB | Bit 8 (MSB) of each sprite's X coordinate |
| `$D011` | CTRL1 | Control register 1: RST8 (raster MSB), ECM, BMM, DEN (screen on/off), RSEL, YSCROLL |
| `$D012` | RASTER | Current raster line (write: raster IRQ compare line, low 8 bits) |
| `$D013`/`$D014` | LPX/LPY | Light pen X/Y |
| `$D015` | SPENA | Sprite enable flags (M0E-M7E) |
| `$D016` | CTRL2 | Control register 2: RES, MCM (multicolor), CSEL, XSCROLL |
| `$D017` | SPYEX | Sprite Y-expansion flags |
| `$D018` | MEMPTR | Screen/character memory pointers (VM13-VM10, CB13-CB11) |
| **`$D019`** | **IRQREG** | **Interrupt status: which VIC IRQ source fired** (IRQ, ILP, IMMC, IMBC, IRST) — write 1 to acknowledge |
| `$D01A` | IRQENA | Interrupt enable: which VIC sources can raise IRQ |
| `$D01B` | SPPRIOR | Sprite/background display priority per sprite |
| `$D01C` | SPMC | Sprite multicolor-mode flags per sprite |
| `$D01D` | SPXEX | Sprite X-expansion flags |
| `$D01E` | SPCOL | Sprite-sprite collision (read clears it) |
| `$D01F` | SPBGC | Sprite-background collision (read clears it) |
| **`$D020`** | **BORDCR** | **Border color** — what our `irq_border.s` example increments every IRQ |
| `$D021` | BG0 | Background color 0 |
| `$D022`-`$D024` | BG1-BG3 | Extra background colors (multicolor/ECM modes) |
| `$D025`/`$D026` | SPMC0/SPMC1 | Shared sprite multicolor colors |
| `$D027`-`$D02E` | SP0C-SP7C | Individual sprite colors 0-7 |

Note: our `irq_border.s` (see `src/`) hooks `CINV` (`$0314`, above) rather
than using the VIC's own raster-IRQ mechanism (`$D012`/`$D019`/`$D01A`) —
that's a legitimate alternative approach for anyone wanting *raster-timed*
effects instead of "once per whatever generates the default IRQ" (CIA1
timer, ~60 Hz).

**Source**: [The MOS 6567/6569 video controller (VIC-II), zimmers.net](https://www.zimmers.net/cbmpics/cbm/c64/vic-ii.txt) (the widely-cited "VIC Article")

### Sprite viewport-clamp coordinates (standard 40×25 unscrolled text mode)

A sprite's `$D0nn` X/Y registers give its **top-left pixel** in raw VIC
coordinate space (0-511 X via `$D010`'s MSB extension, 0-255 Y) — not
screen-relative pixels. Visible display area in that raw space: **X
24-344** (320px wide), **Y 50-250** (200px tall). For an unexpanded
24×21px sprite to stay fully on-screen, clamp its position to **X in
[24, 320]** (344-24), **Y in [50, 229]** (250-21). Confirmed against
[C64-Wiki's Sprite article](https://www.c64-wiki.com/wiki/Sprite) and
[Dustlayer's VIC-II sprite guide](https://dustlayer.com/vic-ii/2013/4/28/vic-ii-for-beginners-part-5-bringing-sprites-in-shape).
Sprites aren't limited to the visible 320×200 area — the full 512×256
coordinate space lets them move off-screen into the border and beyond.

### Raster/timing facts (PAL vs. NTSC)

| Video standard | VIC-II chip | Cycles/line | Total lines/frame | Cycles/frame | Refresh rate |
|---|---|---|---|---|---|
| PAL | 6569 | 63 | 312 | 19,656 | ~50.125 Hz |
| NTSC (older) | 6567R56A | 64 | 262 | 16,768 | ~60.05 Hz |
| NTSC (newer) | 6567R8 | 65 | 263 | 17,095 | ~59.83 Hz |

(Two different NTSC figures show up across sources because there were two
VIC-II chip revisions with genuinely different timing — not a source
disagreement.)

**Bad lines**: every 8th raster line (start of a new character row), the
VIC-II steals 40 extra cycles from the CPU to fetch a row of screen/color
data, leaving only ~23 CPU cycles of that line free for computation
instead of the usual ~63/65. This is *why* raster-timed effects (splits,
sprite multiplexing) are hard to get exactly right — available CPU time
per line isn't constant. `$D011` bit 3 (RST8, raster IRQ compare MSB) +
`$D012` (raster compare low 8 bits) + `$D019`/`$D01A` (IRQ status/enable,
above) is the standard way to trigger a raster IRQ instead of relying on
the CIA1-timer-driven default IRQ our `irq_border.s` hooks.

**Sources**: [raster time, C64-Wiki](https://www.c64-wiki.com/wiki/raster_time)

## SID registers (`$D400`-`$D41C`)

| Addr | Name | Purpose |
|---|---|---|
| `$D400`/`$D401` | FREQLO1/HI1 | Voice 1 frequency (16-bit) |
| `$D402`/`$D403` | PWLO1/HI1 | Voice 1 pulse width (12-bit) |
| `$D404` | CR1 | Voice 1 control: gate, sync, ring mod, test, waveform select (triangle/saw/pulse/noise) |
| `$D405` | AD1 | Voice 1 attack/decay |
| `$D406` | SR1 | Voice 1 sustain/release |
| `$D407`-`$D40D` | (as above) | Voice 2, same layout |
| `$D40E`-`$D414` | (as above) | Voice 3, same layout |
| `$D415`/`$D416` | FCLO/FCHI | Filter cutoff frequency (11-bit) |
| `$D417` | RES/FILT | Filter resonance + which voices are routed through the filter |
| `$D418` | MODE/VOL | Filter mode (low/band/high-pass, voice 3 disable) + master volume (global, all voices) |
| `$D419`/`$D41A` | POTX/POTY | Paddle X/Y (read-only) |
| `$D41B` | OSC3 | Voice 3 oscillator output (read-only — common noise/random source) |
| `$D41C` | ENV3 | Voice 3 envelope output (read-only) |

**Source**: [SID reference, oxyron.de](https://www.oxyron.de/html/registers_sid.html)

## CIA registers (6526, `$DC00`-`$DC0F` and `$DD00`-`$DD0F`)

Both CIAs share the same register layout at their respective base
addresses:

| Offset | Name | Purpose |
|---|---|---|
| `$00` | PRA | Data Port A |
| `$01` | PRB | Data Port B |
| `$02` | DDRA | Data direction, Port A (1=output) |
| `$03` | DDRB | Data direction, Port B (1=output) |
| `$04`/`$05` | TA LO/HI | Timer A |
| `$06`/`$07` | TB LO/HI | Timer B |
| `$08` | TOD 10THS | Time-of-day clock, tenths of a second (BCD) |
| `$09` | TOD SEC | Time-of-day seconds (BCD) |
| `$0A` | TOD MIN | Time-of-day minutes (BCD) |
| `$0B` | TOD HR | Time-of-day hours + AM/PM (BCD) |
| `$0C` | SDR | Serial shift register |
| **`$0D`** | **ICR** | **Interrupt Control/Status Register** — CIA1's drives the standard IRQ, CIA2's drives NMI (see below) |
| `$0E` | CRA | Control register A (Timer A mode, serial direction) |
| `$0F` | CRB | Control register B (Timer B mode, TOD alarm/clock mode) |

- **CIA1** (`$DC00`-`$DCFF`): keyboard matrix scanning (PRA=columns,
  PRB=rows), joystick ports, its Timer A underflow is the standard
  ~60 Hz source that drives `$EA31`'s jiffy-clock/keyboard-scan work —
  which is exactly the KERNAL continuation our IRQ hook chains into (see
  KNOWLEDGE.md).
- **CIA2** (`$DD00`-`$DDFF`): serial bus (IEC), user port, RS-232; its
  ICR (bit 7 set) triggers **NMI**, not IRQ — relevant if hooking `NMINV`
  (`$0318`) instead of `CINV`.

**Source**: [CIA, C64-Wiki](https://www.c64-wiki.com/wiki/CIA)

## BASIC V2 tokens

Every BASIC keyword tokenizes to a single byte `$80`-`$CB` when a line is
entered (this is what `petcat -w2` does for us — see KNOWLEDGE.md — but
relevant if hand-assembling or parsing tokenized BASIC directly).

| Hex | Keyword | Hex | Keyword | Hex | Keyword |
|---|---|---|---|---|---|
| `$80` | END | `$99` | PRINT | `$B2` | `=` |
| `$81` | FOR | `$9A` | CONT | `$B3` | `<` |
| `$82` | NEXT | `$9B` | LIST | `$B4` | SGN |
| `$83` | DATA | `$9C` | CLR | `$B5` | INT |
| `$84` | INPUT# | `$9D` | CMD | `$B6` | ABS |
| `$85` | INPUT | `$9E` | SYS | `$B7` | USR |
| `$86` | DIM | `$9F` | OPEN | `$B8` | FRE |
| `$87` | READ | `$A0` | CLOSE | `$B9` | POS |
| `$88` | LET | `$A1` | GET | `$BA` | SQR |
| `$89` | GOTO | `$A2` | NEW | `$BB` | RND |
| `$8A` | RUN | `$A3` | TAB( | `$BC` | LOG |
| `$8B` | IF | `$A4` | TO | `$BD` | EXP |
| `$8C` | RESTORE | `$A5` | FN | `$BE` | COS |
| `$8D` | GOSUB | `$A6` | SPC( | `$BF` | SIN |
| `$8E` | RETURN | `$A7` | THEN | `$C0` | TAN |
| `$8F` | REM | `$A8` | NOT | `$C1` | ATN |
| `$90` | STOP | `$A9` | STEP | `$C2` | PEEK |
| `$91` | ON | `$AA` | `+` | `$C3` | LEN |
| `$92` | WAIT | `$AB` | `-` | `$C4` | STR$ |
| `$93` | LOAD | `$AC` | `*` | `$C5` | VAL |
| `$94` | SAVE | `$AD` | `/` | `$C6` | ASC |
| `$95` | VERIFY | `$AE` | `^` | `$C7` | CHR$ |
| `$96` | DEF | `$AF` | AND | `$C8` | LEFT$ |
| `$97` | POKE | `$B0` | OR | `$C9` | RIGHT$ |
| `$98` | PRINT# | `$B1` | `>` | `$CA` | MID$ |
| | | | | `$CB` | GO |

**Source**: [BASIC token, C64-Wiki](https://www.c64-wiki.com/wiki/BASIC_token)

## PETSCII vs. screen codes

Two *different* encodings, both easy to confuse (we did — see
KNOWLEDGE.md's PETSCII/charset gotchas section for what this cost us in
practice):

- **PETSCII** is what KERNAL routines like `CHROUT`/`CHRIN` (and thus
  `printf`/`cputc` in cc65's C library) send/receive — Commodore's
  ASCII-derived character encoding, 0-255.
- **Screen code** is what's actually *stored in screen RAM*
  (`$0400`-`$07E7`) and indexes directly into the character generator ROM
  (glyph for screen code `n` lives at `charset_base + 8*n`). Poking a
  screen code into screen RAM and sending the *equivalent* PETSCII byte
  to `CHROUT` produce the same visible character, but the byte values
  differ.

### PETSCII → screen code conversion

| PETSCII range | Screen code range | Rule |
|---|---|---|
| `$00`-`$1F` (control codes) | `$80`-`$9F` | `+$80` |
| `$20`-`$3F` | `$20`-`$3F` | unchanged |
| `$40`-`$5F` (`@`, `A`-`Z`, ...) | `$00`-`$1F` | `-$40` |
| `$60`-`$7F` (lowercase `a`-`z` in lowercase charset) | `$40`-`$5F` | `-$20` |
| `$80`-`$9F` (control codes, shifted) | `$C0`-`$DF` | `+$40` |
| `$A0`-`$BF` | `$60`-`$7F` | `-$40` |
| `$C0`-`$DF` (uppercase, shifted charset) | `$40`-`$5F` | `-$80` |
| `$E0`-`$FE` | `$60`-`$7E` | `-$80` |
| `$FF` (π) | `$5E` | special case |

This confirms what we found empirically this session: PETSCII `$41`-`$5A`
(`A`-`Z`) → screen code `$01`-`$1A` (1-26), and PETSCII `$40` (`@`) →
screen code `$00`. `tools/screendump.py` currently only decodes screen
codes `0`, `1`-`26`, and `32`-`63` — everything else (the
graphics/lowercase range, screen codes `$40`+) is a known gap, now that
this table exists to extend it from.

**Source**: [Commodore 64 PETSCII code to screen code conversion, sta.c64.org](https://sta.c64.org/cbm64pettoscr.html)

### PETSCII control codes actually worth knowing

| Dec/Hex | Effect |
|---|---|
| 13 / `$0D` | Carriage return |
| **14 / `$0E`** | **Switch to lowercase charset** — what `crt0.s` sends before `main()`; see KNOWLEDGE.md |
| 142 / `$8E` | Switch to uppercase+graphics charset (the post-reset default) |
| 17 / `$11` | Cursor down |
| 145 / `$91` | Cursor up |
| 29 / `$1D` | Cursor right |
| 157 / `$9D` | Cursor left |
| 19 / `$13` | Home cursor |
| **147 / `$93`** | **Clear screen + home cursor** |
| 18 / `$12` | Reverse video on |
| 146 / `$92` | Reverse video off |
| 20 / `$14` | Delete/backspace |
| 148 / `$94` | Insert mode |
| 5, 28, 30, 31, 129, 149-156, 158, 159 / `$05,$1C,$1E,$1F,$81,$95-$9C,$9E,$9F` | Text color codes (white, red, green, blue, orange, brown/pink/greys/purple, yellow, cyan — full 16-color set across both blocks) |
| 133-140 / `$85`-`$8C` | F1-F8 function key codes |

Full 0-255 PETSCII and screen-code glyph charts (including the graphics
character set, which doesn't transcribe usefully to a Markdown table)
are best viewed directly at
[sta.c64.org](https://sta.c64.org/cbm64pet.html),
[pagetable.com's Ultimate Commodore Charset](https://www.pagetable.com/?p=1404),
or [c64os.com](https://c64os.com/post/c64petsciicodes) — all cross-checked
consistent with each other and with the control-code list above.

**Source**: [control character, C64-Wiki](https://www.c64-wiki.com/wiki/control_character)
