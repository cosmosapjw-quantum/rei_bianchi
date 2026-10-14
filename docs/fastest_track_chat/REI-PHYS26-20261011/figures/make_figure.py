#!/usr/bin/env python3
"""Display-only PHYS26 plot; no numerical validation, root or derivative campaign."""
from decimal import Decimal as D, getcontext
from hashlib import sha256
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

getcontext().prec=80
ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json'
data=json.loads(SOURCE.read_text())
c=data['constants']
a,m,b=map(D,[c['support_eV'][0],c['mean_eV'],c['support_eV'][1]])
L,H=m-a,b-m
wmax=L*H
jx,jw=D(c['J_h2_x']),D(c['J_h2_w'])
e0,ya,p,chi=map(D,[c['E0_eV'],c['ya'],c['P'],c['chi_eV']])
prefactor=D(c['prefactor'])
sigma0=D.from_float(float('5.475e4'))
area=D.from_float(float('1e-18'))
cache={}
def k(e):
    if e not in cache:
        x=e/e0;z=(x/ya).sqrt();r=p/2-D('5.5')
        sig=sigma0*(x-1)**2*(r*x.ln()-p*(1+z).ln()).exp()*area
        ell=2*x/(x-1)+r-p*z/(2*(1+z))
        dell=-2*x/(x-1)**2-p*z/(4*(1+z)**2)
        cache[e]=prefactor*sig*((ell*ell+dell+3*ell)*(jx+jw*(e-chi))+(2*ell+4)*jw*e)
    return cache[e]
ws=sorted({wmax*D(i)/80 for i in range(81)}|{D(row['W_eV2']) for row in data['variance_cases']})
points=[]
for w in ws:
    v=m+w/L;u=m-w/H
    high=(w*k(a)+L*L*k(v))/(L*L+w)
    low=(H*H*k(u)+w*k(b))/(H*H+w)
    points.append({'W_eV2':str(w),'Aminus_s-4':str(low),'Aplus_s-4':str(high)})
star=float(data['inherited_boundary_residuals']['Vstar_eV2'])
zero=float(data['inherited_boundary_residuals']['W0_eV2'])
mixed=next(row for row in data['variance_cases'] if row['label']=='mixed_19_74')
x=[float(row['W_eV2']) for row in points]
ylow=[float(D(row['Aminus_s-4'])/D('1e-64')) for row in points]
yhigh=[float(D(row['Aplus_s-4'])/D('1e-64')) for row in points]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
                    'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#243142',
                    'text.color':'#172b3a','xtick.color':'#445365','ytick.color':'#445365'})
fig=plt.figure(figsize=(13.8,7.5),facecolor='white')
gs=fig.add_gridspec(2,2,width_ratios=[1.72,1],wspace=.25,hspace=.60)
ax=fig.add_subplot(gs[:,0])
ax.axvspan(0,star,color='#eaf0fa',zorder=0)
ax.axvspan(star,zero,color='#fff3d9',zorder=0)
ax.axvspan(zero,float(wmax),color='#e5f1e9',zorder=0)
ax.fill_between(x,ylow,yhigh,color='#b7ccd4',alpha=.55,label='Attainable response interval')
ax.plot(x,yhigh,color='#007d74',lw=2.7,label=r'Upper $A_+(W)$')
ax.plot(x,ylow,color='#284e8c',lw=2.7,label=r'Lower $A_-(W)$')
for key,color,marker in [('Pa','#007d74','o'),('Pb','#284e8c','s')]:
    ax.scatter([float(row['W_eV2']) for row in data['variance_cases']],
               [float(D(row[key]['response_s-4'])/D('1e-64')) for row in data['variance_cases']],
               s=26,color=color,marker=marker,edgecolors='white',linewidths=.65,zorder=5)
ax.axhline(0,color='#5c6872',lw=1)
ax.axvline(star,color='#68778a',ls='--',lw=1)
ax.axvline(zero,color='#68778a',ls='--',lw=1)
ax.text(star,-1.365,r'$V_* = 16.3399$',ha='right',fontsize=10)
ax.text(zero,-1.445,r'$W_0 = 23.4202$',ha='center',fontsize=10)
ax.text(star/2,.655,r'All $A<0$',ha='center',fontsize=10,weight='bold',color='#284e8c')
ax.text((star+zero)/2,.655,'Both signs',ha='center',fontsize=10,weight='bold',color='#8a641f')
ax.text((zero+float(wmax))/2,.655,r'All $A>0$',ha='center',fontsize=10,weight='bold',color='#006e53')
ax.set(xlim=(0,float(wmax)),ylim=(-1.53,.76),xlabel=r'Photon-energy variance $W$ [eV$^2$]',
       ylabel=r'Initial response $A(P)$ [$10^{-64}$ s$^{-4}$]')
