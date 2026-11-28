"""Source-typed R23 diagnostics, not observations or thermochemistry uncertainty."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/R23_MOLECULAR_CYCLE.json').read_text())
q23=float(r['Q_spectroscopy_candidate_meV'])
q22=-20.9500211513003896007
names=['2021 neutral PES','2019+2021 mixed-A','2021+2019 mixed-B','R22 spectroscopy','R23 ionization cycle']
vals=[-17.4288329,-21.0771863,-21.1288329,q22,q23]
fig,ax=plt.subplots(figsize=(10.8,4.9),constrained_layout=True)
for i,(name,val) in enumerate(zip(names,vals)):
    ax.scatter([val],[4-i],s=75,marker=['o','s','s','D','D'][i],label=name)
    ax.annotate(f'{val:.9f} meV',xy=(val,4-i),xytext=(8,6),textcoords='offset points',fontsize=9)
ax.set_yticks(range(5),names[::-1]);ax.set_xlabel('Candidate Q (meV / event): negative = endothermic')
ax.set_title('Disjoint source conventions — not an uncertainty interval')
ax.set_xlim(-22.0,-16.5);ax.grid(axis='x',alpha=0.2)
fig.savefig(ROOT/'figures/R23_SOURCE_TYPED_Q_COMPARISON.png',dpi=180)
plt.close(fig)
# Exactly compensated thermochemical source dependency: atomic IP terms cancel.
from numpy import linspace
x=linspace(-25,25,201)
fig,ax=plt.subplots(figsize=(9.5,4.7),constrained_layout=True)
ax.plot(x,x,label='Inconsistent: perturb atomic D ionization alone')
ax.plot(x,0*x,label='Consistent: recompute HD D0 from the same source cycle',linewidth=2)
ax.set_xlabel('Synthetic perturbation to the atomic D ionization input (cm$^{-1}$)')
ax.set_ylabel('Change in calculated threshold (cm$^{-1}$)')
ax.set_title('Thermochemical source-dependency adversarial control (synthetic only)')
ax.grid(alpha=0.2);ax.legend(loc='upper left')
fig.savefig(ROOT/'figures/R23_ATOMIC_REFERENCE_CANCELLATION.png',dpi=180)
plt.close(fig)
# Literal source-cycle residual in kHz (uses exact c conversion).
delta=Decimal(r['inter_cycle_residual_cm1'])
kHz=delta*Decimal('29979245800')/Decimal('1000')
print(json.dumps({'figures':['figures/R23_SOURCE_TYPED_Q_COMPARISON.png','figures/R23_ATOMIC_REFERENCE_CANCELLATION.png'],
                  'inter_cycle_residual_kHz':str(kHz),'data_basis':'R22 source literals, R23 ionization source literals, synthetic gauge perturbation',
                  'scientific_admission':'CANDIDATE_ONLY_NO_PES_NATIVE'},indent=2))
