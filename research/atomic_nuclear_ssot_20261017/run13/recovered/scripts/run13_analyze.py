"""RUN13 same-packet m1/m2 contrasts; no continuum-error inference."""
from __future__ import annotations
import os,sys
if __name__=='__main__' and any(os.environ.get(k)!='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')):
    # Set thread controls before any Python startup hook can preload NumPy/BLAS.
    env=dict(os.environ);env.update({k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})
    os.execve(sys.executable,[sys.executable,__file__,*sys.argv[1:]],env)
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import json,hashlib,pathlib,csv
import numpy as np
from run13_endpoint_guard import load_complete,load_sealed_parent
from spectral_joint11 import SpectralModel,coalesce_reflections
from gas_integrator_parent import EV_J
R=pathlib.Path(__file__).resolve().parents[1]

def source_audit():
    packets=[json.loads((R/f'inputs/spectral11/m{m}.json').read_text()) for m in (1,2)]
    p1,p2=packets
    assert {k:v for k,v in p1.items() if k!='cohorts'}=={k:v for k,v in p2.items() if k!='cohorts'},'source metadata changed'
    arrays=[np.array(p['cohorts'],dtype='<f8') for p in packets]
    rest=[a[a[:,7]!=0] for a in arrays];assert rest[0].tobytes()==rest[1].tobytes(),'other47cells changed'
    groups=[]
    for a in arrays:
        first=a[a[:,7]==0];g={}
        for row in first:
            key=tuple(row[[0,1,2,3,5,8]])
            c,e=g.get(key,(0.,0.));g[key]=(c+row[6],e+row[6]*row[4])
        groups.append(g)
    assert groups[0].keys()==groups[1].keys(),'birth/direction keys differ'
    dc=[];de=[]
    for key in groups[0]:
        (c1,e1),(c2,e2)=groups[0][key],groups[1][key]
        dc.append((c2-c1)/c2);de.append(e2/c2-e1/c1)
    r={'packet_sha256':{str(m):hashlib.sha256((R/f'inputs/spectral11/m{m}.json').read_bytes()).hexdigest() for m in (1,2)},'physical_cohorts':[len(a) for a in arrays],'other47_rows':len(rest[0]),'other47_tuple_byte_identity':True,'other47_tuple_sha256':hashlib.sha256(rest[0].tobytes()).hexdigest(),'source_metadata_equal':True,'first_cell_birth_direction_keys':len(groups[0]),'first_cell_count_max_relative_delta':max(map(abs,dc)),'first_cell_mean_max_absolute_delta_eV':max(map(abs,de)),'birth_times':[len(np.unique(a[:,0])) for a in arrays]}
    (R/'evidence/run13/SOURCE_SUPPORT_AUDIT.json').write_text(json.dumps(r,indent=2)+'\n');return r

def read_case(m,rtol):
    rec,y=(load_sealed_parent(R,m,rtol,R/'provenance/RUN11_SHA256SUMS.txt') if m==1 else load_complete(R,m,rtol));packet=json.loads((R/f'inputs/spectral11/m{m}.json').read_text());model=SpectralModel(coalesce_reflections(packet));obs=model.observables(y)
    for k in obs:
        if obs[k]!=rec['observable'][k]:raise ValueError(f'endpoint observable mismatch {m} {k}')
    scale=model.nh*model.a0**3
    for i,species in enumerate(('HI','HeI','HeII','DI')):obs['photoheat_'+species+'_J_com3']=float(y[model.p+4+i]*scale*EV_J)
    obs['photoheat_total_J_com3']=sum(obs['photoheat_'+s+'_J_com3'] for s in ('HI','HeI','HeII','DI'))
    obs['thermal_J_com3']=obs['thermal_J_m3']*(model.a0*np.exp(model.dx))**3
    counts=np.array(packet['cohorts']);obs['born_energy_J_com3']=float(np.dot(counts[:,6],counts[:,4])*model.a0**3*EV_J)
    obs['signed_photon_residual_com3']=obs['survivor_com3']+sum(obs[s+'_com3'] for s in ('HI','HeI','HeII','DI'))-obs['born_com3']
    return rec,obs

