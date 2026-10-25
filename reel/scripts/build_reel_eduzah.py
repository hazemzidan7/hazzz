"""Reproducible build of the EDUZAH at NASA Space Apps Assiut reel (branded version).

Usage: python3 build_reel_eduzah.py <media_dir> <work_dir> <music.wav> <assets_dir> <out.mp4> [<out_with_shout.mp4>]
Source files in <media_dir> are only read, never modified.
"""
import hashlib, json, os, statistics, subprocess, sys

MEDIA, WORK, MUSIC, ASSETS, OUT = sys.argv[1:6]
OUT_SHOUT = sys.argv[6] if len(sys.argv) > 6 else None
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


WHITE = "white"
ACCENT = "0xD81B5D"       # eduzah magenta, sampled from the official logo
EASE = "(1-pow(1-min(max((t-{s})/{d},0),1),3))"          # ease-out cubic, 0..1

def alpha(start, end, fin=0.35, fout=0.25):
    return (f"if(lt(t,{start}),0,if(lt(t,{start+fin}),(t-{start})/{fin},"
            f"if(lt(t,{end-fout}),1,if(lt(t,{end}),({end}-t)/{fout},0))))")

def rise(txt, font, size, y, start, end, color=WHITE, dist=34, fin=0.4, x="(w-text_w)/2"):
    """Line reveal: fades in while sliding up `dist` px with ease-out, fades out in place."""
    yy = f"{y}+{dist}*(1-{EASE.format(s=start, d=fin)})"
    return (f"drawtext=fontfile={font}:text='{txt}':fontsize={size}:fontcolor={color}:x={x}:y='{yy}'"
            f":alpha='{alpha(start, end, fin)}':shadowcolor=black@0.5:shadowx=0:shadowy=3")

BARS = []
def bar(y, start, end, wmax=96, h=6):
    """Magenta accent rule that grows from the centre (rendered as an overlay, see main)."""
    BARS.append((y, start, end, wmax, h))
    return None

def word(txt, start, end, y=1310):
    return [bar(y - 26, start, end, 70), rise(txt, FONT_X, 84, y, start, end, dist=40, fin=0.35)]

TEXT_ALL = [
    # opening 0.3-3.9: EDUZAH AT / NASA SPACE APPS / ASSIUT / supporting line
    bar(1166, 0.25, 3.9, 110),
    rise("E D U Z A H   A T", FONT_S, 44, 1196, 0.35, 3.9),
    rise("NASA SPACE APPS", FONT_X, 82, 1258, 0.55, 3.9),
    rise("ASSIUT", FONT_X, 82, 1350, 0.72, 3.9),
    rise("A Journey of Innovation, Technology & Collaboration", FONT_M, 31, 1462, 1.3, 3.9, dist=20),
    # atmosphere 4.2-7.85
    rise("WHERE IDEAS", FONT_X, 70, 1280, 4.25, 7.85),
    rise("MEET TECHNOLOGY", FONT_X, 70, 1364, 4.45, 7.85),
    # Hazem's workshop 8.0-9.95
    bar(1276, 8.1, 9.95, 80),
    rise("FROM IDEA TO PRODUCT", FONT_X, 60, 1300, 8.15, 9.95),
    rise("Workshop by Eng. Hazem Zidan", FONT_M, 38, 1380, 8.35, 9.95, dist=20),
    # participation, each word on the shot that shows it
    *word("LEARNING.", 14.05, 15.45),
    *word("BUILDING.", 21.55, 23.45),
    *word("COLLABORATING.", 26.05, 27.95),
    # closing 40.2-45: EDUZAH x NASA SPACE APPS ASSIUT / Innovation. Collaboration. Impact.
    rise("EDUZAH", FONT_X, 70, 340, 40.25, 45.1, x="(w/2)-text_w-34"),
    rise("×", FONT_X, 70, 340, 40.35, 45.1, color=ACCENT, x="(w-text_w)/2"),
    rise("NASA", FONT_X, 70, 340, 40.45, 45.1, x="(w/2)+34"),
    rise("SPACE APPS ASSIUT", FONT_X, 56, 424, 40.6, 45.1),
    bar(502, 40.8, 45.1, 90),
    rise("Innovation.  Collaboration.  Impact.", FONT_M, 34, 526, 41.0, 45.1, dist=20),
]
TEXT = [t for t in TEXT_ALL if t]
GRADS = [("grad_bottom.png", 1000, [(0, 4), (4, 8), (8, 10), (14, 15.5), (21.5, 23.5), (26, 28)]),
         ("grad_top.png", 230, [(39.8, 45.0)])]
