"""Saved-output C8 diagnostics. No producer imports, old suite or source replay.

Input: the frozen C7 capsule. Fractions are exact for represented data only.
Scalar sensitivities do not constitute physical input uncertainty.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from fractions import Fraction as F
from pathlib import Path
import platform
import sys

CAPSULE_SHA = '11628bb0754b76468c11b8f1d7f6b4f2bce45368555f9543dd2527bc04bf79b4'
OUTPUT_SHA = '2c9601a3a0baf66ce848b831b0695c600c69973f5372d05fa7045a4c99ec2948'
LITERAL_SHA = 'b77aba9612584ffd74e2cdd951c0b9e2b573113bd7195c04d8cc857354cfe34f'
PRECISIONS = (16, 24, 40, 60, 70, 80, 100)
RHO = (F('1e-16'),F('1e-12'),F('1e-8'),F('1e-4'),F('1e-2'),F('0.5'),F('0.9'),F('0.99'))


def rat(obj):
    if isinstance(obj, dict) and set(obj) == {'num','den'}:
        return F(int(obj['num']),int(obj['den']))
    if isinstance(obj, dict):
        return {k:rat(v) for k,v in obj.items()}
    if isinstance(obj, list):
        return [rat(v) for v in obj]
    return obj


def wire(obj):
    if isinstance(obj,F):
        return {'num':str(obj.numerator),'den':str(obj.denominator)}
    if isinstance(obj,dict):
        return {k:wire(v) for k,v in obj.items()}
    if isinstance(obj,(tuple,list)):
        return [wire(v) for v in obj]
    return obj


def dec(x):
    return Decimal(x.numerator)/Decimal(x.denominator)


def display(x, digits=19):
    with localcontext() as ctx:
        ctx.prec=digits
        return str(dec(x))


def caloric(u,n,c):
    if min(u,n,c) <= 0:
        raise ValueError('positive energy, particle count and heat capacity required')
    return u/(c*n)


def relative_image(a,b,g=F(0)):
    if min(1+a,1+b,1+g) <= 0:
        raise ValueError('perturbation leaves positive caloric domain')
    return (1+a)/((1+b)*(1+g))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('capsule',type=Path);ap.add_argument('output',type=Path)
    args=ap.parse_args()
    if args.output.exists():
        raise FileExistsError('create-only C8 result already exists')
    raw=args.capsule.read_bytes()
    if len(raw)!=212516 or hashlib.sha256(raw).hexdigest()!=CAPSULE_SHA:
        raise ValueError('immutable C7 capsule byte identity mismatch')
    capsule=json.loads(raw)
    files={x['path']:x for x in capsule['files']}
    def load(name,sha):
        row=files[name];b=row['content'].encode('utf-8')
        if len(b)!=row['bytes'] or hashlib.sha256(b).hexdigest()!=sha or row['sha256']!=sha:
            raise ValueError('immutable reused C7 payload identity mismatch: '+name)
        return json.loads(b)
    original=load('attempt_01/stdout.txt',OUTPUT_SHA)
    s=rat(original); packet=load('inputs/SOURCE_BATH_LITERAL_BINDING_20261028.json',LITERAL_SHA)
    p=s['reconstructed_endpoint']; st=s['saved_endpoint']; v=s['decoded_source_values']
    E,D,c=p['U'],p['N'],p['cv']; T=p['T']; U,N,Ts=st['Ub'],st['Nb'],st['T']
    Na,Ta,dn,Q,W=p['Na'],p['Ta'],p['dN'],p['Q'],p['W']
    re,rn=st['rE'],st['rN']; defect=st['temperature_difference']
    driver=v['Tm_K_right_driver']; gap=Ts-driver
    checks=[]
    def check(name,condition):
        checks.append({'name':name,'pass':bool(condition)})
    check('saved_positive_domain',min(E,D,c,U,N,Na,Ta)>0)
    check('source_output_identity_and_stage',s['source_identity']['commit']=='634c3046ffccc5d00f1ab7588b5834a6eb8053ad')
    check('frozen_caloric_assembly',E==c*Na*Ta+Q+W and D==Na+dn)
    check('saved_scalar_identity',Ts==caloric(U,N,c) and T==caloric(E,D,c))
    check('saved_defect_identity',defect==Ts-T==(re*D-E*rn)/(c*D*(D+rn)))
    check('physical_remains_unbound',s['physical']['actual_temperature_update'] is None and s['physical']['actual_native25'] is None and s['physical']['physical_radii'] is None and not s['physical']['L4_ready'])

    numerator=re*D-E*rn
    k_num=(abs(re*D)+abs(E*rn))/abs(numerator)
    P=c*Na*Ta/E
    sensitivity={'Na':P-Na/D,'Ta':P,'cv':P-1,'deltaN':-dn/D,'Q':Q/E,'W':W/E}
    conditioning={
        'endpoint_componentwise_relative_E_N_fixed_cv':F(2),
        'endpoint_componentwise_relative_E_N_cv':F(3),
        'primitive_componentwise_log_sensitivities':sensitivity,
        'primitive_condition_linf':sum(map(abs,sensitivity.values()),F(0)),
        'endpoint_subtraction_condition':(abs(Ts)+abs(T))/abs(defect),
        'driver_gap_subtraction_condition':(abs(Ts)+abs(driver))/abs(gap),
        'retained_residual_numerator_condition':k_num,
        'absolute_dT_dE':1/(c*D), 'absolute_dT_dN':-E/(c*D*D),
        'relative_event_count_margin':D/Na,
        'count_saved_residual_relative':abs(rn)/D,
        'energy_saved_residual_relative':abs(re)/E,
    }
    check('constant_heat_capacity_sensitivity_cancellation',sensitivity['cv']==-(Q+W)/E)

    precision=[]
    for prec in PRECISIONS:
        with localcontext() as ctx:
            ctx.prec=prec;ctx.rounding=ROUND_HALF_EVEN
            e,d,cv,u,n,rer,rnr=map(dec,(E,D,c,U,N,re,rn))
            tr=e/(cv*d);ts=u/(cv*n)
            direct=ts-tr
            # Same rounded endpoints used to reconstruct residuals: no lost digits restored.
            er=u-e;nr=n-d
            from_rounded=(er*d-e*nr)/(cv*d*(d+nr))
            # A different information set: exact rational residuals retained BEFORE rounding.
            retained=(rer*d-e*rnr)/(cv*d*(d+rnr))
            gap_dec=ts-dec(driver)
            results={
                'endpoint_T_K':F(ts), 'direct_defect_K':F(direct),
                'rounded_endpoint_residual_formula_K':F(from_rounded),
                'retained_residual_formula_K':F(retained), 'driver_gap_K':F(gap_dec)
            }
        udec=F(1,10**(prec-1))
        erel=abs(results['endpoint_T_K']-Ts)/Ts
        retained_rel=abs(results['retained_residual_formula_K']-defect)/abs(defect)
        row={'precision':prec,**results,
             'endpoint_relative_error':erel,
             'direct_defect_relative_error':abs(results['direct_defect_K']-defect)/abs(defect),
             'rounded_endpoint_residual_relative_error':abs(results['rounded_endpoint_residual_formula_K']-defect)/abs(defect),
             'retained_residual_relative_error':retained_rel,
             'driver_gap_relative_error':abs(results['driver_gap_K']-gap)/abs(gap)}
        precision.append(row)
        check(f'decimal_endpoint_error_envelope_p{prec}',erel<=100*udec)
        check(f'decimal_retained_residual_error_envelope_p{prec}',retained_rel<=100*k_num*udec)
    # Measure conversion+operation effects for this platform without treating zero as exactness.
    ef,df,cf,uf,nf=map(float,(E,D,c,U,N))
    trf=ef/(cf*df);tsf=uf/(cf*nf)
    fdef=tsf-trf
    fre=(float(re)*df-ef*float(rn))/(cf*df*(df+float(rn)))
    float_record={'radix':sys.float_info.radix,'mantissa_bits':sys.float_info.mant_dig,
                  'saved_T_K':F.from_float(tsf),'saved_T_absolute_error_K':abs(F.from_float(tsf)-Ts),
                  'direct_defect_K':F.from_float(fdef),'direct_defect_relative_error':abs(F.from_float(fdef)-defect)/abs(defect),
                  'retained_defect_K':F.from_float(fre),'retained_defect_relative_error':abs(F.from_float(fre)-defect)/abs(defect),
                  'hex_saved_T':tsf.hex(),'hex_reconstructed_T':trf.hex()}
    check('binary64_endpoint_error_envelope',abs(F.from_float(tsf)-Ts)/Ts<=100*F(1,2**52))
    check('binary64_retained_residual_error_envelope',abs(F.from_float(fre)-defect)/abs(defect)<=100*k_num*F(1,2**52))

    boxes=[]
    for rho in RHO:
        lo=(1-rho)/(1+rho);hi=(1+rho)/(1-rho)
        check('fixed_cv_box_endpoints_'+str(rho),relative_image(-rho,rho)==lo and relative_image(rho,-rho)==hi)
        for sa,sb in itertools.product((-1,1),repeat=2):
            a,b=sa*rho,sb*rho;rr=relative_image(a,b)
            check(f'fixed_cv_corner_{rho}_{sa}_{sb}',lo<=rr<=hi and rr-1==(a-b)/(1+b))
        gc=rho/2
        lo3=(1-rho)/((1+rho)*(1+gc));hi3=(1+rho)/((1-rho)*(1-gc))
        for sa,sb,sc in itertools.product((-1,1),repeat=3):
            a,b,g=sa*rho,sb*rho,sc*gc
            r=relative_image(a,b,g)
            check(f'variable_cv_corner_{rho}_{sa}_{sb}_{sc}',lo3<=r<=hi3 and r-1==(a-b-g-b*g)/((1+b)*(1+g)))
        check('shared_scale_exact_'+str(rho),relative_image(rho,rho)==1 and relative_image(-rho,-rho)==1)
        boxes.append({'rho':rho,'lower_ratio':lo,'upper_ratio':hi,'maximum_relative_deviation':2*rho/(1-rho),
                      'shared_scale_deviation':F(0),'input_kind':'manufactured representation-radius experiment, not a physical radius'})
    conditioning_sweep=[]
    for k in (0,1,2,4,8,12):
        margin=F(1,10**k); n=D*margin
        current=caloric(E,n,c);deriv=E/(c*n*n)
        check('absolute_denominator_scaling_'+str(k),current==T/margin and deriv==abs(conditioning['absolute_dT_dN'])/margin**2)
        conditioning_sweep.append({'relative_denominator_margin':margin,'T_amplification':1/margin,
                                   'absolute_N_derivative_amplification':1/margin**2,
                                   'relative_N_elasticity':F(-1), 'physical_path':False})
    for n in (F(0),-D):
        try: caloric(E,n,c)
        except ValueError: rejected=True
        else: rejected=False
        check('nonpositive_denominator_rejected_'+str(n),rejected)

    differences=[]
    # Derivative direction deltaE=2E, deltaD=3D, fixed cv. Exact rational differences.
    dtrue=-T
    for k in range(4,15):
        h=F(1,2**k)
        fp=caloric(E*(1+2*h),D*(1+3*h),c)
        fm=caloric(E*(1-2*h),D*(1-3*h),c)
        cd=(fp-fm)/(2*h);error=abs(cd-dtrue)
        expected=abs(dtrue)*9*h*h/(1-9*h*h)
        check('central_difference_exact_error_'+str(k),error==expected)
        differences.append({'k':k,'h':h,'relative_derivative_error':error/abs(dtrue)})
    check('central_difference_second_order_trend',all(F(4)<a['relative_derivative_error']/b['relative_derivative_error']<F('4.2') for a,b in zip(differences,differences[1:])))

    # Decimal lexemes treated as exact vs original dyadic inputs: diagnostic alternative only.
    alt={r['name']:F(r['lexeme']) for r in packet['literal_readback'] if r['decoder']=='JSON_NUMBER_VIA_BINARY64'}
    B=s['counts']['inert_He'];B_alt=alt['NH_reference']*alt['fHe_left']
    Na_alt=s['counts']['initial_H']+B_alt;N_alt=s['counts']['final_H']+B_alt
    kB=F('1.380649e-23');Ta_alt=alt['Tm_energy_left']*alt['EV_J_source']/kB
    T_saved_alt=U/(c*N_alt);T_rec_alt=(c*Na_alt*Ta_alt+Q+W)/(c*(Na_alt+dn))
    repr_sensitivity={
        'all_bare_JSON_literals_as_exact_decimal_NOT_REPLACEMENT':{
            'inert_He_count_change_per_V0':B_alt-B,
            'saved_T_change_K':T_saved_alt-Ts,
            'reconstructed_T_change_K':T_rec_alt-T,
            'driver_change_K':alt['Tm_K_right_driver']-driver,
            'saved_driver_gap_change_K':(T_saved_alt-alt['Tm_K_right_driver'])-gap,
            'producer_energy_ports_recomputed':False,
            'scope':'consumer-only re-encoding contrast, not a new consistent provider solution'},
        'exact_SI_eV_only_NOT_REPLACEMENT':{
            'initial_T_change_K':v['Tm_energy_left']*F('1.602176634e-19')/kB-Ta,
            'saved_T_change_K':F(0),
            'scope':'U,N,cv frozen; stored SI gas energy not reconverted'},
        'native_initial_K_substitution_NOT_REPLACEMENT':{
            'reconstructed_T_change_K':(c*Na*v['Tm_K_left']+Q+W)/(c*D)-T,
            'scope':'deliberate alternative convention at initial state; r0 must be retained'}
    }
    check('decimal_reencoding_effect_enclosed',abs(T_saved_alt-Ts)<=Ts*abs(B_alt-B)/(N-abs(B_alt-B)))
    check('convention_effect_is_not_binary64_roundoff',abs(repr_sensitivity['native_initial_K_substitution_NOT_REPLACEMENT']['reconstructed_T_change_K'])>F('1e-4'))
    # Stable finite heating increment, independent of two endpoint subtractions.
    dt=(Q+W-c*Ta*dn)/(c*D)
    kdelta=(abs(Q)+abs(W)+abs(c*Ta*dn))/abs(Q+W-c*Ta*dn)
    check('finite_increment_cancellation_free_identity',dt==T-Ta)
    pass_count=sum(x['pass'] for x in checks)
    result={
        'schema':'REI_C8_CONDITIONING_RESULT_V1','unit':'finite_thermal_endpoint_20261028',
        'status':'PASS_SCOPED_C8_REPRESENTED_DATA_CONDITIONING' if pass_count==len(checks) else 'FAIL_TARGETED_C8',
        'checks':checks,'checks_total':len(checks),'checks_passed':pass_count,
        'failed':[x['name'] for x in checks if not x['pass']],
        'input_identity':{'C7_capsule_sha256':CAPSULE_SHA,'saved_stdout_sha256':OUTPUT_SHA,'literal_sha256':LITERAL_SHA},
        'conditioning_exact':conditioning,'conditioning_display':{k:display(x) for k,x in conditioning.items() if isinstance(x,F)},
        'precision_sweep':precision,'binary64':float_record,'relative_box_sweep':boxes,
        'denominator_sweep':conditioning_sweep,'central_difference_sweep':differences,
        'representation_sensitivity':repr_sensitivity,
        'exact_base':{'reconstructed_T_K':T,'saved_T_K':Ts,'saved_minus_reconstructed_K':defect,'saved_minus_driver_K':gap,
                      'finite_T_increment_K':dt,'finite_increment_numerator_condition':kdelta},
        'physical':s['physical'], 'new_physical_error_bounds':None,
        'execution':{'new_analysis_runs':1,'source_primary_replays':0,'old_fixture_replays':0,'provider_ODE_runs':0,
                     'production_module_imports':0,'author':'controller','independent_review':False,
                     'python':sys.version,'platform':platform.platform()},
        'claim':'Arithmetic representation and conditioning for the fixed saved-data model, not solver/history convergence or physical accuracy'
    }
    args.output.write_text(json.dumps(wire(result),indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'checks':[pass_count,len(checks)],'failed':result['failed'],
                      'conditioning':result['conditioning_display'],
                      'float_direct_residual_K':str(fdef),'exact_residual_K':display(defect)},indent=2))
    return 0 if pass_count==len(checks) else 1


if __name__=='__main__':
    raise SystemExit(main())
