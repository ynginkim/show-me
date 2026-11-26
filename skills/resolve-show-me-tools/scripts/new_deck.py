#!/usr/bin/env python3
"""Create (or refresh) a show-me deck project.

usage: new_deck.py <project> [--title "제목"] [--kicker "20분 강의 · ..."] [--no-fonts] [--update-engine]

Creates <project>/slides/{index.html, deck.css, scenes.js, engine/, fonts/, media/} and <project>/qa/deck/.
- Never overwrites index.html, deck.css, scenes.js (the deck owns them after creation).
- engine/: copied from this skill's assets. If the deck already has an engine that differs, it is left alone and
  reported, unless --update-engine: then the old copy is kept in slides/engine/.prev-<version>-<time>/.
- fonts/: Pretendard (variable) and JetBrains Mono 500/700, SIL OFL. Copied from local font folders when present,
  otherwise downloaded (jsdelivr). Only fonts actually present are written to fonts/fonts.css, so a missing font
  never becomes a failed request. --no-fonts skips this (system fonts are used).
Prints a JSON summary."""
import argparse, datetime, filecmp, json, re, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'assets'
LOCAL_DIRS = [Path.home() / 'Library/Fonts', Path('/Library/Fonts'), Path.home() / '.local/share/fonts', Path('/usr/share/fonts')]
FONTS = [  # (file name in fonts/, family, weight, local file names to look for, download url)
    ('PretendardVariable.woff2', 'Pretendard', '45 920', ['PretendardVariable.woff2', 'PretendardVariable.ttf'],
     'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2'),
    ('JetBrainsMono-500.ttf', 'JB', '400 600', ['JetBrainsMono-Medium.ttf', 'JetBrainsMono-500.ttf'],
     'https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@2.304/fonts/ttf/JetBrainsMono-Medium.ttf'),
    ('JetBrainsMono-700.ttf', 'JB', '700 800', ['JetBrainsMono-Bold.ttf', 'JetBrainsMono-700.ttf'],
     'https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@2.304/fonts/ttf/JetBrainsMono-Bold.ttf'),
]


def engine_version(p: Path):
    m = re.search(r'show-me engine (\S+)', p.read_text(errors='replace')[:300]) if p.exists() else None
    return m.group(1) if m else None


def is_font(p: Path):
    if not p.exists() or p.stat().st_size < 1000:
        return False
    head = p.read_bytes()[:4]
    return head in (b'wOF2', b'wOFF', b'\x00\x01\x00\x00', b'OTTO', b'true')


def find_local(names):
    for d in LOCAL_DIRS:
        if not d.exists():
            continue
        for n in names:
            for p in d.rglob(n):
                return p
    return None


def setup_fonts(fdir: Path):
    fdir.mkdir(parents=True, exist_ok=True)
    faces, notes = [], []
    for fname, fam, wt, local_names, url in FONTS:
        dst = fdir / fname
        if not is_font(dst):
            src = find_local(local_names)
            if src and src.suffix == dst.suffix:
                shutil.copy2(src, dst); notes.append(f'{fname}: 로컬 복사 ({src})')
            else:
                r = subprocess.run(['curl', '-sfL', '--max-time', '90', '-o', str(dst), url], capture_output=True)
                if r.returncode == 0 and is_font(dst):
                    notes.append(f'{fname}: 내려받음 ({url})')
                else:
                    dst.unlink(missing_ok=True); notes.append(f'{fname}: 확보 실패 — 시스템 글꼴로 대체된다. 직접 넣으려면 fonts/{fname}')
                    continue
        fmt = 'woff2-variations' if fname.endswith('.woff2') and fam == 'Pretendard' else ('woff2' if fname.endswith('.woff2') else 'truetype')
        faces.append(f'@font-face {{ font-family: "{fam}"; src: url("{fname}") format("{fmt}"); font-weight: {wt}; }}')
    (fdir / 'fonts.css').write_text('/* new_deck.py가 만든다. 실제로 있는 글꼴만 적는다(SIL OFL: Pretendard, JetBrains Mono). */\n' + '\n'.join(faces) + '\n')
    return len(faces), notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--title', default='제목')
    ap.add_argument('--kicker', default='강의 자료')
    ap.add_argument('--no-fonts', action='store_true')
    ap.add_argument('--update-engine', action='store_true')
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    sl = proj / 'slides'
    for d in (sl / 'engine', sl / 'media', proj / 'qa' / 'deck'):
        d.mkdir(parents=True, exist_ok=True)
    made, kept = [], []
    for name in ('index.html', 'deck.css', 'scenes.js'):
        dst = sl / name
        if dst.exists():
            kept.append(name); continue
        txt = (ASSETS / 'template' / name).read_text()
        txt = txt.replace('{{TITLE}}', a.title).replace('{{KICKER}}', a.kicker)
        dst.write_text(txt); made.append(name)
    # engine copy
    src_e, dst_e = ASSETS / 'engine', sl / 'engine'
    installed = engine_version(src_e / 'show-me.js')
    deck_v = engine_version(dst_e / 'show-me.js')
    same = all((dst_e / f.name).exists() and filecmp.cmp(f, dst_e / f.name, shallow=False) for f in src_e.iterdir())
    engine = {'installed': installed, 'deck_before': deck_v, 'action': 'same' if same else None}
    if not same:
        if deck_v is None or a.update_engine:
            if deck_v is not None:
                bk = dst_e / f'.prev-{deck_v}-{datetime.datetime.now():%Y%m%d-%H%M%S}'
                bk.mkdir()
                for f in dst_e.glob('show-me.*'):
                    shutil.copy2(f, bk / f.name)
                engine['backup'] = str(bk)
            for f in src_e.iterdir():
                shutil.copy2(f, dst_e / f.name)
            engine['action'] = 'copied' if deck_v is None else 'updated'
        else:
            engine['action'] = 'differs-kept'
            engine['note'] = '덱의 엔진이 설치본과 다르다. 그대로 두었다. 갱신하려면 --update-engine(수정 전 촬영본을 먼저 남긴다)'
    fonts = {'skipped': True}
    if not a.no_fonts:
        n, notes = setup_fonts(sl / 'fonts')
        fonts = {'faces': n, 'notes': notes}
    elif not (sl / 'fonts' / 'fonts.css').exists():
        (sl / 'fonts').mkdir(exist_ok=True)
        (sl / 'fonts' / 'fonts.css').write_text('/* --no-fonts: 시스템 글꼴을 쓴다 */\n')
    print(json.dumps({'project': str(proj), 'slides': str(sl), 'made': made, 'kept': kept, 'engine': engine, 'fonts': fonts}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
