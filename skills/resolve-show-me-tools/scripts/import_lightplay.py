#!/usr/bin/env python3
"""Bring a finished Lightplay video into a show-me deck. The Lightplay project is only read, never written.

usage: import_lightplay.py <lightplay-project> <deck-project> [--name <deliverable base>] [--use share|master]
                           [--slug opening] [--onsite] [--dry-run]

Contract read from the Lightplay project (see link-lightplay/references/contract.md):
  project.json                     width, height, fps, duration
  timeline.json                    scenes[{id, start, end}] → chapter start times
  out/<base>.mp4                   master (finish.py)
  out/<base>_공유용.mp4             share copy (finish.py, smaller; default for slides)
  out/<base>_포스터.jpg             poster frame
  out/<base>.srt                   subtitles when the video has narration
  qa/qa_report.md                  present when the automatic delivery check ran (warn if missing)
Writes into <deck-project>/slides/media/: <slug>.mp4, <slug>_poster.jpg, <slug>.srt (if any),
<slug>.chapters.json ([[start, scene id, ""], …] — replace ids with titles from storyboard.md before use),
and media.json entries with the source path and SHA256. Prints a JSON summary; exit 2 if the project does not
match the contract."""
import argparse, datetime, hashlib, json, re, shutil, sys
from pathlib import Path

SKIP = re.compile(r'^(video|draft.*|.*\.tmp)$')


def sha256(p: Path):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def fail(msg, **kw):
    print(json.dumps({'ok': False, 'error': msg, **kw}, ensure_ascii=False, indent=1)); sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lightplay'); ap.add_argument('deck')
    ap.add_argument('--name'); ap.add_argument('--use', choices=['share', 'master'], default='share')
    ap.add_argument('--slug', default='opening'); ap.add_argument('--onsite', action='store_true'); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    lp, deck = Path(a.lightplay).resolve(), Path(a.deck).resolve()
    missing = [n for n in ('project.json', 'timeline.json', 'out') if not (lp / n).exists()]
    if missing:
        fail('Lightplay 프로젝트 계약 파일이 없다', missing=missing, project=str(lp))
    proj = json.loads((lp / 'project.json').read_text())
    tl = json.loads((lp / 'timeline.json').read_text())
    bases = sorted({p.stem for p in (lp / 'out').glob('*.mp4') if not p.stem.endswith('_공유용') and not SKIP.match(p.stem)})
    if a.name:
        bases = [b for b in bases if b == a.name]
    if len(bases) != 1:
        fail('납품 영상(out/<이름>.mp4)을 하나로 정하지 못했다. --name으로 고른다', candidates=bases)
    base = bases[0]
    files = {'master': lp / 'out' / f'{base}.mp4', 'share': lp / 'out' / f'{base}_공유용.mp4',
             'poster': lp / 'out' / f'{base}_포스터.jpg', 'srt': lp / 'out' / f'{base}.srt'}
    video = files[a.use] if files[a.use].exists() else files['master']
    scenes = [s for s in tl.get('scenes', []) if isinstance(s, dict) and 'start' in s]
    chapters = [[round(float(s['start']), 2), s.get('id', f'scene{i + 1}'), ''] for i, s in enumerate(scenes)]
    warnings = []
    if not (lp / 'qa' / 'qa_report.md').exists():
        warnings.append('qa/qa_report.md가 없다. 납품 검수 전 영상일 수 있다')
    if video != files[a.use]:
        warnings.append(f'{a.use} 파일이 없어 master를 쓴다')
    if abs(float(tl.get('duration', proj.get('duration', 0)) or 0) - float(proj.get('duration', 0) or 0)) > 0.5:
        warnings.append('timeline.json과 project.json의 길이가 다르다')
    media = deck / 'slides' / 'media'
    plan = [(video, media / f'{a.slug}.mp4', 'video'), (files['poster'], media / f'{a.slug}_poster.jpg', 'poster'),
            (files['srt'], media / f'{a.slug}.srt', 'subtitles')]
    plan = [(s, d, k) for s, d, k in plan if s.exists()]
    out = {'ok': True, 'lightplay': str(lp), 'deliverable': base, 'video': str(video), 'size': [proj.get('width'), proj.get('height')],
           'duration': proj.get('duration'), 'chapters': chapters, 'copy': [[str(s), str(d)] for s, d, _ in plan], 'warnings': warnings,
           'dry_run': a.dry_run}
    if not a.dry_run:
        media.mkdir(parents=True, exist_ok=True)
        mf = media / 'media.json'
        data = json.loads(mf.read_text()) if mf.exists() else {'files': []}
        for s, d, k in plan:
            shutil.copy2(s, d)
            rel = str(d.relative_to(deck / 'slides'))
            data['files'] = [f for f in data['files'] if f.get('file') != rel]
            data['files'].append({'file': rel, 'kind': k, 'source': str(s), 'source_sha256': sha256(s), 'bytes': d.stat().st_size,
                                  'made': datetime.datetime.now().isoformat(timespec='seconds'), 'share': 'onsite-only' if a.onsite else 'ok',
                                  'from': 'lightplay', 'lightplay_project': str(lp), 'cmd': ' '.join(sys.argv[1:])})
        (media / f'{a.slug}.chapters.json').write_text(json.dumps(chapters, ensure_ascii=False) + '\n')
        data['files'].sort(key=lambda f: f['file'])
        mf.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
