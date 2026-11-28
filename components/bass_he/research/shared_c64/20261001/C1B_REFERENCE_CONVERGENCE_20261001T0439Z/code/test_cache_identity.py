"""Cache byte mismatch rejection, no eigensolve."""
from pathlib import Path
import tempfile,json,shutil
import run_centered as run
ROOT=run.ROOT
x=json.loads((ROOT/'evidence/B_l40.json').read_text())
with tempfile.TemporaryDirectory() as td:
    t=Path(td);(t/'evidence').mkdir()
    (t/'evidence/fixture.json').write_text(json.dumps(x))
    for s in x['states']:
        dest=t/s['array_file']['path'];shutil.copyfile(ROOT/s['array_file']['path'],dest)
    run.ROOT=t
    states=run.load_pair('fixture');assert len(states)==2
    target=t/x['states'][0]['array_file']['path'];data=bytearray(target.read_bytes());data[-1]^=1;target.write_bytes(data)
    try:run.load_pair('fixture')
    except ValueError as e:assert 'identity mismatch' in str(e)
    else:raise AssertionError('tampered state accepted')
print('PASS: trusted cache loaded; same-length modified bytes rejected before np.load; no physics run')
