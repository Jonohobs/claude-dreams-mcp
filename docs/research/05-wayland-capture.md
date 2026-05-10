# Wayland window capture on GNOME — research findings

Research date: 2026-05-10. Scope: programmatic capture of the chiaki-ng window for the MCP screenshot tool, on GNOME-Wayland.

## Summary

**Scaffold's `capture.py` uses `grim`, which doesn't work on GNOME-Wayland** (grim uses wlroots-only `wlr-screencopy`). Correct path: **ScreenCast portal + PipeWire** via the `pipewire-capture` Python package, with one source-picker dialog at session start and unlimited subsequent frames.

## What works / doesn't on GNOME-Wayland (May 2026)

| Tool | Status |
|---|---|
| `grim` | **No.** wlroots-only. |
| `gnome-screenshot` | **No.** Mutter revoked the private D-Bus API in GNOME 49 (Sept 2025). |
| `org.gnome.Shell.Screenshot` D-Bus | **No.** Disabled in GNOME 49+. |
| `org.freedesktop.portal.Screenshot` | **Yes.** Returns file URI. One permission dialog per app per session (persistent grant). Full-screen only. |
| `org.freedesktop.portal.ScreenCast` | **Yes.** PipeWire node. One source-picker dialog at session start, then unlimited frames. |
| Mutter Shell `Eval` extension | Possible but brittle + security footgun. Skip. |
| `flameshot --raw` | Goes through portal anyway. No advantage. |
| `mss` | **X11 only.** Wayland branch unmerged. |
| OBS + `obs-websocket` | Works (uses PipeWire) but heavyweight for 1-3 fps. |

## Window geometry

Not exposed to unprivileged clients on GNOME-Wayland. Two options:
1. Full-screen capture + crop in Pillow. Fine for fullscreen/large chiaki-ng window.
2. ScreenCast portal — user picks chiaki-ng window once, you get PipeWire stream of that window only. No geometry math needed.

## Permission prompts

- **Screenshot portal**: dialog on *first* call per app per session. `permission_store_checked=true` + persistent permission store means later calls go through silently once granted. User can toggle in GNOME Settings → Apps → Permissions → Screenshots.
- **ScreenCast portal**: one source-picker dialog at session start. PipeWire stream stays open — pull frames forever with zero further prompts. Correct API for streaming.

## Recommended approach

### Primary: ScreenCast portal + PipeWire

Package: `pipewire-capture` (`pip install pipewire-capture`).

```python
from pipewire_capture import PipeWireCapture
cap = PipeWireCapture()    # opens portal, user picks chiaki-ng window
cap.start()
frame = cap.get_frame()     # numpy BGRA
png = Image.fromarray(frame).convert("RGB")
buf = io.BytesIO(); png.save(buf, "PNG")
```

User picks chiaki-ng once on MCP startup. Window-scoped capture. No XWayland. No per-frame prompt.

**Confidence:** medium — `pipewire-capture` exists with prebuilt wheels; not personally verified on the target machine. 30-min spike recommended before committing.

### Fallback: Screenshot portal

Via `Gio`/`pydbus` calling `org.freedesktop.portal.Screenshot.Screenshot` with `interactive=false`, `modal=false`. First call prompts; user toggles persistent permission in GNOME Settings; thereafter silent. Full-screen only — crop in Pillow.

### Not recommended

- XWayland fallback (`QT_QPA_PLATFORM=xcb` + `mss`) — would work but regresses chiaki-ng's HDR / fractional-scaling correctness and adds input-latency variance.

## Sources
- <https://www.jwz.org/blog/2025/06/wayland-screenshots/>
- <https://bbs.archlinux.org/viewtopic.php?id=308445>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Screenshot.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.ScreenCast.html>
- <https://github.com/bquenin/pipewire-capture>
- <https://github.com/flatpak/xdg-desktop-portal/pull/851>
- <https://discourse.gnome.org/t/take-screenshot-in-gnome-environment-via-its-dbus-api/21144>
- <https://github.com/BoboTiG/python-mss/issues/155>
