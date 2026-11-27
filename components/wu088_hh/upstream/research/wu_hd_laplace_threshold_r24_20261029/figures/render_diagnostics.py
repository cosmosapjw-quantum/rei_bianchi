"""Source-only conditional diagnostics and SYNTHETIC positivity witness."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
R=Path(__file__).resolve().parents[1]
r=json.loads((R/'results/CONDITIONAL_THRESHOLD_BOUND.json').read_text())
w=json.loads((R/'results/POSITIVE_NONUNIQUENESS_WITNESS.json').read_text())

upper=[float(v) for v in r['adjacent_theta_upper_meV']]
labels=[f'{r["input_T_K"][j]}–{r["input_T_K"][j+1]}' for j in range(9)]
fig,ax=plt.subplots(figsize=(9.3,5.4),layout='constrained')
ax.plot(range(1,10),upper,'o-',label='Necessary adjacent-pair upper bound')
ax.axhline(float(r['spectroscopic_candidate_theta_meV']),linewidth=1.5,linestyle='--',label='External spectroscopic threshold candidate (not GL2022 PES)')
ax.scatter([1],[float(r['theta_nearest_display_rounding_upper_meV'])],marker='s',zorder=8,label='15–55 K, printed mantissa rounding only')
ax.set_xticks(range(1,10),labels,rotation=35,ha='right')
ax.set_ylabel('Threshold energy upper bound [meV]')
ax.set_xlabel('Original GL2022 Table 2 adjacent temperature pair [K]')
ax.set_ylim(0,250)
ax.set_title('Conditional Laplace support bounds, exactly ten native GL2022 temperatures')
ax.legend(loc='upper left',fontsize=9)
fig.savefig(R/'figures/ALL_PAIRS_SOURCE_BOUNDS.png',dpi=180)
plt.close(fig)

fig,ax=plt.subplots(figsize=(8.2,4.6),layout='constrained')
ax.plot([1,2],[float(r['theta_nominal_upper_meV']),float(r['theta_nearest_display_rounding_upper_meV'])],marker='o',linestyle='none',markersize=8)
ax.axhline(float(r['spectroscopic_candidate_theta_meV']),linestyle='--',label='External spectroscopy only (R23)')
ax.set_xlim(0.4,2.6)
ax.set_xticks([1,2],['Source nominal','Printed-mantissa envelope'])
ax.set_ylim(14,23)
ax.set_ylabel('Threshold energy [meV]')
ax.annotate('15.18630 meV', (1,float(r['theta_nominal_upper_meV'])),xytext=(-35,18),textcoords='offset points',ha='center',fontsize=9)
ax.annotate('15.19157 meV', (2,float(r['theta_nearest_display_rounding_upper_meV'])),xytext=(30,-20),textcoords='offset points',ha='center',fontsize=9)
ax.set_title('Conditional 15–55 K support bound versus external spectroscopy')
ax.legend(loc='upper left',fontsize=10)
fig.savefig(R/'figures/LOW_T_CONDITIONAL_GAP.png',dpi=180)
plt.close(fig)

fig,ax=plt.subplots(figsize=(9.0,4.5),layout='constrained')
energies=[float(v) for v in w['baseline_support_meV']]
w0=[1.0]*len(energies)
w1=[float(x) for x in w['alternative_weights']]
ax.vlines(energies,[1e-9]*len(energies),w0,linewidth=2,label='Baseline positive discrete measure (onset 20 meV)')
ax.scatter(energies,w0,marker='o',zorder=3)
ax.vlines([x+0.45 for x in energies],[1e-9]*len(energies),w1,linestyles='--',linewidth=2,label='Different positive measure (onset 12 meV)')
ax.scatter([x+0.45 for x in energies],w1,marker='s',zorder=3)
ax.scatter([12],[float(w['added_12meV_weight'])],marker='^',s=65,zorder=5,label='Additional low-energy weight (small but positive)')
ax.set_yscale('log');ax.set_ylim(3e-7,3);ax.set_xlim(9,51)
ax.set_xlabel('Support energy [meV]')
ax.set_ylabel('Energy-weighted spectral measure (arbitrary normalized units)')
ax.set_title('Synthetic positivity counterexample: identical ten Laplace samples, different supports')
ax.legend(loc='center left',bbox_to_anchor=(1.01,0.5),fontsize=8)
fig.savefig(R/'figures/POSITIVE_NONIDENTIFIABILITY_WITNESS.png',dpi=180)
plt.close(fig)
