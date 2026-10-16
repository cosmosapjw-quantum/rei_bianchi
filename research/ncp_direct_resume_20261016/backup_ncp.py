#!/usr/bin/env python3
"""Preserve existing NCP outputs locally; never launch a solver or upload data.

compact is a bounded recovery snapshot, never a full-history backup. full copies
all regular scientific output files of terminal declared cases, optionally one
--case at a time. Archives stream to a fresh path outside every input root.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tarfile
import time

GIB = 1024 ** 3
STAGE = Path('/root/REI_FLRW_COVARIANT_20261015_005')
CASES = ('FLRW_FULL_Q512_001', 'FLRW_FULL_Q1024_001')
PROFILES = tuple(Path('/root/REI_FLRW_HPC_PROFILE_20261015_' + n) for n in ('002', '003'))
PRIVATE = ('credential', 'private', 'id_rsa', 'id_ed25519', 'ssh', 'environment', '.env', 'token', 'secret')


class BackupStop(Exception):
    def __init__(self, status, detail):
        self.status, self.detail = status, detail
        super().__init__(detail)


def public(path):
    return not any(any(word in part.lower() for word in PRIVATE) for part in path.parts)


def process_matches(stage, campaign, cases, proc_root=Path('/proc')):
    """Read only argv/state; do not retain a terminal environment or private logs."""
    found = []
    try:
        processes = list(proc_root.iterdir())
    except OSError as exc:
        raise BackupStop('PROCESS_OBSERVATION_UNAVAILABLE', str(exc))
    for p in processes:
        if not p.name.isdigit():
            continue
        try:
            argv = [v.decode(errors='replace') for v in (p / 'cmdline').read_bytes().split(b'\0') if v]
        except FileNotFoundError:
            continue  # process exited during observation
        except PermissionError as exc:
            raise BackupStop('PROCESS_OBSERVATION_UNAVAILABLE', str(exc))
        native = str(stage / 'target/release/examples/axbi_reionization') in argv
        for case in cases:
            output = str(campaign / 'runs' / case)
            if native and output in argv:
                try:
                    state = (p / 'stat').read_text().rsplit(')', 1)[1].split()[0]
                except FileNotFoundError:
                    continue
                except OSError as exc:
                    raise BackupStop('PROCESS_OBSERVATION_UNAVAILABLE', str(exc))
                if state != 'Z':
                    found.append({'pid': int(p.name), 'case': case})
    return found


class BoundedWriter:
    def __init__(self, raw, directory, deadline, budget):
        self.raw, self.directory, self.deadline, self.budget = raw, directory, deadline, budget
        self.written = 0
        self.stopped = None

    def check(self, extra=0):
        if self.stopped:
            raise self.stopped
        status = None
        if time.monotonic() >= self.deadline:
            status = ('PARTIAL_RUNTIME_LIMIT', 'archive runtime limit reached')
        elif self.written + extra > self.budget:
            status = ('PARTIAL_ARCHIVE_BUDGET', 'compressed archive byte budget reached')
        elif shutil.disk_usage(self.directory).free - extra < 8 * GIB:
            status = ('PARTIAL_DISK_FLOOR', 'preserve 8 GiB actual free disk')
        if status:
            self.stopped = BackupStop(*status)
            raise self.stopped

    def write(self, data):
        self.check(len(data))
        count = self.raw.write(data)
        self.written += count
        return count

    def flush(self):
        self.raw.flush()


def backup(mode, stage, output, case=None, code_root=None, code_archive=None,
           evidence_roots=PROFILES, max_seconds=1800, max_archive_bytes=16 * GIB,
           max_compact_file_bytes=64 * 1024 ** 2, proc_root=Path('/proc')):
    started = time.monotonic()
    stage, output = Path(stage).resolve(), Path(output).resolve()
    campaign = stage / 'full_campaign001'
    cases = [case] if case else list(CASES)
    roots = [stage, *(Path(p).resolve() for p in evidence_roots)]
    if code_root:
        roots.append(Path(code_root).resolve())
    partial = Path(str(output) + '.partial')
    receipt = Path(str(output) + '.status.json')
    result = {'schema': 'rei.ncp_local_backup.v1', 'mode': mode,
              'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'archive': str(output), 'partial': str(partial), 'cases': cases,
              'scientific_admission': 'NOT_ISSUED', 'ncp_execution': 'LOCAL_ONLY',
              'missing': [], 'excluded': [], 'files': [], 'originals_modified': False}
    if mode not in ('compact', 'full') or any(c not in CASES for c in cases):
        raise ValueError('only compact/full and the two declared cases are supported')
    if max_seconds <= 0 or max_archive_bytes <= 0:
        raise ValueError('positive runtime and archive-byte caps required')
    if any(output == r or r in output.parents for r in roots):
        raise ValueError('archive must be outside the original stage, profile and code roots')
    if code_archive and Path(code_archive).resolve() in (output, partial, receipt):
        raise ValueError('archive output cannot replace code archive')
    if any(p.exists() for p in (output, partial, receipt)):
        raise ValueError('archive, partial and status paths must all be fresh')
    if not output.parent.is_dir():
        raise ValueError('archive parent directory must already exist')
    selected = {}

    def add(path, arcname, required=False):
        if time.monotonic() - started >= max_seconds:
            raise BackupStop('PARTIAL_RUNTIME_LIMIT', 'backup runtime limit reached')
        p = Path(path)
        if not p.is_file() or p.is_symlink():
            if required:
                result['missing'].append(str(p))
            return
        if not public(Path(arcname)):
            result['excluded'].append(str(p))
            return
        if mode == 'compact' and p.stat().st_size > max_compact_file_bytes:
            result['excluded'].append(str(p) + ': compact per-file cap')
            return
        selected[arcname] = p

    try:
        if not stage.is_dir():
            raise BackupStop('BACKUP_INPUT_FAILURE', 'stage missing: ' + str(stage))
        live = process_matches(stage, campaign, cases, proc_root)
        result['live_processes'] = live
        result['snapshot_kind'] = ('LIVE_SNAPSHOT_NOT_FULL_HISTORY' if live else
                                   'COMPACT_SNAPSHOT_NOT_FULL_HISTORY' if mode == 'compact' else
                                   'TERMINAL_CASE_SCIENTIFIC_OUTPUTS')
        if mode == 'full':
            if live:
                raise BackupStop('REJECTED_ACTIVE_SCIENCE', 'full requires terminal cases and no matching scientific process')
            for c in cases:
                p = campaign / 'launches' / (c + '.receipt.json')
                try:
                    terminal = json.loads(p.read_text())
                    if not isinstance(terminal['returncode'], int) or not terminal.get('terminal_utc'):
                        raise ValueError('terminal returncode and terminal_utc required')
                    if not (campaign / 'runs' / c).is_dir():
                        raise ValueError('declared case output directory missing')
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    raise BackupStop('REJECTED_TERMINAL_EVIDENCE_MISSING', str(p) + ': ' + str(exc))
        for name in ('full_control.py', 'ncp_helpers.py',
                     'build_receipt.json', 'source_identity.txt', 'stage/SOURCE_SHA256SUMS.txt'):
            add(stage / name, 'stage005/' + name, required=True)
        add(stage / 'full_resource_plan.json', 'stage005/full_resource_plan.json')
        for name in ('full_control.py', 'ncp_helpers.py'):
            add(campaign / name, 'stage005/full_campaign001/' + name)
        for p in sorted(stage.glob('*build*.log')):
            add(p, 'stage005/' + p.name)
        for name in ('full_resource_plan.json', 'campaign_epoch.json', 'full_campaign.binding.json', 'full_campaign.status.json',
                     'full_campaign.receipt.json', 'host_preflight_before_launch.json'):
            add(campaign / name, 'stage005/full_campaign001/' + name, required=True)
        for p in sorted((campaign / 'configs').glob('*')):
            add(p, 'stage005/full_campaign001/configs/' + p.name)
        for c in cases:
            for suffix in ('.receipt.json', '.binding.json', '.runtime.cfg', '.log'):
                name = c + suffix
                add(campaign / 'launches' / name, 'stage005/full_campaign001/launches/' + name, required=True)
            out = campaign / 'runs' / c
            if mode == 'full':
                def walk_error(exc):
                    raise exc
                for directory, dirs, names in os.walk(out, onerror=walk_error):
                    dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
                    for name in sorted(names):
                        p = Path(directory) / name
                        add(p, 'stage005/full_campaign001/runs/' + c + '/' + str(p.relative_to(out)))
            else:
                for name in ('config.cfg', 'source_identity.txt', 'checkpoint.txt', 'RETURN.txt'):
                    add(out / name, 'stage005/full_campaign001/runs/' + c + '/' + name, required=True)
        # Preserve caller/build failures in historical stages, without sweeping private terminal logs.
        for root in roots[1:1 + len(evidence_roots)]:
            if not root.is_dir():
                result['missing'].append(str(root))
                continue
            for p in sorted(root.iterdir()):
                if p.suffix in ('.py', '.sh', '.cfg', '.json', '.log', '.txt', '.toml', '.lock'):
                    add(p, 'historical/' + root.name + '/' + p.name)
            add(root / 'src/hpc_profile.rs', 'historical/' + root.name + '/src/hpc_profile.rs', required=True)
        if code_root:
            cr = Path(code_root).resolve()
            if not cr.is_dir():
                raise BackupStop('CODE_ROOT_MISSING', str(cr))
            for directory, dirs, names in os.walk(cr):
                dirs[:] = sorted(d for d in dirs if d not in ('.git', 'target', 'node_modules', '__pycache__', '.venv') and not (Path(directory) / d).is_symlink() and public(Path(d)))
                for name in sorted(names):
                    p = Path(directory) / name
                    add(p, 'code/' + str(p.relative_to(cr)))
        if code_archive:
            ca = Path(code_archive).resolve()
            if not ca.is_file():
                raise BackupStop('CODE_ARCHIVE_MISSING', str(ca))
            add(ca, 'code_archive/' + ca.name, required=True)
        result['code_dependencies'] = ('SUPPLIED_CODE_ROOT' if code_root else 'SUPPLIED_EXISTING_ARCHIVE' if code_archive else 'NOT_SUPPLIED_SOURCE_IDENTITY_ONLY')
        with partial.open('xb') as raw:
            sink = BoundedWriter(raw, output.parent, started + max_seconds, max_archive_bytes)
            sink.check()
            with tarfile.open(fileobj=sink, mode='w|gz') as archive:
                for name, p in sorted(selected.items()):
                    sink.check()
                    # Read only the pre-header size: live snapshot files may grow while copied.
                    info = archive.gettarinfo(str(p), arcname=name)
                    h = hashlib.sha256()
                    class Reader:
                        def __init__(self, f):
                            self.f = f
                        def read(self, n):
                            sink.check()
                            chunk = self.f.read(n)
                            h.update(chunk)
                            return chunk
                    with p.open('rb') as f:
                        archive.addfile(info, Reader(f))
                    result['files'].append({'member': name, 'bytes': info.size, 'sha256': h.hexdigest()})
                if mode == 'full' and process_matches(stage, campaign, cases, proc_root):
                    raise BackupStop('PARTIAL_SCIENCE_BECAME_ACTIVE', 'matching science appeared during full backup')
                data = (json.dumps(result, indent=2) + '\n').encode()
                info = tarfile.TarInfo('BACKUP_MANIFEST.json')
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            raw.flush()
            os.fsync(raw.fileno())
            result['archive_bytes'] = sink.written
        partial.rename(output)
        result['status'] = 'ARCHIVE_CREATED'
    except KeyboardInterrupt:
        result.update(status='PARTIAL_INTERRUPTED', error='owner interrupted backup')
    except BackupStop as exc:
        result.update(status=exc.status, error=exc.detail)
    except (OSError, ValueError, tarfile.TarError) as exc:
        result.update(status='PARTIAL_IO_FAILURE' if partial.exists() else 'BACKUP_INPUT_FAILURE', error=str(exc))
    result['elapsed_s'] = time.monotonic() - started
    result['partial_retained'] = partial.exists()
    with receipt.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('compact', 'full'))
    p.add_argument('--stage', type=Path, default=STAGE)
    p.add_argument('--output', type=Path, required=True, help='fresh .tar.gz outside inputs')
    p.add_argument('--case', choices=CASES)
    p.add_argument('--code-root', type=Path, help='local source package including config/data/path dependencies')
    p.add_argument('--code-archive', type=Path, help='existing local Git/source archive to preserve')
    p.add_argument('--evidence-root', type=Path, action='append', help='historical profile root; defaults to attempts002/003')
    p.add_argument('--max-seconds', type=float, default=1800)
    p.add_argument('--max-archive-gib', type=float, default=16)
    a = p.parse_args()
    try:
        result = backup(a.mode, a.stage, a.output, a.case, a.code_root, a.code_archive,
                        PROFILES if a.evidence_root is None else a.evidence_root,
                        a.max_seconds, int(a.max_archive_gib * GIB))
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps({k: result[k] for k in ('status', 'archive', 'partial_retained')}))
    return 0 if result['status'] == 'ARCHIVE_CREATED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
