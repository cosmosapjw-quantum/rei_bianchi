"""HE17 R4 local reconstruction pilot. No ODE or native producer is invoked.
Long-double exploratory arithmetic is NOT a directed interval certificate.
"""
from __future__ import annotations
from pathlib import Path
import json, hashlib, time
import numpy as np
from fractions import Fraction as Q
L=np.longdouble
ROOT=Path(__file__).resolve().parents[1]
C=L('29979245800'); EV=L('1.602176634e-12'); KB=L('1.380649e-16')
CHI=np.array(['13.598434599702','24.587389011','54.41776'],dtype=L)
FF=L(3)/38; PI=np.arccos(L(-1)); HBAR_NOT_NORMALIZED=True
class Source:
    def __init__(self):
        self.rhs_calls=0;self.environment_calls=0
        with np.load(ROOT/'inputs/P01_STATE.npz',allow_pickle=False) as f:
            self.q=f['q_eV'].astype(L);self.mu=f['mu0'].astype(L);self.weights=f['weights'].astype(L)
            self.y=f['states'][:2908].astype(L);self.times=f['times_s'].astype(L)
        vals=[]
        for line in (ROOT/'inputs/emissivity.out').read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#'): vals.append([L(x) for x in line.split()])
        self.zgrid=np.array(vals[0]);tab=np.array(vals[1:]);self.wave=tab[:,0]
        self.energies=(L('6.62607015e-27')*C/EV*L('1e8')/self.wave)[::-1]
        self.tab=tab[:,1:][::-1];self.Mpc=648000/PI*L('149597870700')*100*L('1e6')
        self.zi=L('5.807');self.ai=1/(1+self.zi);self.vi=self.ai**3
        self.hf=L('70')*L('1e5')/L('3.0856775814913673e24')
        self.B=self.hf**2*L('.3');self.D=self.hf**2*L('.7')
        self.Hi=np.sqrt((self.B/self.vi+self.D)/(1-L('.001')**2))
        self.si=L('.001')*self.Hi;self.s0=self.si*self.vi;self.G=self.s0**2
        self.om=3*np.sqrt(self.D);self.ri=np.sqrt(self.D*self.vi**2+self.B*self.vi+self.G)
        rhob=L('.045')*3*self.hf**2/(8*PI*L('6.67430e-8'))
        self.nh0=L('.76')*rhob/L('1.67262192369e-24')/self.vi
        self.nhe0=L('.24')*rhob/(4*L('1.67262192369e-24'))/self.vi
        x,w=np.polynomial.legendre.leggauss(12);self.gx=(x.astype(L)+1)/2;self.gw=w.astype(L)/2
        self.cache={}
    def vol(self,t):
        xx=self.om*t;cm=2*np.sinh(xx/2)**2
        return self.vi*(1+cm+self.ri/(self.vi*np.sqrt(self.D))*np.sinh(xx)+self.B/(2*self.D*self.vi)*cm)
    def env(self,t):
        t=L(t); key=str(t)
        if key in self.cache:return self.cache[key]
        if not 0<=t<=self.times[-1]:raise ValueError('TIME_OUTSIDE_SOURCE')
        self.environment_calls+=1
        v=self.vol(t);vol=v/self.vi;a=np.cbrt(vol)
        b=t*np.sum(self.gw*self.s0/self.vol(t*self.gx),dtype=L)
        h=np.sqrt(self.D+self.B/v+self.G/v**2);nh=self.nh0/vol;nhe=self.nhe0/vol
        R=np.sqrt((1-self.mu**2)*np.exp(2*b)+self.mu**2*np.exp(-4*b))/a
        E=self.q*R;z=self.zi if t==0 else (1+self.zi)/a-1
        zi=int(np.searchsorted(self.zgrid,z,side='left'))
        if z==self.zgrid[zi]: prof=self.tab[:,zi]
        else:
            f=(z-self.zgrid[zi-1])/(self.zgrid[zi]-self.zgrid[zi-1]);prof=(1-f)*self.tab[:,zi-1]+f*self.tab[:,zi]
        idx=np.searchsorted(self.energies,E,side='right')-1
        frac=np.log(E/self.energies[idx])/np.log(self.energies[idx+1]/self.energies[idx])
        eps=(1-frac)*prof[idx]+frac*prof[idx+1]
        source=eps*(1+z)**3/(self.Mpc**3*L('6.62607015e-27'))*self.weights/R**3
        sigma=[]
        for p in [('13.60','.4298','5.475e4','32.88','2.963','0','0','0'),('24.59','13.61','949.2','1.469','3.188','2.039','.4434','2.136'),('54.42','1.720','1.369e4','32.88','2.963','0','0','0')]:
            eth,e0,s0,ya,pw,yw,y0,y1=map(L,p);xx=E/e0-y0;yy=np.sqrt(xx*xx+y1*y1)
            sig=s0*((xx-1)**2+yw*yw)*yy**(pw/2-L('5.5'))*(1+np.sqrt(yy/ya))**(-pw)*L('1e-18')
            sigma.append(np.where(E>=eth,sig,0))
        out=(nh,nhe,vol,h,E,np.array(sigma),source);self.cache[key]=out;return out
    def rates(self,T):
        lam=np.array(['315614','570670','1263030'],dtype=L)/T
        rr=np.empty(3,dtype=L);gg=np.zeros(3,dtype=L)
        for i in range(3):
            if i==1:rr[i]=L('3e-14')*lam[i]**L('.654');gg[i]=L('-.654')
            else:
                u=(lam[i]/L('.522'))**L('.470');rr[i]=(2 if i==2 else 1)*L('1.269e-13')*lam[i]**L('1.503')/(1+u)**L('1.923');gg[i]=-L('1.503')+L('1.923')*L('.470')*u/(1+u)
        aa=np.array(['21.11','32.38','19.95'],dtype=L);pp=np.array(['-1.089','-1.146','-1.089'],dtype=L)
        c0=np.array(['.354','.416','.553'],dtype=L);r=np.array(['.874','.987','.735'],dtype=L);dd=np.array(['1.101','1.056','1.275'],dtype=L)
        ci=aa*T**L('-1.5')*np.exp(-lam/2)*lam**pp/(1+(lam/c0)**r)**dd
        b1=L('40.49664394833662')*11605;b2=L('8.099328789667')*11605
        en=np.array([b1,b1+b2],dtype=L);dr=L('1.54e-9')*L(11605)**L('1.5')*T**L('-1.5')*np.exp(-en/T)*np.array([1,L('.3')])
        return ci,rr,KB*T*rr*(L('1.5')+gg),dr,KB*en
    def opacity(self,t,g):
        nh,nhe,vol,h,E,sig,source=self.env(t);x,y,z,w=g
        lower=np.array([nh*(1-x),nhe*(1-y-z),nhe*y]);return C*(lower@sig),source
    def rhs(self,t,state):
        self.rhs_calls+=1
        nh,nhe,vol,h,E,sig,source=self.env(t);x,y,z,w=state[:4];phot=state[4:]/vol
        ne=nh*x+nhe*(y+2*z);T=2*EV*w/(3*KB*(1+nhe/nh+ne/nh))
        if not L(30000)<=T<=L(110000):raise ValueError('FT03_TEMPERATURE_DOMAIN')
        lower=np.array([nh*(1-x),nhe*(1-y-z),nhe*y]);upper=np.array([nh*x,nhe*y,nhe*z])
        ci,rr,kin,dr,drenergy=self.rates(T);CI=lower*ne*ci;RR=upper*ne*rr;RK=upper*ne*kin;DR=upper[1]*ne*dr
        photo=C*lower[:,None]*sig*phot[None,:];photoSum=np.sum(photo,axis=1,dtype=L)
        net=CI-RR+photoSum;net[1]-=np.sum(DR,dtype=L)
        heat=np.sum(photo*(E[None,:]-CHI[:,None])*EV,dtype=L)-np.sum(CI*CHI*EV+RK,dtype=L)-np.sum(DR*drenergy,dtype=L)
        gas=np.array([net[0]/nh,(net[1]-net[2])/nhe,net[2]/nhe,-2*h*w+heat/(nh*EV)])
        pdot=source-vol*np.sum(photo,axis=0,dtype=L)
        gross=np.array([(CI[0]+RR[0]+photoSum[0])/nh,(np.sum(CI[1:]+RR[1:]+photoSum[1:])+np.sum(DR))/nhe,(CI[2]+RR[2]+photoSum[2])/nhe,L('1e-14')])
        return np.r_[gas,pdot], {'T':T,'gross':gross,'net':net}

