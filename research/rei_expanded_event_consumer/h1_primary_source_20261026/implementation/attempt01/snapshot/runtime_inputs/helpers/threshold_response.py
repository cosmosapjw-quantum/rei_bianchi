"""Positive threshold response of continuous isotropic births; no IVP/opacity.
All energies eV, inventories per Href. Source/background remain prescribed.
"""
from functools import lru_cache
import math
import numpy as np
from scipy.optimize import brentq


@lru_cache(None)
def rule(n):
    x,w=np.polynomial.legendre.leggauss(n)
    return (x+1)/2,w/2


def directional_expansion_certificate(background):
    """Exact extrema of quadratic derivative on each stored cubic segment."""
    bounds=[]
    for i,(lo,hi) in enumerate(zip(background.shear.x[:-1],background.shear.x[1:])):
        c=background.shear.c[:,i];h=hi-lo;xs=[0.,h]
        if c[0]!=0:
            vertex=-c[1]/(3*c[0])
            if 0<vertex<h:xs.append(vertex)
        values=[3*c[0]*x*x+2*c[1]*x+c[2] for x in xs]
        bounds.extend(values)
    low,high=min(bounds),max(bounds)
    return {'bprime_min':float(low),'bprime_max':float(high),
            'Hperp_over_H_min':float(1-high),'Hparallel_over_H_min':float(1+2*low),
            'positive_directional_expansion':bool(high<1 and low>-.5)}


def time_nodes(background,eta_o,chi,support,birth_order,mean_only=False):
    """Split donor cubics and all endpoint support crossings before GL."""
    if eta_o==0:return np.empty(0),np.empty(0),[]
    cuts=list(background.eta[(background.eta>=0)&(background.eta<eta_o)])+[float(eta_o)]
    bo=0. if mean_only else float(background.shear(eta_o))
    roots=[]
    if chi>0:
        for energy in support:
            for sign in (1.,-2.):
                def log_cross(x):
                    bb=0. if mean_only else float(background.shear(x))
                    return x-eta_o+sign*(bo-bb)-math.log(chi/energy)
                left,right=log_cross(0.),log_cross(eta_o)
                if left*right<0:
                    root=brentq(log_cross,0.,eta_o,xtol=1e-14,rtol=1e-14)
                    cuts.append(root);roots.append(root)
    cuts=np.array(sorted(set(cuts)))
    t,w=rule(birth_order);lo,hi=cuts[:-1],cuts[1:]
    return (lo[:,None]+(hi-lo)[:,None]*t).ravel(),((hi-lo)[:,None]*w).ravel(),roots


def raw_shape(E,source):
    if source['spectrum']=='blackbody_photon_number':
        return E**2/np.expm1(E/(1.380649e-23/1.602176634e-19*source['temperature_K']))
    if source['spectrum']=='cutoff_power_law' and source['power_index']==-2:
        return (source['pivot_energy_eV']/E)**2*np.exp(-E/source['cutoff_energy_eV'])
    raise ValueError('UNCONTRACTED_SPECTRUM')


def validate_inputs(background,sources,support,normalizers,eta_o,thresholds,orders):
    if not np.isfinite(eta_o) or not background.eta[0]<=eta_o<=background.eta[-1]:
        raise ValueError('OBSERVER_OUTSIDE_DONOR_DOMAIN')
    thresholds=np.asarray(thresholds,dtype=float)
    if thresholds.ndim!=1 or not np.all(np.isfinite(thresholds)) or np.any(thresholds<0):
        raise ValueError('INVALID_THRESHOLD_DOMAIN')
    if len(support)!=2 or not np.all(np.isfinite(support)) or not 0<support[0]<support[1]:
        raise ValueError('INVALID_POSITIVE_BIRTH_SUPPORT')
    norms=np.asarray(normalizers,dtype=float)
    if norms.shape!=(len(sources),) or not np.all(np.isfinite(norms)) or np.any(norms<=0):
        raise ValueError('INVALID_SPECTRAL_NORMALIZERS')
    if any(not isinstance(k,(int,np.integer)) or k<1 for k in orders):
        raise ValueError('INVALID_GAUSSIAN_ORDER')
    if any(not np.isfinite(s['amplitude_per_Href_s']) or s['amplitude_per_Href_s']<0 or
           not np.isfinite(s['escape_fraction']) or not 0<=s['escape_fraction']<=1 for s in sources):
        raise ValueError('INVALID_PRESCRIBED_SOURCE_AMPLITUDE')


