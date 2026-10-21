"""Exercise actual supervisor accounting without workers or IVPs."""
import sys,time,tempfile,json
from pathlib import Path
sys.dont_write_bytecode=True
begin=time.monotonic()
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unified_pilot as u
checks={}
with tempfile.TemporaryDirectory(prefix='rei_profile_debit_') as temporary:
    out=Path(temporary);cases=[{'id':'a','config':{}},{'id':'b','config':{}}]
    for c,profile,charge,cap in [(cases[0],'ncp',7.25,60.),(cases[1],'sandbox',None,30.)]:
        record={'profile':profile,'per_case_cap_s':cap}
        if charge is not None:record['charged_wall_s']=charge
        u.atomic_json(out/'cases'/c['id']/'ATTEMPT.json',record)
    u.atomic_json(out/'controllers/one.json',{'profile':'sandbox','controller_elapsed_s':2.})
    u.atomic_json(out/'controllers/two.json',{'profile':'ncp','controller_elapsed_s':3.})
    u.plan=lambda output:{'cases':cases};u._approval=lambda path,m:{'decision':'PASS_SCOPED_EXECUTION_CONTRACT'}
    u.bind_execution_identity=lambda output:{'test':'accounting only'};u.resume_state=lambda output,c:'COMPLETED'
    u.ENTRY_STARTED=time.monotonic()
    receipt=u.run(out,'ncp',None,True,None)
    checks['all_profile_child_debits_retained']=receipt['cumulative_child_charged_wall_s']==u.OLD_CHILD+7.25+30.
    checks['unknown_charge_uses_stored_case_cap']=receipt['cumulative_child_charged_wall_s']!=u.OLD_CHILD+7.25+u.LIMITS['ncp']['case_s']
    checks['all_profile_controller_debits_retained']=receipt['previous_controller_elapsed_s']==u.OLD_CONTROLLER+5.
    checks['no_worker_actions']=receipt['unrelated_process_actions']==0 and not receipt['resource_samples']
r={'checks':checks,'pass':all(checks.values()),'elapsed_s':time.monotonic()-begin,'no_IVP_calls':True,'no_worker_launches':True,'source_sha256':u.sha(u.__file__)}
u.atomic_json(u.ROOT/'components/PROFILE_DEBIT_MECHANICAL.json',r)
print(json.dumps(r,indent=2));sys.exit(0 if r['pass'] else 1)
