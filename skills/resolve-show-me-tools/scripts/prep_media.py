#!/usr/bin/env python3
"""Turn recordings and captures into media a browser plays offline, and record where each file came from.

usage:
  prep_media.py video  <src> <slides/media/x.mp4> [--height 1600] [--width W] [--fps 30] [--crf 22] [--trim a:b] [--mute] [--onsite] [--force]
  prep_media.py image  <src> <slides/media/x.jpg> [--width 1600] [--crop x0,x1] [--max-height H] [--q 84] [--onsite] [--force]
  prep_media.py thumbs <src_dir> <slides/media/thumb_dir> [--box 300x650] [--q 80] [--onsite]
  prep_media.py poster <video> <slides/media/x.jpg> --at 12.5
  prep_media.py list   <slides/media>

video: H.264 yuv420p + AAC 128k + faststart, scaled to --height (default 1600, never upscaled), --fps 30.
       Phone recordings (HEVC, 60 fps, 1180×2556) become ~1600 px tall H.264 that any browser plays from file://.
image: RGB JPEG, optional column crop (x0,x1 in source pixels) and height cap for very tall full-page captures.
Each output is recorded in the nearest media/media.json: file (relative to slides/), source path and SHA256, size,
dimensions, duration, the command, and share ("onsite-only" with --onsite: real client/personal screens that may be
shown in the room but must not be published or reused as examples). Existing outputs are skipped unless --force."""
import argparse, datetime, hashlib, json, shutil, subprocess, sys
from pathlib import Path


def sha256(p: Path):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def manifest_for(dst: Path):
    for p in [dst.parent, *dst.parents]:
        if p.name == 'media':
            return p / 'media.json', p.parent
    return dst.parent / 'media.json', dst.parent


def record(dst: Path, src: Path, kind: str, extra: dict, onsite: bool):
    mf, root = manifest_for(dst)
    data = json.loads(mf.read_text()) if mf.exists() else {'files': []}
    rel = str(dst.resolve().relative_to(root.resolve()))
    data['files'] = [f for f in data['files'] if f.get('file') != rel]
    proj = root.resolve().parent  # slides/ → project; sources inside the project are recorded relative to it
    s = src.resolve()
    shown = str(s.relative_to(proj)) if s.is_relative_to(proj) else str(s)
    entry = {'file': rel, 'kind': kind, 'source': shown, 'source_sha256': sha256(src) if src.is_file() else None,
             'bytes': dst.stat().st_size if dst.is_file() else None, 'made': datetime.datetime.now().isoformat(timespec='seconds'),
             'share': 'onsite-only' if onsite else 'ok',
             'cmd': ' '.join(str(Path(x).resolve().relative_to(proj)) if Path(x).is_absolute() and Path(x).resolve().is_relative_to(proj) else x for x in sys.argv[1:])}
    entry.update(extra)
    data['files'].append(entry)
    data['files'].sort(key=lambda f: f['file'])
    mf.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')


def probe(p: Path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,pix_fmt',
                        '-show_entries', 'format=duration', '-of', 'json', str(p)], capture_output=True, text=True)
    if r.returncode:
        return {}
    j = json.loads(r.stdout)
    v = next((s for s in j.get('streams', []) if s.get('codec_type') == 'video'), {})
    a = next((s for s in j.get('streams', []) if s.get('codec_type') == 'audio'), None)
    return {'codec': v.get('codec_name'), 'pix_fmt': v.get('pix_fmt'), 'width': v.get('width'), 'height': v.get('height'),
            'audio': a.get('codec_name') if a else None, 'duration': round(float(j.get('format', {}).get('duration', 0) or 0), 3)}


def cmd_video(a):
    src, dst = Path(a.src), Path(a.dst)
    if dst.exists() and not a.force:
        print(f'skip (exists): {dst}'); return
    dst.parent.mkdir(parents=True, exist_ok=True)
    scale = f'scale=-2:min({a.height}\\,ih)' if not a.width else f'scale=min({a.width}\\,iw):-2'
    cmd = ['ffmpeg', '-v', 'error', '-y']
    if a.trim:
        t0, t1 = a.trim.split(':'); cmd += ['-ss', t0, '-to', t1]
    cmd += ['-i', str(src), '-vf', f'{scale},fps={a.fps}', '-c:v', 'libx264', '-crf', str(a.crf), '-preset', 'medium', '-pix_fmt', 'yuv420p']
    cmd += ['-an'] if a.mute else ['-c:a', 'aac', '-b:a', '128k']
    cmd += ['-movflags', '+faststart', str(dst)]
    subprocess.run(cmd, check=True)
    info = probe(dst)
    record(dst, src, 'video', info, a.onsite)
    print(f'{dst} · {info.get("width")}×{info.get("height")} · {info.get("duration")} s · {dst.stat().st_size / 1e6:.1f} MB')


