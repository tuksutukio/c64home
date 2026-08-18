# 6502/6510 opcode reference

Static instruction-set reference (documented + undocumented/illegal
opcodes). Doesn't change — see **[C64-REFERENCE.md](C64-REFERENCE.md)**
for C64-specific hardware facts (memory map, registers, KERNAL, BASIC
tokens) and **[KNOWLEDGE.md](KNOWLEDGE.md)** for things discovered the
hard way building this repo's pipeline. This file is lookup tables, not
an essay.

The 6510 (the C64's CPU) has an **identical instruction set** to the NMOS
6502 — the only difference is the extra on-chip 8-bit I/O port mapped at
`$00`/`$01` (already documented in C64-REFERENCE.md's memory map), which
isn't an instruction-set change at all. Everything below applies to both.

## Addressing mode key

| Abbr | Mode | Example |
|---|---|---|
| impl | Implied (no operand) | `CLC` |
| A | Accumulator | `ASL A` |
| imm | Immediate | `LDA #$10` |
| zp | Zero page | `LDA $10` |
| zp,X | Zero page indexed, X | `LDA $10,X` |
| zp,Y | Zero page indexed, Y | `LDX $10,Y` |
| abs | Absolute | `LDA $1000` |
| abs,X | Absolute indexed, X | `LDA $1000,X` |
| abs,Y | Absolute indexed, Y | `LDA $1000,Y` |
| ind | Indirect (JMP only) | `JMP ($1000)` |
| (ind,X) | Indexed indirect | `LDA ($10,X)` |
| (ind),Y | Indirect indexed | `LDA ($10),Y` |
| rel | Relative (branches) | `BEQ label` |

Flags column order throughout: **N Z C I D V**. `+` = affected/set per
result, `-` = unaffected, `0`/`1` = unconditionally cleared/set,
`(stack)` = restored from the stack (`PLP`, `RTI`).

Cycle notes: `*` = +1 cycle if a page boundary is crossed; `**` = +1 if
branch taken (same page), +2 if branch taken to a different page;
`***` = NMOS `JMP (abs)` has the famous **page-boundary-crossing bug**
(if the pointer is at `$xxFF`, the high byte is fetched from `$xx00`, not
`$(xx+1)00`) — CMOS 6502 variants fixed this, NMOS 6502/6510 has not.

**Source**: [6502 Instruction Set, masswerk.at](https://www.masswerk.at/6502/6502_instruction_set.html)

## Documented instruction set

### Load / Store

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| LDA | imm | `A9` | 2 | 2 | + + - - - - |
| LDA | zp | `A5` | 2 | 3 | + + - - - - |
| LDA | zp,X | `B5` | 2 | 4 | + + - - - - |
| LDA | abs | `AD` | 3 | 4 | + + - - - - |
| LDA | abs,X | `BD` | 3 | 4* | + + - - - - |
| LDA | abs,Y | `B9` | 3 | 4* | + + - - - - |
| LDA | (ind,X) | `A1` | 2 | 6 | + + - - - - |
| LDA | (ind),Y | `B1` | 2 | 5* | + + - - - - |
| LDX | imm | `A2` | 2 | 2 | + + - - - - |
| LDX | zp | `A6` | 2 | 3 | + + - - - - |
| LDX | zp,Y | `B6` | 2 | 4 | + + - - - - |
| LDX | abs | `AE` | 3 | 4 | + + - - - - |
| LDX | abs,Y | `BE` | 3 | 4* | + + - - - - |
| LDY | imm | `A0` | 2 | 2 | + + - - - - |
| LDY | zp | `A4` | 2 | 3 | + + - - - - |
| LDY | zp,X | `B4` | 2 | 4 | + + - - - - |
| LDY | abs | `AC` | 3 | 4 | + + - - - - |
| LDY | abs,X | `BC` | 3 | 4* | + + - - - - |
| STA | zp | `85` | 2 | 3 | - - - - - - |
| STA | zp,X | `95` | 2 | 4 | - - - - - - |
| STA | abs | `8D` | 3 | 4 | - - - - - - |
| STA | abs,X | `9D` | 3 | 5 | - - - - - - |
| STA | abs,Y | `99` | 3 | 5 | - - - - - - |
| STA | (ind,X) | `81` | 2 | 6 | - - - - - - |
| STA | (ind),Y | `91` | 2 | 6 | - - - - - - |
| STX | zp | `86` | 2 | 3 | - - - - - - |
| STX | zp,Y | `96` | 2 | 4 | - - - - - - |
| STX | abs | `8E` | 3 | 4 | - - - - - - |
| STY | zp | `84` | 2 | 3 | - - - - - - |
| STY | zp,X | `94` | 2 | 4 | - - - - - - |
| STY | abs | `8C` | 3 | 4 | - - - - - - |

### Register transfer

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| TAX | impl | `AA` | 1 | 2 | + + - - - - |
| TAY | impl | `A8` | 1 | 2 | + + - - - - |
| TXA | impl | `8A` | 1 | 2 | + + - - - - |
| TYA | impl | `98` | 1 | 2 | + + - - - - |
| TSX | impl | `BA` | 1 | 2 | + + - - - - |
| TXS | impl | `9A` | 1 | 2 | - - - - - - |

### Stack

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| PHA | impl | `48` | 1 | 3 | - - - - - - |
| PHP | impl | `08` | 1 | 3 | - - - - - - |
| PLA | impl | `68` | 1 | 4 | + + - - - - |
| PLP | impl | `28` | 1 | 4 | (stack) |

### Logical

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| AND | imm | `29` | 2 | 2 | + + - - - - |
| AND | zp | `25` | 2 | 3 | + + - - - - |
| AND | zp,X | `35` | 2 | 4 | + + - - - - |
| AND | abs | `2D` | 3 | 4 | + + - - - - |
| AND | abs,X | `3D` | 3 | 4* | + + - - - - |
| AND | abs,Y | `39` | 3 | 4* | + + - - - - |
| AND | (ind,X) | `21` | 2 | 6 | + + - - - - |
| AND | (ind),Y | `31` | 2 | 5* | + + - - - - |
| EOR | imm | `49` | 2 | 2 | + + - - - - |
| EOR | zp | `45` | 2 | 3 | + + - - - - |
| EOR | zp,X | `55` | 2 | 4 | + + - - - - |
| EOR | abs | `4D` | 3 | 4 | + + - - - - |
| EOR | abs,X | `5D` | 3 | 4* | + + - - - - |
| EOR | abs,Y | `59` | 3 | 4* | + + - - - - |
| EOR | (ind,X) | `41` | 2 | 6 | + + - - - - |
| EOR | (ind),Y | `51` | 2 | 5* | + + - - - - |
| ORA | imm | `09` | 2 | 2 | + + - - - - |
| ORA | zp | `05` | 2 | 3 | + + - - - - |
| ORA | zp,X | `15` | 2 | 4 | + + - - - - |
| ORA | abs | `0D` | 3 | 4 | + + - - - - |
| ORA | abs,X | `1D` | 3 | 4* | + + - - - - |
| ORA | abs,Y | `19` | 3 | 4* | + + - - - - |
| ORA | (ind,X) | `01` | 2 | 6 | + + - - - - |
| ORA | (ind),Y | `11` | 2 | 5* | + + - - - - |
| BIT | zp | `24` | 2 | 3 | M7 + - - - M6 |
| BIT | abs | `2C` | 3 | 4 | M7 + - - - M6 |

`BIT` is the odd one out: N and V are set from bits 7 and 6 of the
*memory operand* (not the AND result), Z is set from `A AND M`.

### Arithmetic / compare

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| ADC | imm | `69` | 2 | 2 | + + + - - + |
| ADC | zp | `65` | 2 | 3 | + + + - - + |
| ADC | zp,X | `75` | 2 | 4 | + + + - - + |
| ADC | abs | `6D` | 3 | 4 | + + + - - + |
| ADC | abs,X | `7D` | 3 | 4* | + + + - - + |
| ADC | abs,Y | `79` | 3 | 4* | + + + - - + |
| ADC | (ind,X) | `61` | 2 | 6 | + + + - - + |
| ADC | (ind),Y | `71` | 2 | 5* | + + + - - + |
| SBC | imm | `E9` | 2 | 2 | + + + - - + |
| SBC | zp | `E5` | 2 | 3 | + + + - - + |
| SBC | zp,X | `F5` | 2 | 4 | + + + - - + |
| SBC | abs | `ED` | 3 | 4 | + + + - - + |
| SBC | abs,X | `FD` | 3 | 4* | + + + - - + |
| SBC | abs,Y | `F9` | 3 | 4* | + + + - - + |
| SBC | (ind,X) | `E1` | 2 | 6 | + + + - - + |
| SBC | (ind),Y | `F1` | 2 | 5* | + + + - - + |
| CMP | imm | `C9` | 2 | 2 | + + + - - - |
| CMP | zp | `C5` | 2 | 3 | + + + - - - |
| CMP | zp,X | `D5` | 2 | 4 | + + + - - - |
| CMP | abs | `CD` | 3 | 4 | + + + - - - |
| CMP | abs,X | `DD` | 3 | 4* | + + + - - - |
| CMP | abs,Y | `D9` | 3 | 4* | + + + - - - |
| CMP | (ind,X) | `C1` | 2 | 6 | + + + - - - |
| CMP | (ind),Y | `D1` | 2 | 5* | + + + - - - |
| CPX | imm | `E0` | 2 | 2 | + + + - - - |
| CPX | zp | `E4` | 2 | 3 | + + + - - - |
| CPX | abs | `EC` | 3 | 4 | + + + - - - |
| CPY | imm | `C0` | 2 | 2 | + + + - - - |
| CPY | zp | `C4` | 2 | 3 | + + + - - - |
| CPY | abs | `CC` | 3 | 4 | + + + - - - |

`ADC`/`SBC` also depend on the **D** (decimal) flag for BCD mode — see
KNOWLEDGE.md if this repo ever does BCD arithmetic; not covered further
here since we haven't used it.

### Increment / decrement

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| INC | zp | `E6` | 2 | 5 | + + - - - - |
| INC | zp,X | `F6` | 2 | 6 | + + - - - - |
| INC | abs | `EE` | 3 | 6 | + + - - - - |
| INC | abs,X | `FE` | 3 | 7 | + + - - - - |
| INX | impl | `E8` | 1 | 2 | + + - - - - |
| INY | impl | `C8` | 1 | 2 | + + - - - - |
| DEC | zp | `C6` | 2 | 5 | + + - - - - |
| DEC | zp,X | `D6` | 2 | 6 | + + - - - - |
| DEC | abs | `CE` | 3 | 6 | + + - - - - |
| DEC | abs,X | `DE` | 3 | 7 | + + - - - - |
| DEX | impl | `CA` | 1 | 2 | + + - - - - |
| DEY | impl | `88` | 1 | 2 | + + - - - - |

`INC $D020` in our `irq_border.s` example is this table's `INC abs`
(`EE`) — 6 cycles, touches no registers, which is exactly why it's safe
to use inside an IRQ handler without saving A/X/Y (see KNOWLEDGE.md's IRQ
pattern).

### Shifts / rotates

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| ASL | A | `0A` | 1 | 2 | + + + - - - |
| ASL | zp | `06` | 2 | 5 | + + + - - - |
| ASL | zp,X | `16` | 2 | 6 | + + + - - - |
| ASL | abs | `0E` | 3 | 6 | + + + - - - |
| ASL | abs,X | `1E` | 3 | 7 | + + + - - - |
| LSR | A | `4A` | 1 | 2 | 0 + + - - - |
| LSR | zp | `46` | 2 | 5 | 0 + + - - - |
| LSR | zp,X | `56` | 2 | 6 | 0 + + - - - |
| LSR | abs | `4E` | 3 | 6 | 0 + + - - - |
| LSR | abs,X | `5E` | 3 | 7 | 0 + + - - - |
| ROL | A | `2A` | 1 | 2 | + + + - - - |
| ROL | zp | `26` | 2 | 5 | + + + - - - |
| ROL | zp,X | `36` | 2 | 6 | + + + - - - |
| ROL | abs | `2E` | 3 | 6 | + + + - - - |
| ROL | abs,X | `3E` | 3 | 7 | + + + - - - |
| ROR | A | `6A` | 1 | 2 | + + + - - - |
| ROR | zp | `66` | 2 | 5 | + + + - - - |
| ROR | zp,X | `76` | 2 | 6 | + + + - - - |
| ROR | abs | `6E` | 3 | 6 | + + + - - - |
| ROR | abs,X | `7E` | 3 | 7 | + + + - - - |

### Jumps / calls

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| JMP | abs | `4C` | 3 | 3 | - - - - - - |
| JMP | ind | `6C` | 3 | 5*** | - - - - - - |
| JSR | abs | `20` | 3 | 6 | - - - - - - |
| RTS | impl | `60` | 1 | 6 | - - - - - - |

Our IRQ hook (`jmp $ea31` in `irq_border.s`) uses `JMP abs` (`4C`) — the
NMOS indirect-jump page-boundary bug (`6C`, `***` above) doesn't apply
since it's a direct jump, not through a pointer.

### Branches (all relative, `rel` mode)

| Mnemonic | Opcode | Bytes | Cycles | Condition |
|---|---|---|---|---|
| BCC | `90` | 2 | 2** | Branch if C=0 |
| BCS | `B0` | 2 | 2** | Branch if C=1 |
| BEQ | `F0` | 2 | 2** | Branch if Z=1 |
| BNE | `D0` | 2 | 2** | Branch if Z=0 |
| BMI | `30` | 2 | 2** | Branch if N=1 |
| BPL | `10` | 2 | 2** | Branch if N=0 |
| BVC | `50` | 2 | 2** | Branch if V=0 |
| BVS | `70` | 2 | 2** | Branch if V=1 |

None of these affect flags themselves; they only *test* flags set by a
prior instruction.

### Status flag instructions

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| CLC | impl | `18` | 1 | 2 | - - 0 - - - |
| SEC | impl | `38` | 1 | 2 | - - 1 - - - |
| CLI | impl | `58` | 1 | 2 | - - - 0 - - |
| SEI | impl | `78` | 1 | 2 | - - - 1 - - |
| CLD | impl | `D8` | 1 | 2 | - - - - 0 - |
| SED | impl | `F8` | 1 | 2 | - - - - 1 - |
| CLV | impl | `B8` | 1 | 2 | - - - - - 0 |

`sei`/`cli` in our IRQ-install sequence (KNOWLEDGE.md) are `78`/`58`
above — bracketing the two-byte vector write so a real IRQ can't land
mid-update.

### System

| Mnemonic | Mode | Opcode | Bytes | Cycles | Flags |
|---|---|---|---|---|---|
| BRK | impl | `00` | 1 | 7 | - - - 1 - - |
| RTI | impl | `40` | 1 | 6 | (stack) |
| NOP | impl | `EA` | 1 | 2 | - - - - - - |

**Source for all documented tables above**: [6502 Instruction Set, masswerk.at](https://www.masswerk.at/6502/6502_instruction_set.html)

## Undocumented / illegal opcodes

The 6502/6510 only decodes 8 bits of opcode, but the documented
instruction set above only defines 151 of the 256 possible values. The
rest do *something* deterministic on real NMOS silicon (a side effect of
how the decode logic is wired), and demos/cracktros have relied on the
stable ones for decades. **Not CPU-architecture-guaranteed behavior** —
treat this whole section with more caution than the documented table
above, and see the stability warnings at the end.

Flags columns below are *derived* from each opcode's documented
constituent operation (e.g. `SLO` = `ASL` then `ORA`, so it carries
`ASL`'s C and the final `ORA` result's N/Z) — masswerk.at's own
undocumented-opcode tables confirm this derivation for the entries they
list explicitly (`ALR`, `ANC`, `ANE`, `ARR`, `DCP`, `LAX`, `RLA`, `SAX`);
oxyron.de's opcode matrix (the primary source for the full byte/cycle
tables below) doesn't tabulate flags at all. Where the two disagree on
naming, both common mnemonics are given.

### Read-Modify-Write combos (shift/rotate + logic op, same operand)

| Mnemonic | Mode | Opcode | Bytes | Cycles | Effective op | Flags |
|---|---|---|---|---|---|---|
| SLO (ASO) | (ind,X) | `03` | 2 | 8 | ASL then ORA A | + + + - - - |
| SLO | zp | `07` | 2 | 5 | ASL then ORA A | + + + - - - |
| SLO | zp,X | `17` | 2 | 6 | ASL then ORA A | + + + - - - |
| SLO | abs | `0F` | 3 | 6 | ASL then ORA A | + + + - - - |
| SLO | abs,X | `1F` | 3 | 7 | ASL then ORA A | + + + - - - |
| SLO | abs,Y | `1B` | 3 | 7 | ASL then ORA A | + + + - - - |
| RLA | (ind,X) | `23` | 2 | 8 | ROL then AND A | + + + - - - |
| RLA | zp | `27` | 2 | 5 | ROL then AND A | + + + - - - |
| RLA | zp,X | `37` | 2 | 6 | ROL then AND A | + + + - - - |
| RLA | abs | `2F` | 3 | 6 | ROL then AND A | + + + - - - |
| RLA | abs,X | `3F` | 3 | 7 | ROL then AND A | + + + - - - |
| RLA | abs,Y | `3B` | 3 | 7 | ROL then AND A | + + + - - - |
| SRE (LSE) | (ind,X) | `43` | 2 | 8 | LSR then EOR A | + + + - - - |
| SRE | zp | `47` | 2 | 5 | LSR then EOR A | + + + - - - |
| SRE | zp,X | `57` | 2 | 6 | LSR then EOR A | + + + - - - |
| SRE | abs | `4F` | 3 | 6 | LSR then EOR A | + + + - - - |
| SRE | abs,X | `5F` | 3 | 7 | LSR then EOR A | + + + - - - |
| SRE | abs,Y | `5B` | 3 | 7 | LSR then EOR A | + + + - - - |
| RRA | (ind,X) | `63` | 2 | 8 | ROR then ADC A | + + + - - + |
| RRA | zp | `67` | 2 | 5 | ROR then ADC A | + + + - - + |
| RRA | zp,X | `77` | 2 | 6 | ROR then ADC A | + + + - - + |
| RRA | abs | `6F` | 3 | 6 | ROR then ADC A | + + + - - + |
| RRA | abs,X | `7F` | 3 | 7 | ROR then ADC A | + + + - - + |
| RRA | abs,Y | `7B` | 3 | 7 | ROR then ADC A | + + + - - + |
| DCP (DCM) | (ind,X) | `C3` | 2 | 8 | DEC then CMP A | + + + - - - |
| DCP | zp | `C7` | 2 | 5 | DEC then CMP A | + + + - - - |
| DCP | zp,X | `D7` | 2 | 6 | DEC then CMP A | + + + - - - |
| DCP | abs | `CF` | 3 | 6 | DEC then CMP A | + + + - - - |
| DCP | abs,X | `DF` | 3 | 7 | DEC then CMP A | + + + - - - |
| DCP | abs,Y | `DB` | 3 | 7 | DEC then CMP A | + + + - - - |
| ISC (ISB/INS) | (ind,X) | `E3` | 2 | 8 | INC then SBC A | + + + - - + |
| ISC | zp | `E7` | 2 | 5 | INC then SBC A | + + + - - + |
| ISC | zp,X | `F7` | 2 | 6 | INC then SBC A | + + + - - + |
| ISC | abs | `EF` | 3 | 6 | INC then SBC A | + + + - - + |
| ISC | abs,X | `FF` | 3 | 7 | INC then SBC A | + + + - - + |
| ISC | abs,Y | `FB` | 3 | 7 | INC then SBC A | + + + - - + |

### Store combos

| Mnemonic | Mode | Opcode | Bytes | Cycles | Effective op | Stability |
|---|---|---|---|---|---|---|
| SAX (AXS/AAX) | (ind,X) | `83` | 2 | 6 | `M = A AND X` | Stable |
| SAX | zp | `87` | 2 | 3 | `M = A AND X` | Stable |
| SAX | zp,Y | `97` | 2 | 4 | `M = A AND X` | Stable |
| SAX | abs | `8F` | 3 | 4 | `M = A AND X` | Stable |
| SHA (AHX/AXA) | (ind),Y | `93` | 2 | 6 | `M = A AND X AND (high byte+1)` | **Unstable** |
| SHA | abs,Y | `9F` | 3 | 5 | `M = A AND X AND (high byte+1)` | **Unstable** |
| SHY (A11/SYA) | abs,X | `9C` | 3 | 5 | `M = Y AND (high byte+1)` | **Unstable** |
| SHX (A11/SXA) | abs,Y | `9E` | 3 | 5 | `M = X AND (high byte+1)` | **Unstable** |
| TAS (XAS/SHS) | abs,Y | `9B` | 3 | 5 | `S = A AND X; M = S AND (high byte+1)` | **Unstable** |

None of the store-combo opcodes affect the processor status flags.

### Load combos

| Mnemonic | Mode | Opcode | Bytes | Cycles | Effective op | Flags | Stability |
|---|---|---|---|---|---|---|---|
| LAX | (ind,X) | `A3` | 2 | 6 | `A = X = M` | + + - - - - | Stable |
| LAX | zp | `A7` | 2 | 3 | `A = X = M` | + + - - - - | Stable |
| LAX | zp,Y | `B7` | 2 | 4 | `A = X = M` | + + - - - - | Stable |
| LAX | abs | `AF` | 3 | 4 | `A = X = M` | + + - - - - | Stable |
| LAX | abs,Y | `BF` | 3 | 4* | `A = X = M` | + + - - - - | Stable |
| LAS (LAR) | abs,Y | `BB` | 3 | 4* | `A = X = S = M AND S` | + + - - - - | Reportedly unreliable |

### Immediate-mode combos

| Mnemonic | Opcode | Bytes | Cycles | Effective op | Flags | Stability |
|---|---|---|---|---|---|---|
| ANC | `0B` | 2 | 2 | `A = A AND #imm`; C = bit 7 of result | + + + - - - | Stable |
| ANC | `2B` | 2 | 2 | same as `0B` (duplicate opcode) | + + + - - - | Stable |
| ALR (ASR) | `4B` | 2 | 2 | `A = (A AND #imm)`, then `LSR A` | + + + - - - | Stable |
| ARR | `6B` | 2 | 2 | `A = (A AND #imm)`, then `ROR A` — C/V set unusually: **bit 0 does not feed C; C and V come from bits 6/5 of the result instead** | + + + - - + | Stable but non-obvious |
| ANE (XAA) | `8B` | 2 | 2 | `A = (A OR magic) AND X AND #imm` | + + - - - - | **Highly unstable — DO NOT USE.** `magic` is an unpredictable constant that varies by chip batch/temperature. |
| LAX | `AB` | 2 | 2 | `A = X = (A OR magic) AND #imm` | + + - - - - | **Unstable** — same `magic`-constant issue as ANE; reported to behave differently on C64-II boards |
| SBX (AXS) | `CB` | 2 | 2 | `X = (A AND X) - #imm` (no borrow in) | + + + - - - | Stable |
| SBC | `EB` | 2 | 2 | identical to documented `SBC #imm` (`E9`) — a pure duplicate opcode, no new behavior | + + + - - + | Stable (it's just SBC) |

### No-ops (many opcodes, all "fetch and discard, no effect")

| Mnemonic | Mode | Opcodes | Bytes | Cycles |
|---|---|---|---|---|
| NOP | impl | `1A`, `3A`, `5A`, `7A`, `DA`, `FA` | 1 | 2 |
| NOP (DOP) | imm | `80`, `82`, `89`, `C2`, `E2` | 2 | 2 |
| NOP (DOP) | zp | `04`, `44`, `64` | 2 | 3 |
| NOP (DOP) | zp,X | `14`, `34`, `54`, `74`, `D4`, `F4` | 2 | 4 |
| NOP (TOP) | abs | `0C` | 3 | 4 |
| NOP (TOP) | abs,X | `1C`, `3C`, `5C`, `7C`, `DC`, `FC` | 3 | 4* |

The single-byte implied-mode NOPs (`1A`/`3A`/`5A`/`7A`/`DA`/`FA`) are
well-established and stable, and are the ones most commonly used in real
code (cycle-padding, self-modifying-code tricks) — worth calling out
since one lossy web-summarization pass while researching this file
initially missed them entirely; a direct search cross-check confirmed
they're real, standard, and reliable. `DOP`/`TOP` ("double/triple-byte
NOP") are alternate names for the multi-byte forms, seen in some sources.

### Halt

| Mnemonic | Mode | Opcodes | Effect |
|---|---|---|---|
| JAM (KIL/HLT) | impl | `02`, `12`, `22`, `32`, `42`, `52`, `62`, `72`, `92`, `B2`, `D2`, `F2` | Locks the CPU — halts and stops responding to interrupts (not even RESET recovers on some, only power-cycle). Data bus floats/reads as `$FF` on most implementations. **Never execute these deliberately** except to intentionally crash/trap. |

### Stability summary

| Mnemonic(s) | Status |
|---|---|
| SLO, RLA, SRE, RRA, DCP, ISC, SAX, LAX (non-imm), ANC, ALR, ARR, SBX, all NOP forms | Stable, well-documented, safe to rely on for NMOS 6502/6510 |
| SHA, SHX, SHY, TAS | **Unstable** — the "AND with high-byte+1" behavior is known to misbehave specifically around page-boundary-crossing indexed addressing; avoid unless the exact chip/behavior has been tested |
| LAS | Reportedly unreliable, less catastrophically so than the above |
| ANE (XAA), LAX (`AB` imm only) | **Highly unstable** — involve an unpredictable "magic constant" that varies by chip; multiple sources explicitly say do not use these in anything relying on deterministic behavior |
| JAM/KIL (all 12 opcodes) | Not "unstable" so much as intentionally catastrophic — locks the CPU |

**Sources**: [Extra Instructions Of The 65XX Series CPU, oxyron.de](https://www.oxyron.de/html/opcodes02.html) (primary source for the full byte/cycle tables); [6502 Instruction Set — undocumented section, masswerk.at](https://www.masswerk.at/6502/6502_instruction_set.html); cross-checked against [NESdev Wiki: unofficial opcodes](https://www.nesdev.org/wiki/CPU_unofficial_opcodes) (the 2A03/6502 core in the NES makes this a rigorously-maintained independent source) specifically for the single-byte NOP family, where an initial web-fetch pass gave an incorrect (incomplete) answer that a follow-up search corrected.
