"""Continuous zero-opacity radiation probe of selected photo channels.

SI cross sections; energies eV; source inventory normalized per Href.
No IVP, target depletion, or empirical spectrum/opacity calibration is performed.
"""
import math
import numpy as np
from scipy.optimize import brentq
from threshold_response import rule, raw_shape, validate_inputs, directional_expansion_certificate

C_M_S = 299792458.0
CHANNEL_NAMES = ('H_I', 'He_I', 'He_II', 'Li_I', 'Li_II', 'Li_III')
CHI_EV = np.array([13.60, 24.59, 54.42, 5.392, 75.64, 122.5])
# Same selected 21-state order as the frozen pilot. Every channel removes one
# electron. D/T electronic equality is an inherited modelling assumption.
SPECIES = ('n','H1_0','H1_1','D_0','D_1','T_0','T_1',
           'He3_0','He3_1','He3_2','He4_0','He4_1','He4_2',
           'Li6_0','Li6_1','Li6_2','Li6_3','Li7_0','Li7_1','Li7_2','Li7_3')
BLOCKS = ((0,), (1,2), (3,4), (5,6), (7,8,9), (10,11,12), (13,14,15,16), (17,18,19,20))
EDGES = ((1,2,0),(3,4,0),(5,6,0),
         (7,8,1),(8,9,2),(10,11,1),(11,12,2),
         (13,14,3),(14,15,4),(15,16,5),(17,18,3),(18,19,4),(19,20,5))


def event_time_nodes(background, eta_o, edges, support, order):
    """Donor-knot partition plus lower/upper observer-band support roots."""
    if eta_o == 0:
        return np.empty(0), np.empty(0), []
    cuts = list(background.eta[(background.eta >= 0) & (background.eta < eta_o)]) + [float(eta_o)]
    bo = float(background.shear(eta_o)); roots = []
    for chi in edges:
        if chi <= 0 or not np.isfinite(chi):
            continue
        for energy in support:
            for sign in (1., -2.):
                def log_cross(x):
                    return x - eta_o + sign * (bo - float(background.shear(x))) - math.log(chi/energy)
                left, right = log_cross(0.), log_cross(eta_o)
                if left * right < 0:
                    r = brentq(log_cross, 0., eta_o, xtol=1e-14, rtol=1e-14)
                    cuts.append(r); roots.append(r)
    cuts = np.array(sorted(set(cuts))); t,w = rule(order)
    lo,hi = cuts[:-1], cuts[1:]
    return (lo[:,None]+(hi-lo)[:,None]*t).ravel(), ((hi-lo)[:,None]*w).ravel(), roots


def _validate(background, sources, support, normalizers, eta_o, bands, orders):
    validate_inputs(background, sources, support, normalizers, eta_o, [b[0] for b in bands], orders)
    bands = np.asarray(bands, float)
    if bands.shape != (6,2) or not np.all(np.isfinite(bands)) or np.any(bands[:,1] <= bands[:,0]):
        raise ValueError('INVALID_PROVIDER_BANDS')
    if not np.array_equal(bands[:,0], CHI_EV):
        raise ValueError('CHANNEL_THRESHOLDS_DIFFER_FROM_PINNED_PILOT')
    if np.any(bands[:,1]>min(support[1],5e4)):
        raise ValueError('BAND_EXCEEDS_SOURCE_OR_PROVIDER_DOMAIN')
    if not directional_expansion_certificate(background)['positive_directional_expansion']:
        raise ValueError('MONOTONE_SUPPORT_PREREQUISITE_FAILED')
    return bands


def _pieces(bands):
    for j,(chi,cap) in enumerate(bands):
        cuts=[chi,64.39,cap] if j==3 and chi<64.39<cap else [chi,cap]
        for low,high in zip(cuts[:-1],cuts[1:]):
            yield j,chi,low,high


