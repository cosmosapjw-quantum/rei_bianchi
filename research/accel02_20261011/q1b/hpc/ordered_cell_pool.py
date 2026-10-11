"""Persistent, ordered process actors for unchanged independent cell arithmetic.

Each actor owns one SIGMA subprocess and one resident prepared-cell shard. No
pipe, absorption global, prepared object, reduction or mutable state is shared
between actors. The coordinator assembles responses in original cell order.
Linux process groups ensure failed actors cannot orphan SIGMA descendants.
"""
from __future__ import annotations
import copy
import importlib.util
import math
import multiprocessing as mp
from multiprocessing.connection import wait
import os
from pathlib import Path
import signal
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
Q1B = HERE.parent
DEFAULT_ABSORPTION = Q1B/'c12/repair/opacity_candidate_v3/positive_absorption_v3.py'
DEFAULT_BINARY = Q1B.parent/'n1/native/target/release/rei_n1_native'


class PoolError(RuntimeError):
    def __init__(self, message, receipt):
        super().__init__(message)
        self.receipt = receipt


def _module(path):
    name = '_hpc_actor_absorption'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _actor(connection, rank, absorption_path, binary, opacity_factory):
    # Never fork a live native pipe. Every actor owns a process group, including
    # SIGMA and any descendants, before opening its provider subprocess.
    os.setsid()
    opacity = api = None
    counters = dict(prepare_cells_started=0, prepare_cells_completed=0,
                    absorb_cells_started=0, absorb_cells_completed=0,
                    prepare_s=0., absorb_s=0.)
    resident = []

    def statistics():
        return dict(counters, native_calls=int(getattr(opacity, 'native_calls', 0)),
                    energy_evaluations=int(getattr(opacity, 'energy_evaluations', 0)))

    def drain():
        return api.pop_refinement_records() if api is not None and hasattr(api, 'pop_refinement_records') else []

    try:
        for path in (Q1B, Q1B/'c10', Q1B/'c11/endpoint', Q1B.parent/'n1'):
            sys.path.insert(0, str(path))
        api = _module(absorption_path)
        if opacity_factory is None:
            from opacity_native import NativeOpacity
            opacity = NativeOpacity(binary)
        else:
            # Explicit dependency injection for manufactured tests, never a
            # fallback from failure of the pinned native provider.
            opacity = opacity_factory(binary)
        connection.send(dict(id=0, rank=rank, ok=True, stats=statistics(),
                             pid=os.getpid(), pgid=os.getpgrp(), refinements=[]))
        while True:
            message = connection.recv()
            command = message['command']
            number = message['id']
            rows = []
            refinements = []
            index = None
            started = time.monotonic()
            try:
                if command == 'stop':
                    opacity.close()
                    opacity = None
                    connection.send(dict(id=number, rank=rank, ok=True, stats=statistics(), rows=[], refinements=[]))
                    break
                if command == 'prepare':
                    resident = []
                    if drain():
                        raise RuntimeError('ACTOR_STALE_REFINEMENTS')
                    for index, request in message['cells']:
                        counters['prepare_cells_started'] += 1
                        try:
                            prepared = api.prepare_incident(**request, opacity=opacity)
                        finally:
                            refinements.extend((index, r) for r in drain())
                        resident.append((index, prepared))
                        counters['prepare_cells_completed'] += 1
                        rows.append((index, copy.deepcopy(prepared.diagnostics)))
                elif command == 'absorb':
                    if len(resident) != message['expected_cells']:
                        raise RuntimeError('ACTOR_RESIDENT_SHARD_NOT_PREPARED')
                    for index, prepared in resident:
                        counters['absorb_cells_started'] += 1
                        try:
                            value = api.absorb(prepared, message['lower'], message['h'])
                        finally:
                            refinements.extend((index, r) for r in drain())
                        counters['absorb_cells_completed'] += 1
                        rows.append((index, value))
                else:
                    raise ValueError('UNKNOWN_ACTOR_COMMAND')
                elapsed = time.monotonic()-started
                counters[command+'_s'] += elapsed
                connection.send(dict(id=number, rank=rank, ok=True, rows=rows,
                                     stats=statistics(), elapsed_s=elapsed, refinements=refinements))
            except BaseException as exc:
                elapsed = time.monotonic()-started
                if command in ('prepare', 'absorb'):
                    counters[command+'_s'] += elapsed
                connection.send(dict(id=number, rank=rank, ok=False, rows=rows,
                    stats=statistics(), elapsed_s=elapsed, refinements=refinements,
                    failure=dict(type=type(exc).__name__, message=str(exc),
                        cell_index=index, notes=getattr(exc, '__notes__', []), traceback=traceback.format_exc())))
                break  # no actor reuse or hidden retry after any failure
    except BaseException as exc:
        try:
            connection.send(dict(id=0, rank=rank, ok=False, stats=statistics(), rows=[], refinements=[],
                failure=dict(type=type(exc).__name__, message=str(exc), cell_index=None,
                             notes=getattr(exc, '__notes__', []), traceback=traceback.format_exc())))
        except (BrokenPipeError, EOFError, OSError):
            pass
    finally:
        if opacity is not None:
            try:
                opacity.close()
            except BaseException:
                pass
        connection.close()


