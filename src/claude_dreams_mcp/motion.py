"""Dreams imp motion helpers — Claude-friendly tool surface over right-stick mode.

These wrap raw stick deltas in motion-language vocabulary (tilt, sweep, recenter)
because that maps to the corpus a VLM has seen describing motion control. The
PS5 is configured for right-stick imp mode (Settings → Accessibility → Controllers),
so the implementation is just stick deflection over a duration.
"""
from __future__ import annotations

import math
import time
from typing import Literal

from .gamepad import VirtualDualSense


Direction = Literal[
    "up", "down", "left", "right",
    "upper-left", "upper-right", "lower-left", "lower-right",
]


_DIR_VEC = {
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
    "upper-left": (-0.7071, -0.7071),
    "upper-right": (0.7071, -0.7071),
    "lower-left": (-0.7071, 0.7071),
    "lower-right": (0.7071, 0.7071),
}


def tilt_imp(
    pad: VirtualDualSense,
    direction: Direction,
    magnitude: float = 0.5,
    duration_ms: int = 200,
) -> None:
    """Move the imp in a direction by holding the right stick for duration_ms.

    magnitude: 0.0–1.0. 1.0 = full deflection.
    """
    magnitude = max(0.0, min(1.0, magnitude))
    dx, dy = _DIR_VEC[direction]
    pad.stick("right", dx * magnitude, dy * magnitude)
    time.sleep(duration_ms / 1000)
    pad.stick("right", 0.0, 0.0)


def aim_at_normalized(
    pad: VirtualDualSense,
    nx: float,
    ny: float,
    duration_ms: int = 200,
) -> None:
    """Push the right stick toward (nx, ny) normalized [-1, 1] for duration_ms."""
    pad.stick("right", nx, ny)
    time.sleep(duration_ms / 1000)
    pad.stick("right", 0.0, 0.0)


def recenter_imp(pad: VirtualDualSense) -> None:
    """Press the recenter binding. In Dreams motion mode this is the touchpad
    or PS button hold depending on settings — TODO: confirm Jonathan's binding."""
    pad.press("ps", hold_ms=120)


def move_player(
    pad: VirtualDualSense,
    direction: Direction,
    duration_ms: int = 500,
) -> None:
    """Move the player/character via left stick (locomotion in Create-mode walk)."""
    dx, dy = _DIR_VEC[direction]
    pad.stick("left", dx, dy)
    time.sleep(duration_ms / 1000)
    pad.stick("left", 0.0, 0.0)
