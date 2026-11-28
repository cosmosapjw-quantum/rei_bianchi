"""Historical key compatibility via the strict source ledger; not independent physics."""
from nonthermal_d_birth import (birth_source, HE4_REST_MEV as A, D_REST_MEV as M,
    GAMMA_MEV as E, MEV_TO_J as J, C_M_S as C, K0_MEV as K)


def source(rate=None, source_class=None, direction=None, frame='TARGET_REST'):
    if frame != 'TARGET_REST': raise ValueError('wrong frame')
    if rate is None and source_class is not None: raise ValueError('unmatched source class')
    s = birth_source(rate, source_class=source_class, photon_direction=direction)
    if rate is None: return {'physical':False,'R':None,'thermal':None,'L4':False}
    return dict(R=s['event_rate_m3_s'], S_He=s['he4_count_m3_s'],
        S_Dfast=s['fast_D_count_m3_s'],S_gamma=s['photon_count_m3_s'],
        S_fast_kin_J_m3s=s['fast_D_kinetic_J_m3_s'],
        S_rest_J_m3s=s['he4_rest_J_m3_s']+s['fast_D_rest_J_m3_s'],
        S_gamma_J_m3s=s['photon_J_m3_s'],residual_J_m3s=s['event_energy_residual_J_m3_s'],
        S_D_momentum_N_m3=s['fast_D_total_momentum_N_m3'],
        S_gamma_momentum_N_m3=s['photon_momentum_N_m3'],
        physical=False,thermal=None,L4=False)
