#!/bin/sh
# Turns the newest Tower walkthrough recording into the files the site serves, and writes the chapter list.
# Needs an ffmpeg with libx264 and libvpx-vp9 (pip install imageio-ffmpeg gives a static one).
set -eu
FF=${FFMPEG:-ffmpeg}
OUT=../../web/public/media
REC=/tmp/tower-demo-rec
SRC=$(ls -t $REC/*.webm | head -1)
mkdir -p "$OUT"
# The page is loaded and the first caption is up a moment after the recording starts: trim to there.
SS=$(node -e "const r=require('$REC/chapters.raw.json');console.log((r.offset+0.2).toFixed(2))")
# The poster is the Ops Wall, a beat after it opens.
POSTER=$(node -e "const r=require('$REC/chapters.raw.json');const m=r.marks.find(x=>x[1].startsWith('What’s running'));console.log((Number(m[0])+r.offset-($SS)+1.5).toFixed(2))")
"$FF" -y -loglevel error -ss "$SS" -i "$SRC" -c:v libx264 -preset slow -crf 26 -tune stillimage -pix_fmt yuv420p -movflags +faststart -an "$OUT/tower-walkthrough.mp4"
"$FF" -y -loglevel error -ss "$SS" -i "$SRC" -c:v libvpx-vp9 -b:v 0 -crf 40 -row-mt 1 -an "$OUT/tower-walkthrough.webm"
"$FF" -y -loglevel error -ss "$POSTER" -i "$OUT/tower-walkthrough.mp4" -frames:v 1 -q:v 3 "$OUT/tower-walkthrough-poster.jpg"
node -e "
const r = require('$REC/chapters.raw.json');
const ss = $SS;
const mmss = s => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
const chapters = r.chapters.map((c, i) => { const t = i === 0 ? 0 : Math.max(0, c.t + r.offset - ss); return { start: mmss(t), seconds: Math.round(t * 10) / 10, title: c.title }; });
const total = Math.round((r.total + r.offset - ss) * 10) / 10;
require('fs').writeFileSync('tower-chapters.json', JSON.stringify({ video: '/media/tower-walkthrough.mp4', duration: mmss(total), durationSeconds: total, chapters }, null, 2) + '\n');
console.log(JSON.stringify(chapters));
"
ls -la "$OUT"/tower-walkthrough*
