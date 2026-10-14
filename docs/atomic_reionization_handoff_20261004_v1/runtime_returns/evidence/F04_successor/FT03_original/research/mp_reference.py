"""Independent full-population / log-temperature RK4, using 50 digit arithmetic.
No call to the float RHS or its analytic logarithmic-slope implementation.
"""
import json,math,time,argparse
from pathlib import Path
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
mp.mp.dps=50;m=mp.mpf
F=m('.083');NH=m('1e-4');H=m('1e14');KB=m('1.380649e-16');EV=m('1.602176634e-12');C=m('29979245800')
CHI=list(map(m,['13.598434599702','24.587389011','54.41776']));EG=list(map(m,['20','35','70']))
L=list(map(m,['315614','570670','1263030']))
rows=json.loads((ROOT/'inputs/VERNER96_HHE_PARAMETERS.json').read_text())['rows']
def photo_sigma(row,E):
    _,_,eth,emax,e0,s0,ya,p,yw,y0,y1=map(m,row)
    if E<eth:return m(0)
    x=E/e0-y0;y=mp.sqrt(x*x+y1*y1)
    return m('1e-18')*s0*((x-1)**2+yw*yw)*y**(p/2-m('5.5'))/(1+mp.sqrt(y/ya))**p
SIG=[[photo_sigma(row,E) for E in EG] for row in rows]

def ar(T,s):
    lam=L[s]/T
    if s==1:return m('3e-14')*lam**m('.654')
    return (2 if s==2 else 1)*m('1.269e-13')*lam**m('1.503')/(1+(lam/m('.522'))**m('.470'))**m('1.923')

def rhs(v):
    h0,hp,he0,hep,hepp=v[:5];p=v[5:8];T=mp.exp(v[8])
    if not m('30000')<T<m('110000'):raise ValueError('reference outside model domain')
    el=hp+hep+2*hepp;nu=sum(v[:5])+el
    alpha=[ar(T,s) for s in range(3)]
    kinetic=[KB*(m('1.5')*T*alpha[s]+T*T*mp.diff(lambda t:ar(t,s),T)) for s in range(3)]
    beta=[]
    for s,(A,ex,c,r,d) in enumerate(zip(['21.11','32.38','19.95'],['-1.089','-1.146','-1.089'],['.354','.416','.553'],['.874','.987','.735'],['1.101','1.056','1.275'])):
        l=L[s]/T
        beta.append(m(A)*T**m('-1.5')*mp.exp(-l/2)*l**m(ex)/(1+(l/m(c))**m(r))**m(d))
    b1=m('40.49664394833662')*m(11605);b2=m('8.099328789667')*m(11605)
    da=m('1.54e-9')*(T/m(11605))**m('-1.5')*mp.exp(-b1/T)
    db=da*m('.3')*mp.exp(-b2/T)
    lower=[h0,he0,hep];upper=[hp,hep,hepp]
    pi=[[C*NH*lower[s]*p[g]*SIG[s][g] for g in range(3)] for s in range(3)]
    ci=[NH*el*lower[s]*beta[s] for s in range(3)]
    rr=[NH*el*upper[s]*alpha[s] for s in range(3)]
    dr=NH*el*hep*(da+db)
    ion=[sum(pi[s])+ci[s] for s in range(3)]
    ih=ion[0]-rr[0];ihe=ion[1]-rr[1]-dr;ihh=ion[2]-rr[2]
    material=[-ih,ih,-ihe,ihe-ihh,ihh]
    photon=[-sum(pi[s][g] for s in range(3)) for g in range(3)]
    heat=sum(pi[s][g]*(EG[g]-CHI[s]) for s in range(3) for g in range(3))
    rec_loss=NH*el*sum(upper[s]*kinetic[s] for s in range(3))/EV
    dr_loss=NH*el*hep*KB*(da*b1+db*(b1+b2))/EV
    heat-=sum(ci[s]*CHI[s] for s in range(3))+rec_loss+dr_loss
    eldot=material[1]+material[3]+2*material[4]
    theta_dot=2*EV*heat/(3*KB*nu*T)-eldot/nu
    escape=sum(rr[s]*CHI[s] for s in range(3))+dr*CHI[1]+rec_loss+dr_loss
    return [H*z for z in material+photon+[theta_dot,escape]]

def run(N):
    v=list(map(m,['.1','.9']))+[F*m('.1'),F*m('.3'),F*m('.6')]+list(map(m,['.05','.005','.001']))+[mp.log(m(50000)),m(0)]
    dt=m(1)/N
    for _ in range(N):
        a=rhs(v);b=rhs([x+dt*y/2 for x,y in zip(v,a)]);c=rhs([x+dt*y/2 for x,y in zip(v,b)]);d=rhs([x+dt*y for x,y in zip(v,c)])
        v=[x+dt*(y+2*z+2*w+r)/6 for x,y,z,w,r in zip(v,a,b,c,d)]
    red=[v[1],v[3]/F,v[4]/F,v[8]]
    T=mp.exp(v[8]);e=v[1]+v[3]+2*v[4];nu=sum(v[:5])+e
    W=m('1.5')*KB*T*nu/EV
    B=CHI[0]*v[1]+CHI[1]*v[3]+(CHI[1]+CHI[2])*v[4]
    E=W+B+sum(EG[g]*v[5+g] for g in range(3))+v[9]
    nu0=1+F+m('.9')+F*(m('.3')+2*m('.6'))
    E0=m('1.5')*KB*50000*nu0/EV+CHI[0]*m('.9')+F*(CHI[1]*m('.3')+(CHI[1]+CHI[2])*m('.6'))+sum(a*b for a,b in zip(EG,map(m,['.05','.005','.001'])))
    return {'N':N,'reduced':list(map(str,red)),'final_T_K':str(T),'state':list(map(str,v)),
     'energy_residual_eV_per_H':str(E-E0),'H_nuclei_residual':str(sum(v[:2])-1),'He_nuclei_residual':str(sum(v[2:5])-F)}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--steps',type=int,nargs='+',default=[128,256,512,1024]);args=ap.parse_args()
    start=time.perf_counter();runs=[run(n) for n in args.steps]
    data={'working_digits':50,'runs':runs,'wall_seconds':time.perf_counter()-start,'independent_state':'five species and logarithmic T, derivatives from mpmath.diff; no float RHS import'}
    if len(runs)>=3:
        vecs=[[m(z) for z in r['reduced']] for r in runs]
        norm=lambda v:max(abs(z) for z in v)
        errs=[norm([b-a for a,b in zip(v,w)]) for v,w in zip(vecs,vecs[1:])]
        ratios=[a/b for a,b in zip(errs,errs[1:])]
        data['successive_differences']=list(map(str,errs));data['ratios']=list(map(str,ratios))
        ext=[b+(b-a)/15 for a,b in zip(vecs[-2],vecs[-1])]
        dd=json.loads((ROOT/'results/float_reference.json').read_text())['DOP853']
        dvec=[m(str(z)) for z in dd['endpoint'][:3]]+[mp.log(m(str(dd['final_T_K'])))]
        dif=norm([a-b for a,b in zip(ext,dvec)])
        data['richardson_reduced']=list(map(str,ext));data['richardson_vs_DOP853']=str(dif)
        assert dif<m('2e-9')
        assert all(12<r<25 for r in ratios[-2:])
    (ROOT/'results/mp_reference.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='runs'},indent=2))
