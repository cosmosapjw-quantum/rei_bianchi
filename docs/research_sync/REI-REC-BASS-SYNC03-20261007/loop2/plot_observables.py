#!/usr/bin/env python3
import csv,json,pathlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=pathlib.Path(__file__).resolve().parents[1];out=R/'figures';out.mkdir(exist_ok=True)
r=json.loads((R/'loop2/TRANSFER_RESULT.json').read_text())
with (R/'loop2/common_grid.csv').open() as f:rows=list(csv.DictReader(f))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','pdf.fonttype':42})
fig,(ax,bx)=plt.subplots(1,2,figsize=(11,4.6),gridspec_kw={'width_ratios':[1.5,1]})
colors=['#6e7d91','#368f95','#234b90']
for level,color in enumerate(colors):
 data=[z for z in rows if z['level']==f'T{level}'];x=np.array([float(z['time_s']) for z in data])/1e13;y=np.array([float(z['delta_tau']) for z in data])*1e12
 if level==2:
  ax.fill_between(x,[float(z['conditional_delta_lo'])*1e12 for z in data],[float(z['conditional_delta_hi'])*1e12 for z in data],color=color,alpha=.16,label='T2 conditional input box')
 ax.plot(x,y,color=color,lw=1.6,ls=[':', '--','-'][level],label=f'T{level}: {8000*2**level:,} cells')
ax.set(xlabel=r'Normal time $t / 10^{13}\,\mathrm{s}$',ylabel=r'$[\tau_{\rm BI}(t)-\tau_{\rm FLRW}(t)] / 10^{-12}$',title='Paired optical-depth history',xlim=(0,1));ax.axhline(0,color='#85909d',lw=.7);ax.grid(alpha=.16);ax.legend(frameon=False,fontsize=8)
y=np.array([float(z['delta_tau_BI_minus_FLRW_decimal90'])*1e12 for z in r['paired']]);lo=np.array([float(z['conditional_delta_lo'])*1e12 for z in r['paired']]);hi=np.array([float(z['conditional_delta_hi'])*1e12 for z in r['paired']])
bx.errorbar(range(3),y,yerr=[y-lo,hi-y],fmt='o',color=colors[-1],capsize=6,lw=1.5);bx.plot(range(3),y,color=colors[-1],ls=':',lw=1)
bx.set(xticks=range(3),xticklabels=['T0\n8,000','T1\n16,000','T2\n32,000'],xlabel='Cells per history',ylabel=r'$\Delta\tau(t_0) / 10^{-12}$',title='Refinement and conditional boxes');bx.grid(axis='y',alpha=.16)
bx.text(.04,.06,'T2 − T1 = −6.189 × 10⁻¹⁶\nAll three conditional signs: positive',transform=bx.transAxes,fontsize=9,bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
fig.suptitle('Actual F08 → BASS: finite-history Thomson diagnostic',fontsize=14,fontweight='bold',y=.98)
fig.text(.07,.018,'Same normal-time window; D = 1; explicit truncated tail = 0. Shading/bars bound the endpoint-linear functional only.\nConditional stage boxes widen with refinement. No continuum, finite-temperature, or observational EoR certificate.',fontsize=9,color='#4b5563')
fig.tight_layout(rect=(0,.11,1,.93))
for ext in ['png','pdf']:fig.savefig(out/f'F08_BASS_CONDITIONAL_VISIBILITY.{ext}',dpi=200,bbox_inches='tight')
print('saved figures/F08_BASS_CONDITIONAL_VISIBILITY.png and .pdf')
