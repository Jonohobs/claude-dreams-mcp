# Dreams knowledge sources — research findings

Research date: 2026-05-10. Scope: where authoritative Dreams (PS4/PS5 game by Media Molecule) knowledge lives, for building a knowledge layer in the MCP.

## Summary

Dreams is **fossilized but breathing**: live support ended Sept 2023; indreams.me, browse, plays, remix all still online with no sunset announced. ~70-80% of needed knowledge is auto-extractable from TAPgiles + Fandom + Dreamschool; ~15-20% (workflow recipes, gadget I/O schema) is hand-curation. Realistic v1 timeline: 2-6 weeks part-time.

## Tier 1 sources (actively useful, scrapable text)

- **TAPgiles Dreams Documentation** — <https://tapgiles.com/docs/> — community-maintained HTML reference. Modes, gadgets, wiring, physics, project limits, icon reference. **Single best human-written reference.** Confidence: high.
- **Dreams Wiki (Fandom)** — <https://dreams.fandom.com/wiki/Gadgets> + secondary fork <https://dreamsuniverse.fandom.com/wiki/Logic_Tools/Components>. Per-gadget pages. Coverage uneven (mainline thorough, sound thin). Both 403'd WebFetch — scrapable with User-Agent header. Confidence: high content exists, medium accuracy.
- **Official Mm docs** — <https://docs.indreams.me/en> — beginner-oriented, "top tips", VR, releasing creations. Light on technical reference. Site still served (2026 copyright) but updates ceased post-Sept-2023.
- **Dreamschool (LadylexUK)** — <https://dreamskool.wordpress.com/logic-gadgets-index/> — curated YouTube-tutorial index per gadget. ~90+ logic gadgets in 8 categories. Last new content ~2021. Good for workflow recipes, bad as primary reference.
- **jaames/dreams-api** — <https://github.com/jaames/dreams-api> — TypeScript proxy with reverse-engineered indreams.me endpoints + auth header notes + file-format scratch. **Archived July 2023, read-only.** Still likely functional. **Action: fork it before bitrot.**

## Tier 2 (supporting)

- YouTube: **MartinNebelong** (game-ready asset sculpting), **LadylexUK** (Dreamschool), Mm's playlist `PLQkxWHNLI2CfB0Neu-enI2zJ-INWd6-cq`. Video-first → needs Whisper transcription before LLM-useful.
- **r/PS4Dreams** — ~20k members, quiet but not dead.
- Discord: `discord.gg/CyUrpwz2vb` ("Dreams CoMmunity"), creator servers. Living tacit knowledge, unstructured.

## Tool/gadget taxonomy (from Dreamschool's index)

| Category | Count |
|---|---:|
| Sensors & Input | ~14 |
| Logic & Processing | ~16 |
| Movers & Output | ~17 |
| Gameplay Gear | ~13 |
| Cameras & Lighting | ~9 |
| Connectors | ~7 |
| Sound | ~16 |
| **Total logic/wiring** | **~90+** |

Plus: Sculpt mode tools (Move, Stretch, Clone, Delete, Stamp Shape, Smear, Spray Paint, Looseness, Crop, Cutout), Style (Apply Fleck, Looseness, Impasto, Comb, Ruffle), Effects (Boil, Flow, Wave, Evaporate, Throb). Animation + sound get dedicated modes.

**No single canonical "all tools in one JSON" exists** — would need assembly.

## indreams.me as a data source

- Site **alive** in 2026 (creator pages dated Feb-Apr 2026 surfaced in search).
- Browse, profiles, comments, plays, remix lineage queryable.
- API undocumented but reverse-engineered by jaames/dreams-api — auth via PSN headers, proxied.
- **Risk:** archived project means breakage won't be fixed by upstream. Fork it.

## Living-vs-fossil game

**Fossilized but breathing.** Servers, indreams.me, browse/play/share all online. No new features, no PS5-native version, no announced sunset.

**Practical implication:** every gadget in the knowledge layer is "as of Sept 2023" and won't change. **Stable target = ideal for a knowledge layer.**

## Comparable AI-usable creator-tool KBs

Blender's docs (docs.blender.org) are RST-sourced, semantically structured, version-tagged — close to ideal MCP-resource shape. Dreams has nothing analogous. Game Builder Garage has even less.

**Conclusion:** you will be building the structured taxonomy yourself.

## PSVR + Move in Dreams

Confirmed. PSVR support added 22 July 2020. Move controllers enable 1:1 sculpting. Both work for full Create-mode use (assembly, wiring). Move-driven control surface may map more naturally to agent spatial reasoning than DS4 thumbstick.

## Curation effort assessment

- **Auto-extractable (~60%)**: TAPgiles + Fandom can be scraped and chunked into MCP resources. ~1 weekend.
- **Semi-auto (~25%)**: YouTube transcripts (Whisper) + manual quality filter. Days to weeks depending on coverage.
- **Hand-curated (~15%)**: workflow recipes ("third-person camera", "health bar wiring"), gadget interaction footguns, gadget I/O schema. **No source has this pre-structured.** Realistic: 2-6 weeks part-time for solid v1.

**Confidence:** high that sources to build a strong knowledge layer exist; medium that it's a one-person casual-timeline task. Main risk: jaames/dreams-api bitrotting.

## Recommended first move

1. Fork jaames/dreams-api today. Confirm it still works against indreams.me.
2. Scrape TAPgiles + Fandom into a flat JSON gadget catalogue (~weekend).
3. Define the gadget I/O schema (inputs, outputs, wires, common pitfalls) — start with the 10 most-used gadgets, expand iteratively.
4. Defer YouTube transcription until the structured catalogue proves valuable in agent runs.

## Sources
- <https://tapgiles.com/docs/>
- <https://dreams.fandom.com/wiki/Gadgets>
- <https://dreamsuniverse.fandom.com/wiki/Logic_Tools/Components>
- <https://docs.indreams.me/en>
- <https://dreamskool.wordpress.com/logic-gadgets-index/>
- <https://github.com/jaames/dreams-api>
- <https://indreams.me/>
- <https://www.gematsu.com/2023/04/dreams-to-end-live-support-on-september-1-as-media-molecule-shifts-focus-to-exciting-new-project>
- <https://blog.playstation.com/2020/06/30/ps-vr-support-comes-to-dreams-on-july-22/>
- <https://en.wikipedia.org/wiki/Dreams_(video_game)>
