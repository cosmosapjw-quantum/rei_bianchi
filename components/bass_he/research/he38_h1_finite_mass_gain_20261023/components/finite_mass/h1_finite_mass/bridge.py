"""Pure-H21 event lift using unchanged HE36/REI ownership and Jacobians.

Only H0(index1), H+(index2) are present, Y_H+Y_p=1 and ne=nb*Y_p.
The physical fixed-T,nb abundance Jacobian includes electron-density feedback;
the unchanged unary donor's Jacobian freezes ne and is separately returned.
Scalar heat and reservoir dEth are the same owner. pi_e/pi_H are independent
species STF directions, never a supplied total-gas pi_b allocation.
"""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from collections.abc import Mapping
import math
import numpy as np
from .model import (
    finite_mass_source, SpeciesSources, _real, I_J, KB_J_K, MODEL_IDENTITY,
    MomentDomainError, MomentRepresentabilityError, MOMENT_ROUNDOFF,
    _scalar, _muldiv, _sum, _readonly,
)
from .he36.event_bridge import (
    attach_event_tensor, NET_TENSOR_SCOPE, CENTRAL_FRAME, EVENT_ENERGY_UNIT,
    ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS,
)
from .he36.vendor.rei_resolved_local import ResolvedEvent, Coefficient, ENERGY, Unresolved

H0_INDEX=1
HP_INDEX=2
MASS_NUMBER=_readonly([1,1,1,2,2,3,3,3,3,3,4,4,4,6,6,6,6,7,7,7,7])
IONIC_CHARGE=_readonly([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3])
_NU=np.zeros(21);_NU[H0_INDEX]=-1.;_NU[HP_INDEX]=1.;_NU=_readonly(_NU)
FROZEN_NE_JACOBIAN_SCOPE='fixed_ne_effective_unary_event_not_physical_state_jacobian'
PHYSICAL_JACOBIAN_SCOPE='ambient_dY_source_dY_fixed_T_nb_ne_equals_nb_Yp_pure_H_tangent_only'


def _state(values):
    y=_real(values,'Y21')
    if y.shape!=(21,) or np.any(y<0): raise MomentDomainError('FINITE_NONNEGATIVE_21_STATE_REQUIRED')
    other=np.ones(21,dtype=bool);other[[H0_INDEX,HP_INDEX]]=False
    if np.any(y[other]!=0): raise Unresolved('ONLY_PURE_H_H0_HPLUS_INVENTORY_ADMITTED')
    if abs(math.fsum((float(y[H0_INDEX]),float(y[HP_INDEX])))-1.0)>MOMENT_ROUNDOFF:
        raise MomentDomainError('PURE_H_ABUNDANCE_MUST_SUM_TO_ONE_NO_RENORMALIZATION')
    return _readonly(y)


@dataclass(frozen=True,slots=True)
class H1FiniteMassSource:
    """Immutable physical result plus an unchanged donor audit snapshot.

    ``J`` and ``species.total_J_Pa_s`` are the authoritative scientific STF
    fields, evaluated directly without subtracting an isotropic trace.
    ``event_tensor_source`` retains the donor audit output. Its nested ``J``
    uses the legacy HE36 trace projection and may round a tiny STF to zero;
    scientific STF consumers must use the wrapper/direct species fields.
    """
    species: SpeciesSources
    Y21: np.ndarray
    nb_m3: float
    abundance_source_s: np.ndarray
    R_species: np.ndarray
    Relectron: float
    Rnucleus: float
    Rpart: float
    physical_abundance_jacobian_s: np.ndarray
    physical_rate_gradient_s: np.ndarray
    frozen_ne_abundance_jacobian_s: np.ndarray
    event_row_frozen_ne: Mapping|None
    event_tensor_source: object|None  # donor audit; nested J is legacy trace projection
    reservoir_sources_W_m3: Mapping
    thermal_particle_density_m3: float
    dot_T_reaction_K_s: float|None
    dot_T_status: str
    model_identity: str=MODEL_IDENTITY
    physical_jacobian_scope: str=PHYSICAL_JACOBIAN_SCOPE
    donor_jacobian_scope: str=FROZEN_NE_JACOBIAN_SCOPE
    energy_owner: str='species_total_Q_and_reservoir_dEth_are_one_quantity_do_not_add'

    @property
    def Q(self): return self.species.total_Q_W_m3
    @property
    def J(self): return self.species.total_J_Pa_s
    @property
    def S(self): return self.species.total_S_Pa_s
    @property
    def volumetric_event_rate(self): return self.species.volumetric_event_rate
    @property
    def status(self): return self.species.status


