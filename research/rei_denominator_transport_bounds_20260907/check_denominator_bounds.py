#!/usr/bin/env python3
"""Exact research-only denominator checks. No production imports or atomic rates."""
from fractions import Fraction as F
from dataclasses import dataclass
from itertools import permutations, combinations
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HELPER = HERE.parent/'rei_thermochemistry_error_transport_20260907/verify_bounds.py'
EXPECTED_HELPER = 'f7b7d7e474ee5877c223ef8ccd5b78659dc2214b0002ea11b247607b3dacaf6b'
if hashlib.sha256(HELPER.read_bytes()).hexdigest() != EXPECTED_HELPER:
    raise RuntimeError('RESEARCH_HELPER_SOURCE_DRIFT')
spec = importlib.util.spec_from_file_location('existing_fraction_reference', HELPER)
alg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alg)
EDGES = ((1,0),(0,1),(3,2),(2,3),(4,3),(3,4))
BLOCKS = ((0,1),(2,3,4))
OMIT_DENOMINATOR = False


def exact(x):
    if type(x) not in (int,F):
        raise ValueError('EXACT_RATIONAL_REQUIRED')
    return F(x)


def vector(v):
    if len(v) != 5:
        raise ValueError('FIVE_SPECIES_REQUIRED')
    return [exact(x) for x in v]


def flux(values):
    if len(values) != 6:
        raise ValueError('SIX_EDGES_REQUIRED')
    out = [[F(0)]*5 for _ in range(5)]
    for (i,j),v in zip(EDGES,values):
        out[i][j] = exact(v)
    return out


def validate(f,b,d,h):
    b,d,h = vector(b),vector(d),exact(h)
    if h<0 or any(x<=0 for x in b+d):
        raise ValueError('POSITIVE_DOMAIN_REQUIRED')
    if len(f)!=5 or any(len(row)!=5 for row in f):
        raise ValueError('FIVE_SPECIES_REQUIRED')
    f = [[exact(x) for x in row] for row in f]
    if any(f[i][j]<0 or (f[i][j]!=0 and (i,j) not in EDGES)
           for i in range(5) for j in range(5)):
        raise ValueError('H_HE_TRANSFER_GRAPH_REQUIRED')
    return f,b,d,h


def gen(f,d):
    a = [[f[i][j]/d[j] for j in range(5)] for i in range(5)]
    for j in range(5):
        a[j][j] = -sum(a[i][j] for i in range(5) if i!=j)
    return a


def add(a,b):
    return [x+y for x,y in zip(a,b)]


def sub(a,b):
    return [x-y for x,y in zip(a,b)]


def solve(f,b,d,h):
    f,b,d,h = validate(f,b,d,h)
    p = alg.resolvent(gen(f,d),h)
    return alg.mv(p,b),p


def jvp(f,b,d,h,db,dd):
    db,dd = vector(db),vector(dd)
    x,p = solve(f,b,d,h)
    direct = alg.mv(p,db)
    if OMIT_DENOMINATOR:
        return x,direct,p
    relative = [xj*dj/den for xj,dj,den in zip(x,dd,d)]
    return x,add(direct,alg.mv(alg.minus(alg.eye(5),p),relative)),p


def average(f,g):
    return [[(x+y)/2 for x,y in zip(fr,gr)] for fr,gr in zip(f,g)]


def stages(f0,f1,b,h,db):
    yp,dyp,pp = jvp(f0,b,b,h,db,db)
    yc,dyc,pc = jvp(average(f0,f1),b,yp,h,db,dyp)
    return yp,yc,dyp,dyc,pp,pc


def bn(v):
    return max(sum(abs(v[j]) for j in block) for block in BLOCKS)


def kappa(p):
    return 2*max(1-p[j][j] for j in range(5))


def kbound(f,d,h):
    return 2*max(h*sum(f[i][j] for i in range(5)) /
                 (d[j]+h*sum(f[i][j] for i in range(5))) for j in range(5))


def constants():
    m0,tmax,qmax = F(1,6),F(1,8),F(1,8)
    kp=2*tmax*qmax/(m0+tmax*qmax)
    mp=m0/(1+tmax*qmax/m0)
    kc=2*tmax*qmax/(mp+tmax*qmax)
    kg=2*(tmax/3)*qmax/(m0+(tmax/3)*qmax)
    gp=1+kp/(2*m0)
    beta=kc/(2*mp)
    return dict(m0=m0,tmax=tmax,qmax=qmax,kp=kp,mp=mp,kc=kc,kg=kg,
                Gp=gp,Gg=1+kg/(2*m0),beta=beta,Gc=1+beta*gp)


