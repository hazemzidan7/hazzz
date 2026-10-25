"""Reproducible build of the EDUZAH at NASA Space Apps Assiut reel (final branded revision).

Usage: python3 build_reel_branded.py <media_dir> <work_dir> <music.wav> <assets_dir> <out.mp4>
Source files in <media_dir> are only read, never modified.
"""
import hashlib, json, os, statistics, subprocess, sys

MEDIA, WORK, MUSIC, ASSETS, OUT = sys.argv[1:6]
os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FONT_B = "/usr/share/fonts/opentype/montserrat/Montserrat-Bold.otf"
FONT_M = "/usr/share/fonts/opentype/montserrat/Montserrat-Medium.otf"
FONT_X = "/usr/share/fonts/opentype/montserrat/Montserrat-ExtraBold.otf"
FONT_S = "/usr/share/fonts/opentype/montserrat/Montserrat-SemiBold.otf"
if not os.path.exists(FONT_B):
    FONT_B = "/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf"
    FONT_M = "/usr/share/fonts/truetype/montserrat/Montserrat-Medium.ttf"

HDR = {"IMG_3438", "IMG_0262", "IMG_0263", "IMG_0387", "IMG_0394", "IMG_0694", "IMG_0701", "IMG_0705",
       "IMG_0706", "IMG_0710", "IMG_0714", "IMG_0715", "IMG_0722", "IMG_0723"}
TONEMAP = ("zscale=t=linear:npl=203:tin=arib-std-b67:pin=bt2020:min=bt2020nc,format=gbrpf32le,"
           "zscale=p=bt709,tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")

# Timeline at 120 BPM: every cut lands on a beat (0.5 s grid).
# z = zoom expression of local time t (1.0 = full frame), cx/cy = crop anchor (0..1).
EASE_IN = "pow(min(max((t-{a})/{d},0),1),2)"
SHOTS = [
    # 0-4 hook + opening title: Hazem mid-gesture, then Space Apps banner + astronaut
    dict(src="IMG_0710", ss=37.3, dur=2.0, z="1.0+0.10*t/2", cx=0.5, cy=0.42),
    dict(src="IMG_4557", ss=3.5, dur=2.0, z="1.04-0.04*t/2"),
    # 4-12 atmosphere: arrivals, hall with the eduzah banner, Hazem's workshop slide, zoom-through
    dict(src="IMG_0263", ss=5.5, dur=2.0, z="1.0"),
    dict(src="IMG_4630", ss=12.4, dur=2.0, z="1.0+0.05*t/2", cx=0.5, cy=0.5),
    dict(src="IMG_4715", ss=0.3, dur=2.0, z="1.06+0.08*t/2", cx=0.45, cy=0.42),
    dict(src="IMG_0715", ss=4.0, dur=2.0, z="1.0+0.6*" + EASE_IN.format(a=1.7, d=0.3), cx=0.5, cy=0.45),
    # 12-28 participation: LEARNING / BUILDING / COLLABORATING
    dict(src="IMG_0710", ss=4.0, dur=2.0, z="1.0+0.45*pow(1-min(t/0.3,1),2)", cx=0.5, cy=0.42),
    dict(src="IMG_4650", ss=30.0, dur=1.5, z="1.04", cx=0.5, cy=0.45),
    dict(src="IMG_0706", ss=2.0, dur=2.5, z="1.04", cx=0.6, cy=0.5),
    dict(src="IMG_0710", ss=18.0, dur=2.0, z="1.08", cx=0.55, cy=0.42),
    dict(src="IMG_0722", ss=0.0, dur=1.5, z="1.08", cx=0.3, cy=0.42),
    dict(src="IMG_4667", ss=0.3, dur=2.0, z="1.05+0.05*t/2", cx=0.5, cy=0.5),
    dict(src="IMG_0710", ss=60.5, dur=2.5, z="1.04+0.06*t/2.5", cx=0.55, cy=0.42),
    dict(src="IMG_4162", ss=0.9, dur=2.0, z="1.0"),
    # 28-40 break + peak, no text
    dict(src="IMG_0706", ss=4.5, dur=2.0, z="1.04+0.08*t/2", cx=0.65, cy=0.5),
    dict(src="IMG_0722", ss=3.0, dur=2.0, z="1.0"),
    dict(src="IMG_0710", ss=45.4, dur=2.0, z="1.12-0.08*t/2", cx=0.5, cy=0.42),
    dict(src="IMG_0263", ss=26.0, dur=2.0, z="1.0"),
    dict(src="IMG_0706", ss=6.4, dur=2.0, z="1.10-0.06*t/2", cx=0.6, cy=0.5),
    # 38-45 arms raised, then the whole group: framed, pushing in to full frame
    dict(src="IMG_0723", ss=0.0, dur=1.8, framed=True),
    dict(src="IMG_3438", ss=6.8, dur=5.2, push=True, cx=0.47, cy=0.52),
]