def production(background, sources, support, normalizers, eta_o, bands, sigma_m2,
               birth_order=8, angle_order=16, energy_order=16):
    """Birth time -> birth angle -> birth energy, positive band quadrature.

    Returns shape (sources,channels,3), quantities [sigma,sigma*E,sigma*(E-chi)]
    integrated against photons/Href. Domain is explicit; no out-of-band sigma
    call or extrapolated physical zero is introduced.
    """
    bands = _validate(background,sources,support,normalizers,eta_o,bands,(birth_order,angle_order,energy_order))
    out = np.zeros((len(sources),6,3)); points = 0; root_counts=[]; piece_outputs=[]
    if eta_o == 0:
        return out, {'spectral_points':0,'time_support_roots':[]}
    an,aw=rule(angle_order); en,ew=rule(energy_order); bo=float(background.shear(eta_o))
    for j,chi,bandlo,cap in _pieces(bands):
        before=out[:,j,:].copy()
        birth,btw,roots=event_time_nodes(background,eta_o,(bandlo,cap),support,birth_order)
        root_counts.append(len(roots))
        for start in range(0,len(birth),192):
            eta=birth[start:start+192];tw=btw[start:start+192]
            H=np.exp(background.logH(eta));bb=background.shear(eta)
            rp=np.exp(eta-eta_o+bo-bb);rz=np.exp(eta-eta_o-2*(bo-bb))
            a=rp*rp;d=rz*rz-a
            angular=[np.zeros_like(eta),np.ones_like(eta)]
            for edge in (bandlo,cap):
                for Eb in support:
                    x=np.divide((edge/Eb)**2-a,d,out=np.zeros_like(d),where=d!=0)
                    angular.append(np.sqrt(np.clip(x,0,1)))
            cuts=np.sort(np.stack(angular),axis=0)
            for lower,upper in zip(cuts[:-1],cuts[1:]):
                active=upper>lower
                if not np.any(active):continue
                mu=lower[active,None]+(upper-lower)[active,None]*an
                mw=(upper-lower)[active,None]*aw
                g=np.sqrt(a[active,None]+d[active,None]*mu*mu)
                L=np.maximum(support[0],bandlo/g);U=np.minimum(support[1],cap/g)
                valid=U>L
                if not np.any(valid):continue
                gi=g[valid];lo=L[valid];lr=np.log(U[valid]/lo)
                E=lo[:,None]*np.exp(lr[:,None]*en)
                dE=E*lr[:,None]*ew;Eo=gi[:,None]*E
                sigma=np.asarray(sigma_m2(j,Eo))
                if sigma.shape!=E.shape or not np.all(np.isfinite(sigma)) or np.any(sigma<0):
                    raise ValueError('INVALID_SIGMA_WITHIN_ADMITTED_BAND')
                points+=E.size;z=21*np.exp(-eta[active])-1
                for si,source in enumerate(sources):
                    q=source['amplitude_per_Href_s']*source['escape_fraction']*(1+np.tanh((source['z_on']-z)/source['delta_z']))/2
                    measure=((tw[active]*q/H[active])[:,None]*mw)[valid]
                    base=raw_shape(E,source)*dE*sigma/normalizers[si]
                    out[si,j,0]+=float(measure@base.sum(axis=1))
                    out[si,j,1]+=float(measure@(Eo*base).sum(axis=1))
                    out[si,j,2]+=float(measure@((Eo-chi)*base).sum(axis=1))
        piece_outputs.append({'channel_index':j,'observer_band_eV':[bandlo,cap],'response':(out[:,j,:]-before).tolist()})
    return out,{'spectral_points':points,'time_support_roots':root_counts,
               'orders':[birth_order,angle_order,energy_order],'piece_responses':piece_outputs}


def oracle(background,sources,support,normalizers,eta_o,bands,sigma_m2,
           birth_order=12,energy_order=32,angle_order=24):
    """Independent order: time -> observer energy -> accepted birth angle.

    Source evaluates Eb=Eo/g with Jacobian dEb=dEo/g. Geometry uses separate
    scale-factor ratios. Time knots/support roots are shared and scope explicit.
    sin² endpoint map regularizes square-root accepted-angle support boundaries.
    """
    bands=_validate(background,sources,support,normalizers,eta_o,bands,(birth_order,energy_order,angle_order))
    out=np.zeros((len(sources),6,3));points=0
    if eta_o==0:return out,{'spectral_points':0}
    en,ew=rule(energy_order);an,aw=rule(angle_order)
    tmap=np.sin(np.pi*en/2)**2;deriv=np.pi*np.sin(np.pi*en)/2
    bo=float(background.shear(eta_o))
    for j,chi,bandlo,cap in _pieces(bands):
        birth,btw,_=event_time_nodes(background,eta_o,(bandlo,cap),support,birth_order)
        for start in range(0,len(birth),96):
            t=birth[start:start+96];wt=btw[start:start+96]
            b=background.shear(t);H=np.exp(background.logH(t))
            rp=np.exp(t-b)/np.exp(eta_o-bo);rz=np.exp(t+2*b)/np.exp(eta_o+2*bo)
            a=rp**2;d=rz**2-a
            cuts=np.sort(np.stack([np.full_like(t,bandlo),np.full_like(t,cap),
                 np.clip(support[0]*rp,bandlo,cap),np.clip(support[0]*rz,bandlo,cap),
                 np.clip(support[1]*rp,bandlo,cap),np.clip(support[1]*rz,bandlo,cap)]),axis=0)
            for low,high in zip(cuts[:-1],cuts[1:]):
                active=high>low
                if not np.any(active):continue
                Eo=low[active,None]+(high-low)[active,None]*tmap
                Eow=(high-low)[active,None]*ew*deriv
                aa=a[active,None];dd=d[active,None]
                # Birth support lo <= Eo/g <= hi gives g² interval.
                g2lo=(Eo/support[1])**2;g2hi=(Eo/support[0])**2
                rlo=np.divide(g2lo-aa,dd,out=np.zeros_like(Eo),where=dd!=0)
                rhi=np.divide(g2hi-aa,dd,out=np.zeros_like(Eo),where=dd!=0)
                ulo=np.sqrt(np.clip(np.minimum(rlo,rhi),0,1));uhi=np.sqrt(np.clip(np.maximum(rlo,rhi),0,1))
                constant=(dd==0)
                accepted_constant=(aa>=g2lo)&(aa<=g2hi)
                ulo=np.where(constant,0,ulo);uhi=np.where(constant&accepted_constant,1,uhi)
                rejected=(g2hi<np.minimum(aa,aa+dd))|(g2lo>np.maximum(aa,aa+dd))|(constant&~accepted_constant)
                uhi=np.where(rejected,ulo,uhi)
                mu=ulo[:,:,None]+(uhi-ulo)[:,:,None]*an
                mw=(uhi-ulo)[:,:,None]*aw
                g=np.sqrt(aa[:,:,None]+dd[:,:,None]*mu*mu);Eb=Eo[:,:,None]/g
                sig=np.asarray(sigma_m2(j,Eo));points+=Eb.size
                z=21*np.exp(-t[active])-1
                for si,s in enumerate(sources):
                    if s['name']=='stellar':
                        raw=Eb*Eb/(np.exp(Eb/(s['temperature_K']*1.380649e-23/1.602176634e-19))-1)
                    else:raw=s['pivot_energy_eV']**2*np.exp(-Eb/s['cutoff_energy_eV'])/Eb**2
                    q=s['amplitude_per_Href_s']*s['escape_fraction']/(1+np.exp(2*(z-s['z_on'])/s['delta_z']))
                    angular=np.sum(mw*raw/g,axis=2)/normalizers[si]
                    base=Eow*sig*angular
                    for k,kernel in enumerate((np.ones_like(Eo),Eo,Eo-chi)):
                        out[si,j,k]+=float((wt[active]*q/H[active])@(base*kernel).sum(axis=1))
    return out,{'spectral_points':points,'orders_birth_energy_angle':[birth_order,energy_order,angle_order],
                'independence':'observer-energy variable, Jacobian1/g, separate geometry/spectrum; shared frozen donor/time roots'}


