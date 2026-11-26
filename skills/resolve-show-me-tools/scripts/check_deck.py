#!/usr/bin/env python3
"""Check a show-me deck: static references, time budget, media format, then screenshots, sheet and comparison.

usage: check_deck.py <project | slides dir | index.html> [--out <dir>] [--pw <playwright dir>] [--baseline <shots dir>]
                     [--actions <json>] [--only 3,5] [--no-shoot] [--no-auto]

Writes <project>/qa/deck/ (or --out): shots/*.png + shoot.json, sheet.png, sheet_interactions.png, compare/ (with
--baseline), report.md and report.json. Exit 1 when a mechanical check fails (page/console errors, missing local
files, broken media, budgets over the talk length, invalid config). Exit 0 does not mean the deck is good: the report
lists what only eyes on the shots and a rehearsal on the real screen can judge."""
import argparse, json, re, shutil, subprocess, sys, datetime
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMES = ('http:', 'https:', 'mailto:', 'tel:', 'obsidian:', 'javascript:', 'data:', '#')
VIDEO_EXT = ('.mp4', '.webm', '.mov', '.m4v')


class DeckParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides, self.refs, self.config_text, self._in_cfg, self.players = [], [], None, False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get('class') or '').split()
        if tag == 'section' and 'slide' in cls:
            self.slides.append({k[5:]: v for k, v in a.items() if k.startswith('data-')})
        if tag == 'script' and a.get('id') == 'showme-config':
            self._in_cfg, self.config_text = True, ''
        if 'player' in cls:
            self.players.append({'slide': len(self.slides), 'src': a.get('data-src'), 'chap': a.get('data-chap')})
        for k in ('src', 'href', 'data-src', 'data-zoom', 'poster'):
            if a.get(k):
                self.refs.append({'slide': len(self.slides), 'tag': tag, 'attr': k, 'url': a[k]})

    def handle_endtag(self, tag):
        if tag == 'script':
            self._in_cfg = False

    def handle_data(self, data):
        if self._in_cfg:
            self.config_text += data


def engine_version(p: Path):
    m = re.search(r'show-me engine (\S+)', p.read_text(errors='replace')[:300]) if p.exists() else None
    return m.group(1) if m else None


def probe(p: Path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,height,pix_fmt', '-show_entries', 'format=duration',
                        '-of', 'json', str(p)], capture_output=True, text=True)
    if r.returncode:
        return None
    j = json.loads(r.stdout)
    v = next((s for s in j.get('streams', []) if s.get('codec_type') == 'video'), {})
    return {'codec': v.get('codec_name'), 'pix_fmt': v.get('pix_fmt'), 'height': v.get('height'), 'duration': float(j.get('format', {}).get('duration', 0) or 0)}


def korean_font(size):
    from PIL import ImageFont
    for p in ('/System/Library/Fonts/AppleSDGothicNeo.ttc', '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
              '/usr/share/fonts/truetype/nanum/NanumGothic.ttf', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size), True
            except OSError:
                pass
    return ImageFont.load_default(), False


