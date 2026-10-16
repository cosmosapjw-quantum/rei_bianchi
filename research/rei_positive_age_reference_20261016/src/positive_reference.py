"""Positive source-age absorption reference, using nonnegative mild/exponential steps.

This is a CONDITIONAL, prescribed-opacity/source model in x=ln(a); it does not
implement native PR166 Grackle Newton or claim a source-matched full ODE reference.
Original method/provenance: rei_bianchi PR166 HEAD 553ce556d9f8662290c000ec675c7e6007c9d895;
actual historical cohort data remain immutable in the separately backed-up ZIP.

For an old photon stock n and total continuously born stock S in a frozen slab
with total optical depth tau = sum_k(rate_k)*dx, the exact mild update is
    n_new = n*exp(-tau) + S*phi1(-tau),
    phi1(-tau) = (1-exp(-tau))/tau.
All species photon sink shares follow frozen competing risks rate_k/rate_tot.
The physical photon energy is frozen only WITHIN THIS SCALAR CHEMICAL SUBSTEP.
"""
from dataclasses import dataclass
from math import exp, expm1, fsum, isfinite, sqrt, sinh
from typing import Callable, Sequence

FIT_EV = (13.60, 24.59, 54.42)
BIND_EV = (13.598434599702, 24.587389011, 54.41776)


def finite_nonnegative(value: float, what: str) -> float:
    if not isfinite(value) or value < 0.0:
        raise ValueError(f"{what}: expected finite nonnegative value")
    return value


def phi1_negative(tau: float) -> float:
    """Stable exact survival factor for uniform time births: phi1(-tau)."""
    finite_nonnegative(tau, "optical depth")
    if tau < 1.0e-4:
        return 1-tau/2+tau*tau/6-tau**3/24+tau**4/120-tau**5/720
    return -expm1(-tau)/tau


def birth_loss_fraction(tau: float) -> float:
    finite_nonnegative(tau,"optical depth")
    if tau < 1.0e-4:
        return tau/2-tau*tau/6+tau**3/24-tau**4/120+tau**5/720
    return 1-phi1_negative(tau)


@dataclass(frozen=True)
class Slab:
    old: float
    born: float
    survived: float
    absorbed: tuple[float, float, float]
    escaped_photon_energy_ev: float
    photoheat_ev: float
    binding_ev: float
    number_residual: float
    energy_residual_ev: float


def frozen_slab(old: float, source_total: float, rate_per_x: Sequence[float],
                width_x: float, energy_ev: float,
                fit_ev: Sequence[float] = FIT_EV,
                bind_ev: Sequence[float] = BIND_EV) -> Slab:
    """Exact photon-positive frozen reaction on one x-slab, per hydrogen nucleus.

    source_total is photons/H emitted UNIFORMLY IN x within this x-slab. It is
    not the midpoint impulse and the source is not forced to be nonnegative by
    clipping. No geometry/shear work/thermal recombinations are integrated here.
    """
    finite_nonnegative(old,"initial photon number")
    finite_nonnegative(source_total,"integrated source")
    if not isfinite(width_x) or width_x<=0:raise ValueError("positive width required")
    finite_nonnegative(energy_ev,"photon energy")
    rates=tuple(float(v) for v in rate_per_x)
    if len(rates)!=3 or len(fit_ev)!=3 or len(bind_ev)!=3:raise ValueError("three species required")
    for k,(rate,fit,bind) in enumerate(zip(rates,fit_ev,bind_ev)):
        finite_nonnegative(rate,"rate");finite_nonnegative(fit,"fit threshold");finite_nonnegative(bind,"binding energy")
        if rate>0 and energy_ev<fit:raise ValueError(f"active species {k} below fit threshold")
        if rate>0 and energy_ev<bind:raise ValueError(f"active species {k} below physical binding")
    total=fsum(rates);tau=total*width_x
    if not isfinite(tau):raise ValueError("optical depth overflow")
    old_survived=old*exp(-tau)
    birth_survived=source_total*phi1_negative(tau)
    survived=fsum((old_survived,birth_survived))
    lost_old=old*(-expm1(-tau))
    lost_new=source_total*birth_loss_fraction(tau)
    lost=fsum((lost_old,lost_new))
    absorbed=tuple((lost*rate/total if total>0 else 0.) for rate in rates)
    absorbed_sum=fsum(absorbed)
    binding=fsum(a*chi for a,chi in zip(absorbed,bind_ev))
    heat=fsum(a*(energy_ev-chi) for a,chi in zip(absorbed,bind_ev))
    return Slab(old,source_total,survived,absorbed,survived*energy_ev,
                heat,binding, old+source_total-survived-absorbed_sum,
                (old+source_total)*energy_ev-survived*energy_ev-heat-binding)


def midpoint_impulses(total_birth: float, optical_depth: float, age_panels: int) -> float:
    """Constant uniform birth, constant opacity, impulses at age-panel midpoints."""
    finite_nonnegative(total_birth,"total birth")
    finite_nonnegative(optical_depth,"total depth")
    if not isinstance(age_panels,int) or age_panels<1:raise ValueError("positive integer age panels")
    d=optical_depth/age_panels
    # Direct positive sum, not a cancellation-prone geometric denominator.
    return fsum(total_birth/age_panels*exp(-d*(k+0.5))
                for k in range(age_panels))


