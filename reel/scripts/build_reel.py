"""Reproducible build of the NASA Space Apps Assiut reel.

Usage: python3 build_reel.py <media_dir> <work_dir> <music.wav> <out.mp4>
Source files in <media_dir> are only read, never modified.
"""
import hashlib, json, os, statistics, subprocess, sys

MEDIA, WORK, MUSIC, OUT = sys.argv[1:5]
os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FONT_B = "/usr/share/fonts/opentype/montserrat/Montserrat-Bold.otf"
FONT_M = "/usr/share/fonts/opentype/montserrat/Montserrat-Medium.otf"
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
    # hook: Hazem mid-gesture, slow digital push-in
    dict(src="IMG_0710", ss=37.3, dur=2.0, z="1.0+0.10*t/2", cx=0.5, cy=0.42),
    # event identity: Space Apps banner + astronaut cut-out
    dict(src="IMG_4557", ss=3.5, dur=2.0, z="1.04-0.04*t/2"),
    # arrivals past the Space Apps banner
    dict(src="IMG_0263", ss=5.5, dur=2.0, z="1.0"),
    # packed hall
    dict(src="IMG_0394", ss=1.0, dur=2.0, z="1.0+0.05*t/2"),
    # Hazem's workshop title slide
    dict(src="IMG_4715", ss=0.3, dur=2.0, z="1.06+0.08*t/2", cx=0.45, cy=0.42),
    # back of the room, zoom-through into the next shot
    dict(src="IMG_0715", ss=4.0, dur=2.0, z="1.0+0.6*" + EASE_IN.format(a=1.7, d=0.3), cx=0.5, cy=0.45),
    dict(src="IMG_0710", ss=4.0, dur=2.0, z="1.0+0.45*pow(1-min(t/0.3,1),2)", cx=0.5, cy=0.42),
    dict(src="IMG_0705", ss=0.4, dur=1.5, z="1.10", cx=0.5, cy=0.42),
    # interaction with students
    dict(src="IMG_0706", ss=2.0, dur=2.5, z="1.04", cx=0.6, cy=0.5),
    dict(src="IMG_0710", ss=18.0, dur=2.0, z="1.08", cx=0.55, cy=0.42),
    dict(src="IMG_0722", ss=0.0, dur=1.5, z="1.08", cx=0.3, cy=0.42),
    dict(src="IMG_0701", ss=4.0, dur=2.0, z="1.0"),
    dict(src="IMG_0710", ss=60.5, dur=2.5, z="1.04+0.06*t/2.5", cx=0.55, cy=0.42),
    dict(src="IMG_4162", ss=0.9, dur=2.0, z="1.0"),
    # break (riser) then peak
    dict(src="IMG_0706", ss=4.5, dur=2.0, z="1.04+0.08*t/2", cx=0.65, cy=0.5),
    dict(src="IMG_0722", ss=3.0, dur=2.0, z="1.0"),
    dict(src="IMG_0710", ss=45.4, dur=2.0, z="1.12-0.08*t/2", cx=0.5, cy=0.42),
    dict(src="IMG_0263", ss=26.0, dur=2.0, z="1.0"),
    dict(src="IMG_0706", ss=6.4, dur=2.0, z="1.10-0.06*t/2", cx=0.6, cy=0.5),
    # arms raised, landscape frame pulls back over a blurred fill
    dict(src="IMG_0723", ss=0.0, dur=1.8, framed=True),
    # closing: whole group framed, push in to full-bleed through the countdown,
    # landing on the "Eduzah" shout (source 10.0-11.2 s, reel 43.0-44.2 s)
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

if __name__ == "__main__":
    lumas = [None if s.get("framed") or s.get("push") else measure_luma(s) for s in SHOTS]
    target = statistics.median([l for l in lumas if l])
    parts = []
    for i, (s, l) in enumerate(zip(SHOTS, lumas)):
        b = 0.0 if l is None else max(-0.06, min(0.06, (target - l) / 255 * 0.7))
        print(f"shot {i:02d} {s['src']} ss={s['ss']} dur={s['dur']} yavg={l and round(l,1)} brightness={b:+.3f}")
        parts.append(render_shot(i, s, b))
    total = sum(s["dur"] for s in SHOTS)
    lst = os.path.join(WORK, "concat.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    band = lambda a, b: (f"drawbox=x=0:y=1240:w=iw:h=230:color=black@0.32:t=fill:enable='between(t,{a},{b})'")
    titles = ",".join([
        band(2.0, 4.0), band(8.0, 10.0),
        f"drawbox=x=0:y=270:w=iw:h=255:color=black@0.38:t=fill:enable='between(t,39.8,45)'",
        text("NASA SPACE APPS", FONT_B, 76, 1290, 2.15, 3.95),
        text("A S S I U T", FONT_M, 40, 1385, 2.3, 3.95),
        text("FROM IDEA TO PRODUCT", FONT_B, 60, 1300, 8.15, 9.95),
        text("Workshop by Eng. Hazem Zidan", FONT_M, 40, 1385, 8.3, 9.95),
        text("NASA SPACE APPS", FONT_B, 84, 300, 40.3, 45.2, fade=0.5),
        text("A S S I U T", FONT_M, 44, 405, 40.6, 45.2, fade=0.5),
        text("From Idea to Product  ·  Eng. Hazem Zidan", FONT_M, 38, 470, 41.0, 45.2, fade=0.5),
    ])
    vf = f"{titles},fade=t=out:st={total-0.3}:d=0.3,format=yuv420p"
    # audio: soundtrack only, except the closing shout, which plays over a ducked soundtrack
    cs = total - SHOTS[-1]["dur"]; cl = SHOTS[-1]
    ms = f"{cs:.3f}"
    af = (f"[1:a]volume='if(lt(t,{ms}),1,if(lt(t,{cs+0.5:.3f}),1-0.65*(t-{ms})/0.5,0.35))':eval=frame[m];"
          f"[2:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=90,volume=1.6,"
          f"afade=t=in:d=0.15,afade=t=out:st={cl['dur']-0.5}:d=0.5,adelay={int(cs*1000)}:all=1[s];"
          f"[m][s]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:level=0[a]")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", MUSIC,
         "-ss", str(cl["ss"]), "-t", str(cl["dur"]), "-i", path(cl["src"]),
         "-filter_complex", f"[0:v]{vf}[v];{af}", "-map", "[v]", "-map", "[a]", "-t", str(total),
         "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-b:v", "16M", "-maxrate", "20M", "-bufsize", "32M",
         "-r", str(FPS), "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", OUT])
    print("total", total)
