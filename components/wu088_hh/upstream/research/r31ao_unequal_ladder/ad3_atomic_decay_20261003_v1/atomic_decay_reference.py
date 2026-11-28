"""Source-bound finite E1 factors. No HH integrator or physical-rate provider.

All rational bounds cover expressions in the supplied frozen approximate-orbital
model only. Cascade recursions assume an incoherent, spontaneous-E1-only graph;
they are not coherent quantum dynamics or radiative-transfer evolution.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import re
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent
MODEL = 'FROZEN_H_12G_REPRESENTED_BOUND_E1_V1'
FROZEN_SHA = '8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c'
ZERO = F(0)

class ContractError(ValueError):
    """Invalid data/operation; no repair is performed."""

class SourceUnavailable(ContractError):
    """A requested physical result has not been established."""

def rational(x: F | int | str) -> F:
    if isinstance(x, bool) or not isinstance(x, (F, int, str)):
        raise ContractError('EXACT_RATIONAL_REQUIRED')
    if isinstance(x, str) and (len(x) > 2500 or not re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?', x)):
        raise ContractError('INVALID_RATIONAL_LITERAL')
    y = F(x)
    if max(y.numerator.bit_length(), y.denominator.bit_length()) > 8192:
        raise ContractError('RATIONAL_INPUT_BUDGET')
    return y

@dataclass(frozen=True)
class IV:
    lo: F
    hi: F
    def __post_init__(self):
        object.__setattr__(self, 'lo', rational(self.lo))
        object.__setattr__(self, 'hi', rational(self.hi))
        if self.lo > self.hi:
            raise ContractError('REVERSED_INTERVAL')
    @classmethod
    def read(cls, x):
        if not isinstance(x, dict) or set(x) != {'lo', 'hi'}:
            raise ContractError('INVALID_INTERVAL_SCHEMA')
        return cls(x['lo'], x['hi'])
    def json(self):
        return {'lo': str(self.lo), 'hi': str(self.hi)}
    def add(self, x: IV) -> IV:
        return IV(self.lo+x.lo, self.hi+x.hi)
    def scale(self, x) -> IV:
        x = rational(x)
        return IV(self.lo*x, self.hi*x) if x >= 0 else IV(self.hi*x, self.lo*x)
    def reciprocal(self) -> IV:
        if self.lo <= 0:
            raise SourceUnavailable('POSITIVE_DENOMINATOR_NOT_ESTABLISHED')
        return IV(1/self.hi, 1/self.lo)
    def grid(self, bits=256) -> IV:
        if type(bits) is not int or not 192 <= bits <= 1024:
            raise ContractError('GRID_SCOPE')
        n = 1 << bits
        return IV(F((self.lo*n).__floor__(), n), F((self.hi*n).__ceil__(), n))
    def contains(self, x) -> bool:
        return self.lo <= rational(x) <= self.hi

def isum(xs: Sequence[IV]) -> IV:
    return IV(sum((x.lo for x in xs),ZERO), sum((x.hi for x in xs),ZERO))

def row_factors(rates: Sequence[IV]):
    if len(rates) > 32 or any(not isinstance(x, IV) or x.lo < 0 for x in rates):
        raise ContractError('NONNEGATIVE_RATE_BOX_REQUIRED')
    total = isum(rates)
    if total.hi == 0:
        return {'total': total, 'lifetime': None, 'branches': [], 'status': 'ZERO_WITHIN_DECLARED_SUBSET_ONLY'}
    if total.lo <= 0:
        raise SourceUnavailable('TOTAL_RATE_CAN_VANISH')
    branches = [IV(a.lo/(a.lo+total.hi-a.hi), a.hi/(a.hi+total.lo-a.lo))
                if a.hi else IV(0,0) for a in rates]
    return {'total': total, 'lifetime': total.reciprocal(), 'branches': branches,
            'status': 'CONDITIONAL_FINITE_SUBSET'}

def rotational_multiplicity(upper_l: int, lower_l: int) -> int:
    if type(upper_l) is not int or type(lower_l) is not int or (upper_l, lower_l) not in ((0,1),(1,0)):
        raise ContractError('ONLY_EXPLICIT_S_P_DATA')
    return 3 if lower_l == 1 else 1

def weighted_average(weights: Sequence[IV], values: Sequence[IV]) -> IV:
    """Enclose sum a_i v_i / sum a_i over boxes, sharing a_i in denominator.

For fixed other coordinates the ratio is monotone (or constant) in one a_i,
so extrema occur at vertices. v_i endpoints suffice because a_i>=0.
    """
    if not weights or len(weights) != len(values) or len(weights) > 8:
        raise ContractError('WEIGHTED_AVERAGE_DIMENSION_BUDGET')
    if any(w.lo < 0 for w in weights) or isum(weights).lo <= 0:
        raise ContractError('STRICTLY_POSITIVE_TOTAL_WEIGHT_REQUIRED')
    lower, upper = [], []
    for a in itertools.product(*[(w.lo,w.hi) if w.lo != w.hi else (w.lo,) for w in weights]):
        total = sum(a)
        lower.append(sum((x*v.lo for x,v in zip(a,values)), ZERO)/total)
        upper.append(sum((x*v.hi for x,v in zip(a,values)), ZERO)/total)
    return IV(min(lower), max(upper)).grid()

def cascade_table(energies: dict[str,F], edges: Sequence[tuple[str,str,IV]]):
    if not energies or len(energies) > 32 or len(edges) > 128:
        raise ContractError('CASCADE_SIZE_BUDGET')
    es = {k:rational(v) for k,v in energies.items()}
    outgoing = {k:[] for k in es}
    seen = set()
    for u,l,a in edges:
        if u not in es or l not in es or es[u] <= es[l]:
            raise ContractError('STRICT_DOWNWARD_EDGE_REQUIRED')
        if (u,l) in seen:
            raise ContractError('DUPLICATE_EDGE')
        seen.add((u,l))
        if not isinstance(a,IV) or a.lo < 0:
            raise ContractError('INVALID_CASCADE_FACTOR')
        if a.hi:
            outgoing[u].append((l,a))
    terminals = sorted(k for k in es if not outgoing[k])
    result = {}
    for u in sorted(es, key=lambda k:(es[k],k)):
        esout = outgoing[u]
        if not esout:
            result[u]={'photon_count':IV(0,0),'emitted_energy_Eh':IV(0,0),
                       'terminal_probabilities':{t:IV(int(u==t),int(u==t)) for t in terminals},
                       'terminal_subset_only':True}
        else:
            w = [a for _,a in esout]
            result[u] = {
                'photon_count':weighted_average(w,[result[l]['photon_count'].add(IV(1,1)) for l,_ in esout]),
                'emitted_energy_Eh':weighted_average(w,[result[l]['emitted_energy_Eh'].add(IV(es[u]-es[l],es[u]-es[l])) for l,_ in esout]),
                'terminal_probabilities':{t:weighted_average(w,[result[l]['terminal_probabilities'][t] for l,_ in esout]) for t in terminals},
                'terminal_subset_only':False}
        if len(terminals)==1 and result[u]['terminal_probabilities'][terminals[0]] == IV(1,1):
            exact = es[u]-es[terminals[0]]
            if not result[u]['emitted_energy_Eh'].contains(exact):
                raise ContractError('TELESCOPING_ENERGY_CHECK_FAILED')
            result[u]['telescoping_energy_identity_Eh']=str(exact)
    return result


def require_physical():
    raise SourceUnavailable("PHYSICAL_LEVEL_CASCADE_AND_HH_RATE_AUTHORITY_UNAVAILABLE")
