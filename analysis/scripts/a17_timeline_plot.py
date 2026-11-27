"""Timeline plot: per-frame visual change (MAD), brightness, audio RMS (mix & voice), with event markers."""
import json, warnings, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')
m = pd.read_csv('analysis/data/frame_metrics.csv'); a = pd.read_csv('analysis/data/audio_frames.csv')
cuts = json.load(open('analysis/data/cuts.json')); words = json.load(open('analysis/data/words.json'))
sfx = pd.read_csv('analysis/data/sfx_candidates.csv'); ev = json.load(open('analysis/data/visual_events.json'))
txt = [e['f0'] for e in ev if e['type'] in ('text', 'ui')]; gfx = [e['f0'] for e in ev if e['type'] == 'graphic']
def panel(ax, f0, f1, label_words=False):
    sl = slice(f0, f1)
    x = m.frame.values[sl]
    ax.plot(x, m.mad.values[sl], color='0.3', lw=0.6, label='visual change (MAD)')
    ax.plot(x, m.y_mean.values[sl]/2, color='goldenrod', lw=0.8, label='brightness/2')
    ax2 = ax.twinx(); ax2.plot(x, a.vocals_rms_db.values[sl], color='tab:blue', lw=0.5, alpha=0.6, label='voice dB')
    ax2.plot(x, a.music_rms_db.values[sl], color='tab:purple', lw=0.6, alpha=0.7, label='music+sfx dB'); ax2.set_ylim(-80, 0)
    for c in cuts['hard_cuts']:
        if f0 <= c < f1: ax.axvline(c, color='r', lw=0.8)
    for t in cuts['transitions']:
        if f0 <= t['start'] < f1: ax.axvspan(t['start'], t['end'], color='r', alpha=0.15)
    for f in sfx.frame:
        if f0 <= f < f1: ax.plot(f, 118, 'v', color='tab:green', ms=4)
    for f in txt:
        if f0 <= f < f1: ax.plot(f, 108, 's', color='tab:orange', ms=3)
    for f in gfx:
        if f0 <= f < f1: ax.plot(f, 103, 'o', color='tab:cyan', ms=2.5)
    for w in words:
        if f0 <= w['start_f'] < f1:
            ax.plot(w['start_f'], 96, '|', color='tab:blue', ms=6)
            if label_words: ax.text(w['start_f'], 90, w['word'], fontsize=6, rotation=90, va='top')
    ax.set_xlim(f0, f1); ax.set_ylim(0, 122)
N = len(m); step = 1680
fig, axs = plt.subplots(10, 1, figsize=(24, 30))
for k, ax in enumerate(axs):
    panel(ax, k*step, min(N, (k+1)*step))
axs[0].legend(loc='upper left', fontsize=7)
axs[0].set_title('Timeline: red line = hard cut, red band = transition, green = SFX onset, orange = text/UI element, cyan = graphic, blue ticks = word onsets; grey = MAD, gold = brightness/2, blue/purple (right axis) = voice / music+SFX RMS dB')
plt.tight_layout(); plt.savefig('analysis/plots/timeline_full.png', dpi=55)
fig, ax = plt.subplots(1, 1, figsize=(26, 7)); panel(ax, 0, 300, label_words=True)
ax.set_title('First 10 s (frames 0-299) with word labels'); plt.tight_layout(); plt.savefig('analysis/plots/timeline_0000_0299.png', dpi=70)
print('ok')
