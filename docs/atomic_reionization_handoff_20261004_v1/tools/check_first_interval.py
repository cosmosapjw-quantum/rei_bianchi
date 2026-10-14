"""Independent MPFI replay of stored static FT03 transactions; no solver calls."""
import argparse,gzip,importlib.util,json,time,hashlib
from pathlib import Path
E=Path('docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F05')
def load(name,file):
    s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class StoredPath:
    def __init__(self,path):self.path=path
    def __truediv__(self,name):return StoredPath(self.path/name)
    def read_text(self):return self.path.read_text()
    def open(self):
        if self.path.exists():return self.path.open()
        return gzip.open(str(self.path)+'.gz','rt')
def main():
    a=argparse.ArgumentParser();a.add_argument('run_dir',type=Path);a.add_argument('--receipt',required=True,type=Path);a.add_argument('--pilot',action='store_true');p=a.parse_args()
    v=load('history_checker',E/'verify_candidate_v2.py');fast=load('expression_reuse',E/'verify_whole_fast.py')
    for f,h in v.manifest['source_identity'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,'IMMUTABLE_SOURCE_MISMATCH: '+f
    start=time.monotonic();stats=fast.install_cache(v);result=v.validate_run(StoredPath(p.run_dir),p.pilot)
    result['validation_expression_reuse']=stats;result['validation_wall_s']=time.monotonic()-start;result['production_evaluator_called']=False
    p.receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
