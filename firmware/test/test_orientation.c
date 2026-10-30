// Reassemble partial DMA strips and prove that touch maps every native pixel
// back to the logical pixel painted there, including the 465/466 boundaries.
#include "orientation.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

static unsigned turns;
static uint16_t native[HT_WIDTH * HT_HEIGHT];
static uint16_t src[HT_WIDTH * 24], dst[HT_WIDTH * 24 + 2];

static uint16_t value(int x, int y) { return (uint16_t)(x * 131 + y * 37); }
static void paint_rect(ht_rect_t r)
{
    for (int y = 0; y < r.h; y++)
        for (int x = 0; x < r.w; x++)
            src[y*r.w+x] = value(r.x+x, r.y+y);
    dst[0] = 0x1234;
    dst[r.w*r.h+1] = 0x5678;
    ht_rect_t out = display_orient_pixels(r, src, dst+1, turns);
    assert(dst[0] == 0x1234 && dst[r.w*r.h+1] == 0x5678);
    assert(out.x >= 0 && out.y >= 0);
    assert(out.x+out.w <= HT_WIDTH && out.y+out.h <= HT_HEIGHT);
    for (int y = 0; y < out.h; y++)
        for (int x = 0; x < out.w; x++) {
            int nx = out.x+x, ny = out.y+y;
            uint16_t tx = nx, ty = ny;
            display_orient_touch(&tx, &ty, turns);
            assert(tx >= r.x && tx < r.x+r.w && ty >= r.y && ty < r.y+r.h);
            assert(dst[1+y*out.w+x] == value(tx, ty));
            native[ny*HT_WIDTH+nx] = dst[1+y*out.w+x];
        }
}
static void test_turn(void)
{
    for (int y = 0; y < HT_HEIGHT; y += 24)
        paint_rect((ht_rect_t){0, y, HT_WIDTH, HT_HEIGHT-y < 24 ? HT_HEIGHT-y : 24});
    // Native left center becomes logical top center, where USB now exits.
    uint16_t x = 0, y = 233;
    display_orient_touch(&x, &y, 1);
    assert(x == 232 && y == 0);
    for (int ny = 0; ny < HT_HEIGHT; ny++)
        for (int nx = 0; nx < HT_WIDTH; nx++)
            {
                int lx = turns == 1 ? 465-ny : turns == 2 ? 465-nx : turns == 3 ? ny : nx;
                int ly = turns == 1 ? nx : turns == 2 ? 465-ny : turns == 3 ? 465-nx : ny;
                assert(native[ny*HT_WIDTH+nx] == value(lx, ly));
            }
    // Nonzero offsets, skinny edge updates and small edits taller than 24 rows.
    paint_rect((ht_rect_t){465, 0, 1, 466});
    paint_rect((ht_rect_t){0, 465, 466, 1});
    paint_rect((ht_rect_t){37, 71, 17, 83});
    srand(1);
    for (int n = 0; n < 1000; n++) {
        int w = 1+rand()%466, h = 1+rand()%24;
        paint_rect((ht_rect_t){rand()%(467-w), rand()%(467-h), w, h});
    }
}
int main(void)
{
    for (turns = 0; turns < 4; turns++) test_turn();
    puts("orientation: PASS (all four turns; full frame, partial damage, edges, guards and inverse touch)");
}
