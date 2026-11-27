#!/usr/bin/env python3
"""Endpoint-free exact rational PHYS05 check. No root/IVP/native execution."""
from fractions import Fraction as Q
from pathlib import Path
from itertools import product
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'hh_phys04_ordered_quartic_20261010_v1'
INPUT_SHA = '26a340065a9a99d02903bf0cc008baaf6ade00d2e845beb9d2b0b7d801316494'
OWNER = '569b04cd71e45756e0fd476aef6643bd9434f4fa'
OWNER_PATH = 'research/r31ao_unequal_ladder/ncp_energy06e_certificate_20261010_v1/original_owner_dependency/src/coupled_primary.rs'
spec = importlib.util.spec_from_file_location('phys04_d2', BASE/'src/implicit_mixed.py')
ref = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ref
spec.loader.exec_module(ref)
D2 = ref.D2

def leaf(x):
    return Q.from_float(x) if isinstance(x, float) else Q(x)

def enc(x):
    if isinstance(x, Q): return {'numerator': str(x.numerator), 'denominator': str(x.denominator)}
    if isinstance(x, dict): return {str(k): enc(v) for k,v in x.items()}
    if isinstance(x, (list,tuple)): return [enc(v) for v in x]
    return x

class P:
    """Independent sparse ring Q[h,a,b]/(h^3,a^2,b^2)."""
    def __init__(self, x=0):
        self.c = {k: Q(v) for k,v in x.items() if v} if isinstance(x,dict) else ({(0,0,0):Q(x)} if x else {})
    @staticmethod
    def co(x): return x if isinstance(x,P) else P(x)
    def __add__(self,x):
        out=self.c.copy()
        for k,v in self.co(x).c.items(): out[k]=out.get(k,Q(0))+v
        return P(out)
    __radd__=__add__
    def __neg__(self): return P({k:-v for k,v in self.c.items()})
    def __sub__(self,x): return self+-self.co(x)
    def __rsub__(self,x): return self.co(x)+-self
    def __mul__(self,x):
        out={}
        for a,va in self.c.items():
            for b,vb in self.co(x).c.items():
                k=tuple(u+v for u,v in zip(a,b))
                if k[0]<=2 and k[1]<=1 and k[2]<=1: out[k]=out.get(k,Q(0))+va*vb
        return P(out)
    __rmul__=__mul__
    def __truediv__(self,x): return self*(1/Q(x))
    def at(self,h=0,a=0,b=0): return self.c.get((h,a,b),Q(0))

def add(*vs): return [sum(v[i] for v in vs) for i in range(len(vs[0]))]
def scale(c,v): return [c*x for x in v]
def dot(a,b): return sum((u*v for u,v in zip(a,b)),Q(0))

