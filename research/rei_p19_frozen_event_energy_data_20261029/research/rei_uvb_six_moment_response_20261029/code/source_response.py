"""Scoped Puchwein2019 six-moment UVB response to PR260 beta/kappa.
Not a Bianchi optical-depth derivative, physical 17-state IVP, or spectral reconstruction.
All derivatives hold redshift, Puchwein shape and target populations fixed.
"""
import hashlib,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BB=ROOT/'source/FROZEN_BB13_SUPPORT_INPUT.json'
P19=ROOT/'source/PUCHWEIN2019_13_ROW_PROJECTION.json'
BB_SHA='13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b'
P_SHA='dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff'
Q_SCALAR95=3.8414588206941236
Q_JOINT2_95=5.991464547107982
L10=math.log(10.)
FIELDS=('Gamma_HI_s-1','heat_HI_eV_s-1','Gamma_HeI_s-1','heat_HeI_eV_s-1','Gamma_HeII_s-1','heat_HeII_eV_s-1')
SPECIES=('HI','HeI','HeII')

def load():
    if hashlib.sha256(BB.read_bytes()).hexdigest()!=BB_SHA:raise ValueError('BB13_SOURCE_SHA_MISMATCH')
    if hashlib.sha256(P19.read_bytes()).hexdigest()!=P_SHA:raise ValueError('P19_PROJECTION_SHA_MISMATCH')
    d=json.loads(BB.read_text());p=json.loads(P19.read_text());rows=np.array(p['rows'],float)
    if rows.shape!=(13,7) or not np.all(np.isfinite(rows)) or not np.all(np.diff(rows[:,0])>0):raise ValueError('BAD_P19_GRID')
    if not np.all(rows[:,1:]>0):raise ValueError('NONPOSITIVE_P19_MOMENT')
    if tuple(p['units'][1:])!=FIELDS:raise ValueError('P19_UNITS_MISMATCH')
    if p['parent_git_blob']!='218d81f68447da438228a7b102e1cec96a8e8a1a':raise ValueError('P19_PARENT_GIT_BLOB_MISMATCH')
    z=np.array(d['z'],float)
    if z.shape!=(7,) or not np.all(np.diff(z)>0):raise ValueError('BAD_BB13_GRID')
    m=np.interp(z,rows[:,0],np.log10(rows[:,1]/1e-12))
    if np.max(np.abs(m-np.array(d['template_dex'])))>1e-12:raise ValueError('P19_SEVEN_POINT_TEMPLATE_MISMATCH')
    return d,p,rows

def geometry(d):
    z=np.array(d['z'],float);C=np.array(d['covariance_dex_squared'],float)
    X=np.column_stack((np.ones(7),z-3.6))
    L=np.linalg.cholesky(C);W_X=np.linalg.solve(L.T,np.linalg.solve(L,X))
    V=np.linalg.inv(X.T@W_X);A=V@W_X.T
    r=np.array(d['observed_dex'])-np.array(d['template_dex'])
    v=np.array(d['eos_response_dex'])
    low=np.array(d['jeans_smoothing_lower_dex']);high=np.array(d['jeans_smoothing_upper_dex'])
    a0=A@r;center=a0+A@((low+high)/2)
    G=np.column_stack((A@v,A*((high-low)/2)[None,:]))
    if np.max(np.abs(A@X-np.eye(2)))>1e-12 or np.max(np.abs(A@C@A.T-V))>1e-12:raise AssertionError('GLS_IDENTITY_FAILED')
    return {'A':A,'V':V,'a0':a0,'center':center,'G':G,'C':C,'X':X,'low':low,'high':high,'v':v,'r':r}

def _validate_z(z,rows):
    if not math.isfinite(z):raise ValueError('INVALID_REDSHIFT')
    if not (2.4<=z<=4.75):
        if z>15.1:raise ValueError('MISSING_PREHISTORY_OR_OUTSIDE_MODEL_DOMAIN')
        raise ValueError('OUTSIDE_OBSERVATION_CALIBRATION_DOMAIN')
    if z<rows[0,0] or z>rows[-1,0]:raise ValueError('OUTSIDE_PROJECTED_P19_GRID')

def p19_moments(z,rows):
    _validate_z(z,rows)
    logs=np.log(rows[:,1:])
    return np.array([math.exp(float(np.interp(z,rows[:,0],logs[:,i]))) for i in range(6)])

def p19_log_slopes(z,rows):
    _validate_z(z,rows)
    if np.any(np.isclose(z,rows[:,0],rtol=0,atol=1e-14)):raise ValueError('ONE_SIDED_REDSHIFT_DERIVATIVE_REQUIRED_AT_KNOT')
    i=int(np.searchsorted(rows[:,0],z)-1)
    return (np.log(rows[i+1,1:])-np.log(rows[i,1:]))/(rows[i+1,0]-rows[i,0])

