"""H1 energy marginal of the original continuous photon measure.

The forward quadrature below follows the H1 branch of the byte-pinned
opacity_response.production; it exposes integrand atoms instead of moments.
No stopping model, electron angular law, or time evolution is supplied.
"""
import numpy as np
from opacity_response import event_time_nodes
from threshold_response import rule, raw_shape, validate_inputs, directional_expansion_certificate

C_M_S = 299792458.0
CHI_EV = 13.6
SOURCE_NAMES = ('stellar', 'external_IGM')
SOURCE_ID = 'GRID044_CONTINUOUS_OPACITY_RESPONSE_20261025'
FRAME = 'normal_tetrad_stationary_ground_state'
REFERENCE = 'fixed_comoving_bookkeeping_number'
EVENT = 'photo:H1_0->H1_1'


def emit_atoms(background, sources, support, normalizers, eta_o, sigma_m2):
    """Return Egamma, epsilon, Eb, A[source,atom], and quadrature metadata."""
    validate_inputs(background, sources, support, normalizers, eta_o, [CHI_EV], (8,12,16))
    if tuple(s['name'] for s in sources) != SOURCE_NAMES or list(support) != [5.,150.]:
        raise ValueError('WRONG_SOURCE_OR_BIRTH_SUPPORT')
    if not directional_expansion_certificate(background)['positive_directional_expansion']:
        raise ValueError('MONOTONE_SUPPORT_PREREQUISITE_FAILED')
    en, ew = rule(16); an, aw = rule(12)
    birth, btw, roots = event_time_nodes(background, eta_o, (CHI_EV,150.), support, 8)
    bo = float(background.shear(eta_o)); energies=[]; birth_energies=[]; atoms=[]
    for start in range(0,len(birth),192):
        eta=birth[start:start+192]; tw=btw[start:start+192]
        H=np.exp(background.logH(eta)); bb=background.shear(eta)
        rp=np.exp(eta-eta_o+bo-bb); rz=np.exp(eta-eta_o-2*(bo-bb))
        a=rp*rp; d=rz*rz-a
        angular=[np.zeros_like(eta),np.ones_like(eta)]
        for edge in (CHI_EV,150.):
            for Eb in support:
                x=np.divide((edge/Eb)**2-a,d,out=np.zeros_like(d),where=d!=0)
                angular.append(np.sqrt(np.clip(x,0,1)))
        cuts=np.sort(np.stack(angular),axis=0)
        for lower,upper in zip(cuts[:-1],cuts[1:]):
            active=upper>lower
            if not np.any(active): continue
            mu=lower[active,None]+(upper-lower)[active,None]*an
            mw=(upper-lower)[active,None]*aw
            g=np.sqrt(a[active,None]+d[active,None]*mu*mu)
            L=np.maximum(support[0],CHI_EV/g); U=np.minimum(support[1],150./g)
            valid=U>L
            if not np.any(valid): continue
            gi=g[valid]; lo=L[valid]; lr=np.log(U[valid]/lo)
            E=lo[:,None]*np.exp(lr[:,None]*en)
            dE=E*lr[:,None]*ew; Eo=gi[:,None]*E
            sigma=np.asarray(sigma_m2(Eo))
            if sigma.shape!=E.shape or not np.all(np.isfinite(sigma)) or np.any(sigma<0):
                raise ValueError('INVALID_HI_SIGMA')
            z=21*np.exp(-eta[active])-1; by_source=[]
            for si,source in enumerate(sources):
                q=source['amplitude_per_Href_s']*source['escape_fraction']*(1+np.tanh((source['z_on']-z)/source['delta_z']))/2
                measure=((tw[active]*q/H[active])[:,None]*mw)[valid]
                base=raw_shape(E,source)*dE*sigma/normalizers[si]
                by_source.append((measure[:,None]*base).ravel())
            energies.append(Eo.ravel()); birth_energies.append(E.ravel()); atoms.append(np.stack(by_source))
    if not energies:
        empty=np.empty(0)
        return empty,empty.copy(),empty.copy(),np.empty((2,0)),{'atoms':0,'time_support_roots':roots}
    Eo=np.concatenate(energies); Eb=np.concatenate(birth_energies); A=np.concatenate(atoms,axis=1)
    return Eo,Eo-CHI_EV,Eb,A,{'atoms':len(Eo),'time_support_roots':roots,'orders_birth_angle_energy':[8,12,16]}


def validate_binding(y, alpha, r, *, frame=FRAME, reference=REFERENCE,
                     source_id=SOURCE_ID, source_names=SOURCE_NAMES, owners=(EVENT,)):
    alpha=np.asarray(alpha)
    if not np.isfinite(y) or not np.isfinite(r) or alpha.shape!=(2,) or not np.all(np.isfinite(alpha)):
        raise ValueError('INVALID_SOURCE_PARAMETERS')
    if np.real(y)<0 or np.real(r)<=0 or np.any(np.real(alpha)<0):
        raise ValueError('INVALID_SOURCE_PARAMETER_DOMAIN')
    if frame!=FRAME or reference!=REFERENCE or source_id!=SOURCE_ID or tuple(source_names)!=SOURCE_NAMES:
        raise ValueError('SOURCE_FRAME_REFERENCE_IDENTITY_MISMATCH')
    if tuple(owners)!=(EVENT,):
        raise ValueError('ONE_EVENT_OWNER_REQUIRED')


def weights(base, y, alpha, r, *, physical=False, **binding):
    """Works for A atoms or their moments, including complex-step extension."""
    validate_binding(y,alpha,r,**binding)
    value=C_M_S*r*y*np.asarray(alpha)[:,None]*base
    return r*value if physical else value


def weight_jvp(base,y,alpha,r,dy,dalpha,dr,*,physical=False):
    """Division-free tangent remains finite at zero target/amplitude."""
    validate_binding(y,alpha,r)
    alpha=np.asarray(alpha); dalpha=np.asarray(dalpha)
    dw=C_M_S*base*(r*alpha[:,None]*dy+r*y*dalpha[:,None]+y*alpha[:,None]*dr)
    return r*dw+weights(base,y,alpha,r)*dr if physical else dw


def receiver_packet():
    return {'event_owner':EVENT,'role':'receiver_of_existing_fast_reservoir',
            'physical_stopping_provider_admitted':False,'thermal_heat_J_m3_s':None,
            'angular_electron_law':None,'secondary_outcomes':None,
            'next_input':'qualified energy-resolved electron stopping and secondary-outcome operator on actual endpoint state'}
