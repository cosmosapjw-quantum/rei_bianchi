#!/usr/bin/env python3
"""Compare recorded executed histories; no predicted or global PASS."""
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
E=HERE/'evidence'
FIELDS=['xHII','xHeII','xHeIII','T_K','ne_cm3','photon_cm3','photon_erg_cm3',
        'GammaHI_s','GammaHeI_s','GammaHeII_s','escape_erg_cm3_reference',
        'work_erg_cm3_reference','source_erg_cm3_reference','absorbed_cm3_reference','source_cm3_reference']

def compare(a,b):
    results={}
    for k in FIELDS:
        av=np.array([r[k] for r in a['history']]);bv=np.array([r[k] for r in b['history']])
        scale=np.maximum(np.maximum(abs(av),abs(bv)),np.finfo(float).tiny)
        results[k]=float(np.max(abs(av-bv)/scale))
    # Quadrupole is near zero and cannot use its own vanishing normalization.
    av=np.array([r['delta_pressure_erg_cm3'] for r in a['history']])
    bv=np.array([r['delta_pressure_erg_cm3'] for r in b['history']])
    u=np.array([r['photon_erg_cm3'] for r in b['history']])
    results['delta_pressure_scaled_to_photon_energy']=float(np.max(abs(av-bv)/u))
    return results

def main():
    names=['base','tight','rk32','rk64','spectral4','angular8','flrw','source_off',
           'extended','extended_rk64','extended_refine']
    data={k:json.loads((E/(k+'.json')).read_text()) for k in names}
    temporal={a+'__'+b:compare(data[a],data[b]) for a,b in [('base','tight'),('base','rk32'),('base','rk64'),('rk32','rk64')]}
    spectral=compare(data['base'],data['spectral4'])
    angular=compare(data['spectral4'],data['angular8'])
    extended_time=compare(data['extended'],data['extended_rk64'])
    extended_joint=compare(data['extended'],data['extended_refine'])
    gates={}
    for name,d in data.items():
        hist=d['history']
        gates[name]={
            'energy_ledger_scaled_max':max(abs(r['energy_ledger_scaled']) for r in hist),
            'photon_number_ledger_scaled_max':max(abs(r['number_ledger_scaled']) for r in hist),
            'positive_photons':all(r['min_photon_cm3_reference']>0 for r in hist),
            'fractions_domain':all(0<=r['xHII']<=1 and min(r['xHeII'],r['xHeIII'])>=0 and r['xHeII']+r['xHeIII']<=1 for r in hist),
            'temperature_in_unchanged_ft03_domain':all(30000<=r['T_K']<=110000 for r in hist),
            'native_call_count':d['metadata']['native_calls']['RHS']}
    initial=data['base']['history'][0]; final=data['base']['history'][-1]
    controls={
       'source_off_changes_photon_count':final['photon_cm3']-data['source_off']['history'][-1]['photon_cm3'],
       'source_off_changes_temperature_K':final['T_K']-data['source_off']['history'][-1]['T_K'],
       'nonzero_shear_generates_pressure_anisotropy':final['delta_pressure_erg_cm3'],
       'flrw_residual_pressure_anisotropy':data['flrw']['history'][-1]['delta_pressure_erg_cm3'],
       'fraction_sum_H':1.,'fraction_sum_He':1.,
       'initial_electron_neutrality_residual_scaled':data['base']['metadata']['neutrality_scaled']}
    controls['fraction_sum_interpretation']='structural identities from eliminated HI/HeI, not independent conservation measurements'
    checks={
        'temporal_fields':max(v for d in temporal.values() for v in d.values())<2e-6,
        'extended_temporal_fields':max(extended_time.values())<2e-6,
        'energy_ledgers':max(d['energy_ledger_scaled_max'] for d in gates.values())<1e-9,
        'number_ledgers':max(d['photon_number_ledger_scaled_max'] for d in gates.values())<1e-9,
        'positivity_and_domain':all(d['positive_photons'] and d['fractions_domain'] and d['temperature_in_unchanged_ft03_domain'] for d in gates.values()),
        'actual_source_consumed':controls['source_off_changes_photon_count']>0 and controls['source_off_changes_temperature_K']!=0,
        'actual_nonzero_shear_transport':abs(controls['nonzero_shear_generates_pressure_anisotropy'])>1000*abs(controls['flrw_residual_pressure_anisotropy'])}
    result={'status':'PASS_SCOPED' if all(checks.values()) else 'FAIL','checks':checks,
            'temporal':temporal,'spectral_order2_vs4':spectral,'angular_mu4_vs8':angular,
            'extended_time_RK4_vs_DOP853':extended_time,
            'extended_joint_energy_angle_refinement':extended_joint,
            'band_sensitivity_200_vs50000':compare(data['base'],data['extended']),
            'executed_histories':gates,'controls':controls,
            'limits':['same-grid RK4 vs DOP853 share native atomic RHS and HM12 parser; not independent atomic model validation',
                      'short interval reaches roundoff in temporal differences: no measured fourth/eighth order rate',
                      'spectral/angular comparisons empirical, not uniform/continuum certificate',
                      'initial ionization equilibrium and band selected per numerical run; spectral difference includes IC quadrature',
                      'legacy F04/F08 strict local/public-width thresholds unchanged and NOT_RUN here',
                      'physical EoR/global history/closure uncertainty admission remains HOLD']}
    (E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit(1)

if __name__=='__main__': main()