ax.set_xticks([0,5,10,15,20,25,float(wmax)],['0','5','10','15','20','25','28.8862'])
ax.grid(axis='y',color='#dae0e4',lw=.6)
ax.set_axisbelow(True)
ax.legend(loc='lower left',bbox_to_anchor=(.015,.008),frameon=True,facecolor='white',edgecolor='#d5dde2',fontsize=10)
ax.set_title('Exact envelope at mean 18 eV',loc='left',pad=30,fontsize=13)
for rowpos,key,color,title in [(0,'Pa','#007d74','Upper extremizer'),(1,'Pb','#284e8c','Lower extremizer')]:
    panel=fig.add_subplot(gs[rowpos,1])
    law=mixed[key]['law']
    energies=[float(z['energy_eV']) for z in law]
    probs=[float(z['probability']) for z in law]
    panel.vlines(energies,0,probs,color=color,lw=3)
    panel.scatter(energies,probs,s=65,color=color,zorder=3)
    panel.axvline(18,ls=':',lw=1,color='#adb8c0')
    for e,prob in zip(energies,probs):
        panel.annotate(f'{prob:.4f}',(e,prob),xytext=(0,9),textcoords='offset points',ha='center',fontsize=10)
    response=float(D(mixed[key]['response_s-4'])/D('1e-65'))
    panel.text(.97,.94,rf'$A={response:+.4f}\times10^{{-65}}$ s$^{{-4}}$',
               transform=panel.transAxes,ha='right',va='top',color=color,fontsize=11)
    panel.set(xlim=(12.85,25.3),ylim=(0,.83),ylabel='Photon-number probability')
    panel.set_xticks(energies,[f'{e:.4f}'.rstrip('0').rstrip('.') for e in energies])
    panel.set_title(f'{title}  |  W = 19.74 eV'+r'$^2$',loc='left',fontsize=11,pad=12)
    panel.set_xlabel('Line energy [eV]')
    panel.grid(axis='y',color='#e3e8ec',lw=.5)
    panel.set_axisbelow(True)
fig.suptitle('HeIII response: two variance thresholds, three sign regions',
             x=.055,y=.988,ha='left',fontsize=18,weight='bold')
fig.text(.055,.935,'Fixed numerical J  |  Photon-number mean 18 eV  |  Support [13.61, 24.58] eV',
         fontsize=11,color='#62717e')
fig.text(.055,.025,'Curves show the proved formulas; dots are the 7 preregistered cases. Continuum signs come from the proof. Physical admission: HOLD.',
         fontsize=9.4,color='#62717e')
fig.subplots_adjust(left=.075,right=.978,top=.83,bottom=.14)
output=HERE/'PHYS26_response_envelope.png'
fig.savefig(output,dpi=200)
plt.close(fig)
plotdata=HERE/'DISPLAY_DATA.json'
plotdata.write_text(json.dumps({'kind':'display only','points':points},indent=2)+'\n')
def ident(p):
    z=p.read_bytes();return {'sha256':sha256(z).hexdigest(),'bytes':len(z)}
provenance={'task':'REI-PHYS26-20261011','role':'display only, no new scientific validation',
 'generator':ident(Path(__file__)),'source':{'path':str(SOURCE.relative_to(ROOT)),**ident(SOURCE)},
 'base_variance_grid_points':81,'additional_points':'reuse the 7 preregistered case variances, remove duplicates',
 'actual_variance_points':len(ws),'display_kernel_unique_energies':len(cache),'decimal_precision':80,
 'formula_lineage':'Explicit display-only adaptation of the read PHYS26 scalar log-fit formula for k; degree-3 jet and scalar science mains are not invoked.',
 'new_science_main_invocations':0,'old_science_main_invocations':0,'new_root_searches':0,
 'derivative_sign_campaigns':0,'independent_physics_credit':0,
 'plot':ident(output),'data':ident(plotdata),'boundary_digits':'inherited PHYS25 decimals, no new root refinement',
 'classification':'Sampled rendering of exact proved envelope formulas, not a continuum proof or interval certificate.'}
(HERE/'DISPLAY_PROVENANCE.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(provenance,ensure_ascii=False))
