"""Prove a local mixed-response bound by ball arithmetic and tube inclusion.

No ODE time integration, nonlinear BE root solve, or native job is performed.
"""
import argparse
import hashlib
import json
import platform
import sys
import time
from decimal import Decimal, Context, ROUND_FLOOR, ROUND_CEILING
from pathlib import Path
import flint
from flint import arb, ctx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'src'))
from jet_algebra import HD, flow_jet
from frozen_source import FrozenSource


def exact_endpoint(v, rounding):
    """Export an exact dyadic endpoint plus a directed decimal enclosure."""
    if not v.is_exact() or not v.is_finite():
        raise ValueError('finite exact dyadic endpoint required')
    mantissa, exponent = (int(a) for a in v.man_exp())
    num = mantissa*(1 << exponent) if exponent >= 0 else mantissa
    den = 1 if exponent >= 0 else 1 << (-exponent)
    dec = Context(prec=42,rounding=rounding).divide(Decimal(num),Decimal(den))
    return str(dec), {'mantissa':str(mantissa),'exponent_2':exponent}


def dump_ball(v):
    if not v.is_finite():
        raise ValueError('cannot export nonfinite scientific enclosure')
    lo, lo_exact = exact_endpoint(v.lower(),ROUND_FLOOR)
    hi, hi_exact = exact_endpoint(v.upper(),ROUND_CEILING)
    return {'ball':v.str(40), 'lower':lo, 'upper':hi,
            'lower_exact_dyadic':lo_exact,'upper_exact_dyadic':hi_exact,
            'finite':True,'decimal_endpoint_rounding':'outward_42_significant_digits'}


def domain_check(model, z):
    vals = [v.c[0] for v in z]
    x, y1, y2, w = vals[:4]
    t, pi = model.thermal(vals)
    checks = {'hydrogen_fraction': bool(x > 0 and x < 1),
              'helium_simplex': bool(y1 > 0 and y2 > 0 and y1+y2 < 1),
              'positive_thermal_energy': bool(w > 0),
              'positive_photons': all(p > 0 for p in vals[4:]),
              'HH_rate_domain': bool(t > 35000 and t < 60000),
              'FT03_rate_domain': bool(t > 30000 and t < 110000),
              'particle_denominator': bool(pi > 0)}
    return {'checks':checks, 'all_pass':all(checks.values()),
            'temperature_K':dump_ball(t), 'particles_per_H':dump_ball(pi)}


def construct_tube(model, max_iterations=16):
    initial = [HD(v) for v in model.initial]
    lam = HD(arb('0.5','0.5'),1)
    source = HD(arb('0.5','0.5'),0,1)
    f0 = model.rhs(initial,lam,source)
    radii = [[(arb(2)*a.abs_upper()).abs_upper() for a in row.c] for row in f0]
    iterations = []
    for it in range(max_iterations):
        box = [HD(*(v+arb(0,r) for v,r in zip(z.c,rad)))
               for z,rad in zip(initial,radii)]
        domain = domain_check(model, box)
        if not domain['all_pass']:
            raise ValueError('DOMAIN_FAILED: '+json.dumps(domain))
        field = model.rhs(box,lam,source)
        strict, invariant, failed, ratios = [], [], [], []
        for i,(z,f,b) in enumerate(zip(initial,field,box)):
            for k in range(4):
                if not f.c[k].is_finite():
                    raise ValueError('nonfinite augmented field')
                # Symmetric image encloses Y0 + tau F(Ybox), 0 <= tau <= 1.
                magnitude = f.c[k].abs_upper()
                image = z.c[k]+arb(0,magnitude)
                if b.c[k].contains_interior(image):
                    strict.append([i,k])
                elif magnitude == 0 and radii[i][k] == 0:
                    invariant.append([i,k])
                else:
                    failed.append([i,k])
                if radii[i][k] > 0:
                    ratios.append((magnitude/radii[i][k]).abs_upper())
                if [i,k] in failed:
                    radii[i][k] = (arb('1.25')*magnitude).abs_upper()
        max_ratio = max(ratios) if ratios else arb(0)
        iterations.append({'iteration':it,'strict_components':len(strict),
                           'invariant_zero_components':len(invariant),
                           'failed_components':failed,'max_radius_ratio':dump_ball(max_ratio)})
        if not failed:
            return box, lam, source, {
                'method':'Y0 + [-1,1]*abs(F_aug(Ybox)) strictly inside Ybox, tau in [0,1]',
                'iterations':iterations,'strict_components':strict,
                'invariant_zero_components':invariant,'domain':domain,
                'box':{name:{key:dump_ball(v) for key,v in zip(['state','lambda_tangent','source_tangent','mixed_tangent'],row.c)}
                       for name,row in zip(model.names,box)}}
    raise ValueError('PICARD_TUBE_INCLUSION_NOT_CLOSED: '+json.dumps(iterations))


