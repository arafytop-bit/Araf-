"""Separate the reference mix into vocals/drums/bass/other with Demucs htdemucs (analysis only)."""
import sys, torch, numpy as np, soundfile as sf
from demucs.pretrained import get_model
from demucs.apply import apply_model
torch.set_num_threads(int(sys.argv[3]) if len(sys.argv)>3 else 2)
src, outdir = sys.argv[1], sys.argv[2]
wav, sr = sf.read(src, dtype='float32', always_2d=True)   # (n, 2) at 44.1k
model = get_model('htdemucs'); model.eval()
assert sr == model.samplerate, (sr, model.samplerate)
x = torch.from_numpy(wav.T.copy())
ref = x.mean(0); mean, std = ref.mean(), ref.std()
with torch.no_grad():
    est = apply_model(model, ((x-mean)/std)[None], shifts=1, split=True, overlap=0.25, progress=True, num_workers=0)[0]
est = est*std + mean
for name, s in zip(model.sources, est):
    sf.write(f"{outdir}/{name}.wav", s.numpy().T, sr, subtype='FLOAT')
print("DONE", model.sources)
