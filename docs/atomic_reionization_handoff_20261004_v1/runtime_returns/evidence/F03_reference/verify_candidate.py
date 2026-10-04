import subprocess,json,math
from pathlib import Path
root=Path.cwd();cargo='/home/cosmosapjw/.cargo/bin/cargo';manifest='rust/rei_microphysics/Cargo.toml'
subprocess.run([cargo,'test','--manifest-path',manifest,'--locked'],check=True)
ref=json.loads((root/'.cuh/fastest-track/REI-F03/reference.json').read_text());results=[]
for dt in ['1e9','5e8','2.5e8']:
 p=subprocess.run([cargo,'run','--quiet','--manifest-path',manifest,'--example','hhe_fixture','--',dt],check=True,capture_output=True,text=True)
 x=json.loads(p.stdout);assert x['dt_s']==float(dt) and x['t_end_s']==1e12
 assert x['fixture_id']=='REI_SYNTHETIC_HHE_3GROUP_STATIC_V1' and x['coordinates']==['x_HII','x_HeII','x_HeIII','u_th_proper_erg_cm3','N0_proper_cm3','N1_proper_cm3','N2_proper_cm3']
 assert x['source_site']=='backward_euler_endpoint' and x['scientific_admission']=='HOLD'
 assert x['accepted_steps']>=1000 and x['max_local_error']<2e-4 and x['rejected_candidate_writes']==0
 assert abs(x['relative_energy_residual'])<1e-12 and x['scaled_event_residual']<1e-12
 assert all(math.isfinite(v) and v>=0 for v in x['photons_cm3'])
 e=max(abs(a-b) for a,b in zip(x['observables'],ref['methods']['DOP853']['observables']));assert e<2e-4
 x['independent_observable_error']=e;results.append(x)
assert results[0]['independent_observable_error']>results[1]['independent_observable_error']>results[2]['independent_observable_error']
(root/'.cuh/fastest-track/REI-F03/fixture-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'status':'PASS','levels':results,'claim':'finite controlled fixture only'},indent=2))