def run(h_s=1250000000, precision=256):
    ctx.prec=precision
    began=time.monotonic()
    input_path=ROOT/'inputs/SELECTED_SOURCE.json'
    m=FrozenSource(input_path,h_s=h_s)
    box,lam,source,tube=construct_tube(m)
    jet=flow_jet(m.rhs,box,lam,source,4)
    leading=m.leading()
    c3=leading['c3_normalized']
    r4=jet[0].a[4].c[3]
    bound=r4.abs_upper()
    relative=bound/(-c3)
    symmetric_interval=c3+arb(0,bound)
    signed_interval=c3+r4
    signs=bool(c3 < 0 and relative < 1 and symmetric_interval < 0)
    origin=flow_jet(m.rhs,[HD(v) for v in m.initial],lam,source,4)
    low_zero=[origin[0].a[k].c[3] == 0 for k in range(3)]
    # This verifies new recurrence compatibility with the inherited coefficient,
    # not a rerun of the parent scientific test suite.
    cubic_agreement=bool((origin[0].a[3].c[3]-c3).contains(0))
    result={
        'schema':'WU088_HH_PHYS02_REMAINDER_V1',
        'status':'FROZEN_MATCHED_CONTINUOUS_SIGN_ENCLOSED' if signs else 'SIGN_UNRESOLVED',
        'input_sha256':hashlib.sha256(input_path.read_bytes()).hexdigest(),
        'model_semantics':'mathematical real FT03/LCS expressions with exact binary64 leaf constants and recorded counts; not native rounding replay',
        'environment':{'python':platform.python_version(),'python_flint':flint.__version__,
                       'flint':flint.__FLINT_VERSION__,'arb_precision_bits':precision},
        'parameter_box':{'lambda':[0,1],'s_equals_S_over_Sstar':[0,1],
                         'Sstar_per_H_s':dump_ball(m.sstar)},
        'time':{'h_s':str(h_s),'tau':[0,1],'meaning':'a single frozen proper-time source stage'},
        'active_photon_original_indices':m.active,
        'inert_photon_original_indices':m.inert,
        'inert_elimination':'sigma_HI=sigma_HeI=sigma_HeII=0; exact constant coordinates retained in input',
        'leading':{k:dump_ball(v) for k,v in leading.items()},
        'fourth_derivative_divided_by_factorial_uniform':dump_ball(r4),
        'absolute_remainder_at_h':dump_ball(bound),
        'relative_remainder_upper_ball':dump_ball(relative),
        'I_over_lambda_s_at_h_enclosure':dump_ball(signed_interval),
        'symmetric_I_over_lambda_s_at_h_enclosure':dump_ball(symmetric_interval),
        'general_time_bound':'I_x/(lambda*s) is in c3*tau^3 + R4_interval*tau^4; abs(remainder)<=R4_abs*tau^4 for 0<=tau<=1',
        'signed_fourth_remainder_positive':bool(r4 > 0),
        'strict_sign_for_positive_lambda_s_t':signs,
        'axes_exact_zero':'lambda=0 or s=0 or t=0 implies I_x=0 by matched rectangle identity',
        'origin_mixed_coefficients':{str(k):dump_ball(origin[0].a[k].c[3]) for k in range(5)},
        'compatibility':{'orders_zero_to_two_exact_zero':all(low_zero),
                         'inherited_cubic_enclosed':cubic_agreement},
        'tube':tube,
        'wall_seconds':time.monotonic()-began,
        'operations':{'time_stepping':0,'IVP_trajectories':0,'BE_root_solves':0,'native_dispatch':0,
                      'NCP_dispatch':0,'legacy_integral_runs':0,'algebraic_parametric_tube_enclosures':1},
        'physical_admission':False,'production_admission':False,
        'actual_owner_macro_bound':False,'full_history_bound':False,
    }
    if not all(low_zero) or not cubic_agreement:
        raise AssertionError('new jet recurrence disagrees with inherited structural zeros/cubic')
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--h-seconds',type=int,default=1250000000)
    p.add_argument('--precision',type=int,default=256)
    a=p.parse_args()
    if a.output.exists():
        raise FileExistsError('refuse to overwrite an existing evidence result')
    result=run(a.h_seconds,a.precision)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','time','absolute_remainder_at_h','relative_remainder_upper_ball','I_over_lambda_s_at_h_enclosure','compatibility','wall_seconds']},indent=2))
    if not result['strict_sign_for_positive_lambda_s_t']:
        raise SystemExit(2)


if __name__=='__main__':
    main()
