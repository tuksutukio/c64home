; Hello world in plain 6502 assembly that also hooks the IRQ vector:
; every hardware IRQ increments the VIC-II border color register.
;
; The handler is installed on the KERNAL's RAM IRQ vector ($0314/$0315,
; "CINV") rather than the hardware vector, and chains to the stock KERNAL
; IRQ continuation at $EA31 afterwards -- so keyboard scanning, the jiffy
; clock, and cursor blink all keep working normally. INC on a memory
; address touches no registers, so no save/restore is needed around it.
;
; Build: cl65 -t c64 -C c64-asm.cfg -u __EXEHDR__ -o build/irq_border.prg src/irq_border.s
; Run:   ru64 <host> run build/irq_border.prg
;
; (-u __EXEHDR__ against c64-asm.cfg adds the small BASIC "SYS" header so
; the program can be started with RUN/DMA-load autostart, jumping straight
; to the start of the CODE segment below -- no C runtime involved.)
;
; The program prints a message and returns to BASIC immediately, but the
; border keeps cycling forever afterwards -- proof the IRQ hook outlives
; the program that installed it.

CHROUT     := $FFD2   ; KERNAL: output character in .A
IRQ_VEC_LO := $0314
IRQ_VEC_HI := $0315
KERNAL_IRQ := $EA31    ; KERNAL: stock IRQ continuation (keyboard/jiffy/cursor)
BORDER     := $D020    ; VIC-II border color register

.segment "CODE"

Start:
        ldx     #0
print_loop:
        lda     message,x
        beq     install_irq
        jsr     CHROUT
        inx
        jmp     print_loop

install_irq:
        sei                     ; avoid a mid-update IRQ landing on half a vector
        lda     #<irq_handler
        sta     IRQ_VEC_LO
        lda     #>irq_handler
        sta     IRQ_VEC_HI
        cli
        rts                     ; back to BASIC; IRQ hook keeps running

irq_handler:
        inc     BORDER
        jmp     KERNAL_IRQ      ; chain: let KERNAL finish the interrupt

message:
        ; cc65's -t c64 charset translation maps lowercase source letters to
        ; the PETSCII codes that render as uppercase on screen (the normal
        ; C64 convention) -- uppercase source letters map to the shifted
        ; graphics range instead, so lowercase here is deliberate.
        .byte   "hello world, irq hooked!", 13, 0
