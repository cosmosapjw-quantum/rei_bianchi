"""Compatibility adapter to the pinned INTAKE01 bounded test runner."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2];RUNNER=ROOT.parent/'continuation_20261025/run_validation.py';EXPECTED='b0f36cb3ee2f79d4fc29fa6596be37b829d299694f3fd167bf40460a3b976e8f'
def main():
 p=argparse.ArgumentParser();p.add_argument('--repair-reason');p.add_argument('--test-name',action='append',default=[]);a=p.parse_args()
 if hashlib.sha256(RUNNER.read_bytes()).hexdigest()!=EXPECTED:raise RuntimeError('runner identity changed')
 spec=importlib.util.spec_from_file_location('state04_runner',RUNNER);r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r);r.ROOT=ROOT;r.OUT=ROOT/'evidence/validation'
 files=[Path(__file__),RUNNER,ROOT/'MODEL_CONTRACT.json',ROOT/'VALIDATION_CONTRACT.json',ROOT/'THEORY_KO.md',ROOT.parent/'continuation_event_20261027/src/reactive_event.py',ROOT.parent/'continuation_20261025/exchange/exchange_closure.py',ROOT.parent/'continuation_20261027/sources/r3_update/raw/PROVIDER_ROWS.json']+sorted((ROOT/'src').glob('*.py'))+sorted((ROOT/'tests').glob('test_*.py'))+sorted(p for p in (ROOT/'sources').rglob('*') if p.is_file())+sorted(p for p in (ROOT/'preflight').rglob('*') if p.is_file())
 ledger=r.OUT/'RESOURCE_LEDGER.json';n=len(json.loads(ledger.read_text())['attempts'])+1 if ledger.exists() else 1;dst=ROOT/'evidence'/f'TESTED_DEPENDENCIES_{n:02d}.json';manifest={'schema':'HE_PHOTON05_TESTED_DEPENDENCIES_V1','files':[{'path':str(f.relative_to(REPO)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(set(files))],'preparation_cost':'UNKNOWN_NOT_ZERO; outside test measurement'}
 if dst.exists() and json.loads(dst.read_text())!=manifest:raise RuntimeError('different existing dependency binding')
 r.save(dst,manifest);return r.run('tests',a.repair_reason,tuple(a.test_name))
if __name__=='__main__':raise SystemExit(main())
