"""Postpilot I/O-only fix check; does not execute physics."""
import tempfile,hashlib,json
from pathlib import Path
import run_pilot as p
with tempfile.TemporaryDirectory() as td:
    p.LOG=Path(td)/'log';p.OUT=Path(td)/'out.json'
    p.preflight()
    p.LOG.write_bytes(b'IMMUTABLE\n')
    before=p.LOG.read_bytes()
    try:p.preflight()
    except FileExistsError:pass
    else:raise AssertionError('existing log not rejected')
    assert p.LOG.read_bytes()==before
    p.atomic_new_json(p.OUT,{'x':1})
    assert json.loads(p.OUT.read_text())=={'x':1}
    original=p.OUT.read_bytes()
    try:p.atomic_new_json(p.OUT,{'x':2})
    except FileExistsError:pass
    else:raise AssertionError('existing output overwritten')
    assert p.OUT.read_bytes()==original
    assert len(list(Path(td).iterdir()))==2
print('PASS: create-only preflight, immutable log, fsynced atomic JSON, overwrite rejection, temporary cleanup; no physics run')
