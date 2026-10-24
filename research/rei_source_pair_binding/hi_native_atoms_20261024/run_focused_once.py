"""One released native-atoms child; no automatic retry or science admission.

The marker/identity checks support reproducibility, not security. Root writes
ROOT_GO.json with authorized=true and the exact proposal_sha256 after review.
"""
import datetime
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
RAW = HERE/'raw'
PROPOSAL = HERE/'PROPOSED_EXECUTION.json'
CPU_LIMIT_S = 2
WALL_LIMIT_S = 10


def cpu_limit():
    resource.setrlimit(resource.RLIMIT_CPU,(CPU_LIMIT_S,CPU_LIMIT_S))


def main():
    proposal_bytes = PROPOSAL.read_bytes()
    proposal = json.loads(proposal_bytes)
    go = json.loads((HERE/'ROOT_GO.json').read_text())
    proposal_sha = hashlib.sha256(proposal_bytes).hexdigest()
    if go.get('authorized') is not True or go.get('proposal_sha256') != proposal_sha:
        raise RuntimeError('root release must bind exact preparation proposal')
    for filename, expected in proposal['file_sha256'].items():
        actual = hashlib.sha256((HERE/filename).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError('immutable execution input byte mismatch: '+filename)
    if proposal['cpu_cap_s'] != CPU_LIMIT_S or proposal['wall_cap_s'] != WALL_LIMIT_S:
        raise RuntimeError('frozen resource contract mismatch')
    command = [sys.executable,'-B',str(HERE/'focused_check.py')]
    RAW.mkdir(exist_ok=True)
    with (RAW/'attempt.json').open('x',encoding='utf-8') as handle:
        json.dump({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'single_child_attempt':1,'command':command,'cpu_limit_s':CPU_LIMIT_S,
                   'wall_timeout_s':WALL_LIMIT_S,'proposal_sha256':proposal_sha,
                   'file_sha256':proposal['file_sha256']},handle,indent=2)
        handle.write('\n')
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    stdout = stderr = b''
    process = None
    timeout = False
    launch_error = None
    returncode = None
    try:
        process = subprocess.Popen(command,cwd=HERE,stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,preexec_fn=cpu_limit)
        try:
            stdout,stderr = process.communicate(timeout=max(0.0,WALL_LIMIT_S-(time.monotonic()-start)))
        except subprocess.TimeoutExpired:
            timeout = True
            process.kill()
            stdout,stderr = process.communicate()
        returncode = process.returncode
    except BaseException:
        launch_error = traceback.format_exc()
        if process is not None and process.poll() is None:
            process.kill()
            stdout,stderr = process.communicate()
            returncode = process.returncode
    finally:
        wall_s = time.monotonic()-start
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        (RAW/'stdout.jsonl').write_bytes(stdout)
        (RAW/'stderr.txt').write_bytes(stderr)
        receipt = {'schema':'REI_HI_NATIVE_ATOMS_SINGLE_CHILD_RECEIPT_V1',
            'command':command,'scientific_child_attempts':1,'fixture_groups':1,
            'cpu_rlimit_soft_s':CPU_LIMIT_S,'cpu_rlimit_hard_s':CPU_LIMIT_S,
            'wall_timeout_s':WALL_LIMIT_S,'wall_elapsed_s':wall_s,
            'child_user_cpu_s':after.ru_utime-before.ru_utime,
            'child_system_cpu_s':after.ru_stime-before.ru_stime,
            'child_total_cpu_s':(after.ru_utime-before.ru_utime)+(after.ru_stime-before.ru_stime),
            'returncode':returncode,'timed_out':timeout,'launch_error':launch_error,
            'python_version':sys.version,'python_executable':sys.executable,
            'proposal_sha256':proposal_sha,'file_sha256':proposal['file_sha256'],
            'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'stdout_sha256':hashlib.sha256(stdout).hexdigest(),
            'stderr_sha256':hashlib.sha256(stderr).hexdigest(),
            'known_partial_cpu_s_before':10.318970,'original_sequence_cpu_s':10.110448,
            'original_cap_s':10,'original_overrun_s':0.110448,'original_status':'FAIL_PRESERVED',
            'whole_L0_cpu':'UNKNOWN_NOT_ZERO','original_cumulative_cap':'NOT_FROZEN',
            'parent_model_IO_remote_CAS_cpu':'SEPARATE_UNMEASURED_NOT_ZERO',
            'allocation_transfer':False,'automatic_retry':False,
            'requested_executor':'gpt-6.1-sol high','observed_backend':'NOT_ASSERTED',
            'scientific_admission':'ROOT_DECISION_REQUIRED_NO_ADMISSION_BY_RUNNER'}
        (RAW/'resource_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(json.dumps(receipt,indent=2,sort_keys=True))
    return 0 if returncode == 0 and not timeout and launch_error is None else 1


if __name__ == '__main__':
    sys.exit(main())
