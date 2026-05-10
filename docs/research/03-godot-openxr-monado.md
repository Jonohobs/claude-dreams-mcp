# Godot + OpenXR + Monado — research findings

Research date: 2026-05-10. Scope: foundation stack for the future open Dreams-/GBG-inspired creation engine.

## Summary

Godot 4.6 + `godot_openxr_vendors` + `godot-xr-tools` over Monado is the correct starter stack on Linux. Develop without a headset using Monado's **remote driver** (GUI pose control, scriptable via port 4242) — more flexible than the simulated driver.

## Key findings

### Godot status (high confidence)
- **Godot 4.6** released Jan 2026: OpenXR 1.1 with 1.0 fallback, Spatial Entities (anchors / plane detection), frame synthesis with depth, Khronos loader APK.
- Action maps are upgraded to 1.1 — **incompatible with earlier Godot versions**.
- Core OpenXR driver ships in-engine; vendor plugins are external.

### Two essential plugins
- `godot_openxr_vendors` <https://github.com/GodotVR/godot_openxr_vendors> — Meta/Pico/HTC/Khronos loaders + vendor extensions + Project Setup Wizard. Updated Feb 2026.
- `godot-xr-tools` <https://github.com/GodotVR/godot-xr-tools> — locomotion, pickup, UI, hand interactions. Updated Apr 2026.

### Linux gotchas (medium confidence)
- Wayland + OpenXR session handoff still rough on GNOME. **Use X11 session** for serious dev sessions if hitting black-screen issues.
- NVIDIA + Monado needs specific env vars to avoid input lag.

### Monado state (high confidence)
Distro-packaged on Arch/Fedora/Ubuntu. Recommended OpenXR runtime on Linux. It's the open-source foundation under Google AndroidXR, Pico, Snapdragon Spaces, NVIDIA CloudXR, Hololight.

### Developing without a headset
Two options:

**A — Simulated driver (zero-config).** Unplug all real HMDs; Monado falls back automatically. Verify with `monado-service` + `monado-cli test`.

**B — Remote driver (better; GUI-controllable).** Create `~/.config/monado/config_v0.json`:
```json
{ "active": "remote", "remote": { "version": 0, "port": 4242 } }
```
Or set `P_OVERRIDE_ACTIVE_CONFIG=remote`. Run `monado-service`, then `monado-gui`, then click "Remote" → sliders for HMD pose and controller buttons.

**Recommendation: remote driver.** The undocumented-but-discoverable port 4242 protocol lets an agent script the remote driver and *be* a user — useful for headless agent testing.

Point apps at Monado via `XR_RUNTIME_JSON=/usr/share/openxr/1/openxr_monado.json` or install as system runtime at `/etc/xdg/openxr/1/active_runtime.json`.

### OpenXR extensions exposed by Godot (high confidence)
- Hand tracking (`XR_EXT_hand_tracking` + FB mesh/capsules) — bridges to Godot Humanoid Skeleton.
- Passthrough — via env blend modes, vendor plugin handles platform specifics.
- Body tracking — via Humanoid Skeleton retargeting.
- Eye tracking — `XR_ANDROID_eye_tracking` and Meta variants via vendor plugin.
- Spatial Entities (anchors, plane detection) in 4.6.
- Face tracking — Meta/Pico.

### Gaps that matter for a creation engine
- Spatial-persistence / scene-mesh extensions are vendor-fragmented.
- Collaborative / multi-user anchoring is not standardized.
- Haptics is minimal.
- Controller introspection for non-standard input devices needs manual action-map work.

### Open creation-engine landscape (medium confidence)
Prior art surveyed:
- **V-Sekai** <https://github.com/V-Sekai/v-sekai-game> — social VR on a Godot fork, MIT. Closest spiritual neighbour. Needs custom engine build.
- **BarkVR** <https://github.com/zodiepupper/barkvr> — Godot 4.x decentralized social-XR creativity, early WIP.
- **bevy_mod_openxr** (was `bevy_oxr`) — Rust, data-driven, smaller ecosystem.
- Closed/Unity peers: Resonite, Open Brush, xrdesktop.

**Unfilled niche:** in-VR scene editor with first-class agent co-editing, open source, Godot-native, Monado-first. V-Sekai is social-shaped, BarkVR is too early, nothing targets Dreams-style creation primitives + AI peers.

### Agent-API prior art
- `Coding-Solo/godot-mcp` — bundled GDScript ops + scene/node creation.
- `HaD0Yun/godot-mcp` (GoPeak) — 95+ tools incl. GDScript LSP + DAP.
- Unity-MCP, Unreal MCPs, Roblox built-in MCP.

**Gap:** none target multi-agent live co-editing inside an XR session — this project's lane.

## Recommended starter stack
- **Engine:** Godot 4.6.x stable, Vulkan, Forward+ desktop.
- **XR plugins:** `godot_openxr_vendors` (Khronos loader) + `godot-xr-tools`.
- **Runtime:** Monado from distro, configured for **remote driver** during agent dev; simulated driver as fallback. `XR_RUNTIME_JSON` pinned in dev env.
- **Agent bridge:** fork `Coding-Solo/godot-mcp` and extend with scene-graph diff/patch ops + in-game RPC (`WebSocketPeer`). Hook Monado's remote port (4242) into the same agent harness.
- **Headset later:** Quest 4 via Link + Monado/SteamVR shim, or Valve Deckard (if it ships) native Monado.

## Risks
- Wayland + OpenXR on GNOME still wobbly.
- Godot has no built-in collaborative editing — CRDT/OT or single-writer-locks is on you.
- Monado remote driver protocol is under-documented — agent integration needs source-diving.
- No standard OpenXR shared-anchor extension — federation is on you.
- `godot-xr-tools` is community-paced — expect to fork pieces.

## Sources
- <https://godotengine.org/article/godot-xr-update-mar-2026/>
- <https://github.com/GodotVR/godot_openxr_vendors>
- <https://github.com/GodotVR/godot-xr-tools>
- <https://monado.freedesktop.org/getting-started.html>
- <https://monado.pages.freedesktop.org/monado/group__drv__simulated.html>
- <https://redstrate.com/blog/2023/11/using-openxr-without-real-hardware/>
- <https://github.com/V-Sekai/v-sekai-game>
- <https://github.com/zodiepupper/barkvr>
- <https://github.com/Coding-Solo/godot-mcp>
