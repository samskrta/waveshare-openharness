# Persistent actionable attention

## Scope

- Preserve the existing protocol and use only pinned `question` notices (ordinary questions and Super Tab ask/stuck waits) as actionable state.
- Reach the display renderer, Focus/home presentation, nap event edges, host tests, provenance patch/hash records, and firmware documentation.
- Reuse the existing mute-aware, microphone-safe, 30-second-coalesced notification chime.
- Do not change daemon/desktop protocol, add settings or dependencies, flash hardware, or merge the pull request.

## Implementation

1. Export a read-only `habitat_actionable_wait()` derived under the display lock from ready + connected + not napping + `waiting() > 0`.
2. In the renderer, keep the normal saved brightness untouched; show a new alert at normal brightness for 15 seconds, then cap the unresolved alert at 12%, block only five-minute auto-sleep, and rearm the five-minute timer when the final wait resolves.
3. Keep explicit PWR/BOOT screen-off effective. Suppress new wake/chime edges during the 15-minute Nap, then wake once if an unresolved wait remains when Nap ends. Quiet continues to stop motion; mute alone controls sound.
4. Add a small static amber `Needs your answer` lower-arc indicator to the existing Focus face. Do not navigate, overlay, flash, or replace any question/answer screen being read.
5. Extend source-extraction tests for power/brightness transitions, questions, multiple waits, Nap, reconnect/stale state, and the amber Focus indicator. Run focused tests, the full available host suite, and an ESP-IDF 5.5.x Waveshare-profile build if the SDK is available.
6. Document behavior, validation commands, hardware caveats, and downstream provenance; update the saved patch/source hashes; commit, push the feature branch, and open a PR without merging.

## Safety checks

- Generic idle/busy/done states never activate attention.
- A stale close or one of several resolved waits cannot clear remaining attention.
- Disconnect and Nap disable the brightness/sleep override even if cached notice rows remain.
- The exact user brightness returns on resolution; the temporary cap is never persisted.
- Explicit screen-off remains possible during an unresolved wait.
