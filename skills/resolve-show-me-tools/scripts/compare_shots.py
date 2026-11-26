#!/usr/bin/env python3
"""Compare two folders of deck screenshots by file name and report pixel differences.

usage: compare_shots.py <before_dir> <after_dir> --out <dir> [--tol 8] [--map a.png=b.png ...]

For each PNG present in both folders: changed pixel count and share (any channel differs by more than --tol),
max channel difference, and the bounding box of the changed area. Writes diff images (changed pixels in red over
a dimmed copy of the after image) for files that differ, plus compare.json and compare.md. Exit code 0 always:
the report, not the exit code, says what changed (a revise expects some slides to change)."""
import argparse, json
from pathlib import Path
import numpy as np
from PIL import Image


def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(np.int16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('before'); ap.add_argument('after')
    ap.add_argument('--out', required=True)
    ap.add_argument('--tol', type=int, default=8)
    ap.add_argument('--map', nargs='*', default=[], help='before.png=after.png pairs when names differ')
    a = ap.parse_args()
    b, c, out = Path(a.before), Path(a.after), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pairs = {p.name: p.name for p in sorted(b.glob('*.png')) if (c / p.name).exists()}
    pairs.update(dict(m.split('=', 1) for m in a.map))
    only_before = sorted(p.name for p in b.glob('*.png') if p.name not in pairs)
    only_after = sorted(p.name for p in c.glob('*.png') if p.name not in pairs.values())
    rows = []
    for x, y in pairs.items():
        A, B = load(b / x), load(c / y)
        if A.shape != B.shape:
            rows.append({'before': x, 'after': y, 'size_mismatch': [A.shape[:2], B.shape[:2]]}); continue
        d = np.abs(A - B).max(axis=2)
        m = d > a.tol
        n = int(m.sum())
        row = {'before': x, 'after': y, 'changed_px': n, 'changed_pct': round(100 * n / m.size, 4), 'max_diff': int(d.max())}
        if n:
            ys, xs = np.nonzero(m)
            row['bbox'] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
            vis = (B * 0.35).astype(np.uint8); vis[m] = [255, 40, 40]
            Image.fromarray(vis).save(out / f'diff_{Path(y).stem}.png')
            row['diff'] = f'diff_{Path(y).stem}.png'
        rows.append(row)
    res = {'before': str(b.resolve()), 'after': str(c.resolve()), 'tol': a.tol, 'rows': rows, 'only_before': only_before, 'only_after': only_after}
    (out / 'compare.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
    lines = [f'# 촬영본 비교\n', f'- 기준: `{b}`', f'- 대상: `{c}`', f'- 허용 오차: 채널 차이 {a.tol} 이하는 같은 픽셀로 본다\n',
             '| 기준 | 대상 | 바뀐 픽셀 | 비율(%) | 최대 차이 | 바뀐 영역(x0,y0,x1,y1) |', '| --- | --- | ---: | ---: | ---: | --- |']
    for r in rows:
        if 'size_mismatch' in r:
            lines.append(f"| {r['before']} | {r['after']} | 크기 다름 {r['size_mismatch']} | | | |"); continue
        lines.append(f"| {r['before']} | {r['after']} | {r['changed_px']} | {r['changed_pct']} | {r['max_diff']} | {r.get('bbox', '')} |")
    if only_before: lines.append(f'\n기준에만 있음: {", ".join(only_before)}')
    if only_after: lines.append(f'\n대상에만 있음: {", ".join(only_after)}')
    (out / 'compare.md').write_text('\n'.join(lines) + '\n')
    same = sum(1 for r in rows if r.get('changed_px') == 0)
    print(f'{len(rows)} pairs · identical {same} · changed {len(rows) - same}')


if __name__ == '__main__':
    main()
