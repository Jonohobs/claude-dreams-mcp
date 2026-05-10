# claude-dreams-mcp

An MCP server that lets an LLM agent drive PS5 *Dreams* Create mode via PS Remote Play (chiaki-ng).

## Status

Scaffold + R&D phase. The skeleton runs but the gamepad backend doesn't forward gyro yet and the capture backend doesn't work on GNOME-Wayland — both have TODOs pointing at the corrected approach. See `docs/architecture.md` for the plan and `docs/research/` for the supporting work.

## Why

PS5 *Dreams* is a deep creative tool with no API. Reaching it from a language-model agent requires (a) virtual controller input forwarded through PS Remote Play and (b) screen capture of the Remote Play window. This server exposes that loop as an MCP so any MCP-capable client (Claude Code, Goose, custom Python) can drive it.

It's also a research spike for a longer-horizon open creation engine — see `docs/roadmap.md`.

## Layout

```
src/claude_dreams_mcp/
  server.py     # FastMCP server entry point + tool definitions
  gamepad.py    # virtual DualSense (TODO: migrate from evdev/uinput to inputtino/uhid)
  capture.py    # screen capture (TODO: migrate from grim to PipeWire ScreenCast portal)
  motion.py     # imp motion helpers over right-stick mode
scripts/
  test_gamepad.py
docs/
  architecture.md
  roadmap.md
  research/     # R&D supporting the architecture decisions
```

## Hardware / system requirements

- Linux with a recent kernel (≥5.16 for `hid-playstation`).
- chiaki-ng installed (Flathub: `io.github.streetpea.Chiaki4deck`).
- A PS5 paired with the Linux host for Remote Play.
- For the corrected gamepad backend: `uhid` kernel module loaded, user in `input` group.
- For the corrected capture backend: PipeWire + xdg-desktop-portal-gnome.

## Known corrections in flight

| Component | Current (scaffold) | Correct | Reason |
|---|---|---|---|
| `gamepad.py` | python-evdev uinput | `inputtino` uhid | uinput isn't seen by `hid-playstation` → no gyro forwarding |
| `capture.py` | `grim` subprocess | `pipewire-capture` (ScreenCast portal) | grim is wlroots-only, doesn't work on GNOME-Wayland |

See `docs/research/01` and `docs/research/05` for the full reasoning.

## License

TBD.
