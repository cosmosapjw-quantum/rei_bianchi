"""Host-only full-campaign validation; invokes no production numerical solver."""
import importlib.util,json,argparse
from pathlib import Path

def main():
    a=argparse.ArgumentParser();a.add_argument('run_dir',type=Path);a.add_argument('--receipt',required=True,type=Path);p=a.parse_args()
    source=Path('.cuh/fastest-track/REI-F05/verify_candidate_v2.py')
    s=importlib.util.spec_from_file_location('frozen_history_checker',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    for f,expected in m.manifest['source_identity'].items():
        assert m.hashlib.sha256(Path(f).read_bytes()).hexdigest()==expected,'SOURCE_INPUT_MISMATCH: '+f
    result=m.validate_run(p.run_dir,False)
    p.receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':
    main()
