# OpenHarness Waveshare standard-board firmware

This is the complete firmware subtree from OpenHarness commit `a270d3e787aed01e9b204abd11b0d8952a4fc071`, with the standard Waveshare board profile applied. Upstream documentation is retained in `UPSTREAM_README.md`.

## Build

Activate ESP-IDF **v5.5.4**. From the repository root:

```sh
idf.py -C firmware -B "$PWD/build/firmware" -DDEVICE_BOARD=waveshare-standard build
```

Use the explicit profile. Omitting it selects upstream shipped-dial wiring, including the wrong MCLK pin for this board. `dependencies.lock` records the resolved component set. Generated sdkconfig/build/component directories are ignored.

## Actionable attention

Pinned Harness questions, including Super Tab ask/stuck waits, wake the AMOLED immediately and show a static amber **Needs your answer** lower arc on the Focus face. The saved brightness is used for 15 seconds; while the wait remains unresolved, the renderer caps the panel at 12% and suspends only the normal five-minute idle sleep. Resolving the final wait restores the exact saved brightness and starts a fresh five-minute idle period. Ordinary idle, busy, completed turns, and restored notification history do not activate this behavior.

Notification audio identifies the event without turning ordinary idle into an alert:

- a fresh genuine question, approval, or actionable Super Tab transition says “Waiting.” once, even when that agent or Lead face is already visible (without redundantly waking it);
- a live completion with an explicit `tier:"alert"` plays a short two-note procedural cue;
- errors and off-face Lead/PM notices retain the established three-beep attention cue.

All three use one speaker worker and independent 30-second cooldowns. Playback continues to honor Mute, yields immediately to microphone capture, and drops rather than retries when the shared codec is busy. Quiet mode stops character motion but does not mute alerts. Nap suppresses wait wake/audio edges for 15 minutes; ending Nap wakes once if a pinned wait remains. No cue interrupts a question currently being read. PWR/BOOT can still turn the screen off during a wait, and the renderer will not immediately undo that explicit choice. Disconnect disables the override without deleting cached rows; reconnect card baselines and replayed question IDs update state silently instead of manufacturing new audio.

The waiting phrase is an embedded 16 kHz mono S16LE asset under `assets/audio/`; there is no runtime TTS or network dependency. Its generation and checksum are documented beside the asset. The completion cue is synthesized in fixed-size blocks, so writable audio RAM remains one 640-byte scratch buffer.

The alert does not navigate or cover the question/answer UI. Its low static brightness reduces, but cannot eliminate, AMOLED burn-in risk during very long unresolved waits. Validate without flashing:

```sh
python3 firmware/test/test_display_power.py
python3 firmware/test/test_question_ui.py
python3 firmware/test/test_audio_notify.py
python3 firmware/test/test_audio_routing.py
bash firmware/test/run.sh
idf.py -C firmware -B "$PWD/build/firmware" -DDEVICE_BOARD=waveshare-standard build
```

On hardware, verify the three cue classes, per-class cooldown, arrival, Mute, active recording preemption, Quiet, Nap expiry/manual wake, PWR screen-off, reconnect, multiple simultaneous waits, final resolution, and exact saved-brightness restoration. Do not flash an unfamiliar unit before following the backup and partition checks below.

Changes:
- `BSP_I2S_MCLK=42` for the standard board, leaving the shipped profile's GPIO16 intact.
- PWR is an active-high input on TCA9554 P4. Preserve other expander bits and avoid changing PMIC charge configuration.
- Initialize the key expander before worker tasks.
- Never pulse GPIO1/2 as candidate reset pins on the standard board; those are SDMMC pins.
- Announce `hw=waveshare-standard-1.75` even if initial probing fails. The official host currently offers no stock image to this identity.

Display/touch pins match the verified standard-board layout. **Rotation is a saved on-device setting.** Hold the dashboard face for about 0.65 seconds to open Tabs, then tap **Controls → Display rotation**. Choose where USB-C should point: Left, Top, Right, or Bottom. The device saves the preference and briefly restarts, applying image and touch together. The selected row says `(current)` and cannot be selected again. If saving fails, the current orientation stays active and the screen reports the failure.

Top is the factory default for this profile and matches the current enclosure. Each image damage strip rotates before DMA; calibrated touch uses the inverse mapping. Native CO5300 addressing and its 6-pixel X gap remain unchanged. One additional 22,368-byte CPU-only PSRAM strip retains the original two internal DMA buffers.

`-DDEVICE_USB_POSITION=left` selects a different **fallback for an unset/corrupt preference**, not a forced orientation. A saved choice overrides the build default and survives normal application updates. Factory reset clears it with the other preferences. The official desktop app has no rotation row; use the device menu. No desktop/daemon patch is required.

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
