"""Linux process-group guard. RSS is sampled, AS/CPU/file size are kernel limits."""
import os
from pathlib import Path
import resource
import signal
import subprocess
import time


class Cancelled(Exception):
    pass


def group_state(pgid):
    """Bounded /proc scan: aggregate RSS of visible same-group processes."""
    rss, live, scanned = 0, [], 0
    namespace = os.readlink("/proc/self/ns/pid")
    with os.scandir("/proc") as entries:
        for entry in entries:
            if not entry.name.isdigit():
                continue
            scanned += 1
            if scanned > 65536:
                raise RuntimeError("PROCESS_SCAN_LIMIT")
            try:
                if os.readlink(Path(entry.path, "ns/pid")) != namespace:
                    continue
                lines = Path(entry.path, "status").read_text().splitlines()
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                continue
            fields = {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in lines if ":" in line}
            # /proc can be mounted in an ancestor PID namespace. Numeric
            # directory names and stat.pgrp then differ from getpid/getpgid.
            group = int(fields["NSpgid"].split()[-1])
            pid = int(fields["NSpid"].split()[-1])
            if group == pgid and fields["State"].split()[0] not in ("Z", "X"):
                rss += int(fields.get("VmRSS", "0 kB").split()[0]) * 1024
                live.append(pid)
    return rss, live


def kill_group(process):
    if process is None:
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass


def run(argv, cwd, env, limits, stdout_path, stderr_path):
    if os.name != "posix" or not Path("/proc/self/stat").is_file():
        raise RuntimeError("LINUX_PROC_GUARD_REQUIRED")
    process = None
    started = time.monotonic()
    reason = "CHILD_EXIT"
    maximum_rss = maximum_processes = 0
    previous = {}
    def interrupted(signum, frame):
        raise Cancelled("supervisor signal " + str(signum))
    for sig in (signal.SIGTERM, signal.SIGINT):
        previous[sig] = signal.signal(sig, interrupted)
    def child_limits():
        resource.setrlimit(resource.RLIMIT_AS, (limits["address_space_bytes"],) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (limits["wall_seconds"] + 1,) * 2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (limits["max_output_bytes"],) * 2)
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)
    try:
        with open(stdout_path, "xb") as out, open(stderr_path, "xb") as err:
            # No cancellation gap between successful spawn and registering pid.
            oldmask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM, signal.SIGINT})
            try:
                process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                    stdout=out, stderr=err, shell=False, start_new_session=True,
                    preexec_fn=child_limits)
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)
            while True:
                rss, members = group_state(process.pid)
                maximum_rss = max(maximum_rss, rss)
                maximum_processes = max(maximum_processes, len(members))
                if rss > limits["rss_bytes"]:
                    reason = "RSS_LIMIT"
                    break
                code = process.poll()
                if code is not None:
                    # A pre-poll snapshot can miss a last-moment fork. After
                    # leader exit, also ask the kernel whether its group exists.
                    final_rss, survivors = group_state(process.pid)
                    maximum_rss = max(maximum_rss, final_rss)
                    try:
                        os.killpg(process.pid, 0)
                        group_exists = True
                    except ProcessLookupError:
                        group_exists = False
                    if survivors or group_exists:
                        reason = "DESCENDANTS_SURVIVE_LEADER"
                    break
                if time.monotonic() - started >= limits["wall_seconds"]:
                    reason = "WALL_TIMEOUT"
                    break
                time.sleep(limits["poll_ms"] / 1000)
    except Cancelled:
        reason = "CANCELLED"
    except (OSError, ValueError, RuntimeError, IndexError) as exc:
        reason = "GUARD_ERROR:" + str(exc)[:500]
    finally:
        kill_group(process)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return {
        "returncode": None if process is None else process.returncode,
        "reason": reason, "wall_seconds": time.monotonic() - started,
        "maximum_sampled_group_rss_bytes": maximum_rss,
        "maximum_sampled_group_processes": maximum_processes,
        "limits": limits, "hard_per_process_address_space": True,
        "hard_aggregate_rss": False, "rss_poll_ms": limits["poll_ms"],
        "process_scope": "same-process-group descendants; deliberate session/group escape forbidden",
        "sigkill_worker_cleanup_guaranteed": False,
    }