def h1_ci_source(temperature_K,Y21,nb_m3,electron_pi_Pa,neutral_pi_Pa,*,
                 thermal_inventory_scope=None,charge_census_scope=None,linear_response=True):
    """Attach the complete finite-mass total tensor to the exact scalar donor.

    Derivatives are at fixed T and nb; temperature/stress derivatives are not
    included. Physical Jacobian is an ambient polynomial extension, applicable
    on the normalized pure-H state only along dY_H+dY_p=0 directions. Neither
    a nonzero boundary derivative nor a donor derivative is a source at an
    absent-reactant state. Thermal dotT requires the explicitly stated inventory.
    """
    if thermal_inventory_scope!=ALL_RETAINED_THERMAL:
        raise Unresolved('EXPLICIT_ALL_RETAINED_PARTICLES_THERMAL_SCOPE_REQUIRED')
    if charge_census_scope!=NEUTRAL_21_STATE_CENSUS:
        raise Unresolved('EXPLICIT_NEUTRAL_21_STATE_CENSUS_REQUIRED')
    nb=_scalar(nb_m3,'nb_m3',nonnegative=True);y=_state(Y21)
    ne=_muldiv((nb,float(y[HP_INDEX])),label='electron_density')
    nh=_muldiv((nb,float(y[H0_INDEX])),label='neutral_density')
    source=finite_mass_source(temperature_K,ne,nh,electron_pi_Pa,neutral_pi_Pa,linear_response=linear_response)
    alpha=float(source.evaluation.alpha_m3_s[0]);rate=source.volumetric_event_rate
    grad=np.zeros(21)
    grad[H0_INDEX]=_muldiv((nb,alpha,float(y[HP_INDEX])),label='dr_dYH')
    grad[HP_INDEX]=_muldiv((nb,alpha,float(y[H0_INDEX])),label='dr_dYp')
    frozen_grad=np.zeros(21);frozen_grad[H0_INDEX]=grad[H0_INDEX]
    jac=_readonly(np.outer(_NU,grad));frozen_jac=_readonly(np.outer(_NU,frozen_grad))
    npart=_muldiv((nb,math.fsum((float(y[H0_INDEX]),2.0*float(y[HP_INDEX])))),label='thermal_census')
    if ne==0 or nh==0:
        zeros=_readonly(np.zeros(21));res=MappingProxyType({key:0.0 for key in ENERGY[2:]})
        return H1FiniteMassSource(source,y,nb,zeros,zeros,0.0,0.0,0.0,jac,_readonly(grad),
            frozen_jac,None,None,res,npart,None if npart==0 else 0.0,
            'UNDEFINED_VACUUM_TEMPERATURE' if npart==0 else 'ZERO_REACTION_SOURCE')
    hazard=_muldiv((ne,alpha),label='frozen_ne_alpha')
    ledger={key:0.0 for key in ENERGY};ledger['dI']=I_J;ledger['dEth']=-I_J
    ref=np.zeros(21);ref[HP_INDEX]=I_J
    event=ResolvedEvent('HE38_H1_CI_FINITE_MASS',{H0_INDEX:1},{HP_INDEX:1},
        Coefficient.positive(hazard),'s^-1','Le-Cambier Eq2-7/85; model='+MODEL_IDENTITY,
        'pure_H_neutral; common_T_u; source_Jacobi_uniform_G; frozen_ne_unary',
        ledger,MASS_NUMBER,IONIC_CHARGE,ionization_reference=ref)
    tensor=np.empty((3,3))
    for i in range(3):
        for j in range(3):
            stf=_muldiv((float(source.J[i,j]),),(rate,),label='per_event_STF')
            tensor[i,j]=_sum((stf,-2.0*I_J/3.0 if i==j else 0.0),label='per_event_tensor')
    attached=attach_event_tensor(event,y,nb,per_event_tensor_J=tensor,
        energy_unit=EVENT_ENERGY_UNIT,tensor_scope=NET_TENSOR_SCOPE,central_frame=CENTRAL_FRAME,
        tensor_provenance='HE38 complete finite-mass gain+loss; '+MODEL_IDENTITY,
        thermal_inventory_scope=thermal_inventory_scope,charge_census_scope=charge_census_scope)
    if attached.row['status']!='POSITIVE':
        raise MomentRepresentabilityError('POSITIVE_REACTANTS_DID_NOT_PRODUCE_POSITIVE_DONOR')
    for actual,expected,label in ((attached.volumetric_event_rate,rate,'rate'),(attached.Q,source.Q,'heat')):
        scale=max(abs(actual),abs(expected))
        if scale and abs(actual/scale-expected/scale)>4*MOMENT_ROUNDOFF:
            raise MomentDomainError('DIRECT_AND_DONOR_DISAGREE_'+label)
    scale=max(float(np.max(np.abs(attached.S))),float(np.max(np.abs(source.S))))
    if scale and np.max(np.abs(attached.S/scale-source.S/scale))>4*MOMENT_ROUNDOFF:
        raise MomentDomainError('DIRECT_AND_DONOR_TENSOR_DISAGREE')
    quotient=_muldiv((rate,),(npart,),label='rate_per_thermal_particle')
    tfactor=_sum((source.temperature_K,_muldiv((2.,I_J),(3.,KB_J_K),label='ionization_temperature')),label='temperature_factor')
    tdot=-_muldiv((quotient,tfactor),label='reaction_temperature_source')
    return H1FiniteMassSource(source,y,nb,_readonly(attached.row['source']),attached.R_species,
        attached.Relectron,attached.Rnucleus,attached.Rpart,jac,_readonly(grad),frozen_jac,
        attached.row,attached,attached.reservoir_sources_W_m3,npart,tdot,
        'CONDITIONAL_ALL_RETAINED_COMMON_THERMAL_POOL')
