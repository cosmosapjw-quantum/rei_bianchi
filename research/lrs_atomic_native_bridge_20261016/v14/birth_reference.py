"""V14 manufactured positive source-birth controls, independent of native Rust.

X is dimensionless ln(a/a0). Linear grey opacity k is per X; source is
photons per total-H per X. Monochromatic source energy 80 eV. These are NOT
Verner/Grackle or production cosmological reference solutions.
"""
from math import exp, expm1, sqrt, isfinite


def birth_nodes(rule):
    if rule == 'gl2':
        a=(1-1/sqrt(3))/2
        return ((a,.5),(1-a,.5))
    if rule == 'midpoint':
        return ((.5,1.),)
    if rule == 'common_halves':
        # Both injection locations at the same geometry. This deliberately
        # tests a frozen-midpoint surrogate, not V13's full native algorithm.
        return ((.5,.5),(.5,.5))
    raise ValueError('unknown birth rule')


def _budget(steps,end):
    if not isinstance(steps,int) or not 1<=steps<=8192 or not isfinite(end) or end<=0:
        raise ValueError('invalid finite interval/step budget')


def linear_history(rule,steps,end,k,source):
    """Exact grey source-free flows, impulses at selected *actual* birth X."""
    _budget(steps,end)
    if not isfinite(k) or k<0:raise ValueError('negative/nonfinite opacity')
    out=dict(N=0.,U=0.,born_N=0.,born_U=0.,absorbed_N=0.,absorbed_U=0.,work_U=0.)
    h=end/steps
    def evolve(dt):
        oldN,oldU=out['N'],out['U']
        out['N']=oldN*exp(-k*dt)
        out['U']=oldU*exp(-(k+1)*dt)
        out['absorbed_N']+=oldN*(-expm1(-k*dt))
        removedU=oldU*(-expm1(-(k+1)*dt))
        out['absorbed_U']+=removedU*k/(k+1)
        out['work_U']+=removedU/(k+1)
    for i in range(steps):
        last=i*h
        for c,w in birth_nodes(rule):
            x=(i+c)*h
            evolve(x-last)
            n=h*w*source(x)
            if not isfinite(n) or n<0:raise ValueError('source must be finite nonnegative')
            out['N']+=n;out['U']+=80*n
            out['born_N']+=n;out['born_U']+=80*n
            last=x
        evolve((i+1)*h-last)
    return out


def nonlinear_history(rule,steps,end,source,kappa):
    """Photo-only mass-action N'=S-k N M, M'=-k N M, no energy model."""
    _budget(steps,end)
    n,m,events,born=.2,1.,0.,0.
    h=end/steps
    def flow(n,m,dt,k):
        if not isfinite(k) or k<0:raise ValueError('bad opacity')
        low,high=min(n,m),max(n,m);d=high-low
        exposure=(-expm1(-d*k*dt)/d) if d>0 else k*dt
        event=low*high*exposure/(1+low*exposure)
        return n-event,m-event,event
    for i in range(steps):
        last=i*h
        for c,w in birth_nodes(rule):
            x=(i+c)*h
            n,m,e=flow(n,m,x-last,kappa((x+last)/2));events+=e
            d=h*w*source(x)
            if not isfinite(d) or d<0:raise ValueError('bad source')
            n+=d;born+=d;last=x
        x=(i+1)*h
        n,m,e=flow(n,m,x-last,kappa((x+last)/2));events+=e
    return dict(N=n,M=m,events=events,born_N=born)
