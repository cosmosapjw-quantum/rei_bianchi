"""Synthetic rational oracle for S01 algebra. No array loader or ball backend."""
from dataclasses import dataclass
from fractions import Fraction as Q


@dataclass(frozen=True)
class QC:
    real:Q
    imag:Q=Q(0)
    def __post_init__(self):
        if not isinstance(self.real,Q) or not isinstance(self.imag,Q):
            raise ValueError('exact Fraction components required')
    def __add__(self,other):
        return QC(self.real+other.real,self.imag+other.imag)
    def __neg__(self): return QC(-self.real,-self.imag)
    def __sub__(self,other): return self+-other
    def __mul__(self,other):
        if isinstance(other,(Q,int)):
            return QC(self.real*other,self.imag*other)
        if not isinstance(other,QC): raise ValueError('exact complex or rational required')
        return QC(self.real*other.real-self.imag*other.imag,
                  self.real*other.imag+self.imag*other.real)
    def conjugate(self): return QC(self.real,-self.imag)


def registry(): return [(0,j) for j in range(24)]+[(1,j) for j in range(1,24)]


def contract_entry(raw,left,ground,orbital,field,cusp):
    if orbital not in (0,1,2) or field not in (0,1,2) or cusp not in (0,1):
        raise ValueError('invalid source index')
    if len(left)!=12 or len(ground)!=12 or len(raw)!=12 or any(len(row)!=12 for row in raw):
        raise ValueError('12 by 12 primitive matrix required')
    if not all(isinstance(x,Q) for x in left+ground):
        raise ValueError('exact represented coefficient lifts required')
    value=QC(Q(0))
    for ia in range(12):
        for ib in range(12): value+=raw[ia][ib]*(left[ia]*ground[ib])
    parity=(-1 if cusp and orbital else 1)*(-1 if cusp and field else 1)
    return value*parity


def phase_argument(z,v,en,ei,cusp):
    if cusp not in (0,1) or not all(isinstance(x,Q) for x in (z,v,en,ei)) or not v:
        raise ValueError('exact phase inputs and nonzero v required')
    kc=v/2 if cusp==0 else -v/2
    cz=z/2 if cusp==0 else -z/2
    return 2*kc*cz+(en-ei)*(z/v)


def final_blocks(O,G1,G2,v,en,ei,active,cusp):
    """Inputs are already contracted, reflected and phased real-domain integrals."""
    if active not in (0,1) or cusp not in (0,1) or not all(isinstance(x,Q) for x in (v,en,ei)) or not v:
        raise ValueError('invalid exact assembly inputs')
    kc=v/2 if cusp==0 else -v/2
    ka=v/2 if active==0 else -v/2
    kb=-ka
    dc=(G1+G2)*kc+QC(Q(0),kc*(2*kc-ka-kb)-ei)*O
    dr=G1.conjugate()*(-ka)+G2.conjugate()*(-kb)-QC(Q(0),en)*O.conjugate()
    return dc,dr
