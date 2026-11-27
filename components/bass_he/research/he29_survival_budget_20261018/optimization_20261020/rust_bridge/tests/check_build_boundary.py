#!/usr/bin/env python3
"""Three new NCP wrapper contracts with subprocesses explicitly simulated.

No compiler, solver, network or inherited source suite is executed here.
Real compilation evidence is kept separately in RUST_BUILD_FINAL.json.
"""
from pathlib import Path
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
from unittest.mock import patch

LANE = Path(__file__).resolve().parents[2]
BUILDER = LANE/'ncp/build_bridge.py'
spec = importlib.util.spec_from_file_location('he29_packed_ncp_build',BUILDER)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def one_case(top, kind):
    root=top/kind;root.mkdir()
    repo=root/'fake_repository';lane=repo/'research/he29/optimization';lane.mkdir(parents=True)
    for name in builder.BRIDGE_PATHS:
        dest=lane/'rust_bridge'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(LANE/'rust_bridge'/name,dest)
    dependency=root/'fake_pinned_vigilode';dependency.mkdir();(dependency/'Cargo.lock').write_text('simulated lock\n')
    tools=root/'fake_toolchain';tools.mkdir()
    for name in ('cargo','rustc'):
        (tools/name).write_bytes(b'not executed fake tool identity');(tools/name).chmod(0o755)
    out=root/'build';source='f'*40;calls=[]
    def query(argv):
        name=Path(argv[0]).name
        if name=='rustc':return 'rustc 1.94.1 (fixture)\nhost: x86_64-unknown-linux-gnu'
        if name=='cargo':return 'cargo 1.94.1 (fixture)'
        assert name=='git',argv
        path=Path(argv[2]).resolve();what=argv[3:]
        is_repo=path==repo
        assert is_repo or path==dependency,argv
        if what==['rev-parse','HEAD']:return source if is_repo else builder.VIGILODE_SOURCE
        if what==['rev-parse','HEAD^{tree}']:return ('a' if is_repo else 'b')*40
        if what==['status','--porcelain']:return ''
        raise AssertionError(argv)
    def process(argv,destination,wall):
        calls.append({'argv':list(argv),'timeout_s':wall})
        assert argv[1]=='build' and '--locked' in argv and '--lib' in argv and '--offline' in argv
        staged=Path(argv[argv.index('--manifest-path')+1]).parent
        assert (staged/'src/packed.rs').is_file()
        assert set(p.name for p in staged.glob('Cargo.*'))=={'Cargo.toml','Cargo.lock'}
        assert os.environ['CARGO_ENCODED_RUSTFLAGS']=='-C\x1ftarget-cpu=x86-64'
        assert os.environ['RUSTC_WRAPPER']==os.environ['RUSTC_WORKSPACE_WRAPPER']==''
        target=Path(argv[argv.index('--target-dir')+1]);lib=target/'release/libhe29_optimized_bridge.so'
        lib.parent.mkdir(parents=True);lib.write_bytes(b'explicitly simulated ABI2 output')
        if kind=='compiler_drift':(tools/'rustc').write_bytes(b'changed fake tool; same reported version')
        receipt={'returncode':0,'timed_out':False,'wall_s':0.,'stdout_sha256':'0'*64,'stderr_sha256':'0'*64}
        builder.atomic_json(Path(destination)/'RECEIPT.json',receipt)
        return receipt
    argv=['build_bridge.py','--out',str(out),'--source-revision',('e'*40 if kind=='source_mismatch' else source),
          '--vigilode-checkout',str(dependency),'--cargo',str(tools/'cargo'),'--rustc',str(tools/'rustc'),'--offline']
    error=None
    with patch.object(builder,'REPO',repo),patch.object(builder,'LANE',lane),patch.object(builder,'query',query),patch.object(builder,'run_process',process),patch.object(sys,'argv',argv):
        try:
            with contextlib.redirect_stdout(io.StringIO()):builder.main()
        except Exception as exc:error=repr(exc)
    if kind=='success':
        assert error is None,error
        identity=json.loads((out/'BUILD_IDENTITY.json').read_text())
        assert identity['schema']=='he29.optimized.build.v1' and identity['abi_version']==2
        assert len(identity['bridge_sources'])==5 and 'rust_bridge/src/packed.rs' in identity['bridge_sources']
        assert identity['source_revision_argument']==source
        assert identity['compiler_binary_identity_before_after_match']
        assert len(calls)==1
        return {'case':kind,'status':'PASS_SIMULATED','command_calls':len(calls),'identity_keys':sorted(identity)}
    failure=json.loads((out/'BUILD_FAILURE.json').read_text())
    expected='HE29_OPT_BUILD_OWNER_CHANGED' if kind=='compiler_drift' else 'HE29_OPT_PUBLISHED_SOURCE_SHA'
    assert error and expected in failure['error'],failure
    assert not (out/'BUILD_IDENTITY.json').exists()
    assert len(calls)==(1 if kind=='compiler_drift' else 0)
    return {'case':kind,'status':'PASS_SIMULATED_REJECTION','command_calls':len(calls),'failure_receipt':failure}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--tmp',required=True);args=ap.parse_args()
    with tempfile.TemporaryDirectory(dir=args.tmp,prefix='boundary_') as td:
        rows=[one_case(Path(td),kind) for kind in ('success','compiler_drift','source_mismatch')]
    result={'schema':'he29.optimized.build_boundary_check.v1','status':'PASS_SCOPED_SIMULATION',
        'builder_sha256':hashlib.sha256(BUILDER.read_bytes()).hexdigest(),
        'test_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'real_processes_executed':0,'real_compiler_runs':0,'native_owner_calls':0,'old_suites_replayed':0,'cases':rows}
    builder.atomic_json(Path(args.output),result)
    print(json.dumps({'status':result['status'],'cases':len(rows)}))


if __name__=='__main__':main()
