// Microphone capture: I2S RX + ES7210 ADC (esp_codec_dev) → mono 16-bit PCM.
#pragma once

#include <stdbool.h>
#include <stdint.h>

// Record at 16 kHz — the rate the STT models are actually trained on. 8 kHz is the telephony fallback,
// and this used to be set to it: halving the byte rate mattered when audio left over the device's flaky
// WiFi and uploads were throughput-limited.
//
// There is no WiFi on this firmware. Audio goes out over the USB cable, measured at ~238 KB/s while
// pushing a firmware image (3,091,648 B in 13 s, 2026-08-24). 16 kHz mono 16-bit produces 32 KB/s, so the
// link carries it with 7x to spare — the constraint that justified spending accuracy on bandwidth is gone
// with the radio.
//
// ONE constant, TWO devices: notification audio uses this same rate (audio_capture.c), so mic
// and speaker stay in step by construction. Changing it here changes both, coherently.
//
// The rate travels with the audio rather than being assumed: `voice.begin` carries it as `sr`, the daemon
// forwards the DIAL's number instead of guessing, and the backend writes it into the WAV header.
#define AUDIO_SAMPLE_RATE 16000

// One-time init of I2S RX + ES7210. Returns true on success (tolerant: false → no mic).
bool audio_capture_init(void);

// Open the mic stream (16k/mono/16-bit) before reading. Returns true on success.
bool audio_capture_start(void);

// Blocking read of PCM bytes into buf (len bytes). Returns bytes read, <=0 on error.
int audio_capture_read(uint8_t *buf, int len);

// Close the mic stream.
void audio_capture_stop(void);

// DMA queue overflows since the current capture opened; a count above zero means lost samples.
uint32_t audio_capture_overruns(void);

// --- Notification cues (ES8311 speaker output) ---
typedef enum {
    AUDIO_NOTIFY_ATTENTION = 0,
    AUDIO_NOTIFY_WAITING,
    AUDIO_NOTIFY_COMPLETE,
    AUDIO_NOTIFY_COUNT,
} audio_notify_cue_t;

// One-time init of the ES8311 OUT path + one worker task for all cue types.
// Call once at boot (after the I2C bus is up). Safe no-op if the speaker codec isn't present.
void audio_notify_init(void);

// Queue a typed cue without blocking. Each type has an independent 30-second cooldown.
// The first eligible request always plays; a busy codec or newly-started capture drops it.
void audio_notify(audio_notify_cue_t cue);

// Applies immediately, including queued notifications, and persists to NVS.
bool audio_notify_set_muted(bool muted);
bool audio_notify_is_muted(void);
