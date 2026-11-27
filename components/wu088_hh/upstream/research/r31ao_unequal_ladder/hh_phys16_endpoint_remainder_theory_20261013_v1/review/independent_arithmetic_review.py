#!/usr/bin/env python3
"""Independent, bounded review of PHYS16 archived arithmetic.

Uses only the Python standard library and exact Fraction endpoint pairs.
Does not import the candidate, old arithmetic, source kernels, or root solvers.
Matrix majorants are solved by determinant/Cramer's rule (candidate: Gaussian
elimination). Narrow checks address source bridge, endpoint transfer and the
new finite adjoint/birth identities; no old physical suite is replayed.
"""
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path
import hashlib, json, struct, time, resource

ROOT=Path(__file__).resolve().parents[1]
P15=ROOT.parent/'HH_PHYS15_THEORY_20261012_v1'
NCP=P15/'inputs/phys14/inputs/ncp07/results'
OUT=ROOT/'review'
checks=[]; identities={}

def load(path,key):
    b=path.read_bytes(); identities[key]={'path':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    return json.loads(b)
def bits(x):return Q.from_float(struct.unpack('>d',bytes.fromhex(x))[0])
def iv(x):return x if isinstance(x,tuple) else (Q(x),Q(x))
def raw(x):
    if 'exact' in x:
        e=x['exact']
        if isinstance(e,list):return iv(Q(*map(int,e)))
        return (Q(*map(int,e['lo'])),Q(*map(int,e['hi'])))
    return bits(x['lo_bits']),bits(x['hi_bits'])
def add(a,b):
    a,b=iv(a),iv(b);return a[0]+b[0],a[1]+b[1]
def neg(a):a=iv(a);return -a[1],-a[0]
def sub(a,b):return add(a,neg(b))
def mul(a,b):
    a,b=iv(a),iv(b);v=[x*y for x in a for y in b];return min(v),max(v)
def div(a,b):
    b=iv(b);assert not b[0]<=0<=b[1];return mul(a,(1/b[1],1/b[0]))
def sq(a):
    a=iv(a);return 0 if a[0]<=0<=a[1] else min(a[0]**2,a[1]**2),max(a[0]**2,a[1]**2)
def summ(xs):
    z=iv(0)
    for v in xs:z=add(z,v)
    return z
def dot(a,b):return summ(mul(x,y) for x,y in zip(a,b))
def mv(a,v):return [dot(row,v) for row in a]
def mm(a,b):return [[dot(row,[r[j] for r in b]) for j in range(len(b[0]))] for row in a]
def vm(v,a):return [dot(v,[r[j] for r in a]) for j in range(len(a[0]))]
def matadd(a,b):return [[add(x,y) for x,y in zip(r,s)] for r,s in zip(a,b)]
def meet(a,b):
    a,b=iv(a),iv(b);r=(max(a[0],b[0]),min(a[1],b[1]));assert r[0]<=r[1];return r
def hull(a,b):return min(a[0],b[0]),max(a[1],b[1])
def mag(a):a=iv(a);return max(abs(a[0]),abs(a[1]))
def inside(a,b,strict=False):return b[0]<a[0]<=a[1]<b[1] if strict else b[0]<=a[0]<=a[1]<=b[1]
def check(name,predicate,detail):
    assert predicate,name
    checks.append({'id':name,'status':'PASS','detail':detail})
def contains_all(narrow,recorded):return all(inside(a,raw(b)) for a,b in zip(narrow,recorded))
def determinant(a):
    out=Q(0)
    for p in permutations(range(len(a))):
        v=Q((-1)**sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p))))
        for i,j in enumerate(p):v*=a[i][j]
        out+=v
    return out
def cramer(a,b):
    den=determinant(a);assert den
    return [determinant([[b[i] if j==k else a[i][j] for j in range(4)] for i in range(4)])/den for k in range(4)]

