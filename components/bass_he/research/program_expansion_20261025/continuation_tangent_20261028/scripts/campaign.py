"""One construction, then eight controls and saved-certificate reading."""
import argparse
import json
import os
from pathlib import Path
import sys
import traceback
import unittest

UNIT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(UNIT/'src'),str(UNIT/'tests')]

def atomic(path,value):
    temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('w') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    temp.replace(path)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--saved',required=True,type=Path);parser.add_argument('--official',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    from tangent13 import construct
    from verify_certificate import verify
    import test_tangent13 as tests
    atomic(args.output/'PARTIAL_PROGRESS.json',{'status':'running','stage':'construction','construction_count':1})
    try:
        result=construct(args.saved,args.official)
        atomic(args.output/'SAVED_PLOT_DATA.json',result)
        atomic(args.output/'CERTIFICATE_READER.json',verify(result,args.saved,args.official))
        tests.SAVED=args.saved;tests.OFFICIAL=args.official;tests.RESULT=result
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.Controls)
        run=unittest.TextTestRunner(verbosity=2).run(suite)
        report={'status':'PASS' if run.wasSuccessful() else 'FAIL','methods_run':run.testsRun,'control_groups':8,'failures':[{'test':str(t),'traceback':msg} for t,msg in run.failures],'errors':[{'test':str(t),'traceback':msg} for t,msg in run.errors],'skipped':run.skipped,'construction_count':1,'predecessor_campaign_reruns':0}
        atomic(args.output/'TEST_REPORT.json',report)
        atomic(args.output/'PARTIAL_PROGRESS.json',{'status':'completed' if run.wasSuccessful() else 'failed','stage':'controls','methods_run':run.testsRun})
        return 0 if run.wasSuccessful() else 1
    except Exception as exc:
        atomic(args.output/'FAILURE.json',{'status':'FAIL','exception':type(exc).__name__,'reason':str(exc),'traceback':traceback.format_exc()})
        traceback.print_exc();return 1

if __name__=='__main__':sys.exit(main())
