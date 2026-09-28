"""Cuts and encodes the two zero-to-running videos into web/public/media/.

    python3 encode.py

Uses ffmpeg from a container (Apple `container` CLI, image docker.io/linuxserver/ffmpeg) so nothing is installed
on the host. Inputs, all under out/:
  gate-raw.webm                      the terminal cast, recorded by record-terminal.mjs
  tower-video/seg*.webm              the Tower segments, recorded by tower-driver.mjs, cut by tower-cuts.json
The terminal video ends with the Tower footage of gate-api's canary (tower-cuts.json "terminal-tail").
"""
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent
OUT = HERE / 'out'
MEDIA = HERE.parent.parent / 'web' / 'public' / 'media'
IMAGE = 'docker.io/linuxserver/ffmpeg:latest'
cuts = json.loads((HERE / 'tower-cuts.json').read_text())


def ff(*args):
    """Runs ffmpeg with out/ mounted at /o and web/public/media at /m."""
    cmd = ['container', 'run', '--rm', '-v', f'{OUT}:/o', '-v', f'{MEDIA}:/m', IMAGE, '-hide_banner', '-loglevel', 'error', '-y', *args]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def cut(parts, name):
    """Cuts [(file, start, end), ...] and joins them into out/<name>.mp4 (H.264, 30 fps, 1440x900)."""
    inputs, filters = [], []
    for i, (f, a, b) in enumerate(parts):
        inputs += ['-i', f'/o/{f}']
        filters.append(f'[{i}:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,fps=30,scale=1440:900,setsar=1[v{i}]')
    concat = ''.join(f'[v{i}]' for i in range(len(parts))) + f'concat=n={len(parts)}:v=1:a=0[out]'
    ff(*inputs, '-filter_complex', ';'.join(filters + [concat]), '-map', '[out]',
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'/o/{name}.mp4')


def publish(name, target, poster_at):
    ff('-i', f'/o/{name}.mp4', '-c:v', 'copy', '-movflags', '+faststart', f'/m/{target}.mp4')
    ff('-i', f'/o/{name}.mp4', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '38', '-row-mt', '1', '-an', f'/m/{target}.webm')
    ff('-ss', str(poster_at), '-i', f'/o/{name}.mp4', '-frames:v', '1', '-q:v', '3', f'/m/{target}-poster.jpg')


tower_parts = [(f'tower-video/{f}.webm', a, b) for f, a, b in cuts['tower']]
terminal_parts = [('gate-raw.webm', 1.0, 100000)] + [(f'tower-video/{f}.webm', a, b) for f, a, b in cuts.get('terminal-tail', [])]

cut(terminal_parts, 'terminal-final')
cut(tower_parts, 'tower-final')
publish('terminal-final', 'zero-to-running-terminal', cuts.get('terminal-poster', 20))
publish('tower-final', 'zero-to-running-tower', cuts.get('tower-poster', 30))
for f in sorted(MEDIA.glob('zero-to-running-*')):
    print(f.name, f.stat().st_size // 1024, 'KB')
