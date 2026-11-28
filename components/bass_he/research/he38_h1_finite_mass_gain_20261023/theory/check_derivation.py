#!/usr/bin/env python3
"""Affected HE38 finite-mass gain controls; no existing source/suite replay."""
from pathlib import Path
from fractions import Fraction as F
import datetime, hashlib, itertools, json, math, resource, sys, time
import mpmath as mp

ROOT=Path(__file__).resolve().parent
START=time.perf_counter()
STAMP=datetime.datetime.now(datetime.timezone.utc).isoformat()
ZERO=(0,)*6

def pconst(c):return {ZERO:F(c)} if c else {}
def pvar(i):
    e=[0]*6;e[i]=1;return {tuple(e):F(1)}
def padd(*ps):
    r={}
    for p in ps:
        for e,c in p.items():r[e]=r.get(e,F(0))+c
    return {e:c for e,c in r.items() if c}
def pscale(p,c):return {e:v*c for e,v in p.items() if v*c}
def pmul(p,q):
    r={}
    for e,c in p.items():
        for f,d in q.items():
            k=tuple(a+b for a,b in zip(e,f));r[k]=r.get(k,F(0))+c*d
    return {e:c for e,c in r.items() if c}
def paverage(p,theta,L,mu,alpha,beta,gamma):
    total=F(0);t=theta/L
    for e,c in p.items():
        ev,eg=e[:3],e[3:]
        if any(i%2 for i in e):continue
        vfac=F(1)
        for power in ev:
            if power==2:vfac*=t
            elif power==4:vfac*=3*t*t
            elif power!=0:raise AssertionError('unexpected V degree')
        dg=sum(eg)
        if dg==0:gfac=alpha
        elif dg==2:gfac=2*beta/(3*mu)
        elif dg==4:gfac=4*gamma/((5 if max(eg)==4 else 15)*mu*mu)
        else:raise AssertionError('unexpected g degree')
        total+=c*vfac*gfac
    return total
