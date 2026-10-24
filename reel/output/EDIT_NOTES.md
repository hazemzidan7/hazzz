# Edit Notes — NASA Space Apps Assiut Reel

## Deliverables
- `NASA_SPACE_APPS_ASSIUT_REEL_FINAL.mp4`: the final reel
- `soundtrack_original.wav`: the soundtrack (48 kHz master)
- `../scripts/compose_music.py`: generates the soundtrack
- `../scripts/build_reel.py`: the full edit as a reproducible timeline (shot list, grade, titles, export)
- `SHOT_SELECTION_REPORT.md`

Rebuild with:
`python3 scripts/compose_music.py output/soundtrack_original.wav`
then
`python3 scripts/build_reel.py <media_dir> <work_dir> output/soundtrack_original.wav output/NASA_SPACE_APPS_ASSIUT_REEL_FINAL.mp4`

## Soundtrack: source and licence
This environment cannot reach any royalty-free music library (Pixabay, FMA, Incompetech, ccMixter and others are blocked by the network policy). So I did not download a track.

Instead, the soundtrack is an **original instrumental composed for this reel in code**. It is synthesised from scratch and uses no samples or third-party audio, so there is no third-party copyright to clear.
- Style: cinematic electronic, 120 BPM, Am–F–C–G
- Structure: impact + pad intro (0–4 s), kick build (4–12 s), full groove with bass and arpeggio (12–28 s), snare roll + riser break (28–30 s), brightest peak (30–40 s), final impact and a chord that decays into the fade (40–45 s)
- Loudness: −12.8 LUFS integrated

Limitation: I checked the track by measurement (loudness per second, section arc), not by ear. It is clean and on-beat, but a synthesised track will not sound like a studio production.

To use a licensed track instead, put the file in the Drive folder. Swapping it in is one command, but the cuts are timed to this track's 120 BPM sections, so a different song may need small timing changes.

## Audio
Only the soundtrack is in the file. The original clip audio is never mapped (`-map 1:a` only).

## Transitions
- Mostly hard cuts, each on a beat (0.5 s grid)
- **Zoom-through cut** at 12 s (back-of-room wide → you), landing on the drop
- **Digital zoom**: slow push-ins and pull-outs on your shots, kept within 1.0–1.12× (1.45× only during the 0.3 s zoom-through)
- **Pull-back reveal**: the closing landscape shot, framed over a blurred, darkened fill so it is never upscaled
- Not used: phone mockup, orbit, paper cut, chart, green screen. They don't suit a documentary recap.

## Colour
1. HLG HDR (BT.2020) tonemapped to SDR Rec.709 with zscale + mobius (natural highlights and skin)
2. Per-shot exposure matching: each shot's mean luma is measured and nudged toward the median (±0.06 max)
3. Shared grade: contrast 1.07, saturation 1.08, slightly cool shadows and warm highlights
4. No skin smoothing, face changes or sharpening

## Stabilisation
None applied. I chose steady segments instead, which avoids the crop that stabilising would cost.

## Typography
Montserrat Bold and Medium, white with a soft shadow, centred inside the 9:16 safe area (y 1150–1400 of 1920). Lower thirds sit on a subtle 32% black band for legibility.

Text used (all of it is on the slide in `IMG_4715` or comes from the brief):
- "NASA SPACE APPS / ASSIUT"
- "FROM IDEA TO PRODUCT / Workshop by Eng. Hazem Zidan"
- Closing: "NASA SPACE APPS / ASSIUT / From Idea to Product · Eng. Hazem Zidan"

No NASA logo assets were added.

## Export (verified with ffprobe and a full decode)
- MP4, H.264 High, 1080×1920, 30 fps, yuv420p, BT.709 tags
- About 15.7 Mbps (16M target / 20M max), +faststart
- AAC-LC 320 kb/s, 48 kHz stereo
- Duration 45.000 s, 1350 frames
- blackdetect / freezedetect: none found. The final 0.5 s fade to black is intentional.

## Limitations
- I could not upload to Google Drive. The Drive connector only handles small files and this file is about 89 MB. The files are in `reel/output/`.
- I could not listen to the soundtrack or watch the video in real time. I reviewed one frame per second across the full reel plus targeted frames.
- CapCut is not available here, so the edit was built with FFmpeg.
