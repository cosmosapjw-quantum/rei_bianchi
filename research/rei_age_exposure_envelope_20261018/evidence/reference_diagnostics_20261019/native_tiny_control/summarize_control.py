from pathlib import Path
import sys,json,shutil
import numpy as np
root=Path('/workspace/scratch/36ed695112a9/rei_bianchi/research/rei_age_exposure_envelope_20261018');sys.path.insert(0,str(root/'src'))
from run_refinement import read_json,save,sha
from source_jump_diagnosis import diagnose_jumps
out=root/'evidence/reference_diagnostics_20261019/native_tiny_control'
a=out/'off/data';b=out/'on/data'
ra=read_json(a/'solver_return.json');rb=read_json(b/'solver_return.json')
assert ra['status']==rb['status']=='SCOPED_NUMERICAL_EXECUTION_COMPLETE'
common_files=sorted(p.name for p in a.iterdir() if p.is_file() and p.name!='solver_return.json')
byte_matches={name:(a/name).read_bytes()==(b/name).read_bytes() for name in common_files}
assert all(byte_matches.values())
keys=['max_rhs','max_wall_s','rpc_mode','error_norm','error_control_identity','status','failure','q','tight','birth_panels','n_mu','source_subdivisions','transport_cells','calls','errors','intervals','server_exit']
return_matches={k:ra[k]==rb[k] for k in keys};assert all(return_matches.values())
coordinate_records=[dict(file=name,shape=list(np.load(a/name).shape),sha256=sha(a/name),uint64_bits_equal=bool(np.array_equal(np.load(a/name).view(np.uint64),np.load(b/name).view(np.uint64)))) for name in common_files if name.endswith('.npy')]
jump=diagnose_jumps(read_json(b/'setup.json'),read_json(b/'source_jumps.json'));save(out/'SOURCE_JUMP_DIAGNOSIS.json',jump)
assert jump['coverage']=='COMPLETE' and jump['available_unique_births']==2
assert all(all(r[k] for k in ['unchanged_nonbirth_coordinates_bits','unchanged_gas_coordinate_bits','unchanged_ledger_coordinate_bits']) for r in jump['records'])
telemetry=read_json(b/'reference_diagnostics.json');attempts=telemetry['attempts']
estimates=[e for attempt in attempts for e in attempt['estimates']]
retained=sum(a['final_trajectory_accepted_estimates'] for a in attempts)
steps=sum(a['solver_steps'] for a in rb['intervals']);assert retained==steps
assert all(a['final_trajectory_accepted_estimates']==0 for a in attempts if a['discarded'])
assert all(e['block_max_diagnostic']==e['error_norm_actual'] for e in estimates)
summary=dict(schema='rei.reference.native_tiny_control.v1',status='PASS_SCOPED_OBSERVER_EQUIVALENCE',config=read_json(out/'CONFIG.json'),receipts={m:read_json(out/m/'RECEIPT.json') for m in ['off','on']},common_output_byte_equality=byte_matches,solver_return_exact_fields=return_matches,accepted_coordinate_snapshots=coordinate_records,accepted_x_equal=ra['intervals']==rb['intervals'],accepted_storage_scope='All saved accepted interval-endpoint x values and whole-state y snapshots compare exactly; original solver does not persist every internal adaptive-step x/y, so no full internal-step array byte comparison is claimed.',rhs=dict(calls_off=ra['calls'],calls_on=rb['calls'],errors_equal=True,byte_stream='NOT_RECORDED; existing native wrapper has no byte-stream recording; deterministic RPC fixture separately passed exact scheduled RHS-byte comparison.'),telemetry=dict(attempt_count=len(attempts),discarded_attempts=sum(a['discarded'] for a in attempts),retained_attempts=sum(a['retained'] for a in attempts),estimator_calls=len(estimates),embedded_rejected_estimates=sum(not e['error_accept'] for e in estimates),retained_accepted_estimates=retained,solver_steps=steps,discarded_attempt_semantics='Final-trajectory accepted count is zero for discarded interval attempts; this actual run had no rollback. Manufactured deterministic fixture independently exercised one rollback with local accepted estimates excluded.',all_diagnostic_max_equal_actual_return=True),source_jumps=dict(coverage=jump['coverage'],births=jump['available_unique_births'],exact_stored_term_delta=[r['delta_photon_invariant'] for r in jump['records']],unchanged_coordinate_bits=True),original_final_ledgers=read_json(a/'ledgers.json'),scientific_scope='Passive observer equivalence for this single tiny q0 birth2 native control only. Does not establish age convergence or RMS dilution causality.',age32='NOT_RUN',age64='NOT_RERUN',NCP='NOT_RUN',PRODUCTION_SCIENTIFIC_ADMISSION='NOT_ISSUED')
save(out/'RESULT.json',summary)
shutil.copyfile('/tmp/run_tiny_reference_control.py',out/'run_control.py')
shutil.copyfile('/tmp/summarize_tiny_reference_control.py',out/'summarize_control.py')
p=root/'evidence/reference_diagnostics_20261019/IMPLEMENTATION.json';impl=read_json(p)
impl['native_tiny_control']=dict(status=summary['status'],result='evidence/reference_diagnostics_20261019/native_tiny_control/RESULT.json',off_exit=0,on_exit=0,rhs_calls_each=ra['calls'],source_jump_coverage='2/2',code_connection_fix='NONE')
save(p,impl)
print(json.dumps(dict(status=summary['status'],common_output_byte_equality=byte_matches,telemetry=summary['telemetry'],source_jumps=summary['source_jumps']),indent=2))
