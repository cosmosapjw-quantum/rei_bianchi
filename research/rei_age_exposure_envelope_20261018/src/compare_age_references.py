"""Bind same-computational-source age32/64 receipts before finite differences."""
from pathlib import Path
import argparse
import subprocess
import sys

from reference_diagnostics import COMPUTATIONAL_BASE_SHA
from run_refinement import NATIVE_SHA, read_json, save, sha


def validate_pair(left, right):
    receipts=[read_json(Path(path)/'RECEIPT.json') for path in (left,right)]
    for expected,receipt,path in zip((32,64),receipts,(left,right)):
        if receipt.get('status')!='COMPLETE':
            raise ValueError('REFERENCE_NOT_COMPLETE')
        config=receipt['config'];identity=receipt['identity']
        required=dict(kind='reference',q=0.,birth_panels=expected,n_mu=8,source_subdivisions=8,
                      transport_cells=16,common_birth_levels=[8,16,32,64],time_factor=1,
                      tight=False,rpc_mode='binary64',error_norm='block-max')
        if any(config.get(key)!=value for key,value in required.items()):
            raise ValueError('REFERENCE_AXIS_CONFIG_MISMATCH')
        if identity.get('native_sha')!=NATIVE_SHA:
            raise ValueError('REFERENCE_NATIVE_SHA_MISMATCH')
        base=identity.get('computational_base_solver_sha',identity.get('solver_sha'))
        if base!=COMPUTATIONAL_BASE_SHA:
            raise ValueError('REFERENCE_COMPUTATIONAL_BASE_MISMATCH')
        if not receipt.get('outputs'):
            raise ValueError('REFERENCE_OUTPUT_IDENTITIES_MISSING')
        for name,digest in receipt['outputs'].items():
            if not (Path(path)/name).is_file() or sha(Path(path)/name)!=digest:
                raise ValueError('REFERENCE_OUTPUT_IDENTITY_MISMATCH: '+name)
    a,b=receipts
    for key in ('native_sha','binary_sha','python','numpy','scipy','transport_threads','rpc_mode'):
        if key not in a['identity'] or a['identity'][key]!=b['identity'].get(key):
            raise ValueError('REFERENCE_RUNTIME_OR_BINARY_MISMATCH: '+key)
    ca={k:v for k,v in a['config'].items() if k not in ('name','birth_panels','reference_diagnostics')}
    cb={k:v for k,v in b['config'].items() if k not in ('name','birth_panels','reference_diagnostics')}
    if ca!=cb:
        raise ValueError('REFERENCE_NONAGE_CONFIG_MISMATCH')
    return dict(status='SAME_COMPUTATIONAL_SOURCE_BOUND',native_sha=NATIVE_SHA,
                binary_sha=a['identity']['binary_sha'],computational_base_solver_sha=COMPUTATIONAL_BASE_SHA,
                source_function_and_clock='Shared native binary and base solver; different birth inventory discretizations are the explicit age axis',
                scope='Finite neighbor age32-to-age64 difference only; no continuum or production admission.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--age32',type=Path,required=True)
    parser.add_argument('--age64',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    binding=validate_pair(args.age32,args.age64)
    subprocess.run([sys.executable,str(Path(__file__).with_name('compare_results.py')),
                    str(args.age32/'data'),str(args.age64/'data'),'--out',str(args.out)],check=True)
    result=read_json(args.out);result['computational_source_binding']=binding
    save(args.out,result)


if __name__ == '__main__':
    main()
