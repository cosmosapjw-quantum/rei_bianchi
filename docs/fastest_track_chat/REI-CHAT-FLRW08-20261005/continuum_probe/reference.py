"""Independent analytic FT03/Verner + projected fixed-grid transport ODE.

No Rust RHS import or execution. Original native sigma samples bind the fit.
State: gas4, direction-major photons, guard N, guard U, six ledgers.
Time coordinate tau=t/1e10. No clipping of state or rates.
"""
import numpy as np
from scipy.integrate import solve_ivp

FHE=.083; KB=1.380649e-16; EV=1.602176634e-12; C=29979245800.
CHI=np.array([13.598434599702,24.587389011,54.41776])
L=np.array([315614.,570670.,1263030.]); SOURCE=5e-15; BIRTH=13.7; END=1e10
HUBBLE={'FLRW':np.array([1e-14]*3),'BI':np.array([1.01e-14,.99e-14,1e-14])}

def coefficients(t):
    if not np.isfinite(t) or not 30000<=t<=110000: raise ValueError('FT03_TEMPERATURE_DOMAIN')
    l=L/t; u=(l/.522)**.470
    rr=np.array([1.,2.,2.])*1.269e-13*l**1.503/(1+u)**1.923
    rr[1]=3e-14*l[1]**.654
    slope=-1.503+1.923*.470*u/(1+u);slope[1]=-.654
    kinetic=KB*t*rr*(1.5+slope)
    ci=np.array([21.11,32.38,19.95])*t**-1.5*np.exp(-l/2)*l**np.array([-1.089,-1.146,-1.089])/(1+(l/np.array([.354,.416,.553]))**np.array([.874,.987,.735]))**np.array([1.101,1.056,1.275])
    b1=40.49664394833662*11605.;b2=8.099328789667*11605.
    dr=1.54e-9*11605.**1.5*t**-1.5*np.exp(-np.array([b1,b1+b2])/t)*np.array([1.,.3])
    return rr,ci,kinetic,dr,KB*np.array([b1,b1+b2])

