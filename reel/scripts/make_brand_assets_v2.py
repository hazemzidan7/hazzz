"""Brand overlays for the branded reel (v2).
Logo: the official transparent dark-background artwork (designer's "Logo/Dark BG/PNG/Asset 23@3x.png"),
cropped to its first two rows (éduzah + ايدوزا) so the tagline row is dropped. Pixels are not recoloured.
Usage: python3 make_brand_assets_v2.py <Asset23.png> <out_dir>"""
import sys, os
import numpy as np
from PIL import Image
src, out = sys.argv[1:3]
im = Image.open(src).convert("RGBA")
a = np.array(im)[:, :, 3]
rows = (a > 20).sum(1)
bands, start = [], None
for y, v in enumerate(rows):
    if v and start is None: start = y
    if not v and start is not None: bands.append((start, y)); start = None
if start is not None: bands.append((start, len(rows)))
assert len(bands) == 3, bands                      # éduzah / ايدوزا / tagline
lock = im.crop((0, 0, im.width, bands[1][1]))
lock = lock.crop(lock.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
LW = 250                                           # px on the 1080-wide frame
lock = lock.resize((LW, round(lock.height * LW / lock.width)), Image.LANCZOS)
lock.save(os.path.join(out, "eduzah_lockup_white.png"))
print("lockup", lock.size)

def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
PINK, PURPLE, DARK = hexrgb("#D91B5B"), hexrgb("#672D86"), hexrgb("#321D3D")
# bottom: brand gradient behind the logo, like the reference photo (dark purple fading into pink at the edge)
h = 620; g = np.zeros((h, 1080, 4), np.uint8)
for y in range(h):
    u = y / (h - 1)
    c = np.array(DARK) * (1 - u ** 2) + np.array(PINK) * u ** 2
    g[y, :, :3] = c; g[y, :, 3] = int(255 * 0.62 * u ** 1.6)
Image.fromarray(g).save(os.path.join(out, "grad_bottom_brand.png"))
# top: dark purple behind titles in the upper-middle text zone (y 330-680)
h = 860; g = np.zeros((h, 1080, 4), np.uint8)
for y in range(h):
    u = y / (h - 1)
    g[y, :, :3] = DARK; g[y, :, 3] = int(255 * 0.72 * (1 - u) ** 1.3)
Image.fromarray(g).save(os.path.join(out, "grad_top_brand.png"))