def rates_from_response(response,nHref_m3):
    response=np.asarray(response)
    if response.shape!=(2,6,3) or not np.all(np.isfinite(response)) or np.any(response<0):
        raise ValueError('INVALID_POSITIVE_RATE_RESPONSE')
    if not np.isfinite(nHref_m3) or nHref_m3<=0:
        raise ValueError('INVALID_PROPER_REFERENCE_DENSITY')
    return C_M_S*nHref_m3*response


def target_response(y,rates,amplitudes=(1.,1.)):
    """Frozen-radiation instantaneous photo-only response and analytical J.

    y[21] is number/Href; rates[2,6,3] is per-target [s^-1,eV/s,eV/s].
    Output vector: 21 atomic derivatives + electron source + radiation energy
    loss + stored ionization energy + primary-electron kinetic energy [eV/Href/s].
    J columns are y[21], then the two relative source-template amplitudes.
    No radiation dynamical Jacobian, secondary deposition, RR or nuclear rates.
    """
    y=np.asarray(y);rates=np.asarray(rates);amplitudes=np.asarray(amplitudes)
    # Complex extension is intentionally permitted for derivative verification;
    # caller owns the physical y>=0/amplitude>=0 domain checked separately.
    if y.shape!=(21,) or rates.shape!=(2,6,3) or amplitudes.shape!=(2,) or not np.all(np.isfinite(y)) or not np.all(np.isfinite(rates)) or not np.all(np.isfinite(amplitudes)):
        raise ValueError('INVALID_TARGET_RESPONSE_SHAPE_OR_FINITE_DOMAIN')
    if np.any(np.real(y)<0) or np.any(np.real(rates)<0) or np.any(np.real(amplitudes)<0):
        raise ValueError('NEGATIVE_PHYSICAL_INPUT')
    dtype=np.result_type(y,rates,amplitudes,float)
    f=np.zeros(25,dtype=dtype);J=np.zeros((25,23),dtype=dtype)
    total=np.einsum('s,sck->ck',amplitudes,rates)
    events=[]
    for lower,upper,ch in EDGES:
        gamma,power,primary=total[ch];event=y[lower]*gamma
        v=np.zeros(25,dtype=dtype);v[lower]=-gamma;v[upper]=gamma;v[21]=gamma
        v[22]=-power;v[23]=CHI_EV[ch]*gamma;v[24]=primary
        f+=y[lower]*v;J[:,lower]+=v
        for si in range(2):
            gamma_s,power_s,primary_s=rates[si,ch]
            J[lower,21+si]-=y[lower]*gamma_s;J[upper,21+si]+=y[lower]*gamma_s
            J[21,21+si]+=y[lower]*gamma_s;J[22,21+si]-=y[lower]*power_s
            J[23,21+si]+=y[lower]*CHI_EV[ch]*gamma_s;J[24,21+si]+=y[lower]*primary_s
        events.append(event)
    return f,J,np.asarray(events)
