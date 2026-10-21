"""Independent read-only component audit: no ODE integration."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv,json,math,hashlib,sys
from pathlib import Path
import numpy as np
Q=Path(__file__).resolve().parents[1];P=Q.parent;sys.path.insert(0,str(P/'vendor'))
from canonical_fv import CanonicalMomentumFV
lock=json.loads((P/'vendor/REI_BACKGROUND_FAMILY_LOCK.json').read_text());c=lock['cosmology'];a0=lock['clock']['a_ref'];H0=c['H0_per_s'];om=c['Omega_m'];orr=c['Omega_r'];ol=c['Omega_lambda'];K=8*math.pi*6.67430e-11/299792458.**2;rhoc=3*H0*H0/K;pref=.1*om/a0**3;href=H0*math.sqrt(om/a0**3+orr/a0**4+ol)
st={'new_cases':0,'new_samples':0,'old_decomposed_cases':0,'old_samples':0,'references_verified':0,'new_lanes':{},'max_new_axis_error':0.,'max_new_pressure_recompute_abs_J_m3':0.,'max_new_dimensionless_recompute_abs':0.,'max_old_decomposition_abs':0.,'max_old_component_closure_abs':0.,'max_new_component_closure_abs':0.,'max_full_reduced_raw_abs':0.,'minimum_E0':1e99,'minimum_H':1e99,'minimum_massive_population':1e99,'maximum_abs_A_m':0.,'maximum_abs_k':0.,'mixed_cases':[]}
R=Q/'results/new_sweep';run=json.loads((R/'run.json').read_text());assert run['status']=='COMPLETE' and run['completed']==606 and run['failed']==0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(Q/'component_pilot.py')==run['identity']['new_model_sha256']=='e2ce8b440765be3a728d8127a4f1085dbc304cabcaa7a5d4e892f92ccabd801e'
for f,h in run['identity']['parent_immutable_files'].items():assert sha(P/f)==h
assert sha(Q/'CONTRACT_KO.md')==run['identity']['contract_sha256'] and sha(Q/'reference_controls.json')==run['identity']['reference_controls_sha256']
end={r['id']:r for r in csv.DictReader((R/'endpoints.csv').open())};assert len(end)==606
child=0.;seen=set()
for f in sorted((R/'cases').glob('*.json')):
 r=json.loads(f.read_text());cid=f.stem;cc=r['case'];ic=r['initial'];assert r['status']=='COMPLETED' and r['logical_task_exit_status']==0 and r['identity']==run['identity'];assert cc['id']==cid;d=np.load(f.with_suffix('.npz'));y=d['state'];x=d['x'];assert y.shape==(8,65) and len(x)==65
 for k in d.files:assert np.isfinite(d[k]).all()
 assert abs(x[0])<1e-15 and abs(x[-1]-math.log(.2/a0))<1e-14 and np.all(np.diff(x)>0)
 A=ic['A_m'];M=CanonicalMomentumFV(30,A,24,12,3);m=M.moment_batch(x,y[1]);a=a0*np.exp(x);s=href*y[2];H=np.sqrt(H0**2*(.9*om/a**3+pref*m[:,0]+orr/a**4*y[3]+ol)+s*s)
 pm=rhoc*pref*(m[:,2]-m[:,1])/3;pr=rhoc*orr/a**4*y[4]/3;fac=math.sqrt(3)*K/H**2;pim=fac*pm;pir=fac*pr;pit=pim+pir
 for k,val in {'p_m_J_m3':pm,'p_r_J_m3':pr}.items():st['max_new_pressure_recompute_abs_J_m3']=max(st['max_new_pressure_recompute_abs_J_m3'],float(np.max(abs(val-d[k]))))
 for k,val in {'signed_Pi_m':pim,'signed_Pi_r':pir,'signed_Pi_total':pit,'Pi_m':abs(pim),'Pi_r':abs(pir),'Pi_total':abs(pit),'Sigma':math.sqrt(3)*abs(s)/H,'s_over_H':s/H}.items():st['max_new_dimensionless_recompute_abs']=max(st['max_new_dimensionless_recompute_abs'],float(np.max(abs(val-d[k]))))
 for k,val in {'work_m_J_m3_per_x':-6*(s/H)*pm,'work_r_J_m3_per_x':-6*(s/H)*pr}.items():assert np.max(abs(val-d[k]))<1e-25
 assert np.all(H>0) and np.all(y[3]>0) and M.cell_numbers.min()>0
 assert -1<=A<=2 and abs(ic['k'])<=.5
 errors=[abs(math.sqrt(3)*s[0]/H[0]-cc['signed_Sigma0']),abs(pim[0]-cc['signed_Pi_m0']),abs(pir[0]-cc['signed_Pi_r0'])];st['max_new_axis_error']=max(st['max_new_axis_error'],*errors);assert max(errors)<1e-12
 if cc['lane']=='MATTER_SLICE':assert ic['k']==0 and pir[0]==0
 else:st['mixed_cases'].append({'id':cid,'signed_Sigma0':cc['signed_Sigma0'],'initial_component_sum':float(pit[0]),'initial_sum_component_magnitudes':float(abs(pim[0])+abs(pir[0])),'endpoint_Sigma':float(d['Sigma'][-1]),'endpoint_signed_Pi_m':float(pim[-1]),'endpoint_signed_Pi_r':float(pir[-1]),'endpoint_signed_Pi_total':float(pit[-1])})
 for k,v in r['endpoint'].items():assert v==float(d[k][-1]) and float(end[cid][k])==v
 st['max_new_component_closure_abs']=max(st['max_new_component_closure_abs'],float(np.max(abs(d['signed_Pi_m']+d['signed_Pi_r']-d['signed_Pi_total']))));st['minimum_E0']=min(st['minimum_E0'],float(y[3].min()));st['minimum_H']=min(st['minimum_H'],float(H.min()));st['minimum_massive_population']=min(st['minimum_massive_population'],float(M.cell_numbers.min()));st['maximum_abs_A_m']=max(st['maximum_abs_A_m'],abs(A));st['maximum_abs_k']=max(st['maximum_abs_k'],abs(ic['k']));st['new_cases']+=1;st['new_samples']+=65;st['new_lanes'][cc['lane']]=st['new_lanes'].get(cc['lane'],0)+1;child+=r['child_wall_s'];seen.add((cc['signed_Sigma0'],cc['signed_Pi_m0'],cc['signed_Pi_r0']))
assert st['new_cases']==len(seen)==606 and len(list((R/'cases').glob('*.npz')))==606 and abs(child-run['aggregate_child_wall_s'])<1e-9
for f in sorted((Q/'decomposition/cases').glob('*.npz')):
 d=np.load(f);o=np.load(P/'results/pilot/cases'/f.name);a=a0*np.exp(o['x']);pm=rhoc*pref*o['massive_pi_s_norm'];pr=rhoc*orr/a**4*o['E2']/3;fac=math.sqrt(3)*K/o['H_per_s']**2
 for k,val in {'p_m_J_m3':pm,'p_r_J_m3':pr,'signed_Pi_m':fac*pm,'signed_Pi_r':fac*pr,'signed_Pi_total':fac*(pm+pr)}.items():st['max_old_decomposition_abs']=max(st['max_old_decomposition_abs'],float(np.max(abs(val-d[k]))))
 for k in ('x','zbar','elapsed_seconds','b','s_over_H','Sigma','H_per_s','E0','E2'):assert np.array_equal(d[k],o[k])
 st['max_old_component_closure_abs']=max(st['max_old_component_closure_abs'],float(np.max(abs(d['signed_Pi_total']-o['signed_Pi']))));st['old_decomposed_cases']+=1;st['old_samples']+=len(d['x'])
assert st['old_decomposed_cases']==625
refs=json.loads((Q/'reference_controls.json').read_text());table=list(csv.DictReader((R/'matter_slice_with_reference_controls.csv').open()));assert len(table)==625 and sum(r['provenance']=='NEW_COUPLED_ODE' for r in table)==600;tr={r['id']:r for r in table if r['provenance']=='REFERENCE_REUSE'};assert len(tr)==25
for r in refs['references']:
 cid=r['old_case_id'];op=P/'results/pilot/cases'/cid;oj=json.loads(op.with_suffix('.json').read_text());assert sha(op.with_suffix('.npz'))==r['old_npz_sha256'] and sha(op.with_suffix('.json'))==r['old_json_sha256'];assert oj['identity']==r['old_case_identity'] and oj['initial']==r['old_initial'] and oj['case']==r['old_case'];d=np.load(Q/'decomposition/cases'/f'{cid}.npz')
 for k,v in r['actual_initial'].items():assert v==float(d[k][0])
 for k,v in r['endpoint'].items():assert v==float(d[k][-1]) and float(tr[cid][k])==v
 assert float(tr[cid]['k'])==r['old_initial']['k'];st['references_verified']+=1
met=json.loads((Q/'validation/metrics.json').read_text())
for i,e in enumerate(met['comparisons']):
 d=np.load(Q/'validation'/f'comparison_{i}.npz');assert d['full_state'].shape==(40,65)
 for k,v in e['max_abs_difference'].items():actual=float(np.max(abs(d['reduced_'+k]-d['full_'+k])));assert actual==v;st['max_full_reduced_raw_abs']=max(st['max_full_reduced_raw_abs'],actual)
 assert np.max(abs(d['full_state'][[13,31]]-1))==0
st['actual_local_run']={k:run[k] for k in ('status','completed','failed','consumed_wall_s','aggregate_child_wall_s')};st['observed_selected_slots']=sorted(set(r['selected_slots'] for r in run['resource_observations']));st['core_model_sha256']=sha(Q/'component_pilot.py');st['review_mode']='read-only static source helper and existing arrays; no ODE solves';st['status']='PASS_RAW_AUDIT'
(Q/'evidence/RAW_AUDIT.json').write_text(json.dumps(st,indent=2)+'\n');print(json.dumps(st,indent=2))
