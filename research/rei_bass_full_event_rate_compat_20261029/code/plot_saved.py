"""Saved-table source-only diagnostic figures, no trajectories or observational posteriors."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parents[1];sys.path.insert(0,str(p/'code'))
import event_rate_compat as m
r=m.selected_rows();z=np.array([float(q[0]) for q in r]);h=np.array([float(q[1]) for q in r]);i=np.array([float(q[3]) for q in r]);ii=np.array([float(q[5]) for q in r]);
fig,ax=plt.subplots(figsize=(7.1,4.3));ax.plot(z,ii/h,marker='o',label=r'He II / H I');ax.plot(z,i/h,marker='s',label=r'He I / H I');ax.set_yscale('log');ax.set_xlabel('Mean redshift z (Puchwein projection knots)');ax.set_ylabel('Photoionization-rate ratio (dimensionless)');ax.set_title('Fixed-spectrum scalar scaling cannot reproduce both ratio histories');ax.legend();fig.tight_layout();fig.savefig(p/'results/UVB_CHANNEL_RATIOS.png',dpi=160);plt.close(fig)

lo=float(m.ratio_exact(r[-1]));hi=float(m.ratio_exact(r[0]));kk=np.geomspace(lo/10,hi*10,600)
e=np.maximum(np.abs(kk-lo)/(kk+lo),np.abs(kk-hi)/(kk+hi));opt=float(m.minimax_two_epochs()['optimal_static_ratio']);err=float(m.minimax_two_epochs()['minimax_relative_error']);
fig,ax=plt.subplots(figsize=(7.1,4.3));ax.plot(kk,e,label='Two-epoch optimum over separate UV amplitudes');ax.scatter([opt],[err],s=45,label=f'Sharp lower bound: {100*err:.3f}%');ax.set_xscale('log');ax.set_ylim(0,1.02);ax.set_xlabel('Fixed BASS He II / H I source-shape rate ratio k');ax.set_ylabel('Best maximum relative rate error');ax.set_title('Sharp two-redshift H I / He II fixed-shape obstruction');ax.legend();fig.tight_layout();fig.savefig(p/'results/SHARP_TWO_EPOCH_MINIMAX.png',dpi=160);plt.close(fig)
print('two source-only PNGs saved; no IVP')
