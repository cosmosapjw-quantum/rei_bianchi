#!/usr/bin/env python3
"""One runnable entry point; PASS means loading/FFI/small identities, not science."""
import argparse,json,platform,sys
from pathlib import Path
import numpy as np
from native_support import Radial,sha

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--output',type=Path)
    args=p.parse_args();r=Radial(args.source,args.cache)
    values,info=r.radial_moments(np.longdouble(1),np.clongdouble(0),2,return_info=True)
    M,D,D2=values
    checks={'M0':bool(M[1]==1),'M2':bool(M[3]==3),'dM2_ds':bool(D[3]==1),
            'd2M2_ds2':bool(D2[3]==0),'finite':bool(all(np.all(np.isfinite(x)) for x in values))}
    result={'status':'PASS_SCOPED_HEALTHCHECK' if all(checks.values()) else 'FAIL',
            'source':str(args.source.resolve()),'source_sha256':sha(args.source),
            'build_path':str(r.folder),'build_manifest_sha256':sha(r.folder/'manifest.json'),
            'abi':r.abi,'python':platform.python_version(),'numpy':np.__version__,
            'machine':platform.machine(),'platform':platform.platform(),'checks':checks,
            'info':info,'claim_ceiling':'Build/load and exact polynomial identities only; no new scientific admission.'}
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text,end='')
    return 0 if all(checks.values()) else 1
if __name__=='__main__':sys.exit(main())
