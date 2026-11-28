"""Focused installed-distribution coexistence check; no atomic scattering claim."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata as md
import json
import os
import sys
import zipfile


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--target',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(a.target.resolve()))
    import bass_he_atomic_export as export
    import bass_he_west82 as optical
    from bass_he_atomic_export._io import write_json_create_only
    for module in (export,optical):
        assert Path(module.__file__).resolve().is_relative_to(a.target.resolve()),module.__file__
    wheels=sorted((a.root/'dist').glob('*.whl'))
    paths=[];wheel_meta=[];entrypoints=[]
    for w in wheels:
        with zipfile.ZipFile(w) as z:
            names=z.namelist()
            src={n for n in names if not n.endswith('/') and '.dist-info/' not in n}
            assert not any(n.startswith('bass_he_rcx/') for n in src)
            assert not any(n.lower().endswith(('.pdf','.csv')) for n in src)
            paths.append(src)
            entrypoints.append([z.read(n).decode() for n in names if n.endswith('/entry_points.txt')])
            wheel_meta.append({'name':w.name,'sha256':hashlib.sha256(w.read_bytes()).hexdigest(),
                               'import_top_levels':sorted({n.split('/')[0] for n in src})})
    assert len(paths)==2
    overlap=paths[0]&paths[1];assert not overlap,overlap
    request=json.loads((a.root/'contract/EXAMPLE_REQUEST.json').read_text())
    packet=export.export_packet(request)
    assert export.validate_packet(packet)
    # Check that importing and exercising the optical reference does not replace rate evaluation.
    r=optical.solve_partial_wave(1.0,0,[0.0,1.0],[0.0],[[1e-18]])
    assert r['loss_probability']>0 and r['RCT_cross_section'] is None
    assert export.export_packet(request)==packet
    assert 'bass_he_rcx' not in sys.modules
    result={'schema':'bass-he.b3.coinstallation.v1','status':'VERIFIED_IN_THIS_RUNTIME',
      'target':str(a.target),'imports':{m.__name__:m.__file__ for m in (export,optical)},
      'distributions':{n:md.version(n) for n in ('bass-he-atomic-export','bass-he-west82-reference','numpy','scipy')},
      'dependency_installation':'two local wheels, --no-index --no-deps; NumPy/SciPy inherited from recorded host',
      'wheel_metadata':wheel_meta,'shared_runtime_paths':sorted(overlap),
      'entrypoints':entrypoints,'legacy_namespace_imported':False,
      'rate_before_after_optical_unchanged':True,'inherited_code_sha256':export.verify_runtime_bindings(),
      'manufactured_optical_case':r,'physical_solves':0,'parent_scientific_suite_reruns':0,
      'actual_receiver_integration':False,'NCP_benchmark':False}
    write_json_create_only(a.out,result)
    print('coexistence verified; only one manufactured optical compatibility call')

if __name__=='__main__':main()
