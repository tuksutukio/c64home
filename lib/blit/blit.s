; blit.s -- fast fixed-size (1000-byte) raw memory copy, for moving a
; decompressed screen/color buffer onto the real $0400/$D800 in as few
; cycles as possible (see lzss.s for why decompressing directly into live
; screen memory causes visible tearing -- this is the fix: decompress to
; an off-screen buffer, then blit it across in one tight pass).
;
; 1000 bytes = 3 full 256-byte pages + a 232-byte tail. Uses Y-register
; page-wraparound addressing (only the pointers' high bytes need
; incrementing, once per 256 bytes) rather than a 16-bit increment per
; byte -- the standard fast 6502 block-copy shape.
;
; C interface (globals, same pattern as lzss.s):
;   extern unsigned int copy_src, copy_dst;
;   extern void fast_copy1000(void);
;   copy_src = ...; copy_dst = ...; fast_copy1000();

.include "zeropage.inc"

.segment "BSS"
_copy_src:      .res 2
_copy_dst:      .res 2

.export _copy_src
.export _copy_dst
.export _fast_copy1000

.segment "CODE"

_fast_copy1000:
        lda     _copy_src
        sta     ptr1
        lda     _copy_src+1
        sta     ptr1+1
        lda     _copy_dst
        sta     ptr2
        lda     _copy_dst+1
        sta     ptr2+1

        ldx     #3             ; 3 full 256-byte pages
fc_page_loop:
        ldy     #0
fc_byte_loop:
        lda     (ptr1),y
        sta     (ptr2),y
        iny
        bne     fc_byte_loop
        inc     ptr1+1
        inc     ptr2+1
        dex
        bne     fc_page_loop

        ldy     #0             ; final partial page: 1000 - 3*256 = 232
fc_tail_loop:
        lda     (ptr1),y
        sta     (ptr2),y
        iny
        cpy     #232
        bne     fc_tail_loop

        rts
