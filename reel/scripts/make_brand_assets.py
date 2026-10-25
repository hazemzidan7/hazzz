"""Brand overlays for the Eduzah reel. The official logo pixels are only trimmed of empty
white margin and scaled proportionally; it is never recoloured or redrawn.
Usage: python3 make_brand_assets.py <IMG_3703.png> <out_dir>"""
import sys, os
from PIL import Image, ImageChops, ImageDraw, ImageFilter
src, out = sys.argv[1:3]
logo = Image.open(src).convert("RGBA")
bg = Image.new("RGBA", logo.size, (255, 255, 255, 255))
bbox = ImageChops.difference(logo, bg).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
logo = logo.crop(bbox)
# white rounded tag (the logo's own background colour) with a soft shadow
LW = 150                                   # logo width on the 1080 px frame
lh = round(logo.height * LW / logo.width)
logo = logo.resize((LW, lh), Image.LANCZOS)
px, py, r = 22, 14, 18
tw, th = LW + 2 * px, lh + 2 * py
pad = 24
canvas = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 4, pad + tw, pad + th + 4], r, fill=(0, 0, 0, 90))
canvas = Image.alpha_composite(canvas, sh.filter(ImageFilter.GaussianBlur(9)))
tag = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
ImageDraw.Draw(tag).rounded_rectangle([pad, pad, pad + tw, pad + th], r, fill=(255, 255, 255, 240))
canvas = Image.alpha_composite(canvas, tag)
canvas.alpha_composite(logo, (pad + px, pad + py))
canvas.save(os.path.join(out, "eduzah_logo_tag.png"))
print("tag", canvas.size, "logo", (LW, lh))
# gradients for text legibility
def grad(h, top_alpha, bottom_alpha, name):
    g = Image.new("RGBA", (1080, h))
    for y in range(h):
        a = top_alpha + (bottom_alpha - top_alpha) * (y / (h - 1)) ** 1.2
        ImageDraw.Draw(g).line([(0, y), (1079, y)], fill=(12, 6, 16, int(a)))
    g.save(os.path.join(out, name))
grad(920, 0, 200, "grad_bottom.png")
grad(520, 165, 0, "grad_top.png")
