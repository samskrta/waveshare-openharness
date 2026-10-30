#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/usb_serial_jtag.h"
#include "esp_log.h"
#include "lvgl.h"
#include "bsp/esp-bsp.h"

static lv_obj_t *status;
static unsigned taps;

static void tapped(lv_event_t *event)
{
    (void)event;
    taps++;
    lv_label_set_text_fmt(status, "Touch confirmed: %u", taps);
    printf("TOUCH_OK count=%u\n", taps);
    fflush(stdout);
}

void app_main(void)
{
    usb_serial_jtag_driver_config_t usb = USB_SERIAL_JTAG_DRIVER_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&usb));
    if (!bsp_display_start()) {
        ESP_LOGE("board_test", "Display/touch initialization failed");
        return;
    }
    bsp_display_lock(-1);
    lv_obj_t *screen = lv_screen_active();
    lv_obj_set_style_bg_color(screen, lv_color_hex(0x101b2d), 0);
    lv_obj_t *title = lv_label_create(screen);
    lv_label_set_text(title, "HARNESS LAB\nWaveshare 1.75");
    lv_obj_set_style_text_color(title, lv_color_hex(0x40e0b0), 0);
    lv_obj_set_style_text_align(title, LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_align(title, LV_ALIGN_CENTER, 0, -100);
    lv_obj_t *button = lv_button_create(screen);
    lv_obj_set_size(button, 220, 70);
    lv_obj_center(button);
    lv_obj_add_event_cb(button, tapped, LV_EVENT_CLICKED, NULL);
    lv_obj_t *label = lv_label_create(button);
    lv_label_set_text(label, "TAP TO TEST");
    lv_obj_center(label);
    status = lv_label_create(screen);
    lv_label_set_text(status, "Display ready - tap above");
    lv_obj_set_style_text_color(status, lv_color_white(), 0);
    lv_obj_align(status, LV_ALIGN_CENTER, 0, 100);
    bsp_display_unlock();
    printf("DISPLAY_INIT_OK board=waveshare-1.75\n");
    fflush(stdout);
    char line[64];
    size_t used = 0;
    unsigned ticks = 0;
    for (;;) {
        char ch;
        if (usb_serial_jtag_read_bytes(&ch, 1, pdMS_TO_TICKS(100)) > 0) {
            if (ch == '\n' || ch == '\r') {
                line[used] = 0;
                if (!strcmp(line, "PING")) {
                    printf("PONG board=waveshare-1.75 taps=%u\n", taps);
                    fflush(stdout);
                }
                used = 0;
            } else if (used < sizeof(line) - 1) {
                line[used++] = ch;
            } else { used = 0; }
        }
        if (++ticks % 50 == 0) {
            printf("HEARTBEAT taps=%u\n", taps);
            fflush(stdout);
        }
    }
}
