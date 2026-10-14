#!/usr/bin/env python3
"""PHYS23 new exact HI spectral sign certificate; Python standard library only.

Polynomials are lists of Fraction coefficients in ascending powers of z.
This script does not execute an inherited PHYS22 entry point or a gas IVP.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
from math import comb
import hashlib
import json
from pathlib import Path
import sys

EXPECTED_CONTRACT = '888eb11c8a53f828b0ed5d3a053d91dc4da671d727e49c519cb3110bb5b6d200'

def frac_literal(s):
    return F.from_float(float(s))

def trim(p):
    p = list(map(F, p))
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p

def add(p, q):
    r = [F(0)] * max(len(p), len(q))
    for i, v in enumerate(p): r[i] += v
    for i, v in enumerate(q): r[i] += v
    return trim(r)

def scale(p, c): return trim([v*c for v in p])

def sub(p, q): return add(p, scale(q, -1))

def mul(p, q):
    r = [F(0)] * (len(p)+len(q)-1)
    for i, u in enumerate(p):
        for j, v in enumerate(q): r[i+j] += u*v
    return trim(r)

def diff(p): return trim([i*p[i] for i in range(1, len(p))] or [0])

def ev(p, x):
    r = F(0)
    for v in reversed(p): r = r*x+v
    return r

def affine(p, lo, hi):
    """Exact monomial coefficients of p(lo+(hi-lo)*t)."""
    n = len(p)-1
    return trim([sum((p[j]*comb(j,k)*lo**(j-k)*(hi-lo)**k for j in range(k,n+1)),F(0)) for k in range(n+1)])

def bernstein(p, lo, hi):
    """b_k for p(lo+(hi-lo)t)=sum b_k binom(n,k)t^k(1-t)^(n-k)."""
    a=affine(p,lo,hi); n=len(p)-1
    a += [F(0)]*(n+1-len(a))
    return [sum((a[j]*F(comb(k,j),comb(n,j)) for j in range(k+1)), F(0)) for k in range(n+1)]

def bernstein_to_power(b):
    n=len(b)-1
    r=[F(0)]*(n+1)
    for k in range(n+1):
        for j in range(n-k+1):
            r[k+j] += b[k]*comb(n,k)*comb(n-k,j)*((-1)**j)
    return trim(r)

def fs(x): return str(x.numerator)+'/'+str(x.denominator)

def packed(p): return [fs(x) for x in p]

def describe(p, lo, hi, sign):
    b=bernstein(p,lo,hi)
    return {
        'degree': len(p)-1,
        'power_coefficients_ascending': packed(p),
        'bernstein_coefficients_ascending': packed(b),
        'bernstein_coefficient_count': len(b),
        'desired_strict_sign': sign,
        'strict_sign_count': sum((x*sign)>0 for x in b),
        'min_bernstein_exact': fs(min(b)),
        'max_bernstein_exact': fs(max(b)),
        'min_bernstein_approx': float(min(b)),
        'max_bernstein_approx': float(max(b)),
        'all_coefficients_strict_sign': all(x*sign>0 for x in b),
        'basis_conversion_identity': bernstein_to_power(b) == affine(p,lo,hi),
    }

def build():
    here=Path(__file__).resolve()
    root=here.parents[2]
    cp=root/'PHYSICS_CONTRACT.json'
    contract_hash=hashlib.sha256(cp.read_bytes()).hexdigest()
    checks=[]
    def check(name, ok, detail=None):
        checks.append({'id': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
        return ok
    check('contract_identity', contract_hash == EXPECTED_CONTRACT, contract_hash)
    a=frac_literal('32.88'); p=frac_literal('2.963'); e0=frac_literal('0.4298')
    k=a*e0; chi=frac_literal('13.598434599702')
    kb=frac_literal('1.380649e-16'); electronvolt=frac_literal('1.602176634e-12')
    temperature=F(50000); eth=F(3,2)*kb*temperature/electronvolt
    lower=F(49,50); upper=F(33,25)
    elo=frac_literal('13.60'); ehi=frac_literal('24.59')
    z=[F(0),F(1)]; z2=mul(z,z)
    B=[F(-1),F(0),a]; C=[F(1),F(1)]; G=mul(B,C)
    N=add(add(scale(G,-7),scale(C,4)),scale(B,p))
    # alpha=N/(2G), beta=z (N'G-NG')/(4G^2).
    W=sub(mul(diff(N),G),mul(N,diff(G)))
    PA=add(add(mul(N,N),scale(mul(N,G),6)),mul(z,W))
    def hpoly(c):
        return add(mul(add(scale(z2,k),[-c]),PA),scale(mul(mul(z2,G),add(N,scale(G,4))),4*k))
    PQ=hpoly(chi); PT=hpoly(chi+eth)
    PR=sub(mul(diff(PQ),PA),mul(PQ,diff(PA)))
    # r(E) = PQ/PA, dr/dE = PR / (2 k z PA^2).
    polynomials={name:describe(poly,lower,upper,sgn) for name,poly,sgn in [
        ('A_numerator',PA,-1),('heat_numerator',PQ,-1),
        ('temperature_numerator',PT,-1),('ratio_derivative_numerator',PR,1),
    ]}
    check('positive_constants',all(v>0 for v in [a,p,e0,k,kb,electronvolt,temperature,eth]))
    check('positive_z_interval',0<lower<upper)
    check('full_open_energy_domain_is_enclosed', k*lower**2<elo<ehi<k*upper**2,
          {'E_from_z_lower_eV':fs(k*lower**2),'E_from_z_upper_eV':fs(k*upper**2),'physical_lower_eV':fs(elo),'physical_upper_eV':fs(ehi)})
    check('main_compact_domain_is_inside',elo<F('13.61')<F('24.58')<ehi)
    check('denominator_positive', a*lower**2-1>0 and 1+lower>0,
          {'B_lower_exact':fs(a*lower**2-1),'C_lower_exact':fs(1+lower)})
    check('opacity_cutoff_above_physical_threshold',elo>chi)
    # The simplified log slope supplies a second short sign proof of A.
    def alpha(zv): return -F(7,2)+2/(a*zv*zv-1)+p/(2*(1+zv))
    check('log_slope_between_minus_three_and_minus_two',-3<alpha(upper)<alpha(lower)<-2,
          {'alpha_lower_z':fs(alpha(lower)),'alpha_upper_z':fs(alpha(upper))})
    check('beta_strictly_negative_formula',a>0 and p>0 and lower>0,
          'beta = -2 a z^2/(a z^2-1)^2 - p z/[4(1+z)^2] < 0')
    check('expanded_N_identity', N == [11-p,F(11),a*(p-7),-7*a])
    for name,rec in polynomials.items():
        check(name+'_exact_bernstein_sign',rec['all_coefficients_strict_sign'],rec['strict_sign_count'])
        check(name+'_basis_conversion',rec['basis_conversion_identity'])
    # At rational z endpoints, r itself is rational: these are conservative
    # strict bounds for all energies in the physical open interval.
    rlo=ev(PQ,lower)/ev(PA,lower); rhi=ev(PQ,upper)/ev(PA,upper)
    check('ratio_lower_bound_exceeds_thermal_particle_cost',rlo>eth,
          {'r_lower_eV':fs(rlo),'e_th_eV':fs(eth)})
    # Pair independent pointwise rational derivative identities with the
    # interval proof, to detect algebraic transcription in PA and PH.
    for zv in [lower,F(1),F(6,5),upper]:
        av=alpha(zv)
        bv=-2*a*zv*zv/(a*zv*zv-1)**2-p*zv/(4*(1+zv)**2)
        aval=av*av+3*av+bv; energy=k*zv*zv
        denom=4*ev(G,zv)**2
        check('A_rational_definition_at_'+fs(zv),ev(PA,zv)/denom==aval)
        for label,c,poly in [('heat',chi,PQ),('temperature',chi+eth,PT)]:
            direct=(energy-c)*aval+energy*(2*av+4)
            check(label+'_product_rule_at_'+fs(zv),ev(poly,zv)/denom==direct)
    data={
        'task':'REI-PHYS23-20261010',
        'kind':'exact_rational_Bernstein_spectral_sign_certificate',
        'evidence_status':['derived','implementation-verified'],
        'contract_sha256':contract_hash,
        'arithmetic':'fractions.Fraction; source binary64 literals interpreted as exact real rationals',
        'python_requirement':'>=3.10; standard library only',
        'constants':{name:{'exact':fs(v),'approx':float(v)} for name,v in [
            ('E0_eV',e0),('ya',a),('P',p),('k_E0_ya_eV',k),('chi_HI_eV',chi),
            ('kB_erg_K',kb),('electronvolt_erg',electronvolt),('T_K',temperature),('e_th_eV',eth)]},
        'domain':{'physical_energy_eV_open':[fs(elo),fs(ehi)],'primary_energy_eV_closed':['1361/100','1229/50'],
                  'certificate_z_closed':[fs(lower),fs(upper)],'z_definition':'sqrt(E/(E0*ya))',
                  'z_to_energy_enclosing_eV_closed':[fs(k*lower**2),fs(k*upper**2)],
                  'strict_local_regularity':'positive spectral support stays separated from HI/HeI cutoffs for initial-time differentiation'},
        'formula_definitions':{
            'B':'ya*z^2 - 1','C':'1+z','G':'B*C',
            'N':'-7*G+4*C+P*B = -7*ya*z^3+(P-7)*ya*z^2+11*z+11-P',
            'alpha':'N/(2*G) = -7/2+2/B+P/(2*C)',
            'beta':'z*(N_prime*G-N*G_prime)/(4*G^2)',
            'A':'alpha^2+3*alpha+beta = PA/(4*G^2)',
            'PA':'N^2+6*N*G+z*(N_prime*G-N*G_prime)',
            'PHc':'(k*z^2-c)*PA+4*k*z^2*G*(N+4*G)',
            'Hc':'(E-c)*A+E*(2*alpha+4) = PHc/(4*G^2)',
            'r':'PQ/PA = C[lambda*(E-chi)]/C[lambda]',
            'PR':'PQ_prime*PA-PQ*PA_prime',
            'dr_dE':'PR/(2*k*z*PA^2)',
            'bernstein':'p(L+(U-L)t) = sum_{k=0}^n b_k binom(n,k)t^k(1-t)^(n-k), 0<=t<=1',
        },
        'auxiliary_polynomials':{'G':packed(G),'N':packed(N)},
        'polynomials':polynomials,
        'ratio_bounds_eV':{'lower_exact':fs(rlo),'upper_exact':fs(rhi),'lower_approx':float(rlo),'upper_approx':float(rhi),
                           'scope':'strict conservative bounds for the full physical open interval, by larger rational z enclosure and positive derivative'},
        'certified_conclusions':{'A':'strictly negative','heat_H_chi':'strictly negative','temperature_H_chi_plus_eth':'strictly negative','dr_dE':'strictly positive',
                                 'HII_heat_T_zero_count_in_full_open_interval':0,
                                 'ratio_exceeds_thermal_particle_cost':True},
        'checks':checks,
        'pass_count':sum(c['status']=='PASS' for c in checks),'check_count':len(checks),
        'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL',
        'scope_limits':['local initial-time epsilon^2 coefficient only','no threshold crossing','no native floating point equivalence','no new gas IVP','no prior PHYS22 proof replay','no full algebra proof assistant kernel'],
    }
    return data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    if args.output.exists(): raise SystemExit('Output exists; use a fresh path to preserve earlier evidence.')
    data=build(); args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':data['status'],'checks':data['check_count'],'passed':data['pass_count'],
                      'polynomial_signs':{k:(v['degree'],v['strict_sign_count'],v['bernstein_coefficient_count']) for k,v in data['polynomials'].items()},
                      'ratio_bounds_eV':{k:v for k,v in data['ratio_bounds_eV'].items() if 'approx' in k}},ensure_ascii=False))
    return 0 if data['status']=='PASS' else 1
if __name__=='__main__': sys.exit(main())
