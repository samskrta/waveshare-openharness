// The cased Waveshare module turns clockwise 90 degrees to put USB-C at the top.
// Keep the CO5300's native addressing/gap; rotate each damage strip before DMA.
// Touch uses the inverse mapping AFTER the controller's existing calibration.
#pragma once
#include "terminal.h"

static inline ht_rect_t display_orient_pixels(ht_rect_t r, const uint16_t *src, uint16_t *dst)
{
    // Logical -> native: (x, y) -> (y, 465-x), a counterclockwise image turn.
    // RGB565 words (including their on-wire byte order) are copied unchanged.
    for (int y = 0; y < r.h; y++)
        for (int x = 0; x < r.w; x++)
            dst[(r.w - 1 - x) * r.h + y] = src[y * r.w + x];
    return (ht_rect_t){r.y, HT_WIDTH - r.x - r.w, r.h, r.w};
}

static inline void display_orient_touch(uint16_t *x, uint16_t *y)
{
    uint16_t native_x = *x;
    *x = HT_WIDTH - 1 - *y;
    *y = native_x;
}
