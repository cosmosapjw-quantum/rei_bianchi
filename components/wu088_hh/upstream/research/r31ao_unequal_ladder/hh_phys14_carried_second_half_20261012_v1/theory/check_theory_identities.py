#!/usr/bin/env python3
"""Exact-rational semantic checks of PHYS14 derived identities.

This is a small derivation check, not an NCP/native/history execution.  The
remap case reuses captured energy nodes but uses a declared rational toy rho.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import struct
import time

BASE = Path('/workspace/scratch/b826cbaab54f/phys14_intake/ncp07/HH_PHYS07_NCP_LOCAL_20261011_v1')
OUT = Path('/workspace/scratch/b826cbaab54f/phys14_theory')

def exact_word(word):
    return F.from_float(struct.unpack('>d', bytes.fromhex(word))[0])

def add(a, b):
    return [x+y for x,y in zip(a,b)]

def scale(c, v):
    return [c*x for x in v]

def mm(A, B):
    return [[sum((a*b for a,b in zip(row,col)),F(0)) for col in zip(*B)] for row in A]

def eye(n):
    return [[F(i==j) for j in range(n)] for i in range(n)]

def hat_column(energies, rho, j):
    x = energies[j]*rho
    ret = [F(0)]*len(energies)
    if x < energies[0]:
        return ret
    if x >= energies[-1]:
        ret[-1] = F(1)
        return ret
    for k in range(1,len(energies)):
        if energies[k-1] <= x <= energies[k]:
            t = (x-energies[k-1])/(energies[k]-energies[k-1])
            ret[k-1], ret[k] = 1-t,t
            return ret
    raise AssertionError('hat branch not assigned')

def remap(energies, rho, values):
    ret = [F(0)]*len(energies)
    for j,n in enumerate(values):
        ret=add(ret,scale(n,hat_column(energies,rho,j)))
    return ret

def jet_mul(a,b):
    x,u,v,w=a; y,s,t,z=b
    return (x*y,u*y+x*s,v*y+x*t,w*y+u*t+v*s+x*z)

def jet_recip(a):
    x,u,v,w=a
    return (1/x,-u/x**2,-v/x**2,2*u*v/x**3-w/x**2)

def jet_add(a,b):
    return tuple(x+y for x,y in zip(a,b))

def main():
    started=time.perf_counter()
    src=BASE/'results/full/SOURCE_BOX.json'
    raw=src.read_bytes(); data=json.loads(raw)
    E=[exact_word(x) for x in data['energy_bits']]
    records=[]

    # Distinct ray distributions and signed derivative carry use one denominator.
    rays=[(F(2),F(1,3),F(-2,7),F(1,13)),
          (F(3),F(-1,5),F(4,7),F(-1,19)),
          (F(5),F(3,11),F(1,3),F(1,17))]
    denom=(F(7,5),F(-1,9),F(-1,8),F(2,11))
    total=tuple(sum((r[k] for r in rays),F(0)) for k in range(4))
    rhs=jet_mul(total,jet_recip(denom))
    lhs=tuple(sum((jet_mul(r,jet_recip(denom))[k] for r in rays),F(0)) for k in range(4))
    assert lhs==rhs
    records.append({'case':'joint ray/group quotient closure', 'status':'PASS',
                    'slots':['value','lambda','b','lambda_b']})

    # First sensitivity includes inherited reservoir and opacity response.
    N=(F(2),F(1,17),F(1,11),F(1,19))
    x=(F(2,3),F(1,7),F(1,13),F(1,23))
    h=F(2,5); a=F(3,7)
    D=(1+h*a*(1-x[0]),-h*a*x[1],-h*a*x[2],-h*a*x[3])
    actual=jet_mul(N,jet_recip(D))
    assert actual[1]==N[1]/D[0]+h*a*N[0]*x[1]/D[0]**2
    assert actual[2]==N[2]/D[0]+h*a*N[0]*x[2]/D[0]**2
    assert actual[1]>0 and actual[2]>0
    # The photon-temperature source is negative even for positive heat input.
    heat=F(1,10); w=F(13); Pi=F(2)
    p=a*(1-x[0])/D[0]
    direct_T=p/Pi*(heat-w/Pi)
    assert p*heat>0 and direct_T<0
    records.append({'case':'positive photon memory and direct thermal dilution', 'status':'PASS'})

    # Rank-one photo inverse is checked as an exact matrix identity.
    A0=[[F(2),F(1,5),F(0),F(0)], [F(0),F(3),F(0),F(0)],
        [F(0),F(0),F(4),F(0)], [F(0),F(0),F(0),F(5)]]
    B0=[[F(1,2),F(-1,30),F(0),F(0)], [F(0),F(1,3),F(0),F(0)],
        [F(0),F(0),F(1,4),F(0)], [F(0),F(0),F(0),F(1,5)]]
    assert mm(A0,B0)==eye(4)
    v=[F(2,3),F(0),F(0),F(1,7)]
    d=F(1,11)
    z=[r[0] for r in mm(B0,[[x] for x in v])]
    denom=1+d*z[0]
    B=[[B0[i][j]-d*z[i]*B0[0][j]/denom for j in range(4)] for i in range(4)]
    A=[[A0[i][j]+(d*v[i] if j==0 else 0) for j in range(4)] for i in range(4)]
    assert mm(A,B)==eye(4)
    records.append({'case':'rank-one photo resolvent with non-diagonal baseline', 'status':'PASS'})

    # Exact nonuniform-node refinement identity; rho is an explicit toy value.
    rho=1-F(1,160000)  # Not a claim to evaluate the physical exponential.
    checked=[]
    for j in (10,16,24):
        assert E[j-1] <= rho*E[j] <= E[j]
        assert E[j-1] <= rho*rho*E[j] <= E[j]
        assert E[j-2] <= rho*E[j-1] <= E[j-1]
        Delta=E[j]-E[j-1]; previous=E[j-1]-E[j-2]
        aj=(1-rho)*E[j]/Delta; ap=(1-rho)*E[j-1]/previous
        first=hat_column(E,rho,j)
        two=remap(E,rho,first); one=hat_column(E,rho*rho,j)
        diff=[u-v for u,v in zip(two,one)]
        expected=[F(0)]*len(E)
        expected[j]=aj*ap*previous/Delta
        expected[j-1]=-aj*ap*(1+previous/Delta)
        expected[j-2]=aj*ap
        assert diff==expected
        assert sum(diff,F(0))==0
        assert sum((e*x for e,x in zip(E,diff)),F(0))==0
        assert any(x!=0 for x in diff)
        checked.append({'node':j,'aj':float(aj),'aj_ap':float(aj*ap),
                        'nonzero_shape_defect':True,'number_defect_exact_zero':True,
                        'energy_defect_exact_zero':True})
    records.append({'case':'nonuniform spectral remap refinement', 'status':'PASS',
                    'rho':str(rho), 'rho_kind':'declared exact rational semantic example',
                    'columns':checked})

    # Source claims are observations of captured sigma words.
    sigma=[[exact_word(x) for x in r] for r in data['sigma_bits']]
    support=[[j for j in range(len(E)) if sigma[j][a]!=0] for a in range(3)]
    assert support==[list(range(16,33)),[],[]]
    result={'schema':'PHYS14_THEORY_EXACT_CHECKS_V1','status':'PASS',
            'scientific_native_or_history_runs':0,'cases':records,
            'case_count':len(records),'sigma_active_nodes_by_absorber':support,
            'source_path':str(src),'source_sha256':hashlib.sha256(raw).hexdigest(),
            'runtime_s':time.perf_counter()-started,
            'role':'candidate author semantic checks, not independent review'}
    (OUT/'THEORY_EXACT_CHECKS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'cases':len(records),'runtime_s':result['runtime_s']},ensure_ascii=False))

if __name__=='__main__':
    main()
