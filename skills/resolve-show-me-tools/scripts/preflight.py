#!/usr/bin/env python3
"""Check what this machine can do for show-me, and where the optional pieces are.

usage: preflight.py [--install]   (--install runs `npm install` in this folder: network, about 8 MB, no browser download)

Prints a JSON object: tools found (node, chrome, playwright-core, ffmpeg, ffprobe, Pillow, numpy), what each enables,
and an optional Lightplay installation (resolve-showreel-tools) when one is found. Nothing is installed without
--install, and nothing outside this folder is changed."""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def ver(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
    except Exception:
        return None


def chrome():
    for p in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
              'C:/Program Files/Google/Chrome/Application/chrome.exe'):
        if Path(p).exists():
            return p
    return shutil.which('google-chrome') or shutil.which('chrome')


def playwright():
    for c in [os.environ.get('SHOWME_PLAYWRIGHT'), str(HERE)]:
        if c and (Path(c) / 'node_modules' / 'playwright-core' / 'package.json').exists():
            return str(Path(c) / 'node_modules' / 'playwright-core')
    return None


def lightplay():
    """Find an installed Lightplay adapter (optional). Only reports a path; show-me never runs Lightplay's mode."""
    env = os.environ.get('LIGHTPLAY_SCRIPTS')
    if env and (Path(env) / 'preflight.py').exists():
        return str(Path(env).resolve())
    roots = [Path.cwd(), *Path.cwd().parents, Path.home()]
    for r in roots:
        for base in ('.claude/skills', '.agents/skills'):
            p = r / base / 'resolve-showreel-tools' / 'scripts'
            if (p / 'preflight.py').exists():
                return str(p.resolve())
    return None


def main():
    import argparse
    ap = argparse.ArgumentParser(description='show-me 환경 점검. JSON(caps, can, todo)을 출력한다. 아무것도 설치하지 않는다(--install 제외).')
    ap.add_argument('--install', action='store_true', help='이 폴더에서 npm install(playwright-core, 네트워크 약 14 MB, 브라우저 내려받기 없음)')
    ap.parse_args()
    if '--install' in sys.argv:
        subprocess.run(['npm', 'install', '--no-audit', '--no-fund'], cwd=HERE, check=True)
    node = ver(['node', '--version'])
    nmaj = int(re.sub(r'\D', '', node.split('.')[0])) if node else 0
    mods = {}
    for m in ('PIL', 'numpy'):
        try:
            mods[m] = __import__(m).__version__
        except Exception:
            mods[m] = None
    caps = {
        'scripts': str(HERE), 'node': node, 'node_ok': nmaj >= 18, 'chrome': chrome(), 'playwright_core': playwright(),
        'ffmpeg': shutil.which('ffmpeg'), 'ffprobe': shutil.which('ffprobe'), 'pillow': mods['PIL'], 'numpy': mods['numpy'],
        'lightplay_scripts': lightplay(),
    }
    can = {
        'new_deck': True,
        'shoot_and_check': bool(caps['node_ok'] and caps['chrome'] and caps['playwright_core'] and caps['pillow'] and caps['numpy']),
        'convert_video': bool(caps['ffmpeg'] and caps['ffprobe']),
        'convert_image': bool(caps['pillow']),
        'import_lightplay_files': True,
    }
    todo = []
    if not caps['playwright_core']:
        todo.append(f'playwright-core 없음: 사용자 승인 뒤 `python3 {HERE}/preflight.py --install` 또는 SHOWME_PLAYWRIGHT=<node_modules가 있는 폴더>')
    if not caps['chrome']:
        todo.append('Chrome 없음: 시스템 Chrome을 설치한다(촬영이 channel "chrome"을 쓴다)')
    if not caps['ffmpeg']:
        todo.append('ffmpeg 없음: 영상 변환을 못 한다(macOS: brew install ffmpeg)')
    if not (caps['pillow'] and caps['numpy']):
        todo.append('Pillow·numpy 없음: python3 -m pip install pillow numpy')
    print(json.dumps({'caps': caps, 'can': can, 'todo': todo}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
