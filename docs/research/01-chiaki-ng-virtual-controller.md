# chiaki-ng + virtual DualSense — research findings

Research date: 2026-05-10.

## Summary

The scaffold's `gamepad.py` (plain python-evdev uinput) is **insufficient for gyro forwarding to the PS5**. Sticks and buttons will work; motion will not. The correct path is `inputtino` over `uhid`.

## Key findings

### chiaki-ng status (high confidence)
- Actively maintained. Latest stable **v1.10.0 (Apr 2025)**. Weekly canary builds through Apr 2026.
- Repo: <https://github.com/streetpea/chiaki-ng>
- Linux install paths: Flathub (`io.github.streetpea.Chiaki4deck`), AppImage, AUR, build from source.

### Gyro forwarding (high confidence with one caveat)
- chiaki-ng forwards DualSense gyro + accel upstream via SDL2's `SDL_CONTROLLERSENSORUPDATE`.
- DualSense haptics + adaptive triggers require **USB-C** (not Bluetooth) — orthogonal but worth knowing.
- Dreams specifically uses the standard DualSense motion API path that chiaki-ng supports → expected to work, no explicit testimonial confirming.

### Why python-evdev uinput is insufficient (high confidence — critical finding)
SDL2's `SDL_SensorType` (gyro/accel) is only exposed for controllers SDL identifies as DualSense via its gamecontrollerdb mapping. On Linux, sensor data comes from the **`hid-playstation`** kernel driver, which inspects HID report descriptors — not just VID/PID on a uinput evdev node.

A python-evdev uinput device with VID/PID `054C:0CE6` is seen as a generic gamepad. Sticks/buttons forward fine. Gyro does not:
- uinput emits evdev events, not HID reports
- `hid-playstation` never binds (no HID device underneath)
- SDL therefore sees no `SDL_SensorType`

**Solution:** use `uhid` with a full DualSense HID descriptor, so `hid-playstation` claims the device and exposes the motion sub-devices.

### DSU motion-source path (low confidence, but likely dead end)
No evidence chiaki-ng implements a DSU client. The "Steam Deck gyro" native path is internal IMU reading, not DSU. SteamDeckGyroDSU is a DSU server. Don't pursue.

### Primary reference project: inputtino (high confidence)
- Repo: <https://github.com/games-on-whales/inputtino>
- C++ library used by Wolf, Sunshine, Moonshine for game-streaming virtual controllers.
- Full virtual DualSense via uhid: gyro, accel, touchpad, adaptive triggers, LED, battery.
- Native Python bindings in `bindings/python/`.
- Used in production by Sunshine PR #3600 for native DualSense over Moonlight — same use-case shape as ours.
- Blog series by maintainer ABeltramo: <https://abeltra.me/blog/inputtino-uhid-2/> and `-3/`.

Setup required:
- `uhid` kernel module loaded
- User in `input` group
- udev rule for `/dev/uhid`
- `hid-playstation` available (mainline kernel since 5.16)

## Recommendation

Drop `python-evdev` for the gamepad backend. Use `inputtino` via its Python bindings. Gives a uhid-backed virtual DualSense with gyro/accel that `hid-playstation` binds to, SDL2 sees as a real DualSense, chiaki-ng forwards motion upstream.

Fallback if Python bindings don't expose sensors cleanly (medium-confidence risk — bindings docs only show buttons/sticks/triggers): write a small C++ shim using inputtino's C++ API exposing a Unix socket for the Python MCP. ~150 lines.

## Sources
- <https://github.com/streetpea/chiaki-ng>
- <https://streetpea.github.io/chiaki-ng/setup/controlling/>
- <https://github.com/games-on-whales/inputtino>
- <https://abeltra.me/blog/inputtino-uhid-2/>
- <https://abeltra.me/blog/inputtino-uhid-3/>
- <https://github.com/LizardByte/Sunshine/pull/3600>
