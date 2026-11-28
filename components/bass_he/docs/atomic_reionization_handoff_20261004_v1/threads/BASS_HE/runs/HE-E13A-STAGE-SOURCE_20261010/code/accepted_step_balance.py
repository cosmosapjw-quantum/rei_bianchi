"""Source-pinned accepted-step material ledger check, not a stage RHS certificate.

All stored CSV numbers are finite binary64. Fraction.from_float reconstructs the
exact representable input, then independent stoichiometric conservation equations
are evaluated without using Rust's coupled::assemble_residual or material::rhs.
This consumes the SAME original event/energy owners: it is not an independent
photo cross-section, EOS, collision integral, or transport oracle.
"""
from __future__ import annotations
import csv
import json
import math
from fractions import Fraction as F
from pathlib import Path
from typing import Sequence

class BalanceError(ValueError):
    pass

SOURCE_Y_HE = 0.24
SOURCE_CHI_EV = (13.598434599702, 24.587389011, 54.41776)
SOURCE_EV_ERG = 1.602176634e-12
SOURCE_TOL = (1e-14, 1e-14, 1e-14, 1e-26)
N_STEPS = 384
MODE_NAMES = ('OFF', 'KF', 'GM')
SOURCE_COLS = (
    'ln_a', 'x_hii','x_heii','x_heiii','w','ne_per_h',
    'ci_HI','ci_HeI','ci_HeII','rr_HII','rr_HeII','rr_HeIII',
    'dr_HeII','abs_HI','abs_HeI','abs_HeII',
)
INTERNAL_COLS = ('step','s','BH','BY','BZ','bindMicro','thermalMicro')
RCT_COLS = ('step','s','x','y','z','w','RCT','RCT_heat','RCT_chem','RCT_escape')
STEPS_COLS = ('step','norm','Nratio','Eratio')

def exact_f64(raw: str) -> F:
    try:
        x=float(raw)
    except (TypeError, ValueError, OverflowError) as exc:
        raise BalanceError('INVALID_BINARY64_INPUT') from exc
    if not math.isfinite(x):
        raise BalanceError('NONFINITE_BINARY64_INPUT')
    return F.from_float(x)

def _f(row:dict, key:str)->F:
    try: return exact_f64(row[key])
    except KeyError as exc: raise BalanceError('MISSING_COLUMN_'+key) from exc

def _check_columns(rows:list[dict], keys:Sequence[str], label:str):
    if len(rows)!=N_STEPS+1: raise BalanceError(label+'_WRONG_ROW_COUNT')
    for i,row in enumerate(rows):
        for k in keys:
            if k not in row: raise BalanceError(label+'_MISSING_'+k)
        if label!='native' and int(row['step'])!=i: raise BalanceError(label+'_STEP_SEQUENCE')

def source_fhe(y_mass:float=SOURCE_Y_HE)->F:
    if not (0<=y_mass<1) or not math.isfinite(y_mass):raise BalanceError('INVALID_Y_HE')
    yy=F.from_float(y_mass)
    return yy/(4*(1-yy))

def preflight(native:list[dict], internal:list[dict], rct:list[dict], trace:list[dict], *,helium_mass_fraction:float=SOURCE_Y_HE):
    _check_columns(native,SOURCE_COLS,'native')
    _check_columns(internal,INTERNAL_COLS,'internal')
    _check_columns(rct,RCT_COLS,'rct')
    _check_columns(trace,STEPS_COLS,'steps')
    fhe=source_fhe(helium_mass_fraction)
    if fhe<=0: raise BalanceError('NONPOSITIVE_HELIUM_RATIO')
    previous=None
    for i in range(N_STEPS+1):
        n,di,re=native[i],internal[i],rct[i]
        s=_f(n,'ln_a')
        if s!=_f(di,'s') or s!=_f(re,'s'): raise BalanceError('CLOCK_MISMATCH')
        if previous is not None and s<=previous: raise BalanceError('CLOCK_NOT_STRICTLY_MONOTONE')
        previous=s
        for a,b in [('x_hii','x'),('x_heii','y'),('x_heiii','z'),('w','w')]:
            if _f(n,a)!=_f(re,b):raise BalanceError('STATE_SIDECAR_MISMATCH_'+a)
        x,y,z=[_f(n,q) for q in ('x_hii','x_heii','x_heiii')]
        if not(0<=x<=1 and 0<=y and 0<=z and y+z<=1):
            raise BalanceError('GAS_FRACTIONS_OUT_OF_DOMAIN')
        ne=_f(n,'ne_per_h')
        if abs(ne-(x+fhe*(y+2*z))) > F.from_float(5e-15):
            raise BalanceError('HELIUM_ABUNDANCE_OR_ELECTRON_SOURCE_MISMATCH')
    for r in (internal[0],rct[0]):
        if any(_f(r,k)!=0 for k in (('BH','BY','BZ','bindMicro','thermalMicro') if r is internal[0] else ('RCT','RCT_heat','RCT_chem','RCT_escape'))):
            raise BalanceError('NONZERO_INITIAL_CUMULATIVE_LEDGER')
    return fhe

