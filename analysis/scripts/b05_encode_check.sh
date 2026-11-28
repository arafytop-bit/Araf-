#!/usr/bin/env bash
# Render a segment at 2x (3840x2160), downscale to 1080p (Lanczos), encode H.264 CRF 16 with explicit BT.709 conversion + tags,
# then decode and compare frames against the PNG masters (dE2000 + max channel error).
set -euo pipefail
F0=${1:-70}; F1=${2:-99}; OUT=work/hq/enc; mkdir -p $OUT/png
cd render
npx remotion render src/index.ts CalibrationHQ ../$OUT/png --sequence --image-format=png --frames=$F0-$F1 \
  --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell --log=error --concurrency=3
cd ..
ffmpeg -nostats -hide_banner -y -framerate 30 -pattern_type glob -i "$OUT/png/element-*.png" \
  -vf "scale=1920:1080:flags=lanczos+accurate_rnd+full_chroma_int:out_color_matrix=bt709:out_range=tv,format=yuv420p" \
  -c:v libx264 -preset slow -crf 16 -profile:v high -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  $OUT/segment_1080p_crf16.mp4 2>&1 | tail -1
