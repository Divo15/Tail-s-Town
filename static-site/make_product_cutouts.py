from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter


ASSET_DIR = Path(__file__).resolve().parent / "assets"


def removable(pixel: tuple[int, int, int, int]) -> bool:
    r, g, b, a = pixel
    if a < 10:
        return True
    mx = max(r, g, b)
    mn = min(r, g, b)
    saturation = mx - mn
    # Light studio background and tabletop tones. Product edges usually have stronger local contrast.
    return mx > 172 and saturation < 58


def cutout(source: str, target: str) -> None:
    image = Image.open(ASSET_DIR / source).convert("RGBA")
    width, height = image.size
    pixels = image.load()
    seen = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def push(x: int, y: int) -> None:
        if 0 <= x < width and 0 <= y < height:
            idx = y * width + x
            if not seen[idx] and removable(pixels[x, y]):
                seen[idx] = 1
                queue.append((x, y))

    for x in range(width):
        push(x, 0)
        push(x, height - 1)
    for y in range(height):
        push(0, y)
        push(width - 1, y)

    while queue:
        x, y = queue.popleft()
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)

    mask = Image.frombytes("L", (width, height), bytes(255 if value else 0 for value in seen))
    mask = mask.filter(ImageFilter.GaussianBlur(1.1))
    alpha = image.getchannel("A")
    alpha = Image.composite(Image.new("L", (width, height), 0), alpha, mask)
    image.putalpha(alpha)

    bbox = alpha.getbbox()
    if bbox:
        pad = 42
        left = max(0, bbox[0] - pad)
        top = max(0, bbox[1] - pad)
        right = min(width, bbox[2] + pad)
        bottom = min(height, bbox[3] + pad)
        image = image.crop((left, top, right, bottom))

    image.save(ASSET_DIR / target)


def main() -> None:
    cutout("tailstown-feeder-product.png", "tailstown-feeder-product-cutout.png")
    cutout("tailstown-water-fountain-product.png", "tailstown-water-fountain-product-cutout.png")


if __name__ == "__main__":
    main()