@dataclass(frozen=True)
class Dual:
    v: F
    t: F = F(0)
    def __post_init__(self):
        object.__setattr__(self,'v',exact(self.v))
        object.__setattr__(self,'t',exact(self.t))
    @staticmethod
    def lift(x):
        return x if isinstance(x,Dual) else Dual(exact(x))
    def __add__(self,other):
        o=self.lift(other); return Dual(self.v+o.v,self.t+o.t)
    __radd__=__add__
    def __neg__(self):
        return Dual(-self.v,-self.t)
    def __sub__(self,other):
        return self+-self.lift(other)
    def __rsub__(self,other):
        return self.lift(other)+-self
    def __mul__(self,other):
        o=self.lift(other); return Dual(self.v*o.v,self.t*o.v+self.v*o.t)
    __rmul__=__mul__
    def __truediv__(self,other):
        o=self.lift(other)
        if not o.v: raise ValueError('DUAL_ZERO_DENOMINATOR')
        return Dual(self.v/o.v,(self.t*o.v-self.v*o.t)/(o.v*o.v))
    def __rtruediv__(self,other):
        return self.lift(other)/self


def determinant(a):
    out=Dual(0)
    for perm in permutations(range(len(a))):
        inv=sum(perm[i]>perm[j] for i in range(len(a)) for j in range(i+1,len(a)))
        term=Dual(-1 if inv%2 else 1)
        for i,j in enumerate(perm): term=term*a[i][j]
        out=out+term
    return out


def cramer(f,b,d,h):
    # Independent primal algebra: separate 2x2/3x3 Cramer solves over duals.
    out=[None]*5
    for ids in BLOCKS:
        a=[]
        for i in ids:
            row=[]
            for j in ids:
                outgoing=sum(f[k][j] for k in ids if k!=j)
                row.append(1+h*outgoing/d[j] if i==j else -h*f[i][j]/d[j])
            a.append(row)
        det=determinant(a)
        for col,j in enumerate(ids):
            replaced=[[b[ids[i]] if k==col else a[i][k]
                       for k in range(len(ids))] for i in range(len(ids))]
            out[j]=determinant(replaced)/det
    return out


def fixtures():
    b=list(map(F,[F(1,2),F(1,2),F(1,3),F(1,3),F(1,3)]))
    f0=flux([F(1,16),F(1,32),F(1,64),F(1,16),F(1,32),F(1,64)])
    f1=flux([F(1,32),F(1,16),F(1,16),F(1,64),F(1,64),F(1,32)])
    db=[F(1,10),F(-1,10),F(1,20),F(-1,20),F(0)]
    return f0,f1,b,F(1,8),db


def parents():
    return [[F(1,4),F(3,4),F(1,6),F(1,6),F(2,3)],
            [F(3,4),F(1,4),F(2,3),F(1,6),F(1,6)],
            [F(1,2),F(1,2),F(1,3),F(1,3),F(1,3)]]


