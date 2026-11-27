"""Standalone input fallback and no-physics existing-output boundary checks."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,json,hashlib,os
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'C1b';(p/'code').mkdir(parents=True);(p/'evidence').mkdir()
    for f in (ROOT/'code').glob('*.py'):shutil.copyfile(f,p/'code'/f.name)
    snap=p/'private_dependencies/C1_PARENT_PUBLIC_SNAPSHOT';shutil.copytree(ROOT/'private_dependencies/C1_PARENT_PUBLIC_SNAPSHOT',snap)
    command="import run_centered as r,json; assert r.PARENT.name=='C1_PARENT_PUBLIC_SNAPSHOT'; x=json.loads((r.PARENT/'evidence/C1_SINGLE_POINT_PILOT.json').read_text()); assert x['scope'].startswith('C1 only'); print('PASS standalone snapshot resolved without eigensolve')"
    cp=subprocess.run([sys.executable,'-c',command],cwd=p/'code',capture_output=True,text=True,check=True)
    print(cp.stdout,end='')
    marker=p/'evidence/PROLATE_TAIL_ONLY.json';marker.write_bytes(b'IMMUTABLE\n')
    cp=subprocess.run([sys.executable,str(p/'code/run_prolate_tail.py')],capture_output=True,text=True)
    assert cp.returncode!=0 and 'FileExistsError' in cp.stderr
    assert marker.read_bytes()==b'IMMUTABLE\n'
    print('PASS delivered prolate driver rejects existing result before solve; original marker unchanged')

# A stale sibling must not silently override the bundled immutable snapshot.
from parent_inputs import resolve_parent,EXPECTED
with tempfile.TemporaryDirectory() as td:
    root=Path(td)/'C1b';root.mkdir()
    sibling=root.parent/'BASS_HE_C1_ELECTRONIC_ARCHITECTURE_20261001_v1'
    for rel in EXPECTED:
        dest=sibling/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'private_dependencies/C1_PARENT_PUBLIC_SNAPSHOT'/rel,dest)
    assert resolve_parent(root)==sibling
    path=sibling/'evidence/C1_SINGLE_POINT_PILOT.json'
    data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data)
    try:resolve_parent(root)
    except ValueError as exc:assert 'parent input byte identity mismatch' in str(exc)
    else:raise AssertionError('modified sibling parent accepted')
print('PASS exact sibling accepted; same-size modified sibling rejected; no solve')
