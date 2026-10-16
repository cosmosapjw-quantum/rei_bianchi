"""Merge three actual completed case-specific bounded sandbox runs without rerunning them."""
import csv,json, math
from pathlib import Path
from statistics import median
ROOT=Path(__file__).resolve().parent
E=ROOT/'evidence'
CASES=['V10_D1_X1E5','D1_X1E4','D5_X1E5']
objects=[json.loads((E/f'C8_MATRIX_{n}.json').read_text()) for n in CASES]
rows=[row for obj in objects for row in obj['rows']]
summary=[row for obj in objects for row in obj['summary']]
assert len(rows)==144 and len(summary)==24
assert len({(r['case'],r['mode'],r['steps']) for r in rows})==144
assert all(math.isfinite(r['temperature_K']) and r['energy_ledger_abs_eV_H']<1e-11 for r in rows)
with (E/'C8_MATRIX_144.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
ident=objects[0]['grackle_literal_table']
assert all(x['grackle_literal_table']==ident for x in objects)
report={
 'schema':'rei.v11.c8.1','source':'source-free frozen PR150 native Grackle literal Python comparator; not original Rust V10 driver',
 'cases':CASES,'methods':list(objects[0]['modes']),'steps':objects[0]['step_grids'],
 'rows_count':len(rows),'grackle_original_literal_C_table':ident,
 'maximum_energy_ledger_abs_eV_per_H':max(r['energy_ledger_abs_eV_H'] for r in rows),
 'max_midpoint_residual':max(r['newton_root_max_residual'] for r in rows),
 'N128':{},'method_reference_conclusion':'CE midpoint improves T error ~97%, yet CE-only and thermal-only retain first order; coupled all-midpoint approximately second order for this nonstiff problem',
 'Native_owner_runtime_this_turn':'NOT_RUN', 'Native_runtime_prior_V10_N128_T_K':14988.7611352303,
 'caveats':['At V10 Xend 1e-5, all-mid N128->256 measured order 1.87 due small errors near numerical floor; coarser ratios near two.',
            'Absolute temperature parity at one native prior endpoint not native source code equivalence.',
            'CE clock intervention fraction is an empirical numerical error reduction under fixed test; not causal decomposition of V10 full source-on solver.',
            'H/He Case A only; no photon source, opacity, transport or full EoR.']
}
for name in CASES:
    vals={s['mode']:s for s in summary if s['case']==name}
    be=vals['owner_like_be']['N128_error_K'];ce=vals['ce_mid']['N128_error_K']
    report['N128'][name]={
        'T_Radau_K':vals['owner_like_be']['Radau_reference_K'],
        'reference_tolerance_difference_K':vals['owner_like_be']['Radau_tolerance_difference_K'],
        'be_error_K':be,'ce_mid_error_K':ce,'all_mid_error_K':vals['all_mid']['N128_error_K'],
        'CE_intervention_fraction':1-ce/be,
        'last_orders':{k:v['last_order'] for k,v in vals.items()},
        'errors_all_modes_K':{k:v['N128_error_K'] for k,v in vals.items()},
    }
report['native_N128_port_minus_native_K']=next(r['temperature_K'] for r in rows if r['case']=='V10_D1_X1E5' and r['mode']=='owner_like_be' and r['steps']==128)-report['Native_runtime_prior_V10_N128_T_K']
(E/'C8_MATRIX_144.json').write_text(json.dumps({'schema':'rei.v11.c8.matrix.1','source':'V11 independent Python full frozen native Grackle literal rate port','cases':CASES,'rows':rows,'summary':summary},ensure_ascii=False,sort_keys=True,indent=2)+'\n')
(E/'C8_SUMMARY.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
print('MERGE_PASS',len(rows),'rows',len(CASES),'cases',len(objects[0]['modes']),'clock modes x',len(objects[0]['step_grids']),'N-grid')
for k,v in report['N128'].items():
 print(k,'CE intervention',100*v['CE_intervention_fraction'],'percent, all-mid error',v['all_mid_error_K'],'K, last order',v['last_orders']['all_mid'])
print('max energy ledger',report['maximum_energy_ledger_abs_eV_per_H'])
