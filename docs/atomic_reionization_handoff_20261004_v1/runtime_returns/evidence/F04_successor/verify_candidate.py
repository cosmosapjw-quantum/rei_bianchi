from pathlib import Path
import subprocess,json,math
r=Path.cwd();d=r/'.cuh/fastest-track/REI-F04';cargo='/home/cosmosapjw/.cargo/bin/cargo';manifest='rust/rei_microphysics/Cargo.toml';subprocess.run([cargo,'test','--manifest-path',manifest,'--locked'],check=True);oracle=json.loads((d/'oracle.json').read_text());ref=oracle['archived_endpoint_reused'];result=[]
for h in ['1e11','5e10','2.5e10']:
 p=subprocess.run([cargo,'run','--quiet','--manifest-path',manifest,'--example','ft03_fixture','--',h],check=True,capture_output=True,text=True);x=json.loads(p.stdout)
 assert x['model_id']==oracle['model_id'] and x['t_end_s']==1e14 and x['dt_s']==float(h)
 assert x['source_site']=='backward_euler_endpoint' and x['scientific_admission']=='HOLD' and x['F04_certificate_completed']==False
 assert x['max_local_error']<2e-4 and x['rejected_candidate_writes']==0 and x['accepted_steps']>=1000
 assert x['temperature_min_K']>=30000 and x['temperature_max_K']<=110000
 assert abs(x['relative_energy_residual'])<1e-12 and x['scaled_event_residual']<1e-12
 assert all(v>=0 and math.isfinite(v) for v in x['photons_cm3']);e=max(abs(a-b) for a,b in zip(x['observables'],ref['observables']));assert e<2e-4;x['independent_observable_error']=e;result.append(x)
assert result[0]['independent_observable_error']>result[1]['independent_observable_error']>result[2]['independent_observable_error'];(d/'fixture-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','F04_final_acceptance':'NOT_COMPLETED','finite_controlled_levels':result},indent=2))
