"""Source-conditional nuclear opacity and measured-support coherent pi0 return.

Uses ACROPOLIS v1.3.1 unmodified; standalone scientific extension not production.
Reference gamma->nuclei photoabsorption is 17 original ACROPOLIS channels.
For E >=204 MeV where published MacCormick 1997 is covered, replace alpha
component by inclusive measured total, rather than add it to the four channels.
Pi0 gain uses ONLY measured Rambo 1999 206..241 MeV support, and is therefore a
strictly restricted lower-coverage model, not complete pion cascade physics.
"""
from __future__ import annotations
import sys, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
PR136=ROOT/'he_dd_acropolis_pi0_20261031'/'src'
for x in (PR136,ROOT/'he_dd_exfor_measured_20261031'/'src'):
    if str(x) not in sys.path:sys.path.insert(0,str(x))
from cascade_bridge import SourceShape
from pi0_physics import (pion_lab, B_2G, interpolated_absorption, source_rows)

NUCLIDE_TARGET_BY_RID={1:2,2:3,3:3,4:4,5:4,6:5,7:5,8:5,9:5,10:6,11:6,12:7,13:7,14:7,15:8,16:8,17:8}
ALPHA_REACTIONS=(6,7,8,9)
GEOM=np.array([206.,216.,229.,241.])
HIST={e:SourceShape.from_exfor(e) for e in GEOM}
RATES={float(v['EN']):float(v['DATA']) for v in source_rows('M0752019') if 206<=float(v['EN'])<=241}
CONVERSION=2.56819e-6 # mb -> MeV^-2, identical ACROPOLIS nucl.py, not cgs


def pion_sigma_mb(E):
    """Measured domain only. Values outside [206,241] excluded rather than extrapolated."""
    if not GEOM[0]<=E<=GEOM[-1]:return 0.
    return float(np.interp(E,GEOM,[RATES[e] for e in GEOM])/1000.)


def pion_angular_spectrum(E_out,E_parent):
    """Conditional daughter dN/dE, interpolate measured angular shapes only within Rambo energy knots.

    Individual angular bins are calibrated at their measured E anchors; the conditional
    interpolation in energy is model-based and has no experimental covariance.
    """
    if not GEOM[0]<=E_parent<=GEOM[-1]:return 0.
    ix=np.searchsorted(GEOM,E_parent,side='right')-1
    if ix>=len(GEOM)-1: ix=len(GEOM)-2
    lo=float(GEOM[ix]);hi=float(GEOM[ix+1]);w=(E_parent-lo)/(hi-lo)
    def conditional(energy,shape):
        mass=0.
        for mu,weight in zip(shape.mu,shape.weights):
            p=pion_lab(energy,float(mu)); left=p['E_gamma_min_MeV'];right=p['E_gamma_max_MeV']
            if left<=E_out<=right:mass+=weight/(right-left)
        return 2*B_2G*mass
    return (1-w)*conditional(E_parent,HIST[lo])+w*conditional(E_parent,HIST[hi])


