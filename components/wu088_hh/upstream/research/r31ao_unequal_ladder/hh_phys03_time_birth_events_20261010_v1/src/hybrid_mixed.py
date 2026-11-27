"""Exact coefficient transport through one regular hybrid event.

Coordinates of guard/reset derivatives are (t, z[0:n], a, b). Inputs are
point derivatives at the nominal event, with pre/post flow derivatives taken
at their respective nominal states. This is an algebraic operator, not a
physical source validator, an event locator, or a certified interval solver.
Use exact Fraction data for the distributed verification fixtures.
"""
from dataclasses import dataclass
from typing import Sequence


def dot(x, y):
    return sum(a*b for a, b in zip(x, y))


def mv(a, x):
    return [dot(row, x) for row in a]


def bilinear(h, x, y):
    return dot(x, mv(h, y))


@dataclass(frozen=True)
class FlowJet:
    f: Sequence
    dt: Sequence
    dz: Sequence[Sequence]
    da: Sequence
    db: Sequence


@dataclass(frozen=True)
class ScalarJet:
    value: object
    gradient: Sequence
    hessian: Sequence[Sequence]


@dataclass(frozen=True)
class ResetJet:
    value: Sequence
    jacobian: Sequence[Sequence]
    hessians: Sequence[Sequence[Sequence]]


def _validate(n, pre, post, guard, reset, u, v, w):
    m=n+3
    for flow in (pre, post):
        if any(len(a)!=n for a in (flow.f,flow.dt,flow.da,flow.db,flow.dz)):
            raise ValueError('flow dimension mismatch')
        if any(len(row)!=n for row in flow.dz):
            raise ValueError('flow Jacobian dimension mismatch')
    if any(len(a)!=n for a in (u,v,w,reset.value,reset.jacobian,reset.hessians)):
        raise ValueError('state/reset dimension mismatch')
    if len(guard.gradient)!=m or len(guard.hessian)!=m:
        raise ValueError('guard dimension mismatch')
    if any(len(row)!=m for row in guard.hessian):
        raise ValueError('guard Hessian dimension mismatch')
    if any(len(row)!=m for row in reset.jacobian):
        raise ValueError('reset Jacobian dimension mismatch')
    if any(len(h)!=m or any(len(row)!=m for row in h) for h in reset.hessians):
        raise ValueError('reset Hessian dimension mismatch')
    if guard.value!=0:
        raise ValueError('nominal point is not on the event guard')


def transport_event(pre, post, guard, reset, u, v, w):
    """Return da, db, mixed derivative on the synchronized post-event branch.

The pre-event u/v/w are derivatives at fixed nominal physical time. The
result is the smooth post-branch extension to that same time; a later common
observation time must still be propagated with the post-event dynamics.
"""
    n=len(pre.f)
    _validate(n,pre,post,guard,reset,u,v,w)
    gz=guard.gradient[1:n+1]
    den=guard.gradient[0]+dot(gz,pre.f)
    if den==0:
        raise ValueError('NONTRANSVERSE_EVENT: g_t + g_z*f_minus is zero')
    ta=-(dot(gz,u)+guard.gradient[n+1])/den
    tb=-(dot(gz,v)+guard.gradient[n+2])/den
    za=[x+f*ta for x,f in zip(u,pre.f)]
    zb=[x+f*tb for x,f in zip(v,pre.f)]
    va=[ta,*za,1,0]
    vb=[tb,*zb,0,1]
    fta=[x+y for x,y in zip(mv(pre.dz,u),pre.da)]
    ftb=[x+y for x,y in zip(mv(pre.dz,v),pre.db)]
    ftt=[x+y for x,y in zip(pre.dt,mv(pre.dz,pre.f))]
    cross=[fta[i]*tb+ftb[i]*ta+ftt[i]*ta*tb for i in range(n)]
    tab=-(dot(gz,[w[i]+cross[i] for i in range(n)])
          +bilinear(guard.hessian,va,vb))/den
    zab=[w[i]+cross[i]+pre.f[i]*tab for i in range(n)]
    ya=mv(reset.jacobian,va)
    yb=mv(reset.jacobian,vb)
    event_ab=[tab,*zab,0,0]
    yab=[dot(reset.jacobian[i],event_ab)
         +bilinear(reset.hessians[i],va,vb) for i in range(n)]
    ua=[ya[i]-post.f[i]*ta for i in range(n)]
    vbpost=[yb[i]-post.f[i]*tb for i in range(n)]
    pa=[x+y for x,y in zip(mv(post.dz,ua),post.da)]
    pb=[x+y for x,y in zip(mv(post.dz,vbpost),post.db)]
    ptt=[x+y for x,y in zip(post.dt,mv(post.dz,post.f))]
    mixed=[yab[i]-post.f[i]*tab-pa[i]*tb-pb[i]*ta-ptt[i]*ta*tb
           for i in range(n)]
    return {'u_plus':ua,'v_plus':vbpost,'w_plus':mixed,
            'event_time_a':ta,'event_time_b':tb,'event_time_ab':tab,
            'transversality':den,'moving_event_state_a':za,
            'moving_event_state_b':zb,'moving_event_state_ab':zab,
            'synchronization':'one-sided smooth post branch at common nominal time'}