def cmd_image(a):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    src, dst = Path(a.src), Path(a.dst)
    if dst.exists() and not a.force:
        print(f'skip (exists): {dst}'); return
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert('RGB')
    x0, x1 = (map(int, a.crop.split(','))) if a.crop else (0, im.width)
    im = im.crop((x0, 0, x1, min(im.height, a.max_height or im.height)))
    if im.width > a.width:
        im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
    im.save(dst, quality=a.q, optimize=True, progressive=True)
    record(dst, src, 'image', {'width': im.width, 'height': im.height}, a.onsite)
    print(f'{dst} · {im.width}×{im.height} · {dst.stat().st_size / 1e3:.0f} KB')


def cmd_thumbs(a):
    from PIL import Image
    src, dst = Path(a.src), Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)
    bw, bh = map(int, a.box.split('x'))
    n = 0
    for p in sorted(src.iterdir()):
        if p.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
            continue
        out = dst / (p.stem + '.jpg')
        if out.exists():
            continue
        im = Image.open(p).convert('RGB'); im.thumbnail((bw, bh), Image.LANCZOS); im.save(out, quality=a.q, optimize=True)
        record(out, p, 'thumb', {'width': im.width, 'height': im.height}, a.onsite); n += 1
    print(f'{n} thumbs → {dst}')


def cmd_poster(a):
    src, dst = Path(a.src), Path(a.dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a.at), '-i', str(src), '-frames:v', '1', '-q:v', '3', str(dst)], check=True)
    record(dst, src, 'poster', {'at': a.at}, a.onsite)
    print(dst)


def cmd_list(a):
    mf = Path(a.dir) / 'media.json'
    data = json.loads(mf.read_text()) if mf.exists() else {'files': []}
    total = 0
    for f in data['files']:
        total += f.get('bytes') or 0
        print(f"{f['file']:<40} {f['kind']:<6} {(f.get('bytes') or 0) / 1e6:7.2f} MB  {f['share']:<11} ← {f['source']}")
    print(f'{len(data["files"])} files · {total / 1e6:.1f} MB · onsite-only {sum(f["share"] == "onsite-only" for f in data["files"])}')


def main():
    if not shutil.which('ffmpeg') and sys.argv[1:2] in (['video'], ['poster']):
        sys.exit('ffmpeg가 없습니다. 설치 후 다시 실행한다(macOS: brew install ffmpeg).')
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    v = sp.add_parser('video'); v.add_argument('src'); v.add_argument('dst')
    v.add_argument('--height', type=int, default=1600); v.add_argument('--width', type=int); v.add_argument('--fps', type=int, default=30)
    v.add_argument('--crf', type=int, default=22); v.add_argument('--trim'); v.add_argument('--mute', action='store_true')
    i = sp.add_parser('image'); i.add_argument('src'); i.add_argument('dst')
    i.add_argument('--width', type=int, default=1600); i.add_argument('--crop'); i.add_argument('--max-height', type=int); i.add_argument('--q', type=int, default=84)
    t = sp.add_parser('thumbs'); t.add_argument('src'); t.add_argument('dst'); t.add_argument('--box', default='300x650'); t.add_argument('--q', type=int, default=80)
    p = sp.add_parser('poster'); p.add_argument('src'); p.add_argument('dst'); p.add_argument('--at', type=float, required=True)
    for x in (v, i, t, p):
        x.add_argument('--onsite', action='store_true', help='현장 전용(공개·예제 재사용 금지)으로 기록')
    for x in (v, i):
        x.add_argument('--force', action='store_true')
    l = sp.add_parser('list'); l.add_argument('dir')
    a = ap.parse_args()
    {'video': cmd_video, 'image': cmd_image, 'thumbs': cmd_thumbs, 'poster': cmd_poster, 'list': cmd_list}[a.cmd](a)


if __name__ == '__main__':
    main()
