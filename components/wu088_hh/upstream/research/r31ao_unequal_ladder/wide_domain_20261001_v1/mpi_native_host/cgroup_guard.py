"""Linux cgroup-v2 job lifetime guard. No process-table or process-group fallback.

Caller supplies an already delegated parent; only a new child is mutated.
Trusted same-UID scientific processes must not migrate themselves out of the job.
This is job supervision, not isolation from malicious same-UID code or SIGKILL
of the supervisor. A service manager must supervise the launcher on production.
"""
import ctypes
import os
from pathlib import Path
import resource
import subprocess
import time
import uuid


class Refusal(ValueError): pass


def text(path):
    with Path(path).open() as f:
        value = f.read(65537)
    if len(value) > 65536: raise Refusal('cgroup metadata cap')
    return value.strip()


def kv(path):
    return {k: int(v) for k, v in (line.split() for line in text(path).splitlines())}


def real_cgroup2(path):
    # f_type is the first native long in Linux statfs; oversized aligned buffer
    # avoids depending on the remainder's architecture-specific layout.
    buf = (ctypes.c_long * 128)()
    libc = ctypes.CDLL(None, use_errno=True)
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        if libc.fstatfs(fd, ctypes.byref(buf)):
            raise OSError(ctypes.get_errno(), 'fstatfs')
        if buf[0] != 0x63677270: raise Refusal('real cgroup v2 filesystem required')
    finally: os.close(fd)


def parent_check(path):
    p = Path(path)
    if not p.is_absolute() or p.resolve(strict=True) != p or not p.is_dir():
        raise Refusal('canonical existing delegated cgroup parent required')
    real_cgroup2(p)
    if text(p/'cgroup.type') != 'domain': raise Refusal('domain cgroup required')
    if not {'cpu', 'memory', 'pids'} <= set(text(p/'cgroup.subtree_control').split()):
        raise Refusal('delegated parent must already enable cpu memory pids')
    if not os.access(p, os.W_OK): raise Refusal('delegated parent is not writable')
    return p


class JobCgroup:
    def __init__(self, parent, *, memory_bytes, ranks, pids):
        if (type(memory_bytes) is not int or not 64*1024**2 <= memory_bytes <= 112*1024**3
                or type(ranks) is not int or not 1 <= ranks <= 64
                or type(pids) is not int or not 32 <= pids <= 4096):
            raise Refusal('bounded strict cgroup caps required')
        self.path = parent_check(parent) / ('wu088-' + uuid.uuid4().hex)
        self.path.mkdir(mode=0o700)
        self.created = True
        try:
            real_cgroup2(self.path)
            if kv(self.path/'cgroup.events')['populated'] != 0:
                raise Refusal('new cgroup unexpectedly populated')
            # Open writable controls before any scientific process can launch.
            self.procs_fd = os.open(self.path/'cgroup.procs', os.O_WRONLY | os.O_CLOEXEC)
            self.kill_fd = os.open(self.path/'cgroup.kill', os.O_WRONLY | os.O_CLOEXEC)
            self.settings = {'memory.max':str(memory_bytes), 'memory.swap.max':'0',
                'memory.oom.group':'1', 'pids.max':str(pids),
                'cpu.max':str(ranks*100000)+' 100000',
                'cgroup.max.descendants':'0', 'cgroup.max.depth':'0'}
            for name, value in self.settings.items():
                (self.path/name).write_text(value+'\n')
                if text(self.path/name) != value: raise Refusal('cgroup cap readback mismatch: '+name)
        except BaseException:
            for name in ('procs_fd', 'kill_fd'):
                if hasattr(self, name): os.close(getattr(self, name))
            self.path.rmdir()
            raise

    def enter(self):
        # Kernel interprets zero as this calling process. It is independent of
        # /proc's mounted PID namespace. Runs before exec/fork of MPI workers.
        fd=os.open(self.path/'cgroup.procs', os.O_WRONLY | os.O_CLOEXEC)
        try: os.write(fd, b'0\n')
        finally: os.close(fd)

    def populated(self): return kv(self.path/'cgroup.events')['populated'] != 0

    def kill_and_empty(self, seconds=5):
        os.write(self.kill_fd, b'1\n')
        end = time.monotonic()+seconds
        while self.populated() and time.monotonic() < end: time.sleep(.02)
        if self.populated(): raise Refusal('CGROUP_CLEANUP_NOT_EMPTY')

    def snapshot(self):
        return {'path':str(self.path), 'settings':self.settings,
            'events':kv(self.path/'cgroup.events'), 'memory_events':kv(self.path/'memory.events'),
            'pids_events':kv(self.path/'pids.events'), 'memory_current':int(text(self.path/'memory.current'))}

    def close(self):
        if self.populated(): raise Refusal('refusing to remove populated cgroup')
        os.close(self.procs_fd); os.close(self.kill_fd)
        self.path.rmdir()


def execute_contained(argv, *, group, output, seconds, cpus, env, file_cap=64*1024**2):
    """Internal argv seam; CLI only constructs a fixed MPI invocation.

    The forked child joins the cgroup before exec. Popen preexec_fn therefore
    requires a single-threaded host, checked before process creation.
    """
    import threading
    if threading.active_count() != 1: raise Refusal('single-threaded supervisor required')
    if not 1 <= seconds <= 86400 or not cpus: raise Refusal('bounded wall/CPU plan required')
    output = Path(output)
    proc = None; start = time.monotonic(); reason = 'COMPLETED'; cleanup = False; failure = None
    def child_setup():
        group.enter()
        os.sched_setaffinity(0, set(cpus))
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_cap, file_cap))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    try:
        with (output/'stdout.log').open('xb') as out, (output/'stderr.log').open('xb') as err:
            proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                cwd=output, env=env, shell=False, close_fds=True, preexec_fn=child_setup)
            while proc.poll() is None:
                if time.monotonic()-start >= seconds: reason='JOB_WALL_LIMIT'; break
                if max(os.fstat(out.fileno()).st_size, os.fstat(err.fileno()).st_size) >= file_cap:
                    reason='LOG_LIMIT'; break
                if group.snapshot()['memory_events'].get('oom_kill', 0): reason='MEMORY_OOM'; break
                time.sleep(.05)
            if reason == 'COMPLETED' and proc.returncode != 0: reason='MPI_NONZERO_EXIT'
            if reason == 'COMPLETED' and group.populated(): reason='SURVIVING_JOB_DESCENDANTS'
    except BaseException as exc:
        reason='LAUNCH_OR_SUPERVISION_ERROR'; failure=type(exc).__name__+': '+str(exc)
    finally:
        # Covers Python exceptions, SIGINT and handled SIGTERM, including a
        # leader that already exited while a setsid grandchild is still live.
        group.kill_and_empty()
        cleanup = True
        if proc is not None: proc.wait(timeout=5)
    state = group.snapshot()
    if reason == 'COMPLETED' and (state['memory_events'].get('oom_kill',0) or state['pids_events'].get('max',0)):
        reason = 'RESOURCE_EVENT'
    return {'status':reason, 'returncode':proc.returncode if proc is not None else None,
        'process_started':proc is not None, 'failure':failure, 'wall_seconds':time.monotonic()-start,
        'wall_cap_seconds':seconds, 'cleanup_populated_zero':cleanup,
        'aggregate_memory_hard_cap':True, 'cgroup':state}
