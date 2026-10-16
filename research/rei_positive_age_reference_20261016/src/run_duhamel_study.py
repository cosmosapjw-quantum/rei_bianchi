"""Deterministic bounded C7/C8 study. Prints grounded JSON metrics.

The continuous Duhamel benchmark uses manufactured j, kappa and a symbolic
piecewise cumulative-depth primitive, not native PR166 time-varying Grackle.
"""
import json
import math
from pathlib import Path
from duhamel_diagnostics import (
    ManufacturedCase,independent_reference,finite_slab_history,
    midpoint_impulse_hazard_reference,adaptive_positive,
)
ROOT=Path(__file__).resolve().parents[1]

def study():
    c=ManufacturedCase()
    ref=independent_reference(c)
    levels=(4,8,16,32,64,128,256)
    rows=[]
    for n in levels:
        cut=finite_slab_history(c,n,split=True)
        baseline=finite_slab_history(c,2*n,split=False)
        impulse=midpoint_impulse_hazard_reference(c,2*n)
        rows.append({'per_smooth_panel':n,'total_slab_evaluations':2*n,
            'cut_relative_survival_error':abs(cut['survived']-ref['survived'])/ref['survived'],
            'undivided_relative_survival_error':abs(baseline['survived']-ref['survived'])/ref['survived'],
            'midpoint_birth_impulse_relative_error':abs(impulse-ref['survived'])/ref['survived'],
            'cut_species_abs_errors': [abs(a-b) for a,b in zip(cut['absorbed'],ref['absorbed'])],
            'cut_photoheat_abs_error_ev_H':abs(cut['heat_ev']-ref['heat_ev']),
            'cut_photon_residual':cut['photon_residual'],
            'cut_energy_residual_ev_H':cut['energy_residual_ev']})
    adap=[]
    for tol in [1e-4,1e-5,1e-6,1e-7,1e-8]:
        a=adaptive_positive(c,rtol=tol,max_leaf=22000)
        adap.append({'tolerance':tol,'survival_error_abs':abs(a['survived']-ref['survived']),
                     'accepted_halfsteps':a['accepted_halfsteps'],'rejected_panels':a['rejected'],
                     'photon_residual':a['photon_residual'],
                     'energy_residual_ev_H':a['energy_residual_ev']})
    n0=json.loads((ROOT/'results/native_age_summary.json').read_text())
    q={key:{'native_N_per_H':[v[str(n)]['survived_n_per_H'] for n in (8,16,32)],
         'native_last_cohort_fraction':[v[str(n)]['last_cohort_share_of_survivors'] for n in (8,16,32)],
         'native_constant_depth_fit_8to16':v['effective_constant_opacity_depth_from_first_ratio'],
         'native_constant_depth_fit_16to32':v['effective_constant_opacity_depth_from_second_ratio']}
      for key,v in n0['by_signed_s_over_H'].items()}
    assert all(row['cut_relative_survival_error'] < row['undivided_relative_survival_error'] for row in rows)
    assert all(row['cut_relative_survival_error']>0 for row in rows)
    order=[]
    for x,y,z in zip(rows[:-2],rows[1:-1],rows[2:]):
        e0=x['cut_relative_survival_error'];e1=y['cut_relative_survival_error'];e2=z['cut_relative_survival_error']
        order.append(math.log(e0/e1,2))
    return dict(scope='MANUFACTURED_j_and_kappa_POSITIVE_DUHAMEL_NO_GRACKLE_NONLINEAR_CLAIM',
                previous_base='rei_bianchi PR166 553ce556d9f8662290c000ec675c7e6007c9d895',
                theta='x in [0,1]; threshold discontinuity x=0.73; E=80 eV',
                analytic_rates='HI=95+35x,HeI=35+25x,HeII=85*1[x>=0.73] in inverse ln(a) units',
                source='j=1+0.3x photons/H/dln(a); old=0.002 photons/H',
                primitive='H(x)=130x+30x^2+85 max(0,x-0.73)',
                baseline_method='independent nested SciPy QUAD over exact primitive',
                exact_reference=ref,
                fixed_work_comparison=rows,estimated_cut_order=order,
                adaptive_comparison=adap,
                original_native_diagnostic=q,
                interpretation='positive event-aligned source-time oracle C7/C8 PASS within specified manufactured smooth/event domain; PR166 full source-matched nonlinear Grackle comparison HOLD')

if __name__=='__main__':
    d=study()
    p=ROOT/'results/duhamel_diagnostics.json'
    p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'reference':d['exact_reference']['survived'],
                      'cut_n8_relative_error':d['fixed_work_comparison'][1]['cut_relative_survival_error'],
                      'cut_n256_relative_error':d['fixed_work_comparison'][-1]['cut_relative_survival_error'],
                      'last_observed_order':d['estimated_cut_order'][-1],
                      'adaptive_finest':d['adaptive_comparison'][-1]},indent=2))
