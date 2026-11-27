from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class UnitedState:
    N: int
    l: int
    m: int

    def __post_init__(self):
        if self.N < 1 or not (0 <= self.l < self.N) or not (0 <= self.m <= self.l):
            raise ValueError("invalid united-atom state")

    @property
    def k(self) -> int:
        return self.N - self.l - 1

    @property
    def q(self) -> int:
        return self.l - self.m


@dataclass(frozen=True)
class SeparatedState:
    center: str
    Z: int
    n: int
    n1: int
    n2: int
    m: int

    def __post_init__(self):
        if self.center not in {"Z1","Z2"}:
            raise ValueError("center must be Z1 or Z2")
        if self.n < 1 or min(self.n1,self.n2,self.m) < 0:
            raise ValueError("invalid parabolic quantum numbers")
        if self.n != self.n1 + self.n2 + self.m + 1:
            raise ValueError("require n=n1+n2+m+1")


def _z1_q_heh(k: int, m: int, n2: int) -> int:
    """CPC Eq. (17) specialized to Z1=1, Z2=2."""
    if min(k,m,n2) < 0:
        raise ValueError("quantum numbers must be non-negative")
    return 3*n2 + k + m + 1


def _is_z1_q_heh(k: int, m: int, q: int) -> tuple[bool,int|None]:
    c=k+m+1
    d=q-c
    if d >= 0 and d % 3 == 0:
        return True, d//3
    return False, None


def _z2_q_from_n2_heh(k: int, m: int, n2p: int) -> int:
    """Z2 map as ordered complement of the unambiguous Eq. (17) Z1 map.

    The published CPC Eq. (18) has ambiguous prime marks when read literally.
    For HeH2+ only, the remaining q-values at fixed (k,m) are assigned in
    adiabatic order to n2'=0,1,2,... .  Appendix-A supplies the exact source
    oracle for this construction at Nmax=3.
    """
    if min(k,m,n2p) < 0:
        raise ValueError("quantum numbers must be non-negative")
    rank=-1
    q=-1
    while rank < n2p:
        q += 1
        is_z1,_ = _is_z1_q_heh(k,m,q)
        if not is_z1:
            rank += 1
    return q


def cordir_heh(N: int, l: int, m: int) -> SeparatedState:
    u=UnitedState(N,l,m)
    is_z1,n2 = _is_z1_q_heh(u.k,u.m,u.q)
    if is_z1:
        assert n2 is not None
        n=u.k+n2+u.m+1
        return SeparatedState("Z1",1,n,u.k,n2,u.m)

    rank=0
    n2p=None
    for qq in range(u.q+1):
        z1,_=_is_z1_q_heh(u.k,u.m,qq)
        if not z1:
            if qq==u.q:
                n2p=rank
                break
            rank += 1
    if n2p is None:
        raise RuntimeError("failed to rank Z2 correlation")
    n=u.k+n2p+u.m+1
    return SeparatedState("Z2",2,n,u.k,n2p,u.m)


def corinv_heh(center: str, n: int, n1: int, n2: int, m: int) -> UnitedState:
    Z=1 if center=="Z1" else 2
    s=SeparatedState(center,Z,n,n1,n2,m)
    k=s.n1
    q=_z1_q_heh(k,m,s.n2) if center=="Z1" else _z2_q_from_n2_heh(k,m,s.n2)
    l=q+m
    N=k+q+m+1
    return UnitedState(N,l,m)


def asymptotic_electronic_energy(state: SeparatedState, R: float, *, include_distant_center=True) -> float:
    if R <= 0:
        raise ValueError("R must be positive")
    E=-(state.Z**2)/(2.0*state.n**2)
    if include_distant_center:
        Zother=2 if state.center=="Z1" else 1
        E -= Zother/R
    return E