def cross_sections(energies):
    out=[]
    for e in energies:
        row=[]
        for eth,e0,s0,ya,p,yw,y0,y1 in [(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]:
            if e<eth:row.append(0.);continue
            x=e/e0-y0;y=np.sqrt(x*x+y1*y1)
            row.append(s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-18)
        out.append(row)
    return np.array(out)

class Reference:
    def __init__(self,native,geometry):
        self.e=np.array(native['energy_ev']);self.q=np.array(native['qhat']);self.h=HUBBLE[geometry]
        self.nd,self.n=len(self.q),len(self.e);self.np=self.nd*self.n
        # Use independently evaluated sigma after native-sample agreement is tested.
        self.sigma=cross_sections(self.e);self.birth=int(np.flatnonzero(self.e==BIRTH)[0])
        s=native['initial'];self.initial=np.concatenate([s['gas'],s['photons'],s['lower_guard_n'],s['lower_guard_u'],s['ledgers']])
        self.scale=np.concatenate([[1.,1.,1.,s['gas'][3]],np.full(self.np,.05),np.full(self.nd,.05),np.full(self.nd,.05*BIRTH),[s['gas'][3],.05*BIRTH,s['gas'][3],.05,.05*BIRTH,.05]])
    def unpack(self,y):
        a=4+self.np;b=a+self.nd;c=b+self.nd
        return y[:4],y[4:a].reshape(self.nd,self.n),y[a:b],y[b:c],y[c:]
    def weights_hd(self,t):
        z=self.q**2*np.exp(-2*self.h*t);g2=z.sum(axis=1);hd=(z*self.h).sum(axis=1)/g2
        raw=np.exp(-self.h.sum()*t)/g2**1.5
        return raw/raw.sum(),hd
    def transport(self,p,un,t):
        _,hd=self.weights_hd(t)
        rate=hd[:,None]*self.e[None,1:]/np.diff(self.e)[None,:]
        flux=p[:,1:]*rate;dp=np.zeros_like(p)
        dp[:,1:]-=flux;dp[:,1:-1]+=flux[:,1:]
        # P transfers lowest10eV population directly to guard; p0 remains zero.
        dn=flux[:,0];du=-hd*un+10*dn
        work=(hd*((p*self.e).sum(axis=1)+un)).sum()
        return dp,dn,du,work
    def temperature(self,gas):
        x,a,b,w=gas;return 2*w*EV/(3*KB*(1+FHE+x+FHE*(a+2*b)))
    def rhs(self,tau,y):
        t=tau*END;gas,p,gn,gu,ledgers=self.unpack(y);x,a,b,w=gas
        rr,ci,kin,dr,de=coefficients(self.temperature(gas))
        nh=1e-4*np.exp(-self.h.sum()*t);ne=nh*(x+FHE*(a+2*b))
        lower=np.array([1-x,FHE*(1-a-b),FHE*a]);upper=np.array([x,FHE*a,FHE*b])
        collision=lower*ne*ci;recombination=upper*ne*rr;dielectronic=upper[1]*ne*dr
        photo=C*nh*lower*(p.sum(axis=0)@self.sigma)
        j=collision-recombination+photo;j[1]-=dielectronic.sum()
        kinetic_loss=(upper*ne*kin).sum()/EV;dr_loss=(dielectronic*de).sum()/EV
        heat=C*nh*np.sum(p.sum(axis=0)[:,None]*self.sigma*lower*(self.e[:,None]-CHI))
        thermal=2*self.h.mean()*w
        dw=heat-(collision*CHI).sum()-kinetic_loss-dr_loss-thermal
        escape=(recombination*CHI).sum()+dielectronic.sum()*CHI[1]+kinetic_loss+dr_loss
        dp,dgn,dgu,work=self.transport(p,gu,t)
        weights,_=self.weights_hd(t);dp[:,self.birth]+=SOURCE*weights
        opacity=C*nh*(self.sigma@lower);dp-=p*opacity[None,:]
        dy=np.concatenate([[j[0],(j[1]-j[2])/FHE,j[2]/FHE,dw],dp.ravel(),dgn,dgu,[escape,work,thermal,SOURCE,SOURCE*BIRTH,photo.sum()]])
        return END*dy
    def project(self,y):
        z=y.copy();_,p,gn,gu,_=self.unpack(z);gn+=p[:,0];gu+=10*p[:,0];p[:,0]=0
        return z
    def from_native(self,s):
        return np.concatenate([s['gas'],s['photons'],s['lower_guard_n'],s['lower_guard_u'],s['ledgers']])
    def observables(self,y):
        gas,p,gn,gu,ledgers=self.unpack(y)
        return np.concatenate([gas,[self.temperature(gas)],p.sum(axis=0),[gn.sum(),gu.sum(),p.sum()+gn.sum(),(p*self.e).sum()+gu.sum()],ledgers])
    def solve(self,method):
        atol=self.scale*2e-15
        sol=solve_ivp(self.rhs,(0.,1.),self.initial,method=method,rtol=2e-12,atol=atol,max_step=.025,dense_output=True)
        if not sol.success:raise RuntimeError(sol.message)
        samples=sol.sol(np.linspace(0,1,201));g=samples[:4]
        temps=np.array([self.temperature(v) for v in g.T])
        if not (np.all(np.isfinite(samples)) and np.all(g[:3]>=0) and np.all(g[0]<=1) and np.all(g[1]+g[2]<=1) and np.all((temps>=35000)&(temps<=60000))):raise ValueError('REFERENCE_DOMAIN')
        n0,u0=self.balances(self.initial);balance=np.array([self.balances(v) for v in samples.T])
        a=4+self.np;b=a+self.nd;c=b+self.nd
        return sol.y[:,-1],{'method':method,'nfev':sol.nfev,'accepted_internal_steps':len(sol.t)-1,'rtol':2e-12,'atol_rule':'2e-15 times declared coordinate scale','coordinate_scale':self.scale.tolist(),'max_step_tau':.025,'temperature_range_k':[float(temps.min()),float(temps.max())],'domain_samples':201,'gas_simplex_pass':True,'dense_samples_finite':True,'minimum_sampled_photon':float(samples[4:a].min()),'minimum_sampled_guard_n':float(samples[a:b].min()),'minimum_sampled_guard_u':float(samples[b:c].min()),'minimum_endpoint_photon':float(sol.y[4:a,-1].min()),'minimum_endpoint_guard_n':float(sol.y[a:b,-1].min()),'minimum_endpoint_guard_u':float(sol.y[b:c,-1].min()),'max_number_ledger_residual_per_h':float(np.max(np.abs(balance[:,0]-n0))),'max_energy_ledger_residual_ev_per_h':float(np.max(np.abs(balance[:,1]-u0))),'positivity_claim':'MEASURED_COORDINATES_ONLY; no clipping, no rigorous positivity enclosure'}
    def balances(self,y):
        gas,p,gn,gu,l=self.unpack(y);x,a,b,w=gas
        return p.sum()+gn.sum()+l[5]-l[3],w+CHI[0]*x+FHE*(CHI[1]*a+(CHI[1]+CHI[2])*b)+(p*self.e).sum()+gu.sum()+l[0]+l[1]+l[2]-l[4]
