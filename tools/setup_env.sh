#!/usr/bin/env bash
# Recreate the analysis/render environment (models, fonts, Python deps).
# Usage: bash tools/setup_env.sh [target_dir]   (default: ./.work)
set -euo pipefail
T="${1:-.work}"; mkdir -p "$T/models" "$T/fonts"
pip install --break-system-packages -q opencv-python-headless scipy scikit-learn soundfile sherpa-onnx resvg-py pandas numpy pillow
REL=https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models
if [ ! -d "$T/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8" ]; then
  curl -sL "$REL/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2" | tar xj -C "$T/models"
fi
[ -f "$T/models/silero_vad.onnx" ] || curl -sL -o "$T/models/silero_vad.onnx" "$REL/silero_vad.onnx"
GF=https://raw.githubusercontent.com/google/fonts/main/ofl
for f in gaegu/Gaegu-Regular.ttf gaegu/Gaegu-Bold.ttf gaegu/Gaegu-Light.ttf comicneue/ComicNeue-Bold.ttf comicneue/ComicNeue-Regular.ttf; do
  [ -f "$T/fonts/$(basename $f)" ] || curl -sL -o "$T/fonts/$(basename $f)" "$GF/$f"
done
echo "ready: $T"