def path(name):
    for ext in (".mov", ".mp4"):
        p = os.path.join(MEDIA, name + ext)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)

def run(cmd):
    subprocess.run(cmd, check=True)

def base_chain(s):
    pre = TONEMAP + "," if s["src"] in HDR else "format=yuv420p,"
    return pre + f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS}"

def measure_luma(s):
    vf = base_chain(s) + ",scale=270:480,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-"
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(s["ss"]), "-t", str(s["dur"]), "-i", path(s["src"]),
                          "-vf", vf, "-an", "-f", "null", "-"], capture_output=True, text=True).stdout
    vals = [float(l.split("=")[1]) for l in out.splitlines() if "YAVG" in l]
    return statistics.mean(vals)

GRADE = ("eq=contrast=1.07:saturation=1.08:brightness={b:.3f},"
         "colorbalance=rs=-0.015:bs=0.02:rh=0.015:bh=-0.01")

def render_shot(i, s, bright):
    key = hashlib.md5((json.dumps(s, sort_keys=True) + f"{bright:.3f}" + GRADE + TONEMAP).encode()).hexdigest()[:8]
    out = os.path.join(WORK, f"shot_{i:02d}_{key}.mp4")
    if os.path.exists(out):
        return out
    src = path(s["src"])
    if s.get("push"):
        d = s["dur"]; cx = s["cx"]; cy = s["cy"]
        u = "min(max((t-0.3)/2.8,0),1)"
        wexp = f"{W}*pow({H*16/9/W:.4f},{u}*{u}*(3-2*{u}))*(1+0.08*min(max((t-3.1)/2.1,0),1))"
        fc = (f"[0:v]{TONEMAP},fps={FPS},{GRADE.format(b=bright)},split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=60,eq=brightness=-0.28:saturation=0.6[bg];"
              f"[b]scale=w='trunc(({wexp})/2)*2':h=-2:eval=frame:flags=lanczos[fg];"
              f"[bg][fg]overlay=x='{W/2}-{cx}*w':y='{H/2}-{cy}*h':eval=frame,setsar=1,format=yuv420p[v]")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["ss"]), "-t", str(d), "-i", src,
             "-filter_complex", fc, "-map", "[v]", "-an", "-frames:v", str(round(d * FPS)), "-c:v", "libx264", "-crf", "10", "-preset", "fast", out])
        return out
    if s.get("framed"):
        pre = TONEMAP + "," if s["src"] in HDR else ""
        d = s["dur"]
        fc = (f"[0:v]{pre}fps={FPS},{GRADE.format(b=bright)},split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=60,eq=brightness=-0.28:saturation=0.6[bg];"
              f"[b]scale=w='trunc(1000*(1.22-0.22*min(t/{d},1))/2)*2':h=-2:eval=frame:flags=lanczos[fg];"
              f"[bg][fg]overlay=x=(W-w)/2:y=760-h/2,setsar=1,format=yuv420p[v]")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["ss"]), "-t", str(d), "-i", src,
             "-filter_complex", fc, "-map", "[v]", "-an", "-frames:v", str(round(d * FPS)), "-c:v", "libx264", "-crf", "10", "-preset", "fast", out])
        return out
    z = s.get("z", "1.0"); cx = s.get("cx", 0.5); cy = s.get("cy", 0.5)
    vf = (base_chain(s) + "," + GRADE.format(b=bright) +
          f",scale=w='trunc({W}*({z})/2)*2':h='trunc({H}*({z})/2)*2':eval=frame:flags=lanczos"
          f",crop={W}:{H}:x='(iw-{W})*{cx}':y='(ih-{H})*{cy}',setsar=1,format=yuv420p")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["ss"]), "-t", str(s["dur"]), "-i", src,
         "-vf", vf, "-an", "-r", str(FPS), "-frames:v", str(round(s["dur"] * FPS)), "-c:v", "libx264", "-crf", "10", "-preset", "fast", out])
    return out

