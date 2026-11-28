#!/usr/bin/env python3
"""Source-exact post-analysis of frozen R37 first-exit probabilities (no interpolation)."""
from pathlib import Path
import csv, json, hashlib, statistics, argparse

argp=argparse.ArgumentParser(description='Recompute source-exact R37 first-exit dominance')
argp.add_argument('--source', type=Path, help='Path to frozen R37_CHEM_VS_EXIT_1920.csv')
argp.add_argument('--out', type=Path, help='Output folder (default beside script)')
args=argp.parse_args()
here=Path(__file__).resolve().parent
candidates=[here/'R37_CLEAN'/'results'/'R37_CHEM_VS_EXIT_1920.csv',
            here.parent/'R37_CLEAN'/'results'/'R37_CHEM_VS_EXIT_1920.csv',
            Path.cwd()/'results'/'R37_CHEM_VS_EXIT_1920.csv']
SOURCE=args.source or next((p for p in candidates if p.is_file()),candidates[0])
OUT=args.out or (here if here.name=='fresh_physics' else here/'fresh_physics')
EXPECTED='83f4678316df964faf32d2dcf8a168261059deced1669414fd54bb3e2f1650cd'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED, 'R37 source provenance changed'
OUT.mkdir(parents=True,exist_ok=True)
with SOURCE.open(newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==1920
zs=['OFF','0','10','30','100','300']
policies=['eq6_7_spin_weighted','unweighted_source_counterfactual']
summary=[]
for p in policies:
    for z in zs:
        cases=[r for r in rows if r['spin_policy']==p and r['z_boundary']==z]
        assert len(cases)==160
        pchem=[float(r['P_H2_before_first_exit']) for r in cases]
        prad=[float(r['P_radiative_exit_first']) for r in cases]
        dom=sum(b>a for a,b in zip(pchem,prad))
        summary.append({'spin_policy':p,'z_boundary':z,'n_cases':len(cases),
                        'radiation_exit_dominates_chemistry_count':dom,
                        'radiation_exit_dominates_fraction':dom/len(cases),
                        'median_P_chem_first':statistics.median(pchem),
                        'min_P_chem_first':min(pchem),'max_P_chem_first':max(pchem)})
with (OUT/'R37_RADIATIVE_DOMINANCE_BY_BOUNDARY_12.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)

# 105 K, density 1000 cm^-3, spin-weighted, initial J=2: actual points only.
selected=[r for r in rows if int(r['Tgas_K'])==105 and float(r['n_Hplus_cm_minus3'])==1000 and r['spin_policy']==policies[0] and int(r['initial_v0_J'])==2]
selected=sorted(selected,key=lambda r: zs.index(r['z_boundary']))
assert len(selected)==6
with (OUT/'R37_REFERENCE_105K_J2_SOURCE_6.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['z_boundary','T_rad_K','P_H2_before_first_exit','P_collision_exit_first','P_radiative_exit_first']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in selected)

# Native Matplotlib figures use default colors, no model interpolation.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
x=range(len(zs))
fig,ax=plt.subplots(figsize=(8.5,4.8))
for p in policies:
    s=[v for v in summary if v['spin_policy']==p]
    lab='GL2022 Eq. (6)-(7) spin weighted' if p==policies[0] else 'Unweighted source counterfactual'
    ax.plot(list(x),[v['radiation_exit_dominates_fraction'] for v in s],marker='o',label=lab)
ax.set_xticks(list(x), zs);ax.set_xlabel('Prescribed CMB boundary z (OFF: no external radiation)')
ax.set_ylabel('Fraction of grid cases with P(rad first) > P(chem first)')
ax.set_ylim(-0.03,1.02);ax.legend(fontsize=8);ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(OUT/'R37_DOMINANCE_FRACTION.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(8.5,4.8))
for key,label in [('P_H2_before_first_exit','Chemical first'),('P_collision_exit_first','Collision exit first'),('P_radiative_exit_first','Radiative exit first')]:
    ax.plot(list(x),[float(r[key]) for r in selected],marker='o',label=label)
ax.set_xticks(list(x),zs);ax.set_xlabel('Prescribed radiation boundary z')
ax.set_ylabel('First-termination probability (conditioned)')
ax.set_title('HD(v=0,J=2), Tgas=105 K, n(H+)=1e3 cm^-3, Eq.(6)-(7)')
ax.set_ylim(-0.03,1.02);ax.legend();ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(OUT/'R37_REFERENCE_105K_J2.png',dpi=180);plt.close(fig)

meta={'schema':'WU_R37_FRESH_POST_ANALYSIS_20261030','frozen_source_sha256':EXPECTED,
      'canonical_DAG':'34/49_UNCHANGED', 'R37_auxiliary':'1/1_SCOPED',
      'spin_policy_comparisons':summary,
      'assumptions':['original 1920 source data only','no interpolation','first exit from v0 J<=4 source graph, not eventual molecule destruction','z is externally prescribed radiation temperature boundary'],
      'validation':{'rows':len(rows),'policy_and_z_categories':len(summary),'each_cell_n':160,'example_n':len(selected)}}
(OUT/'R37_DOMINANCE_SUMMARY.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
for p in sorted(OUT.iterdir()):print(p.name,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())
print('DOMINANCE_COUNTS',[(a['spin_policy'],a['z_boundary'],a['radiation_exit_dominates_chemistry_count']) for a in summary])
