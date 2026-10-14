#!/usr/bin/env python3
"""Render only retained PHYS29 numbers; no kernel, roots or science import."""
from pathlib import Path
from decimal import Decimal as D, getcontext
import hashlib, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
getcontext().prec=80
RAW=ROOT/'contributions/numerics/SECOND_ORDER_FIRST.json'
data=json.loads(RAW.read_bytes())
assert data['summary']['all_pass']
result=data['second_order']['jet_chain']
comparison=data['delta_005_comparison']
out=ROOT/'figures/PHYS29_SECOND_ORDER_DECOMPOSITION.png'
assert not out.exists(),'Preserve earlier figures instead of overwriting them'
names=['Band average','Actual-variance correction','Support / probability motion','Implicit mixed derivative','Implicit variance curvature','Total d']
colors=['#376E99','#70824C','#A37B54','#806D99','#668D8C','#1A2E42']
groups={}
for label in ['upper_root','lower_root']:
    terms={k:D(v) for k,v in result[label]['d_decomposition_dimensionless'].items()}
    explicit=['uniform_band_averaging','center_variance_V_second','implicit_root_delta_W_cross','implicit_root_W_curvature']
    geometry=sum((v for k,v in terms.items() if k not in explicit),D(0))
    groups[label]=[terms['uniform_band_averaging'],terms['center_variance_V_second'],geometry,terms['implicit_root_delta_W_cross'],terms['implicit_root_W_curvature'],D(result[label]['d_dimensionless'])]

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':14,'axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#9AA6AF','text.color':'#253747','axes.labelcolor':'#253747','xtick.color':'#425463','ytick.color':'#425463','savefig.facecolor':'white'})
fig=plt.figure(figsize=(13.5,9.8))
gs=fig.add_gridspec(2,2,height_ratios=[1.25,1],left=.185,right=.978,bottom=.14,top=.89,hspace=.38,wspace=.16)
axes=[fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1])]
extent=max(abs(float(v)) for values in groups.values() for v in values)*1.22
for ax,label,title in zip(axes,['upper_root','lower_root'],[r'Upper-envelope threshold $W_*$ ',r'Lower-envelope threshold $W_0$']):
    values=[float(x) for x in groups[label]]
    y=np.arange(len(values))
    ax.barh(y,values,color=colors,height=.58)
    ax.axvline(0,color='#71808C',linewidth=.7)
    ax.set_yticks(y,names if ax is axes[0] else ['']*len(names))
    ax.invert_yaxis(); ax.set_xlim(-extent,extent)
    ax.set_title(title,pad=12); ax.set_xlabel(r'Contribution to $d$ (dimensionless)')
    ax.grid(axis='x',alpha=.14); ax.set_axisbelow(True)
    for yi,value in zip(y,values):
        ax.annotate(f'{value:+.5f}',(value,yi),xytext=(5 if value>=0 else -5,0),textcoords='offset points',ha='left' if value>=0 else 'right',va='center',fontsize=10)
    ax.axhline(4.5,color='#B2BBC1',linewidth=.7)

ax=fig.add_subplot(gs[1,:])
labels=[r'$W_*$',r'$W_0$','Coexistence-width reduction']
linear=[]; quadratic=[]
for label in ['upper_root','lower_root']:
    comp=comparison[label]
    linear.append(abs(float(comp['linear_residual_from_PHYS28_eV2'])))
    quadratic.append(abs(float(comp['residual_actual_minus_quadratic_eV2'])))
comp=comparison['coexistence_width']
linear.append(abs(float(comp['linear_reduction_residual_from_PHYS28_eV2'])))
quadratic.append(abs(float(comp['residual_actual_minus_quadratic_reduction_eV2'])))
x=np.arange(3)
for i,(l,q) in enumerate(zip(linear,quadratic)):
    if l>0 and q>0: ax.plot([i-.10,i+.10],[l,q],color='#9FACB5',linewidth=1.7,zorder=1)
for dx,values,color,marker,label in [(-.10,linear,'#A9B3BD','o','PHYS28 linear prediction'),(.10,quadratic,'#235E88','D','PHYS29 quadratic prediction')]:
    positive=[i for i,v in enumerate(values) if v>0]
    ax.scatter([i+dx for i in positive],[values[i] for i in positive],color=color,marker=marker,s=65,label=label,zorder=3)
    for i,value in enumerate(values):
        if value>0: ax.annotate(f'{value:.4g}',(i+dx,value),xytext=(-8 if dx<0 else 8,8 if dx<0 else -15),textcoords='offset points',ha='right' if dx<0 else 'left',fontsize=10)
ax.set_yscale('log');ax.set_ylim(4e-6,1.2e-2);ax.set_xticks(x,labels);ax.set_xlim(-.48,2.62)
ax.set_ylabel(r'Absolute residual ($\mathrm{eV}^2$, log scale)')
ax.set_title(r'Comparison with stored PHYS27 roots at half-width $\delta=0.05\,\mathrm{eV}$',pad=12)
ax.grid(axis='y',which='both',alpha=.13);ax.legend(loc='upper right',frameon=False,fontsize=10)
fig.suptitle('PHYS29 | Second-order threshold response at fixed actual photon variance',fontsize=16,weight='semibold',y=.974)
fig.text(.015,.024,'Four stored-root nodes, two algebraic paths. Bars aggregate retained components; full decomposition is in the report.\nSingle-width residuals are diagnostics; no Taylor-remainder bound or physical admission is claimed.',fontsize=9,color='#576875',va='bottom')
fig.savefig(out,dpi=200)
plt.close(fig)
receipt={'task':'REI-PHYS29-20261011','status':'RENDERED_PENDING_VISUAL_INSPECTION','raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),'figure':out.name,'figure_bytes':out.stat().st_size,'figure_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'matplotlib':matplotlib.__version__,'data':'Only retained PHYS29 raw values; Decimal sums for display aggregation and float plotting','new_scientific_main':0,'new_kernel_derivative_evaluations':0,'new_roots':0,'display_groups':{k:[str(v) for v in values] for k,values in groups.items()},'linear_absolute_residual_eV2':linear,'quadratic_absolute_residual_eV2':quadratic,'zero_residuals':sum(v==0 for v in linear+quadratic)}
(ROOT/'figures/DISPLAY_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['display_groups','linear_absolute_residual_eV2','quadratic_absolute_residual_eV2']},ensure_ascii=False))
