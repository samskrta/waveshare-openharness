# OpenHarness Waveshare standard-board firmware

This is the complete firmware subtree from OpenHarness commit `a270d3e787aed01e9b204abd11b0d8952a4fc071`, with the standard Waveshare board profile applied. Upstream documentation is retained in `UPSTREAM_README.md`.

## Build

Activate ESP-IDF **v5.5.4**. From the repository root:

```sh
idf.py -C firmware -B "$PWD/build/firmware" -DDEVICE_BOARD=waveshare-standard build
```

Use the explicit profile. Omitting it selects upstream shipped-dial wiring, including the wrong MCLK pin for this board. `dependencies.lock` records the resolved component set. Generated sdkconfig/build/component directories are ignored.

Changes:
- `BSP_I2S_MCLK=42` for the standard board, leaving the shipped profile's GPIO16 intact.
- PWR is an active-high input on TCA9554 P4. Preserve other expander bits and avoid changing PMIC charge configuration.
- Initialize the key expander before worker tasks.
- Never pulse GPIO1/2 as candidate reset pins on the standard board; those are SDMMC pins.
- Announce `hw=waveshare-standard-1.75` even if initial probing fails. The official host currently offers no stock image to this identity.

Display/touch pins match the verified standard-board layout. The Waveshare profile now defaults to **USB-C at the top**: physically turn the cased unit clockwise 90 degrees from the original left-port position. Each image damage strip rotates counterclockwise before DMA; calibrated touch coordinates use the inverse turn. The panel's native 6-pixel X offset remains unchanged. One additional 22,368-byte PSRAM strip avoids allocating another internal DMA buffer.

For an enclosure already printed with USB on the left, add `-DDEVICE_USB_POSITION=left` to the build command. This disables both image and touch rotation. The current CAD/STLs require the default `top` image. Retaining the protective case does not change this electrical profile.

## Flash the checked binary set

Quit the Harness desktop app, stop the daemon (`harness stop`), and close serial monitors. Recheck the USB port after reconnecting; `/dev/cu.usbmodem1101` was the tested macOS path.

From the repository root, with esptool available:

```sh
python -m esptool --chip esp32s3 --port /dev/cu.usbmodem1101 --baud 460800 write_flash --flash_mode dio --flash_size 16MB --flash_freq 80m 0x0 releases/firmware/bootloader.bin 0x8000 releases/firmware/partition-table.bin 0xf000 releases/firmware/ota-data.bin 0x20000 releases/firmware/app.bin
```

Use the complete matching image set when installing a new device. For an application-only update on an existing unit, first verify its partition table and active OTA slot; write only that app slot and preserve the bootloader, OTA metadata and NVS. On the tested unit, valid OTA sequence 1 selected `ota_0` at `0x20000`. Do not assume that offset on a differently provisioned device. The release manifest records the addresses and SHA-256 hashes. A normal flash does not require erasing the whole chip. This writes a dual-OTA partition layout; preserve a full local backup before the first conversion.

## Backup and recovery

Before flashing an unfamiliar unit, save its full 16 MB flash **locally**, not in Git:

```sh
python -m esptool --chip esp32s3 --port /dev/cu.usbmodem1101 read_flash 0 0x1000000 factory-backup.bin
```

Hold BOOT while powering/reconnecting the board, then release it after the ROM USB device appears if firmware no longer communicates. With a battery, disconnecting USB alone may not reset the chip. Never change eFuses, enable secure boot/flash encryption casually, or disable ROM download mode as part of routine bring-up.

To restore a known local full backup:

```sh
python -m esptool --chip esp32s3 --port /dev/cu.usbmodem1101 write_flash 0 factory-backup.bin
```

Host tests:

```sh
bash firmware/test/run.sh
```

Set `IDF_PATH` through an activated ESP-IDF environment to include the cJSON integration cases at the end of the runner. Firmware hardware acceptance and actual OTA recovery must be recorded separately from these host tests.
