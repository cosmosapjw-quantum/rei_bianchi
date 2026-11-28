"""HE38 finite-mass source-coordinate H1 CI model.

Le--Cambier Eq2--7/85 with explicitly uniform directions of the original
Jacobi g1,g2. Common T/common bulk and independent infinitesimal electron/H
STF directions only. No angular calibration or finite-amplitude closure.
The byte-preserved HE37 provider remains an arithmetic donor, not the
identity or energy-mapping owner of the present finite-mass model.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import json
import math
import numpy as np
from .vendor import lc_ionization as donor
from .he36.reactive_moments import (
    MomentDomainError, MomentRepresentabilityError, MOMENT_ROUNDOFF,
    _scalar, _matrix, _muldiv, _sum, _readonly, _pressure_source,
)

ME_KG = donor.ME_KG
MP_KG = 1.67262192595e-27
MH_KG = MP_KG + ME_KG
TOTAL_MASS_KG = MP_KG + 2.0*ME_KG
KB_J_K = donor.KB_J_K
EV_J = donor.EV_J
I_J = donor.I_J
I_EV = donor.I_EV
A0_M = donor.A0_M
ETA = ME_KG/TOTAL_MASS_KG
ZETA = MH_KG/TOTAL_MASS_KG
ION_FRACTION_INNER = MP_KG/MH_KG
ELECTRON_FRACTION_INNER = ME_KG/MH_KG
MU_KG = ME_KG*ZETA
MU_INNER_KG = ME_KG*ION_FRACTION_INNER
TEMPERATURE_DOMAIN_K = donor.TEMPERATURE_DOMAIN_K
MODEL_SCOPE = 'LC_original_Jacobi_finite_mass_uniform_G_common_T_bulk_linear_e_H_STF'
ENERGY_MAPPING = 'relative_COM_E_mu_g0_squared_over_2'
PROVIDER_SHA256 = '9d40436fbebd2e99666cf15ed069ba4041693de32da843dc23b9672d59b12a16'
_CONTRACT = dict(algorithm='he38_finite_mass_moments_v1',provider_sha256=PROVIDER_SHA256,
    source_pdf_sha256=donor.SOURCE_PDF_SHA256,source_doi=donor.SOURCE_DOI,
    model_scope=MODEL_SCOPE,energy_mapping=ENERGY_MAPPING,m_e_kg=ME_KG,m_p_kg=MP_KG,
    mass_convention='m_H=m_p+m_e_Newtonian_additivity_separate_I_ledger',
    threshold_eV=I_EV,a0_m=A0_M,temperature_domain_K=TEMPERATURE_DOMAIN_K,
    angular_density='1/(16*pi^2)_in_original_g1_g2',physical_angular_calibration=False)
MODEL_IDENTITY = hashlib.sha256(json.dumps(_CONTRACT,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
_DONOR = donor.LCModel()


def _no_bool(value, name):
    try:
        array = np.asarray(value,dtype=object)
    except (TypeError,ValueError) as exc:
        raise MomentDomainError(name+': REAL_NUMERIC_VALUES_REQUIRED') from exc
    if any(isinstance(v,(bool,np.bool_)) for v in array.flat):
        raise MomentDomainError(name+': BOOL_VALUES_FORBIDDEN')


def _real(value,name):
    _no_bool(value,name)
    array=np.asarray(value)
    if array.dtype.kind not in 'fiu':
        raise MomentDomainError(name+': REAL_NUMERIC_VALUES_REQUIRED')
    try:
        result=np.asarray(array,dtype=np.float64)
    except (TypeError,ValueError,OverflowError) as exc:
        raise MomentDomainError(name+': FINITE_BINARY64_REQUIRED') from exc
    if not np.isfinite(result).all():
        raise MomentDomainError(name+': FINITE_BINARY64_REQUIRED')
    return result


@dataclass(frozen=True,slots=True)
class FiniteMassEvaluation:
    temperature_K: np.ndarray
    moments_SI: np.ndarray
    log_moments_SI: np.ndarray
    kappa1_m3_s: np.ndarray
    kappa2_m3_s: np.ndarray
    sharing_moment_J_m3_s: np.ndarray
    first_jacobi_energy_moment_J_m3_s: np.ndarray
    heat_per_pair_J_m3_s: np.ndarray
    heavy_heat_per_pair_J_m3_s: np.ndarray
    stf_coefficients_m3_s: np.ndarray
    conditional_mean_energy_J: np.ndarray
    identity: str = MODEL_IDENTITY
    model_scope: str = MODEL_SCOPE
    energy_mapping: str = ENERGY_MAPPING
    reduced_mass_kg: float = MU_KG
    eta: float = ETA
    zeta: float = ZETA
    ion_fraction_inner: float = ION_FRACTION_INNER
    electron_fraction_inner: float = ELECTRON_FRACTION_INNER
    threshold_eV: float = I_EV
    physical_angular_calibration: bool = False
    species_order: tuple = ('electron','H0','proton')
    stf_input_order: tuple = ('electron','H0')

    @property
    def alpha_m3_s(self): return self.moments_SI[:,0]
    @property
    def beta_J_m3_s(self): return self.moments_SI[:,1]
    @property
    def gamma_J2_m3_s(self): return self.moments_SI[:,2]
    @property
    def delta_J3_m3_s(self): return self.moments_SI[:,3]
    @property
    def kappa2(self): return self.kappa2_m3_s


@dataclass(frozen=True,slots=True)
class FiniteMassModel:
    identity: str = field(default=MODEL_IDENTITY,init=False)
    temperature_domain_K: tuple = field(default=TEMPERATURE_DOMAIN_K,init=False)
    model_scope: str = field(default=MODEL_SCOPE,init=False)

    def evaluate(self,temperature_K):
        t=_real(temperature_K,'temperature_K')
        native=_DONOR.evaluate(t)
        theta=KB_J_K*native.temperature_K
        moments=native.moments_SI/math.sqrt(ZETA)
        alpha,beta,gamma,_=moments.T
        k1=2.0*beta/(3.0*theta)
        k2=4.0*gamma/(15.0*theta**2)
        ta=theta*alpha
        eta,zeta,c,d=ETA,ZETA,ION_FRACTION_INNER,ELECTRON_FRACTION_INNER
        w=eta*d
        # Stable compressed expressions: no small U2 subtraction is needed.
        qe=(1.5*eta+2.0*w)*ta-w*beta-c*I_J*alpha
        qh=-1.5*zeta*ta-eta*beta
        qp=(1.5*(zeta-eta)-2.0*w)*ta+d*beta-d*I_J*alpha
        qheavy=-(1.5*eta+2.0*w)*ta+w*beta-d*I_J*alpha
        aa=eta**2*alpha+2.0*eta*zeta*k1+zeta**2*k2
        bb=zeta**2*alpha+2.0*eta*zeta*k1+eta**2*k2
        cc=eta*zeta*(alpha-2.0*k1+k2)
        block=np.stack((np.column_stack((2.0*eta**2*alpha-aa,2.0*eta*zeta*alpha-cc)),
                        np.column_stack((-cc,-bb)),
                        np.column_stack((eta*(zeta-eta)*alpha,zeta*(zeta-eta)*alpha))),axis=1)
        heat=np.column_stack((qe,qh,qp))
        if not np.isfinite(moments).all() or not np.isfinite(heat).all() or not np.isfinite(block).all():
            raise MomentRepresentabilityError('FINITE_MASS_MOMENT_OVERFLOW')
        return FiniteMassEvaluation(_readonly(native.temperature_K),_readonly(moments),
            _readonly(np.log(moments)),_readonly(k1),_readonly(k2),_readonly(beta-ta),
            _readonly(ta),_readonly(heat),_readonly(qheavy),_readonly(block),
            _readonly(beta/alpha))


def sigma_m2(energy_eV):
    """Eq85 cross section at relative COM energy, not lab electron energy."""
    return donor.sigma_m2(_real(energy_eV,'energy_eV'))


def transfer_u(energy_eV,u):
    return donor.transfer_u(_real(energy_eV,'energy_eV'),_real(u,'u'))


def transfer_mean_eV(energy_eV):
    """Conditional transfer mean; continuous threshold limit I."""
    e=_real(energy_eV,'energy_eV')
    if np.any(e<I_EV): raise MomentDomainError('TRANSFER_REQUIRES_E_AT_OR_ABOVE_I')
    x=(e-I_EV)/I_EV
    quotient=np.ones_like(x)
    np.divide(np.log1p(x),x,out=quotient,where=x!=0)
    value=e*quotient
    if not np.isfinite(value).all(): raise MomentRepresentabilityError('TRANSFER_MEAN_OVERFLOW')
    return _readonly(value)


@dataclass(frozen=True,slots=True)
class SpeciesSources:
    temperature_K: float
    ne_m3: float
    nH_m3: float
    electron_pi_Pa: np.ndarray
    neutral_pi_Pa: np.ndarray
    evaluation: FiniteMassEvaluation
    volumetric_event_rate: float
    number_sources_m3_s: np.ndarray
    heat_sources_W_m3: np.ndarray
    stf_sources_Pa_s: np.ndarray
    pressure_sources_Pa_s: np.ndarray
    total_Q_W_m3: float
    total_J_Pa_s: np.ndarray
    total_S_Pa_s: np.ndarray
    heavy_Q_W_m3: float
    stf_response_s: np.ndarray
    relative_grad_norms: tuple
    status: str
    species_order: tuple = ('electron','H0','proton')
    model_identity: str = MODEL_IDENTITY
    energy_owner: str = 'species_heat_sum_and_total_Q_are_same_energy_owner'
    pressure_scope: str = 'independent_e_H_STF_first_variations_no_total_gas_closure'

    @property
    def Q(self): return self.total_Q_W_m3
    @property
    def J(self): return self.total_J_Pa_s
    @property
    def S(self): return self.total_S_Pa_s


def finite_mass_source(temperature_K,ne_m3,nH_m3,electron_pi_Pa,neutral_pi_Pa,*,linear_response=True):
    """Instantaneous e/H/p kinetic source at common T and common rest frame.

    No finite-amplitude Grad positivity claim is made. All input tensors are
    copied and validated without clipping/projection. Direct total Q/J and
    direct heavy combined Q avoid cancellation losses in summed species data.
    """
    if linear_response is not True: raise MomentDomainError('EXPLICIT_LINEAR_RESPONSE_TRUE_REQUIRED')
    t=_scalar(temperature_K,'temperature_K',positive=True)
    ne=_scalar(ne_m3,'ne_m3',nonnegative=True)
    nh=_scalar(nH_m3,'nH_m3',nonnegative=True)
    _no_bool(electron_pi_Pa,'electron_pi_Pa');_no_bool(neutral_pi_Pa,'neutral_pi_Pa')
    pe,enorm,_,_=_matrix(electron_pi_Pa,'electron_pi_Pa',traceless=True)
    ph,hnorm,_,_=_matrix(neutral_pi_Pa,'neutral_pi_Pa',traceless=True)
    if ne==0 and enorm!=0: raise MomentDomainError('ABSENT_ELECTRON_REQUIRES_ZERO_STF')
    if nh==0 and hnorm!=0: raise MomentDomainError('ABSENT_H_REQUIRES_ZERO_STF')
    ev=FiniteMassModel().evaluate(t)
    theta=KB_J_K*t
    alpha=float(ev.alpha_m3_s[0]);kappa=float(ev.kappa2_m3_s[0])
    norms=tuple(0.0 if norm==0 else _muldiv((norm,),(n,theta),label='relative_Grad_norm')
                for norm,n in ((enorm,ne),(hnorm,nh)))
    rate=_muldiv((ne,nh,alpha),label='event_rate')
    heat=np.array([_muldiv((ne,nh,float(v)),label='species_heat') for v in ev.heat_per_pair_J_m3_s[0]])
    response=np.array([[_muldiv((n,float(ev.stf_coefficients_m3_s[0,s,j])),label='STF_response')
                        for j,n in enumerate((nh,ne))] for s in range(3)])
    stf=np.empty((3,3,3))
    for s in range(3):
        for i in range(3):
            for j in range(3):
                stf[s,i,j]=_sum((_muldiv((float(response[s,0]),float(pe[i,j])),label='J_e_direction'),
                                  _muldiv((float(response[s,1]),float(ph[i,j])),label='J_H_direction')),label='species_J')
    total_j=np.empty((3,3))
    for i in range(3):
        for j in range(3):
            total_j[i,j]=-_sum((_muldiv((kappa,nh,ZETA,float(pe[i,j])),label='total_J_e'),
                                 _muldiv((kappa,ne,ETA,float(ph[i,j])),label='total_J_H')),label='total_J')
    total_q=-_muldiv((I_J,rate),label='net_heat')
    heavy_q=_muldiv((ne,nh,float(ev.heavy_heat_per_pair_J_m3_s[0])),label='heavy_heat')
    pressure=np.stack([_pressure_source(stf[s],float(heat[s]),'species_pressure') for s in range(3)])
    total_s=_pressure_source(total_j,total_q,'total_pressure')
    status='POSITIVE' if ne>0 and nh>0 else 'ZERO_REACTANT'
    return SpeciesSources(t,ne,nh,pe,ph,ev,rate,_readonly([rate,-rate,rate]),
        _readonly(heat),_readonly(stf),_readonly(pressure),total_q,_readonly(total_j),
        total_s,heavy_q,_readonly(response),norms,status)


@dataclass(frozen=True,slots=True)
class EventKinematics:
    input_velocities_m_s: np.ndarray
    output_velocities_m_s: np.ndarray
    COM_velocity_m_s: np.ndarray
    g0_m_s: np.ndarray
    g1_m_s: np.ndarray
    g2_m_s: np.ndarray
    relative_energy_J: float
    transfer_energy_J: float
    incoming_momentum_kg_m_s: np.ndarray
    outgoing_momentum_kg_m_s: np.ndarray
    incoming_kinetic_energy_J: float
    outgoing_kinetic_energy_J: float
    ionization_energy_J: float
    ion_mass_kg: float
    mass_scope: str
    model_identity: str = MODEL_IDENTITY
    output_order: tuple = ('scattered_electron','ejected_electron','proton')


def event_kinematics(electron_velocity_m_s,neutral_velocity_m_s,upsilon_eV,
                     direction_g1,direction_g2,*,ion_mass_kg=MP_KG):
    """Exact source-coordinate event; artificial ion mass is a labelled control.

    Unit directions are validated, never normalized by the routine. A single
    event requires E>I. This is Newtonian kinematics, not a relativistic or
    independently calibrated recoil kernel.
    """
    m=ME_KG;p=_scalar(ion_mass_kg,'ion_mass_kg',positive=True)
    h=_sum((p,m),label='neutral_mass');total=_sum((p,2*m),label='total_mass')
    eta=m/total;zeta=h/total;c=p/h;d=m/h
    if min(eta,zeta,c,d)==0: raise MomentRepresentabilityError('MASS_FRACTION_UNDERFLOW')
    mu=m*zeta;mut=m*c
    vecs=[]
    for value,name in ((electron_velocity_m_s,'electron_velocity'),(neutral_velocity_m_s,'neutral_velocity'),
                       (direction_g1,'direction_g1'),(direction_g2,'direction_g2')):
        a=_real(value,name)
        if a.shape!=(3,): raise MomentDomainError(name+': THREE_VECTOR_REQUIRED')
        if name.startswith('direction') and abs(math.hypot(*a)-1.0)>MOMENT_ROUNDOFF:
            raise MomentDomainError(name+': UNIT_VECTOR_REQUIRED_NO_RENORMALIZATION')
        vecs.append(a)
    ve,vh,n1,n2=vecs
    v=np.array([_sum((_muldiv((eta,float(ve[k])),label='COM_e'),_muldiv((zeta,float(vh[k])),label='COM_H')),label='COM') for k in range(3)])
    g=np.array([_sum((float(ve[k]),-float(vh[k])),label='relative_velocity') for k in range(3)])
    speed=math.hypot(*g)
    energy=_muldiv((0.5,mu,speed,speed),label='relative_energy')
    transfer=_muldiv((_scalar(upsilon_eV,'upsilon_eV',positive=True),EV_J),label='transfer_energy')
    if energy<=I_J or transfer<I_J or transfer>energy:
        raise MomentDomainError('EVENT_REQUIRES_E_GT_I_AND_I_LE_UPSILON_LE_E')
    speed1=math.sqrt(_muldiv((2.0,energy-transfer),(mu,),label='g1_squared'))
    speed2=math.sqrt(_muldiv((2.0,transfer-I_J),(mut,),label='g2_squared'))
    g1=speed1*n1;g2=speed2*n2
    output=np.empty((3,3))
    coeff=((zeta,0.0),(-eta,c),(-eta,-d))
    for s,(a,b) in enumerate(coeff):
        for k in range(3):
            output[s,k]=_sum((float(v[k]),_muldiv((a,float(g1[k])),label='out_g1'),
                             _muldiv((b,float(g2[k])),label='out_g2')),label='output_velocity')
    inp=np.stack((ve,vh))
    def momentum(masses,velocities):
        return _readonly([_sum(tuple(_muldiv((mass,float(vel[k])),label='momentum_term')
                                      for mass,vel in zip(masses,velocities)),label='momentum') for k in range(3)])
    def kinetic(masses,velocities):
        return _sum(tuple(_muldiv((0.5,mass,math.hypot(*vel),math.hypot(*vel)),label='kinetic_term')
                          for mass,vel in zip(masses,velocities)),label='kinetic')
    return EventKinematics(_readonly(inp),_readonly(output),_readonly(v),_readonly(g),
        _readonly(g1),_readonly(g2),energy,transfer,momentum((m,h),inp),momentum((m,m,p),output),
        kinetic((m,h),inp),kinetic((m,m,p),output),I_J,p,
        'physical_CODATA2022_proton' if p==MP_KG else 'artificial_ion_mass_kinematic_control_only')
