"""Versioned C11 macro-endpoint checkpoint with an authoritative adaptive cursor.

Every accepted half-step boundary is stored. Only the final macro endpoint is
resumable; no pending half-step, solver history or hidden precision component is
permitted. Generic `next_segment` denotes the remaining declared interval, not
the next adaptive step. The latter is determined solely by the saved controller
cursor, controls, event list and end time. C10 bytes remain immutable.
"""
from __future__ import annotations
import copy,hashlib,json,math
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'c10'))
sys.path.insert(0,str(HERE.parent/'controller'))
from entry_checkpoint import (make_entry_snapshot,validate_entry_snapshot,
    pack_entry_state,SCHEMA as C10_SCHEMA)
from atomic_checkpoint import publish_generation,load_generation
from adaptive_controller import validate_controls
SCHEMA='rei.q1b.c11.adaptive_checkpoint.v1'
INTERVAL_SEMANTICS='REMAINING_DECLARED_INTERVAL_NOT_THE_NEXT_ADAPTIVE_STEP'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def require(condition,message):
    if not condition:raise ValueError(message)

def _validate_cursor(cursor,controls,clocks):
    require(cursor.get('schema')=='rei.q1b.c11.adaptive_cursor.v1','ADAPTIVE_CURSOR_SCHEMA')
    expected={'schema','next_step_s','attempts','accepted_macros','rejected_macros','accepted_boundaries','accepted_clock_s'}
    require(set(cursor)==expected,'ADAPTIVE_CURSOR_FIELDS')
    require(cursor['accepted_clock_s']==float(clocks[-1]),'ADAPTIVE_CURSOR_CLOCK')
    require(math.isfinite(cursor['next_step_s']) and controls['min_step_s']<=cursor['next_step_s']<=controls['max_step_s'],'ADAPTIVE_CURSOR_STEP')
    for name in ('attempts','accepted_macros','rejected_macros','accepted_boundaries'):
        require(type(cursor[name]) is int and cursor[name]>=0,'ADAPTIVE_CURSOR_COUNT')
    require(cursor['attempts']==cursor['accepted_macros']+cursor['rejected_macros'] and
        cursor['accepted_boundaries']==2*cursor['accepted_macros'] and
        len(clocks)==cursor['accepted_boundaries']+1,'ADAPTIVE_CURSOR_PREFIX_COUNTS')

def make_adaptive_snapshot(*,states,controls,cursor,end_time_s,hard_events,scales,dependency_closure):
    require(bool(states),'ADAPTIVE_STATES_EMPTY')
    clocks=np.array([s['t_s'] for s in states],dtype=float)
    require(clocks[0]==0.,'ADAPTIVE_ORIGINAL_IC_PREFIX_REQUIRED')
    validate_controls(controls);_validate_cursor(cursor,controls,clocks)
    end=float(end_time_s);events=list(map(float,hard_events))
    require(math.isfinite(end) and end>=clocks[-1] and end>clocks[0],'ADAPTIVE_END_TIME')
    require(all(math.isfinite(e) and clocks[0]<e<=end for e in events) and events==sorted(set(events)),'ADAPTIVE_EVENTS')
    schedule=clocks.copy() if end==clocks[-1] else np.r_[clocks,end]
    nH,nHe=states[0]['nH_ref'],states[0]['nHe_ref']
    require(all(s['nH_ref']==nH and s['nHe_ref']==nHe for s in states),'ADAPTIVE_REFERENCE_DENSITY_DRIFT')
    packed=np.array([pack_entry_state(s['gas'],np.asarray(s['N']).ravel(),np.asarray(s['U_eV']).ravel(),s['counters']) for s in states])
    arrays,metadata=make_entry_snapshot(clocks=clocks,states=packed,
        R=np.array([np.asarray(s['R']).ravel() for s in states]),
        support=np.array([np.asarray(s['support']).reshape(-1,2) for s in states]),
        all_boundary_clocks=schedule,nH_ref=nH,nHe_ref=nHe,scales=scales,
        physical_binding='SOURCE_ENTRY_POSITIVE_STEP_V1')
    binding=dict(controls=copy.deepcopy(controls),end_time_s=end,hard_events_s=events,dependency_closure=copy.deepcopy(dependency_closure))
    metadata.update(schema=SCHEMA,adaptive_cursor=copy.deepcopy(cursor),restart_binding=binding,
        restart_binding_sha256=canonical_sha(binding),next_segment_semantics=INTERVAL_SEMANTICS,
        resumed_boundary_kind='ACCEPTED_MACRO_FINE_ENDPOINT',pending_halfstep=None,
        authoritative_state_representation='BINARY64_N_U_NO_HIDDEN_LOW_COMPONENTS',
        native_driver_binding='C11_ACTUAL_DRIVER_EVIDENCE_REQUIRED',
        scientific_admission=False)
    validate_adaptive_snapshot(arrays,metadata)
    return arrays,metadata