def production(background,sources,support,normalizers,eta_o,thresholds,
               birth_order=8,angle_order=16,energy_order=16,mean_only=False):
    """Direct positive E, angle, birth quadrature; exact moving support cuts."""
    validate_inputs(background,sources,support,normalizers,eta_o,thresholds,(birth_order,angle_order,energy_order))
    result=np.zeros((len(sources),len(thresholds),3));counts=0;root_counts=[]
    if eta_o==0:return result,{'spectral_points':0,'time_support_roots_per_threshold':[]}
    an,aw=rule(angle_order);en,ew=rule(energy_order)
    bo=0. if mean_only else float(background.shear(eta_o))
    for j,chi in enumerate(thresholds):
        birth,btw,roots=time_nodes(background,eta_o,chi,support,birth_order,mean_only)
        root_counts.append(len(roots))
        for start in range(0,len(birth),256):
            eta=birth[start:start+256];tw=btw[start:start+256]
            H=np.exp(background.logH(eta));bb=np.zeros_like(eta) if mean_only else background.shear(eta)
            rp=np.exp(eta-eta_o+bo-bb);rz=np.exp(eta-eta_o-2*(bo-bb));a=rp*rp;d=rz*rz-a
            angular_cuts=[np.zeros_like(eta),np.ones_like(eta)]
            for edge in support:
                u2=np.divide((chi/edge)**2-a,d,out=np.zeros_like(d),where=d!=0)
                angular_cuts.append(np.sqrt(np.clip(u2,0,1)))
            cuts=np.sort(np.stack(angular_cuts),axis=0)
            for lower,upper in zip(cuts[:-1],cuts[1:]):
                active=upper>lower
                if not np.any(active):continue
                low,high=lower[active],upper[active]
                mu=low[:,None]+(high-low)[:,None]*an
                weights=(high-low)[:,None]*aw
                g=np.sqrt(a[active,None]+d[active,None]*mu*mu)
                L=np.maximum(support[0],chi/g)
                valid=L<support[1]
                if not np.any(valid):continue
                gi=g[valid];Li=L[valid];lr=np.log(support[1]/Li)
                E=Li[:,None]*np.exp(lr[:,None]*en)
                dE=E*lr[:,None]*ew
                excess=gi[:,None]*E-chi
                counts+=E.size
                z=21*np.exp(-eta[active])-1
                for sidx,source in enumerate(sources):
                    q=source['amplitude_per_Href_s']*source['escape_fraction']*(1+np.tanh((source['z_on']-z)/source['delta_z']))/2
                    measure=(tw[active]*q/H[active])[:,None]*weights
                    density=raw_shape(E,source)/normalizers[sidx]
                    scale=measure[valid]
                    result[sidx,j,0]+=float(scale@(np.sum(density*dE,axis=1)))
                    result[sidx,j,1]+=float(scale@(np.sum(gi[:,None]*E*density*dE,axis=1)))
                    result[sidx,j,2]+=float(scale@(np.sum(excess*density*dE,axis=1)))
    return result,{'spectral_points':counts,'time_support_roots_per_threshold':root_counts,
                   'orders':[birth_order,angle_order,energy_order],'mean_only':mean_only}


def _angular_primitive(mu,a,d):
    """Integral_0^mu sqrt(a+d x²)dx, stable near isotropy."""
    a,d,mu=np.broadcast_arrays(a,d,mu);out=np.empty_like(mu);z=d/a;small=abs(z)<1e-6
    u=mu[small];r=z[small]
    out[small]=np.sqrt(a[small])*(u+r*u**3/6-r*r*u**5/40+r**3*u**7/112)
    pos=(~small)&(d>0);u=mu[pos];aa=a[pos];dd=d[pos]
    out[pos]=.5*(u*np.sqrt(aa+dd*u*u)+aa/np.sqrt(dd)*np.arcsinh(np.sqrt(dd/aa)*u))
    neg=(~small)&(d<0);u=mu[neg];aa=a[neg];dd=-d[neg]
    out[neg]=.5*(u*np.sqrt(aa-dd*u*u)+aa/np.sqrt(dd)*np.arcsin(np.sqrt(dd/aa)*u))
    return out


