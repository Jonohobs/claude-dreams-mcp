"""Virtual DualSense-shaped gamepad over Linux uinput.

Note: this creates an evdev/uinput device (gamepad-class). chiaki-ng identifies
real DualSenses by USB VID/PID at the HID layer (Sony 054c:0ce6) when deciding
to forward gyro upstream. To pass as a DualSense for gyro forwarding through
chiaki, this likely needs to be promoted to a uhid device with the matching
HID descriptor — TODO once button/stick path is verified.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass

from evdev import UInput, ecodes, AbsInfo


BUTTONS = {
    "cross": ecodes.BTN_SOUTH,
    "circle": ecodes.BTN_EAST,
    "square": ecodes.BTN_WEST,
    "triangle": ecodes.BTN_NORTH,
    "l1": ecodes.BTN_TL,
    "r1": ecodes.BTN_TR,
    "l3": ecodes.BTN_THUMBL,
    "r3": ecodes.BTN_THUMBR,
    "share": ecodes.BTN_SELECT,
    "options": ecodes.BTN_START,
    "ps": ecodes.BTN_MODE,
}

STICK_RANGE = (-32768, 32767)
TRIGGER_RANGE = (0, 255)
GYRO_RANGE = (-32768, 32767)

ABS_AXES = {
    "left_x": (ecodes.ABS_X, STICK_RANGE),
    "left_y": (ecodes.ABS_Y, STICK_RANGE),
    "right_x": (ecodes.ABS_RX, STICK_RANGE),
    "right_y": (ecodes.ABS_RY, STICK_RANGE),
    "l2": (ecodes.ABS_Z, TRIGGER_RANGE),
    "r2": (ecodes.ABS_RZ, TRIGGER_RANGE),
    "dpad_x": (ecodes.ABS_HAT0X, (-1, 1)),
    "dpad_y": (ecodes.ABS_HAT0Y, (-1, 1)),
}


@dataclass
class GamepadConfig:
    name: str = "claude-dreams-virtual-dualsense"
    vendor: int = 0x054C
    product: int = 0x0CE6
    version: int = 0x0100


class VirtualDualSense:
    def __init__(self, config: GamepadConfig | None = None) -> None:
        self.config = config or GamepadConfig()
        self._ui: UInput | None = None

    def open(self) -> None:
        capabilities = {
            ecodes.EV_KEY: list(BUTTONS.values()),
            ecodes.EV_ABS: [
                (code, AbsInfo(value=0, min=lo, max=hi, fuzz=0, flat=0, resolution=0))
                for (code, (lo, hi)) in ABS_AXES.values()
            ],
        }
        self._ui = UInput(
            events=capabilities,
            name=self.config.name,
            vendor=self.config.vendor,
            product=self.config.product,
            version=self.config.version,
        )

    def close(self) -> None:
        if self._ui is not None:
            self._ui.close()
            self._ui = None

    def _require(self) -> UInput:
        if self._ui is None:
            raise RuntimeError("gamepad not open — call open() first")
        return self._ui

    def press(self, button: str, hold_ms: int = 80) -> None:
        ui = self._require()
        code = BUTTONS[button]
        ui.write(ecodes.EV_KEY, code, 1)
        ui.syn()
        time.sleep(hold_ms / 1000)
        ui.write(ecodes.EV_KEY, code, 0)
        ui.syn()

    def hold(self, button: str) -> None:
        ui = self._require()
        ui.write(ecodes.EV_KEY, BUTTONS[button], 1)
        ui.syn()

    def release(self, button: str) -> None:
        ui = self._require()
        ui.write(ecodes.EV_KEY, BUTTONS[button], 0)
        ui.syn()

    def stick(self, side: str, x: float, y: float) -> None:
        ui = self._require()
        if side not in ("left", "right"):
            raise ValueError(f"side must be 'left' or 'right', got {side!r}")
        x_code, x_range = ABS_AXES[f"{side}_x"]
        y_code, y_range = ABS_AXES[f"{side}_y"]
        ui.write(ecodes.EV_ABS, x_code, _scale(x, x_range))
        ui.write(ecodes.EV_ABS, y_code, _scale(y, y_range))
        ui.syn()

    def trigger(self, side: str, value: float) -> None:
        ui = self._require()
        if side not in ("l2", "r2"):
            raise ValueError(f"side must be 'l2' or 'r2', got {side!r}")
        code, rng = ABS_AXES[side]
        ui.write(ecodes.EV_ABS, code, _scale(value, rng, lo_in=0.0, hi_in=1.0))
        ui.syn()

    def dpad(self, x: int, y: int) -> None:
        ui = self._require()
        ui.write(ecodes.EV_ABS, ecodes.ABS_HAT0X, x)
        ui.write(ecodes.EV_ABS, ecodes.ABS_HAT0Y, y)
        ui.syn()


def _scale(value: float, out_range: tuple[int, int], lo_in: float = -1.0, hi_in: float = 1.0) -> int:
    value = max(lo_in, min(hi_in, value))
    lo, hi = out_range
    span_in = hi_in - lo_in
    span_out = hi - lo
    return int(lo + (value - lo_in) * span_out / span_in)


@contextmanager
def virtual_dualsense(config: GamepadConfig | None = None):
    pad = VirtualDualSense(config)
    pad.open()
    try:
        yield pad
    finally:
        pad.close()