def midpoint_ratio_exact(optical_depth: float, age_panels: int) -> float:
    """N_mid/N_cont = z/(2 sinh(z/2)), z=optical_depth/n."""
    finite_nonnegative(optical_depth,"depth")
    if not isinstance(age_panels,int) or age_panels<1:raise ValueError("positive integer age panels")
    z=optical_depth/age_panels
    if z<1.e-3:
        return 1-z*z/24+7*z**4/5760-31*z**6/967680
    if z>1400: return 0.0
    return z/(2*sinh(z/2))


def source_time_history(x0: float, x1: float, nstep: int,
                        source_per_x: Callable[[float],float],
                        opacity_per_x: Callable[[float],Sequence[float]],
                        energy_ev: float, initial_photons: float=0,
                        split_at: Sequence[float]=()) -> dict:
    """Positive conditional source-time midpoint method with exact phi1 local maps.

    The only dynamically propagated variable is the photon number; competing
    H/He sink/heat/binding are accumulated, with no native ion fractions.
    Supplied event times are true opacity discontinuities and are inserted as
    integration boundaries before defining nstep refinements per smooth panel.
    """
    if not all(isfinite(v) for v in (x0,x1)) or x1<=x0:raise ValueError("ordered finite bounds")
    if not isinstance(nstep,int) or nstep<1:raise ValueError("positive subdivision count")
    cuts=sorted(set([float(v) for v in split_at]))
    if any((not isfinite(v) or v<=x0 or v>=x1) for v in cuts):raise ValueError("invalid event split")
    edges=[x0]+cuts+[x1]
    n=finite_nonnegative(initial_photons,"initial photons")
    counters=[0.,0.,0.]
    sums=[0.,0.,0.]
    born_total=0.
    max_resid=0.
    for a,b in zip(edges[:-1],edges[1:]):
        for k in range(nstep):
            left=a+(b-a)*k/nstep
            right=a+(b-a)*(k+1)/nstep
            middle=(left+right)/2
            j=finite_nonnegative(float(source_per_x(middle)),"source density")
            src=j*(right-left)
            trial=frozen_slab(n,src,opacity_per_x(middle),right-left,energy_ev)
            n=trial.survived
            born_total+=src
            for ksp in range(3):counters[ksp]+=trial.absorbed[ksp]
            sums[0]+=trial.photoheat_ev
            sums[1]+=trial.binding_ev
            max_resid=max(max_resid,abs(trial.number_residual),abs(trial.energy_residual_ev))
    residual=initial_photons+born_total-n-fsum(counters)
    return {'survived':n,'emitted':born_total,'absorbed':counters,
            'heat_ev':sums[0],'binding_ev':sums[1],
            'photon_ledger_residual':residual,'energy_ledger_residual_ev':
               energy_ev*(initial_photons+born_total-n)-sums[0]-sums[1],
            'max_step_residual':max_resid,'steps':nstep*len(edges[:-1])}


def positive_node_step(q_nodes:Sequence[float], number_nodes:Sequence[float],
                       opacity_nodes:Sequence[Sequence[float]], width:float,
                       geometry_scale:float, fit_ev:Sequence[float]=FIT_EV) -> dict:
    """Positive finite q-node moment reference; *not* native exponential closure.

    Each discrete q-node carries a nonnegative count. Redshift/shear scales E=q*G
    externally; this substep keeps geometry_scale constant and conserves q-support.
    """
    if len(q_nodes)!=len(number_nodes) or len(q_nodes)!=len(opacity_nodes):raise ValueError("node array mismatch")
    if not isfinite(geometry_scale) or geometry_scale<=0:raise ValueError("positive geometry scale required")
    if not isfinite(width) or width<=0:raise ValueError("positive width required")
    num=0.;eref=0.;gains=[0.,0.,0.];heat=0.;binding=0.;ab_q=0.
    for q,n,r in zip(q_nodes,number_nodes,opacity_nodes):
        finite_nonnegative(q,"q");finite_nonnegative(n,"positive node count")
        res=frozen_slab(n,0.,r,width,q*geometry_scale,fit_ev=fit_ev)
        num+=res.survived;eref+=res.survived*q
        for k in range(3):gains[k]+=res.absorbed[k]
        heat+=res.photoheat_ev;binding+=res.binding_ev
        ab_q+=q*fsum(res.absorbed)
    original_num=fsum(number_nodes)
    original_u=fsum(q*n for q,n in zip(q_nodes,number_nodes))
    return dict(number=num,reference_energy=eref,events=gains,heat_ev=heat,binding_ev=binding,
                number_residual=original_num-num-fsum(gains),
                q_energy_residual=original_u-eref-ab_q,
                physical_energy_residual=geometry_scale*(original_u-eref)-heat-binding)
