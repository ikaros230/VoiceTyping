"""Generate application icon for Windows packaging."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICON_PATH = ASSETS / "icon.ico"


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], fill=(50, 120, 220, 255))
    inner = size // 4
    draw.ellipse([inner, inner, size - inner, size - inner], fill=(255, 255, 255, 255))

    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(ICON_PATH, format="ICO", sizes=sizes)
    print(f"Icon saved to {ICON_PATH}")


if __name__ == "__main__":
    main()