def main():
    start=time.perf_counter()
    app=load(ROOT/'checks/application/run01/results/CORRELATED_DEFECT_RESULTS.json','application')
    ep=load(ROOT/'checks/endpoint/application01/ENDPOINT_REMAINDER_RESULTS.json','endpoint')
    hs=load(ROOT/'checks/endpoint/ENDPOINT_HESSIAN_READOUT.json','hessian_readout')
    src=load(NCP/'full/SOURCE_BOX.json','source'); half=load(NCP/'first_half/SOURCE_BOX.json','half_source')
    ctr=load(NCP/'full/SOURCE_CENTRE.json','centre')
    comp=load(NCP/'full/SOURCE_BOX_COMPONENTS.json','nonphoto');ccomp=load(NCP/'full/SOURCE_CENTRE_COMPONENTS.json','centre_nonphoto')
    cs=load(NCP/'full/NATIVE_CONSTANT_LEAVES.json','constants')
    pre=load(P15/'inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json','uniform')
    adv=load(P15/'inputs/phys14/results/advance01/ADVANCE_RESULTS.json','advance')
    fc=load(ROOT.parent/'phys14_intake/ncp07/HH_PHYS07_NCP_LOCAL_20261011_v1/inputs/FROZEN_SOURCE_CONTRACT.json','frozen_contract')
    for d in app['input_identities']:
        b=(P15/d['path']).read_bytes();assert len(b)==d['bytes'] and hashlib.sha256(b).hexdigest()==d['sha256']
    for d in ep['inputs'].values():
        b=Path(d['path']).read_bytes();assert len(b)==d['bytes'] and hashlib.sha256(b).hexdigest()==d['sha256']
    check('input_identity',True,'All 14 application inputs and 6 endpoint inputs match their recorded bytes and SHA256.')
    C=[[iv(Q.from_float(x)) for x in row] for row in pre['fixed_C']]
    S=[Q.from_float(x) for x in pre['radius']];q=bits(pre['q']['hi_bits'])
    B=[[raw(x)[1] for x in row] for row in pre['B']]
    center=[iv(Q.from_float(x)) for x in pre['center']]
    X=[raw(x) for x in adv['root_certificate']['domain_X']]
    floats=[*pre['center'],*pre['radius']]
    check('frozen_binary64_center_radius',all(struct.unpack('>Q',struct.pack('>d',x))[0]==w for x,w in zip(floats,fc['frozen_words'][8:])),
          'Original source centre and S are exactly the frozen binary64 words, not exact decimal 0.915, 0.015, etc.')
    check('original_preconditioner',all(raw(app['transfer']['C'][i][j])==C[i][j] and raw(app['transfer']['B'][i][j])==iv(B[i][j]) for i in range(4) for j in range(4)) and all(raw(x)==iv(s) for x,s in zip(app['transfer']['radius'],S)) and q==raw(app['transfer']['q'])[1] and 0<=max(sum(B[i][j]*S[j]/S[i] for j in range(4)) for i in range(4))<=q<1,
          'Original C, B, q and S are unchanged; q dominates all weighted row sums exactly.')
    g1,g2,gF=[[raw(x) for x in app['root_boxes'][k]] for k in ['g1','g2','gF']]
    fullseg=[hull(a,b) for a,b in zip(g2,gF)];seg12=[hull(a,b) for a,b in zip(g1,g2)]
    def physical(g):return all(z[0]>0 for z in g) and g[0][1]<1 and g[1][1]+g[2][1]<1
    check('gas_domains',all(physical(g) and all(inside(a,b,True) for a,b in zip(g,X)) for g in [g1,g2,gF,fullseg,seg12]) and all(inside(a,b,True) for a,b in zip(center,X)),
          'All root boxes, centre and required gas mean-Jacobian segments lie strictly inside X and the physical H/He population domain.')
    h=bits(half['dt_bits']); n1,n2=bits(half['nH_bits']),bits(src['nH_bits'])
    f1,f2=bits(half['nHe_stored_bits'])/n1,bits(src['nHe_stored_bits'])/n2
    df=f1-f2;rn=n1/n2;CT=2*bits(cs['ev_erg_bits'])/(3*bits(cs['kb_bits']))
    rho=raw(app['linked_factors']['rho']);birth=raw(app['linked_factors']['M'])
    pp=load(NCP/'first_half/PREBE.json','prebe_half');pf=load(NCP/'full/PREBE.json','prebe_full')
    check('shared_constants',h==625000000 and bits(src['dt_bits'])==2*h and inside(iv(df),raw(app['source_bridge']['f1_minus_f2'])) and df<0 and rho==raw(adv['constants']['rho']) and birth==iv(bits(pp['fl_dt_SOURCE_bits'])) and bits(pf['fl_dt_SOURCE_bits'])==2*birth[0],
          'Exact density ratios, h/2h, common rho and exact doubled birth amplitude are bound to the archived COMMON inputs.')
    E=[bits(x) for x in src['energy_bits']];sig=[bits(row[0]) for row in src['sigma_bits']];heat=[bits(row[0]) for row in src['heat_bits']]
    chi=bits(cs['CHI_bits'][0]);cc=bits(cs['c_bits']);H=bits(src['Hmean_bits'])
    check('opacity_species_units',src['sigma_bits']==half['sigma_bits'] and src['energy_bits']==half['energy_bits'] and src['heat_bits']==half['heat_bits'] and [i for i,s in enumerate(sig) if s>0]==list(range(16,33)) and all(bits(row[1])==bits(row[2])==0 for row in src['sigma_bits']) and all(heat[i]==E[i]-chi for i in range(16,33)),
          '33 groups, 17 HI active groups, no He photo opacity, and exact heat=energy-CHI on active groups.')
    # Independent source Taylor inclusion in the four gas coordinates.
    def local(j,jc,g):
        dif=[sub(a,c) for a,c in zip(g,center)]
        grad=[raw(x) for x in j['gradient'][:4]];cgrad=[raw(x) for x in jc['gradient'][:4]]
        Hess=[[raw(x) for x in row[:4]] for row in j['signed_hessian'][:4]]
        value=meet(raw(j['value']),add(raw(jc['value']),dot(grad,dif)))
        deriv=[meet(grad[k],add(cgrad[k],dot(Hess[k],dif))) for k in range(4)]
        return value,deriv
    def npq(g):return [local(j,jc,g) for j,jc in zip(comp['nonphoto'],ccomp['nonphoto'])],local(src['q'],ctr['q'],g)
    s1=add(g1[1],mul(2,g1[2]));e1=add(g1[0],mul(f1,s1));e2=add(g1[0],mul(f2,s1));pi1=add(1+f1,e1)
    pull=div(mul(mul(neg(g1[3]),df),add(1,s1)),pi1)
    star=[*g1[:3],add(g1[3],pull)];ps=[hull(a,b) for a,b in zip(g1,star)]
    np1,q1=npq(g1);npstar,qstar=npq(star);nppull,qpull=npq(ps)
    kwlo=div(npstar[3][0],mul(n2*f2,e2))[0];kw=(kwlo,Q(0))
    correction=mul(mul(mul(n1,e1),df),kw)
    re1=add(rn-1,div(mul(rn*df,s1),e2));re=add(1,re1)
    dnp=[add(mul(re1,np1[i][0]),mul(mul(re,nppull[i][1][3]),pull)) for i in range(4)];dnp[3]=add(dnp[3],correction)
    dq=add(mul(rn-1,q1[0]),mul(mul(rn,qpull[1][3]),pull))
    T1=div(mul(CT,g1[3]),pi1)
    rr=Q.from_float(1.5)-Q.from_float(1.503)+Q.from_float(1.923)*Q.from_float(.470)/2
    check('source_pullback_cooling',all(inside(a,b,True) for a,b in zip(star,X)) and all(inside(a,b,True) for a,b in zip(ps,X)) and physical(star) and 30000<T1[0]<=T1[1]<110000 and rr>0 and Q(315614)/(Q.from_float(.522)*110000)>1 and npstar[3][0][1]<0 and correction[0]>=0 and inside(kw,raw(app['source_bridge']['kwHe'])) and inside(pull,raw(app['source_bridge']['pullback_w'])) and contains_all(dnp,app['source_bridge']['nonphoto_time_difference']) and inside(dq,raw(app['source_bridge']['HH_time_difference'])),
          'Recomputed temperature-aligned pullback, exact density difference, positive RR lower factor, cooling-cone He bound and both source time differences are enclosed by the candidate. Coefficient cooling proof also manually checked in ft03_interval.rs.')
    # Exact reconstruction of the mean gas Jacobian on the full gas segment.
    def JB(g):
        np,qj=npq(g);hh=[Q(1),Q(0),Q(0),-chi]
        z=[[add(np[i][1][j],mul(mul((Q(0),Q(1)),qj[1][j]),hh[i])) for j in range(4)] for i in range(4)]
        z[3][3]=sub(z[3][3],2*H);return z
    a2=[cc*n2*s for s in sig]+[Q(0),Q(0)]
    Dseg=[add(1,mul(2*h*a,sub(1,fullseg[0]))) for a in a2]
    QF=[raw(x) for x in app['linked_factors']['QF']]
    vv=[div(mul(a,nf),sq(dd)) for a,nf,dd in zip(a2,QF,Dseg)]
    v=[summ(vv[:33]),iv(0),iv(0),dot(heat,vv[:33])]
    jb=JB(fullseg)
    ab=[[add(sub(i==j,mul(2*h,jb[i][j])),mul(2*h,v[i]) if j==0 else 0) for j in range(4)] for i in range(4)]
    check('mean_jacobian_enclosure',all(contains_all(row,rec) for row,rec in zip(ab,app['transfer']['averaged_jacobian'])),
          'Mean source Jacobian and positive one-column photo term are enclosed on the entire g2-to-gF segment with the stored QF family.')
    r=[raw(x) for x in app['residual']];cr=[raw(x) for x in app['transfer']['Cr']]
    check('signed_preconditioning',contains_all(mv(C,r),app['transfer']['Cr']),'Signed C times residual independently recomputed before magnitude.')
    A=[[Q(i==j)-B[i][j] for j in range(4)] for i in range(4)]
    major=cramer(A,[mag(x) for x in cr]);rem=[sum(B[i][j]*major[j] for j in range(4)) for i in range(4)]
    check('component_majorant_cramer',all(x>=0 for x in major) and all(major[i]-rem[i]==mag(cr[i]) for i in range(4)) and all(inside(iv(x),raw(y)) for x,y in zip(major,app['transfer']['componentwise_absolute_majorant'])) and all(inside(iv(x),raw(y)) for x,y in zip(rem,app['transfer']['componentwise_remainder'])),
          'Independent determinant/Cramer solution of (I-B)m=mag(Cr) is nonnegative and enclosed by recorded 256-bit outward values.')
    d0=[raw(x) for x in app['transfer']['initial_d']];eb=[[raw(x) for x in row] for row in app['transfer']['Ebar']]
    dd=d0
    for k in range(3):dd=[meet(x,add(y,z)) for x,y,z in zip(dd,cr,mv(eb,dd))]
    d=[raw(x) for x in app['endpoint']['d']]
    check('three_mean_intersections',contains_all(dd,app['endpoint']['d']) and all(inside(a,b) for a,b in zip(d,[sub(a,b) for a,b in zip(g2,gF)])),
          'Three exact interval mean-operator intersections are enclosed by candidate; result also lies within independent root-box difference.')
    le=[iv(1),iv(f2),iv(2*f2),iv(0)];de=dot(le,d)
    pi2=add(add(1+f2,g2[0]),mul(f2,add(g2[1],mul(2,g2[2]))));pif=sub(pi2,de)
    t2=div(mul(CT,g2[3]),pi2);dt=div(sub(mul(CT,d[3]),mul(t2,de)),pif)
    check('finite_readout',pif[0]>0 and d[0][0]>0 and d[3][1]<0 and de[0]>0 and dt[1]<0 and inside(dt,raw(app['endpoint']['DeltaT_K'])) and inside(de,raw(app['endpoint']['Deltae_per_H'])) and inside(mul(n2,de),raw(app['endpoint']['Deltane_cm3'])),
          'Exact finite temperature quotient, electron readouts, positive PiF, dx>0 and dw<0 independently verified.')
    # Read original residual Hessian without introducing a second factor 2h.
    Hess=[[[raw(x) for x in row] for row in mat] for mat in src['G_gg']]
    t=[[[mul(S[j]*S[k]/S[i],summ(mul(C[i][a],Hess[a][j][k]) for a in range(4))) for k in range(4)] for j in range(4)] for i in range(4)]
    L=max(sum(mag(x) for row in mat for x in row) for mat in t)
    check('preconditioned_hessian',iv(L)==raw(hs['L_H']) and iv(L)==raw(ep['L_H']),
          'Exact signed preconditioned original residual Hessian reproduces L_H; no extra 2h factor is applied.')
    diff=[sub(a,b) for a,b in zip(g2,center)]
    jend=[[meet(add(raw(ctr['A_Gg'][i][j]),summ(mul(Hess[i][k][j],diff[k]) for k in range(4))),raw(src['A_Gg'][i][j])) for j in range(4)] for i in range(4)]
    cj=mm(C,jend);M=[[meet(sub(i==j,cj[i][j]),(-B[i][j],B[i][j])) for j in range(4)] for i in range(4)]
    check('endpoint_J_center_Hessian',all(contains_all(a,b) for a,b in zip(jend,ep['endpoint_J_inclusion'])) and all(contains_all(a,b) for a,b in zip(M,ep['M_inclusion'])),
          'Endpoint J uses centre plus full-weight Hessian integral along c-to-g2, intersected with original whole-X J and B.')
    Id=[[iv(i==j) for j in range(4)] for i in range(4)];P=matadd(matadd(Id,M),mm(M,M))
    crnew=mv(C,r);prediction=mv(P,crnew)
    a=max(mag(x)/s for x,s in zip(d,S));psum=1+q+q*q;kappa=1/(1-q)
    eps=q**3*a+L*a*a*psum/2
    # Endpoint application intentionally uses archived Pi2/PiF intervals.
    pi2r,pifr=raw(app['endpoint']['Pi2']),raw(app['endpoint']['PiF'])
    tr=div(mul(CT,g2[3]),pi2r)
    nt=[sub(CT if i==3 else 0,mul(tr,le[i])) for i in range(4)]
    bt=sum(mag(x)*s for x,s in zip(nt,S));z=vm(vm(nt,P),C)
    cn=max(sum(mag(C[i][j])*S[j]/S[i] for j in range(4)) for i in range(4))
    zerr=kappa*cn*bt*(q**3+L*a*psum/2)
    zm=[add(x,(-zerr/s,zerr/s)) for x,s in zip(z,S)]
    num=add(meet(dot(z,r),dot(nt,prediction)),(-bt*eps,bt*eps))
    ref=[meet(x,add(y,(-s*eps,s*eps))) for x,y,s in zip(d,prediction,S)]
    check('finite_m2_adjoint_remainder',iv(a)==raw(ep['a_from_actual_D']) and iv(eps)==raw(ep['epsilon_m']) and iv(kappa*L*a*a/2)==raw(ep['endpoint_newton_error_upper']) and iv(bt*eps/pifr[0])==raw(ep['temperature_error_from_same_denominator_upper_K']) and iv(zerr)==raw(ep['averaged_adjoint_weighted_row_error_upper_K']) and contains_all(prediction,ep['Neumann_prediction']) and contains_all(ref,ep['endpoint_d_intersection']) and inside(num,raw(ep['temperature_numerator'])) and contains_all(zm,ep['averaged_adjoint_numerator_inclusion']),
          'Finite m=2 prediction, quadratic error, weighted mean-adjoint row error and refined d/numerator reproduced exactly using original q,L_H,S.')
    # Rational sign factorizations derived independently by subtracting the
    # exact beta expressions at two rational eta witnesses, then interval bound.
    eta=mul(h*cc*n2,sub(1,g2[0]));s23,s24=sig[23],sig[24]
    d23,d24=add(1,mul(eta,s23)),add(1,mul(eta,s24));den=mul(sq(d23),sq(d24))
    db=div(mul(mul(eta,s23-s24),sub(1,mul(sq(eta),s23*s24))),den)
    A0,A1=heat[23]*s23,heat[24]*s24
    co=[A0-A1,A0*s24-A1*s23,A0*s24*s24-A1*s23*s23]
    dh=div(mul(eta,add(add(co[0],mul(mul(2,eta),co[1])),mul(sq(eta),co[2]))),den)
    for e in [eta[0],eta[1]]:
        b23=e*s23/(1+e*s23)**2;b24=e*s24/(1+e*s24)**2
        assert b23-b24==e*(s23-s24)*(1-e*e*s23*s24)/((1+e*s23)**2*(1+e*s24)**2)
        assert heat[23]*b23-heat[24]*b24==e*(co[0]+2*e*co[1]+e*e*co[2])/((1+e*s23)**2*(1+e*s24)**2)
    alpha=div(mul(sub(1,rho),E[24]),E[24]-E[23]);tau=mul(eta,s24)
    c1=div(tau,mul(sq(add(1,tau)),add(1,mul(2,tau))))
    zn=add(zm[0],mul(heat[24],zm[3]))
    br=div(mul(mul(birth,alpha),add(mul(db,zm[0]),mul(dh,zm[3]))),pifr)
    be=div(mul(mul(neg(birth),c1),zn),pifr)
    bs=ep['birth_signed_factorization']
    check('birth_common_adjoint_sign',all(c<0 for c in co) and db[0]>0 and dh[1]<0 and zm[0][1]<0 and zm[3][0]>0 and zn[1]<0 and alpha[0]>0 and c1[0]>0 and br[1]<0 and be[0]>0 and inside(br,raw(bs['birth_redshift_DeltaT_over_b_K'])) and inside(be,raw(bs['birth_backward_euler_DeltaT_over_b_K'])),
          'Exact b factor retained: birth-redshift DeltaT/b<0 and birth-BE DeltaT/b>0; both exact sectors vanish at b=0. They are attribution terms, not parameter derivatives.')
    # Guard j=1: direct remap composition, including number and energy guards.
    for rr in [Q(99,100),Q(999,1000)]:
        e0,eone=Q(5),Q(7);alph=(1-rr)*eone/(eone-e0)
        def transport(v,rho0):
            aa=(1-rho0)*eone/(eone-e0);v0,v1,gn,gu=v
            return [aa*v1,(1-aa)*v1,gn+v0,rho0*(gu+e0*v0)]
        seed=[Q(0),Q(1),Q(0),Q(0)]
        compo=transport(transport(seed,rr),rr);single=transport(seed,rr*rr)
        actual=[x-y for x,y in zip(compo,single)]
        expected=[-alph*(alph+rr),alph*(alph+rr-1),alph,rr*e0*alph]
        assert actual==expected and sum(actual[:3])==0
        assert e0*actual[0]+eone*actual[1]+actual[3]==0
    check('below_guard_deltaR_j1',True,'Two exact rational guard witnesses: R(rho)^2-R(rho^2) equals all four j=1 coefficients, including GN/GU; number and energy differences vanish.')
    wf=load(ROOT/'checks/wolfram/WOLFRAM_XACT_EXECUTION.json','wolfram_xact')
    last=wf['final_success']['response'] if 'final_success' in wf else None
    if last is None:
        last=next(v['response'] for v in wf.values() if isinstance(v,dict) and 'response' in v and 'code' in v)
    txt='\n'.join(x.get('text','') for x in last['content'])
    names=['HessianLastPairSymmetry','TaylorResidualTransfer','DualResidualGoal','CommonSectorAdjoint','HessianGoalContraction','PhotonRankOneAction','PhotonTaylorRemainder','PhotonMeanToEndpoint','FiniteTemperaturePredictor','AffineCovectorPairing']
    check('wolfram_xact_record',last.get('isError') is False and all('"'+name+'" -> 0' in txt for name in names) and '"ExternalCanonicalizerUsed" -> False' in txt and '"Messages" -> {}' in txt,
          'Inspected actual authenticated Wolfram/xAct output: six tensor and four scalar exact zeros; pure-Wolfram xPerm backend. Earlier MathLink failures are recorded and are not counted as successful verification.')
    for key,rel in [('application_code','src/application/correlated_endpoint_application.py'),('endpoint_code','checks/endpoint/apply_endpoint_remainder.py'),('endpoint_theory','theory/ENDPOINT_REMAINDER_THEORY_KO.md'),('source_helper','../HH_PHYS15_THEORY_20261012_v1/inputs/phys14/src/phys14_advance.py')]:
        p=(ROOT/rel).resolve();bb=p.read_bytes();identities[key]={'path':str(p),'bytes':len(bb),'sha256':hashlib.sha256(bb).hexdigest()}
    result={'schema':'WU088_HH_PHYS16_INDEPENDENT_ARITHMETIC_REVIEW_V1','status':'ALL_BOUNDED_CHECKS_PASS','checks':checks,'input_identities':identities,
            'scope':'Exact rational static checks under the inherited same-COMMON fixed-alpha real C2 family. They supplement direct source/proof reading; no renewed native source certification.',
            'physical_source_calls':0,'root_solves':0,'history_replays':0,'candidate_imports':0,
            'elapsed_seconds':time.perf_counter()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (OUT/'INDEPENDENT_ARITHMETIC_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'bounded_check_groups':len(checks),'elapsed_seconds':result['elapsed_seconds'],'peak_rss_kib':result['peak_rss_kib']}))

if __name__=='__main__':main()