def oracle(background,sources,support,normalizers,eta_o,thresholds,birth_order=16,energy_order=48,mean_only=False):
    """Independent integration order: raw E spectrum, analytic angular interval.
    Uses separate geometric equations; no production quadrature/tail routine.
    X integrand is analytic angular integral of positive(E*g-chi), evaluated
    before source/spectral integration rather than assigned from output U-chi N.
    """
    validate_inputs(background,sources,support,normalizers,eta_o,thresholds,(birth_order,energy_order))
    out=np.zeros((len(sources),len(thresholds),3));point_count=0; raw_x_min=0.; roundoff_violations=0
    if eta_o==0:return out,{'energy_points':0}
    x,w=rule(energy_order);theta=np.pi*x/2;u=np.sin(theta)**2;du=np.pi*np.sin(np.pi*x)/2
    observer_b=0. if mean_only else float(background.shear(eta_o))
    for j,chi in enumerate(thresholds):
        t,tw,_=time_nodes(background,eta_o,chi,support,birth_order,mean_only)
        H=np.exp(background.logH(t));b=np.zeros_like(t) if mean_only else background.shear(t)
        # Separate direct directional-scale ratios.
        ap_b=np.exp(t-b);az_b=np.exp(t+2*b)
        ap_o=np.exp(eta_o-observer_b);az_o=np.exp(eta_o+2*observer_b)
        rp=ap_b/ap_o;rz=az_b/az_o;a=rp**2;d=rz**2-rp**2
        cuts=np.sort(np.stack([np.full_like(t,support[0]),np.full_like(t,support[1]),
                              np.clip(chi/rp,*support),np.clip(chi/rz,*support)]),axis=0)
        for elow,ehigh in zip(cuts[:-1],cuts[1:]):
            active=ehigh>elow
            if not np.any(active):continue
            lo,hi=elow[active],ehigh[active];E=lo[:,None]+(hi-lo)[:,None]*u
            ew=(hi-lo)[:,None]*w*du;aa=a[active,None];dd=d[active,None]
            target=(chi/E)**2;ratio=np.divide(target-aa,dd,out=np.zeros_like(E),where=dd!=0)
            cut=np.sqrt(np.clip(ratio,0,1))
            mu_lo=np.where(dd>0,cut,0.);mu_hi=np.where(dd<0,cut,1.)
            # Constant-g limit and entirely rejected/accepted intervals.
            accept_all=target<=np.minimum(aa,aa+dd);reject_all=target>=np.maximum(aa,aa+dd)
            mu_lo=np.where(accept_all,0.,mu_lo);mu_hi=np.where(accept_all,1.,mu_hi)
            mu_lo=np.where(reject_all,0.,mu_lo);mu_hi=np.where(reject_all,0.,mu_hi)
            length=mu_hi-mu_lo
            Ghi=_angular_primitive(mu_hi,aa,dd);Glo=_angular_primitive(mu_lo,aa,dd)
            G=Ghi-Glo
            raw_x=E*G-chi*length
            raw_x_min=min(raw_x_min,float(np.min(raw_x)))
            roundoff_bound=64*np.finfo(float).eps*(E*(np.abs(Ghi)+np.abs(Glo))+np.abs(chi*length))
            roundoff_violations+=int(np.count_nonzero(raw_x < -roundoff_bound))
            kernels=[length,E*G,raw_x]
            point_count+=E.size
            z=21*np.exp(-t[active])-1
            for si,source in enumerate(sources):
                if source['name']=='stellar':
                    kT=source['temperature_K']*1.380649e-23/1.602176634e-19
                    raw=E*E/(np.exp(E/kT)-1)
                else:raw=source['pivot_energy_eV']**2*np.exp(-E/source['cutoff_energy_eV'])/E**2
                q=source['amplitude_per_Href_s']*source['escape_fraction']/(1+np.exp(2*(z-source['z_on'])/source['delta_z']))
                bw=tw[active]*q/H[active]
                for k,kernel in enumerate(kernels):out[si,j,k]+=float(bw@(np.sum(ew*raw*kernel,axis=1)/normalizers[si]))
    return out,{'energy_points':point_count,'orders':[birth_order,energy_order],'mean_only':mean_only,
                'unclipped_X_integrand_min_eV':raw_x_min,'X_negative_beyond_roundoff_count':roundoff_violations,
                'clipped_X_values':0}