def text(t, font, size, y, start, end, fade=0.3, color="white"):
    a = (f"if(lt(t,{start}),0,if(lt(t,{start+fade}),(t-{start})/{fade},"
         f"if(lt(t,{end-fade}),1,if(lt(t,{end}),({end}-t)/{fade},0))))")
    return (f"drawtext=fontfile={font}:text='{t}':fontsize={size}:fontcolor={color}:x=(w-text_w)/2:y={y}"
            f":alpha='{a}':shadowcolor=black@0.55:shadowx=0:shadowy=3")


# Official EDUZAH palette (authoritative hex values from the brand reference)
PINK, ORANGE, PURPLE, DARK = "0xD91B5B", "0xFDA633", "0x672D86", "0x321D3D"
WHITE = "white"
EASE = "(1-pow(1-min(max((t-{s})/{d},0),1),3))"          # ease-out cubic, 0..1

def alpha(start, end, fin, fout=0.25):
    return (f"if(lt(t,{start}),0,if(lt(t,{start+fin}),(t-{start})/{fin},"
            f"if(lt(t,{end-fout}),1,if(lt(t,{end}),({end}-t)/{fout},0))))")

def rise(txt, font, size, y, start, end, color=WHITE, dist=28, fin=0.45, x="(w-text_w)/2", box=None):
    """Line reveal: fade in while rising `dist` px (ease-out, no overshoot); fade out in place."""
    yy = f"{y}+{dist}*(1-{EASE.format(s=start, d=fin)})"
    b = f":box=1:boxcolor={box}:boxborderw=14|22" if box else ":shadowcolor=black@0.45:shadowx=0:shadowy=2"
    return (f"drawtext=fontfile={font}:text='{txt}':fontsize={size}:fontcolor={color}:x={x}:y='{yy}'"
            f":alpha='{alpha(start, end, fin)}'{b}")

BARS = []
def bar(y, start, end, color, wmax=96, h=6):
    """Accent rule that grows from the centre (overlay, see main)."""
    BARS.append((y, start, end, color, wmax, h))
    return None

def word(n, txt, start, end):
    # numbered kinetic word in the upper-middle zone: orange index, white word, pink rule
    return [rise(n, FONT_S, 30, 418, start, end, color=ORANGE, dist=16, fin=0.35),
            rise(txt, FONT_X, 86, 462, start + 0.08, end, fin=0.4),
            bar(572, start + 0.2, end, PINK, 72)]