class Checks(unittest.TestCase):
    def test_D01_selected_source_links(self):
        binding=HERE.parent/'rei_population_stage_mapping_20260907/SOURCE_BINDINGS.json'
        rows=json.loads(binding.read_text())['files']
        names={'mprk22.py','evaluation_site_trial.py','uncertainty_trial.py','event_uncertainty_operator.py'}
        chosen=[r for r in rows if Path(r['path']).name in names]
        self.assertEqual(len(chosen),4)
        for r in chosen:
            self.assertEqual(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest(),r['sha256'])
        self.assertEqual(hashlib.sha256(HELPER.read_bytes()).hexdigest(),EXPECTED_HELPER)

    def test_D02_solved_cancellation(self):
        f0,_,b,h,db=fixtures(); d=list(map(F,[2,3,4,5,6])); dd=[F(1),F(-1),F(2),F(-2),F(1)]
        x,dx,p=jvp(f0,b,d,h,db,dd)
        a=gen(f0,d); da=[[-a[i][j]*dd[j]/d[j] for j in range(5)] for i in range(5)]
        direct=alg.mv(p,add(db,alg.mv(alg.times(h,da),x)))
        self.assertEqual(dx,direct)
        for ids in BLOCKS: self.assertEqual(sum(dx[j] for j in ids),sum(db[j] for j in ids))

    def test_D03_independent_dual_cramer(self):
        f0,_,b,h,db=fixtures(); d=list(map(F,[2,3,4,5,6])); dd=[F(1),F(-1),F(2),F(-2),F(1)]
        x,dx,_=jvp(f0,b,d,h,db,dd)
        ref=cramer(f0,[Dual(v,t) for v,t in zip(b,db)],
                   [Dual(v,t) for v,t in zip(d,dd)],h)
        self.assertEqual(x,[z.v for z in ref])
        self.assertEqual(dx,[z.t for z in ref])

    def test_D04_finite_pair_identity(self):
        f0,_,b,h,_=fixtures(); c=parents()[0]
        d=list(map(F,[2,3,4,5,6])); e=list(map(F,[3,2,5,4,7]))
        x,p=solve(f0,b,d,h); z,_=solve(f0,c,e,h)
        rhs=add(alg.mv(p,sub(b,c)),alg.mv(alg.minus(alg.eye(5),p),
                [(dj/ej-1)*zj for dj,ej,zj in zip(d,e,z)]))
        self.assertEqual(sub(x,z),rhs)
        self.assertLessEqual(bn(sub(x,z)),bn(sub(b,c))+kappa(p)*max(abs(dj/ej-1) for dj,ej in zip(d,e)))

    def test_D05_weighted_kappa(self):
        f0,_,b,_,_=fixtures(); w=[F(2),F(2),F(3),F(3),F(3)]
        for h in [F(0),F(1,8),F(1000)]:
            _,p=solve(f0,b,b,h)
            self.assertEqual(alg.opnorm1(alg.conjugate(alg.minus(alg.eye(5),p),w)),kappa(p))
            self.assertLessEqual(kappa(p),kbound(f0,b,h))
            self.assertLessEqual(kappa(p),2)

    def test_D06_rare_denominator_cancellation(self):
        _,_,b,_,_=fixtures(); f=flux([1,0,0,0,0,0])
        for eps in [F(1,100),F(1,10**8),F(1,10**20)]:
            d=[eps,F(1),F(1),F(1),F(1)]
            _,dx,_=jvp(f,b,d,F(1),[F(0)]*5,[eps,F(0),F(0),F(0),F(0)])
            self.assertEqual(bn(dx),eps/(1+eps)**2)
            self.assertLessEqual(bn(dx),F(1,4))
            self.assertGreater(2/eps,100)

    def test_D07_nested_corrector_derivative_and_mutants(self):
        f0,f1,b,h,db=fixtures()
        yp,yc,dyp,dyc,_,pc=stages(f0,f1,b,h,db)
        bd=[Dual(v,t) for v,t in zip(b,db)]
        pd=cramer(f0,bd,bd,h)
        cd=cramer(average(f0,f1),bd,pd,h)
        self.assertEqual(yp,[z.v for z in pd]); self.assertEqual(dyp,[z.t for z in pd])
        self.assertEqual(yc,[z.v for z in cd]); self.assertEqual(dyc,[z.t for z in cd])
        self.assertNotEqual(dyc,alg.mv(pc,db))  # missing predictor-denominator term
        self.assertNotEqual(yc,alg.mv(pc,yp))  # wrong corrector RHS
        self.assertNotEqual(dyc,alg.mv(pc,dyp)) # wrong composed derivative

    def test_D08_uniform_box_constants(self):
        c=constants()
        expected={'mp':F(16,105),'kp':F(6,35),'kc':F(210,1129),'kg':F(2,33),
                  'Gp':F(53,35),'Gg':F(13,11),'beta':F(11025,18064),'Gc':F(34759,18064)}
        for key,val in expected.items(): self.assertEqual(c[key],val)
        self.assertGreater(F(1,2),F(4,9)) # proves actual gamma < 1/3
        self.assertLess(F(1,2),1)        # proves actual gamma > 0

    def test_D09_box_sample_sanity(self):
        f0,f1,_,_,_=fixtures(); c=constants()
        directions=[[F(1),F(-1),F(0),F(0),F(0)],
                    [F(0),F(0),F(1),F(-1),F(0)],
                    [F(0),F(0),F(0),F(1),F(-1)]]
        families=[(f0,f1),(flux([F(1,16)]*6),flux([0]*6)),(flux([0]*6),flux([F(1,16)]*6))]
        for fa,fb in families:
            for b in parents():
                for h in [F(1,16),F(1,8)]:
                    for db in directions:
                        yp,yc,dp,dc,pp,pc=stages(fa,fb,b,h,db)
                        self.assertGreaterEqual(min(yp),c['mp'])
                        self.assertLessEqual(kappa(pp),c['kp']); self.assertLessEqual(kappa(pc),c['kc'])
                        self.assertLessEqual(bn(dp),c['Gp']*bn(db)); self.assertLessEqual(bn(dc),c['Gc']*bn(db))
                        # h/3 is the upper endpoint enclosure, not gamma substituted in the method.
                        _,dg,_=jvp(fa,b,b,h/3,db,db)
                        self.assertLessEqual(bn(dg),c['Gg']*bn(db))
                        for ids in BLOCKS:
                            self.assertEqual(sum(yc[j] for j in ids),1)
                            self.assertEqual(sum(dc[j] for j in ids),0)

    def test_D10_finite_stage_pair_bound(self):
        fa,fb,_,_,_=fixtures(); c=constants()
        for b,e in combinations(parents(),2):
            for h in [F(1,16),F(1,8)]:
                p,x,*_=stages(fa,fb,b,h,[F(0)]*5)
                q,z,*_=stages(fa,fb,e,h,[F(0)]*5)
                self.assertLessEqual(bn(sub(p,q)),c['Gp']*bn(sub(b,e)))
                self.assertLessEqual(bn(sub(x,z)),c['Gc']*bn(sub(b,e)))

    def test_D11_zero_step_and_zero_flux(self):
        f0,_,b,h,db=fixtures()
        for f,t in [(f0,F(0)),(flux([0]*6),h)]:
            x,dx,p=jvp(f,b,b,t,db,[F(7)]*5)
            self.assertEqual(x,b); self.assertEqual(dx,db); self.assertEqual(kappa(p),0)

    def test_D12_invalid_research_domain(self):
        f0,_,b,h,_=fixtures()
        for t in [F(-1),True,0.1]:
            with self.assertRaises(ValueError): solve(f0,b,b,t)
        bad=b.copy(); bad[0]=F(0)
        with self.assertRaises(ValueError): solve(f0,b,bad,h)
        badf=[row.copy() for row in f0]; badf[2][0]=F(1)
        with self.assertRaisesRegex(ValueError,'TRANSFER_GRAPH'): solve(badf,b,b,h)
        badf=flux([-1,0,0,0,0,0])
        with self.assertRaises(ValueError): solve(badf,b,b,h)
        with self.assertRaises(ValueError): solve(f0,b[:-1],b,h)


