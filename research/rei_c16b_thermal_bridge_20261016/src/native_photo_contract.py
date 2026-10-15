"""Source-locked, read-only photo input mapper for PR150 native IgmPhotoInput.

This is an algebraic point-state adapter, not native code execution.
It deliberately assigns no CI, RR, DR, CMB, CE, freefree, or photo event owner
outside the original Rust igm_point_rhs / PreparedAbsorption.

Original PR150 src/igm_thermal.rs defines gamma_s as [s^-1 absorber^-1]
and heat_erg_per_absorber_s as [erg/(absorber*s)], not energy/event.
Source photons q,mu and N per H must be from an admitted provider.
"""
from dataclasses import dataclass
from math import fsum,isfinite
import source_aware as src

EV_ERG=1.602176634e-12

@dataclass(frozen=True)
class NativePhotoPoint:
    gamma_s:tuple[float,float,float]
    heat_erg_per_absorber_s:tuple[float,float,float]
    neutral_per_h:tuple[float,float,float]
    photo_events_per_h_s:tuple[float,float,float]
    photo_heat_ev_per_h_s:float
    photo_binding_ev_per_h_s:float
    photon_energy_loss_ev_per_h_s:float
    mapped_fractions:tuple[float,float,float]
    n_he_over_n_h:float
    photon_event_residual:float
    binding_heat_energy_residual_ev_per_h_s:float


def photo_point(state:src.State,nh_proper_cm3:float)->NativePhotoPoint:
    if not isfinite(nh_proper_cm3) or nh_proper_cm3<=0:
        raise ValueError('positive proper nH required')
    gas=state.gas
    if abs(gas.h_total-1)>2e-13:
        raise ValueError('per-h normalisation requires H nuclei total=1')
    he=gas.he_total
    if he<=0:
        y=z=0.0
    else:
        y=gas.he_ii/he
        z=gas.he_iii/he
    fractions=(gas.h_ii,y,z)
    neutral=(gas.h_i,gas.he_i,gas.he_ii)
    gamma=[]
    heat=[]
    photo=[]
    number_loss=0.
    for i in range(3):
        weighted_sigma=[]
        weighted_heat=[]
        for p in state.photons:
            energy=src.physical_energy(p,state.a,state.b)
            sigma=src.verner_mb(i,energy)*src.MB_CM2
            weighted_sigma.append(p.n_per_h*sigma)
            weighted_heat.append(p.n_per_h*sigma*(energy-src.CHI_EV[i]))
        # sigma vanishes below the corresponding Verner threshold. Above it
        # E >= E_fit > chi_physical, so every heat term is nonnegative.
        rate=src.C_CM_S*nh_proper_cm3*fsum(weighted_sigma)
        thermal=src.C_CM_S*nh_proper_cm3*fsum(weighted_heat)
        if (not isfinite(rate) or rate<0. or not isfinite(thermal)
                or thermal < -1e-28):
            raise ArithmeticError('invalid source photo point')
        gamma.append(rate)
        heat.append(thermal*EV_ERG)
        photo.append(rate*neutral[i])
        number_loss+=rate*neutral[i]
    pheat=fsum(heat[i]/EV_ERG*neutral[i] for i in range(3))
    pbind=fsum(photo[i]*src.CHI_EV[i] for i in range(3))
    photon_energy=0.
    for p in state.photons:
        energy=src.physical_energy(p,state.a,state.b)
        sigma_tot=fsum(src.verner_mb(i,energy)*src.MB_CM2*neutral[i]
                       for i in range(3))
        photon_energy+=p.n_per_h*energy*src.C_CM_S*nh_proper_cm3*sigma_tot
    return NativePhotoPoint(tuple(gamma),tuple(heat),neutral,tuple(photo),
        pheat,pbind,photon_energy,fractions,he,
        number_loss-fsum(photo),
        photon_energy-pheat-pbind)