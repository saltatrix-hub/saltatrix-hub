"""Generate polished GitHub profile banner, logo, and project icons."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BG = (10, 6, 20)
BG2 = (31, 17, 53)
ACCENT = (124, 58, 237)
ACCENT2 = (196, 181, 253)
WHITE = (255, 255, 255)
MUTED = (177, 167, 193)
PILL_BORDER = (230, 230, 235)


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def lerp(a: tuple[int, ...], b: tuple[int, ...], t: float) -> tuple[int, ...]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def draw_cosmic_bg(w: int, h: int, seed: int = 42) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), BG)
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        row = lerp(BG, BG2, t * 0.9)
        for x in range(w):
            edge = (x / w) ** 1.4
            c = lerp(row, (48, 28, 88), edge * 0.35)
            px[x, y] = c

    nebula = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    blobs = [
        (int(w * 0.72), int(h * 0.35), 320, 180, (*ACCENT, 55)),
        (int(w * 0.88), int(h * 0.7), 260, 160, (*ACCENT2, 40)),
        (int(w * 0.55), int(h * 0.15), 200, 120, (91, 33, 182, 35)),
        (80, int(h * 0.8), 180, 100, (88, 28, 135, 28)),
    ]
    for cx, cy, rw, rh, color in blobs:
        nd.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=color)
    nebula = nebula.filter(ImageFilter.GaussianBlur(70))
    img = Image.alpha_composite(img.convert("RGBA"), nebula).convert("RGB")

    draw = ImageDraw.Draw(img)
    for _ in range(220):
        x, y = rng.randint(0, w - 1), rng.randint(0, h - 1)
        r = rng.choice([0, 0, 1, 1, 1, 2])
        a = rng.randint(140, 255)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(a, a, min(255, a + 25)))
    return img


def petal_points(cx: float, cy: float, angle: float, length: float, width: float) -> list[tuple[float, float]]:
    ax = math.cos(angle)
    ay = math.sin(angle)
    px, py = -ay, ax
    tip = (cx + ax * length, cy + ay * length)
    left = (cx + ax * length * 0.35 + px * width, cy + ay * length * 0.35 + py * width)
    right = (cx + ax * length * 0.35 - px * width, cy + ay * length * 0.35 - py * width)
    base = (cx - ax * length * 0.15, cy - ay * length * 0.15)
    return [tip, left, base, right]


def draw_logo(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    length = 42 * scale
    width = 16 * scale
    angles = [-math.pi / 2, math.pi / 6, 5 * math.pi / 6]
    colors = [(196, 181, 253), (139, 92, 246), (109, 40, 217)]
    for angle, color in zip(angles, colors):
        pts = petal_points(cx, cy + 4 * scale, angle, length, width)
        draw.polygon(pts, fill=color)
    r = 7 * scale
    draw.ellipse([cx - r, cy + 4 * scale - r, cx + r, cy + 4 * scale + r], fill=ACCENT2)


def draw_pill(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.ImageFont) -> int:
    pad_x, pad_y = 16, 7
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    w, h = tw + pad_x * 2, th + pad_y * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, outline=PILL_BORDER, width=2)
    draw.text((x + pad_x, y + pad_y - 1), text, font=font, fill=WHITE)
    return w + 10


def make_banner() -> Path:
    w, h = 1280, 420
    base = draw_cosmic_bg(w, h).convert("RGBA")

    def compose(extra_stars: int = 0, seed: int = 0) -> Image.Image:
        img = base.copy()
        draw = ImageDraw.Draw(img)
        draw_logo(draw, 108, h // 2 - 8, scale=1.45)

        name_font = find_font(54, bold=True)
        sub_font = find_font(24, bold=False)
        pill_font = find_font(16, bold=False)

        text_x = 188
        draw.text((text_x, 128), "Alperen Şenel", font=name_font, fill=WHITE)
        draw.text((text_x, 196), "IT & Helpdesk · Sistem & Ağ", font=sub_font, fill=MUTED)

        tx, ty = text_x, 252
        for tag in ["Ağ", "Sistem", "Python", "Oyun"]:
            tx += draw_pill(draw, tx, ty, tag, pill_font)

        rng = random.Random(seed)
        for _ in range(extra_stars):
            x, y = rng.randint(520, w - 30), rng.randint(30, h - 30)
            r = rng.randint(1, 2)
            a = rng.randint(200, 255)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(a, a, 255, 220))
        return img

    frames = [compose(extra_stars=25 + i * 8, seed=10 + i).convert("P", palette=Image.ADAPTIVE, colors=160) for i in range(4)]
    gif_path = ASSETS / "banner.gif"
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=450, loop=0, optimize=True)

    compose().convert("RGB").save(ASSETS / "banner.png", "PNG", optimize=True)
    return gif_path


def make_logo_square() -> Path:
    size = 512
    bg = draw_cosmic_bg(size, size, seed=7).convert("RGBA")
    disc = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(disc).ellipse([28, 28, size - 28, size - 28], fill=(10, 6, 20, 235))
    img = Image.alpha_composite(bg, disc)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, size // 2, size // 2 - 6, scale=3.6)
    out = ASSETS / "logo.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    return out


def make_project_icon(name: str, initials: str, color: tuple[int, int, int], filename: str) -> Path:
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([8, 8, size - 8, size - 8], radius=48, fill=BG)
    draw.rounded_rectangle([8, 8, size - 8, size - 8], radius=48, outline=color, width=4)
    draw.ellipse([28, 28, 56, 56], fill=color)
    font = find_font(72, bold=True)
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 10), initials, font=font, fill=WHITE)
    label_font = find_font(17, bold=False)
    lb = draw.textbbox((0, 0), name, font=label_font)
    draw.text(((size - (lb[2] - lb[0])) / 2, size - 48), name, font=label_font, fill=MUTED)
    out = ASSETS / "projects" / filename
    out.parent.mkdir(exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def main() -> None:
    print(make_banner())
    print(make_logo_square())
    for item in [
        ("KısaLink", "KL", (96, 165, 250), "kisalink.png"),
        ("QR Kod", "QR", (52, 211, 153), "qr.png"),
        ("WebTest", "WT", (248, 113, 113), "webtest.png"),
        ("SCRATCH!", "SC", (251, 191, 36), "scratch.png"),
        ("Karanlık Köy", "KK", (167, 139, 250), "vampir.png"),
        ("Son Vardiya", "SV", (251, 146, 60), "son-vardiya.png"),
    ]:
        print(make_project_icon(*item))


if __name__ == "__main__":
    main()
