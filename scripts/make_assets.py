"""Rebuild profile assets using alperensenel.com color palette."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# alperensenel.com :root
BG = (8, 10, 13)          # --bg #080a0d
BG2 = (13, 16, 22)        # --bg2 #0d1016
CARD = (17, 21, 28)       # --card #11151c
GOLD = (217, 184, 95)     # --gold #d9b85f
GOLD2 = (241, 217, 141)   # --gold2 #f1d98d
MUTED = (141, 146, 156)   # --muted #8d929c
TEXT = (238, 240, 243)    # --text #eef0f3
LINE = (32, 38, 49)       # --line #202631


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def prepare_logo() -> Path:
    src = ASSETS / "logo.png"
    img = Image.open(src).convert("RGBA")
    # tighten crop around the mark a bit for avatar clarity
    w, h = img.size
    # keep full square but slightly boost contrast/sharpness
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Sharpness(img).enhance(1.15)
    out = ASSETS / "logo.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    # transparent-friendly square for overlays
    img.save(ASSETS / "logo-transparent.png", "PNG", optimize=True)
    return out


def crop_banner_from_ai() -> Image.Image:
    ai = Image.open(ASSETS / "banner-ai.png").convert("RGB")
    # AI is 1280x720 — crop center band to ~1280x420 for README
    w, h = ai.size
    target_h = int(w * 420 / 1280)
    top = max(0, (h - target_h) // 2 - 20)
    band = ai.crop((0, top, w, top + target_h)).resize((1280, 420), Image.Resampling.LANCZOS)
    return band


def make_banner() -> Path:
    # Prefer AI banner if present; otherwise synthesize
    if (ASSETS / "banner-ai.png").exists():
        base = crop_banner_from_ai().convert("RGBA")
    else:
        base = Image.new("RGBA", (1280, 420), (*BG, 255))

    frames = []
    for i in range(4):
        frame = base.copy()
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        rng = random.Random(40 + i)
        for _ in range(18):
            x, y = rng.randint(700, 1240), rng.randint(40, 380)
            r = rng.randint(1, 2)
            a = 90 + i * 20
            d.ellipse([x - r, y - r, x + r, y + r], fill=(*GOLD2, a))
        frame = Image.alpha_composite(frame, overlay)
        frames.append(frame.convert("P", palette=Image.ADAPTIVE, colors=192))

    gif = ASSETS / "banner.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=480, loop=0, optimize=True)
    base.convert("RGB").save(ASSETS / "banner.png", "PNG", optimize=True)
    return gif


def make_project_icon(name: str, initials: str, accent: tuple[int, int, int], filename: str) -> Path:
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([8, 8, size - 8, size - 8], radius=44, fill=CARD)
    draw.rounded_rectangle([8, 8, size - 8, size - 8], radius=44, outline=accent, width=3)
    draw.ellipse([30, 30, 54, 54], fill=accent)
    font = find_font(68, bold=True)
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 12), initials, font=font, fill=TEXT)
    label = find_font(16, bold=False)
    lb = draw.textbbox((0, 0), name, font=label)
    draw.text(((size - (lb[2] - lb[0])) / 2, size - 46), name, font=label, fill=MUTED)
    out = ASSETS / "projects" / filename
    out.parent.mkdir(exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def main() -> None:
    print(prepare_logo())
    print(make_banner())
    for item in [
        ("KısaLink", "KL", (119, 215, 255), "kisalink.png"),
        ("QR Kod", "QR", GOLD, "qr.png"),
        ("WebTest", "WT", (248, 113, 113), "webtest.png"),
        ("SCRATCH!", "SC", GOLD2, "scratch.png"),
        ("Karanlık Köy", "KK", (184, 146, 255), "vampir.png"),
        ("Son Vardiya", "SV", (251, 146, 60), "son-vardiya.png"),
    ]:
        print(make_project_icon(*item))


if __name__ == "__main__":
    main()
