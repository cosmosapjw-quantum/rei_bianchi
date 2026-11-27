"""One primary campaign: controls, actual tables, and independent exact reader."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]

def save(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.link(tmp,path);tmp.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--saved-json',required=True);parser.add_argument('--report-json',required=True);parser.add_argument('--source',required=True);parser.add_argument('--test-name',action='append',default=[]);args=parser.parse_args()
    import exfor_aperture as E
    import test_exfor_aperture as T
    report={'unit':'HE-EXP-EXFOR-11','status':'RUNNING','science_campaigns':1,'requested_executor':'gpt-6.1-sol','observed_executor_model':None,'observed_executor_reason':'runtime model identity not exposed','checks':[]}
    try:
        suite=unittest.defaultTestLoader.loadTestsFromNames(args.test_name,T) if args.test_name else unittest.defaultTestLoader.loadTestsFromTestCase(T.Controls)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        report.update(controls_run=result.testsRun,control_failures=[(str(t),s) for t,s in result.failures],control_errors=[(str(t),s) for t,s in result.errors])
        # Preserve controls even if one fails; actual scoped cases are independent obligations.
        if not args.test_name:
            data=E.encode(E.campaign(args.source));save(args.saved_json,data)
            reread=json.loads(Path(args.saved_json).read_text());report['certificate_vertices_checked']=T.verify_saved(reread)
            report['cases']=[{'energy':c['energy'],'degree':c['degree'],'endpoint_zero':c['endpoint_zero'],'inner_vertices':c['polytopes']['inner']['unique_vertices'],'outer_vertices':c['polytopes']['outer']['unique_vertices']} for c in reread['cases']]
        else:
            report['science_campaigns']=0
            report['targeted_tests']=args.test_name
        report['status']='PASS' if result.wasSuccessful() else 'FAIL'
    except Exception:
        report['status']='FAIL';report['exception']=traceback.format_exc();traceback.print_exc()
    finally:save(args.report_json,report)
    print(json.dumps(report,indent=2));sys.exit(0 if report['status']=='PASS' else 1)
