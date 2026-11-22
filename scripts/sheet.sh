#!/bin/bash
# usage: scripts/sheet.sh out.jpg in1.jpg in2.jpg ... (stacks horizontally, scaled to 360 wide each)
o=$1; shift; args=(); f=""; i=0
for x in "$@"; do args+=(-i "$x"); f="$f[$i:v]scale=360:-1[v$i];"; i=$((i+1)); done
s=""; for ((k=0;k<i;k++)); do s="$s[v$k]"; done
ffmpeg -loglevel error -y "${args[@]}" -filter_complex "${f}${s}hstack=$i" -q:v 3 "$o"
