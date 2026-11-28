"""Finite checks for the attached derivation; no old scientific gate promotion."""
import json,math,pathlib,sys
from portable_reference import rate,source,particle_temperature_source,NU
checks=[]
def record(name,truth):
    checks.append({'name':name,'passed':bool(truth)})
    if not truth:raise AssertionError(name)
for name,v in NU.items():
    record(name+'_nuclei',sum(a*b for a,b in zip((1,1,1,0),v))==0)
    record(name+'_charge',sum(a*b for a,b in zip((0,1,-1,-1),v))==0)
record('ion_pair_no_free_e',NU['ion_pair'][3]==0)
record('k57_cutoff_is_explicit',rate(3000,'LCS91',(1,1e6))['k']==1e-20 and rate(3000,'LCS91',(1,1e6))['dk_dT'] is None)
record('k57_right_branch_positive',rate(3000.01,'LCS91',(1,1e6))['k']>0)
for bad in [0,-1,float('nan'),float('inf'),1e7]:
    try:rate(bad,'LCS91',(1,1e6));passed=False
    except ValueError:passed=True
    record('invalid_domain_'+str(bad),passed)
for name in ('LCS91','KS92_corrected_Glover15'):
    for T in (4000.,1e4,1e5):
        h=T*1e-5; r=rate(T,name,(3001,1e6));m=rate(T-h,name,(3001,1e6));p=rate(T+h,name,(3001,1e6))
        d=(p['k']-m['k'])/(2*h); d2=(p['dk_dT']-m['dk_dT'])/(2*h)
        record(name+'_d1_'+str(T),abs(d/r['dk_dT']-1)<3e-8)
        record(name+'_d2_'+str(T),abs(d2/r['d2k_dT2']-1)<1e-7)
S=source(2.,3.,4.)
record('no_extra_identical_pair_half',S['R']==12.)
record('thermal_plus_binding_conservation',S['du_th']+S['du_binding']==0)
record('temperature_particle_correction',particle_temperature_source(5.,6.,S,4.,7.)==2*(-48)/(3*7*5)-6*12/5)
record('zero_density_source',source(0.,3.,4.)['R']==0)
rows=[dict(T_K=T,LCS=rate(T,'LCS91',(3001,1e6))['k'],KS=rate(T,'KS92_corrected_Glover15',(3001,1e6))['k']) for T in (1e4,2e4,1e5)]
result={'status':'BOUNDED_REFERENCE_CHECKS_PASSED','checks':checks,'check_count':len(checks),'example_rates_cm3_s':rows,'cosmological_histories':0,'atomic_integrations':0,'grackle_builds':0,'production_admission':False,'scientific_claim_ceiling':'algebra, finite analytic-branch checks and source semantics only; physical model uncertainty and consumer interval proofs unresolved'}
if len(sys.argv)>1:pathlib.Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks)}))
