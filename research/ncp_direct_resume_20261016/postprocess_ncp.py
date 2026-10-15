#!/usr/bin/env python3
"""One-shot, direct-filesystem continuation of the frozen full005 renderer.

This never launches a solver, polls a campaign, uses SSH, or extends an epoch.
The original watcher can remain active; choose a separate fresh output path.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent
DEFAULT_RENDERER_ROOT = HERE.parent / 'flrw_full005_postprocess_20261015'
DEFAULT_CAMPAIGN = Path('/root/REI_FLRW_COVARIANT_20261015_005/full_campaign001')
CASES = ('FLRW_FULL_Q512_001', 'FLRW_FULL_Q1024_001')
NEEDED = ('history.csv', 'abundances.csv', 'ledgers.csv', 'config.cfg',
          'source_identity.txt', 'RETURN.txt', 'checkpoint.txt')
SOURCE_SHA = '1a2268e3da98ed47159cb738762a1a3d3d17bdcb6806e611cbd2bc3c0c6eaff7'
BINARY_SHA = '4aa337414a275c66068a900b8349a4114ddc1b1eebad1d904b61cbbd3da84fd4'
HARD_DEADLINE = 1792122617.77407  # 2026-10-16T03:50:17.774070Z; NEVER reset.
CAP_SECONDS = 300
CAP_MEMORY = 8 * 1024**3
SUCCESS = 'COMPLETED_ACTUAL_FULL_PAIR_DIAGNOSTICS_PENDING_INDEPENDENT_REVIEW'
ARCHIVE_NAME = 'POSTPROCESS_REPORT_WITH_RUNNABLE_CODE_EXTERNAL_INPUTS.zip'
PACKAGE_GENERATED = {ARCHIVE_NAME, 'REPORT_PACKAGE_RECEIPT.json', 'RECOVERY_RECEIPT.json'}
KNOWN_STATUSES = {SUCCESS, 'NOT_READY_NO_FULL_PLOTS',
                  'READY_FOR_EXPLICIT_ONE_SHOT_DIAGNOSTIC_RENDER',
                  'CONTINUATION_FAILED_NO_FULL_PLOTS_OR_ADMISSION'}


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def load(path):
    return json.loads(path.read_text())


def fields(path):
    return dict(line.split('=', 1) for line in path.read_text().splitlines()
                if '=' in line and not line.startswith('#'))


def completed(receipt):
    """Exact successful terminal schema from stage005/full_control.py."""
    if not isinstance(receipt, dict):
        return False
    native = receipt.get('native_return') or {}
    try:
        return (receipt.get('returncode') == 0
                and receipt.get('native_completion_proof') is True
                and receipt.get('source_config_binary_bindings_match') is True
                and receipt.get('source_identity_readback_equal') is True
                and receipt.get('config_readback_equal') is True
                and receipt.get('stop_reason') is None
                and receipt.get('terminal_parse_error') is None
                and native.get('status') == 'COMPLETE_REPRESENTED_INTERVAL'
                and native.get('result') == 'Ok(())'
                and float(native.get('a', 'nan')) == .2)
    except (TypeError, ValueError):
        return False


def inspect(campaign, renderer_root, now=None):
    """Read once. Missing/in-progress controller receipts block rendering."""
    now = time.time() if now is None else now
    result = {'status': 'NOT_READY_NO_FULL_PLOTS', 'observed_utc': utc(),
              'campaign': str(campaign), 'blockers': [], 'cases': {},
              'postprocess_hard_deadline_epoch': HARD_DEADLINE,
              'postprocess_hard_deadline_utc': '2026-10-16T03:50:17.774070+00:00',
              'remaining_seconds': HARD_DEADLINE - now,
              'solver_runs': 0, 'scientific_admission': 'NOT_ISSUED',
              'D_cosmological_activation': 'NOT_ACTIVATED_NOT_PLOTTED'}
    blockers = result['blockers']
    if now >= HARD_DEADLINE:
        blockers.append('ORIGINAL_POSTPROCESS_DEADLINE_EXPIRED_FRESH_SCOPED_POSTPROCESS_BUDGET_REQUIRED')
    try:
        frozen_epoch = load(renderer_root / 'FULL005_EPOCH.json')
        expected = load(renderer_root / 'FULL005_EXPECTED_BINDINGS.json')['bindings']
        plan = load(renderer_root / 'FULL005_RESOURCE_PLAN.json')
        if float(frozen_epoch['deadline_epoch']) + 3600 != HARD_DEADLINE:
            raise ValueError('FROZEN_POSTPROCESS_DEADLINE_DISAGREEMENT')
        if plan['source_identity_sha256'] != SOURCE_SHA or plan['binary_sha256'] != BINARY_SHA:
            raise ValueError('FROZEN_SOURCE_BINARY_DISAGREEMENT')
        planned = {case['case']: case for case in plan['cases']}
        if load(campaign / 'campaign_epoch.json') != frozen_epoch:
            raise ValueError('NATIVE_EPOCH_CHANGED_NO_RESET_ALLOWED')
        actual_plan = load(campaign / 'full_resource_plan.json')
        if actual_plan != plan:
            raise ValueError('CAMPAIGN_RESOURCE_PLAN_DISAGREEMENT')
    except (OSError, KeyError, ValueError, TypeError) as error:
        blockers.append(str(error))
        return result
    try:
        terminal = load(campaign / 'full_campaign.receipt.json')
        if (terminal.get('status') != 'ALL_FULL_CASES_COMPLETE_PENDING_SCIENTIFIC_POSTPROCESS'
                or terminal.get('source_identity_sha256') != SOURCE_SHA
                or terminal.get('binary_sha256') != BINARY_SHA
                or terminal.get('source_unchanged') is not True
                or terminal.get('global_stop_reason') is not None
                or terminal.get('campaign_epoch') != frozen_epoch):
            blockers.append('CAMPAIGN_TERMINAL_NOT_COMPLETE_OR_BOUND')
    except (OSError, ValueError, TypeError) as error:
        blockers.append('CAMPAIGN_TERMINAL_UNAVAILABLE: ' + str(error))
    rows = []
    for case in CASES:
        local = []
        try:
            binding = load(campaign / 'launches' / (case + '.binding.json'))
            receipt = load(campaign / 'launches' / (case + '.receipt.json'))
            if not completed(receipt) or receipt.get('case') != case:
                local.append('CONTROLLER_TERMINAL_INCOMPLETE')
            frozen = expected[case]
            if (frozen['source_identity_sha256'] != SOURCE_SHA
                    or frozen['binary_sha256'] != BINARY_SHA
                    or frozen['base_config_sha256'] != planned[case]['config_sha256']):
                local.append('FROZEN_PLAN_BINDING_DISAGREEMENT')
            for key in ('source_identity_sha256', 'binary_sha256',
                        'base_config_sha256', 'runtime_config_sha256'):
                if binding.get(key) != frozen[key] or receipt.get(key) != frozen[key]:
                    local.append('FROZEN_BINDING_MISMATCH:' + key)
            if binding.get('case') != case:
                local.append('CONTROLLER_BINDING_CASE_MISMATCH')
            run = campaign / 'runs' / case
            for name in NEEDED:
                if not (run / name).is_file():
                    local.append('MISSING_REQUIRED_OUTPUT:' + name)
            # Hash only small frozen source/config inputs here. The unchanged
            # renderer hashes and validates every scientific output in budget.
            for path, digest in ((run / 'source_identity.txt', SOURCE_SHA),
                                 (run / 'config.cfg', frozen['runtime_config_sha256']),
                                 (campaign / 'configs' / planned[case]['config'], frozen['base_config_sha256']),
                                 (campaign / 'launches' / (case + '.runtime.cfg'), frozen['runtime_config_sha256'])):
                if sha(path) != digest:
                    local.append('SOURCE_CONFIG_READBACK_MISMATCH:' + str(path.relative_to(campaign)))
            native = fields(run / 'RETURN.txt')
            if (native.get('status') != 'COMPLETE_REPRESENTED_INTERVAL'
                    or native.get('result') != 'Ok(())' or float(native.get('a', 'nan')) != .2
                    or native != receipt.get('native_return')):
                local.append('NATIVE_TERMINAL_READBACK_MISMATCH')
            rows.append(int(native['accepted']) + 1)
        except (OSError, KeyError, ValueError, TypeError) as error:
            local.append(str(error))
        result['cases'][case] = {'ready': not local, 'blockers': local}
        blockers.extend(case + ': ' + item for item in local)
    if len(rows) == 2:
        estimate = 512 * sum(rows) + 512 * 1024**2
        result['memory_planning'] = {'history_rows': rows, 'estimated_working_bytes': estimate,
                                     'rule': '512 bytes/row plus 512MiB; estimate, not measured RSS',
                                     'enforced_address_space_bytes': CAP_MEMORY}
        if min(rows) <= 0 or estimate > 6 * 1024**3:
            blockers.append('POSTPROCESS_HISTORY_SIZE_ESTIMATE_EXCEEDS_OWNER_HEADROOM')
    if not blockers:
        result['status'] = 'READY_FOR_EXPLICIT_ONE_SHOT_DIAGNOSTIC_RENDER'
    return result


def bounded_command(command, output, deadline):
    remaining = min(CAP_SECONDS, deadline - time.monotonic(), HARD_DEADLINE - time.time())
    if remaining <= 0:
        raise RuntimeError('POSTPROCESS_SHARED_BUDGET_OR_ORIGINAL_DEADLINE_EXPIRED')
    def bound():
        resource.setrlimit(resource.RLIMIT_AS, (CAP_MEMORY, CAP_MEMORY))
    environment = os.environ.copy()
    environment.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    start = time.monotonic()
    with output.open('x') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                 env=environment, preexec_fn=bound, start_new_session=True)
        try:
            code = child.wait(timeout=remaining)
        except BaseException as error:
            # Interruption must not leave a detached renderer outside the shared
            # budget. No retry; kill the group and reap before propagating.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
            if isinstance(error, subprocess.TimeoutExpired):
                raise RuntimeError('POSTPROCESS_SHARED_300S_OR_ABSOLUTE_DEADLINE_CAP') from error
            raise
    return {'command': command, 'returncode': code, 'wall_s': time.monotonic() - start,
            'timeout_seconds': remaining, 'address_space_limit_bytes': CAP_MEMORY,
            'child_peak_rss_bytes_linux_so_far': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024}


def package(output, campaign, renderer_root, status):
    """Reproducible code/evidence report; raw scientific inputs remain external."""
    # Keep the render outcome recoverable even if subsequent packaging fails.
    write(output / 'FINAL_STATUS.json', status)
    index = []
    for case in CASES:
        for name in NEEDED:
            path = campaign / 'runs' / case / name
            if path.is_file():
                index.append({'path': str(path), 'bytes': path.stat().st_size,
                              'archive_member': None, 'raw_input_remains_external': True})
    write(output / 'EXTERNAL_RAW_INPUT_INDEX.json', {
        'status': 'RAW_INPUTS_EXTERNAL_NOT_A_SELF_CONTAINED_SCIENTIFIC_DATA_ARCHIVE',
        'files': index, 'content_hashes_when_bound': 'full_pair_manifest.json'})
    (output / 'REPORT.md').write_text(
        '# Direct NCP postprocessing\n\n' + status['status'] + '\n\n'
        'One-shot; no solver runs, checkpoint changes, watcher, retries, or admission.\n'
        'This ZIP includes runnable renderer code and small reproduction evidence. '
        'Large scientific inputs remain external, indexed in EXTERNAL_RAW_INPUT_INDEX.json. '
        'A copied full_pair_manifest.json retains original absolute input paths; '
        'reproduce by running the wrapper against the original campaign directory.\n'
        'Full pair differences are diagnostic only. D activation is absent.\n')
    archive = build_archive(output, renderer_root, campaign)
    write(output / 'REPORT_PACKAGE_RECEIPT.json', {
        'archive': str(archive), 'bytes': archive.stat().st_size, 'sha256': sha(archive),
        'kind': 'REPORT_WITH_RUNNABLE_CODE_REQUIRING_EXTERNAL_RAW_INPUTS',
        'solver_runs': 0, 'scientific_admission': 'NOT_ISSUED'})


def build_archive(output, renderer_root, campaign=None):
    """Clamp archive metadata only; never change filesystem timestamps."""
    archive = output / ARCHIVE_NAME
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED,
                         allowZip64=True, strict_timestamps=False) as bundle:
        for path in sorted(output.rglob('*')):
            if path.is_file() and path != archive:
                bundle.write(path, 'report/' + str(path.relative_to(output)))
        bundle.write(Path(__file__), 'runnable/ncp_direct_resume_20261016/postprocess_ncp.py')
        for pattern in ('*.json', '*.md', 'postprocess_flrw.py', 'vendor/*.py', 'contracts/*.md'):
            for path in sorted(renderer_root.glob(pattern)):
                if path.is_file():
                    bundle.write(path, 'runnable/flrw_full005_postprocess_20261015/' + str(path.relative_to(renderer_root)))
        small = [] if campaign is None else [campaign / name for name in ('campaign_epoch.json', 'full_campaign.receipt.json',
                 'full_campaign.binding.json', 'full_resource_plan.json')]
        if campaign is not None:
            small += list((campaign / 'configs').glob('*.cfg'))
        for case in CASES if campaign is not None else ():
            small += [campaign / 'launches' / (case + suffix)
                      for suffix in ('.binding.json', '.receipt.json', '.runtime.cfg')]
            small += [campaign / 'runs' / case / name for name in ('source_identity.txt', 'config.cfg', 'RETURN.txt')]
        for path in small:
            if path.is_file():
                bundle.write(path, 'controller_evidence/' + str(path.relative_to(campaign)))
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise RuntimeError('REPORT_ZIP_CRC_FAILURE')
        for path in (output / 'FINAL_STATUS.json', Path(__file__)):
            member = ('report/FINAL_STATUS.json' if path.parent == output else
                      'runnable/ncp_direct_resume_20261016/postprocess_ncp.py')
            if path.is_file() and bundle.read(member) != path.read_bytes():
                raise RuntimeError('REPORT_ZIP_PAYLOAD_READBACK_FAILURE:' + member)
    return archive


def packaged_render(output, campaign, renderer_root, status):
    """Report packaging independently without changing the render receipt."""
    result = dict(status, scientific_status=status['status'],
                  packaging_status='PACKAGED', output=str(output),
                  archive=str(output / ARCHIVE_NAME))
    try:
        package(output, campaign, renderer_root, status)
    except Exception as error:
        result.update(packaging_status='PACKAGING_FAILED', packaging_error=str(error))
    return result


def existing_scientific_status(existing):
    """Interpret only the established wrapper schema; keep its bytes untouched."""
    try:
        status = load(existing / 'FINAL_STATUS.json')
        if (not isinstance(status, dict) or status.get('status') not in KNOWN_STATUSES
                or type(status.get('solver_runs')) is not int or status['solver_runs'] != 0
                or status.get('scientific_admission') != 'NOT_ISSUED'
                or (status['status'] == SUCCESS and
                    (status.get('error') or status.get('blockers')))):
            raise ValueError('UNRECOGNIZED_OR_CONTRADICTORY_FINAL_STATUS_SCHEMA')
        return status, None
    except (OSError, ValueError, TypeError) as error:
        return {'status': 'UNKNOWN_HOLD'}, str(error)


def repackage(existing, output, campaign, renderer_root):
    """Copy preserved evidence and package once, with no readiness/render calls."""
    original, status_error = existing_scientific_status(existing)
    science = original['status']
    if not existing.is_dir():
        raise ValueError('EXISTING_OUTPUT_DIRECTORY_REQUIRED')
    if output.exists():
        raise ValueError('FRESH_SEPARATE_OUTPUT_DIRECTORY_REQUIRED')
    for source in (existing, campaign, renderer_root):
        if output == source or source in output.parents or output in source.parents:
            raise ValueError('RECOVERY_OUTPUT_MUST_NOT_OVERLAP_SOURCE_CAMPAIGN_OR_RENDERER')
    result = {'status': science, 'scientific_status': science,
              'packaging_status': 'PACKAGING_FAILED', 'solver_runs': 0,
              'scientific_admission': 'NOT_ISSUED', 'source_output': str(existing),
              'output': str(output), 'archive': str(output / ARCHIVE_NAME),
              'original_final_status': str(existing / 'FINAL_STATUS.json'),
              'preserved_source_archive': str(existing / ARCHIVE_NAME),
              'exit_code_meaning': 'Packaging outcome only; zero is not scientific success.'}
    if status_error:
        result['original_status_validation_error'] = status_error
    if 'error' in original:
        result['original_error'] = original['error']
    try:
        output.mkdir(parents=True)
        for path in sorted(existing.rglob('*')):
            relative = path.relative_to(existing)
            if path.is_file() and str(relative) not in PACKAGE_GENERATED:
                target = output / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
        archive = build_archive(output, renderer_root)
        result.update(packaging_status='PACKAGED', bytes=archive.stat().st_size,
                      sha256=sha(archive))
    except Exception as error:
        result['packaging_error'] = str(error)
    # Kept beside the ZIP: it describes the finished operation, not science.
    try:
        write(output / 'RECOVERY_RECEIPT.json', result)
    except OSError as error:
        result.update(packaging_status='PACKAGING_FAILED',
                      recovery_receipt_error=str(error))
    return result


def render(campaign, renderer_root, output):
    if output.exists():
        raise ValueError('FRESH_SEPARATE_OUTPUT_DIRECTORY_REQUIRED')
    if campaign == output or campaign in output.parents:
        raise ValueError('OUTPUT_MUST_BE_OUTSIDE_EXISTING_CAMPAIGN')
    output.mkdir(parents=True)
    status = inspect(campaign, renderer_root)
    if status['blockers']:
        return packaged_render(output, campaign, renderer_root, status)
    start = time.monotonic()
    deadline = start + min(CAP_SECONDS, HARD_DEADLINE - time.time())
    try:
        script = renderer_root / 'postprocess_flrw.py'
        command = [sys.executable, str(script), 'bind', '--mode', 'FULL_PAIR',
                   '--end-zbar', '4', '--output', str(output / 'full_pair_manifest.json')]
        for case in CASES:
            command += ['--case', ','.join((case, str(campaign / 'runs' / case),
                        str(campaign / 'launches' / (case + '.binding.json'))))]
        status['bind'] = bounded_command(command, output / 'bind.log', deadline)
        if status['bind']['returncode']:
            raise RuntimeError('COMPLETED_BINDING_INPUT_CHECK_FAILED')
        status['render'] = bounded_command([
            sys.executable, str(script), 'render', '--manifest', str(output / 'full_pair_manifest.json'),
            '--output', str(output / 'figures_and_diagnostics')], output / 'render.log', deadline)
        receipt = load(output / 'figures_and_diagnostics' / 'POSTPROCESS_RECEIPT.json')
        if (status['render']['returncode'] or receipt.get('status') !=
                'CONDITIONAL_FULL_INTERVAL_DIAGNOSTIC_REVIEW_PENDING'):
            raise RuntimeError('POSTPROCESS_GATE_HELD: ' + str(receipt.get('wait_reason')))
        status.update(status=SUCCESS, completed_utc=utc())
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        for path in (output / 'figures_and_diagnostics').glob('*.png'):
            path.unlink()
        status.update(status='CONTINUATION_FAILED_NO_FULL_PLOTS_OR_ADMISSION', error=str(error))
    status['bind_render_total_wall_s'] = time.monotonic() - start
    return packaged_render(output, campaign, renderer_root, status)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('status', 'check', 'render', 'repackage'))
    parser.add_argument('--campaign', type=Path, default=DEFAULT_CAMPAIGN)
    parser.add_argument('--renderer-root', type=Path, default=DEFAULT_RENDERER_ROOT)
    parser.add_argument('--output', type=Path, help='Fresh directory outside campaign and source results')
    parser.add_argument('--existing-output', type=Path, help='Preserved results; repackage only')
    args = parser.parse_args()
    if args.action in ('render', 'repackage') and args.output is None:
        parser.error(args.action + ' requires --output (fresh, separate directory)')
    if args.action == 'repackage' and args.existing_output is None:
        parser.error('repackage requires --existing-output')
    resource.setrlimit(resource.RLIMIT_AS, (CAP_MEMORY, CAP_MEMORY))
    campaign, root = args.campaign.resolve(), args.renderer_root.resolve()
    try:
        if args.action == 'repackage':
            result = repackage(args.existing_output.resolve(), args.output.resolve(), campaign, root)
        else:
            result = (render(campaign, root, args.output.resolve()) if args.action == 'render'
                      else inspect(campaign, root))
    except (OSError, ValueError) as error:
        if args.action == 'repackage':
            original, status_error = existing_scientific_status(args.existing_output.resolve())
            print(json.dumps({'status': original['status'],
                              'scientific_status': original['status'],
                              'packaging_status': 'PACKAGING_FAILED',
                              'packaging_error': str(error), 'original_error': original.get('error'),
                              'original_status_validation_error': status_error,
                              'source_output': str(args.existing_output.resolve()),
                              'output': str(args.output.resolve()), 'solver_runs': 0}))
            return 2
        print(json.dumps({'status': 'REQUEST_FAILED', 'error': str(error), 'solver_runs': 0}))
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    if args.action == 'repackage':
        return 0 if result['packaging_status'] == 'PACKAGED' else 2
    if result.get('packaging_status') == 'PACKAGING_FAILED':
        return 2
    return 0 if result['status'] in ('READY_FOR_EXPLICIT_ONE_SHOT_DIAGNOSTIC_RENDER', SUCCESS) else 2


if __name__ == '__main__':
    raise SystemExit(main())
