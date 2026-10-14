"""Read only completed levels while the one producer continues later levels."""
import json,time,hashlib,importlib.util,datetime
from pathlib import Path
P=Path('.cuh/fastest-track/REI-F05');run=Path('runs/rei_fastest_v1/first_interval')
s=importlib.util.spec_from_file_location('v2',P/'verify_candidate_v2.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
s=importlib.util.spec_from_file_location('fast',P/'verify_whole_fast.py');fast=importlib.util.module_from_spec(s);s.loader.exec_module(fast)
fingerprints=json.loads((P/'final-inputs.json').read_text());assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in fingerprints.items())
for f,h in v.manifest['source_identity'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
class CompleteLevelPath:
    def __init__(self,path):self.path=path
    def __truediv__(self,name):return CompleteLevelPath(self.path/name)
    def read_text(self):
        last=0.
        while True:
            if self.path.exists():
                raw=self.path.read_text();data=json.loads(raw)
                if data['finished'] is True:return raw
            runtime=json.loads((P/'campaign-runtime.json').read_text())
            if runtime['state']=='PROCESS_FAILED':raise RuntimeError('Producer failed; no whole-history admission')
            if runtime['state']=='PROCESS_COMPLETED_PENDING_VALIDATION':raise RuntimeError('Missing finished summary after producer exit')
            if time.monotonic()-last>=60:print(json.dumps({'waiting_for_finished_level':str(self.path)}),flush=True);last=time.monotonic()
            time.sleep(.5)
    def open(self):return self.path.open()
start=time.monotonic();stats=fast.install_cache(v);result=v.validate_run(CompleteLevelPath(run),False)
assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in fingerprints.items()),'FINAL_VALIDATOR_IDENTITY_CHANGED'
result['validation_expression_reuse']=stats;result['validation_wall_s']=time.monotonic()-start;result['completed_level_pipeline']=True;result['validated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(run/'checker_receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
