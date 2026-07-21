from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
CAPTURES = ROOT / "submission" / "video" / "captures"
OUTPUT = ROOT / "submission" / "StartOne_product_gallery.png"

CANVAS_SIZE = (2400, 1600)
BACKGROUND = "#F4F6FB"
SURFACE = "#FFFFFF"
INK = "#13213F"
MUTED = "#5C6880"
BORDER = "#D6DDEB"
SHADOW = "#E4E8F1"
ACCENT = "#3457D5"

FONT_REGULAR = "/System/Library/Fonts/SFNS.ttf"
FONT_ROUNDED = "/System/Library/Fonts/SFNSRounded.ttf"

SCREENS = [
    ("02_upload.png", "Upload material"),
    ("03_map.png", "See the knowledge map"),
    ("04_explanation.png", "Understand one concept"),
    ("05_tutor.png", "Ask the Tutor"),
    ("06_quiz.png", "Retrieve with 3 questions"),
    ("07_feedback.png", "Get immediate feedback"),
    ("08_next.png", "Continue automatically"),
    ("10_resume.png", "Pause and resume anytime"),
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def main() -> None:
    canvas = Image.new("RGB", CANVAS_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    title_font = font(FONT_ROUNDED, 58)
    subtitle_font = font(FONT_REGULAR, 29)
    flow_font = font(FONT_ROUNDED, 24)
    meta_font = font(FONT_REGULAR, 22)
    caption_font = font(FONT_ROUNDED, 25)
    number_font = font(FONT_ROUNDED, 20)

    margin_x = 46
    gap_x = 22
    gap_y = 22
    grid_top = 46
    card_w = 754
    image_pad = 12
    image_w = card_w - image_pad * 2
    image_h = round(image_w * 9 / 16)
    caption_h = 42
    card_h = image_pad + image_h + caption_h + 9

    # Brand and flow tile.
    x = margin_x
    y = grid_top
    draw.rounded_rectangle(
        (x + 6, y + 7, x + card_w + 6, y + card_h + 7),
        radius=22,
        fill=SHADOW,
    )
    draw.rounded_rectangle(
        (x, y, x + card_w, y + card_h),
        radius=22,
        fill=INK,
    )
    draw.text((x + 42, y + 36), "StartOne", fill=SURFACE, font=title_font)
    draw.multiline_text(
        (x + 42, y + 112),
        "Turn uploaded material into one\nfocused step at a time.",
        fill="#D8E1F5",
        font=subtitle_font,
        spacing=8,
    )
    flow_lines = [
        "UPLOAD  →  MAP",
        "UNDERSTAND  →  RETRIEVE",
        "FEEDBACK  →  CONTINUE",
    ]
    for line_index, line in enumerate(flow_lines):
        draw.text(
            (x + 42, y + 222 + line_index * 47),
            line,
            fill=SURFACE,
            font=flow_font,
        )
    draw.rounded_rectangle(
        (x + 42, y + card_h - 63, x + 330, y + card_h - 24),
        radius=13,
        fill="#E9EDFF",
    )
    draw.text(
        (x + 59, y + card_h - 58),
        "Codex + GPT-5.6",
        fill=ACCENT,
        font=meta_font,
    )

    for index, (filename, caption) in enumerate(SCREENS, start=1):
        tile_index = index
        row = tile_index // 3
        col = tile_index % 3
        x = margin_x + col * (card_w + gap_x)
        y = grid_top + row * (card_h + gap_y)

        draw.rounded_rectangle(
            (x + 6, y + 7, x + card_w + 6, y + card_h + 7),
            radius=22,
            fill=SHADOW,
        )
        draw.rounded_rectangle(
            (x, y, x + card_w, y + card_h),
            radius=22,
            fill=SURFACE,
            outline=BORDER,
            width=2,
        )

        screenshot = Image.open(CAPTURES / filename).convert("RGB")
        if filename == "02_upload.png":
            screenshot = screenshot.crop((80, 90, 1200, 720))
        screenshot = screenshot.resize((image_w, image_h), Image.Resampling.LANCZOS)
        screenshot_mask = Image.new("L", (image_w, image_h), 0)
        mask_draw = ImageDraw.Draw(screenshot_mask)
        mask_draw.rounded_rectangle(
            (0, 0, image_w, image_h),
            radius=14,
            fill=255,
        )
        canvas.paste(screenshot, (x + image_pad, y + image_pad), screenshot_mask)

        number_x = x + 18
        number_y = y + image_pad + image_h + 9
        draw.rounded_rectangle(
            (number_x, number_y, number_x + 34, number_y + 29),
            radius=9,
            fill=ACCENT,
        )
        number_text = str(index)
        number_box = draw.textbbox((0, 0), number_text, font=number_font)
        number_width = number_box[2] - number_box[0]
        draw.text(
            (number_x + (34 - number_width) / 2, number_y + 1),
            number_text,
            fill=SURFACE,
            font=number_font,
        )
        draw.text(
            (number_x + 46, number_y - 1),
            caption,
            fill=INK,
            font=caption_font,
        )

    canvas.save(OUTPUT, format="PNG", optimize=True, compress_level=9)
    print(OUTPUT)


if __name__ == "__main__":
    main()
