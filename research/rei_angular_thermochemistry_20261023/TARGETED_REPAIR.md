# Targeted reporting repair and continuation

Owner authorization: one reporting-only repair after batch1 failure. Physics, fits, initial conditions, solver, thresholds and tolerances unchanged.

Resume endpoint: eta=0.3720455828589731, 363 persisted accepted nodes, 39/201 reporting times. Earlier completed intervals are skipped. Original failed JSON and partial raw/metadata are preserved with attempt1 suffix before resume. A single zero-IVP empty/nonempty-mask regression runs inside batch2. Budget includes conservative CPU20/wall30 for the single preflight invocation, plus measured whole-child execution.

## Actual implementation diff

```diff
--- before/run_cases.py
+++ after/run_cases.py
@@ -5,6 +5,7 @@
 import os
 from pathlib import Path
 import resource
+import shutil
 import sys
 import time
 import traceback
@@ -29,6 +30,26 @@
 
 def dump(path,data):
     path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
+
+
+def store_reporting_samples(sol,samples,mask,sample_t):
+    if np.any(mask):
+        samples[:,mask]=sol.sol(sample_t[mask])
+
+
+def repair_regression():
+    class Fake:
+        calls=0
+        def sol(self,t):
+            self.calls+=1
+            assert len(t)>0
+            return np.ones((2,len(t)))
+    fake=Fake();samples=np.zeros((2,3));t=np.arange(3.)
+    store_reporting_samples(fake,samples,np.array([False,False,False]),t)
+    assert fake.calls==0 and np.all(samples==0)
+    store_reporting_samples(fake,samples,np.array([False,True,False]),t)
+    assert fake.calls==1 and np.all(samples[:,1]==1) and np.all(samples[:,[0,2]]==0)
+    dump(RESULTS/'targeted_repair_regression.json',{'pass':True,'new_IVPs':0,'empty_mask_calls':0,'nonempty_mask_calls':fake.calls})
 
 
 def make(case_id):
@@ -57,10 +78,10 @@
             'count_denominator_per_Href':float(h['count_scale_per_Href'])}
 
 
-def run_case(case_id):
+def run_case(case_id,resume=False):
     name,model,tight = make(case_id)
     final = RESULTS/f'{name}.json'
-    if final.exists():
+    if final.exists() and not resume:
         raise RuntimeError(f'CASE_ALREADY_HAS_OUTCOME: {name}; no automatic repeated IVP')
     started, cpu = time.perf_counter(),time.process_time()
     boundaries = model.boundaries()
@@ -70,6 +91,26 @@
     times,states = [0.],[model.y0.copy()]
     y = model.y0.copy()
     segments=[]
+    prior=None
+    resume_eta=0.
+    if resume:
+        prior=json.loads(final.read_text())
+        if prior['status']!='FAILED':
+            raise RuntimeError('RESUME_REQUIRES_FAILED_OUTCOME')
+        for path in [final,RESULTS/f'{name}_partial.json',RESULTS/f'{name}_partial.npz']:
+            backup=path.with_name(path.stem+'_attempt1'+path.suffix)
+            if backup.exists():
+                raise RuntimeError('ORIGINAL_ATTEMPT_ALREADY_PRESERVED')
+            shutil.copyfile(path,backup)
+        saved_meta=json.loads((RESULTS/f'{name}_partial.json').read_text())
+        with np.load(RESULTS/f'{name}_partial.npz',allow_pickle=False) as saved:
+            times=saved['accepted_eta'].tolist()
+            states=list(saved['accepted_Y'].T.copy())
+            assert np.array_equal(saved['sample_eta'],sample_t)
+            samples=saved['sample_Y'].copy()
+        resume_eta=float(times[-1]);y=states[-1].copy()
+        segments=saved_meta['segments']
+        assert segments[-1]['hi']==resume_eta and resume_eta in boundaries
     if model.oracle:
         rtol=2e-10
         atol=np.full(model.size,2e-12)
@@ -85,9 +126,15 @@
               'crossings':model.crossings,'background':model.bg.case,'background_sign':model.bg.sign,
               'endpoint_cross_sections':'interior eta offset min(1e-12,segmentwidth*1e-8); actual eta for geometry/work',
               'status':'RUNNING','segments':segments}
+    if resume:
+        metadata['resume']={'eta':resume_eta,'accepted_nodes':len(times),
+                            'report_times_filled':int(np.sum(np.isfinite(samples).all(axis=0))),
+                            'prior_attempt':final.stem+'_attempt1.json','earlier_intervals_repeated':0}
     dump(RESULTS/f'{name}_partial.json',metadata)
     try:
         for lo,hi in zip(boundaries[:-1],boundaries[1:]):
+            if hi<=resume_eta:
+                continue
             model.segment=(lo,hi)
             stamp=time.perf_counter()
             sol=solve_ivp(model.rhs,(lo,hi),y,method='Radau',jac=None if model.oracle else model.jacobian,
@@ -95,7 +142,7 @@
             y=sol.y[:,-1].copy()
             times.extend(sol.t[1:].tolist());states.extend(sol.y[:,1:].T.copy())
             mask=(sample_t>lo)&(sample_t<=sol.t[-1])
-            samples[:,mask]=sol.sol(sample_t[mask])
+            store_reporting_samples(sol,samples,mask,sample_t)
             segments.append({'lo':lo,'hi':hi,'last_eta':float(sol.t[-1]),'success':bool(sol.success),
                              'message':sol.message,'accepted_nodes':len(sol.t),'nfev':sol.nfev,'njev':sol.njev,
                              'nlu':sol.nlu,'solver_wall_s':time.perf_counter()-stamp})
@@ -121,8 +168,15 @@
         metadata['traceback']=traceback.format_exc()
         raise
     finally:
+        np.savez(RESULTS/f'{name}_partial.npz',accepted_eta=np.array(times),accepted_Y=np.array(states).T,
+                 sample_eta=sample_t,sample_Y=samples)
         metadata['child_case_wall_s']=time.perf_counter()-started
         metadata['child_case_cpu_s']=time.process_time()-cpu
+        if prior is not None:
+            metadata['resumed_invocation_case_wall_s']=metadata['child_case_wall_s']
+            metadata['resumed_invocation_case_cpu_s']=metadata['child_case_cpu_s']
+            metadata['child_case_wall_s']+=prior['child_case_wall_s']
+            metadata['child_case_cpu_s']+=prior['child_case_cpu_s']
         metadata['solver_wall_s']=sum(s['solver_wall_s'] for s in segments)
         metadata['accepted_nodes_total']=len(times)
         metadata['nfev_total']=sum(s['nfev'] for s in segments)
@@ -140,8 +194,12 @@
     parser=argparse.ArgumentParser()
     parser.add_argument('--cases',type=int,nargs='*',default=[])
     parser.add_argument('--checks',action='store_true')
+    parser.add_argument('--repair-regression',action='store_true')
+    parser.add_argument('--resume-case1',action='store_true')
     args=parser.parse_args()
     RESULTS.mkdir(exist_ok=True)
+    if args.repair_regression:
+        repair_regression()
     dump(RESULTS/'environment.json',{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
          'threads':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},
          'requested_executor':'gpt-6.1-sol/high','observed_executor':'runtime model identity unavailable',
@@ -155,7 +213,7 @@
         if not checks.get('overall_pass',False):
             raise RuntimeError('ALGEBRA_CHECKS_FAILED')
     for case_id in args.cases:
-        run_case(case_id)
+        run_case(case_id,resume=case_id==1 and args.resume_case1)
 
 
 if __name__=='__main__':
--- before/bounded_run.py
+++ after/bounded_run.py
@@ -37,10 +37,13 @@
     history=json.loads(ledger.read_text()) if ledger.exists() else {'batches':[],'cpu_limit_s':300,'wall_limit_s':420,'maximum_IVPs':11}
     if any(x['batch']==args.batch for x in history['batches']):
         raise RuntimeError('BATCH_ALREADY_ATTEMPTED; resume only explicitly unexecuted cases with owner authorization')
-    cpu=sum(x['child_cpu_s'] for x in history['batches']);wall=sum(x['child_wall_s'] for x in history['batches'])
+    history['preflight_conservative_charge']={'CPU_s':20,'wall_s':30,'basis':'enforced original check-process caps; body time not substituted for whole child'}
+    cpu=20+sum(x['child_cpu_s'] for x in history['batches']);wall=30+sum(x['child_wall_s'] for x in history['batches'])
     if cpu>=300 or wall>=420:
         raise RuntimeError('CUMULATIVE_BUDGET_EXHAUSTED')
-    groups={1:['--checks','--cases','1','2','3'],2:['--cases','4','5','6','7'],3:['--cases','8','9']}
+    groups={1:['--checks','--cases','1','2','3'],
+            2:['--repair-regression','--resume-case1','--cases','1','2','3','4','5','6','7'],
+            3:['--cases','8','9']}
     command=[sys.executable,str(BASE/'code/run_cases.py')]+groups[args.batch]
     env=os.environ.copy()
     for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
```

