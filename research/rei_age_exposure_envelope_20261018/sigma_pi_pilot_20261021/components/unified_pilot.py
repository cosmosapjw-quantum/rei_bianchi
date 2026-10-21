#!/usr/bin/env python3
"""Selective components and exact-state z4->2 continuation; no prefix replay."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[key]='1'
import sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'components')]
import argparse, json, hashlib, time, traceback, platform, resource, multiprocessing as mp, queue, math, shutil, csv
ENTRY_STARTED=time.monotonic()
from dataclasses import replace
from types import SimpleNamespace
import numpy as np
import scipy
from scipy.integrate import solve_ivp
import adapter as original
import component_adapter as ad
import pilot as legacy
import resources as rs
atomic_json=legacy.atomic_json
atomic_npz=legacy.atomic_npz
PHASE='b1'
LIMITS={'sandbox': {'workers':4,'case_s':30.,'child_s':240.,'controller_s':180.},'ncp':{'workers':63,'case_s':60.,'child_s':1800.,'controller_s':1200.}}
OLD_CHILD=8.778983763986616
OLD_CONTROLLER=2.720931695002946

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def fixed_output(): return ROOT/('components/results' if PHASE=='b1' else 'z2_extension/results')
def case_dir(case):
    return ROOT/case.get('prefix_relative', 'components/results/cases/'+case['id'])
def config_axes(c): return (c['Sigma_F_i'],c.get('P_m_i',0.),c.get('P_r_i',c['Pi_F_signed_i']))
def reuse_records(): return json.loads((ROOT/'components/REUSE_MAP.json').read_text())
def component_cases():
    mapping={(r['Sigma_F_i'],r['P_m_i'],r['P_r_i']):r for r in reuse_records()}
    result=[]
    for c in ad.cases():
        c['phase']='b1'
        if not c['config']['guard'] and config_axes(c['config']) in mapping:
            r=mapping[config_axes(c['config'])]
            d=ROOT/'results/cases'/r['original_case_id']
            for name,key in [('raw.npz','raw_sha256'),('INPUT.json','input_sha256'),('RESULT.json','receipt_sha256')]:
                if sha(d/name)!=r[key]: raise ValueError('REUSE_HASH_MISMATCH:'+str(d/name))
            c['reuse']={**r,'raw_path':'results/cases/'+r['original_case_id']+'/raw.npz'}
        result.append(c)
    assert len([c for c in result if 'reuse' in c])==35
    return result

def tail_cases():
    result=[]
    for c in original.cases()+[c for c in component_cases() if 'reuse' not in c]:
        prefix=('results/cases/' if 'P_m_i' not in c['config'] else 'components/results/cases/')+c['id']
        folder=ROOT/prefix
        r=json.loads((folder/'RESULT.json').read_text())
        if r['status']!='COMPLETED': raise ValueError('PREFIX_NOT_COMPLETED:'+c['id'])
        result.append({'id':c['id'],'config':c['config'],'phase':'b2','prefix_relative':prefix,
            'prefix_raw_sha256':sha(folder/'raw.npz'),'prefix_input_sha256':sha(folder/'INPUT.json'),
            'prefix_result_sha256':sha(folder/'RESULT.json')})
    assert len(result)==237 and len({c['id'] for c in result})==237
    return result

def plan(output):
    output=Path(output)
    if output.resolve()!=fixed_output().resolve(): raise ValueError('FIXED_CHECKPOINT_REQUIRED_NO_BUDGET_RESET')
    ad.verify_source()
    m={'schema':'rei_selective_extension.v1','phase':PHASE,'cases':component_cases() if PHASE=='b1' else tail_cases(),
       'contract_sha256':sha(ROOT/'UNIFIED_EXECUTION_CONTRACT.md'),'component_contract_sha256':sha(ROOT/'components/COMPONENT_CONTRACT.md'),
       'source':original.SOURCE,'nominal_cases':175 if PHASE=='b1' else 231,'guard_cases':3 if PHASE=='b1' else 6}
    f=output/'MANIFEST.json'
    if f.exists():
        if json.loads(f.read_text())!=m: raise ValueError('RESUME_MANIFEST_MISMATCH')
    else: atomic_json(f,m)
    return m

def execution_identity():
    files=['adapter.py','pilot.py','resources.py','components/component_adapter.py','components/unified_pilot.py']
    return {'sha256':{n:sha(ROOT/n) for n in files},'vendor_sha256':original.SOURCE['files'],
      'python_version':sys.version,'python_executable':sys.executable,'python_semantic_version':platform.python_version(),
      'numpy_version':np.__version__,'scipy_version':scipy.__version__}

def bind_execution_identity(output):
    cur=execution_identity();f=Path(output)/'RESUME_CODE_IDENTITY.json'
    if f.exists():
        old=json.loads(f.read_text())['identity']
        if any(old[k]!=cur[k] for k in ('sha256','python_semantic_version','numpy_version','scipy_version')):
            repair_path=ROOT/'z2_extension/OPERATIONAL_REPAIR.json'
            if not repair_path.exists():raise ValueError('RESUME_EXECUTION_CODE_MISMATCH')
            repair=json.loads(repair_path.read_text());changed=[k for k in old['sha256'] if old['sha256'][k]!=cur['sha256'].get(k)]
            if changed!=['components/unified_pilot.py'] or old['sha256'][changed[0]]!=repair['old_runner_sha256'] or cur['sha256'][changed[0]]!=repair['new_runner_sha256']:
                raise ValueError('UNAUTHORIZED_RESUME_SOURCE_TRANSITION')
            if any(old[k]!=cur[k] for k in ('python_semantic_version','numpy_version','scipy_version')):raise ValueError('REPAIR_RUNTIME_MISMATCH')
            sidecar=Path(output)/'RESUME_CODE_IDENTITY.OPERATIONAL_REPAIR.json'
            binding={'identity':cur,'original_identity_sha256':sha(f),'repair_authorization_sha256':sha(repair_path),'original_identity_preserved':True}
            if sidecar.exists() and json.loads(sidecar.read_text())!=binding:raise ValueError('REPAIR_RESUME_BINDING_MISMATCH')
            if not sidecar.exists():atomic_json(sidecar,binding)
    else: atomic_json(f,{'identity':cur})
    return cur

def resume_state(output,case):
    if 'reuse' in case: return 'REUSED_VERIFIED'
    d=Path(output)/'cases'/case['id']
    if (d/'INPUT.json').exists() and json.loads((d/'INPUT.json').read_text())!=case: raise ValueError('RESUME_INPUT_MISMATCH')
    if (d/'RESULT.json').exists():
        r=json.loads((d/'RESULT.json').read_text())
        if r['id']!=case['id'] or r['config']!=case['config']: raise ValueError('RESUME_RESULT_MISMATCH')
        if r['status']=='COMPLETED' and (not (d/'raw.npz').exists() or sha(d/'raw.npz')!=r['raw_sha256']): raise ValueError('RESUME_RAW_HASH_MISMATCH')
        return r['status']
    return 'INCOMPLETE_PRESERVED' if (d/'ATTEMPT.json').exists() else 'PENDING'

def _approval(path,manifest):
    r=json.loads(Path(path).read_text())
    if r.get('decision')!='PASS_SCOPED_EXECUTION_CONTRACT' or r.get('contract_sha256')!=manifest['contract_sha256']: raise ValueError('PHYSICS_CONTRACT_REVIEW_MISMATCH')
    return r

def tail_validate(c,sol,out,prefix,tail):
    checks={'solver_success':bool(sol.success),'finite_solution':bool(np.isfinite(sol.y).all()),
      'finite_observables':all(np.isfinite(v).all() for v in out.values()),'epochs_153':len(sol.t)==153,
      'tail_epochs_33':len(tail.t)==33,'strictly_increasing_x':bool(np.all(np.diff(sol.t)>0)),
      'full_state_preserved':sol.y.shape[0]==(56 if c['guard'] else 40),
      'exact_join_x':bool(tail.t[0]==prefix['x'][-1]), 'exact_join_state':bool(np.array_equal(tail.y[:,0],prefix['raw_y'][:,-1])),
      'exact_prefix_x':bool(np.array_equal(sol.t[:121],prefix['x'])),
      'exact_prefix_y':bool(np.array_equal(sol.y[:,:121],prefix['raw_y'])),
      'reached_z2':bool(sol.t[-1]==math.log(7.) and abs(out['a'][-1]-1/3)<=2e-16),
      'positive_H':bool(np.all(out['H']>0)), 'canonical_nonnegative':bool(np.all(out['massive_min_cell_population']>=0)),
      'gamma_number':bool(np.max(abs(out['gamma_N0']-1))<=5e-11),'nu_number':bool(np.max(abs(out['nu_N0']-1))<=5e-11),
      'positive_energy':all(np.all(out[k]>0) for k in ('rad_energy_norm','dust_energy_norm','massive_energy_norm')),
      'gamma_brightness_sample':bool(out['minimum_brightness_gamma'].min()>=-1e-10),
      'nu_brightness_sample':bool(out['minimum_brightness_nu'].min()>=-1e-10),
      'initial_Sigma':bool(abs(out['Sigma_F'][0]-c['Sigma_F_i'])<=5e-12),
      'initial_P_m':bool(abs(out['P_m'][0]-c.get('P_m_i',0.))<=5e-12),
      'initial_P_r':bool(abs(out['P_r'][0]-c.get('P_r_i',c['Pi_F_signed_i']))<=5e-12),
      'component_sum':bool(np.array_equal(out['P_total'],out['P_m']+out['P_r'])),
      'component_cross_identity':bool(np.max(abs(out['Pi_total']**2-out['Pi_m']**2-out['Pi_r']**2-2*out['normalized_cross']))<=1e-15),
      'triangle_relations':bool(min(out['triangle_upper_slack'].min(),out['reverse_triangle_slack'].min())>=-1e-15)}
    if config_axes(c)==(0.,0.,0.):checks['true_isotropy']=bool(max(np.max(abs(out[k])) for k in ('Sigma_F','P_m','P_r'))<5e-12)
    return checks

def _worker(commands,replies):
    try: os.nice(10)
    except OSError: pass
    ad.verify_source()
    while True:
        task=commands.get()
        if task is None:break
        case,folder=task;folder=Path(folder);begin=time.monotonic();c=case['config']
        result={'id':case['id'],'config':c,'status':'FAILED','exit':1,'checks':{}}
        try:
            obj=ad.model(c)
            if case['phase']=='b1':
                sol=solve_ivp(obj.rhs,(0,obj.source.xmax),obj.initial_state(),t_eval=np.linspace(0,obj.source.xmax,121),method='DOP853',rtol=3e-11,atol=3e-13)
                atomic_npz(folder/'raw.npz',x=sol.t,raw_y=sol.y)
                out=ad.observables(obj,sol);checks=ad.validate(c,sol,out)
            else:
                prefix_folder=ROOT/case['prefix_relative']
                for name,key in [('raw.npz','prefix_raw_sha256'),('INPUT.json','prefix_input_sha256'),('RESULT.json','prefix_result_sha256')]:
                    if sha(prefix_folder/name)!=case[key]:raise ValueError('PREFIX_HASH_CHANGED')
                with np.load(prefix_folder/'raw.npz') as f: prefix={k:f[k] for k in f.files}
                obj.source=replace(obj.source,aend=1/3)
                x0=float(prefix['x'][-1]);end=math.log(7.)
                if x0!=math.log(21/5):raise ValueError('PREFIX_ENDPOINT_CHANGED')
                tail=solve_ivp(obj.rhs,(x0,end),prefix['raw_y'][:,-1].copy(),t_eval=np.linspace(x0,end,33),method='DOP853',rtol=3e-11,atol=3e-13)
                atomic_npz(folder/'tail.npz',x=tail.t,raw_y=tail.y)
                sol=SimpleNamespace(t=np.concatenate((prefix['x'],tail.t[1:])),y=np.concatenate((prefix['raw_y'],tail.y[:,1:]),axis=1),success=tail.success,nfev=tail.nfev,message=tail.message)
                atomic_npz(folder/'raw.npz',x=sol.t,raw_y=sol.y)
                out=ad.observables(obj,sol)
                # Reuse every historical diagnostic prefix exactly; new diagnostics are additive.
                for key in out:
                    if key in prefix:out[key][:121]=prefix[key]
                checks=tail_validate(c,sol,out,prefix,tail)
                result['tail_raw_sha256']=sha(folder/'tail.npz')
                result['prefix_provenance']={k:v for k,v in case.items() if k.startswith('prefix_')}
            atomic_npz(folder/'raw.npz',x=sol.t,raw_y=sol.y,**out)
            result.update(nfev=int(sol.nfev),solver_message=str(sol.message),checks=checks,
                initial={k:float(v[0]) for k,v in out.items()},endpoint={k:float(v[-1]) for k,v in out.items()},
                raw_sha256=sha(folder/'raw.npz'),raw_bytes=(folder/'raw.npz').stat().st_size)
            result['status']='COMPLETED' if all(checks.values()) else 'FAILED_VALIDATION';result['exit']=0 if result['status']=='COMPLETED' else 2
        except BaseException as e:result.update(error=str(e),traceback=traceback.format_exc())
        result.update(worker_wall_s=time.monotonic()-begin,worker_pid=os.getpid(),peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            worker_nice=os.nice(0),thread_environment={k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')})
        atomic_json(folder/'RESULT.json',result);replies.put((os.getpid(),case['id']))

def run(output, profile, requested, resume, approval):
    output = Path(output)
    started = ENTRY_STARTED
    manifest = plan(output)
    review = _approval(approval, manifest)
    code_identity = bind_execution_identity(output)
    limits = LIMITS[profile]
    if requested is not None and requested < 1:
        raise ValueError('max-workers must be positive')
    states = {case['id']: resume_state(output, case) for case in manifest['cases']}
    if not resume and any(v not in ('PENDING','REUSED_VERIFIED') for v in states.values()):
        raise ValueError('EXISTING_ATTEMPTS_REQUIRE_RESUME')
    pending = [c for c in manifest['cases'] if states[c['id']] == 'PENDING']
    receipts = output/'controllers'
    receipts.mkdir(parents=True, exist_ok=True)
    previous = [json.loads(p.read_text()) for p in receipts.glob('*.json')]
    # ATTEMPT charge is the conservative supervisor launch-to-observation wall.
    historical_child = OLD_CHILD if PHASE == 'b1' else 0.
    historical_controller = OLD_CONTROLLER if PHASE == 'b1' else 0.
    charged = historical_child
    for case in manifest['cases']:
        path = output/'cases'/case['id']/'ATTEMPT.json'
        if path.exists():
            attempt = json.loads(path.read_text())
            # Same fixed phase retains every prior profile debit.
            charged += attempt.get('charged_wall_s', attempt['per_case_cap_s'])
    old_elapsed = historical_controller + sum(r['controller_elapsed_s'] for r in previous)
    controller_cap = max(0., limits['controller_s']-old_elapsed)
    ctx = mp.get_context('spawn')
    replies = ctx.Queue()
    workers = {}
    active = {}
    samples = []
    sampler = rs.Sampler()
    stop_reason = 'CASE_SET_EXHAUSTED'
    runid = str(time.time_ns())

    def start_worker():
        commands = ctx.Queue()
        process = ctx.Process(target=_worker, args=(commands, replies))
        process.start()
        workers[process.pid] = (process, commands)
        return process.pid

    def finish(pid, status=None):
        nonlocal charged
        item = active.pop(pid)
        elapsed = time.monotonic()-item['start']
        charged += elapsed
        attempt = item['attempt']
        attempt.update(charged_wall_s=elapsed, supervisor_outcome=status or 'WORKER_RETURNED')
        folder = item['folder']
        atomic_json(folder/'ATTEMPT.json', attempt)
        if status is not None:
            # Stop only this controller's own worker, preserving partial files.
            process, commands = workers.pop(pid)
            process.terminate()
            process.join(timeout=2)
            if process.is_alive():
                process.kill()
                process.join(timeout=2)
            if not (folder/'RESULT.json').exists():
                atomic_json(folder/'RESULT.json', {'id': item['case']['id'],
                    'config': item['case']['config'], 'status': status, 'exit': 124,
                    'error': 'Supervisor bound; partial files and input preserved.'})

    try:
        while pending or active:
            now = time.monotonic()
            elapsed = now-started
            sample = sampler.sample(profile, requested)
            if not samples or now-samples[-1]['observed_monotonic'] >= 1:
                samples.append(sample)
            for pid in list(active):
                process = workers[pid][0]
                if not process.is_alive():
                    finish(pid, 'FAILED_WORKER_EXIT')
                elif now-active[pid]['start'] >= limits['case_s']:
                    finish(pid, 'FAILED_CASE_TIMEOUT')
            while True:
                try:
                    pid, caseid = replies.get_nowait()
                except queue.Empty:
                    break
                if pid in active and active[pid]['case']['id'] == caseid:
                    finish(pid)
            if elapsed >= controller_cap:
                stop_reason = 'CONTROLLER_CAP'
                break
            reserved = charged+len(active)*limits['case_s']
            if shutil.disk_usage(output).free < 100*1024**2:
                stop_reason = 'DISK_DEFERRAL'; break
            if not active and sample['slots'] == 0:
                stop_reason = 'MEMORY_DEFERRAL'; break
            slot_count = sample['slots']
            while pending and len(active) < slot_count and reserved+limits['case_s'] <= limits['child_s']:
                # Enough remaining controller time for a full per-case allowance.
                if controller_cap-(time.monotonic()-started) < limits['case_s']:
                    stop_reason = 'CONTROLLER_LAUNCH_RESERVATION'
                    pending = pending  # retained as pending in readback
                    break
                idle = [p for p in workers if p not in active and workers[p][0].is_alive()]
                pid = idle[0] if idle else start_worker()
                case = pending.pop(0)
                folder = output/'cases'/case['id']
                folder.mkdir(parents=True, exist_ok=True)
                if resume_state(output, case) != 'PENDING':
                    continue
                # Exclusive only for the same case; never a host/global lock.
                try:
                    fd = os.open(folder/'write.lock', os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
                except FileExistsError:
                    continue
                with os.fdopen(fd, 'w') as stream:
                    stream.write(str(os.getpid()))
                atomic_json(folder/'INPUT.json', case)
                attempt = {'id': case['id'], 'profile': profile, 'controller': runid,
                           'worker_pid': pid, 'per_case_cap_s': limits['case_s'],
                           'status': 'LAUNCHED', 'started_unix': time.time()}
                atomic_json(folder/'ATTEMPT.json', attempt)
                active[pid] = {'case': case, 'folder': folder, 'start': time.monotonic(), 'attempt': attempt}
                workers[pid][1].put((case, str(folder)))
                reserved += limits['case_s']
            if not active and pending:
                if charged+limits['case_s'] > limits['child_s']:
                    stop_reason = 'CHILD_WALL_LAUNCH_RESERVATION'
                    break
                if controller_cap-(time.monotonic()-started) < limits['case_s']:
                    stop_reason = 'CONTROLLER_LAUNCH_RESERVATION'
                    break
            time.sleep(.05)
    finally:
        for pid in list(active):
            finish(pid, 'INCOMPLETE_CONTROLLER_STOP')
        for pid, (process, commands) in workers.items():
            if process.is_alive():
                commands.put(None)
            process.join(timeout=2)
            if process.is_alive():
                process.terminate()
                process.join(timeout=2)
        states = {c['id']: resume_state(output, c) for c in manifest['cases']}
        receipt = {'profile': profile, 'controller_elapsed_s': time.monotonic()-started,
                   'previous_controller_elapsed_s': old_elapsed,
                   'cumulative_child_charged_wall_s': charged, 'stop_reason': stop_reason,
                   'states': states, 'resource_samples': samples,
                   'contract_review_decision': review['decision'],
                   'execution_code_identity': code_identity,
                   'budget_accounting': 'supervisor launch to observed return; setup/queue overhead included conservatively',
                   'unrelated_process_actions': 0, 'historical_child_debit_s': historical_child,
                   'historical_controller_debit_s': historical_controller, 'argv': sys.argv,
                   'exit': 0 if all(v in ('COMPLETED','REUSED_VERIFIED') for v in states.values()) else 2}
        atomic_json(receipts/(runid+'.json'), receipt)
        atomic_json(output/'STATUS.json', receipt)
    return receipt



def read_results(output):
    m=plan(output);r={}
    for c in m['cases']:
        state=resume_state(output,c)
        if state=='COMPLETED':r[c['id']]=json.loads((Path(output)/'cases'/c['id']/'RESULT.json').read_text())
        elif state=='REUSED_VERIFIED':
            folder=ROOT/'results/cases'/c['reuse']['original_case_id'];old=json.loads((folder/'RESULT.json').read_text())
            with np.load(folder/'raw.npz') as raw:out=ad.components({k:raw[k] for k in raw.files if k not in ('x','raw_y')})
            r[c['id']]={**old,'id':c['id'],'config':c['config'],'historical_execution':c['reuse'],
                'initial':{k:float(v[0]) for k,v in out.items()},'endpoint':{k:float(v[-1]) for k,v in out.items()}}
    return m,r

def check(output):
    m,r=read_results(output);nom=[c for c in m['cases'] if not c['config']['guard']];guards=[]
    for c in m['cases']:
        if not c['config']['guard']:continue
        base=next(b for b in nom if config_axes(b['config'])==config_axes(c['config']) and ('P_m_i' in b['config'])==('P_m_i' in c['config']))
        if c['id'] not in r or base['id'] not in r:guards.append({'id':c['id'],'status':'PENDING'});continue
        a,b=r[c['id']]['endpoint'],r[base['id']]['endpoint'];delta={k:abs(a[k]-b[k]) for k in ('Sigma_F','P_m','P_r','b')};delta['H_relative']=abs(a['H']/b['H']-1)
        guards.append({'id':c['id'],'nominal_id':base['id'],'status':'PASS' if max(delta.values())<=2e-6 else 'FAIL','absolute_endpoint_differences':delta})
    states={c['id']:resume_state(output,c) for c in m['cases']}
    report={'phase':PHASE,'completed_or_reused':len(r),'planned':len(m['cases']),'states':states,'refinement_controls':guards,
      'numerical_gate':'PASS_SCOPED_PRELIMINARY' if len(r)==len(m['cases']) and all(g['status']=='PASS' for g in guards) else 'PARTIAL_OR_FAILED',
      'scientific_admission':'PENDING_INDEPENDENT_RESULT_REVIEW','brightness_scope':'64-node sample','Hamiltonian_scope':'construction consistency',
      'reused_without_solver':35 if PHASE=='b1' else 0,'new_ivps':sum(resume_state(output,c)=='COMPLETED' for c in m['cases'])}
    atomic_json(Path(output)/'CHECK.json',report);return report

def main():
    global PHASE,LIMITS
    a=argparse.ArgumentParser();a.add_argument('command',choices=['plan','run','check']);a.add_argument('--phase',choices=['b1','b2'],required=True)
    a.add_argument('--profile',choices=['sandbox','ncp'],default='sandbox');a.add_argument('--max-workers',type=int);a.add_argument('--resume',action='store_true');a.add_argument('--review-approval',type=Path);a.add_argument('--case-deadline',type=float)
    args=a.parse_args();PHASE=args.phase
    if PHASE=='b2':
        LIMITS={'sandbox':{'workers':4,'case_s':30.,'child_s':120.,'controller_s':180.},'ncp':{'workers':63,'case_s':60.,'child_s':600.,'controller_s':600.}}
    if args.case_deadline is not None:
        ceiling=LIMITS[args.profile]['case_s']
        if not math.isfinite(args.case_deadline) or not 0<args.case_deadline<=ceiling:a.error('case deadline must be positive and no greater than contracted maximum')
        LIMITS[args.profile]={**LIMITS[args.profile],'case_s':args.case_deadline}
    output=fixed_output()
    if args.command=='run':
        if not args.review_approval:a.error('review approval required')
        r=run(output,args.profile,args.max_workers,args.resume,args.review_approval)
        from collections import Counter
        print(json.dumps({'states':dict(Counter(r['states'].values())),'child_s':r['cumulative_child_charged_wall_s'],'controller_s':r['controller_elapsed_s'],'stop_reason':r['stop_reason']}))
        return r['exit']
    r=plan(output) if args.command=='plan' else check(output)
    atomic_json(output/'controllers'/(str(time.time_ns())+'.json'),{'profile':args.profile,'controller_elapsed_s':time.monotonic()-ENTRY_STARTED,'argv':sys.argv,'operation':args.command,'scientific_solver_calls':0})
    print(json.dumps({k:v for k,v in r.items() if k not in ('cases','states')},indent=2));return 0
if __name__=='__main__':sys.exit(main())
