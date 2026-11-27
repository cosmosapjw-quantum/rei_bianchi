"""H1 CI net number/heat/STF source from one source-defined differential law.

The source is Le--Cambier Eq85 with isotropic outgoing directions (III.E),
heavy fixed target and infinitesimal electron Grad first variation.  This
adapter does not select a finite-anisotropy, thermalization, or species-stress
partition closure.  pi_e is an ELECTRON pressure STF, not total gas pi_b.

Y21=n_species/n_b follows HE32 order; pure H means H0 index1, H+ index2,
Y1+Y2=1, all other entries0.  Charge neutrality fixes n_e=n_b*Y2.  All
retained nuclei/electrons must be declared thermal for the thermal bridge.
Heavy H->p pressure is carried between species and cancels at this leading
recoil-free order.  Q=-I*r and reservoir dEth are one energy owner.

The unchanged REI class has no explicit free-electron reactant. Its local
unary event H->p therefore uses a coefficient n_e*alpha frozen at the current
state. Its row Jacobian is FROZEN_NE_ONLY. A separate physical abundance
Jacobian includes d(n_e)/dY2 and is the derivative of the full pure-H source
at fixed T,n_b. Neither Jacobian includes temperature derivatives.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from collections.abc import Mapping
import math
import numpy as np

from .lc_ionization import LCModel, I_J, KB_J_K, MODEL_IDENTITY, MODEL_SCOPE
from .he36.event_bridge import (
    attach_event_tensor, NET_TENSOR_SCOPE, CENTRAL_FRAME,
    ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS, EVENT_ENERGY_UNIT,
)
from .he36.reactive_moments import (
    MomentDomainError, MomentRepresentabilityError, MOMENT_ROUNDOFF,
    _scalar, _matrix, _muldiv, _sum, _readonly,
)
from .he36.vendor.rei_resolved_local import (
    ResolvedEvent, Coefficient, ENERGY, Unresolved,
)

H0_INDEX=1
HP_INDEX=2
MASS_NUMBER=_readonly([1,1,1,2,2,3,3,3,3,3,4,4,4,6,6,6,6,7,7,7,7])
IONIC_CHARGE=_readonly([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3])
_MODEL=LCModel()
_NU=np.zeros(21);_NU[H0_INDEX]=-1.;_NU[HP_INDEX]=1.;_NU=_readonly(_NU)
FROZEN_NE_JACOBIAN_SCOPE='fixed_ne_effective_unary_event_not_physical_state_jacobian'
PHYSICAL_JACOBIAN_SCOPE='d(dY_dt)/dY_at_fixed_T_nb_with_ne_equals_nb_Yp'


def _no_bool(value,name):
    # Inspect object representation before mixed Python bool/numeric coercion.
    try:
        values=np.asarray(value,dtype=object)
    except (TypeError,ValueError) as exc:
        raise MomentDomainError(name+': REAL_ARRAY_REQUIRED') from exc
    if any(isinstance(x,(bool,np.bool_)) for x in values.flat):
        raise MomentDomainError(name+': BOOL_VALUES_FORBIDDEN')


def _state(Y21):
    _no_bool(Y21,'Y21')
    original=np.asarray(Y21)
    if original.dtype.kind not in 'fiu' or original.shape!=(21,):
        raise MomentDomainError('Y21: REAL_21_STATE_ARRAY_REQUIRED')
    y=np.asarray(original,dtype=np.float64)
    if not np.isfinite(y).all() or np.any(y<0):
        raise MomentDomainError('Y21: FINITE_NONNEGATIVE_VALUES_REQUIRED')
    other=np.ones(21,dtype=bool);other[[H0_INDEX,HP_INDEX]]=False
    if np.any(y[other]!=0):
        raise Unresolved('ONLY_PURE_H_H0_HPLUS_INVENTORY_ADMITTED')
    total=math.fsum((float(y[H0_INDEX]),float(y[HP_INDEX])))
    if abs(total-1)>MOMENT_ROUNDOFF:
        raise MomentDomainError('PURE_H_ABUNDANCE_MUST_SUM_TO_ONE_NO_RENORMALIZATION')
    return _readonly(y)


def _freeze(values):
    if isinstance(values,np.ndarray): return _readonly(values)
    if isinstance(values,Mapping): return MappingProxyType({k:_freeze(v) for k,v in values.items()})
    if isinstance(values,list): return tuple(_freeze(v) for v in values)
    return values


@dataclass(frozen=True,slots=True)
class H1CISource:
    status: str
    temperature_K: float
    nb_m3: float
    ne_m3: float
    nH_m3: float
    Y21: np.ndarray
    electron_pi_Pa: np.ndarray
    alpha_m3_s: float
    kappa2_m3_s: float
    volumetric_event_rate: float
    abundance_source_s: np.ndarray
    R_species: np.ndarray
    Relectron: float
    Rnucleus: float
    Rpart: float
    S: np.ndarray
    Q: float
    J: np.ndarray
    physical_abundance_jacobian_s: np.ndarray
    physical_rate_gradient_s: np.ndarray
    event_row_frozen_ne: Mapping|None
    event_tensor_source: object|None
    reservoir_sources_W_m3: Mapping
    per_event_tensor_J: np.ndarray|None
    thermal_particle_density_m3: float
    dot_T_reaction_K_s: float|None
    dot_T_status: str
    electron_grad_relative_norm: float
    model_identity: str=MODEL_IDENTITY
    model_scope: str=MODEL_SCOPE
    physical_jacobian_scope: str=PHYSICAL_JACOBIAN_SCOPE
    donor_jacobian_scope: str=FROZEN_NE_JACOBIAN_SCOPE
    pressure_scope: str='electron_STF_first_variation_no_total_gas_partition'
    energy_owner: str='Q_and_reservoir_dEth_are_same_quantity_do_not_add'


def h1_ci_source(temperature_K,Y21,nb_m3,electron_pi_Pa,*,
                 thermal_inventory_scope=None,charge_census_scope=None):
    """Return the complete source within the explicitly declared H1 model.

    Source evaluation calls no IVP and no thermalization model. Input pi_e is
    an infinitesimal STF direction: its normalized magnitude is reported,
    not accepted as a finite-amplitude PDF positivity certificate. The tensor
    is never clipped or projected. Nonzero underflow/overflow is rejected.

    The physical Jacobian is the ambient polynomial extension in H0,H+,
    with fixed T,n_b. On the normalized pure-H manifold only directions
    dY_H+dY_p=0 are admissible. All other species remain outside this model.
    Zero electron/target/density states have known zero source. They are not
    physical cross-section support zero; no missing gain is filled with zero.
    """
    if thermal_inventory_scope!=ALL_RETAINED_THERMAL:
        raise Unresolved('EXPLICIT_ALL_RETAINED_PARTICLES_THERMAL_SCOPE_REQUIRED')
    if charge_census_scope!=NEUTRAL_21_STATE_CENSUS:
        raise Unresolved('EXPLICIT_NEUTRAL_21_STATE_CENSUS_REQUIRED')
    temperature=_scalar(temperature_K,'temperature_K',positive=True)
    density=_scalar(nb_m3,'nb_m3',nonnegative=True)
    y=_state(Y21)
    _no_bool(electron_pi_Pa,'electron_pi_Pa')
    pi,pinorm,_,_=_matrix(electron_pi_Pa,'electron_pi_Pa',traceless=True)
    ne=_muldiv((density,float(y[HP_INDEX])),label='ne')
    nh=_muldiv((density,float(y[H0_INDEX])),label='nH')
    if ne==0 and pinorm!=0:
        raise MomentDomainError('ZERO_ELECTRON_DENSITY_REQUIRES_ZERO_ELECTRON_STF')
    evaluation=_MODEL.evaluate(temperature)
    alpha=float(evaluation.alpha_m3_s[0]);kappa=float(evaluation.kappa2_m3_s[0])
    theta=_muldiv((KB_J_K,temperature),label='theta')
    relative=0. if pinorm==0 else _muldiv((pinorm,),(ne,theta),label='electron_grad_relative_norm')
    # Exact polynomial source derivative at fixed T and n_b, including ne(Y).
    grad=np.zeros(21)
    grad[H0_INDEX]=_muldiv((density,alpha,float(y[HP_INDEX])),label='physical_dr_dYH')
    grad[HP_INDEX]=_muldiv((density,alpha,float(y[H0_INDEX])),label='physical_dr_dYp')
    jac=np.outer(_NU,grad)
    # A normalized pure-H number census is n_H + n_p + n_e.
    census=math.fsum((float(y[H0_INDEX]),2.*float(y[HP_INDEX])))
    npart=_muldiv((density,census),label='thermal_particle_density')
    if density==0 or ne==0 or nh==0:
        status='ZERO_DENSITY' if density==0 else ('ZERO_ELECTRON' if ne==0 else 'ZERO_TARGET')
        zero21=_readonly(np.zeros(21));zero33=_readonly(np.zeros((3,3)))
        zeros=MappingProxyType({k:0. for k in ENERGY[2:]})
        return H1CISource(status,temperature,density,ne,nh,y,pi,alpha,kappa,0.,zero21,zero21,
                         0.,0.,0.,zero33,0.,zero33,_readonly(jac),_readonly(grad),None,None,
                         zeros,None,npart,None if npart==0 else 0.,
                         'UNDEFINED_VACUUM_TEMPERATURE' if npart==0 else 'ZERO_REACTION_SOURCE',relative)
    hazard=_muldiv((ne,alpha),label='effective_unary_ne_alpha')
    ledger={k:0. for k in ENERGY};ledger['dI']=I_J;ledger['dEth']=-I_J
    ionization=np.zeros(21);ionization[HP_INDEX]=I_J
    event=ResolvedEvent(
        'HE37_H1_CI_LC_ISOTROPIC', {H0_INDEX:1},{HP_INDEX:1},
        Coefficient.positive(hazard),'s^-1',
        'Le-Cambier2016 Eq85/III.E; model='+MODEL_IDENTITY,
        'pureH_charge_neutral; heavy_fixed_target; electron_Grad_first_variation; frozen_ne_unary',
        ledger,MASS_NUMBER,IONIC_CHARGE,ionization_reference=ionization,
    )
    tensor=np.empty((3,3))
    iso=-2.*I_J/3.
    for i in range(3):
        for j in range(3):
            stf=-_muldiv((kappa,float(pi[i,j])),(ne,alpha),label='per_event_electron_STF')
            tensor[i,j]=_sum((stf,iso if i==j else 0.),label='per_event_net_tensor')
    attached=attach_event_tensor(
        event,y,density,per_event_tensor_J=tensor,energy_unit=EVENT_ENERGY_UNIT,
        tensor_scope=NET_TENSOR_SCOPE,central_frame=CENTRAL_FRAME,
        tensor_provenance='HE37 source-native LC Eq85+III.E gain/loss sum; model='+MODEL_IDENTITY,
        thermal_inventory_scope=thermal_inventory_scope,charge_census_scope=charge_census_scope,
    )
    if attached.row['status']!='POSITIVE':
        raise MomentRepresentabilityError('POSITIVE_REACTANTS_DID_NOT_PRODUCE_POSITIVE_EVENT')
    rate=attached.volumetric_event_rate
    # Stable physical STF formula keeps a tiny STF from subtraction loss in
    # the donor's isotropic projection. The full tensor remains donor-owned.
    stf_source=np.array([[-_muldiv((nh,kappa,float(pi[i,j])),label='net_J')
                          for j in range(3)] for i in range(3)])
    source_scale=float(np.max(np.abs(attached.S)))
    mismatch=0. if source_scale==0 else float(np.max(np.abs((stf_source-attached.J)/source_scale)))
    if mismatch>4*MOMENT_ROUNDOFF:
        raise MomentDomainError('INDEPENDENT_STF_AND_DONOR_PROJECTION_DISAGREE')
    # Use event rate / n_part first, never a separate additional heat owner.
    quotient=_muldiv((rate,),(npart,),label='reaction_rate_per_thermal_particle')
    temp_factor=_sum((temperature,_muldiv((2.,I_J),(3.,KB_J_K),label='ionization_temperature')),
                     label='reaction_temperature_factor')
    tdot=-_muldiv((quotient,temp_factor),label='reaction_temperature_source')
    return H1CISource(
        'POSITIVE',temperature,density,ne,nh,y,pi,alpha,kappa,rate,
        _readonly(attached.row['source']),attached.R_species,attached.Relectron,
        attached.Rnucleus,attached.Rpart,attached.S,attached.Q,_readonly(stf_source),
        _readonly(jac),_readonly(grad),attached.row,attached,
        attached.reservoir_sources_W_m3,attached.per_event_tensor_J,npart,tdot,
        'CONDITIONAL_ALL_THERMAL_REACTION_ONLY',relative,
    )