def _physical_model(Eprimary,z,NE_per_decade,do_gain=True,do_sink=True,do_source=True):
    import acropolis
    import acropolis.cascade as ac
    from acropolis.input import InputInterface,locate_sm_file
    from acropolis.nucl import NuclearReactor
    from acropolis.params import zeta3,pi2
    from acropolis.info import version
    if version!='1.3.1': raise RuntimeError('Only published pinned ACROPOLIS v1.3.1 accepted')
    source=SourceShape.from_exfor(Eprimary)
    Emax=float(max(source.highs))*(1+1e-9)
    T=2.7255*8.617333262145e-11*(1+z)
    ac.NE_pd=int(NE_per_decade)
    n=max(int(math.log10(Emax/ac.Emin)*NE_per_decade),ac.NE_min)
    Eg=np.logspace(math.log(ac.Emin),math.log(Emax),n,base=np.e)
    f,quad=source.project_source(Eg)
    ii=InputInterface(locate_sm_file())
    gen=ac.SpectrumGenerator(ii)
    reactor=NuclearReactor([lambda t:0.]*3,[lambda e,t:0.]*3,(T,T),Emax,ii)
    ni=ii.bbn_abundances_0(); nb=ii.parameter('eta')*2*zeta3/pi2*T**3
    sigma=np.array([[reactor.get_cross_section(rid,float(e)) for e in Eg] for rid in range(1,18)])
    gam=np.array([[gen._rate_x(X,float(E),T) for E in Eg] for X in range(3)])
    K=np.array([[[[gen._kernel_x_xp(X,Xp,float(E),float(Ep),T) if Ep>=E else 0. for Ep in Eg] for E in Eg] for Xp in range(3)] for X in range(3)])
    gamma_nuclear_model=nb*sum(ni[NUCLIDE_TARGET_BY_RID[rid]]*sigma[rid-1] for rid in range(1,18))
    gamma_alpha_model=nb*ni[5]*sum(sigma[rid-1] for rid in ALPHA_REACTIONS)
    # MacCormick measured total inclusive absorbs all alpha channels including coherent pi0.
    # Outside the source-covered interval, retain published Cyburt/ACROPOLIS nuclear models.
    photo_abs_inclusive=np.zeros(n); photo_pi=np.zeros(n); measured_mask=np.zeros(n,dtype=bool)
    for j,E in enumerate(Eg):
        if 204<=E<=min(241,Emax):
            photo_abs_inclusive[j]=nb*ni[5]*interpolated_absorption(float(E))['sigma_micro_b']/1000.*CONVERSION
            photo_pi[j]=nb*ni[5]*pion_sigma_mb(float(E))*CONVERSION
            measured_mask[j]=True
    nucrate=gamma_nuclear_model.copy()
    nucrate[measured_mask]+=photo_abs_inclusive[measured_mask]-gamma_alpha_model[measured_mask]
    assert min(nucrate)>=0, 'Source measured inclusive lower than sum model non-alpha channels'
    assert np.all(photo_pi<=photo_abs_inclusive+1e-50)
    if do_sink:gam[0,:]+=nucrate
    decay_kernel_count=np.zeros(n)
    decay_kernel_energy=np.zeros(n)
    decay_kernel_energy_model_error=np.zeros(n)
    if do_gain:
        for j,Ep in enumerate(Eg):
            if not (GEOM[0]<=Ep<=GEOM[-1]):continue
            shape=np.array([pion_angular_spectrum(float(E),float(Ep)) if E<Ep else 0. for E in Eg])
            weight=np.zeros(n);dy=math.log(Eg[-1]/Eg[0])/(n-1)
            weight[0]=weight[-1]=0.5;weight[1:-1]=1.
            weight*=dy*Eg
            total=float(np.dot(weight,shape))
            if total<=0:continue
            shape*=2*B_2G/total
            decay_kernel_count[j]=np.dot(weight,shape)
            decay_kernel_energy[j]=np.dot(weight*Eg,shape)
            ix=np.searchsorted(GEOM,Ep,side='right')-1
            ix=min(ix,len(GEOM)-2)
            e_lo=float(GEOM[ix]);e_hi=float(GEOM[ix+1]);t=(Ep-e_lo)/(e_hi-e_lo)
            analytic=B_2G*sum(c*np.dot(HIST[e].weights,[pion_lab(float(Ep),float(mu))['E_pi_MeV'] for mu in HIST[e].mu]) for e,c in [(e_lo,1-t),(e_hi,t)])
            decay_kernel_energy_model_error[j]=decay_kernel_energy[j]/analytic-1
            # This adds a GAIN, not an independent extra LOSS (the latter is already inside measured inclusive)
            K[0,0,:,j]+=photo_pi[j]*shape
    f0=np.zeros((3,n))
    if do_source:f0[0,:]=f
    sol=ac._JIT_solve_cascade_equation(Eg,gam,K,np.zeros(3),f0,T)
    if not np.all(np.isfinite(sol)) or np.min(sol[1:])<0:raise ArithmeticError('Negative or nonfinite nuclear feedback spectrum')
    # Published ACROPOLIS complete 17-channel nuclear reaction list. A single
    # unknown-inclusive Li6(gamma,X) channel does not specify its daughter species;
    # its event rate is measured in a separate unassigned-reservoir ledger.
    reaction_events={rid:float(np.trapezoid(sol[1,:]*nb*ni[NUCLIDE_TARGET_BY_RID[rid]]*sigma[rid-1,:],Eg)) for rid in range(1,18)}
    from acropolis.nucl import _rsig
    nuclei={i:0. for i in range(9)}
    A={0:1,1:1,2:2,3:3,4:3,5:4,6:6,7:7,8:7}
    Z={0:0,1:1,2:1,3:1,4:2,5:2,6:3,7:3,8:4}
    for rid,(input_index,outgoing) in _rsig.items():
        if rid==11:continue
        ev=reaction_events[rid]
        nuclei[input_index]-=ev
        for i,mult in outgoing.items():nuclei[i]+=ev*mult
        assert sum(m*A[i] for i,m in outgoing.items())==A[input_index],f'nonconserving reaction {rid} baryon'
        assert sum(m*Z[i] for i,m in outgoing.items())==Z[input_index],f'nonconserving reaction {rid} charge'
    D_net=nuclei[2]
    d_birth=sum(reaction_events[rid]*({2:1,4:1,8:2,9:1}.get(rid,0)) for rid in range(1,18))
    d_destroy=reaction_events[1]
    assert abs(d_birth-d_destroy-D_net)<1e-10*max(1,abs(D_net))
    B_residual=sum(nuclei[i]*A[i] for i in range(9))
    Z_residual=sum(nuclei[i]*Z[i] for i in range(9))
    assert abs(B_residual)<1e-9 and abs(Z_residual)<1e-9
    # Add nuclear-absorption observables only. No thermal energy-deposition claim.
    absorption_events=np.trapezoid(sol[1,:]*nucrate,Eg)
    pi_regen_events=np.trapezoid(sol[1,:]*photo_pi,Eg)
    measured_photo_events=np.trapezoid(sol[1,:]*photo_abs_inclusive,Eg)
    out=dict(E_primary_MeV=Eprimary,z=z,NE_per_decade=NE_per_decade,grid_count=n,
       D_born_per_initial_pi0=float(d_birth),D_destroy_per_initial_pi0=float(d_destroy),
       D_net_per_initial_pi0=float(D_net),
       unassigned_inclusive_Li6_gamma_X_events=float(reaction_events[11]),
       known_channels_baryon_residual=float(B_residual),known_channels_charge_residual=float(Z_residual),
       channel_events={str(i):v for i,v in reaction_events.items()},
       isotope_delta_0to8={str(i):v for i,v in nuclei.items()},
       alpha_total_absorption_events_model=float(absorption_events),
       measured_alpha_absorption_events=float(measured_photo_events),
       pion_regen_events_measured_support=float(pi_regen_events),
       pion_regen_photon_count_measured_support=float(2*B_2G*pi_regen_events),
       pion_regen_photon_count_actually_injected=float(2*B_2G*pi_regen_events if do_gain else 0.),
       max_pi_kernel_count_norm_abs_err=float(np.max(np.abs(decay_kernel_count[decay_kernel_count>0]-2*B_2G))) if np.any(decay_kernel_count>0) else 0.,
       max_pi_kernel_energy_excess_MeV=float(max([decay_kernel_energy[j]-2*B_2G*float(E) for j,E in enumerate(Eg) if decay_kernel_count[j]>0],default=0.)),
       max_pi_kernel_energy_model_relative_error=float(max(np.abs(decay_kernel_energy_model_error))),
       n_measured_inclusive_grid_points=int(np.count_nonzero(measured_mask)),
       n_measured_pion_grid_points=int(np.count_nonzero(photo_pi>0)),
       source_gamma_count_expected=float(source.exact_moments()['N']),
       source_gamma_energy_MeV=float(source.exact_moments()['energy']),
       source_grid_count=float(np.dot(quad,f)),
       source_grid_energy_MeV=float(np.dot(quad,f*Eg)),
       max_photon_spectrum=float(np.max(sol[1,:])),
       max_electron_spectrum=float(np.max(sol[2,:])),
       max_positron_spectrum=float(np.max(sol[3,:])),
       scenario='EM_PLUS_STANDARD_NUCLEAR_AND_MACCORMICK_MEASURED_INCLUSIVE_WITH_PI_GAIN' if do_sink and do_gain else ('EM_PLUS_STANDARD_NUCLEAR_AND_MEASURED_INCLUSIVE_LOSS_ONLY' if do_sink else 'PR136_EM_ONLY'),
       source_outside_pi_measured_E_domain='NO_PION_GAIN',
       pion_angular_interpolation='MODEL_CONDITIONAL_ONLY',
       no_BASS_gamma_emissivity=True,no_final_heat_rate=True)
    return out,sol,nucrate,photo_pi,Eg


def compute_three_scenarios(Eprimary,z,NE_per_decade):
    """Compute only one costly EM matrix per source, to be reused for three physics scenarios."""
    return _physical_model(Eprimary,z,NE_per_decade,do_gain=True,do_sink=True)
