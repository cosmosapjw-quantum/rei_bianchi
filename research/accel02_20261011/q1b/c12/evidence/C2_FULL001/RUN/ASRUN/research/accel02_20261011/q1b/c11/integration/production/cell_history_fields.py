"""Full24 cgs fields from the actual endpoint native-cell measure.

No evolved spectrum reconstruction, time interpolation, native call, or threshold
shift occurs here. Source rates are instantaneous StableCellSource values, not
finite-interval source counters divided by a step. Reference density is per
initial physical cm^3; proper density divides by a_rel^3.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_step_v3 import EV_ERG, CHI, gas_temperature

TIME_FIELDS=['xHII','xHeII','xHeIII','T_K','ne_cm3','photon_cm3','GammaHI_s','GammaHeI_s','GammaHeII_s']
SPECTRAL_FIELDS=['source_number_ref_cm3_s','source_energy_ref_erg_cm3_s','source_number_proper_cm3_s','source_energy_proper_erg_cm3_s','cumulative_source_number_ref_cm3','cumulative_source_energy_ref_erg_cm3','radiation_energy_ref_erg_cm3','radiation_energy_proper_erg_cm3','photoheat_HI_per_absorber_erg_s','photoheat_HeI_per_absorber_erg_s','photoheat_HeII_per_absorber_erg_s','photoheat_HI_proper_erg_cm3_s','photoheat_HeI_proper_erg_cm3_s','photoheat_HeII_proper_erg_cm3_s','total_photoheat_proper_erg_cm3_s']
FIELDS24=TIME_FIELDS+SPECTRAL_FIELDS
UNITS=dict(zip(TIME_FIELDS,['1','1','1','K','cm^-3 (proper)','cm^-3 (proper)','s^-1','s^-1','s^-1']))
UNITS.update(dict(zip(SPECTRAL_FIELDS,['cm^-3 s^-1 (reference)','erg cm^-3 s^-1 (reference)','cm^-3 s^-1 (proper)','erg cm^-3 s^-1 (proper)','cm^-3 (reference)','erg cm^-3 (reference)','erg cm^-3 (reference)','erg cm^-3 (proper)','erg s^-1 absorber^-1','erg s^-1 absorber^-1','erg s^-1 absorber^-1','erg cm^-3 s^-1 (proper)','erg cm^-3 s^-1 (proper)','erg cm^-3 s^-1 (proper)','erg cm^-3 s^-1 (proper)'])))


def physical_state_sha256(state):
    """Content identity for physical arrays/scalars, excluding all diagnostics."""
    h=hashlib.sha256()
    scalars={key:state[key] for key in ('t_s','nH_ref','nHe_ref','counters')}
    h.update(json.dumps(scalars,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
    for key in ('gas','N','U_eV','R','support'):
        value=np.asarray(state[key],dtype='<f8',order='C')
        h.update(key.encode()+b'\0'+json.dumps(value.shape).encode()+b'\0'+value.tobytes())
    return h.hexdigest()


def _kernel(state):
    kernel=state.get('diagnostics',{}).get('output24_kernel')
    if kernel is None:raise ValueError('OUTPUT24_MISSING_SAME_MAP_KERNEL')
    if kernel['state_sha256']!=physical_state_sha256(state):raise ValueError('OUTPUT24_STATE_KERNEL_IDENTITY')
    if kernel['time_s']!=state['t_s']:raise ValueError('OUTPUT24_KERNEL_CLOCK')
    return kernel


def build_fields24(state,source,*,source_api):
    kernel=_kernel(state);g=source.provider.geometry(float(state['t_s']));volume=g['a_rel']**3
    if not math.isfinite(volume) or volume<=0:raise ValueError('OUTPUT24_VOLUME')
    instantaneous=source_api.StableCellSource(source).source(float(state['t_s']))
    sn=math.fsum(np.asarray(instantaneous['N']).ravel())
    se=EV_ERG*math.fsum(np.asarray(instantaneous['U_eV']).ravel())
    radiation=EV_ERG*math.fsum(np.asarray(state['U_eV']).ravel())
    h,he1,he2,w=np.asarray(state['gas'],float)
    gamma=np.asarray(kernel['gamma_s'],float)
    heat=np.asarray(kernel['photoheat_per_absorber_erg_s'],float)
    lower=np.array([g['nH']*(1-h),g['nHe']*(1-he1-he2),g['nHe']*he1])
    proper=lower*heat
    values=[h,he1,he2,gas_temperature(state['gas'],g),g['nH']*h+g['nHe']*(he1+2*he2),math.fsum(np.asarray(state['N']).ravel())/volume,*gamma,
        sn,se,sn/volume,se/volume,state['counters']['Nsource'],EV_ERG*state['counters']['Esource_eV'],radiation,radiation/volume,*heat,*proper,math.fsum(proper)]
    if len(values)!=24 or not np.isfinite(values).all():raise ValueError('OUTPUT24_FIELDS_FINITE')
    return {name:float(value) for name,value in zip(FIELDS24,values)}


def geometry_diagnostics(source,t):
    p=source.provider
    if p.r!=0.:raise ValueError('OUTPUT24_CURRENT_BINDING_FLRW_ONLY')
    g=p.geometry(float(t));_,mu,R=p.ray(np.ones(len(source.mu)),source.mu,float(t))
    weights=np.asarray(source.weights,float)
    if weights.shape!=np.asarray(R).shape:raise ValueError('OUTPUT24_ANGULAR_WEIGHT_SHAPE')
    radial=float(np.max(abs(np.asarray(R)*g['a_rel']-1.)))
    direction=float(np.max(abs(np.asarray(mu)-source.mu)))
    volume=abs(math.fsum(weights/np.asarray(R)**3)/g['a_rel']**3-1.)
    return dict(ray_scale_error=radial,direction_error=direction,angular_volume_error=volume,max_error=max(radial,direction,volume),budget=1e-11)


def build_record(state,source,*,source_api,epoch_index,generation,state_sha256,ledger):
    kernel=_kernel(state);identity=physical_state_sha256(state)
    if state_sha256!=identity:raise ValueError('OUTPUT24_CALLER_STATE_IDENTITY')
    if not isinstance(epoch_index,int) or epoch_index<0:raise ValueError('OUTPUT24_EPOCH_INDEX')
    geometry=geometry_diagnostics(source,state['t_s'])
    if geometry['max_error']>geometry['budget']:raise ArithmeticError('OUTPUT24_GEOMETRY_GATE')
    return dict(schema='rei.q1b.c12.output24.record.v1',epoch_index=epoch_index,time_s=float(state['t_s']),z=float(source.provider.geometry(state['t_s'])['z']),accepted_generation=generation,state_sha256=identity,fields=build_fields24(state,source,source_api=source_api),units=UNITS.copy(),geometry=geometry,original_ic_ledger=dict(ledger),kernel_owner=kernel['owner'],kernel=kernel,source_owner='StableCellSource.source(t): instantaneous same pinned formula',scientific_admission=False)
