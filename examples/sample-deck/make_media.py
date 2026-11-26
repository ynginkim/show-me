#!/usr/bin/env python3
"""Make the neutral sample media for this example deck, then convert it with prep_media.py like real material.

Raw sources go to sources/ (not committed): a portrait "phone recording" (HEVC, 60 fps, like an iPhone capture),
a 16:9 "opening video", and a tall "document capture". prep_media.py turns them into slides/media/ and records
where each file came from in slides/media/media.json. Run from anywhere:  python3 examples/sample-deck/make_media.py"""
import subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PREP = HERE.parents[1] / 'skills/resolve-show-me-tools/scripts/prep_media.py'
SRC, MEDIA = HERE / 'sources', HERE / 'slides' / 'media'
SRC.mkdir(exist_ok=True)


def font(size):
    for p in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/System/Library/Fonts/Helvetica.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def frames_to_video(draw_frame, n, fps, size, out, codec):
    with tempfile.TemporaryDirectory() as td:
        for i in range(n):
            draw_frame(i).save(f'{td}/f{i:04d}.png')
        enc = ['-c:v', 'libx265', '-tag:v', 'hvc1', '-pix_fmt', 'yuv420p'] if codec == 'hevc' else ['-c:v', 'libx264', '-pix_fmt', 'yuv420p']
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', f'{td}/f%04d.png', '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000',
                        '-shortest', '-r', '60' if codec == 'hevc' else str(fps), *enc, '-c:a', 'aac', str(out)], check=True)


# portrait recording: 3 chapters × 2 s, numbered, with a moving progress bar
STEPS = [('STEP 1', (52, 120, 246)), ('STEP 2', (16, 185, 129)), ('STEP 3', (245, 158, 11))]
W, H, FPS = 590, 1278, 10


def phone(i):
    k = min(i // (2 * FPS), 2); lab, col = STEPS[k]
    im = Image.new('RGB', (W, H), (246, 247, 249)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 150), fill=col)
    d.text((40, 50), lab, fill='white', font=font(64))
    for r in range(5):
        y = 220 + r * 170
        d.rounded_rectangle((40, y, W - 40, y + 130), 24, fill=(255, 255, 255), outline=(220, 224, 230), width=3)
        d.rectangle((70, y + 40, 70 + (r + 2) * 50, y + 60), fill=(200, 205, 215))
    d.rectangle((0, H - 30, int(W * (i + 1) / (6 * FPS)), H), fill=col)
    return im


def wide(i):
    k = min(i // (3 * 10), 2); lab, col = [('OPENING', (15, 23, 42)), ('PART A', (30, 64, 175)), ('PART B', (6, 95, 70))][k]
    im = Image.new('RGB', (1280, 720), col); d = ImageDraw.Draw(im)
    x = 200 + (i % 30) * 30
    d.ellipse((x, 300, x + 120, 420), fill=(255, 255, 255))
    d.text((80, 80), lab, fill='white', font=font(96))
    return im


def document():
    im = Image.new('RGB', (1400, 4200), 'white'); d = ImageDraw.Draw(im)
    for s in range(6):
        y = 80 + s * 680
        d.text((100, y), f'Section {s + 1}', fill=(20, 26, 38), font=font(64))
        for r in range(8):
            d.rectangle((100, y + 120 + r * 60, 100 + (900 if r % 3 else 1150), y + 140 + r * 60), fill=(210, 214, 222))
        d.rounded_rectangle((100, y + 620 - 40, 1300, y + 640), 12, fill=(226, 240, 255))
    return im


if __name__ == '__main__':
    frames_to_video(phone, 6 * FPS, FPS, (W, H), SRC / 'phone_raw.mov', 'hevc')
    frames_to_video(wide, 90, 10, (1280, 720), SRC / 'opening_raw.mp4', 'h264')
    document().save(SRC / 'document_full.png')
    py = sys.executable
    subprocess.run([py, str(PREP), 'video', str(SRC / 'phone_raw.mov'), str(MEDIA / 'phone.mp4'), '--crf', '30', '--force'], check=True)
    subprocess.run([py, str(PREP), 'video', str(SRC / 'opening_raw.mp4'), str(MEDIA / 'opening.mp4'), '--height', '720', '--crf', '30', '--force'], check=True)
    subprocess.run([py, str(PREP), 'image', str(SRC / 'document_full.png'), str(MEDIA / 'document.jpg'), '--width', '1100', '--q', '80', '--force'], check=True)
    subprocess.run([py, str(PREP), 'poster', str(MEDIA / 'opening.mp4'), str(MEDIA / 'opening_poster.jpg'), '--at', '4'], check=True)
    subprocess.run([py, str(PREP), 'list', str(MEDIA)], check=True)
