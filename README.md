# My Agent Girlfriend

A playful local desktop companion project for Codex.

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

## License

MIT
