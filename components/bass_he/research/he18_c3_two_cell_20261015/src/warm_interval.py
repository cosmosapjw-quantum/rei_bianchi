"""Same-source interval/Taylor evaluator. It never imports/runs an ODE producer.
CGS inside source; fixed stored dyadic state/slope arrays; decimal model constants.
All mathematical evaluations and automatic differentiation use outward intervals.
"""
from pathlib import Path
from fractions import Fraction as Q
import bisect, json, time
import numpy as np
from mpmath import iv
from interval_jet import Jet, val as V, bound, endpoints, absup, lo, hi, record, polynomial
ROOT=Path(__file__).resolve().parents[1]
C=V('29979245800'); EV=V('1.602176634e-12'); KB=V('1.380649e-16'); FF=V(Q(3,38))
CHI=[V(x) for x in ('13.598434599702','24.587389011','54.41776')]
PARAMS=[tuple(V(x) for x in p) for p in [
('13.60','.4298','5.475e4','32.88','2.963','0','0','0'),
('24.59','13.61','949.2','1.469','3.188','2.039','.4434','2.136'),
('54.42','1.720','1.369e4','32.88','2.963','0','0','0')]]
class WarmSource:
    def __init__(self):
        with np.load(ROOT/'inputs/P01_STATE.npz',allow_pickle=False) as d:
            self.q=[V(float(x)) for x in d['q_eV']];self.mu2=[V(Q.from_float(float(x))**2) for x in d['mu0']]
            self.weights=[V(float(x)) for x in d['weights']];self.initial=d['initial_state'].copy()
        with np.load(ROOT/'inputs/FIXED_REFERENCE.npz',allow_pickle=False) as d:
            self.h=V(float(d['h']));self.hq=Q.from_float(float(d['h']));self.n=len(d['left'])
            self.coeff=[];self.controls=[]
            for a,b,aa,bb in zip(d['left'],d['right'],d['slope_left'],d['slope_right']):
                a,b,aa,bb=map(lambda v:Q.from_float(float(v)),(a,b,aa,bb));h=self.hq
                self.coeff.append([a,h*aa,3*(b-a)-h*(2*aa+bb),-2*(b-a)+h*(aa+bb)])
                self.controls.append([a,a+h*aa/3,b-h*bb/3,b])
        raw=[]
        for l in (ROOT/'inputs/emissivity.out').read_text().splitlines():
            if l.strip() and not l.lstrip().startswith('#'):raw.append(l.split())
        self.zgrid=list(map(V,raw[0]));waves=[V(r[0]) for r in raw[1:]][::-1]
        self.tab=[list(map(V,r[1:])) for r in raw[1:]][::-1]
        hc=V('6.62607015e-27')*C/EV*V('1e8');self.knots=[hc/w for w in waves]
        self.knot_mid=[float((lo(k)+hi(k))/2) for k in self.knots]
        zz=list(map(float,raw[0]));self.zindex=zz.index(5.807); assert self.zindex>0
        self.zlower=self.zgrid[self.zindex-1];self.zupper=self.zgrid[self.zindex]
        self.mpc=648000/iv.pi*V('149597870700')*100*V('1e6')
        self.vi=1/V('6.807')**3;hf=70*V('1e5')/V('3.0856775814913673e24')
        self.B=hf**2*V('.3');self.D=hf**2*V('.7');self.Hi=iv.sqrt((self.B/self.vi+self.D)/(1-V('.001')**2))
        self.si=V('.001')*self.Hi;self.s0=self.si*self.vi;self.G=self.s0**2;self.om=3*iv.sqrt(self.D)
        self.ri=iv.sqrt(self.D*self.vi**2+self.B*self.vi+self.G)
        rho=V('.045')*3*hf**2/(8*iv.pi*V('6.67430e-8'))
        self.nh0=V('.76')*rho/V('1.67262192369e-24')/self.vi
        self.shear_anchor_log=[]
    def global_volume(self,z):
        # Global time from the original initial datum, measured in first-cell h.
        x=z*(self.om*self.h);cm=2*(x/2).sinh()**2
        return 1+cm*(1+self.B/(2*self.D*self.vi))+x.sinh()*(self.ri/(self.vi*iv.sqrt(self.D)))
    def volume(self,z):
        # The selected second saved cell begins at global time t=h.
        return self.global_volume(z+1)
    def shear_anchor(self,x,degree=8):
        # b(x)=h*si*int_0^x 1/vol(s)ds. Taylor at0 with an interval derivative remainder.
        xq=lo(x)+1
        if lo(x)!=hi(x):
            if xq<1 or hi(x)+1>2:raise ValueError('SECOND_CELL_SHEAR_DOMAIN')
            return bound(0,2*self.h*self.si)
        if xq==0:return V(0)
        a=self.global_volume(Jet.variable(0,degree)).reciprocal()
        r=self.global_volume(Jet.variable(bound(0,xq),degree)).reciprocal()
        p=sum((a.c[k]*V(xq)**(k+1)/(k+1) for k in range(degree)),V(0))
        rem=absup(r.c[degree])*xq**(degree+1)/(degree+1)
        v=self.h*self.si*(p+bound(-rem,rem))
        self.shear_anchor_log.append({'x':str(xq),'degree':degree,'integral_remainder':str(rem),'b':record(v)})
        return v
    def env(self,z):
        vr=self.volume(z); inv=vr.reciprocal();a=vr**Q(1,3)
        bs=[self.shear_anchor(z.c[0])]+[self.h*self.si*inv.c[k-1]/k for k in range(1,z.n+1)]
        b=Jet(bs);vv=vr*self.vi;H=(vv.reciprocal()*self.B+(vv**-2)*self.G+self.D).sqrt()
        nh=vr.reciprocal()*self.nh0;zcos=a.reciprocal()*V('6.807')-1
        # The initial upper-slab endpoint is handled from below; arithmetic enclosures may straddle by roundoff.
        fz=(zcos-self.zlower)/(self.zupper-self.zlower)
        return {'vr':vr,'a':a,'b':b,'H':H,'nh':nh,'fz':fz,'zcos':zcos,
                'e2b':(2*b).exp(),'em4b':(-4*b).exp()}
    def node(self,j,env):
        R=(env['e2b']*(1-self.mu2[j])+env['em4b']*self.mu2[j]).sqrt()/env['a']
        E=R*self.q[j]
        # An approximate index is only a candidate; the enclosure is checked before use.
        idx=bisect.bisect_right(self.knot_mid,float(lo(self.q[j])))-1
        if idx<0 or idx+1>=len(self.knots):raise ValueError('SOURCE_KNOT_INDEX')
        if not(lo(E.c[0])>hi(self.knots[idx]) and hi(E.c[0])<lo(self.knots[idx+1])):
            raise ValueError('SOURCE_BRANCH_NOT_CERTIFIED')
        f=(E/self.knots[idx]).log()/iv.log(self.knots[idx+1]/self.knots[idx])
        def prof(k):
            return (1-env['fz'])*self.tab[k][self.zindex-1]+env['fz']*self.tab[k][self.zindex]
        eps=(1-f)*prof(idx)+f*prof(idx+1)
        src=eps*(1+env['zcos'])**3/(self.mpc**3*V('6.62607015e-27'))*self.weights[j]/R**3
        sig=[]
        for eth,e0,s0,ya,p,yw,y0,y1 in PARAMS:
            if hi(E.c[0])<lo(eth):sig.append(Jet.constant(0,E.n));continue
            if lo(E.c[0])<hi(eth):raise ValueError('ACTIVATION_BRANCH_NOT_CERTIFIED')
            X=E/e0-y0;Y=(X*X+y1*y1).sqrt()
            sig.append(((X-1)**2+yw*yw)*s0*(Y**(p/2-V('5.5')))*((1+(Y/ya).sqrt())**(-p))*V('1e-18'))
        if hi(E.c[0])>50000:raise ValueError('VERNER_CEILING')
        return E,sig,src
    def state(self,z):return [polynomial(c,z) for c in self.coeff]
    def derivative(self,z):return [polynomial([c[1],2*c[2],3*c[3]],z) for c in self.coeff]
    def gas(self,g,nh,H,Gamma,Qphoto):
        x,y,z,w=g;chi=x+(y+2*z)*FF;ne=nh*chi;T=w*(2*EV)/((chi+1+FF)*(3*KB))
        lf=[1-x,(1-y-z)*FF,y*FF];uf=[x,y*FF,z*FF]
        ci=[];rr=[];rk=[]
        for a,(l0,ca,cp,cc,cr,cd) in enumerate(zip(['315614','570670','1263030'],['21.11','32.38','19.95'],['-1.089','-1.146','-1.089'],['.354','.416','.553'],['.874','.987','.735'],['1.101','1.056','1.275'])):
            l=T.reciprocal()*V(l0)
            if a==1:al=(l**V('.654'))*V('3e-14');slope=Jet.constant(V('-.654'),T.n)
            else:
                u=(l/V('.522'))**V('.470');al=(l**V('1.503'))*((2 if a==2 else 1)*V('1.269e-13'))/((1+u)**V('1.923'))
                slope=u/(1+u)*(V('1.923')*V('.470'))-V('1.503')
            beta=(T**V('-1.5'))*V(ca)*(-l/2).exp()*(l**V(cp))/((1+(l/V(cc))**V(cr))**V(cd))
            ci.append(ne*lf[a]*beta);rr.append(ne*uf[a]*al);rk.append(ne*uf[a]*KB*T*al*(slope+V('1.5'))/EV)
        en=[V('40.49664394833662')*11605,(V('40.49664394833662')+V('8.099328789667'))*11605]
        dr=[ne*factor*uf[1]*V('1.54e-9')*(V(11605)**V('1.5'))*(T**V('-1.5'))*(-T.reciprocal()*e).exp() for factor,e in zip([1,V('.3')],en)]
        net=[ci[a]-rr[a]+lf[a]*Gamma[a] for a in range(3)];net[1]=net[1]-dr[0]-dr[1]
        heat=sum((lf[a]*Qphoto[a]-ci[a]*CHI[a]-rk[a] for a in range(3)),Jet.constant(0,T.n))-sum((dr[a]*KB*en[a]/EV for a in range(2)),Jet.constant(0,T.n))
        return [net[0],(net[1]-net[2])/FF,net[2]/FF,-2*H*w+heat]
    def evaluate(self,domain,order=3,label='evaluation'):
        start=time.perf_counter();z=Jet.variable(domain,order);env=self.env(z);y=self.state(z);dy=self.derivative(z)
        gm=[Jet.constant(0,order) for _ in range(3)];qp=[Jet.constant(0,order) for _ in range(3)]
        rp=[];node_values=[];cache={}
        for j in range(len(self.q)):
            key=(self.q[j]._mpi_,self.mu2[j]._mpi_)
            if key not in cache:
                E,sigma,src=self.node(j,env);cache[key]=(E,sigma,src/self.weights[j])
            E,sigma,srcunit=cache[key];src=srcunit*self.weights[j]
            chi=y[0]+(y[1]+2*y[2])*FF;lf=[1-y[0],(1-y[1]-y[2])*FF,y[1]*FF]
            kap=sum((env['nh']*C*lf[a]*sigma[a] for a in range(3)),Jet.constant(0,order))
            N=y[4+j]
            for a in range(3):
                v=sigma[a]*C*N/env['vr'];gm[a]=gm[a]+v;qp[a]=qp[a]+v*(E-CHI[a])
            rp.append(dy[4+j]-(src-kap*N)*self.h)
            node_values.append({'E':E.c[0],'sigma':[s.c[0] for s in sigma],'source':src.c[0], 'N':N.c[0]})
            if (j+1)%500==0:print(label,'nodes',j+1,'elapsed',round(time.perf_counter()-start,2),flush=True)
        gas=self.gas(y[:4],env['nh'],env['H'],gm,qp)
        rg=[dy[a]-gas[a]*self.h for a in range(4)]
        return {'gas':rg,'photon':rp,'env':env,'nodes':node_values,'gamma':gm,'qphoto':qp,'seconds':time.perf_counter()-start}
