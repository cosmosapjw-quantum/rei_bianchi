#!/usr/bin/env python3
"""Reproduce the small same-source large-domain adapter bridge (not an oracle)."""
import importlib.util,json
from pathlib import Path
import numpy as np
from native_support import Radial,sha

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
path=ROOT/'production/radial/radial_large.py'
spec=importlib.util.spec_from_file_location('author_radial_adapter',path)
author=importlib.util.module_from_spec(spec);spec.loader.exec_module(author)
guarded=Radial(path.with_suffix('.cpp'),HERE/'build_cache')
x=np.array([-32,-1,-.5,0,.5,32,63.999999,64,64.000001,512,148378.9610393039,1e12],np.clongdouble)+np.clongdouble('1.5j')
records=[]
for order in range(3):
    a=author.radial_moments(1,2*x,order);b=guarded.radial_moments(1,2*x,order)
    records.append({'order':order,'values':sum(q.size for q in a),
                    'exact_equal':all(np.array_equal(aa,bb) for aa,bb in zip(a,b))})
invalid=[]
for v,s in [(0,0),(np.inf,0),(1,np.nan),(1,2e12+1),(1,4.01j),
            (np.longdouble('1e-101'),0),(np.longdouble('1e101'),0)]:
    try:guarded.radial_moments(v,s);invalid.append(False)
    except ValueError:invalid.append(True)
result={'source_sha256':sha(path.with_suffix('.cpp')),
        'author_shared_library_sha256':sha(path.parent/'libradial_large.so'),
        'guarded_build':guarded.folder.name,'bridge':records,'invalid_rejected':invalid,
        'all_passed':all(q['exact_equal'] for q in records) and all(invalid),
        'scope':'small same-source numerical preservation, not independent accuracy'}
output=HERE/'evidence/LARGE_SOURCE_BRIDGE_REPLAY.json'
output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if not result['all_passed']:raise SystemExit(1)
