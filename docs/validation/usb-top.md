# USB-top revision — 2026-10-30

The complete cased module turns clockwise 90 degrees from the original left-port position. The firmware counter-rotates the dashboard image and uses the inverse mapping for touch. The retained protective case and speaker dimensions are unchanged.

## Implementation

- Default Waveshare build: `DEVICE_USB_POSITION=top`; `left` remains available for an older enclosure.
- RGB565 partial damage strips rotate in software into the original two DMA buffers. A CPU-only 22,368-byte PSRAM strip keeps the original DMA ownership/fence pipeline. Native CO5300 addressing and its 6-pixel X gap are unchanged.
- Calibrated touch coordinates rotate after the existing bounds check; controller error/release recovery is unchanged.
- All module port reliefs, the bezel screw pattern and rear module wire relief rotate together. The tilted desk body and speaker mounts stay in their existing orientation.
- Only `Housing_Waveshare_Cased` and `Front_Bezel` need different prints. Use the revised pair together. The other five print meshes are byte-identical to the initial release.

## Checks completed

- ESP-IDF v5.5.4 / Espressif GCC 14.2.0_20260121 build passed. Application size: 3,362,576 bytes, within the 0x7e0000-byte OTA slot.
- Orientation test passed under UB/bounds sanitizers: complete 466x466 reconstruction, 1,000 partial rectangles, skinny edge updates, tall small edits, buffer guards, and inverse touch correspondence at every painted native pixel.
- Existing production touch-driver, touch-UI, display-power, render-guard and brightness tests passed. This is targeted validation; no new full-suite run is claimed.
- Source hash receipt, upstream patch application/byte comparison, and release SHA-256 checks passed.
- Seven valid single CAD solids; seven watertight, consistently wound, connected STL meshes; 21 pairwise assembly checks with zero calculated material overlap. New preview visually reviewed.

## Actual device update

Harness was stopped to release the port. The existing partition table was read and matched the build. OTA sequence 1, state VALID, and its CRC selected `ota_0` at `0x20000`. Only the application slot was written. The bootloader, partition table, OTA selection, NVS/settings and ROM download access were preserved. esptool verified the written image hash. The prior left-port application is retained privately for rollback.

A normal restart passed the 8 MB PSRAM test, identified CST9217, logged `orientation=usb-top image=ccw90 touch=cw90`, and ran without a panic, assert or renderer stall during the captured boot window. Harness reopened, restored the Waveshare Dashboard session, and reported the device Connected; its daemon v0.5.18 reopened native USB.

The release folder contains the complete newly built image set for a fresh installation. Only its app was needed for this unit's upgrade. Existing 2026-10-29 logs describe the previous left-port image and remain separate.

## Physical acceptance still needed

Final human confirmation of upright dashboard/tap/swipe alignment with USB at the top is pending. The enclosure still needs a physical print and fit test, including cable insertion/strain, buttons, microphones, microSD, connector depth, rear wire routing and speaker acoustics. Print both fit coupons first; they check pocket sizes rather than port positions.

## Build environment

macOS had offloaded the prior SDK/toolchain to iCloud. The same official SDK tag and compiler version were restored into local storage before compiling. This recovery is separate from firmware validation. No toolchains, private flash metadata, credentials or daemon state are committed.
