import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
a = pd.read_csv('analysis/data/audio_frames.csv')
fig, axs = plt.subplots(4, 1, figsize=(22, 11), sharex=True)
def sm(x, k=15): return pd.Series(x).rolling(k, center=True, min_periods=1).mean()
for ax, (n, c) in zip(axs, [('vocals', 'tab:blue'), ('other', 'tab:orange'), ('drums', 'tab:green'), ('bass', 'tab:purple')]):
    ax.plot(a.frame, a[f'{n}_rms_db'], lw=0.3, color=c, alpha=0.5)
    ax.plot(a.frame, sm(a[f'{n}_rms_db']), lw=1, color='k')
    ax.set_ylabel(f'{n} dBFS'); ax.set_ylim(-80, -5); ax.grid(alpha=0.3)
    for ch in [4440, 6060, 7470, 9030, 9660, 10320, 11330, 13080, 15180, 16440]:
        ax.axvline(ch, color='r', lw=0.6, alpha=0.6)
axs[-1].set_xlabel('frame (30 fps); red = approx chapter-card / end-screen boundaries from overview')
axs[-1].set_xticks(np.arange(0, 16800, 600))
plt.tight_layout(); plt.savefig('analysis/plots/audio_stems_overview.png', dpi=70)
