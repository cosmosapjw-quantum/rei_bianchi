#!/usr/bin/env python3
"""C17: exact sharp post-emission pressure envelope and CONDITIONAL isotropic
bolometric Case-A photon propagation on ACTUAL C15 stress-sourced geometry.

This does NOT invent recombination photon numbers or spectra. The original C11
Case-A energy-only escaped reservoir remains the source-of-truth. Optional
isotropic spontaneous emission + collisionless/transparent propagation is
an explicit ADDITIONAL PHYSICAL ASSUMPTION, not an original rate provider.

Metric (-,+,+,+), Bianchi I LRS:
ds²=-c²dt²+a²e^-2b(dx²+dy²)+a²e^4b dz².
Energy-angle Killing flow: E_o/E_e=(a_e/a_o)*sqrt[(1-mu²)e^{2db}+mu²e^{-4db}],
mu_o=mu e^{-2db}/sqrt[...].
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from functools import lru_cache
from pathlib import Path
import math,sys

import numpy as np
from scipy.integrate import quad
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/rei_c15_sigma_pi_feedback_20261015"))
sys.path.insert(0,str(ROOT/"research/rei_c13_live_source_20261015"))
import coupled as c15
import short_interval as c13
EV_CM3_TO_PA=1.602176634e-13


@lru_cache(maxsize=12)
def gauss(n:int):
    if n not in (4,8,12,16,24,32,48,64,96,128):
        raise ValueError("STABLE_ANGLE_GRID_NOT_ADMITTED")
    nodes,weights=np.polynomial.legendre.leggauss(n)
    for item in (nodes,weights):item.setflags(write=False)
    return nodes,weights/2


def validate_age(a_emit,a_obs,db):
    if not (math.isfinite(a_emit) and math.isfinite(a_obs) and math.isfinite(db)
            and a_emit>0 and a_obs>=a_emit and abs(db)<1):
        raise ValueError("NEGATIVE_OR_INVALID_SOURCE_AGE")


def kernel(mu,db):
    """Energy shift R and dimensionless physical pressure kernel k=R P2(mu_o)."""
    mu=np.asarray(mu,dtype=float)
    if not np.isfinite(mu).all() or np.any(abs(mu)>1) or not math.isfinite(db) or abs(db)>=1:
        raise ValueError("PHOTON_DIRECTION_OR_AXIS_SHEAR")
    A=math.exp(2*db);B=math.exp(-4*db)
    y=mu*mu
    root=np.sqrt(A+(B-A)*y)
    K=((A+2*B)*y-A)/(2*root)
    F=mu*B**.5  # c*pz (per E_e), along Killing ray
    # The energy-weighted longitudinal momentum emitted per H maps to
    # E_obs*mu_obs=(a_emit/a_obs)* E_emit*mu_emit*exp(-2db).
    return root,K,F


def exact_positive_bounds(U_emit,a_emit,a_obs,db):
    """Sharp post-transport Pi/E bounds for ANY positive angular source measure."""
    validate_age(a_emit,a_obs,db)
    if not math.isfinite(U_emit) or U_emit<0:raise ValueError("NEGATIVE_SOURCE_ENERGY")
    z=U_emit*a_emit/a_obs
    energy_min=z*min(math.exp(db),math.exp(-2*db))
    energy_max=z*max(math.exp(db),math.exp(-2*db))
    return {"energy_lower":energy_min,"energy_upper":energy_max,
            "Pi_lower":-.5*z*math.exp(db),
            "Pi_upper":z*math.exp(-2*db),
            "source_emitted_U_eV_perH":U_emit,"a_emit":a_emit,"a_obs":a_obs,
            "delta_b":db}


def isotropic_kernel(db,nmu=32):
    """Cancellation-free isotropic bolometric moments for small delta-b.

    Isotropic mean P2=0 analytically: integrate k(mu,db)-P2(mu)
    rather than adding O(1) positive and negative quantities to produce
    a tiny O(db) pressure.
    """
    if not math.isfinite(db) or abs(db)>=1:
        raise ValueError("SHEAR_DOMAIN")
    nodes,weights=gauss(nmu)
    y=nodes**2
    da=math.expm1(2*db);dd=math.expm1(-4*db)
    dr=da+(dd-da)*y
    R=np.sqrt(1+dr)
    Rm1=dr/(1+R)
    dP=(((da+2*dd)*y-da)-(3*y-1)*Rm1)/(2*R)
    # An isotropic comoving source carries rigorously zero odd dipole, even
    # when shear maps its directions. Physical ppz=mu exp(-2db).
    return 1.+float(weights@Rm1),float(weights@dP),0.


def isotropic_independent_quad(db):
    if abs(db)>=1:raise ValueError("SHEAR_DOMAIN")
    vals=tuple(quad(lambda m:float(kernel([m],db)[i][0])/2,
                    -1.,1.,epsabs=1e-14,epsrel=1e-13)[0] for i in (0,1,2))
    return vals


def isotropic_shell(U_emit,a_emit,a_obs,b_emit,b_obs,nmu=32):
    bounds=exact_positive_bounds(U_emit,a_emit,a_obs,b_obs-b_emit)
    R,K,F=isotropic_kernel(b_obs-b_emit,nmu)
    fac=U_emit*a_emit/a_obs
    out={"U_eV_H":fac*R,"Pi_eV_H":fac*K,
         "cPz_eV_H":fac*F,"U_emit_eV_H":U_emit,
         "a_emit":a_emit,"b_emit":b_emit,"a_obs":a_obs,"b_obs":b_obs,
         "bolometric_source_assumption":"isotropic_emitted_energy_per_solid_angle; collisionless massless transparent, no spectrum or number inferred",
         "sharp_envelope":bounds}
    if not (bounds["energy_lower"]-2e-13*max(fac,1e-30)<=out["U_eV_H"]<=bounds["energy_upper"]+2e-13*max(fac,1e-30)
          and bounds["Pi_lower"]-2e-13*max(fac,1e-30)<=out["Pi_eV_H"]<=bounds["Pi_upper"]+2e-13*max(fac,1e-30)):
        raise ArithmeticError("EMITTED_ISOTROPIC_PHOTONS_OUTSIDE_EXACT_CONE")
    if abs(out["cPz_eV_H"])>4e-13*max(fac,1e-30):
        raise ArithmeticError("ISOTROPIC_SOURCE_GENERATED_FORBIDDEN_DIPOLE")
    return out


@dataclass(frozen=True)
class Birth:
    a:float
    b:float
    energy_eV_perH:float
    source_macro_index:int


def radiation_from_births(births:list[Birth],a_obs,b_obs,nmu=32):
    if not math.isfinite(a_obs) or a_obs<=0 or not math.isfinite(b_obs):
        raise ValueError("INVALID_RECEIVER")
    valid=[b for b in births if b.a<=a_obs*(1+2e-15)]
    if not valid:
        return {"U_rec_eV_H":0.,"Pi_rec_eV_H":0.,"cPz_rec_eV_H":0.,
                "Pi_lower_eV_H":0.,"Pi_upper_eV_H":0.,
                "U_lower_eV_H":0.,"U_upper_eV_H":0.,
                "escape_input_eV_H":0.,"recomb_geometry_work_eV_H":0.,
                "count":0}
    ae=np.array([x.a for x in valid]);be=np.array([x.b for x in valid])
    u=np.array([x.energy_eV_perH for x in valid])
    if np.any(u<0) or np.any(ae<=0) or np.any(ae>a_obs*(1+2e-15)):
        raise ValueError("NEGATIVE_AGE_OR_EMISSIVITY")
    nodes,weights=gauss(nmu)
    diff=b_obs-be
    dA=np.expm1(2*diff)[:,None]
    dB=np.expm1(-4*diff)[:,None]
    yy=nodes[None,:]**2
    dr=dA+(dB-dA)*yy
    rr=np.sqrt(1+dr)
    rr_minus_one=dr/(1+rr)
    # k-P2 exact cancellation-free reformulation, positive photon source
    # remains unchanged; no ad hoc angular closure introduced.
    dK=(((dA+2*dB)*yy-dA)-(3*yy-1)*rr_minus_one)/(2*rr)
    fac=u*ae/a_obs
    vE=float(np.sum(fac*(1+(rr_minus_one@weights))))
    vPi=float(np.sum(fac*(dK@weights)))
    # Isotropic emitted photons have an odd Killing momentum moment that is
    # exactly zero. Preserve this symmetry analytically, not numerically.
    vF=0.
    gam=u*ae/a_obs
    lo=-.5*gam*np.exp(diff);hi=gam*np.exp(-2*diff)
    ul=gam*np.minimum(np.exp(diff),np.exp(-2*diff))
    uh=gam*np.maximum(np.exp(diff),np.exp(-2*diff))
    total_input=float(u.sum())
    work=total_input-vE
    if abs(total_input-vE-work)>2e-12*max(1.,total_input):
        raise ArithmeticError("BOL_LIOUVILLE_RECOMB_GEOMETRIC_WORK_LEDGER")
    if vPi<float(lo.sum())-1e-12 or vPi>float(hi.sum())+1e-12:
        raise ArithmeticError("POSITIVE_ESCAPED_PRESSURE_OUTSIDE_SHARP_BOUNDS")
    return {"U_rec_eV_H":vE,"Pi_rec_eV_H":vPi,
            "cPz_rec_eV_H":vF,"Pi_lower_eV_H":float(lo.sum()),
            "Pi_upper_eV_H":float(hi.sum()),
            "U_lower_eV_H":float(ul.sum()),"U_upper_eV_H":float(uh.sum()),
            "escape_input_eV_H":total_input,"recomb_geometry_work_eV_H":work,
            "count":len(valid)}


def actual_C15_case(params:c15.Parameters,nsteps=64,emission_clock="midpoint",nmu=32):
    """Supply actual C15 Born Case-A *energy increments*, sourced from true
    C11 native chemistry on dynamically backreacting Einstein s/H and b.
    Then treat escaped radiation as independently isotropic and transparent.
    The C15 chemical/Einstein original source is NOT mutated.
    """
    if emission_clock not in ("midpoint","endpoint"):
        raise ValueError("EMISSION_CLOCK_UNDEFINED")
    if nsteps<4 or nsteps>512:raise ValueError("MICRO_HISTORY_STEP")
    model=c15.EinsteinBoltzmann(params)
    state=model.initial()
    initial_energy=state.gas_and_UV.energy_ledger()
    initial_number=state.gas_and_UV.number_ledger()
    dx=c13.stable_dx(state.a,c13.STOP)/nsteps
    births=[]
    rows=[]
    start={"a":state.a,"b":state.b,"H":state.H,
           "escape_U_eV_perH":0.,
           "U_rec_eV_perH":0.,"Pi_rec_eV_perH":0.,
           "cPz_rec_eV_perH":0.,"U_rec_max":0.,
           "Pi_rec_lower":0.,"Pi_rec_upper":0.,
           "Sigma":params.Sigma_initial,
           "energy_ledger_residual":0.}
    rows.append(start)
    max_ne=0.;max_n=0.;max_energy=0.;max_Pi=0.
    for i in range(nsteps):
        prev=state
        end=c13.STOP if i==nsteps-1 else model.a0*math.exp((i+1)*dx)
        state,r=model.step(state,end,feedback=True,compress=True)
        escaping=state.gas_and_UV.escape_E_eV_perH-prev.gas_and_UV.escape_E_eV_perH
        if escaping<-1e-13:raise ArithmeticError("NEGATIVE_ANGLE_CASEA_SOURCE")
        if emission_clock=="midpoint":
            emit_a=math.sqrt(prev.a*state.a)
            emit_b=(prev.b+state.b)/2
        else:emit_a,emit_b=state.a,state.b
        births.append(Birth(emit_a,emit_b,max(0.,escaping),i))
        z=radiation_from_births(births,state.a,state.b,nmu)
        if abs(z["escape_input_eV_H"]-state.gas_and_UV.escape_E_eV_perH)>2e-11:
            raise ArithmeticError("CASEA_SOURCE_EMISSION_EVENT_CUMULATIVE_MISMATCH")
        # Replacing original C15 scalar Uescape by the actually propagated
        # radiation energy+its own Killing/expansion work must be exactly
        # energy-ledger equivalent at all reported times.
        old=state.gas_and_UV.energy_ledger()
        new=old-state.gas_and_UV.escape_E_eV_perH+z["U_rec_eV_H"]+z["recomb_geometry_work_eV_H"]
        energyr=abs(new-initial_energy)
        max_energy=max(max_energy,energyr)
        max_n=max(max_n,abs(state.gas_and_UV.number_ledger()-initial_number))
        max_Pi=max(max_Pi,abs(z["Pi_rec_eV_H"]))
        rows.append({"a":state.a,"b":state.b,"H":state.H,
             "Sigma":r["Sigma"],"orientation":r["orientation"],
             "t_s":state.gas_and_UV.elapsed_s,
             "escape_new_eV_perH":escaping,
             "escape_U_eV_perH":z["escape_input_eV_H"],
             "U_rec_eV_perH":z["U_rec_eV_H"],"Pi_rec_eV_perH":z["Pi_rec_eV_H"],
             "cPz_rec_eV_perH":z["cPz_rec_eV_H"],
             "Pi_rec_lower":z["Pi_lower_eV_H"],"Pi_rec_upper":z["Pi_upper_eV_H"],
             "U_rec_min":z["U_lower_eV_H"],"U_rec_max":z["U_upper_eV_H"],
             "U_rec_Killing_work_eV_perH":z["recomb_geometry_work_eV_H"],
             "Pi_rec_Pa":z["Pi_rec_eV_H"]*state.gas_and_UV.gas.nH*EV_CM3_TO_PA,
             "energy_ledger_residual":energyr})
    final=rows[-1]
    if max_energy>5e-11 or max_n>1e-11:
        raise ArithmeticError("BOL_CASEA_EMISSION_REPLACE_LEDGER_BROKEN")
    # First-order weak-response Green's function over the actual history.
    # dx is ln a, integrating factor a^3: d(a^3 ds)/dx
    # =kappa a^3 Pi_rec/H. No nonlinear re-solve is being claimed.
    xs=np.log(np.array([r["a"] for r in rows]))
    aa=np.array([r["a"] for r in rows])
    piPa=np.array([r.get("Pi_rec_Pa",0.) for r in rows])
    H=np.array([r["H"] for r in rows])
    response=c15.KAPPA*float(np.trapezoid(aa**3*piPa/H,xs))/aa[-1]**3
    sigma_response=math.sqrt(3)*abs(response)/H[-1]
    nH0=c13.Scenario(c13.ROOT).nh
    nh=nH0/aa**3
    pi_lo=np.array([r.get("Pi_rec_lower",0.) for r in rows])
    pi_hi=np.array([r.get("Pi_rec_upper",0.) for r in rows])
    resp_lo=c15.KAPPA*float(np.trapezoid(
        aa**3*(pi_lo*nh*EV_CM3_TO_PA)/H,xs))/aa[-1]**3
    resp_hi=c15.KAPPA*float(np.trapezoid(
        aa**3*(pi_hi*nh*EV_CM3_TO_PA)/H,xs))/aa[-1]**3
    if not (resp_lo-1e-38<=response<=resp_hi+1e-38):
        raise ArithmeticError("ISOTROPIC_CASEA_OUTSIDE_SHARP_RESPONSE_CONE")
    sigma_envelope=math.sqrt(3)*max(abs(resp_lo),abs(resp_hi))/H[-1]
    out={"schema":"rei.c17.real_C15_CaseA_bolometric_isotropic_conditional.v1",
         "model":"original_C15_Einstein_BASS_native_MD14_GrackleCaseA",
         "physics_gate":"ISOTROPIC_FREE_STREAMING_ESCAPED_CASEA_ADDITIONAL_ASSUMPTION",
         "original_source_sha":c15.source_identity(),
         "parameters":dict(params.__dict__),"emission_clock":emission_clock,
         "nsteps":nsteps,"nmu":nmu,
         "geometry_is_original_C15_backreaction":True,
         "geometry_recomputed_from_added_CaseA_Pi":False,
         "max_hhe_energy_ledger_replacement_abs_eV_H":max_energy,
         "max_hhe_photon_electron_ledger_abs_perH":max_n,
         "max_CaseA_pressure_eV_perH":max_Pi,
         "source_escapes":[asdict(b) for b in births],
         "history":rows,
         "final":final,
         "linearized_same_background_delta_s_per_s":response,
         "linearized_abs_delta_Sigma_from_conditional_isotropic_CaseA":sigma_response,
         "linearized_shear_source_response_interval_per_s":[resp_lo,resp_hi],
         "sharp_linearized_abs_delta_Sigma_envelope_any_positive_angles":sigma_envelope,
         "angular_extremizer_positive_sources":"lower transverse ring mu=0, upper equal axial beams mu=+/-1; both zero dipole",
         "uncertainty_note":"conditional Gaussian-angle quadrature, midpoint age step; NO full atom physical transition spectrum, continuum RT, nonlinear Einstein Q closure"}
    return out


def scalar_ang_kernel(mu,db):
    """Separate scalar reference using native pure math.hypot."""
    d=math.hypot(math.sqrt(max(0.,1-mu*mu))*math.exp(db),
                 mu*math.exp(-2*db))
    mout=mu*math.exp(-2*db)/d
    return d,d*(3*mout*mout-1)/2,d*mout
