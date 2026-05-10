"""Standalone smoke test for the virtual gamepad.

Run with:
    python -m scripts.test_gamepad

While running, in another terminal:
    sudo evtest        # pick the claude-dreams-virtual-dualsense device

You should see KEY and ABS events as the script presses/releases inputs.
Requires uinput permissions — see README.md or run as root once to verify.
"""
from __future__ import annotations

import time

from claude_dreams_mcp.gamepad import virtual_dualsense


def main() -> None:
    with virtual_dualsense() as pad:
        print("virtual gamepad open. running 5s of input...")
        time.sleep(1)
        pad.press("cross")
        time.sleep(0.3)
        pad.press("circle")
        time.sleep(0.3)
        pad.stick("right", 1.0, 0.0)
        time.sleep(0.5)
        pad.stick("right", 0.0, 0.0)
        pad.trigger("r2", 0.7)
        time.sleep(0.3)
        pad.trigger("r2", 0.0)
        pad.dpad(1, 0)
        time.sleep(0.3)
        pad.dpad(0, 0)
        print("done.")


if __name__ == "__main__":
    main()
