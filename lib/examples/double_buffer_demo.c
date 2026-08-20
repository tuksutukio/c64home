/* double_buffer_demo.c -- usage pattern for lib/lzss + lib/blit together:
 * decompress two LZSS-compressed screen/color pairs off-screen, then swap
 * between them with zero tearing using VIC-II screen-pointer double
 * buffering (a single $D018 write) plus a SEI/CLI-wrapped color blit
 * (color RAM has no hardware double-buffer, so it still needs a real
 * copy on every swap -- see KNOWLEDGE.md's VIC-II double-buffering
 * section for why).
 *
 * TEMPLATE, not a drop-in program: comp_screen_a/b and comp_color_a/b
 * below are placeholders for *your* project's own LZSS-compressed
 * screen/color RAM dumps (produced via lib/lzss/lzss.py --asm) -- this
 * file ships the pattern, not any artwork. Adapted from cbm-joy's
 * src/test_lzss.c, which is where this pattern was first built and
 * verified end to end on real hardware (see KNOWLEDGE.md's "Contributing
 * back" history).
 *
 * $2400 is chosen for screen B to stay clear of the VIC-II's
 * character-ROM shadow at bank-relative $1000-$1FFF (in VIC bank 0/2,
 * that range shows the built-in char ROM rather than RAM regardless of
 * underlying content -- exact scope, e.g. whether it's per access-type
 * or per raw address range, not yet pinned down, see KNOWLEDGE.md) --
 * adjust if your project's memory layout needs a different bank/offset,
 * just avoid that shadow range and your own code/data/sprite blocks.
 *
 * $D018 bit layout: bits7-4 = VM13-10 (screen ptr, unit $400), bits3-1 =
 * CB13-11 (char ptr, unit $800), bit0 unused (mirrored as 1 here to
 * match the KERNAL's own observed convention) -- see C64-REFERENCE.md's
 * $D018 entry for the full table and more worked examples.
 */

#include <c64.h>
#include <cbm.h>
#include <6502.h>

#define SCREEN_A        ((unsigned int)0x0400)
#define SCREEN_B        ((unsigned int)0x2400)
#define SCRATCH_COLOR_A ((unsigned int)0xC000)
#define SCRATCH_COLOR_B ((unsigned int)0xC400)

#define D018_SCREEN_A   0x15   /* VM=1 (screen $0400), CB=2 ($1000 charset) */
#define D018_SCREEN_B   0x95   /* VM=9 (screen $2400), same charset */

#define SWAP_FRAMES 100   /* ~2s per side at ~50Hz PAL; adjust to taste */

/* Replace with your own project's compressed assets (see
 * lib/lzss/lzss.py's --asm mode for producing these from a real
 * screen/color RAM capture). */
extern unsigned char comp_screen_a[];
extern unsigned char comp_screen_b[];
extern unsigned char comp_color_a[];
extern unsigned char comp_color_b[];

extern unsigned int lzss_src;
extern unsigned int lzss_dst;
extern void lzss_decompress(void);

extern unsigned int copy_src;
extern unsigned int copy_dst;
extern void fast_copy1000(void);

extern void wait_frame(void);   /* see KNOWLEDGE.md's IRQ/raster-wait pattern
                                  * or src/irq_border.s for one way to get
                                  * this; not provided by this library. */

int main(void)
{
    unsigned char frame;
    unsigned char which = 0;

    /* cc65's crt0 sends PETSCII $0E (switch to lowercase charset) before
     * main() runs; if your artwork was drawn/captured in the post-reset
     * default uppercase+graphics charset, switch back via the KERNAL's
     * own CHROUT (see KNOWLEDGE.md's PETSCII/charset gotchas section). */
    cbm_k_bsout(0x8E);

    lzss_src = (unsigned int)comp_screen_a;
    lzss_dst = SCREEN_A;
    lzss_decompress();

    lzss_src = (unsigned int)comp_screen_b;
    lzss_dst = SCREEN_B;
    lzss_decompress();

    lzss_src = (unsigned int)comp_color_a;
    lzss_dst = SCRATCH_COLOR_A;
    lzss_decompress();

    lzss_src = (unsigned int)comp_color_b;
    lzss_dst = SCRATCH_COLOR_B;
    lzss_decompress();

    /* show A first: screen pointer already defaults there, but color
     * RAM needs an explicit first blit */
    SEI();
    copy_src = SCRATCH_COLOR_A;
    copy_dst = 0xD800;
    fast_copy1000();
    CLI();
    VIC.addr = D018_SCREEN_A;

    for (;;) {
        for (frame = 0; frame < SWAP_FRAMES; frame++) {
            wait_frame();
        }
        which = !which;

        SEI();
        copy_src = which ? SCRATCH_COLOR_B : SCRATCH_COLOR_A;
        copy_dst = 0xD800;
        fast_copy1000();
        VIC.addr = which ? D018_SCREEN_B : D018_SCREEN_A;
        CLI();
    }

    return 0;
}
