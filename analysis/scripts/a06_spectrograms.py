"""10-s spectrogram pages (300 frames) for vocals / other / drums / bass with 1-frame resolution and frame gridlines."""
import sys, numpy as np, soundfile as sf, librosa, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SR=44100; HOP=1470; NFR=16731
st={n: sf.read(f'work/stems/{n}.wav', dtype='float32', always_2d=True)[0].mean(1) for n in ['vocals','other','drums','bass']}
M={}
for n,x in st.items():
    # hop 735 = 2 columns per frame; columns aligned so column 2N = start of frame N
    S=librosa.feature.melspectrogram(y=x, sr=SR, n_fft=2048, hop_length=735, n_mels=128, fmin=30, fmax=16000, center=False)
    M[n]=librosa.power_to_db(S, ref=1.0)
win=int(sys.argv[1]) if len(sys.argv)>1 else 300
starts=range(0, NFR, win)
for s in starts:
    e=min(NFR, s+win)
    fig,axs=plt.subplots(4,1,figsize=(24,10),sharex=True)
    for ax,n in zip(axs,['vocals','other','drums','bass']):
        seg=M[n][:, 2*s:2*e]
        ax.imshow(seg, origin='lower', aspect='auto', extent=[s, s+seg.shape[1]/2, 0, 128], vmin=-90, vmax=-10, cmap='magma', interpolation='nearest')
        for f in range(s, e+1):
            if f%30==0: ax.axvline(f, color='w', lw=0.9, alpha=0.9)
            elif f%5==0: ax.axvline(f, color='c', lw=0.4, alpha=0.5)
        ax.set_ylabel(n); ax.set_yticks([0,32,64,96,127]); ax.set_yticklabels([f'{int(v)}' for v in librosa.mel_frequencies(128, fmin=30, fmax=16000)[[0,32,64,96,127]]])
    axs[-1].set_xticks(range(s, e+1, 10)); axs[-1].set_xlabel('frame (white line = every 30 frames, cyan = every 5)')
    plt.tight_layout(); plt.savefig(f'analysis/spectrograms/spec_{s:05d}_{e-1:05d}.png', dpi=60); plt.close()
print('DONE', len(list(starts)))
