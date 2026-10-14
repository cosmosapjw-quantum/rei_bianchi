#!/usr/bin/env python3
"""PHYS22 local coefficients and one new physical-direction JVP check.

No trajectory, IVP, native Rust, or PHYS21 suite is run.  The SHA-pinned PHYS21
local rate/JVP functions are inherited as a dependency.  HI spectral curvature,
initial asymptotic coefficients and He electron/temperature split are new here.
All scalar computations in this contributor use ordinary binary64 arithmetic.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parent
DEPENDENCY = ROOT.parents[1] / 'inputs/inherited/PHYS21_local_gas.py'
DEPENDENCY_SHA256 = 'f97d21088e239fbad9b1a436fc4b8169fcd37ef30e97765fe249798cd40bc9ef'


def inherited_gas():
    digest = hashlib.sha256(DEPENDENCY.read_bytes()).hexdigest()
    if digest != DEPENDENCY_SHA256:
        raise ValueError('The inherited local-gas dependency has changed.')
    spec = importlib.util.spec_from_file_location('phys21_local_gas', DEPENDENCY)
    gas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gas)
    return gas


def hi_spectral(energy):
    """Smooth HI fit and D sigma, D^2 sigma, with D=E d/dE."""
    if not energy > 13.60:
        raise ValueError('The local energy must be strictly above the HI cutoff.')
    x = energy / 0.4298
    p = 2.963
    v = math.sqrt(x / 32.88)
    sigma = 5.475e4 * (x - 1.0)**2 * x**(p / 2.0 - 5.5) * (1.0 + v)**(-p) * 1e-18
    alpha = 2.0*x/(x-1.0) + p/2.0 - 5.5 - p*v/(2.0*(1.0+v))
    dalpha = -2.0*x/(x-1.0)**2 - p*v/(4.0*(1.0+v)**2)
    return sigma, sigma*alpha, sigma*(alpha**2+dalpha), alpha, dalpha


def compute():
    gas = inherited_gas()
    hmean, n_h, n_init, source = 1e-14, 1e-4, 0.05, 5e-15
    shear = (1.01e-14 - 0.99e-14)/2.0
    q = 2.0*shear**2
    energy, c_cm_s = 13.7, 29979245800.0
    x, a, b, target_t = 0.9, 0.3, 0.6, 50000.0
    pi = 1.0+gas.FHE+x+gas.FHE*(a+2.0*b)
    w = 1.5*gas.KB*target_t*pi/gas.EV
    y = [x,a,b,w]
    temperature = gas.temperature(y)
    sigma, dsigma, d2sigma, alpha, dalpha = hi_spectral(energy)
    density = c_cm_s*n_h*(1.0-x)
    lam, dlam, d2lam = [density*z for z in (sigma,dsigma,d2sigma)]
    clam = d2lam+3.0*dlam
    heat_per_event = energy-gas.CHI[0]
    heat = lam*heat_per_event
    cheat = clam*heat_per_event+2.0*dlam*energy+4.0*lam*energy
    vec = [clam,0.0,0.0,cheat]
    eta3 = [n_init*q*z/45.0 for z in vec]
    eta4_birth = [source*q*z/180.0 for z in vec]
    j_eta3, temp3 = gas.analytic_jvp(y,n_h,eta3)
    j_eta3 = [z.real for z in j_eta3]
    _, temp4_birth = gas.analytic_jvp(y,n_h,eta4_birth)
    he4 = [j_eta3[k]/4.0 for k in (1,2)]
    he5_birth = [source/(5.0*n_init)*z for z in he4]
    # At t=0 the Volterra local matrix includes initial photons.  This is only
    # the endpoint abundance derivative, not the opacity-memory contribution.
    lam_x = -c_cm_s*n_h*sigma
    a0_eta3 = j_eta3.copy()
    a0_eta3[0] += n_init*lam_x*eta3[0]
    a0_eta3[3] += n_init*lam_x*heat_per_event*eta3[0]

    rr, ci, rr_slope, _, ci_slope, dr, _ = gas.rates(temperature)
    rr = [z.real for z in rr]
    ci = [z.real for z in ci]
    dr = [z.real for z in dr]
    dr_slope = [-1.5+z/temperature for z in gas.DR_B]
    ne = n_h*(x+gas.FHE*(a+2.0*b))
    he_g = [(1.0-a-b)*ci[1]-a*rr[1]-a*sum(dr)-a*ci[2]+b*rr[2],
            a*ci[2]-b*rr[2]]
    he_gprime = [((1.0-a-b)*ci[1]*ci_slope[1]-a*rr[1]*rr_slope[1]
                 -a*sum(dr[k]*dr_slope[k] for k in range(2))
                 -a*ci[2]*ci_slope[2]+b*rr[2]*rr_slope[2])/temperature,
                (a*ci[2]*ci_slope[2]-b*rr[2]*rr_slope[2])/temperature]
    he_electron = [n_h*eta3[0]*z/4.0 for z in he_g]
    he_temperature = [ne*temp3*z/4.0 for z in he_gprime]

    baseline_nonphoto = [z.real for z in gas.rhs(y,n_h)]
    baseline_full = baseline_nonphoto.copy()
    baseline_full[0] += n_init*lam
    baseline_full[3] += n_init*heat
    electron_dot = baseline_full[0]+gas.FHE*(baseline_full[1]+2*baseline_full[2])
    temp_dot = temperature*(baseline_full[3]/w-electron_dot/pi)

    direction = [1.0,0.0,0.0,cheat/clam]
    expected, expected_temp = gas.analytic_jvp(y,n_h,direction)
    step, tol = 1e-24, 2e-12
    perturbed = [complex(y[k],step*direction[k]) for k in range(4)]
    observed = [z.imag/step for z in gas.rhs(perturbed,n_h)]
    checks = []

    def check(label, lhs, rhs):
        lhs, rhs = float(lhs), float(rhs)
        relative = abs(lhs-rhs)/max(abs(lhs),abs(rhs),1e-280)
        checks.append({'name':label,'analytic':lhs,'comparison':rhs,
                       'relative_difference':relative,'pass':relative<tol})

    for row in range(4):
        check(f'new_physical_direction_nonphoto_row_{row}',expected[row].real,observed[row])
    check('new_physical_direction_temperature',expected_temp,gas.temperature(perturbed).imag/step)
    expected_local = [z.real for z in expected]
    expected_local[0] += n_init*lam_x*direction[0]
    expected_local[3] += n_init*lam_x*heat_per_event*direction[0]
    observed_local = gas.rhs(perturbed,n_h)
    perturbed_event = n_init*c_cm_s*n_h*(1.0-perturbed[0])*sigma
    observed_local[0] += perturbed_event
    observed_local[3] += perturbed_event*heat_per_event
    for row in range(4):
        check(f'new_physical_direction_instantaneous_coupled_row_{row}',
              expected_local[row],observed_local[row].imag/step)
    for index in range(2):
        check(f'He_{index+1}_electron_plus_temperature_closed_formula',he4[index],
              he_electron[index]+he_temperature[index])

    return {
      'task':'REI_PHYS22_LOCAL_INITIAL_GAS_RESPONSE',
      'role':'contributing derivation and local computation; not final independent decision',
      'coefficient_convention':'y_epsilon=y0+epsilon^2 eta+o(epsilon^2); eta(t)=eta3*t^3+eta4*t^4+...; no factorial in eta_n',
      'arithmetic':'ordinary binary64 after parsing the source literals; algebra follows the exact-real continuum with those constants; not a native binary-equivalence certificate',
      'dependency':{'path':'inputs/inherited/PHYS21_local_gas.py','sha256':DEPENDENCY_SHA256,
                    'mode':'functions imported only; __main__ and PHYS21 60-check suite not run'},
      'input':{'H_s^-1':hmean,'n_H_cm^-3':n_h,'f_He':gas.FHE,'N_initial_photon_per_H':n_init,
               'S_photon_per_H_s':source,'E_birth_eV':energy,'chi_HI_eV':gas.CHI[0],
               'HI_opacity_cutoff_eV':13.60,'shear_s^-1':shear,'tr_Sigma2_s^-2':q,
               'y_initial':y,'T_input_K':target_t,'T_from_binary64_w_K':temperature,
               'Pi_initial':pi,'n_e_initial_cm^-3':ne},
      'local_radiation':{'sigma_HI_cm2':sigma,'Dln_sigma':alpha,'D2ln_sigma':dalpha,
                        'lambda_HI_s^-1':lam,'D_lambda_s^-1':dlam,'D2_lambda_s^-1':d2lam,
                        'C_lambda_s^-1':clam,'primary_heat_eV_s^-1':heat,
                        'C_primary_heat_eV_s^-1':cheat,'heat_excess_eV':heat_per_event,
                        'curvature_heat_to_event_ratio_eV':cheat/clam,
                        'direct_He_photo_forcing':'zero in a threshold-separated neighborhood'},
      'leading_initial_cohort':{'eta_y_t3':eta3,'eta_T_t3_K_s^-3':temp3,
          'eta_T_t3_thermal_part':temperature*eta3[3]/w,
          'eta_T_t3_particle_count_part':-temperature*eta3[0]/pi,
          'eta_HeII_t4_s^-4':he4[0],'eta_HeIII_t4_s^-4':he4[1],
          'eta_HeI_t4_s^-4':-sum(he4),'eta_photon_count_t3_per_H_s^-3':-eta3[0],
          'J_nonphoto_eta3':j_eta3,'A_local_initial_eta3':a0_eta3,
          'helium_t4_parts':{'electron_density':he_electron,'temperature':he_temperature}},
      'leading_continuous_birth_particular':{
          'definition':'r_birth only, propagated by the same full-baseline linear causal operator; not a derivative of the entire solution with respect to S',
          'eta_y_t4':eta4_birth,'eta_T_t4_K_s^-4':temp4_birth,
          'eta_HeII_t5_s^-5':he5_birth[0],'eta_HeIII_t5_s^-5':he5_birth[1],
          'relation_y_t4_to_initial_t3':'S/(4*N_initial)',
          'relation_He_t5_to_initial_He_t4':'S/(5*N_initial)'},
      'baseline_local_only':{'nonphoto_rhs':baseline_nonphoto,'full_initial_rhs':baseline_full,
                             'T_dot_initial_K_s^-1':temp_dot,'electron_count_dot_initial_s^-1':electron_dot,
                             'trajectory_computed':False},
      'helium_fixed_fraction_functions':{'G_HeII_cm3_s^-1':he_g[0],'G_HeIII_cm3_s^-1':he_g[1],
          'dG_HeII_dT_cm3_s^-1_K^-1':he_gprime[0],'dG_HeIII_dT_cm3_s^-1_K^-1':he_gprime[1],
          'alpha_RR_cm3_s^-1':rr,'beta_CI_cm3_s^-1':ci,'alpha_DR_cm3_s^-1':dr},
      'validation':{'status':'PASS' if all(z['pass'] for z in checks) else 'FAIL',
                    'new_check_count':len(checks),'passed':sum(z['pass'] for z in checks),
                    'max_relative_difference':max(z['relative_difference'] for z in checks),
                    'complex_step':step,'relative_tolerance':tol,
                    'direction':direction,'checks':checks},
      'execution_scope':{'native_runs':0,'gas_IVP_runs':0,'old_proof_replay':False,'physical':'HOLD',
                         'inherited_failures':['[160,161] FAIL','tick160','auxiliary escape FAIL'],
                         'inactive_lanes':['HH OFF','RCT OFF','CR OFF','precision atomic PARKED']},
      'limits':['Numerical values are finite binary64 checks, not rigorous enclosures.',
                'The current total H/w t^4 coefficient has additional initial-cohort drift and feedback; the birth coefficient is not that total.',
                'No finite-time eta(t), final gas temperature, native stage derivative, or physical promotion is claimed.'],
      'python':platform.python_version()
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    out=Path(args.output)
    if out.exists():
        raise FileExistsError('refusing to overwrite an execution result')
    data=compute()
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({key:data['validation'][key] for key in
                      ('status','new_check_count','passed','max_relative_difference')}))
    if data['validation']['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
