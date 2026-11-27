"""Plot completed scalar evidence only; no model evaluation."""
import json,io,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create
a=json.loads((ROOT/'evidence/FINAL_AUDIT.json').read_bytes())
out=ROOT/'figures';out.mkdir(exist_ok=True)
if any((out/('small_r_scaled.'+ext)).exists() for ext in ('png','svg')):raise FileExistsError('create-only figure')
rows=a['sequence'];x=[r['R'] for r in rows];s=[r['S'] for r in rows]
fig,ax=plt.subplots(1,2,figsize=(9.2,3.6),layout='constrained')
ax[0].plot(x,s,'o-',color='#176b8e',lw=1.6,label='Finite-basis direct result')
ax[0].axhline(a['coefficient'],color='#ae4b2e',ls='--',label=r'$4\sqrt{2}/15$')
ax[0].set(xscale='log',xlabel=r'$x=R/a_A$',ylabel=r'$S=L_O/(-i\hbar x^3)$',title='Small-R finite sequence')
ax[0].set_xticks(x,[f'{r:g}' for r in x]);ax[0].legend(frameon=False,fontsize=8)
rx=[];space=[];lane=[]
for row in sorted(a['state_audit']['rows'],key=lambda r:r['R']):
 q=row['tiers'][0]['audit'];rx.append(row['R'])
 space.append(max(ref[l]['L_O_delta_scaled_abs'] for ref in q['checks']['refinements'].values() for l in ('direct','force')))
 lane.append(max(p['checks']['direct_force_L_O_scaled_abs'] for p in q['pairs'].values()))
ax[1].plot(rx,space,'o-',color='#176b8e',label='h/p/tail maximum')
ax[1].plot(rx,lane,'s-',color='#7e569f',label='Direct-force maximum')
ax[1].axhline(2e-6,color='#176b8e',ls=':',label='Spatial gate')
ax[1].axhline(1e-7,color='#7e569f',ls=':',label='Direct-force gate')
ax[1].set(xscale='log',yscale='log',xlabel=r'$x=R/a_A$',ylabel=r'Observed $|\Delta\bar L_O|/x^3$',title='Empirical numerical discrepancies')
ax[1].set_xticks(rx,[f'{r:g}' for r in rx]);ax[1].legend(frameon=False,fontsize=8)
for panel in ax:
 panel.grid(alpha=.18);panel.spines[['top','right']].set_visible(False)
 panel.xaxis.set_minor_locator(NullLocator())
fig.suptitle('C2c: finite sequence resolved; asymptotic remainder bound unknown',fontsize=11)
for ext in ('png','svg'):
 buffer=io.BytesIO();fig.savefig(buffer,format=ext,dpi=180)
 atomic_create(out/('small_r_scaled.'+ext),buffer.getvalue())
