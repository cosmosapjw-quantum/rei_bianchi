#!/usr/bin/env python3
"""Render saved Unit8 evidence only. No solvers, physical kernels or inference."""
import csv,json,pathlib,time
start=time.monotonic()
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter
ROOT=pathlib.Path(__file__).resolve().parents[2]
E=ROOT/'evidence';F=ROOT/'figures';F.mkdir(exist_ok=True)
with (E/'lih_CLT_LTE_cooling.csv').open() as f: cooling=list(csv.DictReader(f))
t=[float(r['T_K']) for r in cooling];power=[float(r['power_W_per_molecule']) for r in cooling]
c2=json.loads((E/'GAMMA_COLLISION_COUNT_RESULT.json').read_text());n=[1,2,4,8,16]
# Unit conversion only: eV to keV. Both energy summaries are already exported.
photon=[c2['fine_states'][str(k)]['mean_E_eV']/1000 for k in n]
electron=[c2['fine_states'][str(k)]['cumulative_K_eV']/1000 for k in n]
quantities=['YPBBN','DoH','He3oH','Li7oH','Be7','Li7']
with (E/'nuclear_prior_correlation.csv').open() as f:
    reader=csv.DictReader(f);rows={r['quantity']:r for r in reader}
corr=np.array([[float(rows[a][b]) for b in quantities] for a in quantities])
d=json.loads((E/'NUCLEAR_PRIOR_RESULT.json').read_text());N=d['sample_count']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':15,'axes.labelsize':13,'xtick.labelsize':11,'ytick.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#676b70','text.color':'#20252b','axes.labelcolor':'#20252b','xtick.color':'#20252b','ytick.color':'#20252b','pdf.fonttype':42})
fig=plt.figure(figsize=(17,6.2),facecolor='white')
gs=fig.add_gridspec(1,3,left=.065,right=.965,bottom=.27,top=.79,wspace=.40,width_ratios=[1,1,1.13])
a=fig.add_subplot(gs[0,0]);b=fig.add_subplot(gs[0,1]);c=fig.add_subplot(gs[0,2])
fig.text(.065,.935,'Unit 8 | Saved numerical results',fontsize=22,fontweight='bold',ha='left')
fig.text(.065,.877,'Molecular LTE emission, collision-count energy transfer, and nuclear-prior correlations',fontsize=13,ha='left',color='#545b63')
a.loglog(t,power,color='#1764a0',linewidth=2.6)
a.set(title='B | LiH LTE line cooling',xlabel='Temperature T (K)',ylabel='Cooling power (W per molecule)')
a.grid(which='major',color='#dfe3e7',linewidth=.7);a.set_axisbelow(True);a.set_xlim(min(t),max(t))
a.set_xticks([10,100,1000,5000]);a.xaxis.set_major_formatter(ScalarFormatter());a.minorticks_off()
b.plot(n,photon,'o-',color='#1764a0',linewidth=2.4,markersize=7,label='Mean photon energy')
b.plot(n,electron,'s--',color='#bd6c0e',linewidth=2.4,markersize=6,label='Cumulative electron K')
b.set_xscale('log',base=2);b.set_xticks(n,labels=[str(k) for k in n]);b.set_xlim(.9,18);b.set_ylim(0,500)
b.set(title='C2 | Compton collision sequence',xlabel='Collision count n (not time)',ylabel='Energy (keV per emitted photon)')
b.grid(axis='y',color='#dfe3e7',linewidth=.7);b.set_axisbelow(True);b.legend(loc='upper left',bbox_to_anchor=(0,1.02),fontsize=10.5,frameon=False)
im=c.imshow(corr,vmin=-1,vmax=1,cmap='RdBu_r',interpolation='nearest',aspect='equal')
labels=[r'$Y_P$',r'D/H',r'$^3$He/H',r'$^7$Li/H',r'$Y_{^7\!Be}$',r'$Y_{^7\!Li}$']
c.set_xticks(range(6),labels=labels,rotation=45,ha='right',rotation_mode='anchor');c.set_yticks(range(6),labels=labels)
c.set_title(f'D | Prior correlation (N = {N})',pad=13)
for i in range(6):
    for j in range(6):c.text(j,i,f'{corr[i,j]:.2f}',ha='center',va='center',fontsize=10.5,color='white' if abs(corr[i,j])>.65 else '#172027')
c.tick_params(length=0);c.set_xticks(np.arange(-.5,6,1),minor=True);c.set_yticks(np.arange(-.5,6,1),minor=True);c.grid(which='minor',color='white',linewidth=.65);c.tick_params(which='minor',length=0)
cb=fig.colorbar(im,ax=c,fraction=.045,pad=.04,ticks=[-1,0,1]);cb.set_label('Correlation r (dimensionless)',fontsize=11);cb.ax.tick_params(labelsize=10)
fig.text(.065,.13,'ExoMol CLT lines; LTE populations.\nPer molecule; no abundance weighting.',fontsize=11,ha='left',va='top',linespacing=1.5)
fig.text(.393,.13,'Cold-electron collision-count propagation.\nCumulative K is transferred energy, not heat.',fontsize=11,ha='left',va='top',linespacing=1.5)
fig.text(.718,.13,'PRIMAT small-network prior; finite N.\nNo observational fit or convergence claim.',fontsize=11,ha='left',va='top',linespacing=1.5)
render=[]
for suffix in ['png','pdf']:
    p=F/('UNIT8_RESULTS.'+suffix);ts=time.monotonic();fig.savefig(p,dpi=180,facecolor='white');render.append({'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'save_wall_s':time.monotonic()-ts})
plt.close(fig)
receipt={'status':'RENDERED_ONE_PASS','operation':'Saved-evidence visualization only; eV->keV display unit conversion. No BBN, physical model, new covariance or spectrum calculations.','inputs':['evidence/lih_CLT_LTE_cooling.csv','evidence/GAMMA_COLLISION_COUNT_RESULT.json','evidence/nuclear_prior_correlation.csv','evidence/NUCLEAR_PRIOR_RESULT.json'],'cooling_rows':len(cooling),'cooling_T_K_range':[min(t),max(t)],'collision_counts':n,'nuclear_sample_count':N,'displayed_quantities':quantities,'outputs':render,'actual_process_wall_s':time.monotonic()-start,'budget_s':10,'visual_review':'pending parent inspection of actual PNG'}
(F/'UNIT8_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
