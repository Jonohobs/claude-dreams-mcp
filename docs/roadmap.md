# Roadmap

## Phase 0 — scaffold (DONE)
- Repo structure, pyproject, MCP server skeleton, evdev/uinput gamepad stub, grim capture stub.

## Phase 1 — correct the input + capture backends
- [ ] Replace `python-evdev` uinput gamepad with `inputtino` Python bindings (uhid-based DualSense). Validate `hid-playstation` binds. Validate SDL2 sees motion sensors.
- [ ] Replace `grim` capture with ScreenCast portal + PipeWire (`pipewire-capture` package). Validate one-time source picker, then silent streaming.
- [ ] One-time setup: udev rule for `/dev/uhid`, user in `input` group.
- [ ] Smoke test: `scripts/test_gamepad.py` shows motion events in `evtest` for the virtual DualSense.

**Acceptance:** chiaki-ng connected to PS5, virtual DualSense paired, gyro forwarded such that the imp moves in response to synthetic gyro values.

### Phase 1 alt-path — chiaki-ng DSU motion-source extension

Considered *before* committing to the inputtino/uhid plumbing. If feasible, it's the cleaner architecture.

R&D found that chiaki-ng does **not** currently implement a DSU (cemuhook) motion-source client. Adding one would mean:
- chiaki-ng can receive gyro/accel from any DSU server process over UDP.
- Our MCP becomes a tiny DSU server emitting synthetic motion alongside the regular virtual gamepad (which only needs sticks/buttons → uinput is fine for that).
- Decouples gyro from controller identity — no fake DualSense needed for the motion path.
- Useful upstream (phone-as-gyro for chiaki is a known community want), increasing odds the PR lands.

**Spike (~1 day):** read chiaki-ng's input pipeline (C++/Qt6), assess where a DSU client would slot in (parallel to the SDL2 sensor reader or replacing it), check whether the maintainer (streetpea) is open to the addition via an issue first.

**Decision gate:** if spike says ≤1 week to a working patch, take the alt-path. If it's a multi-week C++ project, fall back to `inputtino` and revisit later.

## Phase 2 — semantic tool surface + world model
- [ ] Implement `set_intent(mode)` and server-side action filtering per mode.
- [ ] Build server-side world model from input history (current mode, last-known selection, imp position estimate).
- [ ] Add `get_context()` tool returning the world model alongside `screenshot()`.
- [ ] Add `verify_last_action()` — cheap VLM check that the screenshot reflects the expected post-action state.
- [ ] Add `macro([...])` for batched inputs without per-action round-trip.

**Acceptance:** Claude can navigate from PS5 home into a blank Dreams scene via semantic tools.

## Phase 3 — agent harness + provider swap
- [ ] Custom Python loop using `mcp` SDK + `openai` client pointed at Groq.
- [ ] Llama 4 Scout as default model. Downscale screenshots to ≤720p to control image token cost.
- [ ] Per-tool success/failure telemetry (CSV log, used for tool surface iteration).
- [ ] Goose as alternative harness for A/B against other providers.

**Acceptance:** sustained autonomous Create-mode session ≥30 min at <$0.50/hr cost.

## Phase 4 — knowledge layer
- [ ] Fork `jaames/dreams-api` (before bitrot) and verify against current indreams.me.
- [ ] Scrape TAPgiles + Fandom into a flat gadget JSON.
- [ ] Define gadget I/O schema (inputs, outputs, wires, footguns). Seed with the 10 most-used gadgets.
- [ ] Expose as MCP resources (`dreams://gadget/<name>`, `dreams://workflow/<name>`).
- [ ] `lookup_dreams_tool(query)` fuzzy-search tool.

**Acceptance:** Claude can complete "sculpt a simple primitive from a sphere" workflow using only screenshot + knowledge-layer context.

## Phase 5 — long-running autonomous mode
- [ ] Checkpoint hooks (auto-save scene every N minutes).
- [ ] Sanity gates (detect input-loop / no-progress, halt).
- [ ] Bounded-scope session goals ("build a small house from a sphere") with explicit termination criteria.

**Acceptance:** 8-hour unattended session that produces inspectable, non-degenerate output.

---

## Parallel track — the open creation engine (no name yet)

Long-horizon. Starts after Phase 2 of the MCP gives us a concrete vocabulary for "what tools an AI needs to make 3D content."

### Phase E0 — design + decision
- Design pillars: XR/VR/AR-native, AI-agents-as-peers, Linux-first, OpenXR-targeted (not headset-specific).
- Decide solo vs collaborator-recruiting model.

### Phase E1 — engine substrate
- Godot 4.6 + `godot_openxr_vendors` + `godot-xr-tools`.
- Monado as default OpenXR runtime; remote driver for headless agent dev.
- Develop primarily in flatscreen + DualSense gyro initially; Monado remote driver for OpenXR code path validation.

### Phase E2 — spatial input substrate (no-headset mode)
- PS Move + PS3 Eye via Monado's PSMV driver → OpenXR controllers in Godot.
- Move Navigation Controller for analog stick (paired via psmoveapi).
- Webcam head tracking via opentrack or MediaPipe for parallax.
- Touchscreen as direct 2D manipulation surface.
- This is the differentiating wedge: "VR-class spatial creation rig on $50 of used hardware most creators already own."

### Phase E3 — agent-as-peer API
- Native scene-graph introspection + edit API exposed to agents via in-engine MCP (cf. Roblox model).
- Reuse the MCP semantic vocabulary (`set_intent`, `tilt_imp`/`tilt_cursor`, etc.) so the same agent can drive Dreams (input-sim) or the engine (native API) with minimal prompt changes.

### Phase E4 — multi-user / multi-agent co-edit
- WebSocket / CRDT for collaborative scenes.
- Agent presence as a first-class user type (agent gets an avatar + input source).

### Headset acquisition
Defer until Quest 4 launches or Valve Deckard ships. The cheap stack covers Phases E1-E3.
