# Saved display rotation — 2026-10-30

## Behavior and use

Hold the dashboard face for about 0.65 seconds until Tabs opens. Tap **Controls → Display rotation**, then select the physical USB-C port position: Left, Top, Right, or Bottom. The current choice is labeled and disabled. A successful save briefly restarts the device; the dashboard and touch apply the same orientation on boot. Normal flashing and power cycles retain the preference; factory reset clears it. The current enclosure uses Top.

A Controls button was added to the tab picker because the legacy Controls view had no visible entry. The setting is local to the board; the official desktop application has no rotation row and needs no modification.

## Implementation and failure behavior

- NVS key `pair/disp_rot` stores image quarter-turns: 0=Left, 1=Top, 2=Right, 3=Bottom. Missing/corrupt values fall back to the build default (Top for the current profile).
- The build's `DEVICE_USB_POSITION=top|left` is now a fallback rather than an override of a saved preference.
- Generalized strip and inverse touch transforms cover all four positions; CO5300 native addressing and gap are unchanged.
- Live orientation is immutable for each boot. NVS writes and restart occur in the action worker, outside the render/touch path. No mid-frame or held-contact coordinate transition occurs.
- Invalid values, selecting the current position, and repeated selections during a pending save are ignored. Voice activity and a full action queue prevent a restart request. A failed save reports an error and leaves the current orientation running.
- Only application firmware changed; CAD and STL geometry are unchanged.

## Validation completed

- Four-way image/touch test under UB/bounds sanitizers: all 466x466 pixels, full frames, 1,000 random damage rectangles per orientation, skinny/tall updates, buffer guards and inverse touch mapping.
- Production NVS/menu/dispatch/worker test: unset and corrupt defaults, all saved values, invalid values, NVS open/set/commit failures, non-overlapping menu targets, text width, current-choice disabling, pending selection disabling, voice and queue guards, failed-save recovery, restart and simulated reboot persistence.
- Existing production device-settings, display-power, touch-driver and touch-UI tests passed. These are targeted checks, not a new full-suite run.
- ESP-IDF v5.5.4 build passed; application size 3,363,536 bytes fits the OTA slot.
- Source receipt, upstream patch round-trip, and release/application SHA-256 checks passed.
- Actual device: verified matching partition table, valid OTA0 sequence/state/CRC; wrote only the application at 0x20000 and verified its hash. Bootloader, partition table, OTA metadata, settings and ROM download access were preserved.
- Normal hardware boot passed PSRAM testing and logged `orientation usb=top image_ccw=90 touch_cw=90`; display/touch initialized without a captured fault. Harness restarted and restored its backend connection.

The prior fixed-Top image's actual upright-screen and touch acceptance remains documented in `usb-top.md`. The user confirmed the new menu on actual hardware: selecting Left restarted into the matching orientation with working touch; selecting Top did the same, returning the unit to Top. This exercises actual NVS save/load across device restarts. Right and Bottom have automated transform/menu coverage but were not separately confirmed on hardware. The persistence/error-path tests above use an NVS stub; they are not a power-loss endurance test on actual flash.