def tvec(z):return np.array([1.,z-3.6])

def rate_response(z,a,rows):
    p=p19_moments(z,rows);a=np.asarray(a,float)
    if a.shape!=(2,) or not np.all(np.isfinite(a)):raise ValueError('BAD_CALIBRATION_PARAMETERS')
    t=tvec(z);factor=math.exp(L10*float(t@a))
    if not math.isfinite(factor):raise OverflowError('RATE_SCALING_OVERFLOW')
    rate=p*factor;jac=rate[:,None]*(L10*t)[None,:]
    hess=rate[:,None,None]*(L10**2)*np.outer(t,t)[None,:,:]
    return {'z':z,'p19':p,'factor':factor,'moments':rate,'jac':jac,'hess':hess}

def logfactor_support(z,q,geo):
    if not math.isfinite(q) or q<0:raise ValueError('INVALID_Q')
    t=tvec(z);c=float(t@geo['center'])
    r=float(np.sum(np.abs(t@geo['G'])))+math.sqrt(max(0.,q*float(t@geo['V']@t)))
    return c-r,c+r

def pointwise_envelope(z,q,geo,rows):
    p=p19_moments(z,rows);lo,hi=logfactor_support(z,q,geo)
    return {'z':z,'q':q,'logfactor_dex':[lo,hi], 'factor':[10.**lo,10.**hi],
            'moments_min':p*10.**lo,'moments_max':p*10.**hi}

def fixed_population_ports(response,y):
    if set(y)!=set(SPECIES):raise ValueError('MISSING_OR_EXTRA_TARGET_FRACTION')
    f=np.array([y[k] for k in SPECIES],float)
    if not np.all(np.isfinite(f)) or np.any(f<0):raise ValueError('BAD_TARGET_FRACTION')
    r=response['moments'].reshape(3,2);j=response['jac'].reshape(3,2,2)
    return {'events_per_Href_s':f*r[:,0],'heat_eV_per_Href_s':f*r[:,1],
            'jac_events':f[:,None]*j[:,0,:],'jac_heat':f[:,None]*j[:,1,:],
            'fixed_population_only':True}

def taylor_remainder(rate,z,da):
    u=L10*float(tvec(z)@np.asarray(da,float))
    if rate<0 or not math.isfinite(rate):raise ValueError('INVALID_RATE')
    remainder=rate*math.expm1(u)-rate*u
    upper=0.5*rate*math.exp(abs(u))*u*u
    return remainder,upper

def mean_clock_response(z,H,a,rows):
    if not math.isfinite(H) or H<=0:raise ValueError('BAD_MEAN_HUBBLE_RATE')
    resp=rate_response(z,a,rows)
    dlogdz=p19_log_slopes(z,rows)+L10*float(a[1])
    dx=-(1+z)*resp['moments']*dlogdz
    return {'d_moments_dx':dx,'d_moments_dt':H*dx,
            'clock':'x=ln(a/a_ref), dz_mean/dx=-(1+z_mean)',
            'H_unit':'s^-1','observed_directional_redshift':'NOT_BOUND'}

def tau_rhs_and_tangent(K,ne,H,dne,dH):
    if not all(map(math.isfinite,(K,ne,H,dne,dH))) or K<0 or ne<0 or H<=0:raise ValueError('INVALID_TAU_PORT')
    return K*ne/H,K*dne/H-K*ne*dH/(H*H)

def photon_energy_ledger(ports,ionization_threshold_eV):
    """Exact per-Href source bookkeeping for supplied thresholds, fixed populations.

    Input thresholds are required external atomic constants; none are invented here.
    Absorbed photon energy is heating plus ionization storage, not an extra heat term.
    """
    if set(ionization_threshold_eV)!=set(SPECIES):
        raise ValueError('MISSING_IONIZATION_THRESHOLDS')
    E=np.array([ionization_threshold_eV[s] for s in SPECIES],float)
    if not np.all(np.isfinite(E)) or np.any(E<=0):
        raise ValueError('BAD_IONIZATION_THRESHOLDS')
    ion=E*ports['events_per_Href_s']
    jac_ion=E[:,None]*ports['jac_events']
    heat=ports['heat_eV_per_Href_s']
    jac_heat=ports['jac_heat']
    return {'ionization_storage_eV_per_Href_s':ion,
            'photoheat_eV_per_Href_s':heat,
            'absorbed_photon_eV_per_Href_s':ion+heat,
            'jac_absorbed_photon':jac_ion+jac_heat,
            'no_double_counting':True}
