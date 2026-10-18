"""Independent V14 output ledger, native Grackle/Verner closure unchanged.

No global photon-energy reconstruction is claimed: V14 does not output the
surviving photon energy or cumulative boundary photon number. Tests here are
native-equation algebra plus manufactured output mutations, not Rust execution.
Constants from frozen hhe_events.rs; He mass fraction from native cosmology.
"""
from __future__ import annotations
from math import fsum,isfinite

KB_ERG_K=1.380649e-16
EV_ERG=1.602176634e-12
HE_PER_H=.2454/(4*(1-.2454))
CHI=(13.598434599702,24.587389011,54.41776)
IC=(.075,.12,.03)
T0=15000.

def audit_row(row:dict, energy_atol:float=1e-9, events_atol:float=1e-9)->dict:
    """Compare independent reconstructions using the fixed V14 fixture.

    Energy residual is eV / total H nucleus; electron residual is number / H.
    These tolerances equal the existing V14 analyzer's energy/species bounds.
    They are NOT a guarantee of accuracy of the time integrator or rates.
    """
    def value(key):
        try: v=float(row[key])
        except (KeyError,TypeError,ValueError) as e:
            raise ValueError('independent missing/invalid field '+key) from e
        if not isfinite(v): raise ValueError('independent nonfinite '+key)
        return v
    ph=[value('photo_'+k) for k in ('HI','HeI','HeII')]
    ci=[value('CI_'+k) for k in ('HI','HeI','HeII')]
    rr=[value('RR_'+k) for k in ('HII','HeII','HeIII')]
    dr=value('DR_HeII')
    frac=[value(k) for k in ('HII','HeII','HeIII')]
    ne=frac[0]+HE_PER_H*(frac[1]+2*frac[2])
    ne0=IC[0]+HE_PER_H*(IC[1]+2*IC[2])
    w=1.5*KB_ERG_K/EV_ERG*value('T_K')*(1+HE_PER_H+ne)
    w0=1.5*KB_ERG_K/EV_ERG*T0*(1+HE_PER_H+ne0)
    cool=fsum(value(k) for k in (
        'RR_HII_eV_H','RR_HeII_eV_H','RR_HeIII_eV_H','DR_HeII_eV_H',
        'CE_HI_eV_H','CE_HeI_eV_H','CE_HeII_eV_H','FF_eV_H'))
    ci_bind=fsum(c*n for c,n in zip(CHI,ci))
    rr_bind=fsum(c*n for c,n in zip(CHI,rr))+CHI[1]*dr
    photo_bind=fsum(c*n for c,n in zip(CHI,ph))
    B=lambda v: CHI[0]*v[0]+HE_PER_H*(CHI[1]*v[1]+(CHI[1]+CHI[2])*v[2])
    residuals={
        'electron_eos_H':value('electrons_per_H')-ne,
        'electron_events_H':ne-ne0-fsum(ph+ci)+fsum(rr)+dr,
        'photo_binding_eV_H':value('photo_binding_eV_H')-photo_bind,
        'chemical_binding_eV_H':B(frac)-B(IC)-(photo_bind+ci_bind-rr_bind),
        'escaped_energy_eV_H':value('escape_eV_H')-(rr_bind+cool),
        'gas_thermal_eV_H':fsum((w,-w0,ci_bind,cool,
            -value('photo_heat_eV_H'),-value('CMB_eV_H'),value('thermal_work_eV_H'))),
    }
    for key,res in residuals.items():
        limit=energy_atol if 'eV' in key else events_atol
        if abs(res)>limit: raise ValueError(f'independent {key} residual {res:.17g} exceeds {limit:.3g}')
    return residuals
