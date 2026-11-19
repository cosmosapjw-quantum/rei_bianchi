#!/usr/bin/env python3
from pathlib import Path
import csv,gzip,json,sys,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
u=Path(__file__).resolve().parents[1];r=Path(sys.argv[1]);data=list(csv.DictReader(gzip.open(u/'prefix_results/PAIRED_PREFIX_RESPONSES.csv.gz','rt')))
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2,'svg.fonttype':'none'})
fig,ax=plt.subplots(2,2,figsize=(12,8.5),layout='constrained')
colors=['#555555','#2166ac','#b2182b']
for coordinate,style in [('fixed_a','-'),('equal_elapsed_proper_time','--')]:
 rows=[x for x in data if x['axis']=='dt' and x['pair']=='PLUS_minus_ZERO' and x['coordinate']==coordinate and x['observable']=='temperature_K']
 x=np.array([1e4*np.log(float(t['reference_a_L0'])/(1/21)) for t in rows])
 for lev in range(3):
  y=np.array([1e6*float(t[f'response_L{lev}']) for t in rows]);ax[0,0].plot(x,y,style,color=colors[lev],lw=1.4,label=f'T{lev} '+('fixed a' if style=='-' else 'equal proper time'))
ax[0,0].set(title='A. Actual paired gas-temperature response',xlabel=r'$10^4\ln(a_0/a_{\rm IC})$',ylabel=r'$T_{+0.01}-T_0$ [$\mu$K]');ax[0,0].legend(fontsize=8,ncol=2)
rows=list(csv.DictReader((r/'results/PLUS_IC_lazy_0/raw/error_components.csv').open()));rows=[x for x in rows if x['outcome']=='accepted']
for key,label in [('HII','HII'),('HeII','HeII'),('HeIII','HeIII'),('thermal','thermal w'),('photon_N_L1','photon N L1'),('photon_U_L1','photon U L1')]:
 ax[0,1].semilogy([int(x['accepted_after']) for x in rows],[float(x[key]) for x in rows],label=label,lw=1)
ax[0,1].axhline(1e-5,color='black',ls=':',lw=1,label='original target');ax[0,1].set(title='B. Native acceptance components, original IC',xlabel='Accepted step',ylabel='Dimensionless local component');ax[0,1].legend(fontsize=8,ncol=2)
cost=json.loads((u/'prefix_results/STEP_DENSITY_AND_COST.json').read_text());density=cost['time_step_density'];vals=[density[k]['median_native_dln_a'] for k in ['PLUS_IC_lazy_0','PLUS_T1_ORIGINAL_START','PLUS_T2_FLOOR_START']]
ax[1,0].bar(['T0','T1','T2'],vals,color=colors,width=.6);ax[1,0].set_yscale('log');ax[1,0].set_ylim(1e-7,1e-5);ax[1,0].set(title='C. Measured step density on a common prefix',ylabel=r'Median native $\Delta\ln a$')
for i,v in enumerate(vals):ax[1,0].text(i,v*1.2,f'{v:.4g}\n{vals[0]/v:.3g}x steps',ha='center',fontsize=9)
summary=json.loads((u/'prefix_results/PAIRED_PREFIX_ERROR_SUMMARY.json').read_text());e=summary['results']['dE__PLUS_minus_ZERO__fixed_a']['observables']['temperature_K']
values=[e['absolute_single_history_D12'],e['max_D12']]
ax[1,1].bar(['Single-history gas T','Paired temperature response'],values,color=['#4d9221','#7b3294'],width=.55);ax[1,1].set_yscale('log');ax[1,1].set_ylim(1e-8,2e-2);ax[1,1].set(title='D. Energy 32 to 64: common bias cancels',ylabel='Maximum absolute difference [K]')
for i,v in enumerate(values):ax[1,1].text(i,v*1.3,f'{v:.5g} K',ha='center',fontsize=9)
fig.suptitle('REI AX11: source-qualified short-prefix data\nOriginal z=20 IC; no full-history convergence claim; workflow 10/17, expansion 28/88',fontsize=13)
fig.savefig(u/'AX11_NATIVE_RESULTS.png',dpi=180);fig.savefig(u/'AX11_NATIVE_RESULTS.svg');print('saved source-data figure')