LOGO_Y = 150   # top of the tag graphic (incl. its 24 px shadow margin), inside the Reels safe area

if __name__ == "__main__":
    lumas = [None if s.get("framed") or s.get("push") else measure_luma(s) for s in SHOTS]
    target = statistics.median([l for l in lumas if l])
    parts = []
    for i, (s, l) in enumerate(zip(SHOTS, lumas)):
        b = 0.0 if l is None else max(-0.06, min(0.06, (target - l) / 255 * 0.7))
        print(f"shot {i:02d} {s['src']} ss={s['ss']} dur={s['dur']} yavg={l and round(l,1)} brightness={b:+.3f}")
        parts.append(render_shot(i, s, b))
    total = sum(s["dur"] for s in SHOTS)
    lst = os.path.join(WORK, "concat_eduzah.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)

    inputs = ["-f", "concat", "-safe", "0", "-i", lst, "-i", MUSIC]
    fc = []; cur = "[0:v]"; n = 2
    for png, y, wins in GRADS:
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", str(total), "-i", os.path.join(ASSETS, png)]
        en = "+".join(f"between(t,{a},{b})" for a, b in wins)
        fc.append(f"{cur}[{n}:v]overlay=0:{y}:enable='{en}'[g{n}]"); cur = f"[g{n}]"; n += 1
    inputs += ["-loop", "1", "-framerate", str(FPS), "-t", str(total), "-i", os.path.join(ASSETS, "eduzah_logo_tag.png")]
    fc.append(f"[{n}:v]format=rgba,fade=t=in:st=0.6:d=0.6:alpha=1[logo]")
    fc.append(f"{cur}[logo]overlay=x=(W-w)/2:y={LOGO_Y}[lg]")
    cur = "[lg]"
    for k, (y, a, b, wmax, h) in enumerate(BARS):
        n += 1
        inputs += ["-f", "lavfi", "-i", f"color=c={ACCENT}:s={wmax}x{h}:r={FPS}:d={total}"]
        e = EASE.format(s=a, d=0.45)
        fc.append(f"[{n}:v]format=rgba,scale=w='trunc(max(2,{wmax}*{e})/2)*2':h={h}:eval=frame,"
                  f"fade=t=in:st={a}:d=0.2:alpha=1,fade=t=out:st={b-0.25}:d=0.25:alpha=1[bar{k}]")
        fc.append(f"{cur}[bar{k}]overlay=x=(W-w)/2:y={y}:enable='between(t,{a},{b})'[b{k}]"); cur = f"[b{k}]"
    fc.append(f"{cur}{','.join(TEXT)},fade=t=out:st={total-0.3}:d=0.3,format=yuv420p[v]")
    enc = ["-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-b:v", "16M", "-maxrate", "20M", "-bufsize", "32M",
           "-r", str(FPS), "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
           "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart"]
    # main version: soundtrack only, no clip audio at all
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
         "-map", "[v]", "-map", "1:a", "-t", str(total), *enc, OUT])
    if OUT_SHOUT:
        # alternate: identical picture (re-muxed from OUT), closing shout over a ducked soundtrack
        cs = total - SHOTS[-1]["dur"]; cl = SHOTS[-1]
        af = (f"[1:a]volume='if(lt(t,{cs:.3f}),1,if(lt(t,{cs+0.5:.3f}),1-0.65*(t-{cs:.3f})/0.5,0.35))':eval=frame[m];"
              f"[2:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=90,volume=1.6,"
              f"afade=t=in:d=0.15,afade=t=out:st={cl['dur']-0.5}:d=0.5,adelay={int(cs*1000)}:all=1[s];"
              f"[m][s]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:level=0[a]")
        run(["ffmpeg", "-v", "error", "-y", "-i", OUT, "-i", MUSIC, "-ss", str(cl["ss"]), "-t", str(cl["dur"]), "-i", path(cl["src"]),
             "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", str(total), OUT_SHOUT])
    print("total", total)
