"""Event-aware first-order step doubling with declared fixed solver scales.

Accepts the positive two-half-step trajectory, never Richardson extrapolation.
No science comparison denominator is computed or modified here. Source/native
errors propagate failclosed; only a measured temporal defect triggers rejection.
All physical maps, strict domain checks and fixed-origin ledger checks are injected.
"""
from __future__ import annotations
import copy
import math
from typing import Callable
import numpy as np

SCHEMA='rei.q1b.c11.adaptive_controls.v1'


def validate_controls(c):
    if c.get('schema')!=SCHEMA or c.get('method_order')!=1:
        raise ValueError('CONTROLLER_METHOD_CONTRACT')
    if c.get('physical_state_floor') is not False or c.get('scientific_normalization_changed') is not False:
        raise ValueError('CONTROLLER_PROTECTED_SEMANTICS')
    for name in ('local_defect_target','safety','min_shrink','max_growth','min_step_s','max_step_s','initial_step_s'):
        if not (math.isfinite(c[name]) and c[name]>0):raise ValueError('CONTROLLER_PARAMETER_DOMAIN')
    if not (c['safety']<1 and c['min_shrink']<1 and c['max_growth']>=1 and
            c['min_step_s']<=c['initial_step_s']<=c['max_step_s']):
        raise ValueError('CONTROLLER_PARAMETER_ORDER')
    for name in ('max_attempts','max_accepted_macros'):
        if not isinstance(c[name],int) or isinstance(c[name],bool) or c[name]<=0:
            raise ValueError('CONTROLLER_BUDGET_DOMAIN')
    if not c['observable_scales']:raise ValueError('CONTROLLER_EMPTY_OBSERVABLES')
    for mapping in ('observable_scales','distribution_scales'):
        for name,value in c[mapping].items():
            if not isinstance(name,str) or not (math.isfinite(value) and value>0):
                raise ValueError('CONTROLLER_FIXED_SCALE_DOMAIN')
    if set(c['observable_scales'])&set(c['distribution_scales']):
        raise ValueError('CONTROLLER_DUPLICATE_FIELD')
    return c


def next_boundary(t,h,end,hard_events=()):
    """Return an actual supplied event/endpoint value, never nextafter."""
    t,h,end=float(t),float(h),float(end)
    events=tuple(float(e) for e in hard_events)
    if not all(math.isfinite(v) for v in (t,h,end,*events)) or h<=0 or end<=t:
        raise ValueError('CONTROLLER_TIME_DOMAIN')
    stop=min(t+h,end);kind='FINAL' if stop==end else 'PROPOSED'
    for event in sorted(set(events)):
        if t<event<=stop:
            stop=event;kind='FINAL' if event==end else 'HARD_EVENT';break
    if stop<=t:raise ArithmeticError('CONTROLLER_CLOCK_RESOLUTION')
    return stop,kind


def _defect(coarse,fine,observe,c):
    left,right=observe(coarse),observe(fine)
    expected=set(c['observable_scales'])|set(c['distribution_scales'])
    if set(left)!=expected or set(right)!=expected:raise ValueError('CONTROLLER_OBSERVABLE_KEYS')
    absolute={};normalized={}
    for name,scale in c['observable_scales'].items():
        a,b=float(left[name]),float(right[name])
        if not math.isfinite(a) or not math.isfinite(b):raise ValueError('CONTROLLER_OBSERVABLE_DOMAIN')
        difference=abs(a-b);absolute[name]=difference;normalized[name]=difference/scale
    for name,scale in c['distribution_scales'].items():
        a,b=np.asarray(left[name],float),np.asarray(right[name],float)
        if a.shape!=b.shape or a.ndim!=2 or not np.isfinite(a).all() or not np.isfinite(b).all():
            raise ValueError('CONTROLLER_DISTRIBUTION_DOMAIN')
        difference=math.fsum(np.abs(a-b).ravel());absolute[name]=difference;normalized[name]=difference/scale
    maximum=max(normalized.values())
    return dict(absolute=absolute,normalized_by_scale=normalized,max_scaled_defect=maximum,
        error_ratio=maximum/c['local_defect_target'],worst_field=max(normalized,key=normalized.get),
        estimator='FULL_VS_TWO_HALF_FIRST_ORDER_FINE_LOCAL_DEFECT_ESTIMATE',
        estimator_denominator_2powp_minus1=1.,rigorous_error_bound=False)


def controlled_trial(state,t1,step,observe,validate,c):
    """Evaluate a full/two-half trial from untouched committed state.

    validate must raise unless strict physical domains and the ORIGINAL-IC
    cumulative ledgers pass. A step-local ledger is not an adequate substitute.
    Every trial boundary (coarse, midpoint, fine) is checked before the error norm.
    A rejected trial yields diagnostics and no accepted trajectory.
    """
    validate_controls(c)
    t0=float(state['t_s']);t1=float(t1);h=t1-t0;mid=t0+.5*h
    if not (math.isfinite(t0) and math.isfinite(t1) and t0<mid<t1):
        raise ValueError('CONTROLLER_STEP_CLOCK_DOMAIN')
    validate(state)
    coarse=step(copy.deepcopy(state),t1);validate(coarse)
    first=step(copy.deepcopy(state),mid);validate(first)
    fine=step(copy.deepcopy(first),t1);validate(fine)
    for actual,expected in ((coarse,t1),(first,mid),(fine,t1)):
        if actual['t_s']!=expected:raise ValueError('CONTROLLER_RETURNED_CLOCK')
    metric=_defect(coarse,fine,observe,c)
    ratio=metric['error_ratio'];accepted=ratio<=1
    factor=c['max_growth'] if ratio==0 else c['safety']*ratio**(-.5)
    factor=min(c['max_growth'],max(c['min_shrink'],factor))
    if not accepted:factor=min(factor,.9)
    next_h=min(c['max_step_s'],h*factor)
    if next_h<c['min_step_s']:
        raise ArithmeticError('CONTROLLER_MIN_STEP_REACHED')
    return dict(t0_s=t0,t1_s=t1,h_s=h,midpoint_s=mid,accepted=accepted,
        next_step_s=next_h,step_evaluations=3,defect=metric,
        fine_states=(first,fine),coarse_state=coarse,
        richardson_extrapolation=False,state_floor=False,scientific_admission=False)


