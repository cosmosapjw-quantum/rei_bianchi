"""Bounded delivery regressions; no spectral solver, native cloud job or upload."""
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


def api():
    assert importlib.util.find_spec('prepared_io') is not None, 'prepared I/O implementation missing'
    return importlib.import_module('prepared_io')


@pytest.fixture
def inputs(tmp_path):
    root = tmp_path / 'r1'
    (root / 'results').mkdir(parents=True)
    entries = []
    for i in range(7):
        relative = f'results/branch_{i}.json'
        data = json.dumps({'case': i}).encode()
        (root / relative).write_bytes(data)
        entries.append({'path': relative, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    manifest = tmp_path / 'input_manifest.json'
    manifest.write_text(json.dumps({'schema': 'bass_he.fixed_trace_input.v1', 'entries': entries}))
    return root, manifest, entries


def test_verified_bytes_are_returned_once(inputs):
    root, manifest, entries = inputs
    traces, receipt = api().read_trace_inputs(root, manifest)
    assert len(traces) == receipt['files_checked'] == 7
    assert receipt['status'] == 'INPUT_IDENTITY_VERIFIED'
    assert receipt['manifest_sha256'] == hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert [item[0] for item in traces] == [e['path'] for e in entries]
    for relative, payload in traces:
        assert payload == (root / relative).read_bytes()


def test_tampered_trace_is_rejected(inputs):
    root, manifest, _ = inputs
    (root / 'results/branch_0.json').write_bytes(b'tampered')
    with pytest.raises(ValueError, match='identity mismatch'):
        api().read_trace_inputs(root, manifest)


def test_extra_trace_is_rejected(inputs):
    root, manifest, _ = inputs
    (root / 'results/extra.json').write_text('{}')
    with pytest.raises(ValueError, match='file set'):
        api().read_trace_inputs(root, manifest)


def test_missing_trace_is_rejected(inputs):
    root, manifest, _ = inputs
    (root / 'results/branch_0.json').unlink()
    with pytest.raises(ValueError, match='file set'):
        api().read_trace_inputs(root, manifest)


@pytest.mark.parametrize('bad_path', ['../outside.json', '/tmp/outside.json', 'results/../branch.json'])
def test_noncanonical_paths_are_rejected(inputs, bad_path):
    root, manifest, entries = inputs
    entries[0]['path'] = bad_path
    manifest.write_text(json.dumps({'schema': 'bass_he.fixed_trace_input.v1', 'entries': entries}))
    with pytest.raises(ValueError, match='path'):
        api().read_trace_inputs(root, manifest)


def test_duplicate_manifest_entry_is_rejected(inputs):
    root, manifest, entries = inputs
    entries[-1] = entries[0]
    manifest.write_text(json.dumps({'schema': 'bass_he.fixed_trace_input.v1', 'entries': entries}))
    with pytest.raises(ValueError, match='duplicate'):
        api().read_trace_inputs(root, manifest)


def test_symlink_trace_is_rejected(inputs, tmp_path):
    root, manifest, _ = inputs
    source = root / 'results/branch_0.json'
    external = tmp_path / 'external.json'
    external.write_bytes(source.read_bytes())
    source.unlink()
    source.symlink_to(external)
    with pytest.raises(ValueError, match='symlink'):
        api().read_trace_inputs(root, manifest)


def test_read_buffer_survives_later_file_change(inputs):
    root, manifest, _ = inputs
    traces, _ = api().read_trace_inputs(root, manifest)
    before = traces[0][1]
    (root / traces[0][0]).write_text('not the verified data')
    assert traces[0][1] == before


def test_existing_output_is_never_overwritten(tmp_path):
    p = tmp_path / 'result.json'
    p.write_text('old evidence')
    with pytest.raises(FileExistsError):
        api().publish_json(p, {'new': True})
    assert p.read_text() == 'old evidence'


def test_existing_symlink_output_is_rejected(tmp_path):
    target = tmp_path / 'target.json'
    target.write_text('immutable')
    p = tmp_path / 'result.json'
    p.symlink_to(target)
    with pytest.raises(FileExistsError):
        api().publish_json(p, {'new': True})
    assert target.read_text() == 'immutable'


def test_successful_publication_is_create_only_and_has_no_temp_left(tmp_path):
    p = tmp_path / 'result.json'
    api().publish_json(p, {'complete': True})
    assert json.loads(p.read_text()) == {'complete': True}
    assert sorted(x.name for x in tmp_path.iterdir()) == ['result.json']


def test_nonfinite_json_is_rejected_before_publication(tmp_path):
    p = tmp_path / 'result.json'
    with pytest.raises(ValueError):
        api().publish_json(p, {'value': float('nan')})
    assert not p.exists()


def test_verify_only_skips_numerical_dependency_import_and_does_not_claim_tests(inputs, tmp_path):
    # The seven inputs are identity-only JSON, not usable spectral traces.
    root, manifest, _ = inputs
    p = tmp_path / 'verify.json'
    script = Path(__file__).with_name('evaluate_r2.py')
    proc = subprocess.run([sys.executable, '-S', str(script), '--r1-root', str(root),
                           '--input-manifest', str(manifest), '--verify-only', '--out', str(p)],
                          capture_output=True, text=True, timeout=10)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(p.read_text())
    assert result['status'] == 'INPUT_IDENTITY_VERIFIED'
    assert result['new_spectral_solves'] == result['new_cloud_runs'] == 0
    assert result['tests']['status'] == 'NOT_RUN_BY_THIS_COMMAND'
    assert result['tests']['passed'] is None
    assert result['saved_trace_analysis'] == 'NOT_RUN'


def test_output_conflict_stops_before_missing_inputs_are_read(tmp_path):
    # Existing result is preserved even when no source data exists.
    p = tmp_path / 'result.json'
    p.write_text('old evidence')
    script = Path(__file__).with_name('evaluate_r2.py')
    proc = subprocess.run([sys.executable, '-S', str(script), '--r1-root', str(tmp_path/'missing'),
                           '--verify-only', '--out', str(p)], capture_output=True, text=True, timeout=10)
    assert proc.returncode != 0
    assert 'FileExistsError' in proc.stderr
    assert p.read_text() == 'old evidence'
