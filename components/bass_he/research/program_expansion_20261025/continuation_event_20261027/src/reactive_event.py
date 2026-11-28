"""Conditional labelled 2-to-2 Newtonian event moments; no rate or DCS inference.

The caller supplies a complete axisymmetric CM angular measure and explicit
internal-state energies. Product birth pools remain unassigned. Internal energy
is a population-derived witness, never a second independently evolved source.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import math
from numbers import Real
from pathlib import Path
import sys
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
LEGACY_PATH = ROOT.parent / "continuation_20261025/exchange/exchange_closure.py"
LEGACY_SHA256 = "533c49838d03572b106168cd9333a20e1b4a7d06f88d5f3727f8b80c5b96f262"
if hashlib.sha256(LEGACY_PATH.read_bytes()).hexdigest() != LEGACY_SHA256:
    raise RuntimeError("Inherited exchange/caloric implementation identity changed")
_spec = importlib.util.spec_from_file_location("he_event03_intake01_exchange", LEGACY_PATH)
LEGACY = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = LEGACY
_spec.loader.exec_module(LEGACY)
AngularTransport = LEGACY.AngularTransport
ConservativeSource = LEGACY.ConservativeSource
CaloricSpecies = LEGACY.CaloricSpecies
temperature_rhs = LEGACY.temperature_rhs
monatomic_caloric = LEGACY.monatomic_caloric
ContractError = LEGACY.ContractError
Vec3 = tuple[float, float, float]
Mat3 = tuple[Vec3, Vec3, Vec3]


def finite(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ContractError(name + " must be a finite real scalar")
    try:
        value = float(value)
    except (ValueError, OverflowError) as error:
        raise ContractError(name + " exceeds binary64") from error
    if not math.isfinite(value):
        raise ContractError(name + " must be finite")
    return value


def vec(value, name):
    try:
        values = tuple(finite(x, name) for x in value)
    except TypeError as error:
        raise ContractError(name + " must contain three scalars") from error
    if len(values) != 3:
        raise ContractError(name + " must contain three scalars")
    return values


def total(values, name="derived sum"):
    try:
        return finite(math.fsum(values), name)
    except (OverflowError, ValueError) as error:
        raise ContractError(name + " exceeds binary64") from error


def _scaled(values, divisors=()):
    """Keep exponents separate so representable products need no unsafe staging."""
    mantissa, exponent = 1.0, 0
    for value in values:
        if value == 0:
            return 0.0, 0
        m, e = math.frexp(value)
        mantissa *= m
        exponent += e
        mantissa, e = math.frexp(mantissa)
        exponent += e
    for value in divisors:
        if value == 0:
            raise ContractError("zero derived divisor")
        m, e = math.frexp(value)
        mantissa /= m
        exponent -= e
        mantissa, e = math.frexp(mantissa)
        exponent += e
    return mantissa, exponent


def product(*values, divisors=(), square_root=False):
    m, e = _scaled(values, divisors)
    if square_root:
        if m < 0:
            raise ContractError("negative square-root argument")
        if e % 2:
            m *= 2
            e -= 1
        m, e = math.sqrt(m), e // 2
    try:
        result = math.ldexp(m, e)
    except OverflowError as error:
        raise ContractError("derived product overflows binary64") from error
    if not math.isfinite(result) or (result == 0 and m != 0):
        raise ContractError("nonzero derived product is outside binary64 range")
    return result


@dataclass(frozen=True)
class ReactiveSource:
    source_id: str
    immutable_locator: str
    incoming_ids: tuple[str, str]
    outgoing_ids: tuple[str, str]
    energy_min_j: float
    energy_max_j: float
    full_com_angular_support: bool
    axisymmetric_about_relative_velocity: bool
    count_convention: str
    mass_convention: str
    internal_energy_convention: str
    internal_energy_owner: str

    def check(self, incoming_energy_j, purpose):
        if purpose != "conditional_algebra":
            raise ContractError("Only conditional_algebra is implemented")
        for pair in (self.incoming_ids, self.outgoing_ids):
            if not isinstance(pair, tuple) or len(pair) != 2 or any(not isinstance(i,str) or not i for i in pair):
                raise ContractError("Two exact incoming and outgoing species/state IDs are required")
        if not isinstance(self.source_id,str) or not self.source_id or not isinstance(self.immutable_locator,str) or not self.immutable_locator:
            raise ContractError("Source identity and immutable locator required")
        lo, hi = finite(self.energy_min_j,"source energy minimum"), finite(self.energy_max_j,"source energy maximum")
        if lo < 0 or hi < lo or not lo <= incoming_energy_j <= hi:
            raise ContractError("Incoming CM energy outside source support")
        if self.full_com_angular_support is not True or self.axisymmetric_about_relative_velocity is not True:
            raise ContractError("Full axisymmetric CM angular support required")
        if self.count_convention != "labelled_pair_once":
            raise ContractError("Event count must be labelled_pair_once")
        if self.mass_convention != "constant_compositional_inertial_mass":
            raise ContractError("Constant compositional inertial masses required")
        if self.internal_energy_convention != "explicit_nonrel_internal_energy_separate_from_inertial_mass":
            raise ContractError("Explicit internal energy separate from inertial mass required")
        if self.internal_energy_owner != "population_derived_internal_witness":
            raise ContractError("Internal energy must have one population-derived owner")


@dataclass(frozen=True)
class SpeciesMoment:
    number_m2: float
    mass_kg_m2: float
    momentum_kg_m3_s: Vec3
    kinetic_j_m2: float
    second_j_m2: Mat3


@dataclass(frozen=True)
class ReactiveEventMoments:
    source_id: str
    incoming_ids: tuple[str, str]
    outgoing_ids: tuple[str, str]
    species: dict[str, SpeciesMoment]
    incoming_energy_j: float
    outgoing_energy_j: float
    delta_internal_j: float
    mass_sum_roundoff_residual_kg: float
    population_internal_witness_j_m2: float
    purpose: str = "conditional_algebra"
    physical_admitted: bool = False
    birth_pool: str = "UNASSIGNED"

    def to_dict(self):
        return asdict(self)


def reactive_moment_kernel(
    source: ReactiveSource, mass_kg: Mapping[str,float], internal_energy_j: Mapping[str,float],
    velocity_a_m_s: Vec3, velocity_b_m_s: Vec3, angular: AngularTransport, *, purpose: str,
) -> ReactiveEventMoments:
    """Cross-section weighted gain/loss moments, before encounter-flux integration."""
    source.check(source.energy_min_j,purpose)
    ids = source.incoming_ids + source.outgoing_ids
    try:
        masses = {i:finite(mass_kg[i],"species mass") for i in set(ids)}
        eps = {i:finite(internal_energy_j[i],"species internal energy") for i in set(ids)}
    except (KeyError, TypeError) as error:
        raise ContractError("Every exact species/state ID requires mass and internal energy") from error
    if any(m <= 0 for m in masses.values()):
        raise ContractError("Species masses must be positive")
    a,b,c,d = ids
    ma,mb,mc,md = (masses[i] for i in ids)
    mi,mo = total((ma,mb),"incoming mass sum"),total((mc,md),"outgoing mass sum")
    residual = total((mi,-mo),"mass sum residual")
    if abs(residual)/max(mi,mo) > 16*sys.float_info.epsilon:
        raise ContractError("Physical mass defect is outside constant-mass convention")
    va,vb = vec(velocity_a_m_s,"velocity a"),vec(velocity_b_m_s,"velocity b")
    g = tuple(total((x,-y),"relative velocity") for x,y in zip(va,vb))
    speed = finite(math.hypot(*g),"relative speed")
    com = tuple(total((product(ma,x,divisors=(mi,)),product(mb,y,divisors=(mi,))),"COM velocity") for x,y in zip(va,vb))
    muin,muout = product(ma,mb,divisors=(mi,)),product(mc,md,divisors=(mi,))
    ein = product(0.5,muin,speed,speed)
    delta = total((eps[c],eps[d],-eps[a],-eps[b]),"internal energy gap")
    eout = total((ein,-delta),"outgoing CM energy")
    source.check(ein,purpose)
    if not isinstance(angular,AngularTransport):
        raise ContractError("Reuse the supplied AngularTransport interface")
    for value in (angular.sigma0_m2,angular.sigma1_m2,angular.sigma2_m2):
        finite(value,"angular moment")
    angular.validate()
    s0,s1,s2 = angular.sigma0_m2,angular.sigma1_m2,angular.sigma2_m2
    if speed == 0 and (s1 != s0 or s2 != s0):
        raise ContractError("Zero incoming speed permits only isotropic angular moments")
    if s0 > 0 and eout < 0:
        raise ContractError("Positive cross section on a closed outgoing branch")
    zero = SpeciesMoment(0.0,0.0,(0.0,)*3,0.0,((0.0,)*3,)*3)
    if s0 == 0:
        return ReactiveEventMoments(source.source_id,source.incoming_ids,source.outgoing_ids,
            {i:zero for i in dict.fromkeys(ids)},ein,eout,delta,residual,0.0)
    axis = tuple(product(x,divisors=(speed,)) for x in g) if speed else (0.0,0.0,0.0)
    l1,l2 = total((s0,-s1)),total((s0,-s2))
    n = tuple(tuple(total((product(s2,1/3) if i==j else 0.0,product(l2,axis[i],axis[j]))) for j in range(3)) for i in range(3))
    p = product(2.0,muout,eout,square_root=True)
    legs = []
    for identifier,velocity in ((a,va),(b,vb)):
        m = masses[identifier]
        momentum = tuple(-product(s0,m,x) for x in velocity)
        tensor = tuple(tuple(-product(s0,m,velocity[i],velocity[j]) for j in range(3)) for i in range(3))
        kinetic = -total(product(0.5,s0,m,x,x) for x in velocity)
        legs.append((identifier,-s0,momentum,kinetic,tensor))
    for identifier,sign in ((c,1.0),(d,-1.0)):
        m = masses[identifier]
        momentum = tuple(total((product(s0,m,com[i]),product(sign,p,l1,axis[i]))) for i in range(3))
        tensor = tuple(tuple(total((product(s0,m,com[i],com[j]),product(sign,p,l1,com[i],axis[j]),product(sign,p,l1,axis[i],com[j]),product(p,p,n[i][j],divisors=(m,)))) for j in range(3)) for i in range(3))
        kinetic = total((total(product(0.5,s0,m,x,x) for x in com),product(0.5,s0,p,p,divisors=(m,)),total(product(sign,p,l1,com[i],axis[i]) for i in range(3))))
        legs.append((identifier,s0,momentum,kinetic,tensor))
    result = {}
    for identifier in dict.fromkeys(ids):
        own = [leg for leg in legs if leg[0]==identifier]
        number = total(leg[1] for leg in own)
        result[identifier] = SpeciesMoment(number,product(masses[identifier],number),
            tuple(total(leg[2][i] for leg in own) for i in range(3)),
            total(leg[3] for leg in own),
            tuple(tuple(total(leg[4][i][j] for leg in own) for j in range(3)) for i in range(3)))
    internal = total(product(eps[i],r.number_m2) for i,r in result.items())
    return ReactiveEventMoments(source.source_id,source.incoming_ids,source.outgoing_ids,result,ein,eout,delta,residual,internal)


def explicit_flux_adapter(event: ReactiveEventMoments, *, encounter_flux_m5_s: float):
    """Convert supplied weighted moments to raw volumetric sources; no rate default."""
    flux = finite(encounter_flux_m5_s,"encounter flux")
    if flux < 0:
        raise ContractError("Encounter flux must be nonnegative")
    if not isinstance(event,ReactiveEventMoments) or event.physical_admitted or event.birth_pool != "UNASSIGNED":
        raise ContractError("Expected an unassigned conditional event result")
    witness = finite(event.population_internal_witness_j_m2,"population internal witness")
    sources,gamma,second = {},{},{}
    for identifier,r in event.species.items():
        values = (r.number_m2,r.mass_kg_m2,r.kinetic_j_m2,*r.momentum_kg_m3_s,*(x for row in r.second_j_m2 for x in row))
        for value in values:finite(value,"weighted event moment")
        gamma[identifier] = product(flux,r.number_m2)
        sources[identifier] = ConservativeSource(product(flux,r.mass_kg_m2),tuple(product(flux,x) for x in r.momentum_kg_m3_s),product(flux,r.kinetic_j_m2))
        second[identifier] = tuple(tuple(product(flux,x) for x in row) for row in r.second_j_m2)
    return {"source_id":event.source_id,"Gamma_m3_s":gamma,"conservative_sources":sources,
        "second_w_m3":second,"population_internal_witness_w_m3":product(flux,witness),
        "internal_energy_owner":"population_derived_internal_witness","independent_internal_rhs_w_m3":None,
        "birth_pool":"UNASSIGNED","physical_admitted":False}