def run_bounded(state,end,step,observe,validate,c,*,hard_events=(),cursor=None,on_accept=None,on_attempt=None):
    """Bounded adaptive progression with transactional accepted-prefix callback.

    on_accept((midpoint,fine), compact_trial, prospective_cursor) is called only
    after both halves and error gate pass. It must durably record *both* natural
    boundaries plus the next-step cursor; any failure aborts before return.
    Checkpoints are resumable at the fine macro endpoint. Midpoint restart would
    require a pending accepted segment record, which this API does not certify.
    on_attempt sees rejected/accepted trial diagnostics without trajectory arrays.
    """
    validate_controls(c);validate(state)
    if cursor is None:
        cursor=dict(schema='rei.q1b.c11.adaptive_cursor.v1',next_step_s=c['initial_step_s'],
            attempts=0,accepted_macros=0,rejected_macros=0,accepted_boundaries=0,
            accepted_clock_s=float(state['t_s']))
    else:cursor=copy.deepcopy(cursor)
    if cursor.get('schema')!='rei.q1b.c11.adaptive_cursor.v1' or cursor['accepted_clock_s']!=state['t_s']:
        raise ValueError('CONTROLLER_RESTART_CURSOR_CLOCK')
    if not (math.isfinite(cursor['next_step_s']) and c['min_step_s']<=cursor['next_step_s']<=c['max_step_s']):
        raise ValueError('CONTROLLER_RESTART_STEP_DOMAIN')
    for key in ('attempts','accepted_macros','rejected_macros','accepted_boundaries'):
        if not isinstance(cursor[key],int) or cursor[key]<0:raise ValueError('CONTROLLER_RESTART_COUNT')
    if cursor['attempts']!=cursor['accepted_macros']+cursor['rejected_macros'] or cursor['accepted_boundaries']!=2*cursor['accepted_macros']:
        raise ValueError('CONTROLLER_RESTART_COUNT_IDENTITY')
    end=float(end);events=tuple(map(float,hard_events))
    if not math.isfinite(end) or end<state['t_s'] or not all(map(math.isfinite,events)):
        raise ValueError('CONTROLLER_RUN_CLOCK')
    current=copy.deepcopy(state);attempts=[];local_accepted=0
    while current['t_s']<end:
        if len(attempts)>=c['max_attempts'] or local_accepted>=c['max_accepted_macros']:break
        t1,kind=next_boundary(current['t_s'],cursor['next_step_s'],end,events)
        trial=controlled_trial(current,t1,step,observe,validate,c)
        compact={key:value for key,value in trial.items() if key not in ('fine_states','coarse_state')}
        compact['boundary_kind']=kind
        trial_cursor=copy.deepcopy(cursor);trial_cursor['attempts']+=1;trial_cursor['next_step_s']=trial['next_step_s']
        if trial['accepted']:
            trial_cursor['accepted_macros']+=1;trial_cursor['accepted_boundaries']+=2
            trial_cursor['accepted_clock_s']=t1
            if on_accept is not None:on_accept(trial['fine_states'],compact,copy.deepcopy(trial_cursor))
            current=trial['fine_states'][-1];local_accepted+=1
        else:trial_cursor['rejected_macros']+=1
        cursor=trial_cursor;attempts.append(compact)
        if on_attempt is not None:on_attempt(compact,copy.deepcopy(cursor))
    return dict(status='REACHED_REQUESTED_BOUNDARY' if current['t_s']==end else 'BUDGET_BOUNDARY',
        state=current,cursor=cursor,attempts=attempts,scientific_admission=False,
        claim='FIXED_SCALE_LOCAL_CONTROLLER_ONLY; WHOLE_HISTORY_GATES_NOT_EVALUATED')


def native_observables(state,provider):
    """Fixed-unit nine fields + full radiation distributions; no physical floor."""
    g=provider.geometry(float(state['t_s']))
    x,y,z,w=np.asarray(state['gas'],float)
    f=g['nHe']/g['nH']
    temperature=2*w*1.602176634e-12/(3*1.380649e-16*(1+f+x+f*(y+2*z)))
    gamma=state['diagnostics']['gamma']
    return dict(xHII=float(x),xHeII=float(y),xHeIII=float(z),T_K=float(temperature),
        ne_cm3=float(g['nH']*x+g['nHe']*(y+2*z)),
        photon_cm3=math.fsum(np.asarray(state['N']).ravel())/g['a_rel']**3,
        GammaHI_s=float(gamma[0]),GammaHeI_s=float(gamma[1]),GammaHeII_s=float(gamma[2]),
        N_ref_distribution=np.asarray(state['N']),U_eV_ref_distribution=np.asarray(state['U_eV']))
