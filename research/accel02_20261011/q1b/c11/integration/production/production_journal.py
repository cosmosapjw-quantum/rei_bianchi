"""Create-only durable attempt transactions over immutable accepted checkpoints.

A rejection advances the controller cursor but never the physical prefix. An
unresolved inflight attempt is never replayed. A completed accepted checkpoint
may reconcile its exact transaction receipt without any numerical work.
"""
from __future__ import annotations
import copy
import hashlib
import json
import os
import time
import traceback
import uuid
from pathlib import Path


class JournalError(ValueError):
    pass


def canonical_bytes(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fsync_dir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


def durable_json(path,value):
    """Publish one immutable complete file atomically, preserving orphan temps."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    with tmp.open('xb') as f:
        f.write(canonical_bytes(value));f.flush();os.fsync(f.fileno())
    # hard link atomically refuses replacement and exposes only complete bytes.
    os.link(tmp,path);fsync_dir(path.parent);tmp.unlink();fsync_dir(path.parent)


def ensure_json(path,value):
    path=Path(path)
    if path.exists():
        if path.read_bytes()!=canonical_bytes(value):raise JournalError('IMMUTABLE_RECORD_MISMATCH:'+str(path))
    else:durable_json(path,value)


def reconcile_output_records(directory,records):
    """Restore lost authoritative records; reject same-schema content mutation."""
    seen=set()
    for record in records:
        i=record['epoch_index']
        if type(i) is not int or i<0 or i in seen:raise JournalError('OUTPUT_RECORD_INDEX')
        seen.add(i);ensure_json(Path(directory)/f'epoch-{i:03d}.json',record)


def validate_cursor(c):
    keys={'schema','attempts','accepted_macros','rejected_macros','accepted_boundaries','accepted_clock_s','next_step_s'}
    if set(c)!=keys or c['schema']!='rei.q1b.c11.adaptive_cursor.v1':raise JournalError('CURSOR_SCHEMA')
    if any(type(c[k]) is not int or c[k]<0 for k in ('attempts','accepted_macros','rejected_macros','accepted_boundaries')):
        raise JournalError('CURSOR_COUNTS')
    if c['attempts']!=c['accepted_macros']+c['rejected_macros'] or c['accepted_boundaries']!=2*c['accepted_macros']:
        raise JournalError('CURSOR_COUNT_IDENTITY')
    import math
    if not all(math.isfinite(c[k]) for k in ('accepted_clock_s','next_step_s')) or c['next_step_s']<=0:
        raise JournalError('CURSOR_CLOCK')


class AttemptJournal:
    def __init__(self,directory,initial_cursor,initial_checkpoint):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        validate_cursor(initial_cursor)
        seed=dict(schema='rei.c12.production_journal_seed.v1',cursor=copy.deepcopy(initial_cursor),
                  checkpoint=copy.deepcopy(initial_checkpoint),replay_policy='UNRESOLVED_INFLIGHT_FAILS_CLOSED')
        ensure_json(self.directory/'SEED.json',seed)
        self.seed=seed;self.head=copy.deepcopy(seed);self.inflight=None
        self._scan()

    def _path(self,number,kind):return self.directory/f'attempt-{number:08d}.{kind}.json'

    def _validate_commit(self,begin,receipt):
        before=begin['cursor'];after=receipt['cursor'];validate_cursor(after)
        yes=receipt['trial']['accepted']
        if type(yes) is not bool:raise JournalError('TRIAL_ACCEPTED_TYPE')
        expected=dict(attempts=before['attempts']+1,
                      accepted_macros=before['accepted_macros']+int(yes),
                      rejected_macros=before['rejected_macros']+int(not yes),
                      accepted_boundaries=before['accepted_boundaries']+2*int(yes))
        if any(after[k]!=v for k,v in expected.items()):raise JournalError('NONMONOTONIC_ATTEMPT_CURSOR')
        if yes:
            if after['accepted_clock_s']<=before['accepted_clock_s']:raise JournalError('ACCEPTED_CLOCK_NOT_ADVANCED')
            if receipt['checkpoint']['generation']!=after['accepted_macros']:raise JournalError('CHECKPOINT_GENERATION')
        else:
            if after['accepted_clock_s']!=before['accepted_clock_s'] or receipt['checkpoint']!=begin['checkpoint']:
                raise JournalError('REJECTED_STATE_MOVED')

    def _scan(self):
        self.head=copy.deepcopy(self.seed);self.inflight=None
        while True:
            number=self.head['cursor']['attempts']+1
            bp=self._path(number,'begin');cp=self._path(number,'commit');fp=self._path(number,'failure')
            if not bp.exists():
                if cp.exists() or fp.exists():raise JournalError('JOURNAL_MISSING_BEGIN')
                break
            begin=json.loads(bp.read_text())
            if begin['cursor']!=self.head['cursor'] or begin['checkpoint']!=self.head['checkpoint']:
                raise JournalError('JOURNAL_BROKEN_LINEAGE')
            if cp.exists():
                row=json.loads(cp.read_text())
                if row['begin_sha256']!=sha(bp):raise JournalError('JOURNAL_BEGIN_HASH')
                self._validate_commit(begin,row['receipt']);self.head=copy.deepcopy(row['receipt'])
                if fp.exists():raise JournalError('JOURNAL_COMMIT_AND_FAILURE')
            else:self.inflight=begin;break
        expected=self.head['cursor']['attempts']+int(self.inflight is not None)
        for path in self.directory.glob('attempt-*.begin.json'):
            if int(path.name.split('.')[0].split('-')[1])>expected:raise JournalError('JOURNAL_SEQUENCE_GAP')

    def resume(self,reconcile=None):
        self._scan()
        if self.inflight is not None:
            number=self.inflight['cursor']['attempts']+1
            if self._path(number,'failure').exists():raise JournalError('FAILED_ATTEMPT_REQUIRES_NEW_EXPLICIT_REPAIR_LANE')
            receipt=reconcile(self.inflight) if reconcile is not None else None
            if receipt is None:raise JournalError('UNRESOLVED_INFLIGHT_NO_IMPLICIT_REPLAY')
            if not receipt['trial']['accepted']:raise JournalError('ONLY_ATOMIC_ACCEPTED_CHECKPOINT_CAN_RECONCILE')
            self.commit(receipt,reconciled=True)
        return copy.deepcopy(self.head)

    def begin(self,request):
        if self.inflight is not None:raise JournalError('INFLIGHT_ALREADY_EXISTS')
        number=self.head['cursor']['attempts']+1
        begin=dict(schema='rei.c12.production_attempt_begin.v1',attempt=number,cursor=copy.deepcopy(self.head['cursor']),
                   checkpoint=copy.deepcopy(self.head['checkpoint']),request=copy.deepcopy(request))
        durable_json(self._path(number,'begin'),begin);self.inflight=begin
        return number

    def commit(self,receipt,*,reconciled=False):
        if self.inflight is None:raise JournalError('NO_INFLIGHT_TO_COMMIT')
        self._validate_commit(self.inflight,receipt)
        number=self.inflight['cursor']['attempts']+1
        row=dict(schema='rei.c12.production_attempt_commit.v1',begin_sha256=sha(self._path(number,'begin')),
                 receipt=copy.deepcopy(receipt),reconciled_from_atomic_checkpoint=bool(reconciled))
        durable_json(self._path(number,'commit'),row);self.head=copy.deepcopy(receipt);self.inflight=None

    def fail(self,exc):
        if self.inflight is None:raise JournalError('NO_INFLIGHT_TO_FAIL')
        number=self.inflight['cursor']['attempts']+1
        failure=dict(type=type(exc).__name__,message=str(exc),notes=getattr(exc,'__notes__',[]),traceback=traceback.format_exc())
        durable_json(self._path(number,'failure'),dict(schema='rei.c12.production_attempt_failure.v1',
            begin_sha256=sha(self._path(number,'begin')),failure=failure,accepted_journal_advanced=False,accepted_checkpoint_status='NOT_CLAIMED_BY_FAILURE_RECORD'))
        return failure


def run_chunk(journal,attempt,*,target,total_attempts,total_macros,new_attempt_cap=3,wall_s=45.,clock=time.monotonic,
              request=None,reconcile=None):
    """Runtime caps only; attempt owns unchanged controller and checkpoint gate.

    Wall stop is cooperative: a started trial always finishes or records failure.
    No pointwise wall-bound or whole-run completion estimate is asserted.
    """
    if type(new_attempt_cap) is not int or new_attempt_cap<=0 or not wall_s>0:raise JournalError('CHUNK_BUDGET_DOMAIN')
    journal.resume();start=clock();done=0;failure=None
    while True:
        c=journal.head['cursor']
        if c['accepted_clock_s']==target:status='REACHED_FULL_TARGET';break
        if c['accepted_clock_s']>target:raise JournalError('PAST_TARGET')
        if c['attempts']>=total_attempts or c['accepted_macros']>=total_macros:status='ALLOCATION_EXHAUSTED';break
        if done>=new_attempt_cap:status='CHUNK_ATTEMPT_BOUNDARY';break
        if clock()-start>=wall_s:status='CHUNK_WALL_BOUNDARY';break
        number=journal.begin(request(c) if request is not None else {'target_time_s':target})
        try:
            receipt=attempt(copy.deepcopy(c),number)
            journal.commit(receipt)
        except Exception as exc:
            if reconcile is not None:
                # A checkpoint may already be durably accepted although an
                # output/attempt/journal publication or print then failed.
                observation=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),
                    accepted_checkpoint_status='RESOLVE_FROM_ATOMIC_CHECKPOINT')
                ensure_json(journal._path(number,'exception'),observation)
                try:
                    journal.resume(reconcile)
                except JournalError as recovery_error:
                    if str(recovery_error)=='UNRESOLVED_INFLIGHT_NO_IMPLICIT_REPLAY':
                        failure=journal.fail(exc);status='FAILED_ATTEMPT'
                    else:
                        failure=dict(observed=observation,recovery_error=str(recovery_error))
                        status='CHECKPOINT_RECONCILIATION_PENDING'
                except Exception as recovery_error:
                    failure=dict(observed=observation,recovery_error=str(recovery_error))
                    status='CHECKPOINT_RECONCILIATION_PENDING'
                else:
                    if journal.head['cursor']['attempts']!=number:
                        raise JournalError('POST_EXCEPTION_RECONCILIATION_COUNT')
                    done+=1;failure=observation;status='CHUNK_RECOVERED_COMMIT_BOUNDARY'
            else:
                failure=journal.fail(exc);status='FAILED_ATTEMPT'
            break
        done+=1
    return dict(schema='rei.c12.production_chunk_result.v1',status=status,cursor=copy.deepcopy(journal.head['cursor']),
        checkpoint=copy.deepcopy(journal.head['checkpoint']),new_completed_attempts=done,failure=failure,
        target_time_s=target,scientific_admission=False,whole_history_gates='NOT_EVALUATED',completed_replays=0)
