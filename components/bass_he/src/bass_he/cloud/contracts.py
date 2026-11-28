"""Canonical case and execution identities. No numerical policy is defined here."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json, math
from typing import Any
from bass_he.replay_contract import RESIDUAL_LIMIT, SHEET_GAP_MIN, EP_DISTANCE_LIMIT, SOURCE_DELTA, SOURCE_REL_LIMIT

KINDS = {'wrong_pair_check', 'control', 'endpoint', 'geometry'}
STATUSES = {'PASS', 'WRONG_PAIR', 'NUMERICAL_REJECTED', 'TIME_BUDGET_EXCEEDED', 'WORKER_CRASH', 'ENVIRONMENT_ERROR'}

def canonical(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, str): return value
    if isinstance(value, int): return value
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError('nonfinite scientific value')
        return {'float64_hex': value.hex()}
    if isinstance(value, complex): return {'complex128': [canonical(value.real), canonical(value.imag)]}
    if isinstance(value, (tuple, list)): return [canonical(v) for v in value]
    if isinstance(value, dict): return {str(k): canonical(v) for k,v in sorted(value.items())}
    raise TypeError(f'unsupported scientific value: {type(value)}')

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(canonical(value), sort_keys=True, separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class CaseSpec:
    kind: str
    science_fields: dict
    def __post_init__(self):
        if self.kind not in KINDS: raise ValueError('invalid case kind')
        required = {'source', 'backend', 'depth', 'pair', 'seed'} if self.kind != 'geometry' else {'source','backend','depth','pair','endpoint','certificate_sha256','rho','panels','path'}
        if not required <= self.science_fields.keys(): raise ValueError(f'missing science fields: {required-self.science_fields.keys()}')
        f=self.science_fields
        if not isinstance(f['source'],str) or not f['source'] or not isinstance(f['backend'],str):raise ValueError('invalid source/backend')
        if len(f['pair'])!=2 or any(len(state)!=3 or any(type(n) is not int for n in state) for state in f['pair']):raise ValueError('invalid state pair')
        if type(f['depth']) is not int or f['depth'] <= 0: raise ValueError('invalid depth')
        if self.kind == 'geometry' and (type(f['panels']) is not int or f['panels'] <= 0 or type(f['rho']) not in (int,float)): raise ValueError('invalid panels/rho')
        canonical(f)

def task_id(spec: CaseSpec) -> str: return digest({'kind':spec.kind,'science_fields':spec.science_fields})

@dataclass(frozen=True)
class Attempt:
    task_id: str
    run_epoch: str
    number: int

@dataclass(frozen=True)
class ExecutionBinding:
    source_commit: str
    source_tree: str
    runner_sha256: str
    python: str
    packages: dict
    machine: str
    thread_policy: dict
    scientific_parent: str = "ac09160bae74f051e5e2e17d8a1cde4084576c16"
    plan_commit: str = "4e775fdb61e72fd75f956fe0a83064e37e0522da"
    scientific_source_id: str = ''
    def identity(self):
        data=asdict(self)
        if not self.scientific_source_id:data.pop('scientific_source_id') # v1 receipt compatibility
        return digest(data)

@dataclass(frozen=True)
class CaseOutcome:
    status: str
    payload: dict
    diagnostics: dict
    def __post_init__(self):
        if self.status not in STATUSES: raise ValueError('unknown outcome status')
        canonical(self.payload); canonical(self.diagnostics)


def outcome_document(spec: CaseSpec, outcome: CaseOutcome, binding: ExecutionBinding, attempt: Attempt) -> dict:
    return {'schema':'bass_he.case_result.v1','task_id':task_id(spec),'spec':json.loads(json.dumps(asdict(spec))),'binding':binding.identity(),'outcome':asdict(outcome),'attempt':asdict(attempt)}

def validate_document(doc: dict, spec: CaseSpec, binding: ExecutionBinding, attempt: Attempt) -> CaseOutcome:
    if doc.get('schema') != 'bass_he.case_result.v1' or doc.get('task_id') != task_id(spec) or doc.get('spec') != json.loads(json.dumps(asdict(spec))) or doc.get('binding') != binding.identity() or doc.get('attempt') != asdict(attempt):
        raise ValueError('payload or binding mismatch')
    out=CaseOutcome(**doc['outcome'])
    if spec.kind == 'wrong_pair_check' and out.status == 'WRONG_PAIR' and 'pair membership' not in out.diagnostics.get('reason',''):
        raise ValueError('wrong-pair rejection lacks membership evidence')
    if out.status == 'PASS':
        if spec.kind == 'geometry':
            p=out.payload
            if not (p['delta'] > 0 and p['max_spectral_residual'] <= RESIDUAL_LIMIT and p['minimum_normalized_sheet_gap'] > SHEET_GAP_MIN): raise ValueError('geometry gate failed')
        elif spec.kind in ('endpoint','control'):
            p=out.payload;ep=p['ep'];pair=spec.science_fields['pair']
            if list(ep['state_a'])!=list(pair[0]) or list(ep['state_b'])!=list(pair[1]) or not ep['certificate']['simple_fold'] or not ep['pair_membership']['passed']:raise ValueError('endpoint membership gate failed')
            if spec.kind == 'endpoint':
                seed=spec.science_fields['seed']['complex'];r=ep['R']['complex'];distance=abs(complex(*r)-complex(*seed))
                if abs(distance-p['distance'])>1e-14 or distance>EP_DISTANCE_LIMIT:raise ValueError('endpoint distance gate failed')
            else:
                g=p['geometry'];relative=abs(g['delta']-SOURCE_DELTA)/SOURCE_DELTA
                if abs(relative-p['relative_to_source'])>1e-14 or relative>SOURCE_REL_LIMIT or g['max_spectral_residual']>RESIDUAL_LIMIT:raise ValueError('control gate failed')
    return out