def run():
    raw=(BASE/'inputs/SELECTED_SOURCE.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==INPUT_SHA
    data=json.loads(raw)
    owner=subprocess.check_output(['git','show',OWNER+':'+OWNER_PATH],cwd=HERE)
    source=owner.decode()
    assert 'fn interval_rhs(' in source and 'let pk = jdiv(' in source
    g=list(map(leaf,data['old_gas'])); p=list(map(leaf,data['old_point_photons']))
    e=list(map(leaf,data['energies_ev'])); sig=[list(map(leaf,row)) for row in data['sigma_cm2']]
    fhe=leaf(data['f_he']); H=leaf(data['h_mean_per_s']); d=leaf(data['dt_s'])
    # Rust c_cm_s and CHI are immutable source leaves, not new physical inputs.
    constants=subprocess.check_output(['git','show',OWNER+':'+OWNER_PATH.replace('coupled_primary.rs','group_rates.rs')],cwd=HERE).decode()
    assert 'pub const C_LIGHT: f64 = 2.99792458e10;' in constants
    assert 'const CHI: [f64; 3] = [13.598_434_599_702, 24.587_389_011, 54.417_76];' in source
    c=leaf(2.99792458e10); density=leaf(data['n_h_cm3']); chi=list(map(leaf,[13.598434599702,24.587389011,54.41776]))
    assert all(row[1]==row[2]==0 for row in sig)
    assert all(all(s==0 for s in row) for row in sig[:16])
    rates=[H*e[j]/(e[j]-e[j-1]) for j in range(16,len(e))]
    def L(v):
        out=[0*v[0] for _ in v]
        for j in range(16,len(v)):
            out[j]=out[j]-rates[j-16]*v[j]
            if j>16: out[j-1]=out[j-1]+rates[j-16]*v[j]
        return out
    def low(z): return [1-z[0],fhe*(1-z[1]-z[2]),fhe*z[1]]
    def K(z,v):
        out=[0*z[0] for _ in range(4)]
        for E,s,stock in zip(e,sig,v):
            r=[c*density*l*t*stock for l,t in zip(low(z),s)]
            out[0]+=r[0]; out[1]+=(r[1]-r[2])/fhe; out[2]+=r[2]/fhe
            out[3]+=sum(t*(E-cut) for t,cut in zip(r,chi))
        return out
    def Kg(u,v):
        slopes=[-u[0],-fhe*(u[1]+u[2]),fhe*u[1]]
        out=[Q(0)]*4
        for E,s,stock in zip(e,sig,v):
            r=[c*density*l*t*stock for l,t in zip(slopes,s)]
            out[0]+=r[0]; out[1]+=(r[1]-r[2])/fhe; out[2]+=r[2]/fhe
            out[3]+=sum(t*(E-cut) for t,cut in zip(r,chi))
        return out
    rows=[]; checks=0
    def equal(name,candidate,oracle,details=None):
        nonlocal checks
        residual=[a-b for a,b in zip(candidate,oracle)]
        row={'name':name,'candidate':candidate,'oracle':oracle,'residual':residual}
        if details is not None: row['directions']=details
        rows.append(row); checks+=len(residual)
        if any(residual): raise AssertionError(name)
    # Enumerate every full gas/photon coordinate with both signed unit directions.
    dirs=[]
    for j in range(29):
        for s in (-1,1):
            u=[Q(0)]*4; v=[Q(0)]*25
            (u if j<4 else v)[j if j<4 else j-4]=Q(s)
            dirs.append((j,s,u,v))
    for ja,sa,U,pa in dirs:
        for jb,sb,V,pb in dirs:
            terms=[K(g,L([Q(0)]*25)),Kg([Q(0)]*4,L(p)),Kg(U,L(pb)),Kg(V,L(pa))]
            candidate=scale(-Q(1,4),add(*terms))
            gp=[P({(0,0,0):z,(0,1,0):u,(0,0,1):v}) for z,u,v in zip(g,U,V)]
            pp=[P({(0,0,0):z,(0,1,0):u,(0,0,1):v}) for z,u,v in zip(p,pa,pb)]
            oracle=[-z.at(0,1,1)/4 for z in K(gp,L(pp))]
            equal('four_term_signed_basis',candidate,oracle,[ja,sa,jb,sb])
    # Mixed input directions isolate the first two terms, independent of U,V.
    for j,s,W,Wp in dirs:
        terms=[K(g,L(Wp)),Kg(W,L(p)),[Q(0)]*4,[Q(0)]*4]
        gp=[P({(0,0,0):z,(0,1,1):v}) for z,v in zip(g,W)]
        pp=[P({(0,0,0):z,(0,1,1):v}) for z,v in zip(p,Wp)]
        equal('mixed_input_direction',scale(-Q(1,4),add(*terms)),[-z.at(0,1,1)/4 for z in K(gp,L(pp))],[j,s])
    U=[Q(1),Q(-1),Q(1),Q(-1)]; V=scale(-1,U); W=U
    pa=[Q((-1)**j) for j in range(25)]; pb=scale(-1,pa); Wp=pa
    terms=[K(g,L(Wp)),Kg(W,L(p)),Kg(U,L(pb)),Kg(V,L(pa))]
    gp=[P({(0,0,0):z,(0,1,0):u,(0,0,1):v,(0,1,1):w}) for z,u,v,w in zip(g,U,V,W)]
    pp=[P({(0,0,0):z,(0,1,0):u,(0,0,1):v,(0,1,1):w}) for z,u,v,w in zip(p,pa,pb,Wp)]
    equal('four_terms_simultaneous',scale(-Q(1,4),add(*terms)),[-z.at(0,1,1)/4 for z in K(gp,L(pp))])
    equal('zero_incoming_entire_family',scale(-Q(1,4),add(K(g,L([Q(0)]*25)),Kg(W,L([Q(0)]*25)),Kg(U,L([Q(0)]*25)),Kg(V,L([Q(0)]*25)))),[Q(0)]*4)
    # Affinity gives Kgg=0, checked directly in the independent dual ring.
    for _,_,U,_ in dirs[:8]:
        for _,_,V,_ in dirs[:8]:
            gp=[P({(0,0,0):z,(0,1,0):u,(0,0,1):v}) for z,u,v in zip(g,U,V)]
            equal('Kgg_zero',[z.at(0,1,1) for z in K(gp,p)],[Q(0)]*4)
    # Direct formal BE substitution (two Picard substitutions suffice through h²).
    # Nuisance gas-only polynomials stand for algebraic jets, not FT03/HH evaluations.
    def rhs(z,q,gas_only):
        photo=K(z,q)
        if gas_only:
            ft=[z[0]*z[0]+z[1],z[1]*z[2],z[2]*z[2],z[3]*z[0]]
            hh=z[0]*z[0]*(1+z[3]); photo=add(photo,ft,[hh,0,0,-chi[0]*hh])
        photon=[-c*density*sum(l*t for l,t in zip(low(z),s))*v for s,v in zip(sig,q)]
        return photo,photon
    h=P({(1,0,0):1})
    def step(z,q,t,transport,gas_only):
        incoming=add(q,scale(t,L(q))) if transport else q
        zg,qg=z,incoming
        for _ in range(2):
            f,fp=rhs(zg,qg,gas_only)
            zg,qg=add(z,scale(t,f)),add(incoming,scale(t,fp))
        return zg,qg
    direct=[]
    for label,stock in [('selected',p),('zero',[Q(0)]*25)]:
        z=list(map(P,g)); q=list(map(P,stock))
        coefficients=[]
        for nuisance in (False,True):
            defects=[]
            for transport in (False,True):
                full,_=step(z,q,h,transport,nuisance)
                half,qhalf=step(z,q,h/2,transport,nuisance)
                two,_=step(half,qhalf,h/2,transport,nuisance)
                defects.append([b-a for a,b in zip(full,two)])
            isolated=[b-a for a,b in zip(*defects)]
            equal('direct_h1_cancellation',[v.at(1) for v in isolated],[Q(0)]*4)
            equal('direct_two_step_photo_h2',[v.at(2) for v in isolated],scale(-Q(1,4),K(g,L(stock))))
            coefficients.append([v.at(2) for v in isolated])
        equal('gas_only_FT03_HH_jet_cancellation',*coefficients)
        direct.append({'stock':label,'isolated_h2':coefficients[0]})
    # Exact PHYS04 D2 reduced-photo quotient arithmetic; no use of its solver.
    quotient=[]
    for j,(E,s,N) in enumerate(zip(e,sig,p)):
        kap=c*density*dot(low(g),s); D=1+d*kap
        assert D>0
        for a,b in product(range(4),repeat=2):
            U=[Q(int(i==a)) for i in range(4)]; V=[Q(int(i==b)) for i in range(4)]
            ku=c*density*dot([-U[0],-fhe*(U[1]+U[2]),fhe*U[1]],s)
            kv=c*density*dot([-V[0],-fhe*(V[1]+V[2]),fhe*V[1]],s)
            z=[D2(v,u,w) for v,u,w in zip(g,U,V)]
            kval=K(g,[Q(int(i==j)) for i in range(25)])
            ka=Kg(U,[Q(int(i==j)) for i in range(25)])
            kb=Kg(V,[Q(int(i==j)) for i in range(25)])
            slots=[D2(v,u,w)/(1+d*D2(kap,ku,kv)) for v,u,w in zip(kval,ka,kb)]
            first=[u/D-d*v*ku/D**2 for v,u in zip(kval,ka)]
            second=[-d*(u*kv+w*ku)/D**2+2*d*d*v*ku*kv/D**3 for v,u,w in zip(kval,ka,kb)]
            equal('quotient_first',[v.a for v in slots],first,[j,a,b])
            equal('quotient_hessian',[v.ab for v in slots],second,[j,a,b])
            stock_slots=[D2(v,u,0)/(1+d*D2(kap,ku,0))*D2(Q(0),0,Q(1)) for v,u in zip(kval,ka)]
            equal('zero_stock_gas_photon_cross',[v.ab for v in stock_slots],first,[j,a,b])
        A=c*density*s[0]; x=D2(g[0],Q(1),Q(1))
        hi=N*A*(1-x)/(1+d*A*(1-x))
        equal('HI_second_derivative',[hi.ab],[-2*N*d*A*A/(1+d*A*(1-g[0]))**3],[j])
        quotient.append({'node':j,'D':D,'opacity':kap,'HI_hessian':hi.ab,'inactive':not any(s)})
    result={'status':'EXACT_COMPONENT_CHECK_PASS','tolerance':0,'scalar_equalities':checks,'signed_directions':len(dirs),'checks':rows,'direct_photo':direct,'quotient_nodes':quotient,'selected_source_sha256':INPUT_SHA,'owner_commit':OWNER,'owner_path':OWNER_PATH,'owner_source_sha256':hashlib.sha256(owner).hexdigest(),'source_lines':[463,524],'claim':'endpoint-free local component identities only','root_certificate':False,'W_observed':False,'tube_observed':False,'native_runs':0,'root_runs':0,'IVP_runs':0,'history_runs':0,'atomic_runs':0,'old_suite_runs':0}
    return result

if __name__=='__main__':
    start=time.monotonic()
    try:
        result=run()
        result['wall_seconds']=time.monotonic()-start
        target=HERE/'EXACT_CHECK_FIRST.json'
        with target.open('x') as f: json.dump(enc(result),f,indent=2); f.write('\n')
        print(json.dumps({k:result[k] for k in ('status','scalar_equalities','signed_directions','wall_seconds')}))
    except Exception:
        traceback.print_exc()
        with (HERE/'FIRST_FAILURE.json').open('x') as f: json.dump({'status':'FIRST_FAILURE','traceback':traceback.format_exc(),'wall_seconds':time.monotonic()-start},f,indent=2)
        raise SystemExit(1)
