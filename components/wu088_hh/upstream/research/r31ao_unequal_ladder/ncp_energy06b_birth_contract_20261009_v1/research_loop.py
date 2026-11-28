"""Independent 110-digit checks and deterministic JSON for read-only toy lemma."""
from pathlib import Path
import argparse
from fractions import Fraction as Q
import hashlib
import json
import sys
import mpmath as mp

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from birth_contract import (read_birth_contract, audit_ncp_science_gates,
                            toy_full,toy_halves,toy_delta_closed,
                            toy_full_tangent,toy_halves_tangent,toy_halves_tangent_closed)
parser=argparse.ArgumentParser(description="Verify pinned HH/BE scalar birth law with exact arithmetic")
parser.add_argument("--output",required=True,help="new, nonexistent directory (create-only)")
args=parser.parse_args()
mp.mp.dps=120

def fm(q):
    return mp.mpf(q.numerator)/mp.mpf(q.denominator)

def s(q):return str(q.numerator)+'/'+str(q.denominator) if q.denominator!=1 else str(q.numerator)

def decimal(q,digits=70):return mp.nstr(fm(q),digits)

contract=read_birth_contract(ROOT/'inputs')
audit=audit_ncp_science_gates(ROOT/'inputs')
actualmoment=sum(t*w for t,w in contract.halves)-sum(t*w for t,w in contract.full)
assert actualmoment==-contract.amount*(contract.end-contract.start)/4
rows=[];maxdev=mp.mpf(0)
for x in [Q(0),Q(1,1000),Q(1,100),Q(1,4),Q(1),Q(4)]:
    for m in [Q(0),Q(1),Q(2)]:
        # At x=0 choose a fixed nonnegative stock instead of W/x.
        p=contract.amount*m/x if x else Q(1,100)*m
        w=contract.amount
        full=toy_full(p,w,x);half=toy_halves(p,w,x);delta=toy_delta_closed(p,w,x)
        assert delta==half-full
        # Separate direct 110-digit calculation, not rational closed-defect evaluation.
        mmx=fm(x);mmp=fm(p);mmw=fm(w)
        numerical_full=(mmp+mmw)/(1+mmx)
        numerical_half=((mmp+mmw/2)/(1+mmx/2)+mmw/2)/(1+mmx/2)
        err=abs(numerical_half-numerical_full-fm(delta))
        maxdev=max(maxdev,err)
        assert err<mp.mpf('1e-108'),(x,m,err)
        if x:
            continuous=mmp*mp.exp(-mmx)+(mmw/mmx)*(-mp.expm1(-mmx))
        else:continuous=mmp+mmw
        rows.append({'x_synthetic':s(x),'stock_over_equilibrium':s(m) if x else 'not_defined',
                     'p_exact':s(p),'w_exact':s(w),'delta_exact':s(delta),
                     'delta_decimal':decimal(delta,42),
                     'direct_full_decimal':mp.nstr(numerical_full,42),
                     'direct_half_decimal':mp.nstr(numerical_half,42),
                     'continuous_const_coefficient_reference':mp.nstr(continuous,42),
                     'sign':0 if delta==0 else (1 if delta>0 else -1),
                     'numerical_consistency_abs':mp.nstr(err,14)})

tan_rows=[]
for x in [Q(0),Q(1,1000),Q(1,4),Q(2),Q(4)]:
    p,dp,w,dw,dx=Q(1,7),Q(1,13),contract.amount,Q(1,300000),Q(1,9)
    f,df=toy_full_tangent(p,dp,w,dw,x,dx)
    h,dh=toy_halves_tangent(p,dp,w,dw,x,dx)
    assert (h,dh)==toy_halves_tangent_closed(p,dp,w,dw,x,dx)
    # Function composition independently differentiated numerically at 120-digit.
    def fun(lam):
        pm=fm(p)+fm(dp)*lam;wm=fm(w)+fm(dw)*lam;xm=fm(x)+fm(dx)*lam
        return ((pm+wm/2)/(1+xm/2)+wm/2)/(1+xm/2)
    dcheck=mp.diff(fun,mp.mpf(0))
    e=abs(dcheck-fm(dh));maxdev=max(maxdev,e)
    assert e<mp.mpf('1e-108'),(x,e)
    tan_rows.append({'x_synthetic':s(x),'endpoint_exact':s(h),'d_endpoint_dlambda_exact':s(dh),
                     'd_full_dlambda_exact':s(df),'independent_mpmath_error':mp.nstr(e,12)})

