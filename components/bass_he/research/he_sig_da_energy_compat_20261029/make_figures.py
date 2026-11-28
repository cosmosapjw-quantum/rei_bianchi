"""Render conditional mathematics, never measured sigma(330) or physical rate."""
from pathlib import Path
import sys
from fractions import Fraction as F
from decimal import Decimal
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'evidence')]
from sig_da_bridge import *
from independent_angular import I_lower

rows=source_rows(ROOT/'source/M0475.x4')
K=min_energy_L(rows)
L=np.linspace(float(F(1,700)),.010,100)
K1=[];K2=[]
# Compute upper envelope independently via the parent source frozen bounds only for L-grid?
# The Kcrit at these L is controlled by the angular LOWER vs source upper, but
# compute the upper angular endpoint from exact piecewise min of upper cones.
import mpmath as mp
points=[(F(46),F('.17')),(F(61),F('.21')),(F(73),F('.12')),(F(87),F('.24'))]

def upper_I(L):
    L=F(str(L))
    knots=sorted({F(0),F(90)}|{t for t,_ in points})
    pieces=[]
    for a,b in zip(knots,knots[1:]):
        m=(a+b)/2
        lines=[]
        for t,v in points:
            sign=1 if m>=t else -1
            lines.append((v-L*sign*t,L*sign))
        cuts={a,b}
        for i,(c,d) in enumerate(lines):
            for e,f in lines[i+1:]:
                if d!=f:
                    x=(e-c)/(d-f)
                    if a<x<b:cuts.add(x)
        xx=sorted(cuts)
        for x,y in zip(xx,xx[1:]):
            c,d=min(lines,key=lambda t:t[0]+t[1]*(x+y)/2)
            pieces.append((x,y,c,d))
    with mp.workdps(45):
        k=mp.pi/180
        def mpr(z):return mp.mpf(z.numerator)/z.denominator
        def antideriv(x,a,b):
            x,a,b=map(mpr,(x,a,b))
            return -(a+b*x)*mp.cos(k*x)/k+b*mp.sin(k*x)/k**2
        return mp.fsum(4*mp.pi*k*(antideriv(y,a,b)-antideriv(x,a,b)) for x,y,a,b in pieces)

for l in L:
    Il=I_lower(str(l),50)
    Iu=upper_I(l)
    K1.append(float(critical_energy_L(rows,mp.nstr(Il,43),mp.nstr(Iu,43),1,60)))
    K2.append(float(critical_energy_L(rows,mp.nstr(Il,43),mp.nstr(Iu,43),2,60)))

fig,ax=plt.subplots(figsize=(7.8,4.5))
ax.plot(L,K1,label='Hypothesis kappa=1')
ax.plot(L,K2,label='Hypothesis kappa=2')
ax.axhline(float(K),linestyle='--',linewidth=1.3,label='SIG-only minimum K = 0.02375')
ax.axvline(0.005,linestyle=':',linewidth=1.2,label='L_theta = 0.005')
ax.set(xlabel='Assumed angular Lipschitz L_theta (nb/sr/degree)',
       ylabel='Minimum compatible energy K (nb/MeV)',
       title='EXFOR M0475: conditional DA/SIG compatibility frontier')
ax.grid(alpha=.25);ax.legend(fontsize=8,loc='upper right')
fig.tight_layout();fig.savefig(ROOT/'results/Kcrit_vs_Ltheta.png',dpi=190);plt.close(fig)

import json
angles=json.loads((ROOT/'evidence/PR105_ANGULAR_BOUNDS.json').read_text())['1/200']
fig,ax=plt.subplots(figsize=(7.8,3.7))
for y,kappa in [(1,1),(0,2)]:
    result=joint_interval(rows,K,angles['lo'],angles['hi'],kappa)
    a=float(result['sigma330_lower_nb']);b=float(result['sigma330_upper_nb'])
    ax.plot([a,b],[y,y],linewidth=4,label=f'kappa={kappa} conditional')
    ax.plot([a,b],[y,y],'o',markersize=6)
ax.set(yticks=[0,1],yticklabels=['kappa=2','kappa=1'],xlabel='Conditional sigma(330 MeV) (nb)',
       title='Support intersection at K=0.02375, L_theta=0.005')
ax.set_xlim(.4,1.10);ax.set_ylim(-.65,1.65)
ax.grid(axis='x',alpha=.3)
fig.tight_layout();fig.savefig(ROOT/'results/joint_support_kappa.png',dpi=190);plt.close(fig)

# Resolve the sub-millinanobarn width that collapses visually in the full-scale plot.
r1=joint_interval(rows,K,angles['lo'],angles['hi'],1)
low=float(r1['sigma330_lower_nb']);high=float(r1['sigma330_upper_nb'])
fig,ax=plt.subplots(figsize=(7.8,3.6))
ax.plot([low,high],[0,0],linewidth=5)
ax.plot([low,high],[0,0],'o',markersize=7)
ax.set(xlabel='Conditional sigma(330 MeV) (nb)',
       title='Magnified kappa=1 interval (hypothesis only)')
ax.set_xlim(low-0.00015,high+0.00015);ax.set_ylim(-0.2,0.2)
ax.set_yticks([]);ax.grid(axis='x',alpha=.3)
fig.tight_layout();fig.savefig(ROOT/'results/kappa1_zoom.png',dpi=190);plt.close(fig)