def vector_add(a,b):return [x+y for x,y in zip(a,b)]
def vector_scale(a,s):return [x*s for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def outer(a,b):return [[x*y for y in b] for x in a]
def matscale(a,s):return [[x*s for x in r] for r in a]
def matadd(*args):return [[sum(a[i][j] for a in args) for j in range(3)] for i in range(3)]
def normmax(a):return max(abs(x) for row in a for x in row)

def event_checks():
    cases=[]
    directions=[]
    for i in range(3):
        for sign in [-1,1]:
            a=[F(0)]*3;a[i]=F(sign);directions.append(a)
    for M in map(F,[1,17,1836]):
        m=F(1);h=M+m;L=h+m;eta=m/L;zeta=h/L;c=M/h;d=m/h;mu=m*zeta;mut=m*c
        V=[F(2,5),F(-1,7),F(3,11)];g0=[F(5),F(-3),F(2)]
        ve=vector_add(V,vector_scale(g0,zeta));vH=vector_add(V,vector_scale(g0,-eta))
        E=mu*dot(g0,g0)/2;E1=mu*9/2;E2=mut*4/2;I=E-E1-E2;Upsilon=I+E2
        assert I>0 and I<Upsilon<E
        incoming_momentum=vector_add(vector_scale(ve,m),vector_scale(vH,h))
        incoming_energy=(m*dot(ve,ve)+h*dot(vH,vH))/2
        sum_e=[[F(0)]*3 for _ in range(3)];sum_p=[[F(0)]*3 for _ in range(3)]
        for u1,u2 in itertools.product(directions,repeat=2):
            g1=vector_scale(u1,F(3));g2=vector_scale(u2,F(2))
            v1=vector_add(V,vector_scale(g1,zeta))
            v2=vector_add(vector_add(V,vector_scale(g1,-eta)),vector_scale(g2,c))
            vp=vector_add(vector_add(V,vector_scale(g1,-eta)),vector_scale(g2,-d))
            momentum=vector_add(vector_scale(vector_add(v1,v2),m),vector_scale(vp,M))
            assert momentum==incoming_momentum
            energy=(m*(dot(v1,v1)+dot(v2,v2))+M*dot(vp,vp))/2
            assert energy-incoming_energy+I==0
            sum_e=matadd(sum_e,matscale(matadd(outer(v1,v1),outer(v2,v2)),m))
            sum_p=matadd(sum_p,matscale(outer(vp,vp),M))
        avg_e=matscale(sum_e,F(1,36));avg_p=matscale(sum_p,F(1,36))
        expect_e=matscale(outer(V,V),2*m);expect_p=matscale(outer(V,V),M)
        for j in range(3):
            expect_e[j][j]+=F(2,3)*((1-eta*c)*E1+c*E2)
            expect_p[j][j]+=F(2,3)*(eta*c*E1+d*E2)
        assert avg_e==expect_e and avg_p==expect_p
        total=matadd(avg_e,avg_p,matscale(outer(ve,ve),-m),matscale(outer(vH,vH),-h))
        expected=matscale(outer(g0,g0),-mu)
        for j in range(3):expected[j][j]+=F(2,3)*(E-I)
        assert total==expected
        cases.append({'M_over_m':str(M),'exact_event_direction_pairs':36,'momentum_residual':'0','energy_residual':'0','gain_tensor_residual':'0','total_tensor_residual':'0'})
    return cases

def stf_checks():
    theta=F(3,2);I=2*theta;alpha=F(7,5);beta=alpha*(I+F(3,2)*theta);gamma=beta*(I+2*theta)
    ne=F(7,10);nH=F(13,10);k1=2*beta/(3*theta);k2=4*gamma/(15*theta**2)
    bases=[]
    for diag in [(1,-1,0),(0,1,-1)]:bases.append([[F(diag[i]) if i==j else F(0) for j in range(3)] for i in range(3)])
    for i,j in [(0,1),(0,2),(1,2)]:
        b=[[F(0)]*3 for _ in range(3)];b[i][j]=b[j][i]=F(1);bases.append(b)
    result=[]
    for M in map(F,[1,17,1836]):
        m=F(1);h=M+m;L=h+m;eta=m/L;zeta=h/L;c=M/h;d=m/h;mu=m*zeta
        V=[pvar(i) for i in range(3)];g=[pvar(i+3) for i in range(3)]
        ve=[padd(V[i],pscale(g[i],zeta)) for i in range(3)]
        vH=[padd(V[i],pscale(g[i],-eta)) for i in range(3)]
        vv=[[pmul(V[i],V[j]) for j in range(3)] for i in range(3)]
        ee=[[pmul(ve[i],ve[j]) for j in range(3)] for i in range(3)]
        hh=[[pmul(vH[i],vH[j]) for j in range(3)] for i in range(3)]
        source_e=[[padd(pscale(vv[i][j],2*m),pscale(ee[i][j],-m)) for j in range(3)] for i in range(3)]
        source_H=[[pscale(hh[i][j],-h) for j in range(3)] for i in range(3)]
        source_p=[[pscale(vv[i][j],M) for j in range(3)] for i in range(3)]
        source=[source_e,source_H,source_p]
        # Internal Jacobi gains are isotropic and vanish under this pointwise STF projection.
        for s in source:
            trace=padd(*(s[j][j] for j in range(3)))
            for j in range(3):s[j][j]=padd(s[j][j],pscale(trace,F(-1,3)))
        A=eta**2*alpha+2*eta*zeta*k1+zeta**2*k2
        B=zeta**2*alpha+2*eta*zeta*k1+eta**2*k2
        C=eta*zeta*(alpha-2*k1+k2)
        matrix=[[nH*(2*eta**2*alpha-A),ne*(2*eta*zeta*alpha-C)],[-nH*C,-ne*B],[nH*eta*(zeta-eta)*alpha,ne*zeta*(zeta-eta)*alpha]]
        assert sum(r[0] for r in matrix)==-nH*zeta*k2
        assert sum(r[1] for r in matrix)==-ne*eta*k2
        checked=0
        for column,(mass,density,velocity) in enumerate([(m,ne,ve),(h,nH,vH)]):
            for pi in bases:
                contraction=padd(*(pscale(pmul(velocity[i],velocity[j]),pi[i][j]) for i in range(3) for j in range(3)))
                perturbation=pscale(contraction,mass/(2*density*theta**2))
                for row,s in enumerate(source):
                    actual=[[ne*nH*paverage(pmul(s[i][j],perturbation),theta,L,mu,alpha,beta,gamma) for j in range(3)] for i in range(3)]
                    assert actual==matscale(pi,matrix[row][column])
                checked+=1
        qe=eta*((F(3,2)+2*d)*theta*alpha-d*beta)-c*I*alpha
        qH=-F(3,2)*zeta*theta*alpha-eta*beta
        qp=(F(3,2)*(zeta-eta)-2*eta*d)*theta*alpha+d*beta-d*I*alpha
        assert qe+qH+qp==-I*alpha
        u1=theta*alpha;u2=beta-(I+theta)*alpha
        qe_gain=3*eta*theta*alpha+(1-eta*c)*u1+c*u2
        qp_gain=F(3,2)*(zeta-eta)*theta*alpha+eta*c*u1+d*u2
        assert qe_gain-F(3,2)*eta*theta*alpha-zeta*beta==qe
        assert qp_gain==qp
        result.append({'M_over_m':str(M),'independent_incoming_STF_directions':checked,'species_tensors_per_direction':3,'exact_polynomial_Wick_residual':'0','scalar_partition_residual':'0','total_STF_residual':'0'})
    return result

def sharing_checks():
    mp.mp.dps=65
    cases=[]
    # These are new transferred-energy/partition observables. No old normalization suite is replayed.
    for ratio in [mp.mpf('1.00000001'),mp.mpf('2'),mp.mpf('100')]:
        x=mp.mpf(1);E=ratio
        actual=mp.quad(lambda y:y*E/((E-1)*y*y),[1,E])
        expected=E*mp.log1p(E-1)/(E-1)
        rel=abs(actual/expected-1);assert rel<mp.mpf('1e-55')
        cases.append({'kind':'new_conditional_transfer_mean','E_over_I':str(ratio),'relative_error':float(rel)})
    for x in map(mp.mpf,['0.8','8','80']):
        cuts=[0,1,4,16,64,mp.inf]
        Fv=mp.quad(lambda t:t/(x+t)*mp.exp(-t),cuts)
        Lambdav=mp.quad(lambda t:x*mp.log1p(t/x)*mp.exp(-t),cuts)
        H=mp.quad(lambda t:x*t/(x+t)**2*mp.exp(-t),cuts)
        def outgoing1(t):
            if not t:return mp.mpf(0)
            ubar=x*(x+t)/t*mp.log1p(t/x)
            return t/(x+t)*(x+t-ubar)*mp.exp(-t)
        def outgoing2(t):
            if not t:return mp.mpf(0)
            ubar=x*(x+t)/t*mp.log1p(t/x)
            return t/(x+t)*(ubar-x)*mp.exp(-t)
        u1=mp.quad(outgoing1,cuts);u2=mp.quad(outgoing2,cuts)
        residuals=[abs(Lambdav/(1-Fv)-1),abs(u1/Fv-1),abs(u2/H-1),abs((1-(x+1)*Fv)/H-1)]
        assert all(r<mp.mpf('1e-55') for r in residuals)
        assert 0<H<Fv
        cases.append({'kind':'new_Maxwell_transfer_compression','x':str(x),'Lambda_equals_beta_minus_theta_alpha_relative':float(residuals[0]),'U1_equals_theta_alpha_relative':float(residuals[1]),'U2_positive_oracle_relative':float(residuals[2]),'H_identity_relative':float(residuals[3]),'U2_over_theta_alpha':float(H/Fv),'subtraction_amplification_1_over_H':float(1/H)})
    return cases

def main():
    output={'schema':'he38.independent_gain_derivation_checks.v1','workflow_version':'1.0.0','approval_version':'0.2','started_utc':STAMP,'command':'python /tmp/he38_gain_theory/check_derivation.py','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'method':'exact rational event reconstruction and Cartesian Wick/angle polynomial contractions; new65digit transfer/partition quadratures','python':sys.version,'mpmath':mp.__version__,'old_scientific_suite_replays':0,'new_IVPs':0,'new_benchmarks':0,'new_renders':0,'checks':{}}
    try:
        output['checks']['event_and_gain']=event_checks()
        output['checks']['STF_and_heat']=stf_checks()
        output['checks']['sharing_compression']=sharing_checks()
        output['status']='PASS_SCOPED';code=0
    except Exception as exc:
        output['status']='FAIL';output['exception']={'type':type(exc).__name__,'message':str(exc)};code=1
    output['elapsed_seconds']=time.perf_counter()-START
    output['peak_RSS_KiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    output['exit_code']=code
    output['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    output['scope']='Exact and numerical controls for the declared finite-M source-coordinate isotropic Jacobi model, not empirical calibration.'
    (ROOT/'CHECKS.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='checks'},ensure_ascii=False))
    return code

if __name__=='__main__':sys.exit(main())
