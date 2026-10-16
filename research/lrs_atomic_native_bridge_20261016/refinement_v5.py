"""Independent angular and spectral quadrature refinement of fixed bands."""
from __future__ import annotations
import json
from math import fsum
import numpy as np
from study_v5 import GAS,H0,N_STAR,T0
from lrs_threshold_oracle import Ray
from recomb_thermal import evolve_thermal
from rate_table import CaseARates

BANDS=((43.,1.,.06),(72.,2.,.08),(110.,2.,.12))


def band_rays(angular_nodes:int,spectral_nodes:int,shear:float):
    mu,mw=np.polynomial.legendre.leggauss(angular_nodes)
    en,ew=np.polynomial.legendre.leggauss(spectral_nodes)
    return tuple(Ray(center+half*float(e),float(m),
                     .005*count*float(w)*float(v)/4,shear)
                 for center,half,count in BANDS
                 for e,v in zip(en,ew)
                 for m,w in zip(mu,mw))


def run():
    provider=CaseARates()
    out={}
    for angle,energy in ((8,2),(16,2),(8,4),(16,4)):
        rr=band_rays(angle,energy,.04)
        v=evolve_thermal(rr,GAS,.05,temperature_initial_K=T0,max_step=.00125,
                         atomic_rates=provider,n_star_cm3=N_STAR,h0_s=H0)
        out[f'a{angle}_e{energy}']={
            'rays':len(rr),'T_K':v.final_temperature_K,'ne':v.final.electrons,
            'photon_final':fsum(v.photons_final),
            'energy_residual_ev':v.energy_residual_ev,
            'hydrogen_residual':v.hydrogen_residual,
            'helium_residual':v.helium_residual}
    out['angular_delta_T_K']=abs(out['a8_e4']['T_K']-out['a16_e4']['T_K'])
    out['spectral_delta_T_K']=abs(out['a16_e2']['T_K']-out['a16_e4']['T_K'])
    out['angular_delta_ne']=abs(out['a8_e4']['ne']-out['a16_e4']['ne'])
    out['spectral_delta_ne']=abs(out['a16_e2']['ne']-out['a16_e4']['ne'])
    return out


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
