# Preset Pack v1

All images are speech-bubble-free character renders. Dialogue is added only in post-processing.

## Visual lock

- Same character for all presets
- Long red hair
- Plain white short-sleeve shirt
- Wholesome 2D anime illustration
- Clean, unobtrusive background
- No speech bubble
- No watermark
- No text

## Base approval prompt

```text
2D anime-style illustration of the same fixed character for a reusable visual preset pack. Long red hair, plain white short-sleeve shirt, wholesome non-sexualized presentation, upper-body portrait, clean polished line art, soft shading, expressive face, simple unobtrusive background, no text, no speech bubble, no watermark.
```

## Presets

Canonical preset IDs, emotion tags, framing, camera, and notes live in
`assets/presets/manifest.json`. Generate the prompt pack from that manifest with:

```bash
python3 scripts/bootstrap_presets.py --output-prompts output/preset-prompts.json
```

Only manifest entries without `usage: "work_in_progress"` are live generation/routing
targets. Work-in-progress alternates remain in the manifest so they can be promoted
without inventing a second preset list.
