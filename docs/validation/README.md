# Validation record

Initial bring-up validated on 2026-10-29, America/Chicago. The original sections below describe that left-port image. For the current USB-top firmware and CAD, see [USB-top revision](usb-top.md).

## Firmware and hardware

- ESP32-S3 revision 0.2, 16 MB flash, 8 MB PSRAM, Waveshare standard 1.75-inch board with protective case.
- Built using ESP-IDF v5.5.4 and the explicit `DEVICE_BOARD=waveshare-standard` profile.
- App image fits the 0x7e0000-byte OTA slot. esptool verified written image hashes.
- Boot/PSRAM test and CO5300/CST9217 identification succeeded; user confirmed display and physical touch.
- Native USB protocol 3 connected to the official Harness 0.5.9 daemon. A sampled traffic record had 20,075 B transmitted, 743,945 B received, zero corrupt frames and zero discarded bytes.
- ES7210 and ES8311 initialized. A three-second / 95 KB microphone recording reached the host's STT path. This is data-path evidence, not a calibrated audio-quality test.
- A real Claude Code session returned `Waveshare dashboard connected.` after an expired OAuth login was refreshed through the normal login flow.
- A full original flash backup was retained privately. No eFuses or ROM-download restrictions were changed.
- The stock firmware update channel was not offered to the custom board identity.

`device-tests.log` is the output of the upstream host test runner. It passed all cases invoked. The runner has an additional cJSON integration block gated by `IDF_PATH`; the provided log does not claim that optional block as executed. Build, flash and host-test logs are separate from physical acceptance.

Not tested on hardware: PWR-button interaction, speaker sound/voice accuracy, battery operation and actual OTA rollback/recovery. Simulated OTA tests are not hardware OTA tests.

## Mechanical

- Cased-module and speaker dimensions were checked against official references and the user's approximate speaker measurement.
- Build script exported each printable part as one valid CAD solid.
- Mesh checks require watertight, consistently wound, single-component STL output.
- Pairwise checks of printed parts and reference component envelopes found zero overlapping material at the recorded configuration.
- Visual review covered assembled, open, exploded and underside views.

The enclosure has **not** been printed or physically fitted. Fit coupons only check two mating pocket sizes. Button/microphone/card alignment, depth stack, cable overmold clearance, wall strength, cooling, acoustics and print durability still need physical acceptance. See hardware/enclosure/validation.json for numeric results.

## Scope / provenance

The initial firmware binary set was the hardware-validated port from the original checkout. The current set adds USB-top orientation and was rebuilt; the new source receipt and revision record distinguish it from the original snapshot. Native host source was inspected and built during bring-up, then retired in favor of the official desktop/daemon. Only the focused firmware subtree and its patch are carried here.

Implementation, firmware checks, hardware acceptance, mechanical generation and repository publication were separate steps. No upstream merge or upstream release was performed. Temporary engine and Harness sign-in waits were part of the elapsed setup, not build time. Private account state and raw factory flash are excluded.