def calculate_components(native,internal,rct,k, *,helium_mass_fraction=SOURCE_Y_HE,
                         thresholds=SOURCE_CHI_EV,include_thermal=True,rct_multiplier=1):
    if not 1<=k<=N_STEPS: raise BalanceError('STEP_OUT_OF_BOUNDS')
    fhe=source_fhe(helium_mass_fraction)
    if len(thresholds)!=3:raise BalanceError('THRESHOLD_COUNT')
    if any(not(math.isfinite(c) and c>0) for c in thresholds):raise BalanceError('THRESHOLD_DOMAIN')
    if not isinstance(rct_multiplier,int):raise BalanceError('RCT_MULTIPLIER_NOT_INTEGER')
    b,a=native[k-1],native[k]
    bb,aa=internal[k-1],internal[k]
    rb,ra=rct[k-1],rct[k]
    dn=lambda c:_f(a,c)-_f(b,c)
    di=lambda c:_f(aa,c)-_f(bb,c)
    dr=lambda c:_f(ra,c)-_f(rb,c)
    ci=[dn('ci_'+name) for name in ('HI','HeI','HeII')]
    rr=[dn('rr_'+name) for name in ('HII','HeII','HeIII')]
    absorbed=[dn('abs_'+name) for name in ('HI','HeI','HeII')]
    drHeII=dn('dr_HeII')
    rct_d=dr('RCT')*rct_multiplier
    # Derive independently from H, HeI, HeII, HeIII population balances.
    material_h=ci[0]-rr[0]+rct_d
    material_heii=(ci[1]-rr[1]-drHeII)-(ci[2]-rr[2])+rct_d
    material_heiii=ci[2]-rr[2]-rct_d
    photo_h=absorbed[0]
    photo_heii=(absorbed[1]-absorbed[2])
    photo_heiii=absorbed[2]
    ev=F.from_float(SOURCE_EV_ERG)
    threshold=[F.from_float(z) for z in thresholds]
    photoheat=sum(di(c) for c in ('BH','BY','BZ'))-ev*sum(threshold[i]*absorbed[i] for i in range(3))
    nonphoto=di('thermalMicro') if include_thermal else F(0)
    return {
        'residual':[
            dn('x_hii')-material_h-photo_h,
            dn('x_heii')-(material_heii+photo_heii)/fhe,
            dn('x_heiii')-(material_heiii+photo_heiii)/fhe,
            dn('w')-photoheat-nonphoto,
        ],
        'material_species':[material_h,material_heii,material_heiii],
        'photo_species':[photo_h,photo_heii,photo_heiii],
        'RCT_count':rct_d,
        'material_thermal_integral':nonphoto,
        'photo_thermal_integral':photoheat,
    }

def reconstruct_step(native,internal,rct,trace,k,**opts):
    if not(1<=k<=N_STEPS):raise BalanceError('STEP_OUT_OF_BOUNDS')
    if 'helium_mass_fraction' in opts:
        custom=opts['helium_mass_fraction']
        if custom!=SOURCE_Y_HE:preflight(native,internal,rct,trace,helium_mass_fraction=custom)
    rs=calculate_components(native,internal,rct,k,**opts)['residual']
    return [abs(v)/F.from_float(t) for v,t in zip(rs,SOURCE_TOL)]

def _load(f:Path):
    if not f.is_file():raise BalanceError('MISSING_INPUT_'+str(f))
    with f.open(newline='') as fh:return list(csv.DictReader(fh))

def analyze(path:Path):
    path=Path(path)
    result={
        'schema':'bass-he.e13.accepted-step-audit.v1',
        'input_unit':'exact binary64 from stored .17e strings',
        'accepted_steps':0,
        'failures':[],
        'per_mode':{},
        'stage_independent_evaluator_executed':False,
        'true_error_enclosure':False,
        'protected_status':{'baseline_RCT':'OFF','physical':'HOLD','HE_F2_F09_global':'OPEN','actual_atomic_moments':None,'endpoint_Gamma_equivalence':'FAIL_3.543295_RETAINED'},
        'claim_ceiling':'Native-event-observable accepted-step balance; no independent microphysical RHS or phase-space transport proof',
    }
    for mode in MODE_NAMES:
        folder=path/mode
        n=_load(folder/'OWNER_NATIVE_41.csv')
        i=_load(folder/'OWNER_INTERNAL_5.csv')
        r=_load(folder/'OWNER_SELECTED_RCT.csv')
        s=_load(folder/'STEPS.csv')
        preflight(n,i,r,s)
        extrema=[{'ratio':-1.0,'step':None,'exact_residual':None,'exact_normalized_ratio':None} for _ in range(4)]
        diff_max={'value':0.,'step':None}
        for step in range(1,N_STEPS+1):
            p=calculate_components(n,i,r,step)
            ratios=[abs(x)/F.from_float(tol) for x,tol in zip(p['residual'],SOURCE_TOL)]
            for j,val in enumerate(ratios):
                fval=float(val)
                if fval>1:result['failures'].append({'mode':mode,'step':step,'component':j,'scaled':fval})
                if fval>extrema[j]['ratio']:
                    extrema[j]={'ratio':fval,'step':step,'exact_residual':f'{p["residual"][j].numerator}/{p["residual"][j].denominator}', 'exact_normalized_ratio':f'{val.numerator}/{val.denominator}'}
            norm=max(map(float,ratios))
            native_norm=float(s[step]['norm'])
            d=abs(native_norm-norm)
            if d>diff_max['value']:diff_max={'value':d,'step':step}
        result['per_mode'][mode]={
            'tested_scalar_residuals':4*N_STEPS,
            'maxima':extrema,
            'max_ratio':max(x['ratio'] for x in extrema),
            'native_max_norm':max(float(x['norm']) for x in s),
            'max_scaled_norm_difference_vs_native':diff_max,
            'accepted_stage_summary_not_independent_proof':True,
        }
        result['accepted_steps']+=N_STEPS
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('parent_full_dir',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise SystemExit('CREATE_ONLY_OUTPUT_EXISTS')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(analyze(args.parent_full_dir),sort_keys=True,indent=2)+'\n'
    with args.output.open('x') as f:f.write(content)
    print('E13_ACCEPTED_STEP_BALANCE',args.output)
