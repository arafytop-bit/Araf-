#!/bin/bash
# Final render of MincemeatShort at 1080x1920 in chunks (resumable). WORKER=k of WORKERS takes every WORKERS-th chunk.
# (software WebGL here: 2K direct would take ~4 h; the 1440x2560 export is a Lanczos upscale of this render)
cd /home/user/Araf-
T=2650; C=${CHUNK:-166}; W=${WORKERS:-1}; K=${WORKER:-0}; i=0
for ((a=0; a<T; a+=C)); do
  if (( i++ % W != K )); then continue; fi
  b=$((a+C-1)); [ $b -ge $T ] && b=$((T-1))
  out=out/final/chunk_$(printf %04d $a).mp4
  [ -s "$out" ] && { echo "skip $a-$b"; continue; }
  s=$(date +%s)
  npx remotion render src/index.ts MincemeatShort "$out.tmp.mp4" --frames=$a-$b --gl=swangle --browser-executable=/opt/pw-browsers/chromium \
    --concurrency=1 --codec=h264 --crf=14 --timeout=900000 --log=error > out/final/log_$a.txt 2>&1 \
    && mv "$out.tmp.mp4" "$out" && echo "done $a-$b in $(( $(date +%s)-s ))s" || { echo "FAILED $a-$b (see out/final/log_$a.txt)"; exit 1; }
done
echo WORKER_DONE $K