class Pool:
    """One coordinator, fixed routing, private native providers, no retries.

    prepare(requests) returns ordered preparation diagnostics. The matching
    prepared objects remain actor-local until the next prepare. absorb(lower,h)
    returns ordered full absorption results. timeout_s bounds each collective
    operation, not individual calls or complete production chunks.

    opacity_factory is an explicit manufactured-test seam. Production drivers
    must require metrics['opacity_binding']=='PINNED_NATIVE_OPACITY'.
    """
    def __init__(self, workers=8, timeout_s=120., opacity_binary=DEFAULT_BINARY,
                 absorption_path=DEFAULT_ABSORPTION, *, opacity_factory=None):
        if type(workers) is not int or not 1 <= workers <= 48:
            raise ValueError('HPC_WORKERS_REQUIRE_INTEGER_1_TO_48')
        if not math.isfinite(timeout_s) or timeout_s <= 0:
            raise ValueError('HPC_TIMEOUT_POSITIVE_FINITE')
        if os.name != 'posix':
            raise ValueError('HPC_ACTOR_PROCESS_GROUPS_REQUIRE_POSIX')
        self.workers, self.timeout_s = workers, float(timeout_s)
        self.opacity_binary = str(Path(opacity_binary).resolve())
        self.absorption_path = str(Path(absorption_path).resolve())
        self.opacity_factory = opacity_factory
        self._actors = []
        self._sequence = 0
        self._prepared_count = None
        self._stats = {}
        self._refinements = []
        self._closed = self._broken = False
        self._timings = dict(startup_s=0., prepare_wall_s=0., absorb_wall_s=0.)
        self.last_timings = {}
        self.failure_receipt = None
        self.cleanup_receipt = None

    @property
    def native_calls(self):
        return sum(s.get('native_calls', 0) for s in self._stats.values())

    @property
    def energy_evaluations(self):
        return sum(s.get('energy_evaluations', 0) for s in self._stats.values())

    @property
    def metrics(self):
        return dict(workers=self.workers, native_calls=self.native_calls,
            energy_evaluations=self.energy_evaluations, timings=copy.deepcopy(self._timings),
            worker_statistics=copy.deepcopy(self._stats),
            opacity_binding='PINNED_NATIVE_OPACITY' if self.opacity_factory is None else 'INJECTED_TEST_OPACITY',
            counter_status='PARTIAL_RECEIPTS_ONLY' if self._broken and self.failure_receipt.get('unobserved_workers') else 'EXACT_RECEIVED_ACTOR_COUNTERS',
            broken=self._broken, closed=self._closed)

    def pop_refinement_records(self):
        records, self._refinements = self._refinements, []
        return records

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        if self._closed or self._broken:
            raise PoolError('HPC_POOL_CLOSED_NO_RETRY', self.failure_receipt or {})
        if self._actors:
            return self
        started = time.monotonic()
        context = mp.get_context('spawn')
        try:
            for rank in range(self.workers):
                parent, child = context.Pipe(duplex=True)
                process = context.Process(target=_actor, args=(child, rank, self.absorption_path,
                    self.opacity_binary, self.opacity_factory), name=f'rei-cell-{rank:02d}')
                process.start()
                child.close()
                self._actors.append(dict(rank=rank, process=process, connection=parent))
            self._receive(0, 'startup', started)
            self._timings['startup_s'] = time.monotonic()-started
        except BaseException:
            self.close()
            raise
        return self

    def _receive(self, number, command, started):
        pending = {a['connection']: a for a in self._actors}
        replies = {}
        faults = []
        deadline = started+self.timeout_s
        while pending:
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                break
            ready = wait(list(pending), timeout=remaining)
            if not ready:
                break
            for connection in ready:
                actor = pending.pop(connection)
                rank = actor['rank']
                try:
                    reply = connection.recv()
                    if reply.get('id') != number or reply.get('rank') != rank:
                        raise ValueError('ACTOR_RESPONSE_ROUTING_MISMATCH')
                    replies[rank] = reply
                    self._stats[rank] = reply['stats']
                except (EOFError, OSError, ValueError) as exc:
                    faults.append(dict(rank=rank, type=type(exc).__name__, message=str(exc)))
        ordered = [replies[k] for k in sorted(replies)]
        refinements = [(index, position, record) for reply in ordered
                       for position, (index, record) in enumerate(reply.get('refinements', []))]
        self._refinements.extend(record for _, _, record in sorted(refinements, key=lambda v:(v[0],v[1])))
        failed = [dict(rank=r['rank'], **r['failure']) for r in ordered if not r['ok']]
        self.last_timings = dict(operation=command, wall_s=time.monotonic()-started,
                                 worker_elapsed_s={r['rank']:r.get('elapsed_s',0.) for r in ordered})
        if pending or faults or failed:
            unobserved = sorted([a['rank'] for a in pending.values()]+[f['rank'] for f in faults])
            self.failure_receipt = dict(operation=command, request_id=number,
                failures=sorted(failed, key=lambda f:(f['cell_index'] if f['cell_index'] is not None else -1, f['rank'])),
                transport_faults=sorted(faults,key=lambda f:f['rank']),
                unobserved_workers=unobserved, timed_out_workers=sorted(a['rank'] for a in pending.values()),
                received_worker_statistics=copy.deepcopy(self._stats),
                completed_cell_indices=sorted(index for r in ordered for index,_ in r.get('rows',[])),
                no_retry=True, counter_status='PARTIAL_RECEIPTS_ONLY' if unobserved else 'EXACT_RECEIVED_ACTOR_COUNTERS')
            self._broken = True
            self.close()
            raise PoolError('HPC_ACTOR_OPERATION_FAILED_CLOSED', copy.deepcopy(self.failure_receipt))
        return ordered

    def _operation(self, command, messages):
        self.start()
        self._sequence += 1
        started = time.monotonic()
        try:
            for actor, payload in zip(self._actors, messages, strict=True):
                actor['connection'].send(dict(id=self._sequence, command=command, **payload))
        except BaseException as exc:
            self.failure_receipt = dict(operation=command, request_id=self._sequence,
                transport_send_failure=dict(type=type(exc).__name__,message=str(exc)),
                unobserved_workers=list(range(self.workers)),no_retry=True)
            self._broken = True
            self.close()
            raise PoolError('HPC_ACTOR_SEND_FAILED_CLOSED',copy.deepcopy(self.failure_receipt)) from exc
        replies = self._receive(self._sequence, command, started)
        self._timings[command+'_wall_s'] += time.monotonic()-started
        rows = [v for r in replies for v in r.get('rows',[])]
        rows.sort(key=lambda v:v[0])
        expected = self._prepared_count
        if [index for index,_ in rows] != list(range(expected)):
            self.failure_receipt = dict(operation=command, error='ORDERED_CELL_COVERAGE',no_retry=True,
                                        unobserved_workers=[])
            self._broken = True
            self.close()
            raise PoolError('HPC_ORDERED_CELL_COVERAGE',copy.deepcopy(self.failure_receipt))
        return [value for _,value in rows]

    def prepare(self, requests):
        requests = list(requests)
        if not requests:
            raise ValueError('HPC_EMPTY_CELL_REQUESTS')
        self._prepared_count = len(requests)
        shards = [[] for _ in range(self.workers)]
        for index, request in enumerate(requests):
            # Fixed cyclic routing balances isolated expensive threshold cells.
            shards[index % self.workers].append((index, dict(request)))
        return self._operation('prepare',[dict(cells=s) for s in shards])

    def absorb(self, lower, h):
        if self._prepared_count is None:
            raise ValueError('HPC_ABSORB_REQUIRES_PREPARED_MAP')
        sizes = [len(range(rank,self._prepared_count,self.workers)) for rank in range(self.workers)]
        return self._operation('absorb',[dict(lower=lower,h=h,expected_cells=n) for n in sizes])

    def close(self):
        if self._closed:
            return
        self._closed = True
        graceful = not self._broken
        if graceful:
            for actor in self._actors:
                try:
                    actor['connection'].send(dict(id=-1,command='stop'))
                except (BrokenPipeError,EOFError,OSError):
                    graceful = False
            deadline = time.monotonic()+min(5.,self.timeout_s)
            for actor in self._actors:
                actor['process'].join(max(0.,deadline-time.monotonic()))
        cleanup = []
        for actor in self._actors:
            process = actor['process']
            # Actor-created group remains addressable even if the actor died
            # abruptly while its SIGMA child was still alive.
            signalled = []
            for signum in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(process.pid, signum)
                    signalled.append(int(signum))
                except ProcessLookupError:
                    pass
                except PermissionError:
                    if process.is_alive():
                        process.kill()
                process.join(.2)
            if process.is_alive():
                process.kill()
                process.join(1.)
            actor['connection'].close()
            cleanup.append(dict(rank=actor['rank'],pid=process.pid,exitcode=process.exitcode,
                                alive=process.is_alive(),group_signals=signalled))
        self.cleanup_receipt = dict(graceful_requested=graceful,actors=cleanup,
                                   all_actors_stopped=all(not r['alive'] for r in cleanup))
