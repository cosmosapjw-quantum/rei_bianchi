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
    rust=rust.replace('    io::{self, BufRead},','    io::{self, BufRead},',1)
    signature='    transport_cells: usize,\n) -> Result<(), Box<dyn std::error::Error>> {\n    let s = setup(q, birth_count, nmu, source, transport_cells)?;'
    assert rust.count(signature)==1
    rust=rust.replace(signature,signature.replace('    transport_cells: usize,','    transport_cells: usize,\n    binary_rpc: bool,'),1)
    loop='    for line in io::stdin().lock().lines() {'
    assert rust.count(loop)==1
    rust=rust.replace(loop,Path(__file__).with_name('binary_server.rs.inc').read_text()+loop,1)
    rust=rust.replace('let offset = if args[1] == "server" { 3 } else { 4 };',
                      'let offset = if args[1] == "server" || args[1] == "server_binary64" { 3 } else { 4 };',1)
    assert rust.count('"server" => server(q, births, nmu, source, cells),')==1
    rust=rust.replace('"server" => server(q, births, nmu, source, cells),',
                      '"server" => server(q, births, nmu, source, cells, false),\n        "server_binary64" => server(q, births, nmu, source, cells, true),',1)
    extra="p.add_argument('--max-wall-s',type=float,default=600.);p.add_argument('--max-rhs',type=int,default=200000);"
    py=py.replace('a=p.parse_args();',extra+'a=p.parse_args();')
    py=py.replace('calls>200000 or time.monotonic()-started>600',
                  'calls>a.max_rhs or time.monotonic()-started>a.max_wall_s')
    py=py.replace("dict(status=status,failure=failure,q=a.q", "dict(max_rhs=a.max_rhs,max_wall_s=a.max_wall_s,status=status,failure=failure,q=a.q")
    py=py.replace('import argparse,json,subprocess,time,resource','import argparse,json,subprocess,time,resource,struct',1)
    py=py.replace('a=p.parse_args();',"p.add_argument('--rpc-mode',choices=('text','binary64'),default='text');a=p.parse_args();",1)
    original="server=subprocess.Popen([str(a.binary),'server',str(a.q),str(a.birth_panels),str(a.n_mu),str(a.source_subdivisions),str(a.transport_cells)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)"
    assert py.count(original)==1
    py=py.replace(original,"server=subprocess.Popen([str(a.binary),'server_binary64' if a.rpc_mode=='binary64' else 'server',str(a.q),str(a.birth_panels),str(a.n_mu),str(a.source_subdivisions),str(a.transport_cells)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)",1)
    py=py.replace('setup=json.loads(server.stdout.readline());','setup=json.loads(server.stdout.readline().decode());',1)
    old="""def send(mode,active,x,y):
    server.stdin.write(f'{mode} {active} {x:.17e} '+' '.join(format(v,'.17e') for v in y)+'\\n');server.stdin.flush()
    line=server.stdout.readline()
    if not line:raise RuntimeError(server.stderr.read())
    return line.strip()
"""
    assert py.count(old)==1
    py=py.replace(old,Path(__file__).with_name('binary_solver.py.inc').read_text(),1)
    py=py.replace("if answer.startswith('ERR'):","if isinstance(answer,str) and answer.startswith('ERR'):",1)
    py=py.replace("result=np.fromstring(answer,sep=' ');", "result=answer if isinstance(answer,np.ndarray) else np.fromstring(answer,sep=' ');",1)
    py=py.replace('max_rhs=a.max_rhs,max_wall_s=a.max_wall_s,status=status', 'max_rhs=a.max_rhs,max_wall_s=a.max_wall_s,rpc_mode=a.rpc_mode,status=status',1)
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
