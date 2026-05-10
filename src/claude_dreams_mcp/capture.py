"""Wayland screen capture via grim, scoped to the chiaki-ng window.

STATUS: scaffold-only. Will not work on GNOME-Wayland.

R&D finding (docs/research/05): `grim` uses the `wlr-screencopy` protocol
which Mutter (GNOME) does not implement. Will work on wlroots compositors
(Sway, Hyprland) only. `gnome-screenshot`'s D-Bus API was also revoked in
GNOME 49.

TODO: replace with PipeWire via the xdg-desktop-portal ScreenCast interface.
Python package `pipewire-capture` (pip install pipewire-capture) handles the
portal handshake. User picks the chiaki-ng window once at MCP startup
(source-picker dialog), then frames stream silently — correct API for
1-3 fps capture. See docs/research/05 for fallback (Screenshot portal +
full-screen + crop).
"""
from __future__ import annotations

import io
import re
import subprocess
from dataclasses import dataclass


@dataclass
class WindowGeometry:
    output: str
    x: int
    y: int
    width: int
    height: int

    def grim_geom(self) -> str:
        return f"{self.x},{self.y} {self.width}x{self.height}"


def find_chiaki_window() -> WindowGeometry | None:
    """Find the chiaki-ng window via swaymsg / hyprctl. Returns None if not found.

    TODO: GNOME on Wayland (Jonathan's setup) doesn't expose window geometry the
    same way. Probable path: full-screen capture + crop, or use a GNOME extension
    that exposes window rects. For now this is a stub.
    """
    return None


def capture_png(geom: WindowGeometry | None = None) -> bytes:
    """Capture the screen (or the given region) as PNG bytes."""
    cmd = ["grim"]
    if geom is not None:
        cmd += ["-g", geom.grim_geom()]
    cmd += ["-"]
    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout


def capture_png_resized(max_dim: int = 1280) -> bytes:
    """Capture full screen and downscale to keep MCP payloads modest."""
    from PIL import Image

    raw = capture_png(None)
    img = Image.open(io.BytesIO(raw))
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()
