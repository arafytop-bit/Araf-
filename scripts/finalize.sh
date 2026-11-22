#!/bin/bash
# Join the 1080x1920 chunks, Lanczos-upscale to 1440x2560, mux the final mix (Remotion's silent track dropped), QA.
set -e
cd /home/user/Araf-/out/final
ls chunk_*.mp4 | sort | sed "s/^/file '/; s/$/'/" > list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i list.txt -c copy joined_1080.mp4
ffmpeg -loglevel error -y -i joined_1080.mp4 -i ../../shorts/mincemeat/audio/mix.wav -map 0:v:0 -map 1:a:0 \
  -vf "scale=1440:2560:flags=lanczos" -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -r 30 \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest mincemeat_final_2k.mp4
python3 ../../scripts/short_qa.py mincemeat_final_2k.mp4 qa shots.json > qa.txt 2>&1 || true
echo FINALIZED
