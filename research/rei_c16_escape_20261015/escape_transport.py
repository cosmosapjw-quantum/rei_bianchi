#!/usr/bin/env python3
"""C16.0B positive Case-A escaped-photon transport and sharp fixed-background Pi envelope.

Sources:
  exact original C16 A real C13/C15 photon/Grackle CaseA step and original
  PR144 Qmu moment positive construction, copied without changing its source
  body, with runtime imports bound to the C13 PhotonCloud.
Physics:
  actual escaped-energy births at C15 chemistry midpoint (Strang split);
  propagate positive angular energy atoms by native Bianchi I Killing drift;
  calculate exact energy-integrated P2 positive angular bounds at each future a;
  integrate the bounded O(escape Pi) signed-shear Green response at *fixed*
  solved Einstein H(a), b(a), not a nonlinear fully stress-closed run.
The stellar emitter and escaping radiation EOS/physics spectra remain unassigned.
No arbitrary CaseA photon spectral energy, recoil or stellar H2 counterterm
is promoted as actual source.
"""
from __future__ import annotations
from pathlib import Path
import math,sys,hashlib
from dataclasses import dataclass
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/rei_c16_source_energy_20261015"))
from c16_exchange import (WorkAuditor,Config,Scenario,NativeStellarSource,
    START,STOP,EV_CM3_TO_PA,initial_gas,KAPPA)
from positive_source_pr144 import Moment,positive_three_atom,c13

# The moment is energy per physical H nucleus. Photon count for original
# Case-A escape has NOT been provided; using arbitrary 30 eV is a mathematical
# energy-weight quadrature adapter, NOT a physical photon-number estimate.
E_QUADRATURE_EV=30.
LARGEST_ANGULAR_NODES=64

@dataclass(frozen=True)
class EscapeBirth:
    a:float
    b:float
    energy_eV_perH:float
    t_s:float
    source_provenance:str
    def __post_init__(self):
        if not (START<=self.a<=STOP and math.isfinite(self.b) and
                self.energy_eV_perH>=0 and math.isfinite(self.t_s)):
            raise ValueError("INVALID_NATIVE_CASEA_ESCAPE_BIRTH")

class CaseABirthRecorder(WorkAuditor):
    """Actual C15 source solver with independent C16A work and event midpoint tags."""
    def __init__(self,cfg,source,order=8):
        super().__init__(cfg,source,order=order)
        self.births=[]
    def step(self,micro,y,a_end):
        start=len(self.admitted_receipts)
        before=micro.escape_E_eV_perH
        out,yend,receipt=super().step(micro,y,a_end)
        events=self.admitted_receipts[start:]
        if len(events)!=2:raise RuntimeError("C16_CASEA_MIDPOINT_SOURCE_OWNER_MISSING")
        mid=events[0]
        if abs(mid["a1"]-math.sqrt(micro.a*a_end))>4e-15:
            raise RuntimeError("ACTUAL_CASEA_BIRTH_NOT_SPLIT_MIDPOINT")
        U=out.escape_E_eV_perH-before
        if U<-1e-13:raise RuntimeError("NEGATIVE_CASEA_ESCAPE_ENERGY")
        born=EscapeBirth(
            float(mid["a1"]),float(mid["end_C15_b"]),max(0.,float(U)),
            micro.elapsed_s+float(mid["proper_dt_s"]),
            "C13 source_native CaseA recombination escape energy emitted at the actual split chemistry midpoint")
        self.births.append(born)
        return out,yend,receipt