TEXT_ALL = [
    # opening 0.25-3.95 — event name dominant, EDUZAH AT as a pink label above it
    rise("EDUZAH AT", FONT_X, 34, 392, 0.25, 3.95, dist=16, fin=0.35, box=PINK),
    rise("NASA SPACE APPS", FONT_X, 88, 470, 0.45, 3.95),
    rise("ASSIUT", FONT_X, 88, 566, 0.62, 3.95),
    bar(680, 0.9, 3.95, ORANGE, 110),
    # atmosphere 4.25-7.85 (arrivals, hall with the eduzah roll-up)
    rise("INNOVATION", FONT_X, 80, 440, 4.25, 7.85),
    rise("IN ACTION", FONT_X, 80, 530, 4.42, 7.85, color=PINK),
    # Hazem's workshop 8.1-9.95 (real session title from the slide)
    rise("WORKSHOP", FONT_S, 30, 418, 8.1, 9.95, color=ORANGE, dist=16, fin=0.35),
    rise("FROM IDEA TO PRODUCT", FONT_X, 62, 462, 8.18, 9.95),
    rise("Eng. Hazem Zidan", FONT_M, 40, 545, 8.35, 9.95, dist=18),
    # participation: each word on the shot that shows it
    *word("01", "LEARNING.", 14.05, 15.45),
    *word("02", "BUILDING.", 21.55, 23.45),
    *word("03", "COLLABORATING.", 26.05, 27.95),
    # closing 40.25-45, fully visible through the last frame
    rise("EDUZAH", FONT_X, 92, 330, 40.25, 46.0),
    rise("×", FONT_X, 56, 436, 40.45, 46.0, color=PINK, dist=14, fin=0.35),
    rise("NASA SPACE APPS ASSIUT", FONT_X, 58, 502, 40.6, 46.0),
    bar(588, 40.9, 46.0, ORANGE, 110),
]
TEXT = [t for t in TEXT_ALL if t]
TOP_WINDOWS = [(0, 4), (4, 8), (8, 10), (14, 15.5), (21.5, 23.5), (26, 28), (39.8, 45.0)]
LOGO_BOTTOM = 1620     # logo sits above Instagram's caption/UI band (~ the bottom 300 px)

if __name__ == "__main__":
    lumas = [None if s.get("framed") or s.get("push") else measure_luma(s) for s in SHOTS]
    target = statistics.median([l for l in lumas if l])
    parts = []
    for i, (s, l) in enumerate(zip(SHOTS, lumas)):
        b = 0.0 if l is None else max(-0.06, min(0.06, (target - l) / 255 * 0.7))
        parts.append(render_shot(i, s, b))
    total = sum(s["dur"] for s in SHOTS)
    lst = os.path.join(WORK, "concat_branded.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    loop = ["-loop", "1", "-framerate", str(FPS), "-t", str(total), "-i"]
    inputs = ["-f", "concat", "-safe", "0", "-i", lst, "-i", MUSIC,
              *loop, os.path.join(ASSETS, "grad_top_brand.png"),
              *loop, os.path.join(ASSETS, "grad_bottom_brand.png"),
              *loop, os.path.join(ASSETS, "eduzah_lockup_white.png")]
    en = "+".join(f"between(t,{a},{b})" for a, b in TOP_WINDOWS)
    fc = [f"[0:v][2:v]overlay=0:0:enable='{en}'[t0]",
          # the bottom brand gradient and the logo are on screen for the whole reel
          f"[t0][3:v]overlay=0:H-h[t1]",
          f"[4:v]format=rgba,fade=t=in:st=0:d=0.5:alpha=1[logo]",
          f"[t1][logo]overlay=x=(W-w)/2:y={LOGO_BOTTOM}-h[t2]"]
    cur, n = "[t2]", 4
    for k, (y, a, b, col, wmax, h) in enumerate(BARS):
        n += 1
        inputs += ["-f", "lavfi", "-i", f"color=c={col}:s={wmax}x{h}:r={FPS}:d={total}"]
        e = EASE.format(s=a, d=0.45)
        fc.append(f"[{n}:v]format=rgba,scale=w='trunc(max(2,{wmax}*{e})/2)*2':h={h}:eval=frame,"
                  f"fade=t=in:st={a}:d=0.2:alpha=1,fade=t=out:st={b-0.25}:d=0.25:alpha=1[bar{k}]")
        fc.append(f"{cur}[bar{k}]overlay=x=(W-w)/2:y={y}:enable='between(t,{a},{b})'[b{k}]"); cur = f"[b{k}]"
    # no fade-to-black: the logo must stay visible on the final frame
    fc.append(f"{cur}{','.join(TEXT)},format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
         "-map", "[v]", "-map", "1:a", "-t", str(total),
         "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-b:v", "16M", "-maxrate", "20M", "-bufsize", "32M",
         "-r", str(FPS), "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", OUT])
    print("total", total)
