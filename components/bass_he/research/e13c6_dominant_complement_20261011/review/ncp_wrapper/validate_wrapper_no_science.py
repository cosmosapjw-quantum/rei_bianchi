#!/usr/bin/env python3
"""Focused one-shot guard checks; no scientific/analysis child is launched."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

TASK = Path(__file__).resolve().parents[2]
PACKAGE = TASK / 'BASS_HE_E13C6_DOMINANT_COMPLEMENT_REFINEMENT_20261011_v1'
WRAPPER = PACKAGE / 'code/ncp_execute_once.py'
OUTPUT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []
    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)
    ast.parse(WRAPPER.read_text())
    check('wrapper_syntax', True)
    spec = importlib.util.spec_from_file_location('e13c6_ncp_wrapper_under_review', WRAPPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    number = module.numerical_identity(PACKAGE / 'runs/N512_P60')
    analysis = module.analysis_identity(PACKAGE / 'analysis/N512_P60')
    check('actual_baseline_whole_numerical_projection_identity', number['semantic_sha256'] == module.NUMERICAL_SHA)
    check('actual_baseline_whole_exact_analysis_identity', analysis['semantic_sha256'] == module.ANALYSIS_SHA)
    check('no_scientific_vendor_loaded', not any(x in sys.modules for x in
          ('directed_interval', 'local_enclosure', 'path_enclosure', 'dominant_complement', 'analyze_refinement')))
    with tempfile.TemporaryDirectory(prefix='e13c6_no_science_', dir=OUTPUT) as temp:
        root = Path(temp)
        outside = root / 'outside'
        outside.write_bytes(b'outside')
        try:
            module.verify_inventory(root, {'../outside': {'bytes': 7, 'sha256': digest(outside)}})
        except ValueError as exc:
            check('escaping_inventory_rejected', 'escaping inventory path' in str(exc))
        else:
            check('escaping_inventory_rejected', False)
        source = root / 'source'
        source.write_bytes(b'changed')
        try:
            module.verify_inventory(root, {'source': {'bytes': 7, 'sha256': hashlib.sha256(b'initial').hexdigest()}})
        except ValueError as exc:
            check('tampered_input_bytes_rejected', 'pinned file mismatch' in str(exc))
        else:
            check('tampered_input_bytes_rejected', False)
        fixture = root / 'fixture_package'
        (fixture / 'code').mkdir(parents=True)
        copied = fixture / 'code/ncp_execute_once.py'
        shutil.copyfile(WRAPPER, copied)
        lock = fixture / 'EXECUTION_LOCK.json'
        lock.write_text('{"schema":"one","schema":"duplicate"}\n')
        malformed_output = root / 'malformed_output'
        command = [sys.executable, '-E', '-s', '-S', '-B', str(copied),
                   '--output-root', str(malformed_output), '--execution-lock-sha256', digest(lock)]
        malformed = subprocess.run(command, capture_output=True, text=True, timeout=15)
        malformed_receipt = json.loads((malformed_output / 'EXECUTION_RECEIPT.json').read_text())
        check('duplicate_manifest_prelaunch_NOT_RUN', malformed.returncode == 1 and
              malformed_receipt['status'] == 'NOT_RUN' and
              malformed_receipt['failure']['failing_phase'] == 'EXECUTION_SOURCE_AND_BASELINE_CLOSURE' and
              'duplicate JSON key' in malformed_receipt['failure']['message'])
        check('duplicate_manifest_consumes_zero_slots', malformed_receipt['counters']['consumed_N512_slots'] == 0 and
              malformed_receipt['counters']['new_N512_work_unit_invocations'] == 0 and
              malformed_receipt['counters']['new_exact_analysis_invocations'] == 0)
        before = digest(malformed_output / 'EXECUTION_RECEIPT.json')
        collision = subprocess.run(command, capture_output=True, text=True, timeout=15)
        check('fresh_output_collision_rejected_without_overwrite', collision.returncode == 2 and
              json.loads(collision.stderr)['status'] == 'NOT_RUN_OUTPUT_COLLISION' and
              before == digest(malformed_output / 'EXECUTION_RECEIPT.json'))
        lock.write_text('{"schema":"bass-he-e13c6-execution-lock-v1","files":{}}\n')
        tamper_output = root / 'tampered_manifest_output'
        tampered = subprocess.run([sys.executable, '-E', '-s', '-S', '-B', str(copied),
                                  '--output-root', str(tamper_output), '--execution-lock-sha256', '0' * 64],
                                 capture_output=True, text=True, timeout=15)
        tamper_receipt = json.loads((tamper_output / 'EXECUTION_RECEIPT.json').read_text())
        check('externally_pinned_manifest_tamper_rejected', tampered.returncode == 1 and
              tamper_receipt['status'] == 'NOT_RUN' and
              tamper_receipt['failure']['message'] == 'EXECUTION_LOCK SHA mismatch')
        check('tampered_manifest_consumes_zero_slots', tamper_receipt['counters']['consumed_N512_slots'] == 0 and
              tamper_receipt['counters']['new_N512_work_unit_invocations'] == 0 and
              tamper_receipt['counters']['new_exact_analysis_invocations'] == 0)
        archive = malformed_output / 'NCP_RETURN.zip'
        archive_identity = json.loads((malformed_output / 'RETURN_ARCHIVE_IDENTITY.json').read_text())
        check('failure_return_actual_zip_identity', archive_identity['bytes'] == archive.stat().st_size and
              archive_identity['sha256'] == digest(archive))
        with zipfile.ZipFile(archive) as zf:
            manifest = json.loads(zf.read('RETURN_MANIFEST.json'))
            check('return_member_paths_relative_and_closed', set(zf.namelist()) == set(manifest['files']) | {'RETURN_MANIFEST.json'} and
                  all(not Path(x).is_absolute() and '..' not in Path(x).parts for x in zf.namelist()))
            check('return_member_manifest_exact_bytes_and_SHA', all(
                  len(zf.read(name)) == record['bytes'] and hashlib.sha256(zf.read(name)).hexdigest() == record['sha256']
                  for name, record in manifest['files'].items()))
        # Retain only the intentionally failed fixture receipts/ZIPs, not source copies.
        preserved = OUTPUT / 'EXPECTED_GUARD_FAILURE_EVIDENCE'
        preserved.mkdir(exist_ok=False)
        shutil.copytree(malformed_output, preserved / 'duplicate_manifest')
        shutil.copytree(tamper_output, preserved / 'wrong_external_manifest_sha')
        (preserved / 'collision_stderr.json').write_text(collision.stderr)
    receipt = {'schema': 'bass-he-e13c6-wrapper-no-science-validation-v1',
               'status': 'PASS_FOCUSED_NO_SCIENCE_GUARDS', 'wrapper_sha256': digest(WRAPPER),
               'checks': checks, 'passed_count': sum(x['passed'] for x in checks),
               'failed_count': sum(not x['passed'] for x in checks),
               'scientific_work_unit_invocations': 0, 'coefficient_evaluations': 0,
               'exact_analysis_reexecutions': 0, 'ODE_solves': 0,
               'scope': 'Syntax, actual saved-baseline hash/projection checks and intentional pre-launch failure/packaging guards only. Actual NCP execution remains NOT_RUN.'}
    with (OUTPUT / 'NO_SCIENCE_VALIDATION.json').open('x') as stream:
        json.dump(receipt, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({k: receipt[k] for k in ('status', 'wrapper_sha256', 'passed_count', 'failed_count',
                                            'scientific_work_unit_invocations', 'coefficient_evaluations')}))


if __name__ == '__main__':
    main()
