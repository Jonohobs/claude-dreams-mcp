# Prior art: 3D-tool MCPs and agent-controlled creation — research findings

Research date: 2026-05-10. Scope: lessons from existing MCPs and harnesses controlling Blender, Houdini, Unity, etc., applicable to (a) this Dreams MCP, (b) the future open creation engine.

## Summary

Direct DCC analogues (Blender/Houdini/Unity MCPs) all assume rich text scene state — which Dreams **doesn't give you**. The closest analogue for Dreams MCP architecture is **Anthropic's computer-use tool + Claude Plays Pokémon**, not Blender MCP. Plan for a qualitatively different (input-sim + visual-verification) architecture.

## Project landscape

### Blender
- **ahujasid/blender-mcp** — the viral original. v1.5.5, actively maintained. Tools: `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code`, plus Poly Haven / Hyper3D Rodin / Sketchfab / Hunyuan3D integrations. Known issues: arbitrary-code-execution risk, Poly Haven flakiness, single-instance constraint.
- **VxASI/blender-mcp-vxai** — notable fork: more tools, multi-LLM (Ollama, Gemini), text-to-4D.
- **Official Blender MCP** at blender.org/lab/mcp-server — Blender Foundation building their own first-party MCP, lab/preview state.
- **gd3kr/BlenderGPT** — pre-MCP ancestor; pure `bpy` code-gen, no structured tool surface.
- **SceneCraft (arxiv 2403.01248)** — research agent: synthesizes scenes as Blender code via dual-loop optimization + structured spatial constraints. **88.9 vs 5.6 on "constraint passing" metric** vs BlenderGPT. Strongest quantitative evidence that structured > pure code-gen.

### Other DCC
- **oculairmedia/houdini-mcp** — 43 tools across 15 categories, RPyC-based. Notable patterns: `get_parameter_schema` precedes `set_parameter` (introspect-then-set), TTL caching, response truncation + AI summarization, retry/backoff.
- **ttiimmaacc/cinema4d-mcp** — 30+ fine-grained tools with `execute_python` escape hatch.
- **loonghao/dcc-mcp** — unified launcher for Maya/Houdini/3ds Max/Nuke.
- **CoplayDev/unity-mcp** — 5,800 stars, 40+ tools, hybrid Roslyn-compiled C# execution + scene-graph API. `batch_execute` advertised as 10-100× faster.
- **Roblox/studio-rust-mcp-server** — Roblox now ships MCP *inside Studio*. Tools: `run_code`, `insert_model`, `get_console_output`, `start_stop_play`, `run_script_in_play_mode`.
- **Unreal MCP Pro** — paid; 200+ command handlers across 39 categories.

### Cross-domain references
- **Figma MCP** — `get_design_context` + `get_screenshot` intentionally paired. Visual ground-truth checks the structured context. **Steal this pattern.**
- **Claude Plays Pokémon** — purest input+screenshot agent. Anthropic takeaway: *"the harness is the hard part."* Long-context embodied tasks "demand qualitatively different architectures" than coding agents.
- **Anthropic computer use** — action set: `screenshot, left_click, type, key, mouse_move, scroll, ...`. Closest analog to a DualSense surface.
- **Dreams** — live support ended Sept 2023; no API. `jaames/dreams-api` is network-RE only (indreams.me proxy), not Create-mode. Input-sim is the only path.

## Design patterns

### What works
- **Pure code-gen loses.** BlenderGPT-style "LLM writes raw `bpy` and we `exec` it" breaks on API drift, mode/context sensitivity, silent failures. SceneCraft's 88.9 vs 5.6 delta is the quantitative case. *High confidence.*
- **Validated structured tools win** — but every successful project keeps an `execute_python` / `run_code` escape hatch. Cinema4D, Houdini, Roblox, Blender all do this. *High confidence.*
- **Coarse-grained "manager" tools beat per-action tools at scale.** Unity's `manage_physics` bundles 21 actions. Roblox uses action-based dispatching to cut token consumption. *Medium-high.*
- **Introspect-before-mutate.** Houdini MCP requires `get_parameter_schema` before `set_parameter`. Substitutes for the type-checking LLMs hallucinate around. *High.*
- **Batch ops are not optional.** Unity's "10-100× faster" claim is real for any agent-controlled DCC — round-trip latency dominates. *High.*
- **Screenshot-as-ground-truth is now standard.** Blender added viewport screenshot; Figma pairs screenshot + structured context; Houdini has `capture_pane_screenshot`. **Nobody is doing screenshot-only for DCC** — they all combine VLM screenshots with scene introspection. *High.*
- **Goal-routing layer above tools.** `blender-ai-mcp`'s `router_set_goal(...)` gives downstream calls context. *Medium.*
- **Response truncation / summarization.** Houdini enforces size thresholds and AI-summarizes large responses. Scene-graph dumps blow context fast. *High.*

## Lessons for `claude-dreams-mcp`

1. **You cannot do scene introspection — you only have pixels.** Structurally closer to Claude Plays Pokémon / computer-use than to Blender MCP. Plan harness, memory, plan-iteration accordingly. Expect a *qualitatively different* architecture (Anthropic's own language).

2. **Steal Figma's `get_design_context` + `get_screenshot` pairing — except your "context" is your server-side world-model.** Maintain "what is currently selected / what mode / what's on the gadget grid" from input history. Expose it as a tool alongside screenshots. Don't make the VLM re-derive it every frame.

3. **Action surface should mirror Anthropic computer-use, not raw DualSense bytes.** Expose semantic actions (`enter_build_mode`, `place_primitive(type, location_hint)`, `grab_imp`, `rotate_imp(axis, degrees)`) that the server decomposes into stick/button sequences. Raw input is the escape hatch (cf. `execute_python`).

4. **Introspect-before-mutate has no Dreams analog → invent one.** After every semantic action, automatically screenshot + run a cheap VLM "did the expected thing happen?" check. Bake into the harness, don't leave it to the agent to remember.

5. **Batch is more critical here than for Blender.** A controller action takes 100-500ms wall-clock; round-tripping to the model between each is fatal. Expose `macro` / `sequence` tools that run K actions before screenshot.

6. **Keep a goal-routing layer.** Dreams' Create mode is deeply modal (build/sculpt/wiring/animation/test play). The agent will get lost. A `set_intent(...)` tool that the server uses to filter the action space prevents off-mode tool calls.

7. **For the future engine: design the native AI API to BE the canonical surface, then implement input-sim as a thin shim on top for testing/regression.** Roblox's "built-in MCP that ships with Studio" is the model. Every external MCP for Unity/Unreal is racing to match what an in-engine MCP gives for free. Reusing input-sim for end-to-end test harness is a known good pattern from game QA — don't throw it away when the native API arrives.

8. **Telemetry from day 1.** Per-tool success/failure rates so you know which semantic actions the VLM verification keeps flagging.

## Sources
- <https://github.com/ahujasid/blender-mcp>
- <https://www.blender.org/lab/mcp-server/>
- <https://github.com/gd3kr/BlenderGPT>
- <https://arxiv.org/abs/2403.01248>
- <https://github.com/oculairmedia/houdini-mcp>
- <https://github.com/ttiimmaacc/cinema4d-mcp>
- <https://github.com/loonghao/dcc-mcp>
- <https://github.com/CoplayDev/unity-mcp>
- <https://github.com/Roblox/studio-rust-mcp-server>
- <https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/>
- <https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool>
- <https://www.latent.space/p/how-claude-plays-pokemon-was-made>
- <https://github.com/jaames/dreams-api>
