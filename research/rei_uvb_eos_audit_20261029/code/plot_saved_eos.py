#!/usr/bin/env python3
"""Presentation-only: read frozen numerical audit JSON, never call GLS or source rates."""
import json
from pathlib import Path
from decimal import Decimal as D
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results/EOS_EXACT_RATIONAL.json').read_text())
b=float(D(data['coefficients_theta0']['kappa']))
s=float(D(data['coefficient_direction_per_theta']['kappa']))
q0=float(D(data['chi2_polynomial']['constant']))
q1=float(D(data['chi2_polynomial']['linear']))
q2=float(D(data['chi2_polynomial']['quadratic']))
ths=[-1+i/100 for i in range(201)]
assert abs((1.4+0.2*ths[0])-1.2)<1e-12
assert abs((1.4+0.2*ths[100])-1.4)<1e-12
assert abs((1.4+0.2*ths[-1])-1.6)<1e-12
vals_k=[b+t*s for t in ths]
vals_q=[q0+t*q1+t*t*q2 for t in ths]
for kind,y,label,filename in [
    ('kappa', vals_k, r'Fitted $\kappa$ (dex / unit redshift)', 'EOS_KAPPA_SENSITIVITY'),
    ('chisq', vals_q, r'Conditional residual $\chi^2$ (5 nominal dof)', 'EOS_CHI2_SENSITIVITY')]:
    fig,ax=plt.subplots(figsize=(8,4.6))
    ax.plot([1.4+0.2*t for t in ths],y,linewidth=2.1)
    ax.scatter([1.4],[b if kind=='kappa' else q0],zorder=5,label=r'Frozen selected $\theta=0$')
    ax.set_xlabel(r'IGM temperature-density index $\gamma_{\rm TDR}=1.4+0.2\theta$')
    ax.set_ylabel(label)
    ax.grid(alpha=.25)
    ax.legend(loc='best')
    ax.set_xlim(1.2,1.6)
    ax.set_title(('One-nuisance response of redshift slope' if kind=='kappa' else 'One-nuisance response of residual fit'))
    fig.text(.5,.02,'BB13 seven-point statistical C; Puchwein2019 fixed template. EOS response only. Not physical-model certification.',
             ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.05,1,1])
    for ext in ('svg','png'):
        fig.savefig(ROOT/'figures'/f'{filename}.{ext}',dpi=170)
    plt.close(fig)
print('PLOTS_FROM_SAVED_DATA_ONLY')
