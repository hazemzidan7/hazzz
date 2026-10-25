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
Only the soundtrack plays from 0 to 39.8 s. The original clip audio is not used anywhere in that part.

The one exception, at the user's request, is the closing group clip (`IMG_3438`, 39.8–45 s). Its own audio (the countdown and the "Eduzah" shout) plays over the soundtrack, which is ducked to 35%. The clip audio is high-passed at 90 Hz, faded in and out, and the whole mix runs through a limiter (peak −1.2 dBFS).

I picked the shout from the loudness pattern, not by ear: three short bursts (7.3 / 8.2 / 9.0 s) and then one sustained shout at 10.0–11.2 s. There is also an earlier sustained shout at 3.1–4.6 s.

## Transitions
- Mostly hard cuts, each on a beat (0.5 s grid)
- **Zoom-through cut** at 12 s (back-of-room wide → you), landing on the drop
- **Digital zoom**: slow push-ins and pull-outs on your shots, kept within 1.0–1.12× (1.45× only during the 0.3 s zoom-through)
- **Closing push-in**: the 4K group shot starts framed over a blurred fill and pushes in to full frame (up to about 3.4×, still below 4K native, so nothing is upscaled), timed to land on the shout
- **Pull-back reveal**: the arms-raised landscape shot (0723), framed over a blurred, darkened fill so it is never upscaled
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

Text used (all of it is on the slide in `IMG_4715` or comes from the brief). The closing title sits at the top of the frame so it doesn't cover the students' faces:
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
- I could not listen to the soundtrack or the closing shout, or watch the video in real time. I reviewed one frame per second across the full reel plus targeted frames.
- CapCut is not available here, so the edit was built with FFmpeg.

---

# EDUZAH version: what changed

Files:
- `NASA_SPACE_APPS_ASSIUT_EDUZAH_REEL_FINAL.mp4`: main deliverable
- `NASA_SPACE_APPS_ASSIUT_EDUZAH_REEL_ALT_WITH_SHOUT.mp4`: same picture, with the closing "Eduzah" shout kept
- `NASA_SPACE_APPS_ASSIUT_REEL_FINAL.mp4`: the previous version, left untouched
- Build: `scripts/make_brand_assets.py`, then `scripts/build_reel_eduzah.py`

## Audio
**FINAL is soundtrack only.** The addendum requires all clip audio to be inaudible, so the closing shout from the previous version was removed.

Verified: I decoded the FINAL audio and compared it with `soundtrack_original.wav`. The difference is −43 to −62 dB in every 5-second window, which is the level of AAC encoding error. That means no clip audio is present.

Because the shout ending was something you asked for earlier, the ALT file keeps it, mixed over the ducked soundtrack exactly as before.

## Logo
- **Asset:** your official horizontal logo `IMG_3703.png`. I only trimmed its empty white margin and scaled it proportionally (150 px wide). It is not recoloured or redrawn.
- **Treatment:** the PNG has an opaque white background and no transparent version of the current identity was found, so I did not cut the background out. The logo sits unchanged on a small white rounded tag (94% opacity, soft shadow).
- **Placement:** top centre, y = 174–284 px, inside the Reels safe area, same position for the whole reel. It fades in at 0.6 s and goes out with the final fade.
- **Size:** the tag is about 18% of the frame width, the logo itself 14%. That is larger than the 5–8% guideline, because below this size the Arabic "ايدوزا" line becomes illegible on a phone.

## Brand colours (sampled from the official logo pixels)
- Plum `#321D3C`
- Magenta `#D81B5D`, used as the single accent
- Orange dot

Titles are white for legibility on the footage. Magenta is used only for the accent bars and the "×", because magenta text tested poorly on the bright classroom footage.

## Typography and animation
- **Font:** Montserrat ExtraBold for titles; SemiBold and Medium for supporting lines.
- **Line reveals:** each line fades in over 0.35–0.4 s while rising 20–40 px with an ease-out curve (no overshoot), and fades out over 0.25 s. Multi-line titles are staggered 0.15–0.2 s apart.
- **Accent bars:** the magenta bars grow from the centre over 0.45 s.
- **Legibility:** soft dark gradients sit behind text only while it is on screen, and they switch on at shot cuts.
- **Kinetic words:** "LEARNING." / "BUILDING." / "COLLABORATING." each land on the cut to the shot that shows them (14.0 / 21.5 / 26.0 s, on the beat).
- **No text during the peak** (28–40 s), so the footage carries it.

## Wording
The wording describes participation only: "EDUZAH AT …", "EDUZAH × …". There is no claim of organising, sponsorship, partnership or NASA endorsement, and no NASA logo is used.

## Export (both files verified)
- 45.000 s, 1350 frames, 1080×1920, H.264 High, 30 fps, about 16.5 Mbps
- AAC 48 kHz stereo
- Full decode clean
- No black or frozen frames
