"""Intake integrity checks only; no scientific acceptance claim."""
from pathlib import Path
import importlib.util
import json
import shutil
import pytest

ROOT = Path(__file__).resolve().parents[3]
REL = Path('research/continuation_20260830')


def validator():
    path = ROOT / REL / 'verify_payload.py'
    assert path.is_file(), 'missing continuation validator'
    spec = importlib.util.spec_from_file_location('rei_payload_check', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def copy_payload(target):
    contract = json.loads((ROOT / REL / 'CONTRACT.json').read_bytes())
    for name in contract['delivery_paths'] + [str(REL / 'MANIFEST.sha256')]:
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, path)
    return target


def test_intake_payload_closes():
    result = validator().validate(ROOT)
    assert result['claim'] == 'NO_PASS_FIRST_CANONICAL_INTERVAL'
    assert result['source_objects'] == 'NOT_RUN'


def test_changed_helper_not_silently_accepted(tmp_path):
    check = validator()
    root = copy_payload(tmp_path / 'payload')
    path = root / REL / 'paired_budget.py'
    path.write_bytes(path.read_bytes() + b'\n# mutation\n')
    with pytest.raises(ValueError, match='digest mismatch'):
        check.validate(root)


def test_manifest_escape_rejected(tmp_path):
    check = validator()
    root = copy_payload(tmp_path / 'payload')
    (root / REL / 'MANIFEST.sha256').write_text('0'*64 + '  ../escape\n')
    with pytest.raises(ValueError, match='unsafe'):
        check.validate(root)