class Recorded(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); self.outcomes=[]
    def addSuccess(self,test):
        super().addSuccess(test); self.outcomes.append({'id':test.id(),'outcome':'PASS'})
    def addFailure(self,test,err):
        super().addFailure(test,err); self.outcomes.append({'id':test.id(),'outcome':'FAIL'})
    def addError(self,test,err):
        super().addError(test,err); self.outcomes.append({'id':test.id(),'outcome':'ERROR'})


def main():
    global OMIT_DENOMINATOR
    ap=argparse.ArgumentParser()
    ap.add_argument('--report',required=True)
    ap.add_argument('--mutant',choices=['omit-denominator'])
    args=ap.parse_args()
    OMIT_DENOMINATOR=args.mutant is not None
    if OMIT_DENOMINATOR:
        suite=unittest.TestSuite([Checks('test_D03_independent_dual_cramer')]); expected=1
    else:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks); expected=12
    ids=[t.id() for t in suite]
    result=unittest.TextTestRunner(verbosity=2,resultclass=Recorded).run(suite)
    ok=result.wasSuccessful() and result.testsRun==expected and not result.skipped and len(set(ids))==expected
    report={'status':'PASS_DENOMINATOR_RESEARCH_CHECKS' if ok else 'FAIL_DENOMINATOR_RESEARCH_CHECKS',
            'hypothesis':'OMITTED_DENOMINATOR_MUTANT' if OMIT_DENOMINATOR else 'EXACT_SOLVED_DENOMINATOR',
            'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
            'test_ids':ids,'outcomes':result.outcomes,'box_constants':{k:str(v) for k,v in constants().items()},
            'box_kind':'DECLARED_ALGEBRAIC_CONTINUUM_NOT_PHYSICAL_REI_ENVELOPE',
            'flux_numerators_differentiated':False,'physical_flux_bounds':'UNKNOWN',
            'thermal_coupled_bound':'UNKNOWN','exact_flow_rho':'UNKNOWN',
            'production_imports':False,'production_replay':False,'first_interval_admitted':False,
            'runtime_authority_effect':'NONE','gamma_execution':'ANALYTIC_GAMMA_LT_ONE_THIRD_ONLY',
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':sys.version}
    with Path(args.report).open('x',encoding='utf-8') as out:
        json.dump(report,out,indent=2,sort_keys=True); out.write('\n')
    print(json.dumps(report,sort_keys=True))
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
