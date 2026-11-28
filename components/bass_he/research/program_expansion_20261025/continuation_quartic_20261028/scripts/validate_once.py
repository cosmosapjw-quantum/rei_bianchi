"""One primary QUARTIC12 campaign, exact progress and independent saved reader."""
import argparse
import json
import os
from pathlib import Path
import sys
import traceback
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]

def save(path,value,replace=False):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    if replace:os.replace(tmp,path)
    else:os.link(tmp,path);tmp.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--saved-json',required=True);p.add_argument('--report-json',required=True);p.add_argument('--source',required=True);p.add_argument('--prior-saved',required=True);p.add_argument('--test-name',action='append',default=[]);a=p.parse_args()
    import quartic_aperture as Q
    import test_quartic_aperture as T
    report={'unit':'HE-EXP-QUARTIC-12','status':'RUNNING','science_campaigns':0 if a.test_name else 1,'requested_executor':'gpt-6.1-sol','observed_executor_model':None,'observed_executor_reason':'runtime identity unexposed'}
    try:
        suite=unittest.defaultTestLoader.loadTestsFromNames(a.test_name,T) if a.test_name else unittest.defaultTestLoader.loadTestsFromTestCase(T.Controls)
        result=unittest.TextTestRunner(verbosity=2).run(suite);report.update(controls_run=result.testsRun,control_failures=[(str(t),s) for t,s in result.failures],control_errors=[(str(t),s) for t,s in result.errors])
        if not a.test_name:
            progress_path=Path(a.saved_json).with_name('PARTIAL_PROGRESS.json')
            def progress(data):save(progress_path,Q.encode(data),replace=True)
            data=Q.encode(Q.campaign(a.source,a.prior_saved,progress));save(a.saved_json,data)
            reread=json.loads(Path(a.saved_json).read_text());report['certificate_reader']=T.verify_saved(reread)
            report['cases']=[{'energy':c['energy'],'case':c['case'],'inner_vertices':c['polytopes']['inner']['unique_vertices'],'outer_vertices':c['polytopes']['outer']['unique_vertices'],'outside_old_sufficient_cone_witness':None if c['inner_witness'] is None else c['inner_witness']['outside_old_sufficient_cone']} for c in reread['cases']]
        else:report['targeted_tests']=a.test_name
        report['status']='PASS' if result.wasSuccessful() else 'FAIL'
    except Exception:report['status']='FAIL';report['exception']=traceback.format_exc();traceback.print_exc()
    finally:save(a.report_json,report)
    print(json.dumps(report,indent=2));sys.exit(0 if report['status']=='PASS' else 1)
