"""Plot the exact numerical evidence, no fabricated/illustrative curves."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]
evidence=json.loads((root/'evidence'/'SOURCE_AGE_NUMERICS.json').read_text())
figdir=root/'figures';figdir.mkdir(exist_ok=True)

fig,ax=plt.subplots(figsize=(8,5))
for r in evidence['signed_convergence']:
    xs=[e['n_time'] for e in r['data']]
    ys=[e['max_error_normalized'] for e in r['data']]
    ax.loglog(xs,ys,marker='o',label=f"s/H={r['v']:+.2f}")
ax.set_xlabel('transport steps per birth ray')
ax.set_ylabel('max relative-to-emitted-energy/count error vs DOP853')
ax.set_title('Event-aligned frozen-stock ray: proper time-resolution control')
ax.grid(True,which='both',alpha=.25);ax.legend();fig.tight_layout()
fig.savefig(figdir/'time_refinement.png',dpi=160);plt.close(fig)

fig,ax=plt.subplots(figsize=(8,5))
for v in [-.04,.04]:
    for split in [False,True]:
        q=[r for r in evidence['angular_refinement'] if r['v']==v and r['terminal_event_split']==split]
        ax.loglog([e['n_mu_target'] for e in q],
                  [e['abs_HeII_error_against_mu64_split'] for e in q],
                  marker='o',label=f"s/H={v:+.2f}, {'cut panels' if split else 'global GL'}")
ax.set_xlabel('requested angular nodes (effective panel nodes vary)')
ax.set_ylabel('absolute HeII absorbed-photons/H error vs cut-GL64')
ax.set_title('Source-age integrated angular-threshold refinement')
ax.grid(True,which='both',alpha=.25);ax.legend();fig.tight_layout()
fig.savefig(figdir/'angular_threshold.png',dpi=160);plt.close(fig)
print('FIGURES',[(p.name,p.stat().st_size) for p in figdir.glob('*.png')])
