import sys,pathlib,json,csv,math,hashlib,shutil
R=pathlib.Path(__file__).parent
sys.path.insert(0,str(R/'E11/BASS_HE_E11_OBSERVER_ALIAS_20261009_v1'))
from e11.verify_telemetry import verify
from execute import write
scope=sys.argv[1];steps=2 if scope=='pilot' else 384
results={}
for mode in ('OFF','KF','GM'):
 d=R/scope/mode
 # Preserve raw k0 initialized Trace; the supplied consumer expects only accepted k>0.
 # Derived view changes stage input only, never owner source or measured outputs.
 stages=list(csv.DictReader((d/'OWNER_ACCEPTED_STAGES.csv').open()))
 sentinel=[s for s in stages if int(s['step'])==0]
 assert len(sentinel)==3 and [int(s['stage']) for s in sentinel]==[0,1,2]
 for s in sentinel:
  assert int(s['count'])==0 and float(s['min'])==math.inf and float(s['max'])==0
  assert int(s['any'])==0 and int(s['all'])==65535 and int(s['continuity_checks'])==0 and float(s['continuity_max_relative'])==0
 view=R/'verifier_views'/scope/mode;view.mkdir(parents=True,exist_ok=False)
 for name in ('OWNER_INTERNAL_5.csv','READY.json'):shutil.copy2(d/name,view/name)
 with (view/'OWNER_ACCEPTED_STAGES.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(stages[0]));w.writeheader();w.writerows(s for s in stages if int(s['step'])>0)
 q=verify(view,R/'E7',mode,steps)
 q['consumer_input']='derived accepted-k>0 view; raw unchanged; raw supplied verifier failed k0 sentinel'
 q['k0_initialized_sentinel_rows_preserved']=3
 oldfiles={}
 for name in ('OWNER_NATIVE_41.csv','OWNER_SELECTED_RCT.csv','STEPS.csv'):
  b=(d/name).read_bytes();old=(R/'E10'/('smoke/'+mode if steps==2 else 'full_'+mode)/name).read_bytes()
  assert b==old,(mode,name,'E10_BYTE_PARITY_FAIL')
  oldfiles[name]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'E10_byte_equal':True}
 stages=[s for s in stages if int(s['step'])>0]
 assert len(stages)==3*steps
 for k in range(1,steps+1):assert [int(s['stage']) for s in stages if int(s['step'])==k]==[0,1,2]
 for s in stages:
  assert all(math.isfinite(float(s[k])) for k in ('min','max','continuity_max_relative'))
  assert int(s['count'])>0 and int(s['continuity_checks'])>0
  assert 0<float(s['min'])<=float(s['max'])
  assert all(0<=int(s[k])<=65535 for k in ('any','all'))
  assert int(s['all']) & ~int(s['any'])==0
 traces=list(csv.DictReader((d/'STEPS.csv').open()))
 gates={k:max(float(t[k]) for t in traces) for k in ('norm','Nratio','Eratio')}
 assert all(v<=1 and math.isfinite(v) for v in gates.values())
 q.update({'old_output_bytes':oldfiles,'internal_clock_bit_checks':steps+1,'stage_finite_schema':'PASS','original_gates':gates,'stage_independent_numerical_verdict':'NOT_EVALUATED','true_error_certificate':False})
 results[mode]=q
write(scope.upper()+'_VALIDATION.json',results)
print(json.dumps(results,indent=2))
