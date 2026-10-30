#!/usr/bin/env python3
"""Build Hank's import-ready Harness pet sheet and animated preview."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PET = ROOT / "assets" / "pets" / "hank"
SOURCE = PET / "source" / "hank_pose_reference.png"
SHEET = PET / "hank_spritesheet.png"
PREVIEW = PET / "hank_preview.gif"

CELL = (192, 208)
LOGICAL = (96, 104)
SHEET_SIZE = (CELL[0] * 8, CELL[1] * 9)

# Row-major boxes around the nine isolated poses in the generated reference.
POSE_BOXES = (
    (74, 22, 338, 423),    # idle
    (437, 30, 814, 406),   # running right
    (887, 30, 1222, 423),  # running left
    (64, 441, 341, 823),   # waving
    (433, 436, 815, 808),  # jumping
    (887, 527, 1225, 816), # failed
    (67, 830, 338, 1226),  # waiting
    (416, 835, 843, 1233), # forward run
    (902, 830, 1190, 1226),# review/listening
)

# Four restrained offsets per animation. The art stays crisp and the cape/boots
# remain the visual anchors at the dial's small size.
MOTION = (
    ((0, 0), (0, -1), (0, 0), (0, 1)),
    ((-2, 0), (0, -2), (2, 0), (3, -1)),
    ((2, 0), (0, -2), (-2, 0), (-3, -1)),
    ((0, 0), (0, -1), (1, 0), (0, 1)),
    ((0, 2), (0, -2), (0, -5), (0, -2)),
    ((0, 0), (0, 1), (0, 0), (0, 1)),
    ((0, 0), (0, -1), (0, 0), (0, 1)),
    ((-1, 1), (0, -2), (1, 0), (0, -1)),
    ((0, 0), (1, -1), (0, 0), (-1, 0)),
)

LABELS = ("Idle", "Run right", "Run left", "Wave", "Jump", "Failed", "Waiting", "Running", "Review")


def poses() -> list[Image.Image]:
    source = Image.open(SOURCE).convert("RGBA")
    return [source.crop(box) for box in POSE_BOXES]


def logical_sprite(pose: Image.Image) -> Image.Image:
    box = pose.getchannel("A").getbbox()
    if not box:
        raise ValueError("Hank pose is empty")
    pose = pose.crop(box)
    scale = min(88 / pose.width, 98 / pose.height)
    size = (max(1, round(pose.width * scale)), max(1, round(pose.height * scale)))
    return pose.resize(size, Image.Resampling.NEAREST)


def frame(sprite: Image.Image, offset: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGBA", LOGICAL)
    x = (LOGICAL[0] - sprite.width) // 2 + offset[0]
    y = LOGICAL[1] - sprite.height - 2 + offset[1]
    canvas.alpha_composite(sprite, (x, y))
    canvas.putalpha(canvas.getchannel("A").point(lambda alpha: 255 if alpha >= 128 else 0))
    return canvas.resize(CELL, Image.Resampling.NEAREST)


def build() -> list[list[Image.Image]]:
    sprites = [logical_sprite(pose) for pose in poses()]
    rows = [[frame(sprite, move) for move in MOTION[i]] for i, sprite in enumerate(sprites)]
    sheet = Image.new("RGBA", SHEET_SIZE)
    for row, frames in enumerate(rows):
        for col, image in enumerate(frames):
            sheet.alpha_composite(image, (col * CELL[0], row * CELL[1]))
    sheet.save(SHEET, optimize=True)
    return rows


def preview(rows: list[list[Image.Image]]) -> None:
    frames = []
    for tick in range(12):
        page = Image.new("RGBA", (660, 720), (10, 16, 30, 255))
        draw = ImageDraw.Draw(page)
        for row, label in enumerate(LABELS):
            x, y = (row % 3) * 220, (row // 3) * 240
            draw.rounded_rectangle((x + 8, y + 8, x + 212, y + 232), 18, fill=(20, 31, 53, 255))
            draw.text((x + 18, y + 16), label, fill=(225, 231, 244, 255))
            image = rows[row][tick % len(rows[row])]
            page.alpha_composite(image, (x + 14, y + 28))
        frames.append(page.convert("P", palette=Image.Palette.ADAPTIVE))
    frames[0].save(PREVIEW, save_all=True, append_images=frames[1:], duration=120, loop=0, disposal=2)


def validate() -> None:
    image = Image.open(SHEET).convert("RGBA")
    if image.size != SHEET_SIZE:
        raise ValueError(f"wrong sheet size: {image.size}")
    for row in range(9):
        for col in range(8):
            cell = image.crop((col * CELL[0], row * CELL[1], (col + 1) * CELL[0], (row + 1) * CELL[1]))
            visible = cell.getchannel("A").getbbox() is not None
            if visible != (col < 4):
                raise ValueError(f"row {row + 1}, cell {col + 1}: unexpected alpha")
    alpha_histogram = image.getchannel("A").histogram()
    if any(alpha_histogram[1:255]):
        raise ValueError("sheet has soft alpha")
    pixels = image.load()
    for y in range(0, image.height, 2):
        for x in range(0, image.width, 2):
            if len({pixels[x, y], pixels[x + 1, y], pixels[x, y + 1], pixels[x + 1, y + 1]}) != 1:
                raise ValueError(f"nonuniform 2x pixel block at {x}, {y}")


if __name__ == "__main__":
    preview(build())
    validate()
    print(f"wrote {SHEET.relative_to(ROOT)} ({SHEET_SIZE[0]}x{SHEET_SIZE[1]})")
    print(f"wrote {PREVIEW.relative_to(ROOT)}")
