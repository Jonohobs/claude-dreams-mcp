# Architecture

Updated 2026-05-10 based on R&D findings in `docs/research/`.

## What this is

An MCP server that lets an LLM agent drive PS5 *Dreams* Create mode by:

1. Capturing the chiaki-ng (PS Remote Play) window as PNG frames.
2. Receiving tool calls from the agent and translating them into a stream of DualSense events (sticks, buttons, gyro).
3. Forwarding those events upstream to the PS5 via a `uhid` virtual DualSense that `hid-playstation` binds, so SDL2 / chiaki-ng treats it as a real DualSense and forwards motion data.

## Why an MCP and not a regular agent harness

Dreams has no API — `jaames/dreams-api` is a reverse-engineered indreams.me proxy, not a Create-mode bridge. Input simulation + screenshot vision is the only path. The MCP is the right shape because it exposes a stable, language-model-friendly tool surface (`press_button`, `tilt_imp`, `screenshot`) that any MCP-capable client (Claude Code, Goose, custom Python) can drive.

## Critical correction from R&D

The initial scaffold used `python-evdev` + `uinput` for the virtual gamepad and `grim` for screen capture. Both are wrong on this stack:

- **Gamepad:** plain uinput is **not** recognized as a DualSense by `hid-playstation`, so chiaki-ng won't forward gyro. Use **`inputtino`** (uhid-based, production-used by Sunshine/Wolf) — see `docs/research/01`.
- **Capture:** `grim` is wlroots-only and doesn't work on GNOME-Wayland. Use **ScreenCast portal + PipeWire** (`pipewire-capture` Python package) — see `docs/research/05`.

These corrections are tracked as TODOs in `src/claude_dreams_mcp/gamepad.py` and `capture.py` so the scaffold still runs for sticks/buttons testing while the real backends are integrated.

## Component diagram

```
            ┌──────────────────────────┐
            │  Agent (Claude/Groq/etc) │
            └──────────────┬───────────┘
                           │ MCP tool calls
            ┌──────────────▼───────────┐
            │  claude-dreams-mcp       │
            │                          │
            │  ┌────────────┐          │
            │  │ tools.py   │ semantic │
            │  └────┬───────┘ surface  │
            │       │                  │
            │  ┌────▼──────┐           │
            │  │ gamepad.py│ inputtino │
            │  └────┬──────┘ (uhid)    │
            │  ┌────▼──────┐           │
            │  │ capture.py│ PipeWire  │
            │  └────┬──────┘ ScreenCast│
            └───────┼──────────────────┘
                    │
            uhid /dev/uhid           PipeWire
                    │                       │
            ┌───────▼───────┐    ┌──────────▼───────┐
            │ hid-playstn   │    │ chiaki-ng window │
            │ (kernel)      │    │ (Qt6 on Wayland) │
            └───────┬───────┘    └──────────▲───────┘
                    │                       │
            ┌───────▼───────┐                │
            │ SDL2 sees     │                │
            │ a DualSense   │                │
            └───────┬───────┘                │
                    │                        │
            ┌───────▼────────────────────────┘
            │ chiaki-ng (forwards to PS5)
            │
        upstream: input + gyro
        downstream: video
            │
        ┌───▼───┐
        │ PS5   │
        │ Dreams│
        └───────┘
```

## Tool surface

Two layers — keep the agent on the upper layer.

### Semantic (preferred for agents)
- `screenshot()` — current Dreams view (PNG, downscaled to ≤720p to keep image-token budget sane on multimodal models that bill by tile count).
- `tilt_imp(direction, magnitude, duration_ms)` — motion-language imp navigation. Backed by right-stick mode (Accessibility → Controllers must be set).
- `aim_imp(nx, ny, duration_ms)` — push imp toward normalized screen direction.
- `recenter_imp()` — reset reference frame.
- `move_player(direction, duration_ms)` — left-stick locomotion.
- `press_button(button, hold_ms)` — face buttons, dpad, shoulders. Constrained to a flat list.
- `set_intent(mode)` — goal-routing layer (`build`, `sculpt`, `wiring`, `animation`, `test_play`). Server filters action space accordingly.

### Raw (escape hatch — cf. `execute_python` in Blender MCP)
- `stick(side, x, y, duration_ms)`
- `trigger(side, value)`
- `dpad(x, y)`
- `hold_button` / `release_button`

## Key design patterns borrowed from DCC-MCP prior art

(See `docs/research/06` for derivation.)

- **Screenshot + server-side world model.** Maintain "current mode / selected tool / imp position estimate" from input history. Surface as a `get_context()` tool alongside `screenshot()`. Don't make the VLM re-derive every frame.
- **Verify-after-act.** After each semantic action, the server takes a quick low-res screenshot and runs a cheap VLM check ("did the expected thing happen?"). Replaces the introspect-before-mutate idiom from DCC MCPs.
- **Batch / macro tools.** Round-trip latency dominates a 100-500ms-per-action surface. Expose `macro([action1, action2, ...])` so multiple inputs flow before the next screenshot.
- **Goal-routing.** `set_intent(mode)` filters which tools are valid. Prevents off-mode tool calls in Dreams' deeply modal Create environment.

## Recommended agent default

**Llama 4 Scout on Groq** as the primary model — ~$0.0007/turn, ~$7/8h sustained autonomous run, sub-second inference, native vision, function calling. Fallback: Gemini 2.5 Flash (~$27/8h) if Scout reasoning falls short. Claude Sonnet only for in-the-loop debugging (~$216/8h is prohibitive for unattended runs). See `docs/research/04`.

## Knowledge layer (deferred)

Dreams expertise is sparse in any LLM's training corpus. The MCP will eventually expose curated Dreams resources (gadget reference, workflow recipes, indreams.me search) — see `docs/research/07`. Not in scope for v0; the first goal is to prove the input + capture loop works.

## Relationship to the future open creation engine

This MCP is also a **research spike** for a longer-horizon project: an open-source Dreams-/Game-Builder-Garage-inspired XR/VR/AR creation engine on Godot + OpenXR, with AI agents as first-class participants. The MCP's semantic tool surface (`tilt_imp`, `set_intent`, etc.) is design input for that engine's eventual native AI API — same vocabulary, different backend (engine-API instead of input-sim). See `docs/roadmap.md`.
