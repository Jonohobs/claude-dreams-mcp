# PSMoveService / Monado on Linux — research findings

Research date: 2026-05-10. Scope: spatial input substrate for the future open creation engine using PS Move controllers + PS3 Eye.

## Summary

**PSMoveService-the-project is not viable on Linux.** The original is archived; the active `Timocop/PSMoveServiceEx` fork is Windows-first with no documented Linux build. The correct path is **Monado's `psmv` driver → OpenXR → Godot**, with `thp/psmoveapi` for pairing utilities.

## Key findings

### Project landscape (high confidence)
- `psmoveservice/PSMoveService` — archived, Windows/macOS focused. Skip.
- `Timocop/PSMoveServiceEx` — active Windows fork, no Linux build. Reference only.
- `thp/psmoveapi` — Thomas Perl's lower-level library. Linux-native path; still maintained; what you actually use.
- **Monado's `psmv` driver** — Move support baked into the Monado OpenXR runtime. Strategically the right answer for Godot+OpenXR.

### Cameras (high confidence)
- **PS3 Eye**: kernel `gspca_ov534` driver, V4L2 out of the box on modern distros. Manual exposure/gain via `v4l2-ctl`. PSMoveAPI and Monado's tracker both consume V4L2.
- **PS4 Camera**: not supported through standard paths without a custom AUX→USB3 adapter cable. Skip unless you already have one.
- Other UVC cameras with manual exposure work in principle but lose tracker presets.

### Bluetooth pairing (medium-high confidence)
- Built-in Intel/Qualcomm adapters generally pair Moves via BlueZ 5.6x — the "CSR8510 required" claim is about old Windows tooling.
- Gotchas: set `ClassicBondedOnly=false` in `/etc/bluetooth/input.conf`; some Intel 8260/7260 cards still misbehave.
- **CSR8510 A10 dongle (~$8)** is zero-risk fallback. **TP-Link UB400 v1 = CSR (works), v2 = Realtek (does NOT work)** — verify carefully.

### Move Navigation Controller (high confidence)
- Supported by psmoveapi (`psmove pair-nav` uses `sixpair`).
- **Untracked** (no light ball) — pure IMU + buttons + analog stick.
- Shows up as a standard evdev joystick on Linux after pairing.
- No rumble/LED, so haptic feedback must come from the Move.

### Output interfaces (high confidence)
- psmoveapi: C library + Python bindings + `psmove-tracker` example. Best for a custom GDExtension.
- PSMoveSteamVRBridge: archived. Ignore.
- **Monado**: exposes Moves as OpenXR input devices → cleanest output for Godot.

### Tracking quality (medium-high confidence)
- PS3 Eye 60Hz → ~35-60ms end-to-end. Acceptable for sculpt/menu, marginal for fast melee.
- Single Eye tracking volume ~1.5m cone, ~3m max usable.
- **Ball occlusion is the killer issue.** Hand-behind-hand, ball-against-torso, LED color collisions all drop tracking. IMU dead-reckons ~1-2s before drift is visible.
- Single-camera Z (depth) noisier than X/Y — ~2-5cm jitter at 1.5m. Two PS3 Eyes fix this but double calibration work.

## Recommended setup (Ubuntu 24.04/26.04)

```bash
sudo apt install bluez libusb-1.0-0-dev v4l-utils \
                 libopencv-dev cmake build-essential \
                 libudev-dev libhidapi-dev
v4l2-ctl --list-devices   # should show PS3 Eye
sudo apt install monado-cli monado-service libopenxr-loader1
# pair Moves via psmoveapi pairing docs
```

Keep a CSR8510 A10 dongle on the shelf as insurance.

## Known biters

1. **Monado's PSMV driver is community-maintained and brittle.** Calibration files in `~/.config/monado/`; tracker thread eats a full core per camera. Expect to read source.
2. **No active Linux-targeted PSMoveService fork.** Fallback if Monado fails = write a GDExtension over `psmoveapi` yourself, NOT build PSMoveServiceEx on Linux.
3. **Pairing is fiddly every time.** Budget a half-day for the first pair.
4. **Ball-tracking is fragile.** Design UX around it (don't require reaching behind back).
5. **Single PS3 Eye = noisy depth.** Two cameras fix it but double calibration.

## Sources
- <https://github.com/thp/psmoveapi>
- <https://monado.pages.freedesktop.org/monado/group__drv__psmv.html>
- <https://monado.freedesktop.org/positional-tracking-psmove.html>
- <https://github.com/Timocop/PSMoveServiceEx>
- <https://psmoveapi.readthedocs.io/en/latest/pairing.html>
- <https://psmoveapi.readthedocs.io/en/latest/navcon.html>