def get_actual_source(q_signed=0.005,nstep=32,kappa=.2):
    ROOTC=Scenario(ROOT)
    source=NativeStellarSource.load(ROOTC,
           ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
    cfg=Config(legacy_q_for_locked_source=q_signed,kappa_gamma=kappa,
             kappa_nu=kappa,nstep=nstep,compression=True)
    obj=CaseABirthRecorder(cfg,source)
    result=obj.run()
    births=obj.births
    if len(births)!=nstep:raise RuntimeError("UNRECONCILED_OWNER_SOURCE_STEPS")
    if abs(sum(z.energy_eV_perH for z in births)-result["endpoint"]["escape_E_eV_perH"])>5e-14:
        raise RuntimeError("CASEA_SOURCE_EVENT_OWNERSHIP_ENERGY_NOT_CONSERVED")
    if not all(z.energy_eV_perH>=0 for z in births):
        raise RuntimeError("NOT_POSITIVE_CASEA_EXTERNAL_SOURCE")
    return result,births

def radiation_cloud(U,kind:str,order=64):
    """Positive distributions with identical energy and ZERO net axial momentum.

    transverse: Pi/U=-1/2; axial: Pi/U=1; PR144_zeroPi: Pi/U=0;
    isotropic: equal angular intensity in d(mu), Pi/U=0.
    The emission spectrum is UNSPECIFIED; E=30eV is a non-physical atom carrier.
    """
    if not(math.isfinite(U) and U>=0):
        raise ValueError("SOURCE_ESCAPED_RADIATION_NOT_POSITIVE")
    if kind in ("transverse","axial","PR144_zeroPi"):
        p2= -U/2 if kind=="transverse" else U if kind=="axial" else 0.
        obj=positive_three_atom(Moment(U,0.,p2),energy_eV=E_QUADRATURE_EV)
    elif kind=="isotropic":
        if order not in (16,32,64):
            raise ValueError("bounded verified isotropic GL quadrature")
        mu,w=leggauss(order)
        obj=c13.PhotonCloud(np.full(len(mu),E_QUADRATURE_EV),
                           mu,np.maximum(0.,U*w/(2*E_QUADRATURE_EV)))
    else:raise ValueError("UNKNOWN_CASEA_ANGULAR_MOMENT_POLICY")
    values=Moment.from_sky(obj)
    if not values.positive_cone():raise RuntimeError("SOURCE_PR144_CONE_REGRESSION_FAILED")
    if abs(values.U-U)>max(5e-14*U,1e-20) or abs(values.cPz)>max(3e-14*U,1e-20):
        raise RuntimeError("ESCAPED_SOURCE_CONE_OR_REFLECTION_FAILED")
    return obj

def evolved_moments(U,b_em,a_em,b_now,a_now,mode):
    if a_now<a_em:return Moment(0.,0.,0.)
    sky=radiation_cloud(U,mode)
    drifted=sky.drift(math.log1p((a_now-a_em)/a_em),b_now-b_em)
    return Moment.from_sky(drifted)

class FixedSourceGeometry:
    def __init__(self,source_result,initial_nH_cm3):
        h=source_result["history"]
        self.x=np.log(np.array([v["a"] for v in h],float))
        self.b=np.array([v["b"] for v in h],float)
        self.H=np.array([v["H_per_s"] for v in h],float)
        self.s=np.array([v["s_per_s"] for v in h],float)
        if (len(self.x)<9 or np.any(np.diff(self.x)<=0) or
              np.any(self.H<=0) or not np.all(np.isfinite(self.H)) or
              not np.all(np.isfinite(self.b)) or
              not(math.isfinite(initial_nH_cm3) and initial_nH_cm3>0)):
            raise ValueError("INVALID_ACTUAL_OWNER_GEOMETRY")
        self.b_interp=PchipInterpolator(self.x,self.b,extrapolate=False)
        self.logH_interp=PchipInterpolator(self.x,np.log(self.H),extrapolate=False)
        self.initial_nH_cm3=initial_nH_cm3
    def geometry(self,x):
        x=np.asarray(x)
        b=self.b_interp(x)
        H=np.exp(self.logH_interp(x))
        a=np.exp(x)
        if np.any(~np.isfinite(H)) or np.any(H<=0):
            raise RuntimeError("OWNED_EINSTEIN_GEOMETRY_INTERPOLATION_OUT_OF_BOUNDS")
        return a,b,H
    def hydrogen_density_cm3(self,a):
        return self.initial_nH_cm3*(START/a)**3

def angular_moments_fast(event:EscapeBirth,a_now,b_now,kind,order=64):
    """Vectorized native-Killing formula, separate from C13 PhotonCloud.drift."""
    if not np.all(a_now>=event.a):
        raise ValueError("ESCAPE_CANNOT_EXIST_BEFORE_ACTUAL_CASEA_BIRTH")
    obj=radiation_cloud(event.energy_eV_perH,kind,order=order)
    w=obj.NperH*obj.E
    mu2=obj.mu**2
    aa=np.asarray(a_now).reshape(-1)
    bb=np.asarray(b_now).reshape(-1)
    db=bb-event.b
    Wperp=np.exp(2*db)[:,None]
    Wpar=np.exp(-4*db)[:,None]
    RR=np.sqrt(Wperp*(1-mu2[None,:])+Wpar*mu2[None,:])
    moved_mu2=Wpar*mu2[None,:]/RR**2
    re=(event.a/aa)[:,None]*RR*w[None,:]
    U=np.sum(re,axis=1)
    Pi=np.sum(re*(3*moved_mu2-1)/2,axis=1)
    if np.any(U<-1e-19) or np.any(Pi<-U/2-5e-14*np.maximum(U,1e-30)) or np.any(Pi>U*(1+5e-14)):
        raise RuntimeError("ESCAPED_POSITIVE_PHOTON_CONE_LOST_IN_KILLING")
    return U,Pi

def sharp_per_event(event:EscapeBirth,a_now,b_now):
    """Sharp realizability envelope valid at ANY signed Δb on fixed geometry.

    At source direction z=mu_e² in [0,1], E_emit×R×P2(mu_local)
      =E_emit/2 [3 B z /sqrt(A+(B-A)z)-sqrt(A+(B-A)z)],
    A=exp(2Δb), B=exp(-4Δb).
    Its derivative ∝ A(A+5B)+(B-A)(A+2B)z, positive at z=0,1;
    affine in z hence positive for all z∈[0,1]. Extremizers actual
    transverse mu=0 and balanced axial poles mu=±1.
    """
    a=np.asarray(a_now)
    b=np.asarray(b_now)
    db=b-event.b
    factor=event.energy_eV_perH*(event.a/a)
    return -.5*factor*np.exp(db),factor*np.exp(-2*db)

def response_mode(births,geometry:FixedSourceGeometry,kind,order=16,at_x=None):
    """Actual fixed-background signed δs from a positive CaseA escape pressure.

    δs'= -3 δs + KAPPA ΔP_escaped/H; KAPPA=8πG/(3c²).
    Green kernel exp(-3(xend-x))>0, so low/high instantaneous sharp
    cones integrate to *sharp* linear-response brackets for independent
    event angular emission choices. Sign and H geometry are fixed from C16.
    """
    if order not in (8,16,32):
        raise ValueError("INTEGRATION_ORDER_UNVERIFIED")
    xf=float(geometry.x[-1] if at_x is None else at_x)
    nodes,weights=leggauss(order)
    total=0.0
    for ev in births:
        x0=math.log(ev.a)
        if x0>=xf:continue
        sample=x0+(xf-x0)*(nodes+1)/2
        a,b,H=geometry.geometry(sample)
        if kind=="envelope_low":
            _,P=None,sharp_per_event(ev,a,b)[0]
        elif kind=="envelope_high":
            _,P=None,sharp_per_event(ev,a,b)[1]
        else:
            _,P=angular_moments_fast(ev,a,b,kind)
        stress=geometry.hydrogen_density_cm3(a)*EV_CM3_TO_PA*P
        integrand=np.exp(-3*(xf-sample))*(KAPPA*stress/H)
        total+=(xf-x0)/2*float(weights@integrand)
    return total

def endpoint_source_pressure(births,geometry,kind):
    xf=geometry.x[-1]
    a,b,H=geometry.geometry([xf])
    Utotal=Ptotal=0.
    for ev in births:
        U,P=angular_moments_fast(ev,a,b,kind)
        Utotal+=float(U[0]);Ptotal+=float(P[0])
    return Utotal,Ptotal

def run_escape_response(q_signed=0.005,nstep=32,kappa=.2,order=16):
    raw,births=get_actual_source(q_signed=q_signed,nstep=nstep,kappa=kappa)
    gas0=initial_gas(Scenario(ROOT),START)
    g=FixedSourceGeometry(raw,gas0.nH)
    last=raw["endpoint"]
    sig=last["Sigma"]
    Hlast=last["H_per_s"]
    sign=int(np.sign(last["s_per_s"]))
    kinds=("transverse","PR144_zeroPi","isotropic","axial")
    preds={k:response_mode(births,g,k,order=order) for k in kinds}
    lower=response_mode(births,g,"envelope_low",order=order)
    upper=response_mode(births,g,"envelope_high",order=order)
    if not (lower<=preds["transverse"]+2e-34
            and upper>=preds["axial"]-2e-34):
        raise RuntimeError("EXTREMAL_CASEA_CONE_RESPONSE_NOT_BRACKETED")
    if abs(lower-preds["transverse"])>2e-31 or abs(upper-preds["axial"])>2e-31:
        raise RuntimeError("POSITIVE_CASEA_EXTREMA_NOT_SHARP_UNDER_KILLING")
    if not(lower<=preds["isotropic"]<=upper):
        raise RuntimeError("CASEA_ISOTROPIC_SHARP_PRESSURE_BOUNDS")
    rec={
      "schema":"rei.c16B.native_CaseA_escape_positive_transport_linear_shear_response.v1",
      "status":"ACTUAL_CASEA_RECOMBINATION_ENERGY_EMISSION_TRANSPORTED_KILLING_BIANCHI_PLUS_SHARP_PRESSURE_GREEN_BOUNDS",
      "original_real_source":"C15 actual Case-A escaped eV/H at actual chemical midpoint using C16A WorkAuditor halfstep receipt",
      "actual_C15_emission_source_sha256":raw["source_native_sha256"],
      "initial_Sigma_user":raw["Sigma_ref_user"],
      "initial_axis_orientation":raw["orientation_initial"],
      "initial_quadrupoles":{"gamma":kappa,"massless_nu":kappa},
      "nsteps":nstep,"actual_CaseA_escaped_events":len(births),
      "proper_source_end_a":last["a"],"Sigma_base_end":sig,
      "H_base_end_per_s":Hlast,"base_axis_orientation_end":sign,
      "original_actual_CaseA_emitted_U_eV_perH":last["escape_E_eV_perH"],
      "positive_escaped_sky_policy":"Actual angular/spectral escape source not supplied; conditional angular laws and mathematically sharp all-positive envelope",
      "escaped_U_and_Pi_endpoint_perH":{k:{
          "U_eV_perH":endpoint_source_pressure(births,g,k)[0],
          "pressure_difference_eV_perH":endpoint_source_pressure(births,g,k)[1]}
              for k in kinds},
      "response_shear_signed_per_s":preds,
      "source_sharp_lower_shear_signed_per_s":lower,
      "source_sharp_upper_shear_signed_per_s":upper,
      "fixed_background_signed_Normalized_Sigma_response_bounds":[
            math.sqrt(3)*lower/Hlast,math.sqrt(3)*upper/Hlast],
      "fixed_background_shear_magnitude_Sigma_first_order_bounds":[
            math.sqrt(3)*sign*lower/Hlast,math.sqrt(3)*sign*upper/Hlast],
      "fixed_background_Sigma_magnitude_valid_only_if_sign_does_not_cross":True,
      "conditional_angular_realizations_reproduce_extrema":True,
      "separately_green_source_and_escaped_radiation_energy_dilution":True,
      "fully_nonlinear_Einstein_chemistry_backreaction":"NOT_SOLVED",
      "star_emitter_mass_energy_and_escaped_recombination_physical_EOS":"NOT_ASSIGNED",
      "original_full_z20_to4_source_result":"NOT_CLAIMED",
      "scientific_admission":"SCOPED_FIXED_C16_BACKGROUND_SHARP_LINEAR_SOURCE_PRESSURE_RESPONSE_ONLY",
      "events":[vars(ev) for ev in births]
    }
    return rec,g,births
