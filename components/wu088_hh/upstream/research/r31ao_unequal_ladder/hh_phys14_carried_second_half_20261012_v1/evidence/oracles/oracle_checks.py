#!/usr/bin/env python3
"""Bounded PHYS14 arithmetic/implicit-function semantic oracles.

Imports the candidate's pure functions, never its main or scientific inputs.
Analytic oracle: one scalar gas root of a quadratic, with nonzero gas/photon
value, first derivatives and mixed derivative inherited from an earlier map.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import pathlib
import resource
import time
from fractions import Fraction as F
from types import SimpleNamespace

CPU_LIMIT = 30
MEMORY_LIMIT = 256 * 1024 * 1024
resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT, CPU_LIMIT))
resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))
resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024, 16 * 1024 * 1024))

HERE = pathlib.Path(__file__).resolve().parent
CANDIDATE = pathlib.Path('/workspace/scratch/b826cbaab54f/HH_PHYS14_20261012_v1/src/phys14_advance.py')

def pf(x):
    x=F(x)
    return {'numerator':str(x.numerator),'denominator':str(x.denominator)}

def dump_interval(x):
    return {'lo':pf(x.lo),'hi':pf(x.hi)}

def pow2(k):
    return F(2**k) if k>=0 else F(1,2**(-k))

class Polynomial:
    """Exact truncated polynomial, lambda/b increments squared are zero.

    No differentiation formulas for an implicit residual are used here.
    The closed-form quadratic root is evaluated algebraically in this ring.
    """
    KEYS=((0,0),(1,0),(0,1),(1,1))
    def __init__(self, x=0):
        self.c={k:F(0) for k in self.KEYS}
        if isinstance(x,Polynomial): self.c=dict(x.c)
        elif isinstance(x,dict): self.c.update({k:F(v) for k,v in x.items()})
        else: self.c[(0,0)]=F(x)
    def __add__(self,other):
        other=Polynomial(other)
        return Polynomial({k:self.c[k]+other.c[k] for k in self.KEYS})
    __radd__=__add__
    def __neg__(self): return Polynomial({k:-v for k,v in self.c.items()})
    def __sub__(self,other): return self+-Polynomial(other)
    def __rsub__(self,other): return Polynomial(other)+-self
    def __mul__(self,other):
        other=Polynomial(other); ret={k:F(0) for k in self.KEYS}
        for (a,b),x in self.c.items():
            for (c,d),y in other.c.items():
                if a+c<2 and b+d<2: ret[(a+c,b+d)]+=x*y
        return Polynomial(ret)
    __rmul__=__mul__
    def __truediv__(self,other):
        other=Polynomial(other); v=other.c[(0,0)]
        assert v!=0
        n=(other-v)*(1/v)
        return self*(1-n+n*n)*(1/v)
    def __rtruediv__(self,other): return Polynomial(other)/self
    def sqrt_at_rational_positive_value(self):
        v=self.c[(0,0)]; assert v>0
        rn,rd=math.isqrt(v.numerator),math.isqrt(v.denominator)
        assert rn*rn==v.numerator and rd*rd==v.denominator
        s=F(rn,rd); n=(self-v)/v
        return s*(1+n/2-n*n/8)
    def slots(self): return tuple(self.c[k] for k in self.KEYS)
    def zero(self): return all(v==0 for v in self.c.values())

def reference_round_known_binade(mantissa, exponent, sign, bits):
    """Independent oracle using a binade known by construction.

    Positive magnitude Euclidean division, followed by sign exchange.  It does
    not infer a binary exponent with the candidate's bit_length algorithm.
    """
    assert 1<=mantissa<2 and sign in (-1,1)
    scaled=mantissa*2**(bits-1)
    quotient,remainder=divmod(scaled.numerator,scaled.denominator)
    floor_mag=F(quotient)*pow2(exponent-bits+1)
    ceil_mag=F(quotient+(remainder!=0))*pow2(exponent-bits+1)
    return (floor_mag,ceil_mag) if sign==1 else (-ceil_mag,-floor_mag)

def rounding_checks(candidate):
    bits=candidate.BITS; assert bits==256
    fractions=[('one',F(1)),('three_halves',F(3,2)),('four_thirds',F(4,3)),
        ('almost_one_nondyadic',1+F(1,2**260+3)),
        ('almost_two_nondyadic',2-F(1,2**260+3)),
        ('exact_last_bit',1+F(1,2**255)),
        ('half_ulp_above_one',1+F(1,2**256)),
        ('inside_high_significand',1+F(2**255-1,2**256)),
        ('wide_odd_denominator',1+F(2**280+11,2**281+33))]
    exponents=(-16384,-4096,-1075,-1074,-1022,-512,-256,-1,0,1,53,255,256,511,1023,4096,16384)
    records=[]; total=0; digest=hashlib.sha256()
    for exponent in exponents:
        for label,mantissa in fractions:
            for sign in (-1,1):
                x=sign*mantissa*pow2(exponent)
                expected=reference_round_known_binade(mantissa,exponent,sign,bits)
                actual=(candidate.dyadic(x,False),candidate.dyadic(x,True))
                assert actual==expected,(label,exponent,sign,'rounding disagreement')
                assert actual[0]<=x<=actual[1]
                assert (actual[0]>0) if sign==1 else (actual[1]<0)
                assert candidate.dyadic(actual[0],False)==actual[0]
                assert candidate.dyadic(actual[1],True)==actual[1]
                digest.update(f'{label},{exponent},{sign};'.encode())
                # Exact output identity without enormous decimal serialization.
                for y in actual:
                    digest.update(hex(y.numerator).encode()+b'/'+hex(y.denominator).encode()+b';')
                total+=1
    assert candidate.dyadic(F(0),False)==candidate.dyadic(F(0),True)==0
    tiny=pow2(-100000)
    tiny_pos=candidate.I(F(3,7)*tiny,F(5,11)*tiny)
    tiny_neg=-tiny_pos
    crossing=candidate.I(-F(5,11)*tiny,F(3,7)*tiny)
    assert 0<tiny_pos.lo<=F(3,7)*tiny<=F(5,11)*tiny<=tiny_pos.hi
    assert tiny_neg.lo<=-F(5,11)*tiny<=-F(3,7)*tiny<=tiny_neg.hi<0
    assert crossing.lo<0<crossing.hi
    rejected=[]
    for label,z in [('point_zero',candidate.I(0)),('symmetric_tiny',candidate.I(-tiny,tiny)),
                    ('positive_with_zero',candidate.I(0,tiny)),('negative_with_zero',candidate.I(-tiny,0))]:
        try: candidate.I(1)/z
        except AssertionError as e:
            assert str(e)=='interval division by zero'; rejected.append(label)
        else: raise AssertionError(f'zero divisor accepted: {label}')
    # Mixed signs and huge exponent gap: addition/multiplication/division include
    # exact rational corner extrema independently computed from original inputs.
    aa=(F(-5,7)*pow2(-4096),F(9,11)*pow2(-4096))
    bb=(F(13,17)*pow2(4096),F(19,23)*pow2(4096))
    ai,bi=candidate.I(*aa),candidate.I(*bb)
    product=ai*bi; quotient=ai/bi
    exact_products=[a*b for a in aa for b in bb]
    exact_quotients=[a/b for a in aa for b in bb]
    assert product.lo<=min(exact_products)<=max(exact_products)<=product.hi
    assert quotient.lo<=min(exact_quotients)<=max(exact_quotients)<=quotient.hi
    return {'status':'PASS','kind':'arithmetic implementation semantic check',
        'significand_bits':bits,'known_binade_point_cases':total,'binade_exponents':list(exponents),
        'mantissa_families':[x[0] for x in fractions],'signs':[-1,1],
        'rounding_oracle':'known input binade; independent positive magnitude Euclidean division and sign exchange',
        'all_point_inclusions_and_exact_directed_outputs':True,
        'all_nonzero_signs_preserved':True,'exact_zero_preserved':True,
        'unbounded_tiny_tail_exponent':-100000,'tiny_positive_negative_and_crossing_preserved':True,
        'zero_divisor_rejections':rejected,'mixed_sign_large_exponent_gap_arithmetic':'PASS',
        'exact_output_stream_sha256':digest.hexdigest()}

def closed_form_case(beta):
    theta_l=F(1,3); theta_b=F(2,5); gamma=F(1,20)
    x_target=F(1,2); r0=F(5,14)-gamma*theta_l*(1-beta*x_target)
    eps=Polynomial({(1,0):1}); eta=Polynomial({(0,1):1})
    la=theta_l+eps
    old=r0+eps/F(13)+eta/F(17)+eps*eta/F(19)
    incoming=1+eps/F(7)+eta/F(11)+eps*eta/F(23)
    B=1+gamma*beta*la; C0=old+gamma*la
    middle=4*B+C0+incoming; constant=4*C0+incoming
    discr=middle*middle-4*B*constant
    root=(middle-discr.sqrt_at_rational_positive_value())/(2*B)
    photon=3*incoming/(4-root)
    absorbed=incoming-photon
    residual=root-old-gamma*la*(1-beta*root)-absorbed
    assert residual.zero()
    assert root.slots()[0]==x_target
    # Exact source partial formula compared with a root obtained independently
    # from the quadratic closed form, including nonzero incoming mixed carry.
    x,u,v,w=root.slots(); n,nu,nv,nw=incoming.slots(); r,ru,rv,rw=old.slots()
    h=F(1); a=F(1,3); D=1+h*a*(1-x)
    K=a*(1-x)/D; Kp=-a/D**2; Kpp=-2*h*a*a/D**3
    A=1-(-gamma*beta*theta_l+n*Kp)
    f_la=gamma*(1-beta*x)+K*nu; f_b=K*nv
    terms={'inherited_gas_W':rw,'Fgg_U_V':n*Kpp*u*v,
        'F_g_lambda_V':(-gamma*beta+Kp*nu)*v,
        'F_g_b_U':Kp*nv*u,'F_lambdab_incoming':K*nw}
    assert (ru+f_la)/A==u and (rv+f_b)/A==v
    assert sum(terms.values(),F(0))/A==w
    assert all(t!=0 for t in terms.values())
    # Check the five quotient mixed terms against the closed-form photon root.
    quotient_terms={'incoming_W_over_D':nw/D,'incoming_U_times_gas_V':h*a*nu*v/D**2,
       'incoming_V_times_gas_U':h*a*nv*u/D**2,'gas_W_times_incoming_value':h*a*n*w/D**2,
       'two_denominator_cross_terms':2*(h*a)**2*n*u*v/D**3}
    assert photon.slots()[1]==nu/D+h*a*n*u/D**2
    assert photon.slots()[2]==nv/D+h*a*n*v/D**2
    assert sum(quotient_terms.values(),F(0))==photon.slots()[3]
    assert all(t!=0 for t in quotient_terms.values())
    # Every individual omission is distinguishable from the closed-form answer.
    omitted={k:(sum(terms.values(),F(0))-term)/A for k,term in terms.items()}
    assert all(z!=w for z in omitted.values())
    q_omitted={k:photon.slots()[3]-term for k,term in quotient_terms.items()}
    assert all(z!=photon.slots()[3] for z in q_omitted.values())
    return {'beta':beta,'theta':(theta_l,theta_b),'gamma':gamma,'old':old,'incoming':incoming,
       'root':root,'photon':photon,'absorbed':absorbed,'A':A,'terms':terms,
       'quotient_terms':quotient_terms,'K':K,'Kp':Kp,'Kpp':Kpp}

def exercise_candidate(candidate,case):
    I=candidate.I; beta=case['beta']; gamma=case['gamma']
    gvals=[case['root'].slots()[0],F(1,10),F(1,5),F(1)]
    g=[I(x) for x in gvals]
    def const_jet(val=0,grad=0):
        return {'value':I(val),'g':[I(grad),I(0),I(0),I(0)],
                'gg':[[I(0) for _ in range(4)] for _ in range(4)]}
    # Synthetic fixture for a public evaluation method: exactly one unknown and
    # one photon.  It does not call Source.__init__ or read any scientific data.
    synthetic=SimpleNamespace(X=g,z0=g,np=[const_jet() for _ in range(4)],
        q=const_jet(gamma*(1-beta*gvals[0]),-gamma*beta),
        hh=[I(1),I(0),I(0),I(0)],h=I(1),a=[I(F(1,3))],heat=[I(0)],H=I(0),
        N={slot:[I(value)] for slot,value in zip(candidate.SLOTS,case['incoming'].slots())})
    evaluated=candidate.Source.evaluate(synthetic,g,tighten=False)
    scales=[F(1)]*4
    L=evaluated['Fg']; bound,_=candidate.contraction(L,scales)
    assert 0<=bound<1
    old=case['old'].slots(); truth=case['root'].slots()
    prev={slot:[I(value),I(0),I(0),I(0)] for slot,value in zip(candidate.SLOTS,old)}
    rhs_u=candidate.vadd(prev['U'],evaluated['F_lambda'])
    rhs_v=candidate.vadd(prev['V'],evaluated['F_b'])
    U,cu=candidate.neumann(L,rhs_u,scales,bound)
    V,cv=candidate.neumann(L,rhs_v,scales,bound)
    bilinear=[sum((evaluated['Fgg'][i][j][k]*U[j]*V[k]
                  for j in range(4) for k in range(4)),I(0)) for i in range(4)]
    wterms=[bilinear,candidate.matvec(evaluated['F_g_lambda'],V),
         candidate.matvec(evaluated['F_g_b'],U),evaluated['F_lambdab']]
    rhs_w=candidate.vadd(prev['W'],[sum((v[i] for v in wterms),I(0)) for i in range(4)])
    W,cw=candidate.neumann(L,rhs_w,scales,bound)
    for vec,target in zip((U,V,W),truth[1:]):
        assert vec[0].lo<=target<=vec[0].hi
        assert all(z.contains_zero() for z in vec[1:])
    photons,absorbed=candidate.outgoing_carry(synthetic,g,U,V,W,evaluated)
    for slot,truth_n,truth_a in zip(candidate.SLOTS,case['photon'].slots(),case['absorbed'].slots()):
        assert photons[slot][0].lo<=truth_n<=photons[slot][0].hi
        assert absorbed[slot][0].lo<=truth_a<=absorbed[slot][0].hi
    return {'candidate_functions_exercised':['Source.evaluate','contraction','neumann','outgoing_carry'],
       'lambda_evaluation_box':[0,1],'oracle_derivative_point':[pf(x) for x in case['theta']],
       'contraction_upper':pf(bound),'neumann_degree':cu['degree'],
       'candidate_gas_UVW':[dump_interval(z[0]) for z in (U,V,W)],
       'candidate_photon_UVW':[dump_interval(photons[s][0]) for s in ('U','V','W')],
       'all_exact_root_and_photon_derivatives_contained':True,
       'primal_nonlinear_solver_executed':False,'candidate_main_executed':False}

def main():
    started=time.perf_counter(); before=CANDIDATE.read_bytes()
    spec=importlib.util.spec_from_file_location('phys14_candidate_pure_functions',CANDIDATE)
    candidate=importlib.util.module_from_spec(spec); spec.loader.exec_module(candidate)
    rounding=rounding_checks(candidate)
    cases=[]
    for beta in (0,1):
        case=closed_form_case(beta)
        impl=exercise_candidate(candidate,case)
        cases.append({'status':'PASS','HH_shape_beta':beta,
           'implicit_equation':'x = old(lambda,b) + gamma*lambda*(1-beta*x) + Nin(lambda,b)*(1-x)/(4-x)',
           'root_formula':'(L-sqrt(L^2-4BC))/(2B), B=1+gamma*beta*lambda, c=old+gamma*lambda, L=4B+c+Nin, C=4c+Nin',
           'parameter_point':[pf(x) for x in case['theta']], 'gamma':pf(case['gamma']),
           'old_value_U_V_W':[pf(x) for x in case['old'].slots()],
           'incoming_value_U_V_W':[pf(x) for x in case['incoming'].slots()],
           'closed_root_value_U_V_W':[pf(x) for x in case['root'].slots()],
           'closed_photon_value_U_V_W':[pf(x) for x in case['photon'].slots()],
           'A':pf(case['A']),'mixed_gas_numerator_terms':{k:pf(v) for k,v in case['terms'].items()},
           'mixed_photon_terms':{k:pf(v) for k,v in case['quotient_terms'].items()},
           'each_gas_and_photon_mixed_term_omission_detected':True,
           'all_residual_polynomial_coefficients_exact_zero':True,
           'implementation':impl})
    assert CANDIDATE.read_bytes()==before,'candidate changed during check'
    result={'schema':'PHYS14_REQUIRED_SEMANTIC_ORACLES_V1','status':'PASS',
       'role':'candidate validation by candidate theory author; not independent decision review',
       'new_physical_cases':0,'old_scientific_suites_rerun':0,'candidate_main_calls':0,
       'semantic_families':2,'quadratic_oracle_variants':2,
       'rounding':rounding,'implicit_oracle':cases,
       'candidate_path':str(CANDIDATE),'candidate_sha256':hashlib.sha256(before).hexdigest(),
       'oracle_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
       'candidate_unchanged':True,'elapsed_s':time.perf_counter()-started,
       'ru_maxrss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       'limits':{'cpu_s':CPU_LIMIT,'address_space_bytes':MEMORY_LIMIT}}
    with (HERE/'ORACLE_RESULTS.json').open('x') as f:
        json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
    print(json.dumps({'status':result['status'],'semantic_families':2,
       'dyadic_point_cases':rounding['known_binade_point_cases'],
       'quadratic_variants':len(cases),'elapsed_s':result['elapsed_s'],
       'maxrss_KiB':result['ru_maxrss_KiB'],'new_physical_cases':0},ensure_ascii=False))

if __name__=='__main__': main()
