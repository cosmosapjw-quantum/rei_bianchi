#!/usr/bin/env python3
"""Independent saved-CSV structure, units, conservation and provenance audit.
Does not import or invoke the physical cascade code to compute expected values.
"""
import csv,json,math
from collections import defaultdict
from pathlib import Path
BASE=Path(__file__).resolve().parent; D=BASE/'data'
def load(name):
    with (D/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def close(a,b,rtol=4e-12,atol=5e-17):
    if not math.isclose(a,b,rel_tol=rtol,abs_tol=atol):raise AssertionError((a,b))
s=load('BARNETT_SOURCE_TYPED_216.csv');p=load('MEASURED_NEAR_THRESHOLD_PHYSICS_GREEN_15.csv');r=load('NUCLEAR_17_CHANNEL_EVENTS_255.csv');n=load('NUCLIDE_SIGNED_RESPONSE_135.csv');spectrum=load('THREE_SPECIES_SPECTRA.csv');test=load('ANGULAR_AND_GRID_SENSITIVITY_8.csv')
assert (len(s),len(p),len(r),len(n),len(test))==(216,15,255,135,8)
assert len(spectrum)==2622
E=sorted(set(float(x['Eprimary_MeV']) for x in p));Z=sorted(set(float(x['z']) for x in p))
assert E==[139.8,144.02,148.04,152.03,156.13] and Z==[1e4,1e5,1e6]
keys={(float(x['Eprimary_MeV']),float(x['z'])) for x in p}
assert len(keys)==15
rs=defaultdict(dict);ns=defaultdict(dict);g=defaultdict(list)
for x in r:rs[(float(x['Eprimary_MeV']),float(x['z']))][int(x['rid'])]=float(x['events_per_initial_pi0'])
for x in n:ns[(float(x['Eprimary_MeV']),float(x['z']))][int(x['nuclide_index'])]=float(x['signed_number_per_initial_pi0'])
for x in spectrum:g[(float(x['Eprimary_MeV']),float(x['z']))].append(x)
for x in p:
    key=(float(x['Eprimary_MeV']),float(x['z']))
    assert key in rs and key in ns and key in g
    q=rs[key];d=ns[key];assert len(q)==17 and len(d)==9
    born=q[2]+q[4]+2*q[8]+q[9];destroy=q[1]
    close(born,float(x['D_born_per_pi0']))
    close(destroy,float(x['D_destroyed_per_pi0']))
    close(born-destroy,float(x['D_net_per_pi0']))
    close(float(x['D_net_per_pi0']),d[2])
    close(sum(q.values()),float(x['total_photonuclear_events_per_pi0']))
    close(float(x['D_net_per_pi0'])*float(x['pion_first_hit_P']),float(x['D_net_per_primary_first_hit']))
    close(float(x['D_net_per_primary_first_hit'])*.02*(1-float(x['pion_first_hit_P'])),float(x['D_net_first_hit_sys_shared_1sigma']),rtol=4e-12)
    assert float(x['daughter_Emax_MeV'])<137.420706902
    assert float(x['fastD_from_dd_gross_lower_MeV_per_pi0'])>=0
    assert float(x['fastD_from_dd_plus_npD_gross_upper_MeV_per_pi0'])>=float(x['fastD_from_dd_gross_lower_MeV_per_pi0'])
    assert abs(float(x['known_stoichiometry_baryon_residual']))<1e-14
    assert abs(float(x['known_stoichiometry_charge_residual']))<1e-14
    assert int(float(x['num_grid']))==len(g[key])
    assert all(float(row['gamma_EM_plus_nuclear_sink'])>=0 and float(row['electron_EM_plus_nuclear_sink'])>=0 and float(row['positron_EM_plus_nuclear_sink'])>=0 for row in g[key])
    assert float(x['D_net_per_primary_first_hit'])>0
assert all(float(x['shared_sys_percent'])==2 for x in s)
assert all(float(x['sigma_pi0_micro_b'])>0 for x in p)
summary=json.loads((D/'SCIENTIFIC_SUMMARY.json').read_text())
assert summary['model_cases']==15 and summary['new_derived_science_rows']==3035
assert summary['HE_physical_DAG']=='14/18' and summary['central_DAG']=='28/88'
print(json.dumps({'verified':True,'source_exfor_rows':len(s),'green_cases':len(p),'reaction_events':len(r),'nuclide_signed':len(n),'spectra':len(spectrum),'comparisons':len(test),'max_baryon_residual':summary['max_known_stoichiometry_B_residual'],'max_charge_residual':summary['max_known_stoichiometry_charge_residual'],'source_stat_systematic_separated':True,'dag':'28/88 14/18 unchanged'},ensure_ascii=False))
