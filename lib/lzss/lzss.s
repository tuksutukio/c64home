; lzss.s -- fast 6502 decompressor for cbm-joy's byte-oriented LZSS format.
; See tools/lzss.py for the format spec and the dev-machine compressor;
; compression cost doesn't matter (runs on the Mac), decompression speed
; does (this is the actual "present screens fast" performance path), so
; this side is hand-written asm rather than C.
;
; Format: [2-byte LE uncompressed length][token groups]. Each group = 1
; control byte (8 flag bits, LSB-first) + up to 8 tokens. Flag bit 1 =
; next token is 1 literal byte. Flag bit 0 = next token is a 2-byte match
; [offset][length]: distance = offset+1 (1-256), length = length byte
; directly (2-255). Decompression stops once the length-prefixed byte
; count has been produced.
;
; Match copies must run low-index-to-high (not the usual backward/BPL
; countdown trick): distance can be less than length (e.g. distance=1,
; length=200 for a run of 200 identical bytes), where each newly-written
; byte is itself a valid source for a later byte in the *same* copy.
; Forward order is what makes that self-referential expansion correct;
; backward order would read still-uninitialized destination bytes.
;
; Zero page: cc65's stock c64.cfg gives the "ZP" memory area exactly
; zpspace (26) bytes, all already claimed by the C runtime itself (see
; zeropage.inc) -- there's no free zero page to declare new (zp),y
; pointers in without guessing into undocumented BASIC/KERNAL territory.
; So this reuses the runtime's own general-purpose scratch pointers
; (ptr1/ptr2/ptr3) instead of declaring any new ones: the C-facing
; lzss_src/lzss_dst live in ordinary (non-zp) BSS, and get copied into
; ptr1/ptr2 once at routine entry.
;
; C interface (globals, not stack-passed args -- deliberately sidesteps
; cc65's calling convention entirely):
;   extern unsigned int lzss_src, lzss_dst;
;   extern void lzss_decompress(void);
;   lzss_src = (unsigned)compressed_data; lzss_dst = dest_address;
;   lzss_decompress();

.include "zeropage.inc"

.segment "BSS"
_lzss_src:      .res 2   ; C-facing: compressed stream start address
_lzss_dst:      .res 2   ; C-facing: output destination address
lzss_remain:    .res 2   ; bytes of output still to produce
lzss_flags:     .res 1   ; current control byte, shifted right per token
lzss_bitcount:  .res 1   ; flag bits left in lzss_flags before reload
lzss_offset:    .res 1   ; scratch: this match's offset byte
lzss_length:    .res 1   ; scratch: this match's length byte

.export _lzss_src
.export _lzss_dst
.export _lzss_decompress

.segment "CODE"

; ptr1 = compressed stream read pointer (was _lzss_src)
; ptr2 = output write pointer (was _lzss_dst)
; ptr3 = match source pointer (dst - distance), internal only

_lzss_decompress:
        lda     _lzss_src
        sta     ptr1
        lda     _lzss_src+1
        sta     ptr1+1
        lda     _lzss_dst
        sta     ptr2
        lda     _lzss_dst+1
        sta     ptr2+1

        ; read 2-byte LE length prefix, advance ptr1 past it
        ldy     #0
        lda     (ptr1),y
        sta     lzss_remain
        iny
        lda     (ptr1),y
        sta     lzss_remain+1
        lda     ptr1
        clc
        adc     #2
        sta     ptr1
        lda     ptr1+1
        adc     #0
        sta     ptr1+1

        lda     #0
        sta     lzss_bitcount

ld_main_loop:
        lda     lzss_remain
        ora     lzss_remain+1
        bne     ld_not_done
        jmp     ld_done
ld_not_done:

        lda     lzss_bitcount
        bne     ld_have_bits
        ldy     #0
        lda     (ptr1),y
        sta     lzss_flags
        inc     ptr1
        bne     :+
        inc     ptr1+1
:       lda     #8
        sta     lzss_bitcount

ld_have_bits:
        lsr     lzss_flags
        dec     lzss_bitcount
        bcs     ld_literal

        ; --- match: read [offset][length], advance ptr1 by 2 ---
        ldy     #0
        lda     (ptr1),y
        sta     lzss_offset
        iny
        lda     (ptr1),y
        sta     lzss_length
        lda     ptr1
        clc
        adc     #2
        sta     ptr1
        lda     ptr1+1
        adc     #0
        sta     ptr1+1

        ; ptr3 = dst - offset - 1 = (dst - 1) - offset
        sec
        lda     ptr2
        sbc     lzss_offset
        sta     ptr3
        lda     ptr2+1
        sbc     #0
        sta     ptr3+1
        lda     ptr3
        bne     :+
        dec     ptr3+1
:       dec     ptr3

        ; copy lzss_length bytes from (ptr3) to (ptr2), forward (see file
        ; header: must NOT be a backward/BPL countdown loop)
        ldy     #0
ld_copy_loop:
        lda     (ptr3),y
        sta     (ptr2),y
        iny
        cpy     lzss_length
        bne     ld_copy_loop

        ; advance ptr2, remain -= length (single 16-bit adjust, not
        ; per-byte)
        lda     ptr2
        clc
        adc     lzss_length
        sta     ptr2
        lda     ptr2+1
        adc     #0
        sta     ptr2+1

        lda     lzss_remain
        sec
        sbc     lzss_length
        sta     lzss_remain
        lda     lzss_remain+1
        sbc     #0
        sta     lzss_remain+1
        jmp     ld_main_loop

ld_literal:
        ldy     #0
        lda     (ptr1),y
        sta     (ptr2),y
        inc     ptr1
        bne     :+
        inc     ptr1+1
:       inc     ptr2
        bne     :+
        inc     ptr2+1
:       lda     lzss_remain
        bne     :+
        dec     lzss_remain+1
:       dec     lzss_remain
        jmp     ld_main_loop

ld_done:
        rts
