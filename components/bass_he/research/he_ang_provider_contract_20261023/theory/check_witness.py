"""Independent exact construction; does not import the provider implementation.

Two finite positive laws are quadratures of the continuous law proved in
DERIVATION.md. Dimensionless manufactured masses are not calibrated H1 data.
"""
from fractions import Fraction as F
from collections import Counter
import json,sys

I3=[[F(i==j) for j in range(3)] for i in range(3)]
outcomes=[]
def add(x,y):return [a+b for a,b in zip(x,y)]
def scale(c,x):return [c*a for a in x]
def dot(x,y):return sum(a*b for a,b in zip(x,y))
def outer(x,y):return [[a*b for b in y] for a in x]
def matadd(x,y):return [add(a,b) for a,b in zip(x,y)]
def matscale(c,x):return [scale(c,a) for a in x]
def trace(x):return sum(x[i][i] for i in range(3))
def apply(o,x):return [dot(row,x) for row in o]
def rotate(o,r):return [[sum(o[i][k]*r[k][l]*o[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
def clean(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(a) for a in x]
    return x
def eq(name,actual,expected):
    outcomes.append({'id':name,'pass':actual==expected,'actual':clean(actual),'expected':clean(expected)})
def moment(points,mass):
    n=F(0);p=[F(0)]*3;r=[[F(0)]*3 for _ in range(3)]
    for weight,q in points:
        n+=weight;p=add(p,scale(weight,q));r=matadd(r,matscale(weight/mass,outer(q,q)))
    return n,p,r
def D(r,a):return (3*dot(a,apply(r,a))-trace(r))/4
def stf(r):return matadd(r,matscale(-trace(r)/3,I3))
def predicted_boost(raw,mass,u,o):
    n,p,r=raw
    x=matadd(matadd(r,matscale(-1,outer(u,p))),matscale(-1,outer(p,u)))
    x=matadd(x,matscale(mass*n,outer(u,u)))
    return n,apply(o,add(p,scale(-mass*n,u))),rotate(o,x)

cases=[('coordinate_mass_ratio',F(1),F(1836),F(1),[F(0),F(0),F(1)],[F(1),F(0),F(0)],[F(0),F(1),F(0)]),
       ('rotated_unequal_mass',F(2),F(7),F(3,5),[F(3,5),F(0),F(4,5)],[F(4,5),F(0),F(-3,5)],[F(0),F(1),F(0)])]
payload=[]
for name,m,M,k,a,b1,b2 in cases:
    W=2*k*k*(1/m+1/M);ke=2*k*k/m;kp=2*k*k/M
    aa=outer(a,a);perp=matadd(I3,matscale(-1,aa))
    re=matscale(2*k*k/m,matadd(aa,matscale(F(1,2),perp)))
    expected_p={'A':matscale(4*k*k/M,aa),'B':matscale(2*k*k/M,perp)}
    expected_c=matscale(2*k*k,matadd(aa,matscale(F(-1,2),perp)))
    laws={};marginals={};all_raw={}
    for law in ['A','B']:
        events=[];ep=[];pp=[];joint=Counter();marginal=Counter();c=[[F(0)]*3 for _ in range(3)]
        for s in [-1,1]:
            for b in [b1,scale(-1,b1),b2,scale(-1,b2)]:
                if law=='A':q1=scale(s*k,add(a,b));q2=scale(s*k,add(a,scale(-1,b)));qp=scale(-2*s*k,a)
                else:q1=scale(k,add(scale(s,a),b));q2=scale(k,add(scale(-s,a),b));qp=scale(-2*k,b)
                w=F(1,8);i=len(events);tag=f'{name}/{law}/event{i}'
                eq(tag+'/momentum',add(add(q1,q2),qp),[0,0,0])
                eq(tag+'/energy',(dot(q1,q1)+dot(q2,q2))/(2*m)+dot(qp,qp)/(2*M),W)
                eq(tag+'/electron_norms',[dot(q1,q1),dot(q2,q2)],[2*k*k,2*k*k])
                eq(tag+'/pair_dot',dot(q1,q2),0)
                eq(tag+'/ion_norm',dot(qp,qp),4*k*k)
                events.append({'weight':w,'q1':q1,'q2':q2,'qp':qp});ep.extend([(w,q1),(w,q2)]);pp.append((w,qp))
                joint[(tuple(q1),tuple(q2),tuple(qp))]+=w
                for q in [q1,q2]:marginal[tuple(q)]+=w
                c=matadd(c,matscale(w,matadd(outer(q1,q2),outer(q2,q1))))
        eq(f'{name}/{law}/exchange',joint,Counter({(b,a,p):w for (a,b,p),w in joint.items()}))
        er=moment(ep,m);pr=moment(pp,M);all_raw[law]=(er,pr)
        eq(f'{name}/{law}/counts',[er[0],pr[0]],[2,1])
        eq(f'{name}/{law}/electron_R',er[2],re)
        eq(f'{name}/{law}/ion_R',pr[2],expected_p[law])
        eq(f'{name}/{law}/first_moments',[er[1],pr[1]],[[0,0,0],[0,0,0]])
        eq(f'{name}/{law}/C12',c,expected_c if law=='A' else matscale(-1,expected_c))
        eq(f'{name}/{law}/same_law_Rp',pr[2],matadd(matscale(m/M,er[2]),matscale(1/M,c)))
        eq(f'{name}/{law}/D_e',D(er[2],a),ke/4)
        eq(f'{name}/{law}/D_p',D(pr[2],a),kp if law=='A' else -kp/2)
        z=F(7,3)
        eq(f'{name}/{law}/sigma_weighted_energy',z*trace(pr[2])/2,z*W-z*trace(er[2])/2)
        eq(f'{name}/{law}/sigma_weighted_C_trace',z*trace(c),2*M*z*W-2*(M+m)*z*ke)
        u=[F(1,3),F(-2,5),F(3,7)];o=[[0,-1,0],[1,0,0],[0,0,1]]
        for species,points,mass,raw in [('e',ep,m,er),('p',pp,M,pr)]:
            transformed=[(w,apply(o,add(q,scale(-mass,u)))) for w,q in points]
            eq(f'{name}/{law}/{species}_frame',moment(transformed,mass),predicted_boost(raw,mass,u,o))
        h=M+m;qin=scale(F(3),a);incoming_E=dot(qin,qin)*(1/m+1/h)/2;threshold=incoming_E-W
        eq(f'{name}/{law}/positive_fixture_threshold',threshold>0,True)
        signed={'e':(ep+[(F(-1),qin)],m),'H':([(F(-1),scale(-1,qin))],h),'p':(pp,M)}
        net={sp:moment(points,mass) for sp,(points,mass) in signed.items()}
        eq(f'{name}/{law}/reactive_counts',[net[sp][0] for sp in ['e','H','p']],[1,-1,1])
        eq(f'{name}/{law}/reactive_mass',sum(mass*net[sp][0] for sp,(_,mass) in signed.items()),0)
        eq(f'{name}/{law}/reactive_energy',sum(trace(raw[2])/2 for raw in net.values()),-threshold)
        shifted=[]
        for sp,(points,mass) in signed.items():
            direct=moment([(w,apply(o,add(q,scale(-mass,u)))) for w,q in points],mass)
            eq(f'{name}/{law}/{sp}_signed_frame',direct,predicted_boost(net[sp],mass,u,o));shifted.append(direct)
        eq(f'{name}/{law}/boosted_net_momentum',[sum(v[1][i] for v in shifted) for i in range(3)],[0,0,0])
        eq(f'{name}/{law}/boosted_net_energy',sum(trace(v[2])/2 for v in shifted),-threshold)
        laws[law]={'events':events,'electron':{'N':er[0],'P':er[1],'R':er[2]},'proton':{'N':pr[0],'P':pr[1],'R':pr[2]},'C12':c,'D_e':D(er[2],a),'D_p':D(pr[2],a)}
        marginals[law]=marginal
    eq(name+'/full_discrete_marginal',marginals['A'],marginals['B'])
    eq(name+'/ion_STF_difference',matadd(stf(all_raw['A'][1][2]),matscale(-1,stf(all_raw['B'][1][2]))),matscale(3*kp,matadd(aa,matscale(F(-1,3),I3))))
    payload.append({'id':name,'m':m,'M':M,'kappa':k,'axis':a,'W':W,'K_e':ke,'K_p':kp,'laws':laws})
report={'schema':'he_ang.exact_witness_results.v1','fixture_kind':'manufactured_kinematic_contract','units':'consistent arbitrary rational kinetic units; not empirical SI source data','cases':clean(payload),'case_count':len(cases),'ensembles':2*len(cases),'events':16*len(cases),'predicates':len(outcomes),'passed':sum(r['pass'] for r in outcomes),'outcomes':outcomes,'old_HE_X1_replays':0,'old_HE38_replays':0,'empirical_calibration':False,'continuous_law_proof':'theory/DERIVATION.md section5; finite quadrature only exact through degree2'}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(0 if all(r['pass'] for r in outcomes) else 1)