def sheet(files, labels, out: Path, cols=4, w=480):
    from PIL import Image, ImageDraw
    if not files:
        return None
    h = w * 9 // 16
    font, ko = korean_font(20)
    rows = (len(files) + cols - 1) // cols
    S = Image.new('RGB', (cols * (w + 12) + 12, rows * (h + 44) + 12), (24, 26, 32))
    d = ImageDraw.Draw(S)
    for k, (f, lab) in enumerate(zip(files, labels)):
        im = Image.open(f).convert('RGB').resize((w, h))
        x, y = 12 + (k % cols) * (w + 12), 12 + (k // cols) * (h + 44)
        S.paste(im, (x, y))
        d.text((x, y + h + 8), lab if ko else lab.encode('ascii', 'replace').decode(), fill=(230, 232, 238), font=font)
    S.save(out)
    return str(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target'); ap.add_argument('--out'); ap.add_argument('--pw'); ap.add_argument('--baseline'); ap.add_argument('--actions')
    ap.add_argument('--only'); ap.add_argument('--no-shoot', action='store_true'); ap.add_argument('--no-auto', action='store_true')
    a = ap.parse_args()
    t = Path(a.target).resolve()
    index = t if t.suffix == '.html' else (t / 'index.html' if (t / 'index.html').exists() else t / 'slides' / 'index.html')
    if not index.exists():
        sys.exit(f'index.html을 찾지 못했다: {t}')
    sl = index.parent
    proj = sl.parent if sl.name == 'slides' else sl
    out = Path(a.out).resolve() if a.out else proj / 'qa' / 'deck'
    out.mkdir(parents=True, exist_ok=True)
    fails, warns = [], []

    # ── static ──
    P = DeckParser(); P.feed(index.read_text())
    try:
        cfg = json.loads(P.config_text) if P.config_text is not None else {}
        if P.config_text is None:
            warns.append('설정 JSON(#showme-config)이 없다. 구간 예산·타이머 없이 동작한다')
    except json.JSONDecodeError as e:
        cfg = {}; fails.append(f'설정 JSON을 읽지 못했다: {e}')
    secs = cfg.get('sections', {}) or {}
    missing, machine_local = [], []
    css_refs = []
    for css in [sl / 'deck.css', sl / 'fonts' / 'fonts.css']:
        if css.exists():
            for u in re.findall(r'url\(\s*["\']?([^"\')]+)', css.read_text()):
                css_refs.append({'slide': 0, 'tag': css.name, 'attr': 'url()', 'url': u, 'base': css.parent})
    for r in P.refs + css_refs:
        u = r['url'].strip()
        if u.startswith(SCHEMES):
            continue
        if u.startswith('file://'):
            p = Path(re.sub(r'^file://', '', u).split('#')[0].split('?')[0])
            machine_local.append({'slide': r['slide'], 'url': u, 'exists': p.exists()}); continue
        p = (r.get('base') or sl) / u.split('#')[0].split('?')[0]
        if not p.exists():
            missing.append({'slide': r['slide'], 'where': f"{r['tag']}[{r['attr']}]", 'url': u})
    if missing:
        fails.append(f'없는 파일 참조 {len(missing)}개')
    if machine_local:
        warns.append(f'이 컴퓨터에서만 열리는 file:// 링크 {len(machine_local)}개(발표 컴퓨터에서 확인)')
    bad_chap = []
    for pl in P.players:
        try:
            ch = json.loads(pl['chap']) if pl['chap'] else []
            assert all(isinstance(c, list) and isinstance(c[0], (int, float)) for c in ch)
        except Exception:
            bad_chap.append(pl)
    if bad_chap:
        fails.append(f'플레이어 data-chap 형식 오류 {len(bad_chap)}개')
    unknown_sec = [(i + 1, s.get('sec')) for i, s in enumerate(P.slides) if s.get('sec') and s.get('sec') not in secs]
    if unknown_sec:
        fails.append(f'설정에 없는 data-sec {unknown_sec}')

    # ── budget ──
    length = cfg.get('length')
    budget_rows, plan_total = [], 0
    for k, s in secs.items():
        plans = [int(float(x.get('plan'))) for x in P.slides if x.get('sec') == k and x.get('plan')]
        n = sum(1 for x in P.slides if x.get('sec') == k)
        budget_rows.append({'key': k, 'name': s.get('name'), 'budget': s.get('budget'), 'slides': n, 'planned': sum(plans), 'planned_slides': len(plans)})
        if s.get('budget') and sum(plans) > s['budget']:
            warns.append(f"구간 {s.get('name')}: 예상 합 {sum(plans)}초가 예산 {s['budget']}초를 넘는다")
    common = [int(float(x.get('plan'))) for x in P.slides if not x.get('sec') and x.get('plan')]
    plan_total = sum(int(float(x.get('plan'))) for x in P.slides if x.get('plan'))
    bsum = sum((s.get('budget') or 0) for s in secs.values())
    if length and bsum > length:
        fails.append(f'구간 예산 합 {bsum}초가 강의 길이 {length}초를 넘는다')
    if length and plan_total > length:
        warns.append(f'슬라이드 예상 합 {plan_total}초가 강의 길이 {length}초를 넘는다')
    if not length:
        warns.append('설정에 length(강의 길이, 초)가 없어 전체 예산을 대조하지 못했다')

    # ── engine & media ──
    deck_v, inst_v = engine_version(sl / 'engine' / 'show-me.js'), engine_version(HERE.parent / 'assets' / 'engine' / 'show-me.js')
    if deck_v is None:
        warns.append('덱에 show-me 엔진 사본(engine/show-me.js)이 없다')
    elif deck_v != inst_v:
        warns.append(f'덱 엔진 {deck_v}와 설치본 {inst_v}가 다르다(갱신은 사용자가 요청할 때만)')
    vids, total = [], 0
    media = sl / 'media'
    if media.exists():
        for p in media.rglob('*'):
            if p.is_file():
                total += p.stat().st_size
            if p.suffix.lower() in VIDEO_EXT and shutil.which('ffprobe'):
                info = probe(p) or {}
                ok = info.get('codec') == 'h264' and info.get('pix_fmt') in ('yuv420p', 'yuvj420p')
                vids.append({'file': str(p.relative_to(sl)), **info, 'ok': ok})
                if not ok:
                    warns.append(f'{p.name}: {info.get("codec")}/{info.get("pix_fmt")} — 브라우저 재생을 위해 prep_media.py video로 H.264 yuv420p로 바꾼다')
    manifest = json.loads((media / 'media.json').read_text()) if (media / 'media.json').exists() else {'files': []}
    onsite = [f['file'] for f in manifest['files'] if f.get('share') == 'onsite-only']

    # ── shoot ──
    shoot = None
    if not a.no_shoot:
        cmd = ['node', str(HERE / 'shoot.mjs'), '--deck', str(index), '--out', str(out / 'shots')]
        for k, v in (('--pw', a.pw), ('--actions', a.actions), ('--only', a.only)):
            if v:
                cmd += [k, v]
        if a.no_auto:
            cmd.append('--no-auto')
        if (out / 'shots').exists():
            shutil.rmtree(out / 'shots')
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode:
            fails.append(f'촬영 실패(exit {r.returncode}): {r.stderr.strip()[-400:]}')
        else:
            shoot = json.loads((out / 'shots' / 'shoot.json').read_text())
            if shoot['errors']:
                fails.append(f"페이지·콘솔 오류 {len(shoot['errors'])}개")
            broken = [(s['n'], s['brokenImg']) for s in shoot['slides'] if s['brokenImg']] + \
                     [(s['n'], [v['src'] for v in s['vids'] if v['err'] or v['ready'] == 0]) for s in shoot['slides'] if any(v['err'] or v['ready'] == 0 for v in s['vids'])]
            if broken:
                fails.append(f'깨진 이미지·영상 {broken}')
            if shoot['timer'] is not None and not (shoot['timer'] or {}).get('visible'):
                fails.append('T를 눌러도 타이머가 보이지 않았다')
            shots = sorted((out / 'shots').glob('s[0-9][0-9].png'))
            byn = {s['n']: s for s in shoot['slides']}
            sheet(shots, [f"{p.stem} · {byn.get(int(p.stem[1:]), {}).get('sec') or '-'} · {byn.get(int(p.stem[1:]), {}).get('title', '')[:22]}" for p in shots], out / 'sheet.png')
            inter = [out / 'shots' / x['shot'] for x in shoot['interactions']]
            sheet(inter, [x['name'] for x in shoot['interactions']], out / 'sheet_interactions.png')
    cmp = None
    if a.baseline and shoot:
        subprocess.run([sys.executable, str(HERE / 'compare_shots.py'), a.baseline, str(out / 'shots'), '--out', str(out / 'compare')], check=True)
        cmp = json.loads((out / 'compare' / 'compare.json').read_text())

    # ── report ──
    res = {'deck': str(index), 'checked': datetime.datetime.now().isoformat(timespec='seconds'), 'engine': {'deck': deck_v, 'installed': inst_v},
           'slides': len(P.slides), 'config': cfg, 'fails': fails, 'warnings': warns, 'missing': missing, 'machine_local': machine_local,
           'budget': budget_rows, 'common_planned': sum(common), 'planned_total': plan_total, 'videos': vids, 'media_mb': round(total / 1e6, 1),
           'onsite_only': onsite, 'shoot': shoot and {k: shoot[k] for k in ('count', 'timer', 'errors')}, 'compare': cmp and cmp['rows']}
    (out / 'report.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
    L = [f'# 덱 검사 보고\n', f'- 덱: `{index}`', f'- 검사: {res["checked"]} · 슬라이드 {len(P.slides)}장 · 엔진 덱 {deck_v} / 설치본 {inst_v} · 미디어 {res["media_mb"]} MB',
         f'- 판정: {"자동 검사 실패 " + str(len(fails)) + "건" if fails else "자동 검사 통과"} · 경고 {len(warns)}건\n', '## 자동 검사\n']
    L += [f'- 실패: {x}' for x in fails] + [f'- 경고: {x}' for x in warns] + ([] if fails or warns else ['- 실패·경고 없음'])
    if shoot:
        L += [f"- 촬영: 슬라이드 {len(shoot['slides'])}장, 상호작용 {len(shoot['interactions'])}장, 오류 {len(shoot['errors'])}개",
              f"- 타이머: {shoot['timer']['text'] if shoot['timer'] else '구간 슬라이드 없음'}"]
        L += [f"  - [{e['at']}] {e['kind']}: {e['text'][:160]}" for e in shoot['errors'][:20]]
    L += ['\n## 구간 예산\n', f'강의 길이: {length or "미정"}초 · 구간 예산 합 {bsum}초 · 슬라이드 예상 합 {plan_total}초(구간 밖 {sum(common)}초)\n',
          '| 구간 | 예산(초) | 슬라이드 | 예상 합(초) | 예상 적은 장 |', '| --- | ---: | ---: | ---: | ---: |']
    L += [f"| {b['name']} | {b['budget'] or '-'} | {b['slides']} | {b['planned']} | {b['planned_slides']} |" for b in budget_rows]
    if shoot:
        L += ['\n## 슬라이드\n', '| 장 | 구간 | 제목 | 예상(초) | 화면 밖 | 잘린 글자 |', '| ---: | --- | --- | ---: | ---: | ---: |']
        L += [f"| {s['n']} | {s['sec'] or '-'} | {s['title']} | {s['plan'] or '-'} | {s['outsideCount']} | {s['clippedCount']} |" for s in shoot['slides']]
        det = [(s['n'], x) for s in shoot['slides'] for x in s['outside'][:3]] + [(s['n'], x) for s in shoot['slides'] for x in s['clipped'][:3]]
        L += [f"- {n}장: {x['el']} {x.get('box', x.get('over'))}" for n, x in det[:30]]
    if missing:
        L += ['\n## 없는 파일\n'] + [f"- {m['slide']}장 {m['where']}: `{m['url']}`" for m in missing]
    if machine_local:
        L += ['\n## 이 컴퓨터에서만 열리는 링크\n'] + [f"- {m['slide']}장 `{m['url']}` ({'있음' if m['exists'] else '없음'})" for m in machine_local]
    if cmp:
        ch = [r for r in cmp['rows'] if r.get('changed_px') or 'size_mismatch' in r]
        L += ['\n## 기준 촬영본과 비교\n', f"{len(cmp['rows'])}쌍 중 바뀐 것 {len(ch)}개. 자세한 표와 차이 그림: `compare/compare.md`"]
        L += [f"- {r['after']}: {r.get('changed_pct', '크기 다름')}% {r.get('bbox', '')}" for r in ch]
    if onsite:
        L += ['\n## 현장 전용 자료\n', '공개 게시·예제 재사용을 하지 않는다: ' + ', '.join(onsite)]
    L += ['\n## 눈으로 볼 것(에이전트)\n', '- `sheet.png`, `sheet_interactions.png`, 그리고 글이 많은 장은 `shots/sNN.png`를 원본 크기로 연다.',
          '- 볼 것: 맨 뒷줄에서 읽힐 글자 크기, 한 장에 한 메시지, 겹침·잘림, 영상 첫 프레임이 검은 화면이 아닌지, 청중의 말인지.',
          '\n## 사람 확인(미확인)\n', '- 발표할 화면(프로젝터·대형 모니터)에서의 가독성과 색', '- 리허설로 잰 구간별 시간(T 타이머)',
          '- 영상 소리와 음량', '- 내용과 말투가 청중에게 맞는지']
    (out / 'report.md').write_text('\n'.join(L) + '\n')
    print(f"report: {out / 'report.md'} · fails {len(fails)} · warnings {len(warns)}")
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