def Hval(v0,v1,m0,m1,h,z):
    z=L(z);d=v1-v0;a=h*m0;b=3*d-h*(2*m0+m1);c=-2*d+h*(m0+m1)
    return v0+z*(a+z*(b+z*c)),(a+z*(2*b+3*z*c))/h

def PLval(v0,v1,h,z):return v0+L(z)*(v1-v0),(v1-v0)/h

def qfloat(x):return Q(*float(x).as_integer_ratio())

def main():
    start=time.perf_counter();s=Source();h=s.times[1]-s.times[0];v0=s.y[:,0];v1=s.y[:,1]
    m0,info0=s.rhs(0,v0);m1,info1=s.rhs(h,v1)
    # The fixed reference uses binary64 slope tokens interpreted as exact dyadics.
    m0=m0.astype(float).astype(L);m1=m1.astype(float).astype(L)
    rows=[];scale=np.array([1,1,1,32],dtype=L);normp=np.sum(v0[4:],dtype=L)
    for z in np.linspace(0,1,9):
        for label in ['PL','HERMITE']:
            v,dv=PLval(v0,v1,h,z) if label=='PL' else Hval(v0,v1,m0,m1,h,z)
            f,info=s.rhs(L(z)*h,v);res=dv-f
            rows.append(dict(candidate=label,z=str(z),gas_scaled_max=str(np.max(np.abs(res[:4])/scale)),photon_l1_normalized=str(np.sum(np.abs(res[4:]),dtype=L)/normp),gas_residual=[str(x) for x in res[:4]],temperature=str(info['T'])))
    # Force the photon part without integrating a source IVP: nested positive GL quadrature.
    # The cell's left anchor is the actual initial state, so there is no previous-cell error here.
    def lifted(z,n):
        gx,gw=np.polynomial.legendre.leggauss(n);gx=(gx.astype(L)+1)/2;gw=gw.astype(L)/2;t=L(z)*h
        def gv(t0):return Hval(v0[:4],v1[:4],m0[:4],m1[:4],h,t0/h)[0]
        def kval(t0):return s.opacity(t0,gv(t0))[0]
        K=t*np.sum(np.array([w*kval(t*x) for x,w in zip(gx,gw)]),axis=0,dtype=L)
        acc=np.zeros(len(s.q),dtype=L)
        for x,w in zip(gx,gw):
            ts=t*x;d=t-ts
            Ktail=d*np.sum(np.array([wi*kval(ts+d*xi) for xi,wi in zip(gx,gw)]),axis=0,dtype=L)
            src=s.env(ts)[-1];acc+=w*np.exp(-Ktail)*src
        return np.exp(-K)*v0[4:]+t*acc
    forced=[]
    for z in [L('.5'),L(1)]:
        p8=lifted(z,8);p12=lifted(z,12)
        g,dg=Hval(v0[:4],v1[:4],m0[:4],m1[:4],h,z);f,_=s.rhs(z*h,np.r_[g,p12]);res=dg-f[:4]
        forced.append(dict(z=str(z),gas_scaled_max=str(np.max(np.abs(res)/scale)),photon_rule_8_12_l1_normalized=str(np.sum(np.abs(p8-p12),dtype=L)/normp),anchor_mismatch_l1_normalized=str(np.sum(np.abs(p12-v1[4:]),dtype=L)/normp) if z==1 else None))
    # Whole-cell polynomial-domain checks using exact Bernstein control points, not samples.
    hh=qfloat(h);g0=[qfloat(v) for v in v0[:4]];g1=[qfloat(v) for v in v1[:4]]
    c0=g0;c1=[g0[i]+hh*qfloat(m0[i])/3 for i in range(4)];c2=[g1[i]-hh*qfloat(m1[i])/3 for i in range(4)];c3=g1
    radii=list(map(Q,['1e-7','2e-7','2e-7','1e-4']));gasbox=all(abs(c[i]-g0[i])<=radii[i] for c in [c0,c1,c2,c3] for i in range(4))
    Ctemp=2*Q('1.602176634e-19')/(3*Q('1.380649e-23'));ff=Q(3,38)
    controls=[c0,c1,c2,c3]
    simplex=all(0<=c[0]<=1 and c[1]>=0 and c[2]>=0 and c[1]+c[2]<=1 for c in controls)
    thermal=all(Q(30000)*(1+ff+c[0]+ff*(c[1]+2*c[2]))<=Ctemp*c[3]<=Q(110000)*(1+ff+c[0]+ff*(c[1]+2*c[2])) for c in controls)
    positive=all(qfloat(v0[4+i])+hh*qfloat(m0[4+i])/3>=0 and qfloat(v1[4+i])-hh*qfloat(m1[4+i])/3>=0 for i in range(len(s.q)))
    probe=[]
    for label,k in [('initial_IC',0),('retained_final_saved_stage_probe',16)]:
        raw=json.loads((ROOT/f'inputs/{label}_RHS.json').read_text())['values'];val,info=s.rhs(s.times[k],s.y[:,k]);orig=np.array(raw[:4]+raw[14:],dtype=L)
        probe.append(dict(label=label,gas_gross_normalized=str(np.max(np.abs(val[:4]-orig[:4])/info['gross'])),photon_max_relative=str(np.max(np.abs(val[4:]-orig[4:])/np.maximum(np.abs(orig[4:]),L('1e-60'))))))
    np.savez_compressed(ROOT/'results/FIXED_REFERENCE.npz',left=np.array(v0,dtype=float),right=np.array(v1,dtype=float),slope_left=np.array(m0,dtype=float),slope_right=np.array(m1,dtype=float),h=float(h))
    out=dict(stage='R4',cell=[str(s.times[0]),str(s.times[1])],arithmetic='NumPy longdouble exploratory; not directed',longdouble_mantissa=np.finfo(L).nmant,rows=rows,forced_photon=forced,whole_cell_exact_Bernstein=dict(gas_box=gasbox,simplex=simplex,temperature_domain=thermal,photon_positivity=positive),endpoint_source_crosscheck=probe,rhs_calls=s.rhs_calls,environment_evaluations=s.environment_calls,old_ODE_calls=0,native_calls=0,elapsed_seconds=time.perf_counter()-start)
    (ROOT/'results/PILOT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
