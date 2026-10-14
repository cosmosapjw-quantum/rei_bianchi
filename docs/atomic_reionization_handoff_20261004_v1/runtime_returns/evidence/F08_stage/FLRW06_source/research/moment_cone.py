"""Exact rational forward-Euler moment realizability, not an error estimator."""
from fractions import Fraction as F

def exact_forward_euler_limit(L, R, N, U, dN, dU):
    """Largest h>=0 keeping N>=0 and L*N<=U<=R*N for frozen derivatives.

    Return None if there is no finite upper bound. Equality is permitted for
    a positive measure, but an exponential-density inversion needs strict
    interior moments or an explicitly separate delta-cohort representation.
    """
    L,R,N,U,dN,dU=map(F,(L,R,N,U,dN,dU))
    if not (0<L<R and N>=0 and L*N<=U<=R*N):
        raise ValueError('MOMENT_CONE_DOMAIN')
    q=(N,U-L*N,R*N-U)
    dq=(dN,dU-L*dN,R*dN-dU)
    limits=[-v/d for v,d in zip(q,dq) if d<0]
    return min(limits) if limits else None

def margins(L,R,N,U):
    L,R,N,U=map(F,(L,R,N,U))
    return (N,U-L*N,R*N-U)
