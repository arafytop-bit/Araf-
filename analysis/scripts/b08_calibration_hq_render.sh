#!/usr/bin/env bash
# Full high-fidelity calibration render: frames 0-149 at 3840x2160 -> 1080p CRF 16 master (+ reference audio for timing),
# and a full-resolution 3840x1080 side-by-side (reference upscaled 854x480 -> 1920x1080 Lanczos | rebuild) with frame counters.
# usage: bash analysis/scripts/b08_calibration_hq_render.sh '{"heroSrc":"hq/hero_bust.png","posterPrintSrc":"hq/hero_masked.png"}'
set -euo pipefail
PROPS=${1:-'{}'}
LABEL=${2:-'REBUILD (blueprint timing)'}
OUT=work/hq/final; mkdir -p $OUT/png analysis/calibration
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
cd render
npx remotion render src/index.ts CalibrationHQ ../$OUT/png --sequence --image-format=png --frames=0-149 --props="$PROPS" \
  --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell --log=error --concurrency=3
cd ..
SCALE="scale=1920:1080:flags=lanczos+accurate_rnd+full_chroma_int:out_color_matrix=bt709:out_range=tv,format=yuv420p"
TAGS="-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv"
ffmpeg -nostats -hide_banner -y -framerate 30 -pattern_type glob -i "$OUT/png/element-*.png" -i work/ref/ref.mp4 -map 0:v -map 1:a -t 5 \
  -vf "$SCALE" -c:v libx264 -preset slow -crf 16 -profile:v high $TAGS -c:a aac -b:a 320k -ar 48000 -shortest $OUT/calibration_hq_1080p.mp4
ffmpeg -nostats -hide_banner -y -i work/ref/ref.mp4 -i $OUT/calibration_hq_1080p.mp4 -t 5 -filter_complex \
 "[0:v]trim=end_frame=150,setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,drawtext=fontfile=$FONT:text='REFERENCE (480p source, upscaled)  f%{n}':x=24:y=20:fontsize=40:fontcolor=yellow:box=1:boxcolor=black@0.7[a];\
  [1:v]scale=in_color_matrix=bt709:in_range=tv:flags=accurate_rnd+full_chroma_int,drawtext=fontfile=$FONT:text='$LABEL  f%{n}':x=24:y=20:fontsize=40:fontcolor=cyan:box=1:boxcolor=black@0.7[b];\
  [a][b]hstack=inputs=2,format=yuv420p[v]" -map "[v]" -map 0:a -c:v libx264 -preset slow -crf 16 $TAGS -c:a aac -b:a 192k -shortest analysis/calibration/calibration_hq_side_by_side.mp4
echo DONE
