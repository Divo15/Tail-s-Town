from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ASSET_DIR = Path(__file__).resolve().parent / "assets"
FONT_PATH = Path("C:/Windows/Fonts/bahnschrift.ttf")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size=size)
    return ImageFont.load_default()


def make_wordmark(width: int, color: tuple[int, int, int], opacity: int) -> Image.Image:
    canvas = Image.new("RGBA", (width, max(42, width // 5)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    font = load_font(max(15, int(width * 0.112)))
    text = "TAILS TOWN"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (canvas.width - text_w) // 2
    y = (canvas.height - text_h) // 2 - 1

    draw.text((x, y), text, font=font, fill=color + (opacity,))
    underline_y = y + text_h + 8
    if underline_y < canvas.height - 2:
        line_w = int(text_w * 0.76)
        line_x = (canvas.width - line_w) // 2
        draw.line((line_x, underline_y, line_x + line_w, underline_y), fill=color + (int(opacity * 0.52),), width=1)

    return canvas.filter(ImageFilter.GaussianBlur(0.16))


def imprint_wordmark(
    source: str,
    target: str,
    position: tuple[int, int],
    width: int,
    color: tuple[int, int, int],
    opacity: int,
) -> None:
    base = Image.open(ASSET_DIR / source).convert("RGBA")
    mark = make_wordmark(width, color, opacity)
    x, y = position

    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_mark = Image.new("RGBA", mark.size, (0, 0, 0, 0))
    shadow_alpha = mark.getchannel("A").filter(ImageFilter.GaussianBlur(1.0))
    shadow_alpha = shadow_alpha.point(lambda px: int(px * 0.16))
    shadow_mark.putalpha(shadow_alpha)
    shadow.alpha_composite(shadow_mark, (x + 1, y + 1))

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.alpha_composite(mark, (x, y))

    branded = Image.alpha_composite(base, shadow)
    branded = Image.alpha_composite(branded, layer).convert("RGB")
    branded.save(ASSET_DIR / target, quality=96, optimize=True)


def make_all() -> None:
    # Product tile/detail renders. Positions sit on clean, visible product surfaces.
    imprint_wordmark(
        "tile-feeder-product.png",
        "tile-feeder-product-branded.png",
        (1208, 352),
        172,
        (46, 44, 39),
        132,
    )
    imprint_wordmark(
        "tile-water-product.png",
        "tile-water-product-branded.png",
        (880, 626),
        190,
        (36, 69, 67),
        124,
    )
    imprint_wordmark(
        "tile-litter-product-clean.png",
        "tile-litter-product-branded.png",
        (1010, 218),
        178,
        (50, 50, 46),
        128,
    )

    # Homepage hero/poster renders. Same logic, scaled to each product angle.
    imprint_wordmark(
        "hero-dogs-feeder-autumn.png",
        "hero-dogs-feeder-autumn-branded.png",
        (880, 608),
        120,
        (46, 44, 39),
        132,
    )
    imprint_wordmark(
        "hero-cats-water-winter.png",
        "hero-cats-water-winter-branded.png",
        (902, 596),
        146,
        (36, 69, 67),
        124,
    )
    imprint_wordmark(
        "hero-cat-litter-winter-clean.png",
        "hero-cat-litter-winter-clean-branded.png",
        (1088, 210),
        146,
        (50, 50, 46),
        128,
    )
    imprint_wordmark(
        "hero-dog-water-summer.png",
        "hero-dog-water-summer-branded.png",
        (842, 594),
        138,
        (36, 69, 67),
        124,
    )
    imprint_wordmark(
        "hero-both-mudroom-spring.png",
        "hero-both-mudroom-spring-branded.png",
        (918, 508),
        118,
        (46, 44, 39),
        132,
    )
    make_preview()


def make_preview() -> None:
    names = [
        "tile-feeder-product-branded.png",
        "tile-water-product-branded.png",
        "tile-litter-product-branded.png",
    ]
    thumb_w, thumb_h = 560, 315
    tiles = []
    for name in names:
        image = Image.open(ASSET_DIR / name).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h), (246, 244, 239))
        tile.paste(image, ((thumb_w - image.width) // 2, (thumb_h - image.height) // 2))
        tiles.append(tile)

    sheet = Image.new("RGB", (thumb_w * len(tiles), thumb_h), (246, 244, 239))
    for index, tile in enumerate(tiles):
        sheet.paste(tile, (index * thumb_w, 0))
    sheet.save(ASSET_DIR / "branded-product-preview.jpg", quality=92, optimize=True)


if __name__ == "__main__":
    make_all()
