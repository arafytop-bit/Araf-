#!/bin/bash
# QA pass on a rendered v3 video: mux with the current mix, measure (4 fps sheets), automated audit, audio measures.
# usage: qa_pass.sh VIDEO_NOAUDIO TAG
set -e
V=$1; TAG=$2
S=/tmp/claude-0/-home-user-Araf-/81de6a8a-0e7a-5a80-9554-3f626d2780df/scratchpad
cd /home/user/Araf-/projects/epic_deaths/v3
python3 build3.py mux "$V" mix.wav $S/${TAG}.mp4 2>&1 | grep -v Fontconfig
python3 /home/user/Araf-/analysis/v2/measure.py $S/${TAG}.mp4 $S/m/$TAG --sheets > $S/m_${TAG}.log 2>&1
python3 /home/user/Araf-/analysis/v2/audit_v3.py $S/${TAG}.mp4 $S/m/$TAG render_qa.json $S/${TAG}_report.md
python3 /home/user/Araf-/analysis/v2/audio_measure.py $S/${TAG}.mp4 $S/m/$TAG/cuts.json 30 $S/${TAG}_audio.json > /dev/null
python3 /home/user/Araf-/analysis/v2/audio_qa.py mix.wav stems/music.wav > $S/${TAG}_audioqa.json
echo QA_DONE $TAG
