"""One actual construction, independent saved-certificate validation, controls."""
import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path
import sys
import traceback

UNIT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(UNIT/'src'),str(UNIT/'tests')]
import endpoint14 as science
import verify_certificate
import test_endpoint14

def write(path,obj):
    tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(science.encode(obj),indent=2,sort_keys=True)+'\n');tmp.replace(path)

def validate_pin(saved_path,official_path):
    pin_path=UNIT/'evidence/EXECUTION_PIN.json'
    if not pin_path.is_file():raise ValueError('mandatory actual S05 execution pin missing')
    pin=json.loads(pin_path.read_text());repo=UNIT.parents[2]
    if pin.get('unit_id')!='HE-EXP-ENDPOINT-14' or pin.get('metadata_scope')!='POSTPUBLICATION_EXECUTION_PIN':raise ValueError('execution pin unit/scope')
    for field in ('source_commit','source_tree'):
        if not re.fullmatch(r'[0-9a-fA-F]{40}',str(pin.get(field,''))):raise ValueError('execution pin '+field)
    if pin.get('repository')!='cosmosapjw-quantum/BASS_HE' or not isinstance(pin.get('branch'),str) or not pin['branch']:raise ValueError('execution pin repository/branch')
    for field in ('files','input_sha256'):
        if not isinstance(pin.get(field),dict) or not pin[field]:raise ValueError('execution pin '+field)
        for relative,digest in pin[field].items():
            path=Path(relative)
            if path.is_absolute() or '..' in path.parts:raise ValueError('execution pin invalid relative repository path')
            if not re.fullmatch(r'[0-9a-fA-F]{64}',str(digest)):raise ValueError('execution pin invalid SHA256 '+relative)
            if not (repo/path).is_file() or hashlib.sha256((repo/path).read_bytes()).hexdigest()!=digest.lower():raise ValueError('execution pin actual hash mismatch '+relative)
    required=[UNIT/'CONTRACT.md']+[p for folder in ('src','scripts','tests') for p in (UNIT/folder).glob('*.py')]
    for path in required:
        if str(path.relative_to(repo)) not in pin['files']:raise ValueError('own source absent from execution pin '+str(path))
    for path in (saved_path,official_path):
        if str(path.resolve().relative_to(repo.resolve())) not in pin['input_sha256']:raise ValueError('actual input absent from execution pin '+str(path))
    return {'path':'evidence/EXECUTION_PIN.json','sha256':hashlib.sha256(pin_path.read_bytes()).hexdigest(),'content':pin,'all_listed_code_input_hashes_match':True}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--saved',type=Path,required=True);parser.add_argument('--official',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(exist_ok=True,parents=True)
    try:
        execution_pin=validate_pin(args.saved,args.official)
        old=science.load_inputs(args.saved,args.official)
        # Preserve predeclared outcome independently of subsequent construction success.
        candidate=science.witness(science.CANDIDATE,science.rows_from_saved(old));write(args.output/'CANDIDATE_OUTCOME.json',candidate)
        result=science.construct(old) # sole actual construction call
        result['implementation_sha256']={str(p.relative_to(UNIT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('src','scripts','tests') for p in sorted((UNIT/folder).glob('*.py'))}
        result['execution_pin']=execution_pin
        write(args.output/'SAVED_PLOT_DATA.json',result)
        saved=json.loads((args.output/'SAVED_PLOT_DATA.json').read_text())
        report=verify_certificate.verify(saved,old,args.saved,args.official,UNIT);write(args.output/'READER_REPORT.json',report)
        tests=test_endpoint14.run(saved,old,args.saved,args.official,UNIT);write(args.output/'TEST_REPORT.json',tests)
        status='PASS' if tests['status']=='PASS' and report['status']=='PASS' else 'FAIL'
        write(args.output/'FINISH.json',{'status':status,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'construction_calls':1,'requested_model':'gpt-6.1-sol','observed_runtime_model':None,'scientific_admission':'PENDING_ROOT_INDEPENDENT_REVIEW'})
        return 0 if status=='PASS' else 1
    except Exception as exc:
        write(args.output/'FINISH.json',{'status':'FAIL','error':repr(exc),'traceback':traceback.format_exc(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'automatic_retry':False,'scientific_admission':'PENDING_ROOT_CLASSIFICATION'})
        traceback.print_exc();return 1

if __name__=='__main__':sys.exit(main())
