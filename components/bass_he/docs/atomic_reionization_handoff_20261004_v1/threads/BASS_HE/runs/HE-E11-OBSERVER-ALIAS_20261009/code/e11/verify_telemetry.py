"""Fail-closed byte-source consumer of proposed E11 internal Rust telemetry.

A successful synthetic test is NOT a native E11 run. The native emitter must
be compiled and executed in a pinned NCP worktree with actual owner State.
"""
import csv,json
from pathlib import Path
from e11.observer_alias import assert_same_bits
FIELD=('s','BH','BY','BZ','bindMicro','thermalMicro')


def verify(export_dir:Path,e7_root:Path,mode:str,steps:int=2)->dict:
    if mode not in ('OFF','KF','GM') or steps not in (2,384):
        raise ValueError('UNDECLARED_TELEMETRY_MODE_OR_STEPS')
    export_dir=Path(export_dir);e7_root=Path(e7_root)
    with (export_dir/'READY.json').open() as f:ready=json.load(f)
    if any([ready.get('task')!='E11_SHADOW_INTERNAL_TELEMETRY',ready.get('mode')!=mode,
            ready.get('N')!=384,ready.get('steps')!=steps,ready.get('rows')!=steps+1]):
        raise ValueError('READY_BINDING_MISMATCH')
    with (export_dir/'OWNER_INTERNAL_5.csv').open(newline='') as f:got=list(csv.DictReader(f))
    with (e7_root/f'data/histories/{mode}_N384_P512_O4.csv').open(newline='') as f:ref=list(csv.DictReader(f))
    if len(got)!=steps+1 or len(ref)<steps+1:
        raise ValueError('TELEMETRY_ROW_COUNT_MISMATCH')
    matched=0
    for i,(row,old) in enumerate(zip(got,ref)):
        if int(row['step'])!=i or int(old['step'])!=i:raise ValueError('STEP_IDENTITY_FAILED')
        for k in FIELD[1:]:
            assert_same_bits(row[k],old[k],f'{mode}:{i}:{k}')
            matched+=1
        assert_same_bits(row['s'],old['s'],f'{mode}:{i}:s')
    with (export_dir/'OWNER_ACCEPTED_STAGES.csv').open(newline='') as f: stages=list(csv.DictReader(f))
    bins={k:0 for k in range(1,steps+1)}
    for q in stages:
        k=int(q['step'])
        if k not in bins:raise ValueError('STAGE_OUTSIDE_ACCEPTED_RANGE')
        bins[k]+=1
        if int(q['count'])<0:raise ValueError('NEGATIVE_STAGE_EVENT_COUNT')
    if any(v<=0 for v in bins.values()):raise ValueError('MISSING_ACCEPTED_STAGE')
    return {'mode':mode,'steps':steps,'matched_bits':matched,'stage_rows':len(stages),
            'true_error_certificate':False,'independent_stage_numeric_check':False}
