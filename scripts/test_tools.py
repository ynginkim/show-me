#!/usr/bin/env python3
"""Repository tests for the show-me runtime tools (not installed with the skills).

usage: python3 scripts/test_tools.py [--no-browser]

Works on copies in a temporary folder; the repository and any Lightplay project are not modified.
1. new_deck: creates files, never overwrites index.html/deck.css/scenes.js, keeps a different engine unless
   --update-engine, and then backs up the old engine.
2. check_deck static faults (no browser): missing media file, unknown data-sec, budgets over the talk length,
   invalid data-chap → exit 1 with the matching message. The clean sample passes.
3. check_deck browser faults (skipped with --no-browser or when preflight cannot shoot): a scenes.js exception
   is reported as a page error and fails the check.
4. import_lightplay: a fake Lightplay project is imported (share copy, chapters from timeline.json, provenance
   in media.json) and stays byte-identical; a folder without the contract exits 2."""
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'skills/resolve-show-me-tools/scripts'
SAMPLE = ROOT / 'examples/sample-deck'
PY = sys.executable
results = []


def run(*cmd, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('PASS ' if cond else 'FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def tree_hash(p: Path):
    return {str(f.relative_to(p)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file()}


def copy_sample(tmp: Path, name: str):
    dst = tmp / name
    shutil.copytree(SAMPLE, dst, ignore=shutil.ignore_patterns('qa', 'sources'))
    return dst


def main():
    browser = '--no-browser' not in sys.argv
    if browser:
        pf = json.loads(run(PY, D / 'preflight.py').stdout)
        browser = pf['can']['shoot_and_check']
        if not browser:
            print('SKIP browser tests: ' + '; '.join(pf['todo']))
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        # 1. new_deck
        p = tmp / 'deck1'
        r = json.loads(run(PY, D / 'new_deck.py', p, '--title', '테스트', '--no-fonts').stdout)
        check('new_deck creates files', r['made'] == ['index.html', 'deck.css', 'scenes.js'] and r['engine']['action'] == 'copied')
        (p / 'slides/index.html').write_text('<!-- edited -->')
        (p / 'slides/engine/show-me.js').write_text('/* show-me engine 0.0.9 */')
        r = json.loads(run(PY, D / 'new_deck.py', p, '--no-fonts').stdout)
        check('new_deck keeps edited index.html', (p / 'slides/index.html').read_text() == '<!-- edited -->' and 'index.html' in r['kept'])
        check('new_deck keeps a different engine by default', r['engine']['action'] == 'differs-kept' and 'show-me engine 0.0.9' in (p / 'slides/engine/show-me.js').read_text())
        r = json.loads(run(PY, D / 'new_deck.py', p, '--no-fonts', '--update-engine').stdout)
        bk = Path(r['engine'].get('backup', '/nonexistent'))
        check('new_deck --update-engine backs up the old engine', r['engine']['action'] == 'updated' and (bk / 'show-me.js').read_text() == '/* show-me engine 0.0.9 */')

        # 2. static faults
        clean = copy_sample(tmp, 'clean')
        r = run(PY, D / 'check_deck.py', clean, '--no-shoot')
        check('clean sample passes static check', r.returncode == 0, r.stdout + r.stderr)
        faults = {
            'missing media': (lambda t: t.replace('media/document.jpg" alt=""', 'media/nope.jpg" alt=""'), '없는 파일 참조'),
            'unknown data-sec': (lambda t: t.replace('data-sec="b" data-title="이야기 카드', 'data-sec="z" data-title="이야기 카드'), '설정에 없는 data-sec'),
            'budget over length': (lambda t: t.replace('"length": 600', '"length": 300'), '강의 길이'),
            'invalid data-chap': (lambda t: t.replace('[[0,"STEP 1"', '[[oops,"STEP 1"'), 'data-chap'),
        }
        for name, (edit, msg) in faults.items():
            d = copy_sample(tmp, 'f_' + name.replace(' ', '_'))
            f = d / 'slides/index.html'; f.write_text(edit(f.read_text()))
            r = run(PY, D / 'check_deck.py', d, '--no-shoot')
            rep = json.loads((d / 'qa/deck/report.json').read_text())
            check(f'static fault detected: {name}', r.returncode == 1 and any(msg in x for x in rep['fails']), rep['fails'])

        # 3. browser fault
        if browser:
            d = copy_sample(tmp, 'f_scene_error')
            s = d / 'slides/scenes.js'; s.write_text(s.read_text() + '\nShowMe.scene("#bars", { init() { throw new Error("injected scene error"); } });\n')
            r = run(PY, D / 'check_deck.py', d, '--only', '1', '--no-auto')
            rep = json.loads((d / 'qa/deck/report.json').read_text())
            check('scene exception fails the check', r.returncode == 1 and any('injected scene error' in e['text'] for e in rep['shoot']['errors']), rep['fails'])

        # 4. Lightplay import
        lp = tmp / 'fake-video'
        for sub in ('out', 'qa'):
            (lp / sub).mkdir(parents=True)
        m = SAMPLE / 'slides/media'
        shutil.copy2(m / 'opening.mp4', lp / 'out/샘플_9s.mp4'); shutil.copy2(m / 'opening.mp4', lp / 'out/샘플_9s_공유용.mp4')
        shutil.copy2(m / 'opening_poster.jpg', lp / 'out/샘플_9s_포스터.jpg'); shutil.copy2(m / 'opening.mp4', lp / 'out/video.mp4')
        (lp / 'qa/qa_report.md').write_text('# QA\n')
        (lp / 'project.json').write_text(json.dumps({'width': 1280, 'height': 720, 'fps': 30, 'duration': 9.0}))
        (lp / 'timeline.json').write_text(json.dumps({'duration': 9.0, 'scenes': [{'id': 's01', 'start': 0, 'end': 4}, {'id': 's02', 'start': 4, 'end': 9}]}))
        before = tree_hash(lp)
        deck = tmp / 'deck2'
        run(PY, D / 'new_deck.py', deck, '--no-fonts')
        r = run(PY, D / 'import_lightplay.py', lp, deck)
        out = json.loads(r.stdout)
        mf = json.loads((deck / 'slides/media/media.json').read_text())
        check('import_lightplay copies the share video and chapters', r.returncode == 0 and out['video'].endswith('_공유용.mp4')
              and json.loads((deck / 'slides/media/opening.chapters.json').read_text()) == [[0, 's01', ''], [4, 's02', '']], out)
        check('import_lightplay records provenance', all(f.get('from') == 'lightplay' and len(f['source_sha256']) == 64 for f in mf['files']))
        check('Lightplay project unchanged', tree_hash(lp) == before)
        (tmp / 'empty').mkdir()
        r = run(PY, D / 'import_lightplay.py', tmp / 'empty', deck)
        check('non-Lightplay folder exits 2', r.returncode == 2)
    bad = [n for n, ok, _ in results if not ok]
    print(f'\n{len(results) - len(bad)}/{len(results)} passed' + (f' · failed: {bad}' if bad else ''))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