def classify_survivors():
    result={}
    for m,tol in [(1,3e-11),(2,3e-11),(1,6e-12),(2,6e-12)]:
        if not (R/f'evidence/joint11_sided_m{m}_{tol:.0e}/result.json').exists():continue
        rec,y=(load_sealed_parent(R,m,tol,R/'provenance/RUN11_SHA256SUMS.txt') if m==1 else load_complete(R,m,tol))
        packet=json.loads((R/f'inputs/spectral11/m{m}.json').read_text());model=SpectralModel(coalesce_reflections(packet))
        energy=model.rays(1.,model.m)[0];pop=model.B*np.exp(-y[27:model.p])*model.nh*model.a0**3;first=model.coh[:,7]==0
        masks={'first_below_H':first&(energy<13.6),'first_H_only':first&(energy>=13.6)&(energy<model.chi[3]),'first_above_D':first&(energy>=model.chi[3]),'other47':~first}
        data={key:float(pop[mask].sum()) for key,mask in masks.items()}
        from retarded_integrator import CHARGE
        data['nthermal_scaled']=float((1+CHARGE)@y[:13]);data['u_scaled']=float(y[13])
        result[f'm{m}_{tol:.0e}']=data
    a,b=result['m1_3e-11'],result['m2_3e-11']
    result['m2_minus_m1']={k:b[k]-a[k] for k in a}
    result['relative_subH_difference']=(b['first_below_H']-a['first_below_H'])/b['first_below_H']
    result['temperature_ratio_u_times_inverse_n']=b['u_scaled']/a['u_scaled']*a['nthermal_scaled']/b['nthermal_scaled']
    result['relative_u_change']=(b['u_scaled']-a['u_scaled'])/b['u_scaled']
    result['relative_nthermal_change']=(b['nthermal_scaled']-a['nthermal_scaled'])/b['nthermal_scaled']
    return result

def analyze():
    source=source_audit();a1,o1=read_case(1,3e-11);a2,o2=read_case(2,3e-11)
    _,t1=read_case(1,6e-12)
    fields=['T_K','x_HII','x_DII','x_HeII','x_HeIII','survivor_com3','HI_com3','HeI_com3','HeII_com3','DI_com3','thermal_J_m3','thermal_J_com3','photoheat_total_J_com3','photoheat_HI_J_com3','photoheat_HeI_J_com3','photoheat_HeII_J_com3','photoheat_DI_J_com3','photon_energy_J_com3','photon_work_J_com3','gas_work_J_com3','born_com3','born_energy_J_com3']
    rows=[{'quantity':k,'m1':o1[k],'m2':o2[k],'delta_m2_minus_m1':o2[k]-o1[k],'relative_to_m2':(o2[k]-o1[k])/o2[k] if o2[k]!=0 else None,'m1_solver_delta_tight_minus_standard':t1[k]-o1[k]} for k in fields]
    tight_path=R/'evidence/joint11_sided_m2_6e-12/result.json'
    tight_record=tight_obs=None
    if tight_path.exists():
        tight_record,tight_obs=read_case(2,6e-12)
        for row in rows:
            k=row['quantity'];row.update(m1_tight=t1[k],m2_tight=tight_obs[k],m2_solver_delta_tight_minus_standard=tight_obs[k]-o2[k],m2_solver_relative_to_tight=(tight_obs[k]-o2[k])/tight_obs[k] if tight_obs[k]!=0 else None,tight_spectral_relative_to_m2=(tight_obs[k]-t1[k])/tight_obs[k] if tight_obs[k]!=0 else None)
    residual_diff=o2['signed_photon_residual_com3']-o1['signed_photon_residual_com3']
    contrast=(o2['survivor_com3']-o1['survivor_com3'])+sum(o2[s+'_com3']-o1[s+'_com3'] for s in ('HI','HeI','HeII','DI'))-(o2['born_com3']-o1['born_com3'])
    result={'schema':'rei.run13.m2.comparison.v1','source_audit':source,'m2_complete':True,'m2_new_runs':1,'m1_evidence':'retained RUN11 verified archive','m2_rtol':a2['rtol'],'m2_segments':a2['next_segment'],'m2_dimension':a2['dimension'],'m2_integration_wall_s':sum(a2['chunk_wall_s']),'m1_observable':o1,'m2_observable':o2,'comparison':rows,'photon_contrast_residual_com3':contrast,'signed_ledger_difference_com3':residual_diff,'contrast_identity_roundoff_com3':contrast-residual_diff,'continuum_error_bound':'NOT_ESTABLISHED','observed_order':'NOT_ESTABLISHED_m4_not_run'}
    result['m2_tight_status']='COMPLETE' if tight_record else 'NOT_RUN'
    if tight_record:
        result['m2_new_runs']=2;result['m2_tight_observable']=tight_obs;result['m2_tight_integration_wall_s']=sum(tight_record['chunk_wall_s'])
    result['survivor_classification']=classify_survivors()
    out=R/'evidence/run13'
    with (out/'M1_M2_COMPARISON.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'NUMERICAL_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'source_audit':source,'comparison':rows,'m2_wall':result['m2_integration_wall_s']},indent=2));return result
if __name__=='__main__':
    import sys
    if '--source-only' in sys.argv: print(json.dumps(source_audit(),indent=2))
    else:analyze()