## Authorized numerical zero-face summary guard

The full oracle reached eta=ln7 with 1073 accepted nodes. Its T populations stayed exactly zero; the identically-zero neutron RHS row acquired only implicit-solver roundoff (maximum accepted scaled magnitude1.7899843162408834e-30). Owner classified the exact postprocessing equality as overly strict. The oracle numerical zero-face bound is64 machine eps =1.4210854715202004e-14; primary lift retains exact zeros. Every raw accepted/reporting state is preserved unchanged. The original oracle postprocessing failure and raw arrays are copied with attempt1 suffix; only its summaries are regenerated, with zero IVP replay. Batch3 runs only cases5–9.

```diff
--- before/angular_model.py
+++ after/angular_model.py
@@ -351,8 +351,12 @@
         values = np.sum(physical[list(block)],axis=0)
         if initial:
             nucleus = np.maximum(nucleus,abs(values-initial)/initial)
-        elif np.any(values != 0):
+        elif not model.oracle and np.any(values != 0):
             raise ArithmeticError('ZERO_N_T_FACE_CHANGED')
+    zero_ids=list(ATOM.blocks['n'])+list(ATOM.blocks['T'])
+    zero_face_scaled_max_abs=float(np.max(abs(x[zero_ids])))
+    if model.oracle and zero_face_scaled_max_abs>64*np.finfo(float).eps:
+        raise ArithmeticError('ZERO_FACE_NUMERICAL_ROUNDOFF_LIMIT_EXCEEDED')
     r = {'eta':np.array(eta),'Y':Y,'fractions':f,'atomic_scaled':x,'photon_groups':g,
          'photon_log_counts': np.log(model.g0,where=model.g0>0,out=np.full_like(model.g0,-np.inf))[:,None]-Y[model.gx] if not model.oracle else np.log(g,where=g>0,out=np.full_like(g,-np.inf)),
          'temperature_K':Y[model.iu]/(CT*(NN+v)),'electron_per_Href':v,'photon_per_Href':photons,
@@ -362,5 +366,6 @@
          'charge_residual':(v+Y[model.irr]-Y[model.iabs]-v[0])/count_scale,
          'photon_residual':(photons+Y[model.iabs]-photons[0])/count_scale,
          'nucleus_residual':nucleus,'energy_scale_eV_per_Href':np.array(energy_scale),
-         'count_scale_per_Href':np.array(count_scale),'bprime':np.array(bps),'H':np.array(hs),'nHref':np.array(ns)}
+         'count_scale_per_Href':np.array(count_scale),'bprime':np.array(bps),'H':np.array(hs),'nHref':np.array(ns),
+         'zero_face_scaled_max_abs':np.array(zero_face_scaled_max_abs)}
     return r
--- before/run_cases.py
+++ after/run_cases.py
@@ -67,12 +67,15 @@
     minimum_fraction = float(np.min(h['fractions']))
     checks['fraction_negativity'] = minimum_fraction >= -1e-10
     checks['temperature_domain'] = bool(np.all((h['temperature_K']>=3)&(h['temperature_K']<=1e9)))
-    checks['structural_n_T_zero'] = bool(np.all(h['atomic_scaled'][[0,5,6]]==0))
+    zero_limit=64*np.finfo(float).eps if model.oracle else 0.
+    zero_max=float(h['zero_face_scaled_max_abs'])
+    checks['zero_face_numerical_bound' if model.oracle else 'structural_n_T_exact_zero'] = zero_max<=zero_limit
     # Photon sign is observed, including the direct oracle's possible tiny
     # negatives; the optical system reconstructs nonnegative counts.
     return {'checks':checks,'all_pass':all(checks.values()),'maxima':maximum,
             'limits':limits,'minimum_fraction':minimum_fraction,
             'minimum_photon':float(np.min(h['photon_groups'])),
+            'zero_face_scaled_max_abs':zero_max,'zero_face_scaled_limit':zero_limit,
             'temperature_range_K':[float(np.min(h['temperature_K'])),float(np.max(h['temperature_K']))],
             'energy_denominator_eV_per_Href':float(h['energy_scale_eV_per_Href']),
             'count_denominator_per_Href':float(h['count_scale_per_Href'])}
@@ -190,16 +193,49 @@
         raise RuntimeError(f'TRAJECTORY_ACCEPTANCE_FAILURE: {name}')
 
 
+def finalize_saved_oracle():
+    name,model,tight=make(4)
+    path=RESULTS/f'{name}.json'
+    metadata=json.loads(path.read_text())
+    assert metadata['status']=='FAILED'
+    for p in [path,RESULTS/f'{name}_partial.json',RESULTS/f'{name}_partial.npz']:
+        backup=p.with_name(p.stem+'_attempt1'+p.suffix)
+        if backup.exists():
+            raise RuntimeError('ORIGINAL_ORACLE_ATTEMPT_ALREADY_PRESERVED')
+        shutil.copyfile(p,backup)
+    with np.load(RESULTS/f'{name}_partial.npz',allow_pickle=False) as d:
+        eta,Y=d['sample_eta'].copy(),d['sample_Y'].copy()
+        accepted_t,accepted_Y=d['accepted_eta'].copy(),d['accepted_Y'].copy()
+    assert accepted_t[-1]==END and np.isfinite(Y).all()
+    model.segment=None
+    h=model.observables(eta,Y)
+    h['accepted_eta'],h['accepted_Y']=accepted_t,accepted_Y
+    h['support_boundaries']=np.array(model.boundaries())
+    np.savez_compressed(RESULTS/f'{name}.npz',**h)
+    metadata['validation']=validate_history(h,model)
+    metadata['status']='COMPLETED' if metadata['validation']['all_pass'] else 'COMPLETED_WITH_ACCEPTANCE_FAILURE'
+    metadata['summary_only_repair']={'raw_states_changed':False,'IVPs_replayed':0,
+        'zero_face_scaled_tolerance':64*np.finfo(float).eps,
+        'original_failure_record':name+'_attempt1.json'}
+    dump(path,metadata)
+    print(json.dumps({'case':name,'summary_only_repair':True,'validation':metadata['validation']}),flush=True)
+    if not metadata['validation']['all_pass']:
+        raise RuntimeError('ORACLE_SUMMARY_ACCEPTANCE_FAILURE')
+
+
 def main():
     parser=argparse.ArgumentParser()
     parser.add_argument('--cases',type=int,nargs='*',default=[])
     parser.add_argument('--checks',action='store_true')
     parser.add_argument('--repair-regression',action='store_true')
     parser.add_argument('--resume-case1',action='store_true')
+    parser.add_argument('--finalize-oracle-saved',action='store_true')
     args=parser.parse_args()
     RESULTS.mkdir(exist_ok=True)
     if args.repair_regression:
         repair_regression()
+    if args.finalize_oracle_saved:
+        finalize_saved_oracle()
     dump(RESULTS/'environment.json',{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
          'threads':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},
          'requested_executor':'gpt-6.1-sol/high','observed_executor':'runtime model identity unavailable',
```

The initial summary-only invocation completed raw NPZ summary generation but encountered a NumPy boolean JSON serialization error before any new IVP. The scalar numerical-bound comparison is now explicitly converted with `bool(...)`. Existing identical original backups are reused. This changes serialization only; it does not modify raw states or the numerical tolerance. Original batch3 logs and its whole-child CPU2.223165s/wall2.350811326s remain in the cumulative budget.
