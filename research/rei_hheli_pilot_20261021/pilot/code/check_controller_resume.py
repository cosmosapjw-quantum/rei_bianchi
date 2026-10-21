"""Targeted no-IVP regression for an interrupted attempt; no scientific runs."""
from pathlib import Path
import hashlib,json,tempfile
from run_pilot import admission_guard,resolve_manifest,ROOT

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='hheli-controller-') as directory:
 base=Path(directory);p=base/'cases/interrupted';p.mkdir(parents=True);attempt=p/'ATTEMPT.json';attempt.write_text('{"status":"LAUNCHED","unknown_cpu_debit":"PRESERVE_UNRESOLVED"}\n');before=sha(attempt)
 try:admission_guard(base)
 except RuntimeError as exc:assert 'UNRESOLVED_ATTEMPT_NO_RESULT' in str(exc);error=str(exc)
 else:raise AssertionError('Incomplete attempt was silently admitted')
 assert before==sha(attempt) and not (p/'RESULT.json').exists()
 report={'status':'PASS_TARGETED_NO_IVP_RESUME_GUARD','new_IVPs':0,'unresolved_attempt_preserved':True,'unknown_cpu_debit_preserved':True,'error':error,'attempt_sha256':before}
(ROOT/'evidence/controller_repair/TEST_RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
