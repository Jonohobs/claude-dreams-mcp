# Incoming: Hermes R&D digests 04–09 (2026-06-10)

Six Frankensteingine research digests are being produced by Hermes
(`worker-research` profile, board `frankenstengine-rnd`) and land in
`~/.hermes/research/frankenstengine/` (the container's only host mount).

After review, promote them into this directory as:
`04-sdf-sculpting-landscape.md`, `05-voice-to-scene-pipelines.md`,
`06-voice-stack.md`, `07-visual-scripting-options.md`,
`08-substrate-and-collab.md`, `09-ftue-landscape.md`.

Check progress: `docker exec -u hermes hermes /opt/hermes/.venv/bin/hermes kanban --board frankenstengine-rnd list`
Playable spike these inform: `~/code/dream-garage/` (parked build slices in its `docs/slices/`).
