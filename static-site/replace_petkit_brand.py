from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


SOURCE = Path(r"C:\Users\gs164\AppData\Local\Temp\codex-clipboard-12466a94-e6df-4a30-9d9c-cd7b0dfd0eb6.png")
OUTPUT = Path(r"C:\nifty_project\outputs\pet-product-site\assets\tails-town-feeder-reference.png")
FONT = Path(r"C:\Windows\Fonts\bahnschrift.ttf")
LOGO = Path(r"C:\nifty_project\outputs\pet-product-site\assets\tails-town-official-logo.png")


def font(size: int) -> ImageFont.ImageFont:
    if FONT.exists():
        return ImageFont.truetype(str(FONT), size=size)
    return ImageFont.load_default()


def soft_cover(image: Image.Image, box: tuple[int, int, int, int], fill: tuple[int, int, int]) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(box, radius=5, fill=225)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    surface = Image.new("RGBA", image.size, fill + (255,))
    return Image.composite(surface, image, mask)


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")

    # Remove the PETKIT vertical wordmark and the tiny top PETKIT tag.
    image = soft_cover(image, (160, 70, 206, 212), (232, 233, 231))
    image = soft_cover(image, (126, 59, 147, 72), (236, 237, 235))

    wordmark = Image.new("RGBA", (132, 42), (0, 0, 0, 0))
    draw = ImageDraw.Draw(wordmark)
    draw.text((2, 0), "TAILS TOWN", font=font(16), fill=(72, 74, 70, 245))
    draw.text((6, 24), "SMART PET CARE", font=font(8), fill=(94, 96, 92, 205))
    draw.line((2, 38, 104, 38), fill=(94, 96, 92, 170), width=1)
    wordmark = wordmark.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    image.alpha_composite(wordmark, (164, 78))

    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA")
        icon = logo.crop((70, 72, 338, 332)).convert("RGBA")
        icon = icon.resize((42, 40), Image.Resampling.LANCZOS)
        gray = icon.convert("L")
        alpha = gray.point(lambda px: max(0, min(255, int((150 - px) * 2.5))))
        alpha = alpha.filter(ImageFilter.GaussianBlur(0.2)).point(lambda px: int(px * 0.72))
        icon_mark = Image.new("RGBA", icon.size, (72, 74, 70, 0))
        icon_mark.putalpha(alpha)
        image.alpha_composite(icon_mark, (158, 178))

    tag = Image.new("RGBA", (23, 9), (0, 0, 0, 0))
    tag_draw = ImageDraw.Draw(tag)
    tag_draw.rounded_rectangle(
        (0, 0, 22, 8),
        radius=2,
        fill=(244, 245, 242, 220),
        outline=(172, 174, 169, 135),
    )
    tag_draw.text((5, 1), "TT", font=font(5), fill=(82, 84, 80, 185))
    image.alpha_composite(tag, (126, 61))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
