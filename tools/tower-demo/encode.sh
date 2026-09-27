#!/bin/sh
# Turns the newest Playwright recording into the files the site serves.
set -eu
FF=${FFMPEG:-ffmpeg}
OUT=../../web/public/media
SRC=$(ls -t /tmp/tower-demo-rec/*.webm | head -1)
mkdir -p "$OUT"
"$FF" -y -loglevel error -ss 1.2 -i "$SRC" -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart -an "$OUT/tower-walkthrough.mp4"
"$FF" -y -loglevel error -ss 1.2 -i "$SRC" -c:v libvpx-vp9 -b:v 0 -crf 40 -row-mt 1 -an "$OUT/tower-walkthrough.webm"
"$FF" -y -loglevel error -ss 44 -i "$OUT/tower-walkthrough.mp4" -frames:v 1 -q:v 3 "$OUT/tower-walkthrough-poster.jpg"
ls -la "$OUT"
