#!/usr/bin/env python3
import pathlib,subprocess,json,hashlib,time
r=pathlib.Path(__file__).resolve().parent;s=r/'src/ledger_sidecar.rs';base=s.read_text();(r/'evidence/PRE_MUTANT_GREEN_SOURCE.rs').write_text(base)
mutants=[
 ('generation','generation.to_string(),','"generation-omitted".into(),','generation_is_part_of_occurrence_even_same_attempt'),
 ('attempt','self.serial.to_string()','"0".to_string()','global_identity_replay_coefficients_zero_and_species'),
 ('coefficient','if b.coefficient != wide_key(c.coefficient)','if false && b.coefficient != wide_key(c.coefficient)','global_identity_replay_coefficients_zero_and_species'),
 ('mapping','Self::A(s) => 7 + s.index()','Self::A(s) => 10 + s.index()','dimensional_mapping_named_terms_dt_epsilon_once'),
 ('coverage','if leaves != self.leaves || a != self.a || b != self.b || self.state_out.is_empty()','if a != self.a || b != self.b || self.state_out.is_empty()','leaf_coverage_historical_fresh_and_no_double_charge'),
 ('half_order','if h[0].role != Stage::Half1','if false && h[0].role != Stage::Half1','accepted_half_order_full_exclusion_wrong_dt_and_missing_add'),
 ('rollback','let mut candidate = self.snapshot.clone();','self.snapshot.state = p.state_out.clone();\n        let mut candidate = self.snapshot.clone();','atomic_rollback_all_objects_disk_gate_and_burned_attempts'),
 ('history_caps','let mut candidate = self.snapshot.clone();','let mut candidate = self.snapshot.clone();\n        candidate.ledger=Ledger::default();','original_caps_cumulative_history_and_four_increment_limit'),
 ('readout','if export {','if false && export {','performed_export_only_positive_tail_zero_and_overflow'),
 ('witness','candidate.witnesses.push(WitnessBundle {','candidate.witnesses.clear();\n        if false {candidate.witnesses.push(WitnessBundle {','durable_attempts_restart_branch_and_stale_snapshot'),
 ('hold','Err(HOLD.into())','Ok(())','unknowns_hold_even_complete_bookkeeping_and_source_context_errors'),
 ('native_accept','let accepted = trial.accept().map_err(err)?;','let mut trial=trial;trial.legacy.error_norm=0.;let accepted = trial.accept().map_err(err)?;','native_acceptance_boundary_without_rhs_and_generation_witness'),
]
result=[]
def run(name,as_mib,command):
 return subprocess.run(['python',str(r/'run_limited.py'),'--core','0','--as-mib',str(as_mib),'--cpu-slice','8','--wall-slice','12',name,'--',*command],capture_output=True,text=True)
try:
 for name,before,after,test in mutants:
  prior=[json.loads(p.read_text())for p in(r/'results').glob('*.json')]
  if sum(p['wall_s']for p in prior)+15+14>=150 or sum(p['cpu_s']for p in prior)+10+9>=90:raise RuntimeError('reserved aggregate budget boundary; stop')
  assert base.count(before)==1,(name,base.count(before))
  mutated=base.replace(before,after)
  if name=='half_order':
   # Disable the complete guard, not only its first disjunct.
   mutated=mutated.replace('if false && h[0].role != Stage::Half1','if false && (h[0].role != Stage::Half1').replace('|| h[0].point >= h[1].point\n    {','|| h[0].point >= h[1].point)\n    {')
  if name=='witness':mutated=mutated.replace('native_receipt: p.native_receipt.clone(),\n        });','native_receipt: p.native_receipt.clone(),\n        });}')
  s.write_text(mutated);(r/f'evidence/RED_{name}.rs').write_text(mutated)
  build=run(f'red-{name}-build',2048,['cargo','test','--offline','--manifest-path',str(r/'Cargo.toml'),'--test','ledger_sidecar','--no-run'])
  assert build.returncode==0,(name,'build failure is not RED',build.stdout,build.stderr)
  red=run(f'red-{name}',512,['python',str(r/'run_control.py'),test,'--exact','--test-threads=1','--nocapture'])
  stderr=(r/f'logs/red-{name}.stderr').read_text();stdout=(r/f'logs/red-{name}.stdout').read_text()
  assert red.returncode==101 and 'assertion' in stderr and 'FAILED' in stdout,(name,'not assertion RED',red.returncode,stderr,stdout)
  result.append({'name':name,'test':test,'source_sha256':hashlib.sha256(mutated.encode()).hexdigest(),'compiled':True,'assertion_RED':True,'exit':101});(r/'evidence/MUTANTS.json').write_text(json.dumps(result,indent=2));print(name+' assertion RED',flush=True)
finally:s.write_text(base)
