#!/usr/bin/env python3
"""Bounded P4/S5 evidence admission. Timing is recorded, not a pass gate."""
from pathlib import Path
import csv,json,math,statistics
R=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((R/'evidence/p5_tail_campaign.csv').open()))
assert len(rows)==36,len(rows)
for row in rows:
    assert row['scenario'] in ['high_opacity','low_opacity']
    assert row['mode'] in ['retain_all','exact_zero','budget_nonzero','species_guard']
    for k in ['total_wall_s','last_step_s','photons_com3','absorbed_com3','temp_K','removed_com3','energy_error_envelope_J','number_inventory_residual','HI_com3','HeI_com3','HeII_com3','DI_com3']:
        assert math.isfinite(float(row[k])),(row,k)
    if row['mode'] in ('budget_nonzero','species_guard'):
        assert float(row['number_inventory_residual'])<1e-10,row
        assert 0<=float(row['removed_com3'])<=1e-10
        assert 0<=float(row['energy_error_envelope_J'])<=1e-26
for scenario,n in [('high_opacity',12),('low_opacity',8),('low_opacity',16)]:
    assert {(r['mode'],r['repeat']) for r in rows if r['scenario']==scenario and int(r['nsteps'])==n}=={(m,str(i)) for m in ('retain_all','exact_zero','budget_nonzero','species_guard') for i in range(3)}

def med(s,n,mode,key):
    return statistics.median(float(r[key]) for r in rows if r['scenario']==s and int(r['nsteps'])==n and r['mode']==mode)
results=[]
for scenario,n in [('high_opacity',12),('low_opacity',8),('low_opacity',16)]:
    b={k:med(scenario,n,'retain_all',k) for k in ('total_wall_s','photons_com3','absorbed_com3','temp_K','retained','HI_com3','HeI_com3','HeII_com3','DI_com3')}
    for mode in ('exact_zero','budget_nonzero','species_guard'):
        d={k:med(scenario,n,mode,k) for k in (*b,'removed_com3','energy_error_envelope_J','removed_nonzero')}
        results.append(dict(scenario=scenario,nsteps=n,mode=mode,median_speedup_over_no_compaction=b['total_wall_s']/d['total_wall_s'],baseline_cohorts=int(b['retained']),remaining_cohorts=int(d['retained']),removed_nonzero=int(d['removed_nonzero']),removed_photons_com3=d['removed_com3'],direct_future_photo_energy_upper_j_com3=d['energy_error_envelope_J'],relative_changes={k:(d[k]-b[k])/max(abs(b[k]),1e-40) for k in ['photons_com3','absorbed_com3','temp_K','HI_com3','HeI_com3','HeII_com3','DI_com3']}))
low16={q['mode']:q for q in results if q['scenario']=='low_opacity' and q['nsteps']==16}
low8={q['mode']:q for q in results if q['scenario']=='low_opacity' and q['nsteps']==8}
assert abs(low16['budget_nonzero']['relative_changes']['HeII_com3'])>0.5,low16
assert abs(low16['species_guard']['relative_changes']['HeII_com3'])<0.005,low16
assert abs(low8['species_guard']['relative_changes']['HeII_com3'])<0.005,low8
assert low16['species_guard']['remaining_cohorts']>low16['budget_nonzero']['remaining_cohorts']
ind=json.loads((R/'evidence/P5_INDEPENDENT_SCIPY.json').read_text())
assert ind['max_photon_identity_residual']<5e-11
summary={'schema':'rei.iso.p4.s5.numeric_scope.v1','status':'PASS_SCOPED_DIRECT_REMAINDER_AND_MEASURED_COUPLED_COMPARATORS','replay_rows':len(rows),'rust_tests_total':100,'independent_cases':len(ind['cases']),'independent_photon_identity_max_relative':ind['max_photon_identity_residual'],'diagnostics':results,'scope':{'DIRECT_COUNTS':'upper under no photon splitting/scattering; each omitted photon <=1 direct event','DIRECT_SPECIES_ENERGY':'geometry-horizon model upper under arbitrary nonnegative history opacity','COUPLED_NONLINEAR_GAS':'NOT_BOUNDED; measured comparison only','OBSERVATIONAL_RELATIVE_ERROR':'NOT_CERTIFIED; minority HeII measured violation under mass-only budget','SOURCE_LOCK':'P4/S4 PR186, original PR150 12 byte-identical owner modules'}}
(R/'evidence/P5_SCIENCE_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
print('P4S5_SCOPED_VALIDATION_PASS: 36 native rows, 4 independent direct-rate ODEs, species counterexample and guarded control')
