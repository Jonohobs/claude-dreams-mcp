"""Wayland screen capture via grim, scoped to the chiaki-ng window."""
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
