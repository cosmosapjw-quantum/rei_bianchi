"""Read-only pinned primary-source symbol/signature checks; no native build."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile

PIN='108ab51a4dd33918ff3308f0c63a63616ae30a2c174d50c9188676e85011346f'


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-archive',required=True,type=Path)
    p.add_argument('--reference-dir',required=True,type=Path)
    args=p.parse_args()
    actual=hashlib.sha256(args.source_archive.read_bytes()).hexdigest()
    if actual!=PIN: raise SystemExit('FLINT3.4 source archive hash mismatch')
    relevant=['src/acb_calc.h','src/acb.h','src/arb.h','src/mag.h','src/arb_calc.h',
              'src/flint.h.in','src/fmpq.h','src/acb_calc/integrate.c',
              'src/acb_calc/integrate_gl_auto_deg.c','doc/source/acb_calc.rst']
    raw={}
    with tarfile.open(args.source_archive) as tf:
        members=tf.getmembers()
        for suffix in relevant:
            hits=[m for m in members if m.name.endswith('/'+suffix)]
            if len(hits)!=1: raise SystemExit('nonunique primary member '+suffix)
            raw[suffix]=tf.extractfile(hits[0]).read()
    for rel in ['src/acb_calc.h','src/acb.h','src/arb.h','doc/source/acb_calc.rst']:
        if (args.reference_dir/rel).read_bytes()!=raw[rel]:
            raise SystemExit('staged primary reference drift: '+rel)
    here=Path(__file__).parent
    names=['petras_host.hpp','petras_host.cpp','native_petras_synthetic.cpp']
    sources={n:(here/n).read_text() for n in names}
    symbols=sorted(set(re.findall(r'\b((?:acb|arb|mag|flint|fmpq)_[A-Za-z0-9_]+)\s*\(', '\n'.join(sources.values()))))
    headers='\n'.join(b.decode() for name,b in raw.items() if name.endswith(('.h','.h.in')))
    missing=[s for s in symbols if not re.search(r'\b'+s+r'\s*\(',headers)]
    calc=' '.join(raw['src/acb_calc.h'].decode().split())
    signature='acb_calc_integrate(acb_t res, acb_calc_func_t f, void * param, const acb_t a, const acb_t b, slong goal, const mag_t tol, const acb_calc_integrate_opt_t options, slong prec);'
    signature_ok=signature in calc
    report={'schema':'WU088_G6_PETRAS_PINNED_API_STATIC_V1','FLINT_version':'3.4.0',
        'source_archive_sha256':PIN,'header_symbols':symbols,'symbols_missing':missing,
        'acb_calc_integrate_signature_match':signature_ok,
        'primary_member_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in raw.items()},
        'draft_source_sha256':{n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in names},
        'runtime_compiler_verified':False,'native_builds':0,'native_runtime_tests':0,
        'classification':'STATIC_API_NAMES_SIGNATURE_AND_SOURCE_IDENTITY_ONLY',
        'notes':['FLINT depth_limit is maximum queued subinterval count, not local bisection depth',
                 'eval_limit is documented as approximate; wrapper strictly caps evaluator dispatch',
                 'callback return code is reserved; errors are carried by nonfinite output',
                 'FLINT3.4 passes requested prec to callback; higher wp is used for node precomputation'],
        'passed':not missing and signature_ok}
    print(json.dumps(report,indent=2))
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__': main()
