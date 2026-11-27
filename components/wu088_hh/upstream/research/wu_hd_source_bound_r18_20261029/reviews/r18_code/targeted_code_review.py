"""Distinct-author targeted review; independent source oracle was frozen first."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
PDF=Path('/workspace/scratch/5f3e9bf5a6d0/source_research/GL2022_CSIC_supplement.pdf')
ORACLE=Path('/workspace/scratch/5f3e9bf5a6d0/review_r18_source/INDEPENDENT_SOURCE_REVIEW.json')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--module',type=Path,default=ROOT/'frozen_native_rates_s05.py')
    parser.add_argument('--output',type=Path,default=ROOT/'S05_TARGETED_REVIEW.json')
    args=parser.parse_args()
    b=args.module.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    spec=importlib.util.spec_from_file_location('r18_distinct_code_review',args.module)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    oracle=json.loads(ORACLE.read_text())
    t0,c0=time.monotonic(),time.process_time()
    checks=[];findings=[]
    def check(name,fn):
        fn();checks.append({'name':name,'status':'PASS'})
    def equal(a,b):
        assert a==b,(a,b)
    def rejected(fn,kind):
        try:fn()
        except kind:return
        raise AssertionError('expected '+kind.__name__)
    grid=m.load_native_grid(PDF)
    for cell in oracle['cells']:
        t=cell['temperature_K'];got=grid.lookup(t)
        raw=cell['printed_value_cm3_per_s_exact'];si=cell['printed_value_m3_per_s_exact']
        check('independent_source_T'+str(t),lambda got=got,cell=cell,raw=raw,si=si:
              equal((got.original_token,got.nominal_cm3_s,got.nominal_m3_s),
                    (cell['source_token'],F(int(raw['numerator']),int(raw['denominator'])),
                     F(int(si['numerator']),int(si['denominator'])))))
    for t in [5,14,205,295,3000,3006,True,15.0,F(15),'15']:
        check('unsupported_temperature_'+repr(t),lambda t=t:rejected(lambda:grid.lookup(t),m.SourceContractError))
    for kw in [{'initial_v':1},{'initial_j':7},{'initial_j':8},{'product_v':1},
               {'product_j':0},{'method':'TIQM'},{'method':'EQM'},{'method':'SACM'},
               {'initial_v':False}]:
        check('state_method_'+repr(kw),lambda kw=kw:rejected(lambda:grid.lookup(15,**kw),m.SourceContractError))
    data=grid.as_json()
    check('source_binding',lambda:equal(data['source']['pdf_sha256'],oracle['source']['sha256']))
    check('raw_spin_not_preapplied',lambda:equal(data['reaction']['raw_thermal_spin_factor_applied'],False))
    check('odd_spin_once_metadata',lambda:equal(data['reaction']['thermal_odd_spin_factor_if_used'],{'numerator':'3','denominator':'4'}))
    check('source_uncertainty_unresolved',lambda:equal(data['precision']['true_rate_enclosure'],None))
    for token in ['3.99(-14)','3.99(1.4)','-3.99(14)','nan','0.00(00)','x'*33]:
        check('malformed_token_'+token,lambda token=token:rejected(lambda:m.decode_printed_token(token),m.SourceContractError))
    for timeout in [0,-1,31,float('inf'),float('nan')]:
        check('timeout_guard_'+str(timeout),lambda timeout=timeout:rejected(lambda:m.load_native_grid(PDF,timeout_seconds=timeout),m.SourceContractError))
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp);bad=tmp/'changed.pdf';raw=bytearray(PDF.read_bytes());raw[-200]^=1;bad.write_bytes(raw)
        check('same_size_corrupt_pdf',lambda:rejected(lambda:m.load_native_grid(bad),m.SourceContractError))
        out=tmp/'out.json'
        run=subprocess.run([sys.executable,str(args.module),'--source-pdf',str(PDF),'--output',str(out)],capture_output=True,text=True)
        check('cli_first_write',lambda:equal(run.returncode,0))
        prior=out.read_bytes()
        again=subprocess.run([sys.executable,str(args.module),'--source-pdf',str(PDF),'--output',str(out)],capture_output=True,text=True)
        check('cli_exclusive_output',lambda:equal((again.returncode,'FileExistsError' in again.stderr,out.read_bytes()==prior),(2,True,True)))
        unsupported=subprocess.run([sys.executable,str(args.module),'--source-pdf',str(PDF),'--output',str(tmp/'wrongT.json'),'--temperature-K','205'],capture_output=True,text=True)
        check('cli_bad_domain_classification',lambda:equal((unsupported.returncode,'SourceContractError' in unsupported.stderr,(tmp/'wrongT.json').exists()),(2,True,False)))
    with patch.object(m.subprocess,'run',side_effect=FileNotFoundError('pdftotext absent')):
        check('extractor_missing_classification',lambda:rejected(lambda:m.load_native_grid(PDF),m.ExtractionExecutionError))
    with patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],17,b'',b'failed')):
        check('extractor_nonzero_classification',lambda:rejected(lambda:m.load_native_grid(PDF),m.ExtractionExecutionError))
    with patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0,b'\xff',b'')):
        check('extractor_encoding_classification',lambda:rejected(lambda:m.load_native_grid(PDF),m.ExtractionExecutionError))
    with patch.object(m.subprocess,'run',side_effect=subprocess.TimeoutExpired('pdftotext',1)):
        check('extractor_timeout_classification',lambda:rejected(lambda:m.load_native_grid(PDF),m.ExtractionExecutionError))
    try:
        fake=m.NativeGrid(tuple(m.PrintedCell(t,'1.00(0)',F(1)) for t in m.TEMPERATURES_K),
                          m.PDF_SHA256,'fabricated-not-a-sha')
        result=fake.as_json()
        assert fake.lookup(15).nominal_cm3_s==1
    except (m.SourceContractError,TypeError,ValueError):
        checks.append({'name':'unattested_constructor_rejection','status':'PASS'})
    else:
        findings.append({'id':'R18-C9-F01','severity':'P2','class':'implementation/source-provenance binding',
                         'target':'PrintedCell and NativeGrid constructors; NativeGrid.lookup/as_json',
                         'observed':'Arbitrary synthetic cells passed public constructor and emitted SOURCE_NATIVE_PRINTED_NOMINAL with original PDF_SHA and fabricated extracted-page hash',
                         'reproduction':'NativeGrid(tuple(PrintedCell(t,"1.00(0)",Fraction(1)) for t in TEMPERATURES_K),PDF_SHA256,"fabricated-not-a-sha").as_json()',
                         'impact':'public library API can serialize source-qualified labels for values not in the source; actual loader CLI path remains correct',
                         'minimal_fix':'validated loader issuance or exact source-bound immutable representation; reject unattested construction before lookup/as_json; verify count/order/token/value/source digest coupling'})
    result={'schema':'WU_R18_DISTINCT_AUTHOR_CODE_REVIEW_V1','reviewer':'/root/r17b_independent_review',
            'scope':'source-bound API, independent printed-row conversion, domain guards and exclusive CLI; no physical uncertainty or consumer admission',
            'module':str(args.module),'baseline_commit':'8fd7111a1c56dbfeca10893231b16c5ea65543fc',
            'reviewed_delta_commit':'NOT_BOUND_IN_THIS_LOCAL_RECEIPT',
            'git_blob':blob,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),
            'independent_oracle':str(ORACLE),'checks':checks,'passed_checks':len(checks),
            'findings':findings,'open_material_findings':len(findings),
            'verdict':'REQUIRES_SCOPED_CORRECTION' if findings else 'PASS_SCOPED',
            'cpu_seconds':time.process_time()-c0,'wall_seconds':time.monotonic()-t0,
            'physical_admission':False,'old_suite_replay':False,'exit_code':0}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'verdict':result['verdict'],'checks':len(checks),'findings':findings,
                      'cpu_seconds':result['cpu_seconds'],'git_blob':blob},indent=2))

if __name__=='__main__':main()
