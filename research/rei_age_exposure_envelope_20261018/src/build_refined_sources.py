"""Generate an additive native CLI and resource-configurable reference script.

The donor functions implementing physics and the old native modes stay verbatim.
This is not a replacement integrator. Donor SHA checks precede any output write.
"""
from pathlib import Path
import argparse
import hashlib
import json

NATIVE_SHA='d09b242796208657fe62a831f3a503464c914a0c720eac659c3d5cb825345894'
SOLVER_SHA='5a6074cdc93f6036c01553b0db0ad8e12fbd8af04ead8873b3908a35c56c346d'

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def overlay(native: bytes, solver: bytes) -> tuple[str, str]:
    if digest(native)!=NATIVE_SHA or digest(solver)!=SOLVER_SHA:
        raise ValueError('DONOR_SHA_MISMATCH: refusing to patch different source')
    rust=native.decode('utf-8'); py=solver.decode('utf-8')
    thread_assignment='    cfg.transport_threads = 1;'
    if rust.count(thread_assignment)!=1:
        raise ValueError('NATIVE_TRANSPORT_THREADS_ANCHOR')
    rust=rust.replace(thread_assignment,
        '    cfg.transport_threads = std::env::var("REI_TRANSPORT_THREADS")\n'
        '        .ok().and_then(|value| value.parse::<usize>().ok())\n'
        '        .unwrap_or(1).clamp(1, 48);',1)
    addition=Path(__file__).with_name('native_refine.rs.inc').read_text()
    anchor='fn main() -> Result<(), Box<dyn std::error::Error>> {'
    if rust.count(anchor)!=1:
        raise ValueError('NATIVE_MAIN_ANCHOR')
    rust=rust.replace(anchor,addition+'\n'+anchor)
    anchor='        _ => Err("mode".into()),'
    arm='''        "native_refine" => {
            let levels = args.get(8).ok_or("missing common birth levels")?
                .split(',').map(str::parse::<usize>).collect::<Result<Vec<_>, _>>()?;
            let factor: usize = args.get(9).ok_or("missing time factor")?.parse()?;
            native_refine(q, Path::new(&args[3]), births, nmu, source, cells, &levels, factor)
        }
'''
    if rust.count(anchor)!=1: raise ValueError('NATIVE_MODE_ANCHOR')
    rust=rust.replace(anchor,arm+anchor)
    extra="p.add_argument('--max-wall-s',type=float,default=600.);p.add_argument('--max-rhs',type=int,default=200000);"
    py=py.replace('a=p.parse_args();',extra+'a=p.parse_args();')
    py=py.replace('calls>200000 or time.monotonic()-started>600',
                  'calls>a.max_rhs or time.monotonic()-started>a.max_wall_s')
    py=py.replace("dict(status=status,failure=failure,q=a.q", "dict(max_rhs=a.max_rhs,max_wall_s=a.max_wall_s,status=status,failure=failure,q=a.q")
    return rust,py

def write_checked(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()!=data:
        raise FileExistsError(f'OUTPUT_IDENTITY_CONFLICT: {path}')
    if not path.exists(): path.write_bytes(data)

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--donor',type=Path,default=Path(__file__).resolve().parents[1]/'donors/pr171')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    rs,py=overlay((a.donor/'positive_native.rs').read_bytes(),(a.donor/'positive_solver.py').read_bytes())
    outputs={'positive_native.rs':rs.encode(),'positive_solver_refined.py':py.encode()}
    for n,b in outputs.items(): write_checked(a.out/n,b)
    record={'schema':'rei.age-refinement.overlay.v1','original_native_sha256':NATIVE_SHA,
            'original_solver_sha256':SOLVER_SHA,'physics_functions_changed':False,
            'outputs':{n:digest(b) for n,b in outputs.items()}}
    write_checked(a.out/'OVERLAY_IDENTITY.json',(json.dumps(record,indent=2)+'\n').encode())
    print(json.dumps(record,indent=2))
if __name__=='__main__': main()
