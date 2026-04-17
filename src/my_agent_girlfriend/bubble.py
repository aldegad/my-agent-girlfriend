from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from .manifest import DEFAULT_FONT_PATH


@dataclass(frozen=True)
class BubbleLayout:
    bubble_rect: tuple[int, int, int, int]
    tail_anchor: tuple[int, int]
    font_size_range: tuple[int, int]


CANONICAL_CANVAS = (768, 1024)


def _load_font(size: int, font_path: Path | None = None) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidate = Path(font_path or DEFAULT_FONT_PATH)
    if candidate.exists():
        return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _line_height(font: ImageFont.ImageFont) -> int:
    bbox = font.getbbox("한글Ay")
    return bbox[3] - bbox[1] + 6


def _measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    tokens = text.split(" ")
    if not tokens:
        return [text]
    lines: list[str] = []
    current = tokens[0]
    for token in tokens[1:]:
        trial = f"{current} {token}".strip()
        width, _ = _measure(draw, trial, font)
        if width <= max_width:
            current = trial
            continue
        lines.append(current)
        current = token
    if current:
        lines.append(current)
    expanded: list[str] = []
    for line in lines:
        width, _ = _measure(draw, line, font)
        if width <= max_width:
            expanded.append(line)
            continue
        chunk = ""
        for char in line:
            trial = f"{chunk}{char}"
            char_width, _ = _measure(draw, trial, font)
            if chunk and char_width > max_width:
                expanded.append(chunk)
                chunk = char
            else:
                chunk = trial
        if chunk:
            expanded.append(chunk)
    return expanded


def fit_dialogue(
    text: str,
    layout: BubbleLayout,
    font_path: Path | None = None,
) -> tuple[ImageFont.ImageFont, list[str], int]:
    x1, y1, x2, y2 = layout.bubble_rect
    padding_x = 32
    padding_y = 24
    max_width = max(40, (x2 - x1) - padding_x * 2)
    max_height = max(40, (y2 - y1) - padding_y * 2)
    probe = ImageDraw.Draw(Image.new("RGBA", (x2 - x1, y2 - y1), (0, 0, 0, 0)))
    min_size, max_size = layout.font_size_range
    for size in range(max_size, min_size - 1, -2):
        font = _load_font(size, font_path=font_path)
        lines = _wrap_text(probe, text, font, max_width)
        height = _line_height(font) * len(lines)
        longest = max((_measure(probe, line, font)[0] for line in lines), default=0)
        if longest <= max_width and height <= max_height:
            return font, lines, size
    font = _load_font(min_size, font_path=font_path)
    lines = _wrap_text(probe, text, font, max_width)
    return font, lines, min_size


def compose_dialogue_image(
    base_image: Image.Image,
    text: str,
    layout: BubbleLayout,
    font_path: Path | None = None,
    stroke_width: int = 5,
) -> Image.Image:
    image = base_image.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x1, y1, x2, y2 = layout.bubble_rect
    anchor_x, anchor_y = layout.tail_anchor

    # Bubble fill and outline
    draw.rounded_rectangle((x1, y1, x2, y2), radius=34, fill=(255, 255, 255, 248), outline=(0, 0, 0, 255), width=stroke_width)

    bubble_mid_x = (x1 + x2) // 2
    tail_base_left = bubble_mid_x - 42
    tail_base_right = bubble_mid_x + 42
    tail_base_y = y2 - 8
    tail_points = [(tail_base_left, tail_base_y), (tail_base_right, tail_base_y), (anchor_x, anchor_y)]
    draw.polygon(tail_points, fill=(255, 255, 255, 248), outline=(0, 0, 0, 255))
    draw.line([tail_points[0], tail_points[2], tail_points[1]], fill=(0, 0, 0, 255), width=stroke_width)

    font, lines, _ = fit_dialogue(text, layout, font_path=font_path)
    text_draw = ImageDraw.Draw(overlay)
    padding_x = 32
    padding_y = 24
    cursor_y = y1 + padding_y
    line_height = _line_height(font)
    for line in lines:
        text_draw.text((x1 + padding_x, cursor_y), line, font=font, fill=(20, 20, 20, 255))
        cursor_y += line_height

    return Image.alpha_composite(image, overlay)


def layout_from_manifest(preset: dict[str, object]) -> BubbleLayout:
    bubble_rect = tuple(int(value) for value in preset["bubble_rect"])  # type: ignore[index]
    tail_anchor = tuple(int(value) for value in preset["tail_anchor"])  # type: ignore[index]
    font_size_range = tuple(int(value) for value in preset["font_size_range"])  # type: ignore[index]
    return BubbleLayout(
        bubble_rect=bubble_rect,  # type: ignore[arg-type]
        tail_anchor=tail_anchor,  # type: ignore[arg-type]
        font_size_range=font_size_range,  # type: ignore[arg-type]
    )


def scale_layout(layout: BubbleLayout, image_size: tuple[int, int], canonical_size: tuple[int, int] = CANONICAL_CANVAS) -> BubbleLayout:
    scale_x = image_size[0] / canonical_size[0]
    scale_y = image_size[1] / canonical_size[1]
    x1, y1, x2, y2 = layout.bubble_rect
    anchor_x, anchor_y = layout.tail_anchor
    min_font, max_font = layout.font_size_range
    font_scale = min(scale_x, scale_y)
    return BubbleLayout(
        bubble_rect=(
            int(round(x1 * scale_x)),
            int(round(y1 * scale_y)),
            int(round(x2 * scale_x)),
            int(round(y2 * scale_y)),
        ),
        tail_anchor=(
            int(round(anchor_x * scale_x)),
            int(round(anchor_y * scale_y)),
        ),
        font_size_range=(
            max(18, int(round(min_font * font_scale))),
            max(20, int(round(max_font * font_scale))),
        ),
    )


def make_placeholder_base(size: Sequence[int] = (768, 1024)) -> Image.Image:
    width, height = int(size[0]), int(size[1])
    image = Image.new("RGBA", (width, height), (248, 241, 246, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((180, 160, 600, 900), fill=(255, 221, 228, 255))
    draw.rectangle((240, 520, 540, 980), fill=(247, 247, 247, 255))
    draw.ellipse((260, 120, 520, 400), fill=(255, 228, 214, 255))
    draw.rectangle((200, 120, 270, 580), fill=(165, 52, 64, 255))
    draw.rectangle((510, 120, 580, 580), fill=(165, 52, 64, 255))
    draw.ellipse((296, 230, 330, 248), fill=(65, 43, 43, 255))
    draw.ellipse((420, 230, 454, 248), fill=(65, 43, 43, 255))
    draw.line((352, 320, 400, 332), fill=(190, 111, 117, 255), width=5)
    return image
