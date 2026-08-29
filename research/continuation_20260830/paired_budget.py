"""Exact difference-first affine budget bookkeeping, NOT a thermal-map proof.

Coefficients are supplied by a source-bound paired implicit adapter. Named IDs
represent declared physical dependence, never equality inferred from interval
bounds. Remainders are conservatively independent unless an upstream joint
certificate supplied a direct difference remainder. No tolerance or time-step adjustments.
"""
from fractions import Fraction
from dataclasses import dataclass
from types import MappingProxyType
import math


def exact(value):
    if isinstance(value,bool):raise TypeError('boolean coefficient')
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError('nonfinite coefficient')
        return Fraction.from_float(value)
    return Fraction(value)

@dataclass(frozen=True)
class AffineBudget:
    center:Fraction
    coefficients:dict
    remainder_radius:Fraction
    def __post_init__(self):
        c=exact(self.center);r=exact(self.remainder_radius)
        if r<0 or any(not isinstance(k,str) or not k for k in self.coefficients):raise ValueError('invalid remainder or source identity')
        object.__setattr__(self,'center',c);object.__setattr__(self,'remainder_radius',r)
        object.__setattr__(self,'coefficients',MappingProxyType({k:exact(v) for k,v in self.coefficients.items()}))
    @property
    def radius(self):return sum(map(abs,self.coefficients.values()),self.remainder_radius)
    @property
    def bound(self):return abs(self.center)+self.radius


def paired_difference(full:AffineBudget,half:AffineBudget):
    ids=set(full.coefficients)|set(half.coefficients)
    return AffineBudget(half.center-full.center,
        {i:half.coefficients.get(i,Fraction(0))-full.coefficients.get(i,Fraction(0)) for i in ids},
        full.remainder_radius+half.remainder_radius)


def compare_declared_budget(full,half,limit):
    delta=paired_difference(full,half);limit=exact(limit)
    if limit<=0:raise ValueError('positive predeclared minicriterion required')
    cartesian=abs(half.center-full.center)+full.radius+half.radius
    return {'paired_bound':delta.bound,'cartesian_bound':cartesian,
            'strict_declared_bound_below_limit':delta.bound<limit,
            'scope':'CONDITIONAL_ON_SUPPLIED_MAP_ENCLOSURES_NOT_CANONICAL_ACCEPTANCE'}