def validate_adaptive_snapshot(arrays,metadata):
    require(metadata.get('schema')==SCHEMA,'ADAPTIVE_SCHEMA')
    require(metadata.get('next_segment_semantics')==INTERVAL_SEMANTICS and
        metadata.get('resumed_boundary_kind')=='ACCEPTED_MACRO_FINE_ENDPOINT','ADAPTIVE_BOUNDARY_SEMANTICS')
    require(metadata.get('pending_halfstep') is None,'ADAPTIVE_PENDING_HALFSTEP_UNSUPPORTED')
    require(metadata.get('authoritative_state_representation')=='BINARY64_N_U_NO_HIDDEN_LOW_COMPONENTS','ADAPTIVE_PRECISION_STATE_UNSUPPORTED')
    binding=metadata.get('restart_binding')
    require(isinstance(binding,dict) and set(binding)=={'controls','end_time_s','hard_events_s','dependency_closure'},'ADAPTIVE_BINDING_FIELDS')
    require(canonical_sha(binding)==metadata.get('restart_binding_sha256'),'ADAPTIVE_BINDING_HASH')
    controls=binding['controls'];validate_controls(controls)
    clocks=arrays['prefix_clock'];_validate_cursor(metadata['adaptive_cursor'],controls,clocks)
    end=binding['end_time_s'];events=binding['hard_events_s']
    require(clocks[0]==0. and math.isfinite(end) and end>=clocks[-1] and end>0.,'ADAPTIVE_INTERVAL')
    require(all(math.isfinite(e) and 0.<e<=end for e in events) and events==sorted(set(events)),'ADAPTIVE_EVENTS')
    expected=clocks if end==clocks[-1] else np.r_[clocks,end]
    require(np.array_equal(arrays['scheduled_clock'],expected),'ADAPTIVE_SCHEDULE_EXACT_HISTORY')
    # Reuse the pinned C10 physical-domain/ledger checker through an explicit
    # schema translation only; adaptive semantics are checked above here.
    physical=copy.deepcopy(metadata);physical['schema']=C10_SCHEMA
    result=validate_entry_snapshot(arrays,physical)
    result.update(controller_checked=True,pending_halfstep_checked=True,
        scope='C11_ADAPTIVE_MACRO_ENDPOINT_FULL_ACCEPTED_HALFSTEP_PREFIX',scientific_admission=False)
    return result

def adaptive_identity(*,source,grid,binary,physics_contract,metadata):
    return dict(source=sha(source),grid=sha(grid),binary=sha(binary),physics_contract=sha(physics_contract),
        physical_validator=sha(__file__),control=canonical_sha(metadata['restart_binding']))

def _check_control(metadata,identity):
    require(identity['control']==canonical_sha(metadata['restart_binding']),'ADAPTIVE_CONTROL_IDENTITY')

def verify_dependency_closure(metadata):
    mapping=metadata['restart_binding']['dependency_closure']
    require(isinstance(mapping,dict) and bool(mapping),'ADAPTIVE_EMPTY_DEPENDENCY_CLOSURE')
    for key,expected in mapping.items():
        require(isinstance(key,str) and key.startswith('dependency:'),'ADAPTIVE_DEPENDENCY_KEY')
        relative=Path(key.split(':',1)[1])
        require(not relative.is_absolute() and '..' not in relative.parts,'ADAPTIVE_DEPENDENCY_PATH')
        require(sha(HERE.parents[4]/relative)==expected,'ADAPTIVE_DEPENDENCY_MISMATCH:'+str(relative))
    return mapping

def write_adaptive_checkpoint(directory,generation,arrays,metadata,expected_identity):
    _check_control(metadata,expected_identity)
    verify_dependency_closure(metadata)
    return publish_generation(directory,generation,arrays,metadata,expected_identity,validate_adaptive_snapshot)

def load_adaptive_checkpoint(directory,generation,expected_identity,*,expected_manifest_sha256=None):
    loaded=load_generation(directory,generation,expected_identity,validate_adaptive_snapshot,
        expected_manifest_sha256=expected_manifest_sha256)
    _check_control(loaded['metadata'],expected_identity)
    verify_dependency_closure(loaded['metadata'])
    return loaded
