"""Additive cumulative runtime-budget wrapper; V1 numerical method is unchanged.

CONTROL_V1 remains immutable. Only invocation allowances are translated from
frozen total caps minus persisted attempts/accepted macros. The helper returns
zero allowance for exhausted runs; callers must not invoke V1 with zero budgets.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path

_spec=importlib.util.spec_from_file_location('_rei_c11_controller_v1_budget_dependency',Path(__file__).with_name('adaptive_controller.py'))
_v1=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)
controlled_trial=_v1.controlled_trial
next_boundary=_v1.next_boundary
native_observables=_v1.native_observables
validate_controls=_v1.validate_controls


def _checked_counts(cursor):
    if cursor is None:return {'attempts':0,'accepted_macros':0,'rejected_macros':0,'accepted_boundaries':0}
    if cursor.get('schema')!='rei.q1b.c11.adaptive_cursor.v1':raise ValueError('CONTROLLER_RESTART_CURSOR_SCHEMA')
    result={key:cursor[key] for key in ('attempts','accepted_macros','rejected_macros','accepted_boundaries')}
    if any(not isinstance(v,int) or isinstance(v,bool) or v<0 for v in result.values()):
        raise ValueError('CONTROLLER_RESTART_COUNT')
    if result['attempts']!=result['accepted_macros']+result['rejected_macros'] or result['accepted_boundaries']!=2*result['accepted_macros']:
        raise ValueError('CONTROLLER_RESTART_COUNT_IDENTITY')
    return result


def effective_budget_controls(controls,cursor=None):
    """Return a new controls dict with remaining *runtime* allowances only.

    Call exactly once against original frozen total controls, never against an
    already effective copy. Numerical fields/scales are byte-value unchanged.
    """
    validate_controls(controls);counts=_checked_counts(cursor)
    effective=copy.deepcopy(controls)
    for limit,count in (('max_attempts','attempts'),('max_accepted_macros','accepted_macros')):
        remaining=controls[limit]-counts[count]
        if remaining<0:raise ValueError('CONTROLLER_CUMULATIVE_BUDGET_ALREADY_EXCEEDED')
        effective[limit]=remaining
    return effective


def budget_lineage(controls,effective,cursor=None):
    """Canonical dict hashes; original CONTROL_V1 file identity stays separate."""
    expected=effective_budget_controls(controls,cursor)
    if effective!=expected:raise ValueError('CONTROLLER_EFFECTIVE_BUDGET_IDENTITY')
    digest=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    numerical=lambda value:{k:v for k,v in value.items() if k not in ('max_attempts','max_accepted_macros')}
    if numerical(controls)!=numerical(effective):raise ValueError('CONTROLLER_NUMERICAL_CONTROL_DRIFT')
    return dict(schema='rei.q1b.c11.runtime_budget_lineage.v1',scope='CUMULATIVE_ACROSS_RESUME',
        original_controls_canonical_sha256=digest(controls),effective_controls_canonical_sha256=digest(effective),
        original_runtime_limits={key:controls[key] for key in ('max_attempts','max_accepted_macros')},
        effective_runtime_allowances={key:effective[key] for key in ('max_attempts','max_accepted_macros')},
        prior_counts=_checked_counts(cursor),numerical_controls_changed=False,
        physical_or_scientific_criteria_changed=False)


def run_bounded(state,end,step,observe,validate,controls,*,hard_events=(),cursor=None,on_accept=None,on_attempt=None):
    """V1 runner with cumulative remaining allowance, plus hashed lineage."""
    effective=effective_budget_controls(controls,cursor)
    lineage=budget_lineage(controls,effective,cursor)
    end=float(end)
    if not math.isfinite(end) or end<state['t_s']:raise ValueError('CONTROLLER_RUN_CLOCK')
    def accepted(pair,row,new_cursor):
        enriched={**row,'runtime_budget_lineage':copy.deepcopy(lineage)}
        if on_accept is not None:on_accept(pair,enriched,new_cursor)
    def attempted(row,new_cursor):
        enriched={**row,'runtime_budget_lineage':copy.deepcopy(lineage)}
        if on_attempt is not None:on_attempt(enriched,new_cursor)
    if effective['max_attempts']==0 or effective['max_accepted_macros']==0:
        # V1 performs all unchanged state/cursor/event validation without a map.
        result=_v1.run_bounded(state,float(state['t_s']),step,observe,validate,controls,
                              hard_events=hard_events,cursor=cursor)
        result['status']='REACHED_REQUESTED_BOUNDARY' if state['t_s']==end else 'BUDGET_BOUNDARY'
    else:
        result=_v1.run_bounded(state,end,step,observe,validate,effective,hard_events=hard_events,
                              cursor=cursor,on_accept=accepted,on_attempt=attempted)
    result['runtime_budget_lineage']=lineage
    result['effective_runtime_controls']=effective
    for row in result['attempts']:row['runtime_budget_lineage']=copy.deepcopy(lineage)
    return result
