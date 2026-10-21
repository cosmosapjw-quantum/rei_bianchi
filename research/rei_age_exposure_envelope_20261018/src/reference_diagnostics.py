"""Transform the known generated reference into a passive diagnostic copy."""
from pathlib import Path
import argparse
import hashlib
import json


COMPUTATIONAL_BASE_SHA = '78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620'


def transform_identity():
    return hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name('reference_diagnostics_runtime.py').read_bytes()).hexdigest()


def transform_solver(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != COMPUTATIONAL_BASE_SHA:
        raise ValueError('REFERENCE_DIAGNOSTIC_BASE_SHA_MISMATCH')
    text = source.decode()
    def replace_once(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('REFERENCE_DIAGNOSTIC_ANCHOR: '+old[:60])
        text = text.replace(old, new, 1)
    runtime = Path(__file__).with_name('reference_diagnostics_runtime.py').read_text()
    identity = dict(computational_base_solver_sha=COMPUTATIONAL_BASE_SHA,
                    diagnostic_transform_sha=transform_identity(), reference_diagnostics=True)
    adapter = '''
if a.error_norm != 'block-max':
    raise ValueError('REFERENCE_DIAGNOSTICS_REQUIRE_BLOCK_MAX')
_reference_diagnostics = ReferenceDiagnostics(a.out, IDENTITY, __file__)
make_block_dop853 = _reference_diagnostics.instrument_factory(make_block_dop853, block_error_norm)
_reference_base_solve = solve_ivp
def solve_ivp(*args, **kwargs):
    return _reference_diagnostics.solve(_reference_base_solve, event, retry, *args, **kwargs)
'''.replace('IDENTITY', repr(identity))
    replace_once('server=subprocess.Popen(', runtime+'\n'+adapter+'\nserver=subprocess.Popen(')
    birth = "            y[4+2*cells*event:4+2*cells*(event+1)]=setup['encoded_births'][event];active+=1"
    replace_once(birth, "            _before_birth_coordinates=y.copy()\n"+birth+"\n            _reference_diagnostics.birth(event,stop,active-1,active,setup,_before_birth_coordinates,y,physical,lambda:json.loads(send('P',active,stop,y)))")
    replace_once('finally:\n    server.stdin.close();', 'finally:\n    _reference_diagnostics.persist()\n    server.stdin.close();')
    replace_once('dict(max_rhs=a.max_rhs,max_wall_s=a.max_wall_s,rpc_mode=',
                 'dict(reference_diagnostics=True,reference_diagnostic_identity=_reference_diagnostics.identity,max_rhs=a.max_rhs,max_wall_s=a.max_wall_s,rpc_mode=')
    return text.encode()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    data=transform_solver(args.source.read_bytes())
    args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.out.exists() and args.out.read_bytes()!=data:
        raise FileExistsError('DIAGNOSTIC_COPY_EXISTS')
    args.out.write_bytes(data)
    print(json.dumps(dict(computational_base_solver_sha=COMPUTATIONAL_BASE_SHA,
                         diagnostic_transform_sha=transform_identity(), executed_solver_sha=hashlib.sha256(data).hexdigest())))


if __name__ == '__main__':
    main()
