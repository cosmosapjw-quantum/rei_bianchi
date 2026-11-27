#!/usr/bin/env python3
"""One bounded audit of saved PHYS80 execution data; imports no ODE code.

No solver, RHS, Jacobian, source-rate or equilibrium-root call is made.
New arithmetic is limited to read-only validation of already saved arrays.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[key]='1'
import hashlib
import json
import math
from pathlib import Path
import platform
import traceback
from datetime import datetime, timezone
import numpy as np

ROOT=Path('/tmp/hh_phys79_work/WU088_HH/research/hh_phys80_sandbox_reduction_20261022')
RUN=ROOT/'results/reduced'
OUT=Path('/tmp/phys80_review/postflight_audit_001.json')
if OUT.exists():raise SystemExit('CREATE_ONLY_POSTFLIGHT_RECEIPT_ALREADY_EXISTS')
def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def check(condition,message):
    if not condition:raise AssertionError(message)
def finite(array):return array.dtype.kind not in 'fc' or bool(np.isfinite(array).all())
def arrays(path):
    with np.load(path,allow_pickle=False) as a:return {k:a[k].copy() for k in a.files}
KB=1.380649e-23/1.602176634e-19
GROUPS=[('H1',1),('D',1),('T',1),('He3',2),('He4',2),('Li6',3),('Li7',3),('n',0)]
ROMAN=('I','II','III','IV')
NAMES=[iso+'_'+ROMAN[q] if iso!='n' else 'n' for iso,maximum in GROUPS for q in range(maximum+1)]
CHARGES=[q for iso,maximum in GROUPS for q in range(maximum+1)]
INDICES={iso:[i for i,name in enumerate(NAMES) if name==iso or name.startswith(iso+'_')] for iso,_ in GROUPS}
def state_metrics(states,p):
    y,u=states[:,:-1],states[:,-1]
    check(states.shape[1]==22 and np.isfinite(states).all(),'finite 22-state shape')
    check(bool(np.all(y>=0)) and bool(np.all(u>0)),'strict saved state positivity')
    totals=np.array([[math.fsum(float(row[j]) for j in INDICES[iso]) for iso,_ in GROUPS] for row in y])
    initial=np.array([math.fsum(float(p['initial_Y_per_H'][j]) for j in INDICES[iso]) for iso,_ in GROUPS])
    present=initial>0
    isotope=float(np.max(abs(totals[:,present]/initial[present]-1)))
    absent=float(np.max(abs(totals[:,~present])))
    xe=np.array([math.fsum(float(q)*float(a) for q,a in zip(CHARGES,row)) for row in y])
    particle=np.array([math.fsum([*[float(a) for a in row],float(x)]) for row,x in zip(y,xe)])
    temp=np.array([float(a)/(1.5*KB*float(n)) for a,n in zip(u,particle)])
    eps=p['ionic_potential_eV']
    energy=np.array([math.fsum([float(a),*[float(e)*float(v) for e,v in zip(eps,row)]]) for row,a in zip(y,u)])
    e0=math.fsum([p['initial_u_eV_per_H'],*[float(e)*float(v) for e,v in zip(eps,p['initial_Y_per_H'])]])
    energy_error=float(np.max(abs((energy-e0)/e0)))
    check(isotope<=1e-10 and absent==0,'isotope gate')
    check(energy_error<=2e-10,'energy gate')
    check(bool(np.all((temp>=2.7)&(temp<=2e5))),'CX source domain')
    if p['ci_rows']:
        check(p['ci_rows']==[0,1,3],'neutral CI rows')
        check(bool(np.all((temp>=1/KB)&(temp<=20000/KB))),'CI source domain')
    return {'points':len(states),'minimum_species':float(y.min()),'minimum_u':float(u.min()),
            'isotope_relative_max_fsum':isotope,'absent_isotope_absolute_max':absent,
            'energy_relative_max_fsum':energy_error,'temperature_min_K':float(temp.min()),
            'temperature_max_K':float(temp.max()),'source_domains':'PASS'},temp,xe,particle

report={'schema':'PHYS80_INDEPENDENT_SAVED_RESULT_AUDIT_V1','started_utc':datetime.now(timezone.utc).isoformat(),
        'command':'python -B /tmp/phys80_review/postflight_readonly.py',
        'versions':{'Python':platform.python_version(),'NumPy':np.__version__},
        'actual_new_ODE_calls_by_auditor':0,'old_suite_runs_by_auditor':0,'RHS_calls_by_auditor':0,
        'Jacobian_calls_by_auditor':0,'rate_evaluations_by_auditor':0,'root_solves_by_auditor':0,
        'root_mutations_by_auditor':0,'status':'IN_PROGRESS','cases':[],'HH_R10':'OFF','production_admission':'NOT_ISSUED'}
try:
    science=read(ROOT/'verification/SCIENCE_STDOUT.json')
    resume=read(ROOT/'verification/RESUME_STDOUT.json')
    completed=read(ROOT/'verification/SCIENCE_COMMAND_COMPLETED.json')
    resumed=read(ROOT/'verification/RESUME_COMMAND_COMPLETED.json')
    check(completed['exit_code']==resumed['exit_code']==0,'CLI exit status')
    check((ROOT/'verification/SCIENCE_STDERR.txt').stat().st_size==0,'science stderr')
    check((ROOT/'verification/RESUME_STDERR.txt').stat().st_size==0,'resume stderr')
    source=science['source'];check(source==resume['source'],'resume used same sources')
    check(hashlib.sha256(canonical(source['files'])).hexdigest()==source['sha256'],'manifest digest')
    for relative,meta in source['files'].items():
        path=ROOT/relative
        check(path.stat().st_size==meta['bytes'] and sha(path)==meta['sha256'],'source pin:'+relative)
    prior=read('/tmp/phys80_review/check_result_001.json')
    for relative in ('source/reduced.py','source/phys79_bridge.py','source/run_reduced.py','inputs/REDUCTION_PLAN.json','vendor/PHYS79_PROVENANCE.json'):
        check(source['files'][relative]['sha256']==prior['source_hashes_before'][relative],'preflight-reviewed identity:'+relative)
    report['manifest_sha256']=source['sha256'];report['source_file_pins_checked']=len(source['files'])
    check(science['new_ODE_calls']==3 and resume['new_ODE_calls']==0,'execution/resume aggregate count')
    check(len(science['entries'])==len(resume['entries'])==3,'three exact requested entries')
    byid={r['science_id']:r for r in science['entries']}
    check(len(byid)==3 and {e['science_id'] for e in resume['entries']}==set(byid),'identity set')
    check(all(e['status']=='SKIP_COMPLETE_VERIFIED' and e['new_ODE_calls']==0 for e in resume['entries']),'verified resume skips')
    case_files=sorted((RUN/'cases').glob('*.json'))
    check({f.stem for f in case_files}==set(byid),'exactly three case receipts')
    file_hashes_before={str(p.relative_to(ROOT)):sha(p) for p in (RUN/'cases').iterdir() if p.is_file()}
    all_markers=list((RUN/'attempts').glob('*/*/SOLVE_IVP_CALL_*.json'))
    all_failures=list((RUN/'attempts').glob('*/*/FAILED.json'))
    check(len(all_markers)==3 and not all_failures,'three call markers, no failed scientific attempts')
    check(len(list((RUN/'claims').glob('*.json')))==3,'three claims')
    saved={}
    for receipt_path in case_files:
        record=read(receipt_path);key=record['science_id'];summary=byid[key];binding=record['binding'];p=binding['physics']
        check(sha(receipt_path)==receipt_path.with_suffix('.json.sha256').read_text().strip(),'case receipt SHA')
        check(hashlib.sha256(canonical(binding)).hexdigest()==key,'scientific identity digest')
        check(record['status']=='COMPLETE' and record['checks']['passed'] is True,'completed passed receipt')
        check(binding['source']==source,'bound execution source')
        check(record['HH_R10']=='OFF' and record['production_admission']=='NOT_ISSUED','scope flags')
        check(binding['numerics']['strict_nonnegative_trials'] is True and binding['numerics']['projection']=='NONE','strict numerical contract')
        check(binding['numerics']['method']=='Radau' and binding['numerics']['analytic_jacobian'] is True,'solver method/Jacobian')
        check(record['solver']==summary['solver'] and record['checks']==summary['checks'],'stdout/receipt equality')
        check(record['solver']['new_ODE_calls']==1 and record['solver']['success'] is True,'one successful ODE')
        check(record['solver']['nfev']==record['solver']['rhs_calls'],'nfev callback count')
        check(record['solver']['njev']==record['solver']['jacobian_calls'],'njev callback count')
        check(record['provenance']['old_completed_replays']==record['provenance']['new_cosmological_ODE']==record['provenance']['NCP']==record['provenance']['benchmark']==0,'scope provenance counts')
        check(record['provenance']['resources']['admissible_slots']>=1,'positive lease admission observation')
        path=RUN/record['npz']['path'];check(path.stat().st_size==record['npz']['bytes'] and sha(path)==record['npz']['sha256'],'case NPZ pin')
        attempt=RUN/record['attempt'];started=read(attempt/'STARTED.json');returned=read(attempt/'SOLVE_IVP_RETURNED.json')
        check(started['binding']==binding and returned==record['solver'],'attempt binding/result identity')
        markers=list(attempt.glob('SOLVE_IVP_CALL_*.json'));check(len(markers)==1,'one marker per identity')
        marker=read(markers[0]);check(marker['call_index']==1 and marker['old_completed_identity_replay'] is False,'call marker meaning')
        check(sha(attempt/'RESULT.npz')==record['npz']['sha256'],'attempt/final result bytes')
        postflight=read(attempt/'POSTFLIGHT.json');check(postflight['checks']==record['checks'] and postflight['oracle']==record['oracle'],'postflight/receipt identity')
        a=arrays(path);raw=arrays(attempt/'RAW_SOLVER_RESULT.npz')
        check(all(finite(v) for v in a.values()),'all numeric saved arrays finite')
        check(a['species_names'].tolist()==NAMES,'frozen species order')
        check(a['isotope_names'].tolist()==[iso for iso,_ in GROUPS],'frozen isotope order')
        check(np.array_equal(raw['accepted_theta'],a['accepted_theta']) and np.array_equal(raw['accepted_z'],a['accepted_z']),'raw solver mesh preserved')
        nmesh=record['solver']['accepted_mesh_points'];dimension=binding['numerics']['dimension']
        check(a['accepted_raw_states'].shape==(nmesh,22) and a['accepted_z'].shape==(nmesh,dimension),'accepted arrays shape')
        check(a['raw_states'].shape==(161,22) and a['theta'].shape==(161,),'dense arrays shape')
        check(np.all(np.diff(a['accepted_theta'])>0) and a['accepted_theta'][0]==0 and a['accepted_theta'][-1]==p['theta_end'],'accepted time grid')
        check(np.array_equal(a['theta'],np.linspace(0,p['theta_end'],161)),'dense time grid')
        check(np.array_equal(a['raw_states'],np.c_[a['Y'],a['u_eV_per_H']]),'full/split saved arrays')
        initial=np.r_[p['initial_Y_per_H'],p['initial_u_eV_per_H']]
        check(np.array_equal(a['raw_states'][0],initial) and np.array_equal(a['accepted_raw_states'][0],initial),'exact saved initial state')
        accepted,_,_,_=state_metrics(a['accepted_raw_states'],p)
        dense,temperature,electron,particles=state_metrics(a['raw_states'],p)
        check(np.allclose(temperature,a['T_K'],rtol=5e-15,atol=0),'independent temperature recovery')
        parent_key=binding['parent_comparison_science_id'];parent_record=read(ROOT/'inputs/phys79_cases'/(parent_key+'.json'))
        parent_arrays=arrays(ROOT/'inputs/phys79_cases'/(parent_key+'.npz'))
        check(p==parent_record['binding']['physics'] and binding['parent_physics_id']==parent_record['physics_id'],'parent physics exactly preserved')
        check(np.array_equal(parent_arrays['theta'],a['theta']),'parent comparison grid')
        scale=np.array(parent_record['binding']['numerics']['scale_vector'])
        difference=(a['raw_states']-np.c_[parent_arrays['Y'],parent_arrays['u_eV_per_H']])/scale
        check(np.array_equal(difference,a['parent_scaled_state_difference']),'stored parent difference')
        parent_error=float(np.max(abs(difference)));check(parent_error<=1e-6,'parent comparison gate')
        check(parent_error==record['checks']['parent_max_scaled_state_error'],'reported parent error')
        check(np.array_equal(a['scaled_states'],a['raw_states']/scale),'stored scaled states')
        case={'task_id':record['task_id'],'science_id':key,'receipt_sha256':sha(receipt_path),'npz_sha256':sha(path),
              'solver':record['solver'],'accepted':accepted,'dense':dense,'parent_scaled_error':parent_error,
              'independent_saved_temperature_difference_max_K':float(np.max(abs(temperature-a['T_K']))),
              'source_pins':'PASS','receipt_stdout_attempt_identity':'PASS','strict_contract':'PASS'}
        if p['control_id']=='C02':
            oracle=record['oracle'];D=p['isotope_inventory_per_H']['D'];dii=NAMES.index('D_II')
            distance=abs(float(a['Y'][-1,dii])-oracle['equilibrium_Y_per_H'][dii])/D
            n0=math.fsum([*[float(v) for v in p['initial_Y_per_H']],float(electron[0])])
            delta=p['ionic_potential_eV'][dii]-p['ionic_potential_eV'][NAMES.index('H1_II')]
            expected=p['T_initial_K']-delta*(a['Y'][:,dii]-p['initial_Y_per_H'][dii])/(1.5*KB*n0)
            extent_error=float(np.max(abs(a['T_K']-expected)))
            check(distance<=1e-6 and extent_error<=1e-9,'C02 equilibrium/extent-T gates')
            check(distance==record['checks']['D_final_equilibrium_distance_over_inventory'],'reported C02 equilibrium distance')
            eq=np.array(oracle['equilibrium_Y_per_H']);ix={name:i for i,name in enumerate(NAMES)}
            balance=math.exp(-43/oracle['equilibrium_T_K'])*eq[ix['D_I']]*eq[ix['H1_II']]-eq[ix['D_II']]*eq[ix['H1_I']]
            case['C02']={'D_final_equilibrium_distance_over_inventory':distance,'extent_temperature_error_K':extent_error,
                         'saved_equilibrium_balance_recomputed':balance,'equilibrium_root_resolved_again':False}
        saved[record['task_id']]=a;report['cases'].append(case)
    refinement=float(np.max(abs(saved['C01_REDUCED_BASE']['scaled_states']-saved['C01_REDUCED_REFINED']['scaled_states'])))
    check(refinement==science['refinement']['max_scaled_state_difference'] and refinement<=1e-6,'refinement gate')
    check(science['refinement']==resume['refinement'],'resume refinement readout')
    invocations=[read(p) for p in (RUN/'invocations').glob('*.json')]
    check(any(i==science for i in invocations) and any(i==resume for i in invocations),'durable invocation readbacks')
    first=read(ROOT/'verification/independent/check_result_001.json');supplement=read(ROOT/'verification/independent/jacobian_supplement_001.json')
    check(first['failed']==1 and first['passed']==15 and first['actual_ODE_calls']==0,'first fixture failure preserved')
    check(supplement['passed'] is True and supplement['completed_Jacobian_points_replayed']==0 and supplement['actual_ODE_calls']==0,'bounded supplement preserved')
    check(sha(ROOT/'verification/independent/check_result_001.json')==sha('/tmp/phys80_review/check_result_001.json'),'first failure original bytes')
    check(sha(ROOT/'verification/independent/jacobian_supplement_001.json')==sha('/tmp/phys80_review/jacobian_supplement_001.json'),'supplement original bytes')
    file_hashes_after={str(p.relative_to(ROOT)):sha(p) for p in (RUN/'cases').iterdir() if p.is_file()}
    check(file_hashes_before==file_hashes_after,'audit preserved case bytes')
    report.update(status='PASS_SCOPED',new_scientific_ODE_calls_observed=3,scientific_failures_observed=0,
                  successful_verified_resume_skips=3,resume_new_ODE_calls=0,old_completed_replays=0,
                  total_nfev=sum(c['solver']['nfev'] for c in report['cases']),
                  total_njev=sum(c['solver']['njev'] for c in report['cases']),
                  total_nlu=sum(c['solver']['nlu'] for c in report['cases']),
                  accepted_mesh_points=sum(c['accepted']['points'] for c in report['cases']),
                  dense_samples=sum(c['dense']['points'] for c in report['cases']),
                  refinement_max_scaled_difference=refinement,first_verification_fixture_failure_preserved=True,
                  case_files_unchanged_during_audit=True,case_file_hashes=file_hashes_after,
                  claim_scope='saved finite endpoints and samples, byte/source/identity/count audit; no continuum certificate, no rerun, no rate-accuracy or production admission')
except Exception as exc:
    report.update(status='FAIL',error=repr(exc),traceback=traceback.format_exc())
report['completed_utc']=datetime.now(timezone.utc).isoformat()
report['audit_script_sha256']=sha(__file__)
report['input_summary_sha256']={name:sha(ROOT/'verification'/name) for name in ('SCIENCE_STDOUT.json','RESUME_STDOUT.json','SCIENCE_COMMAND_COMPLETED.json','RESUME_COMMAND_COMPLETED.json')}
with OUT.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('cases','case_file_hashes','traceback')},indent=2,sort_keys=True))
for case in report['cases']:
    print(json.dumps({k:case[k] for k in ('task_id','accepted','dense','parent_scaled_error')},sort_keys=True))
raise SystemExit(0 if report['status']=='PASS_SCOPED' else 1)
