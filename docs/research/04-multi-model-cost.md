# Multi-model agent stack — cost + architecture findings

Research date: 2026-05-10. Scope: cheapest viable model stack for sustained autonomous Dreams Create-mode play.

## Summary

**Llama 4 Scout on Groq at ~$7/8h is the cheapest viable single-model stack.** Native vision + tool use + sub-second inference + OpenAI-compatible API. Claude Sonnet at ~$216/8h is ~30× more expensive — only justified if Scout's reasoning falls short for Dreams' menu navigation.

Two-stage (VLM caption → text reasoner) is **not** worth it — Hermes 4 has no vision variant; the caption hop adds latency and lossy bottleneck.

## Pricing table (~3K text input + 1 screenshot ~1.5K image tokens + 500 output per turn; 9,600 turns / 8h)

| Model (provider) | $/M in | $/M out | $/turn | $/8h | Vision | Tool use |
|---|---:|---:|---:|---:|---|---|
| Claude Sonnet 4.6 | $3.00 | $15.00 | ~$0.0225 | ~$216 | yes | excellent |
| Claude Haiku 4.5 | $1.00 | $5.00 | ~$0.0075 | ~$72 | yes | very good |
| Gemini 2.5 Flash | $0.30 | $2.50 | ~$0.0028 | ~$27 | yes (image ~258 tok flat) | good |
| Gemini 2.5 Flash-Lite | ~$0.10 | ~$0.40 | ~$0.0007 | ~$7 | yes | adequate |
| GPT-5-mini | $0.25 | $2.00 | ~$0.0023 | ~$22 | yes | very good |
| GPT-5 | $1.25 | $10.00 | ~$0.0113 | ~$108 | yes | excellent |
| **Llama 4 Scout (Groq)** | **$0.11** | **$0.34** | **~$0.0007** | **~$7** | native multimodal | function calling |
| Qwen3-VL-235B (OpenRouter) | ~$0.80 | ~$0.80 | ~$0.0044 | ~$42 | yes | strong, GUI-tuned |
| Hermes 4 70B (OpenRouter) | $0.13 | $0.40 | ~$0.0009 | ~$8 | **no vision** | function calling |
| GPT-OSS 120B (Groq) | $0.15 | $0.60 | ~$0.0011 | ~$10 | no | yes |

Numbers conservative; real $/8h likely 0.7-1.4× these depending on prompt caching, screenshot resolution, agent chattiness.

## Recommended architecture

**Primary: Llama 4 Scout on Groq, single model.** ~$0.0007/turn, ~$7/8h. ~594 TPS so a turn finishes in well under 1s, leaving most of the 3s budget for screenshot capture + dispatch.

**Fallback if Scout reasoning is too weak:** Gemini 2.5 Flash single-model. ~$27/8h. Stronger reasoning; image tokens nearly free at ~258 each. A/B test on recorded screenshots before committing.

**Two-stage Qwen3-VL caption + Hermes 4 70B reason:** ~$0.005/turn, ~$48/8h. **Don't recommend** — 7× more expensive than Scout, adds 200-500ms network latency, caption becomes lossy bottleneck. Only worth it if Scout vision empirically fails and Qwen3-VL strictly beats it on Dreams iconography.

## Honest constraints

- **Hermes 4 is text-only in 2026.** No Nous vision variant. Gemma-4-Hermes-VLM MLX merge is a hobby project, not production.
- **Groq tool use:** Llama 4 Scout, Qwen3-32B, GPT-OSS expose OpenAI-compatible function calling. Reliable for ≤5 flat-arg tools like `press_button`/`tilt_imp`. Less reliable than Claude/GPT for nested or 20+ schemas — keep the MCP surface narrow.
- **Hermes 4 OpenRouter has documented tool-schema 400 errors** with large tool sets (issue #13927). Mitigation: <10 tools, or use Nous's own portal.
- **Llama 4 Scout image tokens are variable** (dynamic tile count). A 1080p chiaki frame can blow up to 5-8K image tokens. **Downscale screenshots to ~512-720p** or silently 3× the bill.
- **3s loop is comfortable** for any Groq model (<1s inference) and Gemini Flash (~1s). Claude Sonnet (~3-5s) and GPT-5 (~3-8s) will occasionally blow past the 3s cadence.

## Harness recommendation

- **Custom Python loop** — `mcp` Python SDK + `openai` client pointed at Groq's OpenAI-compatible endpoint. ~200 lines. Tighter control over screenshot batching and 3s cadence. Probably the right call for a real-time loop.
- **Goose (Block's open-source agent)** — native MCP client, swappable provider. Worth keeping as an alternative for quick A/B against different providers without rewriting.
- **Aider** — code-editing shaped, not a fit.

## Empirical validation needed

Before committing to Scout:
1. Record 50-100 Dreams Create-mode screenshots covering menu, sculpt, wiring, animation modes.
2. A/B Scout vs Gemini Flash vs Claude Haiku on "describe this screen + propose next action" — measure correctness manually.
3. Measure real $/turn including actual image token counts (downscaled vs native).

## Sources
- <https://groq.com/pricing>
- <https://console.groq.com/docs/model/meta-llama/llama-4-scout-17b-16e-instruct>
- <https://platform.claude.com/docs/en/about-claude/pricing>
- <https://ai.google.dev/gemini-api/docs/pricing>
- <https://openai.com/api/pricing/>
- <https://openrouter.ai/nousresearch/hermes-4-70b>
- <https://openrouter.ai/qwen>
- <https://github.com/NousResearch/hermes-agent/issues/13927>
- <https://goose-docs.ai/>
- <https://artificialanalysis.ai/providers/groq>
