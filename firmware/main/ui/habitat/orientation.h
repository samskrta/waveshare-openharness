// Saved image quarter-turns: USB left=0, top=1, right=2, bottom=3.
// Keep the CO5300's native addressing/gap; rotate each damage strip before DMA.
// Touch uses the inverse mapping AFTER the controller's existing calibration.
#pragma once
#include "terminal.h"

static inline ht_rect_t display_orient_pixels(ht_rect_t r, const uint16_t *src, uint16_t *dst, unsigned turns)
{
    // Logical -> native: counterclockwise image turns; odd turns transpose strips.
    // RGB565 words (including their on-wire byte order) are copied unchanged.
    for (int y = 0; y < r.h; y++)
        for (int x = 0; x < r.w; x++) {
            int to = turns == 1 ? (r.w - 1 - x) * r.h + y :
                     turns == 2 ? (r.h - 1 - y) * r.w + r.w - 1 - x :
                     turns == 3 ? x * r.h + r.h - 1 - y : y * r.w + x;
            dst[to] = src[y * r.w + x];
        }
    if (turns == 1) return (ht_rect_t){r.y, HT_WIDTH - r.x - r.w, r.h, r.w};
    if (turns == 2) return (ht_rect_t){HT_WIDTH - r.x - r.w, HT_HEIGHT - r.y - r.h, r.w, r.h};
    if (turns == 3) return (ht_rect_t){HT_HEIGHT - r.y - r.h, r.x, r.h, r.w};
    return r;
}

static inline void display_orient_touch(uint16_t *x, uint16_t *y, unsigned turns)
{
    uint16_t native_x = *x;
    uint16_t native_y = *y;
    if (turns == 1) { *x = HT_WIDTH - 1 - native_y; *y = native_x; }
    if (turns == 2) { *x = HT_WIDTH - 1 - native_x; *y = HT_HEIGHT - 1 - native_y; }
    if (turns == 3) { *x = native_y; *y = HT_HEIGHT - 1 - native_x; }
}
