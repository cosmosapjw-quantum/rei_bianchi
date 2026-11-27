"""Two invented exact tasks through C shim / real worker / real collector."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'executor'), str(ROOT / 'mpi_fortran')]
from make_fixture import create_fixture
from export_worklist import export
from core import prepare_manifest, collect


def main():
    names = ['executor/core.py', 'executor/guard.py', 'executor/worker.py',
             'executor/make_fixture.py', 'executor/synthetic_backend.py',
             'mpi_fortran/worker_spawn.c', 'mpi_fortran/spawn_cli.c',
             'mpi_fortran/export_worklist.py']
    hashes = lambda: {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in names}
    before = hashes()
    result = {'scope': 'SYNTHETIC_ONLY', 'actual_HH_runs': 0, 'Fortran_runs': 0,
              'MPI_runs': 0, 'native_callback_runs': 0, 'source_hashes': before}
    with tempfile.TemporaryDirectory(prefix='integration_', dir=Path(__file__).parent) as tmp:
        base = Path(tmp)
        shim = base / 'shim'
        build = ['/usr/bin/gcc', '-std=c11', '-O3', '-fno-fast-math', '-ffp-contract=off',
                 '-Wall', '-Wextra', '-Werror', '-pedantic',
                 str(ROOT / 'mpi_fortran/worker_spawn.c'), str(ROOT / 'mpi_fortran/spawn_cli.c'),
                 '-o', str(shim)]
        subprocess.run(build, check=True, capture_output=True, timeout=20)
        manifest, worklist = base / 'manifest.json', base / 'worklist.txt'
        create_fixture(manifest, base / 'tasks', task_count=2, cpu_units=800)
        exported = export(manifest, worklist)
        assert prepare_manifest(str(manifest))['status'] == 'READY'
        receipts = []
        for line in worklist.read_text().splitlines()[1:]:
            index, deadline = line.split()
            run = subprocess.run([str(shim), str(Path(sys.executable).resolve()),
                                  str(ROOT / 'executor/worker.py'), str(manifest), index, deadline],
                                 capture_output=True, text=True, timeout=40)
            records = [json.loads(line) for line in run.stdout.splitlines()]
            assert run.returncode == 0 and records[-1]['shim_status'] == 0, (run.returncode, run.stdout, run.stderr)
            assert records[0]['status'] == 'COMPLETE', records
            receipts.append({'task_index': int(index), 'shim_status': records[-1]['shim_status'],
                             'worker_status': records[0]['status'], 'payload_sha256': records[0]['payload_sha256']})
        collection = collect(str(manifest))
        assert collection['status'] == 'COLLECTED'
        assert collection['complete_task_count'] == collection['declared_task_count'] == 2
        # Expected payload hashes are mandatory in this fixture and independently
        # calculated from exact rational values and integer sums of squares.
        result.update(status='PASS_BOUNDED_CONTROL_INTEGRATION', dispatch_order=exported['dispatch_order'],
                      receipts=receipts, canonical_payload_digest=collection['canonical_payload_digest'],
                      complete_task_count=2, exact_expected_payloads_matched=True)
        assert before == hashes(), 'source changed during bounded integration probe'
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
