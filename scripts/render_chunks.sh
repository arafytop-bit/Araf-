#!/bin/bash
# Final 2K render of MincemeatShort in chunks (resumable: skips chunks already on disk).
cd /home/user/Araf-
T=2650; C=${CHUNK:-332}
for ((a=0; a<T; a+=C)); do
  b=$((a+C-1)); [ $b -ge $T ] && b=$((T-1))
  out=out/final/chunk_$(printf %04d $a).mp4
  [ -s "$out" ] && { echo "skip $a-$b"; continue; }
  s=$(date +%s)
  npx remotion render src/index.ts MincemeatShort "$out.tmp.mp4" --frames=$a-$b --gl=swangle --browser-executable=/opt/pw-browsers/chromium \
    --concurrency=${CONC:-3} --scale=1.3333333333333333 --codec=h264 --crf=16 --timeout=900000 --log=error > out/final/log_$a.txt 2>&1 \
    && mv "$out.tmp.mp4" "$out" && echo "done $a-$b in $(( $(date +%s)-s ))s" || { echo "FAILED $a-$b (see out/final/log_$a.txt)"; exit 1; }
done
echo ALL_DONE
