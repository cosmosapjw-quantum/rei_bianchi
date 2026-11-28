"""Plots read only certified scalar outputs and previous PR109 reported bounds."""
from pathlib import Path
from fractions import Fraction as F
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
Ls=['1/700','1/200','1/100']
legacy=[(0.279238681235,0.386397436244),(0.186315404014,0.472747698143),(0.133108297140,0.573194162276)]
fig,ax=plt.subplots(figsize=(8.4,4.8))
for j,L in enumerate(Ls):
 d=json.loads((ROOT/'evidence'/f'EXTREMA_CERT_L_{L.replace("/","_")}.json').read_text())
 ll,lh,ul,uh=[float(F(d[x])) for x in ('min_b_outer_low','min_b_inner_high','max_b_inner_low','max_b_outer_high')]
 y=2-j
 ax.plot(legacy[j],[y+.16]*2,linewidth=2,alpha=.5,linestyle='--',label='PR109 sign-split outer (numerical)' if j==0 else None)
 ax.plot([ll,uh],[y-.03]*2,linewidth=3,label='New continuum outer (certified, conditional)' if j==0 else None)
 ax.plot([ll,lh],[y-.16]*2,linewidth=5,label='Certified min-extremum bracket' if j==0 else None)
 ax.plot([ul,uh],[y-.28]*2,linewidth=5,label='Certified max-extremum bracket' if j==0 else None)
ax.set_yticks([2,1,0],Ls)
ax.set_xlabel(r'$b=\langle \cos^2\theta \rangle$ (dimensionless)')
ax.set_ylabel(r'Assumed $L$ [nb/(sr degree)]')
ax.set_title('Source-conditional angular moments, E_gamma=330 MeV')
ax.grid(axis='x',alpha=.25)
ax.legend(loc='upper center', bbox_to_anchor=(.5,-.2),ncol=2,fontsize=8,frameon=False)
ax.set_xlim(.09,.62)
fig.tight_layout();p=ROOT/'figures'/'certified_extrema.png';fig.savefig(p,dpi=185,bbox_inches='tight');print(p)

fig,ax=plt.subplots(figsize=(7.8,4.6))
from fractions import Fraction as F
x=[];y=[]
for subdiv in (3,5,10,50):
 from sys import path
 path.insert(0,str(ROOT/'src'))
 from lipschitz_lp_certificate import make_grid,errors
 g=make_grid('1/700',subdiv)
 x.append(float(g.h));y.append(float(errors(g)['total']/g.Dmin))
ax.plot(x,y,marker='o',linewidth=1.7)
ax.set_xscale('log');ax.set_yscale('log')
ax.set_xlabel('Grid spacing h [degree]')
ax.set_ylabel('Proved generic ratio-error budget (dimensionless)')
ax.set_title('Analytic continuum and quadrature budget, L=1/700')
ax.grid(True,which='both',alpha=.2)
fig.tight_layout();p=ROOT/'figures'/'continuum_budget.png';fig.savefig(p,dpi=185);print(p)
