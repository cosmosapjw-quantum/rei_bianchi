"""Create a comparison-only plot; no physical-source rate/heat claim."""
import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results/SPECTROSCOPY_RESULT.json').read_text())
components=data['components_cm1']
labels=['Atomic isotope IP (D-H)','Molecular D0 (HD-H2)','Rotation (H2 J1 - HD J2)','Total product-minus-reactant']
values=[float(components['isotopic_atomic_ionization_cm1']),float(components['molecular_ground_dissociation_cm1']),float(components['state_rotational_correction_cm1']),float(data['delta_E_products_minus_reactants_cm1'])]
fig,ax=plt.subplots(figsize=(9.2,4.9),layout='constrained')
bars=ax.barh(labels,values,edgecolor='black',linewidth=.8)
bars[-1].set_hatch('///')
ax.axvline(0,color='black',lw=.9)
for b,v in zip(bars,values):
    ax.annotate(f'{v:+.3f}',(v if v>=0 else 0,b.get_y()+b.get_height()/2),xytext=(5,0),textcoords='offset points',ha='left',va='center',fontsize=10)
ax.invert_yaxis()
ax.set_xlim(-190,350)
ax.set_xlabel('Energy contribution to ΔE = E(products) − E(reactants)   [cm⁻¹]')
ax.set_title('H⁺ + HD(v=0,J=2) → D⁺ + H₂(v=0,J=1): spectroscopy-side decomposition')
fig.text(.5,-.018,'Comparison candidate only; GL2022 PES threshold, source-bound Q and bath heat remain UNAUTHENTICATED.',ha='center',fontsize=9)
fig.savefig(ROOT/'figures'/'R22_STATE_ENERGY_COMPONENTS.png',dpi=180,bbox_inches='tight',pad_inches=.12)
plt.close(fig)