payload={
 'task':'HH_ENERGY06B_COMMON_SOURCE_LAW_DISCRETE_MEASURE_AUDIT',
 'scope':'exact stored binary64 birth weights and synthetic constant-opacity scalar BE model',
 'source_identity':{'paired_runtime_sha256':contract.source_digests[0],
                    'hh_paired_extension_sha256':contract.source_digests[1],
                    'NCP_SOURCE_MEASURE_sha256':hashlib.sha256((ROOT/'inputs/NCP_ENERGY06_SOURCE_MEASURE.json').read_bytes()).hexdigest()},
 'stored_owner_birth':{'t0_s':s(contract.start),'t1_s':s(contract.middle),'t2_s':s(contract.end),
       'h_s':s(contract.end-contract.start),'full':[{'time_s':s(t),'per_H':s(w)} for t,w in contract.full],
       'halves':[{'time_s':s(t),'per_H':s(w)} for t,w in contract.halves],
       'born_mass_per_H':s(contract.amount),'born_mass_decimal':decimal(contract.amount,40),
       'effective_source_per_H_s':s(contract.effective_source),
       'source_literal_binary64_fraction':s(contract.original_rate_binary64),
       'same_born_mass':True,'same_discrete_measure':False,
       'first_time_moment_half_minus_full_exact':s(actualmoment),
       'first_time_moment_decimal':decimal(actualmoment,62)},
 'lemma':{'constant_opacity_x':'x=kappa*h >= 0',
       'full':'F=(P+W)/(1+x)',
       'two_half':'H=(P+W/2)/(1+x/2)^2 +(W/2)/(1+x/2)',
       'difference_exact':'H-F=x*(W-x*P)/(4*(1+x)*(1+x/2)^2)',
       'sign':'x>0: sign(H-F)=sign(W-x*P); x=0: H=F',
       'continuous_reference':'P exp(-x) + W(1-exp(-x))/x if x>0; P+W for x=0',
       'tangent':'M_i v_i=v_previous+birth_lambda - x_lambda*P_i, M_i=1+x_i; do not reset previous term'},
 'direct_cases':rows,'tangent_cases':tan_rows,
 'numerical_check':{'mpmath_digits':120,'max_abs_error':mp.nstr(maxdev,25),'tolerance':'1e-108',
                    'direct_cases':len(rows),'tangent_cases':len(tan_rows)},
 'science_gate':audit,
 'claims_excluded':['actual HH coupled source/root/paired acceptance','energy dependent photo cross sections and cutoff','direction-dependent Bianchi transport','uniform lambda-energy interval proof','continuous source or local truncation error','new native scientific dispatch or authorization','272/0 next integral or whole289 coverage']
}
output_dir=Path(args.output).resolve()
output_dir.mkdir(parents=True,exist_ok=False)
out=output_dir/'ANALYSIS.json'
out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('RESULT',out)
print('source_born_mass',decimal(contract.amount,32))
print('source_moment',decimal(actualmoment,44))
print('exact_comparison_cases',len(rows),'tangent_cases',len(tan_rows))
print('max_abs_high_precision_check',mp.nstr(maxdev,24))
print('x=1/4,P=0 difference',next(t['delta_decimal'] for t in rows if t['x_synthetic']=='1/4' and t['stock_over_equilibrium']=='0'))
print('gate',audit['coverage_accepted'],'/',audit['coverage_accepted']+audit['missing_unbounded'],'science dispatch',audit['new_science_dispatch'])
