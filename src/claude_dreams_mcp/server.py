"""MCP server exposing Dreams Create-mode controls.

Tools:
  - screenshot              capture current chiaki-ng frame
  - press_button            momentary button press
  - hold_button / release   discrete state changes
  - stick                   raw stick deflection (left|right, x, y, duration_ms)
  - trigger                 L2/R2 analog
  - dpad                    discrete dpad direction
  - tilt_imp                motion-language imp navigation (right-stick under the hood)
  - move_player             left-stick locomotion
  - recenter_imp            reset imp reference frame
"""
from __future__ import annotations

import base64
from typing import Literal

from mcp.server.fastmcp import FastMCP

from .capture import capture_png_resized
from .gamepad import VirtualDualSense, virtual_dualsense
from .motion import Direction, aim_at_normalized, move_player, recenter_imp, tilt_imp


mcp = FastMCP("claude-dreams")

_pad: VirtualDualSense | None = None


def _get_pad() -> VirtualDualSense:
    global _pad
    if _pad is None:
        _pad = VirtualDualSense()
        _pad.open()
    return _pad


@mcp.tool()
def screenshot() -> dict:
    """Capture the current Dreams view (via the chiaki-ng window) as a PNG."""
    png = capture_png_resized(max_dim=1280)
    return {
        "mime_type": "image/png",
        "data_base64": base64.b64encode(png).decode("ascii"),
    }


@mcp.tool()
def press_button(button: str, hold_ms: int = 80) -> str:
    """Press and release a button. Buttons: cross, circle, square, triangle, l1, r1, l3, r3, share, options, ps."""
    _get_pad().press(button, hold_ms=hold_ms)
    return f"pressed {button} for {hold_ms}ms"


@mcp.tool()
def hold_button(button: str) -> str:
    """Press and hold a button (until release_button)."""
    _get_pad().hold(button)
    return f"holding {button}"


@mcp.tool()
def release_button(button: str) -> str:
    """Release a held button."""
    _get_pad().release(button)
    return f"released {button}"


@mcp.tool()
def stick(side: Literal["left", "right"], x: float, y: float, duration_ms: int = 200) -> str:
    """Deflect a stick to (x, y) in [-1, 1], hold for duration_ms, then release."""
    import time as _t
    pad = _get_pad()
    pad.stick(side, x, y)
    _t.sleep(duration_ms / 1000)
    pad.stick(side, 0.0, 0.0)
    return f"stick {side} -> ({x:.2f}, {y:.2f}) for {duration_ms}ms"


@mcp.tool()
def trigger(side: Literal["l2", "r2"], value: float) -> str:
    """Set L2 or R2 analog trigger to value in [0, 1]."""
    _get_pad().trigger(side, value)
    return f"trigger {side} -> {value:.2f}"


@mcp.tool()
def dpad(x: int, y: int) -> str:
    """Set dpad state. x and y in {-1, 0, 1}."""
    _get_pad().dpad(x, y)
    return f"dpad -> ({x}, {y})"


@mcp.tool()
def tilt_imp_tool(
    direction: Direction,
    magnitude: float = 0.5,
    duration_ms: int = 200,
) -> str:
    """Move the Dreams imp in a direction.

    Right-stick imp mode required (PS5 Settings → Accessibility → Controllers).
    direction: up, down, left, right, upper-left, upper-right, lower-left, lower-right.
    magnitude: 0.0–1.0. duration_ms: how long to hold the stick.
    """
    tilt_imp(_get_pad(), direction, magnitude=magnitude, duration_ms=duration_ms)
    return f"tilted imp {direction} mag={magnitude:.2f} for {duration_ms}ms"


@mcp.tool()
def aim_imp(nx: float, ny: float, duration_ms: int = 200) -> str:
    """Push the imp toward normalized screen direction (nx, ny) in [-1, 1].
    (-1, 0) = full left; (0, -1) = full up."""
    aim_at_normalized(_get_pad(), nx, ny, duration_ms=duration_ms)
    return f"aimed imp -> ({nx:.2f}, {ny:.2f}) for {duration_ms}ms"


@mcp.tool()
def recenter_imp_tool() -> str:
    """Reset the imp reference frame."""
    recenter_imp(_get_pad())
    return "recentered imp"


@mcp.tool()
def move_player_tool(direction: Direction, duration_ms: int = 500) -> str:
    """Move the player (left stick locomotion)."""
    move_player(_get_pad(), direction, duration_ms=duration_ms)
    return f"moved player {direction} for {duration_ms}ms"


def main() -> None:
    try:
        mcp.run()
    finally:
        if _pad is not None:
            _pad.close()


if __name__ == "__main__":
    main()
