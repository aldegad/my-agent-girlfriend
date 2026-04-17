# My Agent Girlfriend

A playful local desktop companion project for Codex.

<p align="center">
  <img src="assets/base/base-character-v1-approved.png" alt="Base character (v1, approved)" width="420" />
</p>

## Preset gallery

| neutral_smile | cheerful_bright | bashful_blush | playful_tease |
| :---: | :---: | :---: | :---: |
| <img src="assets/presets/neutral_smile.png" width="180" alt="neutral_smile" /> | <img src="assets/presets/cheerful_bright.png" width="180" alt="cheerful_bright" /> | <img src="assets/presets/bashful_blush.png" width="180" alt="bashful_blush" /> | <img src="assets/presets/playful_tease.png" width="180" alt="playful_tease" /> |
| **curious_tilt** | **surprised_wide** | **pouty** | **worried** |
| <img src="assets/presets/curious_tilt.png" width="180" alt="curious_tilt" /> | <img src="assets/presets/surprised_wide.png" width="180" alt="surprised_wide" /> | <img src="assets/presets/pouty.png" width="180" alt="pouty" /> | <img src="assets/presets/worried.png" width="180" alt="worried" /> |
| **teary** | **crying_closed_eyes** | **pleading_look_up** | **apology_look_up** |
| <img src="assets/presets/teary.png" width="180" alt="teary" /> | <img src="assets/presets/crying_closed_eyes.png" width="180" alt="crying_closed_eyes" /> | <img src="assets/presets/pleading_look_up.png" width="180" alt="pleading_look_up" /> | <img src="assets/presets/apology_look_up.png" width="180" alt="apology_look_up" /> |

Preset metadata (emotion tags, bubble rects, tail anchors) lives in [`assets/presets/manifest.json`](assets/presets/manifest.json).

## What it includes

- A persona-driven reply renderer for anime-style image replies
- A local bridge service for driving overlay updates
- A macOS floating overlay app built with SwiftUI
- Preset character assets and speech-bubble composition helpers

## Project layout

- `src/my_agent_girlfriend/`: Python package for routing, rendering, and bridge state
- `scripts/`: local bridge and overlay helper scripts
- `mac-app/`: Swift package for the macOS floating overlay app
- `assets/`: approved base art, preset images, and manifest data

## Local development

```bash
uv sync
uv run python scripts/run_bridge.py
```

In another terminal:

```bash
cd mac-app
swift run
```

To push a new overlay line into the running app:

```bash
uv run python scripts/push_overlay.py --reply "안녕. 너는 뭐라고 불리고 싶어?"
```

## One-line bootstrap

To install dependencies, start the local bridge, and launch the floating macOS overlay app in one step:

```bash
zsh scripts/launch_desktop.sh
```

## License

MIT
