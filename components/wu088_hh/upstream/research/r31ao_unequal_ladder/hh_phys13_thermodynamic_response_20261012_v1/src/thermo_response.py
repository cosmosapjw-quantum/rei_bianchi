#!/usr/bin/env python3
"""PHYS13: exact interval transfer of retained first-stage HH responses.

No source evaluation, inverse, root solver, or historical suite is called.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import resource
import struct
import sys
import time

sys.set_int_max_str_digits(0)


@dataclass(frozen=True)
class I:
    lo: Q
    hi: Q

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError('empty interval')

    @staticmethod
    def point(x):
        x = Q(x)
        return I(x, x)

    def __add__(self, other):
        other = as_i(other)
        return I(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -as_i(other)

    def __rsub__(self, other):
        return as_i(other) + -self

    def __mul__(self, other):
        other = as_i(other)
        products = [a*b for a in (self.lo,self.hi) for b in (other.lo,other.hi)]
        return I(min(products),max(products))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError('interval contains zero')
        return I(1/self.hi,1/self.lo)

    def __truediv__(self, other):
        return self * as_i(other).reciprocal()

    def __rtruediv__(self, other):
        return as_i(other) * self.reciprocal()

    def __pow__(self, n):
        if n < 0:
            return self.reciprocal() ** (-n)
        if n == 0:
            return I.point(1)
        if n % 2 and self.lo < 0:
            return I(self.lo**n,self.hi**n)
        if self.lo >= 0:
            return I(self.lo**n,self.hi**n)
        if self.hi <= 0:
            return I(self.hi**n,self.lo**n)
        return I(Q(0),max(self.lo**n,self.hi**n))

    def intersect(self, other):
        return I(max(self.lo,other.lo),min(self.hi,other.hi))

    def subset(self, other):
        return other.lo <= self.lo <= self.hi <= other.hi

    def mag(self):
        return max(abs(self.lo),abs(self.hi))


def as_i(x):
    return x if isinstance(x,I) else I.point(x)


def bits_q(bits):
    value = struct.unpack('>d',bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise ValueError('non-finite captured leaf')
    return Q.from_float(value)


def read_i(row):
    if 'exact' in row:
        ex=row['exact']
        result=I(Q(int(ex['lo'][0]),int(ex['lo'][1])),Q(int(ex['hi'][0]),int(ex['hi'][1])))
        if 'lo_bits' in row:
            outer=I(bits_q(row['lo_bits']),bits_q(row['hi_bits']))
            if not result.subset(outer):
                raise ValueError('stored floating display does not enclose exact endpoints')
    else:
        result=I(bits_q(row['lo_bits']),bits_q(row['hi_bits']))
    if 'lo' in row:
        for edge in ('lo','hi'):
            if struct.pack('>d',row[edge]).hex()!=row[edge+'_bits']:
                raise ValueError('decimal/bit display mismatch')
    return result


def decimal_out(x,lower):
    with localcontext() as ctx:
        ctx.prec=10
        ctx.rounding=ROUND_FLOOR if lower else ROUND_CEILING
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def packed(x,unit=None):
    x=as_i(x)
    d={'exact':{'lo':[str(x.lo.numerator),str(x.lo.denominator)],'hi':[str(x.hi.numerator),str(x.hi.denominator)]},
       'outward_decimal':[decimal_out(x.lo,True),decimal_out(x.hi,False)],
       'sign':'STRICT_POSITIVE' if x.lo>0 else 'STRICT_NEGATIVE' if x.hi<0 else 'ZERO' if x.lo==x.hi==0 else 'CONTAINS_ZERO'}
    if unit is not None:d['unit']=unit
    return d


def value_and_lambda(g,U,beta,C):
    x,y1,y2,w=g
    e=x+beta*(y1+2*y2)
    P=1+beta+e
    Ue=U[0]+beta*(U[1]+2*U[2])
    T=C*w/P
    thermal=C*U[3]/P
    particle=-C*w*Ue/P**2
    return {'e':e,'P':P,'T':T,'Ue':Ue,'UT':thermal+particle,
            'thermal':thermal,'particle':particle}


def readout_bridge(g,U,f,fh,C):
    x,y1,y2,w=g
    Z=1+y1+2*y2
    UZ=U[1]+2*U[2]
    Pf=1+x+f*Z
    Ph=1+x+fh*Z
    Upf=U[0]+f*UZ
    Uph=U[0]+fh*UZ
    den=Pf*Ph
    change=-C*(f-fh)*w*Z/den
    deriv=-C*(f-fh)*((U[3]*Z+w*UZ)/den-w*Z*(Upf*Ph+Pf*Uph)/den**2)
    return change,deriv


def semantic_cases():
    checks=[]
    def ok(name,truth):
        if not truth:raise AssertionError(name)
        checks.append({'case':name,'status':'PASS'})
    # Independent finite quotient identity at two exact rational endpoints.
    C=Q(7,3);w0=Q(27,2);w1=Q(61,5);p0=Q(53,25);p1=Q(11,5)
    finite=C*w1/p1-C*w0/p0
    split=C*(w1-w0)/p1-C*w0*(p1-p0)/(p1*p0)
    ok('finite_temperature_endpoint_identity',finite==split and finite<0)
    # A decreasing thermal energy does not force decreasing temperature.
    g=list(map(I.point,[1,0,0,2]));U=list(map(I.point,[-1,0,0,Q(-1,10)]))
    v=value_and_lambda(g,U,Q(0),Q(1))
    ok('negative_Uw_can_heat_when_particles_fall',v['UT']==I.point(Q(9,20)))
    # Nonzero correlated state changes preserve an exactly constant T.
    U=list(map(I.point,[Q(1,10),0,0,Q(1,5)]));g=list(map(I.point,[1,0,0,4]))
    v=value_and_lambda(g,U,Q(0),Q(1))
    ok('constant_temperature_correlated_limit',v['UT']==I.point(0))
    # Compare the factored bridge with separately differentiated two readouts at a point.
    g=list(map(I.point,[Q(9,10),Q(3,10),Q(3,5),Q(27,2)]))
    U=list(map(I.point,[Q(1,100),Q(-1,1000),Q(1,2000),Q(-3,20)]))
    f,fh,C=Q(83,1000),Q(829,10000),Q(7000)
    delta,deriv=readout_bridge(g,U,f,fh,C)
    vf=value_and_lambda(g,U,f,C);vh=value_and_lambda(g,U,fh,C)
    ok('factored_normalization_bridge_exact',delta==vf['T']-vh['T'] and deriv==vf['UT']-vh['UT'])
    zero_delta,zero_deriv=readout_bridge(g,U,fh,fh,C)
    ok('equal_readout_normalization_limit',zero_delta==zero_deriv==I.point(0))
    try:
        I(Q(-1),Q(1)).reciprocal()
    except ZeroDivisionError:
        ok('zero_containing_denominator_rejected',True)
    else:raise AssertionError('zero denominator not rejected')
    return checks


def stage_result(root,s,d,leaves):
    name=s['stage']
    source_path=root/'inputs/ncp07/results'/name/'SOURCE_BOX.json'
    raw=json.loads(source_path.read_text())
    expected=next(e for e in d['input_exports'] if e['path'].endswith('/SOURCE_BOX.json'))
    if hashlib.sha256(source_path.read_bytes()).hexdigest()!=expected['sha256']:
        raise ValueError('PHYS09 SOURCE_BOX identity mismatch')
    nH=bits_q(raw['nH_bits']);nHe=bits_q(raw['nHe_stored_bits'])
    f=bits_q(raw['fHe_bits']);fh=nHe/nH;dt=bits_q(raw['dt_bits'])
    C=2*bits_q(leaves['ev_erg_bits'])/(3*bits_q(leaves['kb_bits']))
    chi,ch1,ch2=map(bits_q,leaves['CHI_bits'])
    U=[read_i(v) for v in s['U']]
    V=[read_i(v) for v in s['V']]
    W=[read_i(v) for v in s['W']]
    X=[read_i(v) for v in d['thermal_X']]
    centres=[read_i(v) for v in d['Banach_ball_center']]
    radius=[read_i(v) for v in d['radius']]
    beta=[read_i(v) for v in d['banach_beta']]
    kr=[read_i(v) for v in d['banach_absK_radius']]
    m=[b+k for b,k in zip(beta,kr)]
    if any(v.hi>=r.lo for v,r in zip(m,radius)):
        raise ValueError('retained strict self-map margin not positive')
    g=[I(c.lo-v.hi,c.hi+v.hi).intersect(x) for c,v,x in zip(centres,m,X)]
    val=value_and_lambda(g,U,fh,C)
    if not (val['P'].lo>0 and val['Ue'].lo>0 and U[3].hi<0):
        raise ValueError('positive particle/electron or negative thermal prerequisite not certified')
    # First derivative of the already projected source energy: a NEW contraction.
    EJ=d['energy_source_Jet']
    grad=[read_i(v) for v in EJ['gradient']]
    Eprojected=dt*(sum((grad[k]*U[k] for k in range(4)),I.point(0))+grad[4])
    ell=[chi,f*ch1,f*(ch1+ch2),Q(1)]
    Edirect=sum((a*u for a,u in zip(ell,U)),I.point(0))
    Eg=Eprojected.intersect(Edirect)
    R=Eg+(chi*fh-f*ch1)*U[1]+(2*chi*fh-f*(ch1+ch2))*U[2]
    eff=(chi-R/val['Ue']).intersect(-U[3]/val['Ue'])
    if eff.lo<=0:raise ValueError('effective cooling energy not positive')
    P,w=val['P'],g[3]
    UT_projected=C/P*(R-(chi+w/P)*val['Ue'])
    UT=val['UT'].intersect(UT_projected)
    thermal_projected=C/P*(R-chi*val['Ue'])
    thermal=val['thermal'].intersect(thermal_projected)
    particle=val['particle']
    if UT.hi>=0 or thermal.hi>=0 or particle.hi>=0:
        raise ValueError('cooling sign could not be certified')
    # Monotonic positive expression; also bounds the positive-weighted integral ratio.
    share=I(w.lo/(eff.hi*P.hi+w.lo),w.hi/(eff.lo*P.lo+w.hi))
    WTe=read_i(d['temperature_mixed_K'])
    if WTe.lo<=0:raise ValueError('retained mixed temperature is not strictly positive')
    Db0=UT-WTe
    suppression=WTe/(-UT)
    eta=I(suppression.lo/(1+suppression.lo),suppression.hi/(1+suppression.hi))
    # A diagnostic readout transformation: source equations/root family stay fixed.
    offset,bridge=readout_bridge(g,U,f,fh,C)
    e_bridge=(f-fh)*(U[1]+2*U[2])
    # New simple physical companion: kinetic pressure/nH=(2/3)w in eV/H.
    pressure=Q(2,3)*U[3]
    We=W[0]+fh*(W[1]+2*W[2])
    Ve=V[0]+fh*(V[1]+2*V[2])
    vT=value_and_lambda(g,V,fh,C)['UT']
    if not (Ve.lo>0 and V[3].lo>0):
        raise ValueError('birth energy/electron response prerequisite not positive')
    birth_energy=V[3]/Ve
    mean_thermal=w/P
    if not (birth_energy.hi<mean_thermal.lo and vT.hi<0):
        raise ValueError('birth particle dilution criterion not certified')
    return {
      'stage':name,'dt_s':int(dt),'lambda_path':[0,1],'b_amp':1,
      'chronology':'separate first stage from the same COMMON',
      'constants':{'nH_cm3':packed(nH),'nHe_cm3':packed(nHe),'f':packed(f),'fhat':packed(fh),
                   'f_minus_fhat':packed(f-fh),'C_T_K_per_eV':packed(C),'chiH_eV':packed(chi)},
      'root_image':{'coordinates':['x_HII','y_HeII','y_HeIII','w_eV_per_H'],
                    'intervals':[packed(v) for v in g],
                    'method':'retained gc +/- (beta + B r); no root iteration'},
      'value_readouts':{'electron_fraction':packed(val['e']),'particles_per_H':packed(P),'temperature_K':packed(val['T'],'K')},
      'finite_HH_response':{
        'electron_fraction':packed(val['Ue'],'electrons/H'),
        'electron_density_cm3':packed(nH*val['Ue'],'cm^-3'),
        'temperature_K':packed(UT,'K'),
        'thermal_part_K':packed(thermal,'K'),
        'particle_part_K':packed(particle,'K'),
        'particle_fraction_of_cooling':packed(share,'dimensionless'),
        'thermal_fraction_of_cooling':packed(1-share,'dimensionless'),
        'effective_energy_eV_per_electron':packed(eff,'eV/electron'),
        'gas_energy_eV_per_H':packed(Eg,'eV/H'),
        'pressure_per_nH_eV':packed(pressure,'eV'),
        'temperature_b0_K':packed(Db0,'K')},
      'energy_correlation':{'projected_first_energy':packed(Eprojected),'direct_first_energy':packed(Edirect),
                            'Uw_plus_chi_Ue':packed(R),'UT_direct':packed(val['UT']),
                            'UT_projected':packed(UT_projected)},
      'birth_and_mixed':{'temperature_mixed_K_REUSED_PHYS09':packed(WTe,'K'),
                         'electron_mixed_NEW_LINEAR_READOUT':packed(We,'electrons/H'),
                         'temperature_suppression_relative_to_b1':packed(suppression,'dimensionless'),
                         'temperature_suppression_relative_to_b0':packed(eta,'dimensionless'),
                         'birth_only_electron_response':packed(Ve,'electrons/H'),
                         'birth_only_temperature_response_K':packed(vT,'K'),
                         'birth_only_thermal_energy_response':packed(V[3],'eV/H'),
                         'birth_energy_per_extra_electron':packed(birth_energy,'eV/electron'),
                         'mean_thermal_energy_per_particle':packed(mean_thermal,'eV/particle'),
                         'birth_path':{'b_path':[0,1],'fixed_lambda':'any lambda in [0,1]',
                                       'criterion':'Vw/Ve < w/P implies Tb < 0'}},
      'normalization_readout_bridge':{'definition':'same gas family T_f - T_fhat; no change to source',
                                     'pointwise_temperature_offset_K':packed(offset,'K'),
                                     'finite_HH_temperature_difference_K':packed(bridge,'K'),
                                     'finite_HH_temperature_abs_bound_K':packed(bridge.mag(),'K'),
                                     'finite_electron_readout_difference':packed(e_bridge,'electrons/H')},
      'inherited_premises':['fixed same-alpha source family','whole-box energy/source inclusion',
                            'PHYS09 uniform C2 root and exact response bounds'],
      'new_native_root_or_source_calls':0,
      'actual_corners_evaluated':False,
    }


def compact_result(row):
    return {key:{k:v['outward_decimal'] for k,v in row[key].items() if isinstance(v,dict) and 'outward_decimal' in v}
            for key in ['value_readouts','finite_HH_response','birth_and_mixed','normalization_readout_bridge']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU,(45,45))
    resource.setrlimit(resource.RLIMIT_AS,(384*1024**2,384*1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024**2,32*1024**2))
    started=time.perf_counter();root=Path(__file__).resolve().parents[1]
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False)
    source=root/'inputs/phys09/PROJECTED_RESULTS.json'
    inp=json.loads(source.read_text())
    leaves_path=root/'inputs/ncp07/results/full/NATIVE_CONSTANT_LEAVES.json'
    leaves=json.loads(leaves_path.read_text())
    leaf_hash=hashlib.sha256(leaves_path.read_bytes()).hexdigest()
    for d in inp['details']:
        expected=next(e for e in d['input_exports'] if e['path'].endswith('/NATIVE_CONSTANT_LEAVES.json'))
        if leaf_hash!=expected['sha256']:raise ValueError('captured constant identity mismatch')
    cases=semantic_cases()
    details={d['stage']:d for d in inp['details']}
    rows=[stage_result(root,s,details[s['stage']],leaves) for s in inp['stages']]
    result={'schema':'WU088_HH_PHYS13_THERMO_RESPONSE_V1','arithmetic':'exact Fraction; outward decimal display at 10 significant digits',
            'source_projected_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'rows':rows,'semantic_cases':cases,'scientific_cases':2,
            'native_authority':False,'matched_history':False,'source_family_changed':False,
            'consumer_bound':False,'global_nodes_newly_completed':[],
            'new_source_evaluations':0,'new_root_solves':0,'NCP_jobs':0}
    (out/'THERMO_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    summary={'stages':{r['stage']:compact_result(r) for r in rows},'semantic_cases':cases,
             'elapsed_wall_s':time.perf_counter()-started,'max_rss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (out/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
