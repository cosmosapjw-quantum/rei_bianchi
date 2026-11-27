"""R16 exact preprocessor and pinned R15 production solver bridge.

Never substitutes a mock/placeholder for the R15 full-A comparison.
"""
import argparse, hashlib, importlib.util, json, sys, traceback
from pathlib import Path
from r16_nonnegative_cubic import adapt_case_for_r15

R15_CORE_GIT_BLOB='0a95d907790cbf87207deb32c9a9ab1ae24aa3a1'

def pinned_r15_core(path):
    code=Path(path).read_bytes()
    obj=hashlib.sha1(b'blob '+str(len(code)).encode()+b'\0'+code).hexdigest()
    if obj!=R15_CORE_GIT_BLOB:
        raise RuntimeError('R15 source Git blob differs from frozen authority: '+obj)
    spec=importlib.util.spec_from_file_location('r15_pinned_core',path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--r15-core',type=Path,default=Path(__file__).resolve().parents[2]/'provider_registry_molecular_r15_20261028'/'src'/'cubic_convolution.py')
    ap.add_argument('--depth',type=int,default=256)
    ap.add_argument('--nodes',type=int,default=16384)
    args=ap.parse_args()
    if args.output.exists():raise FileExistsError('create-only output exists')
    try:
        old=json.loads(args.input.read_text(encoding='utf-8'))
        new,lineage=adapt_case_for_r15(old,args.depth,args.nodes)
        R15=pinned_r15_core(args.r15_core)
        R15.configure_r15_runtime()
        R15.validate(new)  # no assumption-only bypass
        result=R15.serializable(R15.run_case(new))
        payload={'status':'COMPUTED_CONDITIONAL_FROM_R16_EXACT_PREPROCESSING',
                 'lineage':lineage,'R15_result':result}
        code=0
    except Exception as e:
        payload={'status':'FAIL','exception_type':type(e).__name__,'message':str(e)}
        code=2
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(payload,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)
        f.write('\n')
    return code

if __name__=='__main__':raise SystemExit(main())
