"""Saved-output visualization only. Does not rerun R15 scientific calculations."""
from pathlib import Path
import sys
from fractions import Fraction as Q
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from r16_nonnegative_cubic import positive_partition,evaluate
root=Path(__file__).resolve().parents[1]
b=[Q(1,9),Q(-1,9),Q(0),Q(4,9)]
p=positive_partition(b)
fig,ax=plt.subplots(figsize=(7.8,4.3))
X=[i/600 for i in range(601)]
Y=[float(evaluate(b,Q(i,600))) for i in range(601)]
ax.plot(X,Y,label=r'$p(t)=(t-1/3)^2$ (exact source)')
ax.plot([0,1/3,2/3,1],[float(z) for z in b],linestyle=':',marker='o',label='Original Bernstein B3 control values')
for a,c,row in p['leaves']:
    xx=[float(a+(c-a)*Q(i,3)) for i in range(4)]
    yy=[float(z) for z in row]
    ax.plot(xx,yy,marker='.',linestyle='--',alpha=0.7,label='Refined nonnegative controls' if a==0 else None)
ax.axhline(0,linewidth=0.8,alpha=0.5)
ax.axvline(1/3,linewidth=0.8,alpha=0.6,label='Exact rational double root')
ax.set(xlabel='Source-cell coordinate t',ylabel='Value / Bernstein coefficient (arbitrary units)',title='R16: source nonnegativity vs signed B3 coefficients')
ax.text(0.02,0.02,'Control points are coefficients, not samples on the source curve.',transform=ax.transAxes,fontsize=9)
ax.legend(loc='upper center',fontsize=8,ncol=2)
fig.tight_layout();fig.savefig(root/'figures/R16_B3_SIGNED_PREPROCESSING.png',dpi=180);fig.savefig(root/'figures/R16_B3_SIGNED_PREPROCESSING.svg');plt.close(fig)
print('PLOT_CREATED',[(p.name,p.stat().st_size) for p in (root/'figures').iterdir()])
