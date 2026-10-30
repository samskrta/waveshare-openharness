# Minimal Waveshare display / touch / USB test

Bring-up test for the standard 1.75-inch Waveshare board. Uses ESP-IDF v5.5.4, Waveshare BSP 3.0.1 and LVGL 9.4.0.

```sh
idf.py -C examples/waveshare-usb-test -B "$PWD/build/usb-test" set-target esp32s3 build
```

Displays HARNESS LAB and a TAP TO TEST button. Physical taps increment the screen counter and emit TOUCH_OK. Send PING followed by a newline over USB serial to receive PONG; the firmware emits a heartbeat. This test was compiled, flashed and validated on the actual unit before OpenHarness was installed.

This is a separate application and partition layout, not the OpenHarness dashboard. Preserve a backup and stop the host daemon before flashing it. The project configuration derives from Waveshare's example repository; its Apache 2.0 license notice is included.
