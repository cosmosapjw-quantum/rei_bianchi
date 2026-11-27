"""Source-locked conditional 4He(gamma,dd) <-> dd->4He+gamma reciprocity.
Mass convention is frozen PR104 rest energies in MeV. Metric (-,+,+,+).
No physical event-normalization or inverse cross section is admitted.
"""
from fractions import Fraction as F
from decimal import Decimal
from pathlib import Path
from hashlib import sha1,sha256

MA=F('3727.3794118') # M_alpha*c^2 [MeV]
MD=F('1875.61294500') # m_d*c^2 [MeV]
C=299792458
SOURCE_SHA256='b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'
SOURCE_GIT_BLOB='c49433293921dbb012d7f1b0387745732a598efa'
SOURCE_COMMIT='939a14d7bba1ddce51975cb5e8711ce96b3b0871'
ORDERED='ordered_or_inclusive_D'
FULL_EVENT='full_sphere_event_density'
THERMAL_DD_PAIR_FACTOR=F(1,2)

def exact(x):
    if isinstance(x,(bool,float)): raise ValueError('rounded float/bool not accepted')
    if not isinstance(x,(F,int,str,Decimal)): raise TypeError('exact input required')
    return F(x)

def gamma_threshold():return (4*MD**2-MA**2)/(2*MA)

def s_gamma(e):
    e=exact(e)
    if e<0:raise ValueError('negative photon energy')
    return MA**2+2*MA*e

def s_dd(t):
    t=exact(t)
    if t<0:raise ValueError('negative deuteron kinetic energy')
    return 4*MD**2+2*MD*t

def T_matching(e):
    e=exact(e)
    if e<gamma_threshold():raise ValueError('below threshold')
    return (s_gamma(e)-4*MD**2)/(2*MD)

def E_matching(t):
    t=exact(t)
    if t<0:raise ValueError('negative kinetic energy')
    return (s_dd(t)-MA**2)/(2*MA)

def cm_momenta_squared(e):
    s=s_gamma(e)
    if s<=4*MD**2:raise ValueError('zero/negative final CM momentum')
    return (s-MA**2)**2/(4*s),(s-4*MD**2)/4

def reciprocity_ratio(e,convention):
    if convention not in (ORDERED,FULL_EVENT):raise ValueError('unknown event/particle convention')
    k2,q2=cm_momenta_squared(e)
    ordered=F(2,9)*k2/q2 # photon 2 helicities, alpha 1, D spin 3 each
    return ordered if convention==ORDERED else 2*ordered

def alignment(e,t):
    return {'same_s':s_gamma(e)==s_dd(t),'delta_s_MeV2':s_dd(t)-s_gamma(e),
            'matched_Td_MeV':T_matching(e),'matched_Egamma_MeV':E_matching(t)}

def read_DA(path=None):
    if path is None:
        sibling=Path(__file__).resolve().parents[2]/'he_sig_da_energy_compat_20261029'/'source'/'M0475.x4'
        packaged=Path(__file__).resolve().parents[1]/'source'/'M0475.x4'
        path=sibling if sibling.is_file() else packaged
    raw=Path(path).read_bytes()
    if sha256(raw).hexdigest()!=SOURCE_SHA256 or sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=SOURCE_GIT_BLOB:
        raise ValueError('EXFOR byte identity')
    text=raw.decode('ascii')
    if '(COINC,TOF)' not in text or '(ERR-S) Statistical errors.' not in text:raise ValueError('EXFOR metadata')
    section=text.split('SUBENT        M0475002',1)[1].split('ENDSUBENT',1)[0]
    if '(2-HE-4(G,D)1-H-2,,DA)' not in section:raise ValueError('wrong reaction')
    header='MEV        ADEG       NB/SR      NB/SR'
    if header not in section:raise ValueError('units')
    rows=[]
    for line in section.split(header,1)[1].split('ENDDATA',1)[0].splitlines():
        fields=line.split()
        if len(fields)==4:rows.append(tuple(exact(x) for x in fields))
    if len(rows)!=12:raise ValueError('expected 12 DA rows')
    return tuple(rows)

def conditional_inverse_DA(e,theta,convention,source_path=None,inverse_Td=None):
    e,theta=exact(e),exact(theta)
    if inverse_Td is not None and not alignment(e,inverse_Td)['same_s']:
        raise ValueError('invariant-energy mismatch: no interpolation authorized')
    rows=[r for r in read_DA(source_path) if r[0]==e and r[1]==theta]
    if len(rows)!=1:raise ValueError('no exact measured forward DA row')
    _,_,da,stat=rows[0];factor=reciprocity_ratio(e,convention)
    return {'forward_Egamma_MeV':e,'inverse_matched_Td_MeV':T_matching(e),
            'theta_cm_deg':theta,'source_DA_nb_sr':da,'ERR_S_nb_sr':stat,
            'ratio_inverse_to_forward':factor,
            'inverse_lower_nb_sr':max(F(0),da-stat)*factor,
            'inverse_upper_nb_sr':(da+stat)*factor,
            'inverse_measured':None,'event_rate':None,'physical_activation':False,
            'production':'HOLD','L4':False,
            'uncertainty':'coordinatewise_ERR-S_sensitivity_not_joint_CI'}

def forward_event_ledger(e):
    e=exact(e)
    if e<gamma_threshold():raise ValueError('below threshold')
    kinetic=MA+e-2*MD
    return {'n_alpha':-1,'n_gamma':-1,'n_D':2,'rest_MeV':2*MD-MA,
            'D_kinetic_MeV':kinetic,'photon_MeV':-e,
            'energy_residual_MeV':2*MD-MA+kinetic-e,
            'baryon_residual':-4+2*2,'charge_residual':-2+2,
            'momentum_pair_p_c_MeV':e,'thermal_initial_dd_pair_factor':THERMAL_DD_PAIR_FACTOR,
            'event_multiplicity_source':None,'physical_activation':False}

def lab_daughters(e,mu,dps=70):
    """Boost opposite CM daughter momenta to He-target-rest lab.
    E in MeV, p*c in MeV. Strings are high-precision, NOT directed intervals.
    """
    import mpmath as mp
    e=exact(e);mu=exact(mu)
    if not -1<=mu<=1 or type(dps)!=int or not 35<=dps<=150:
        raise ValueError('mu or precision')
    _,q2=cm_momenta_squared(e)
    with mp.workdps(dps):
        cv=lambda z:mp.mpf(z.numerator)/z.denominator
        ee=cv(e);m=cv(MA);md=cv(MD);z=cv(mu)
        s=cv(s_gamma(e));q=mp.sqrt(cv(q2));root=mp.sqrt(s)
        gam=(m+ee)/root
        ep=(m+ee)/2+ee*q*z/root
        em=(m+ee)/2-ee*q*z/root
        pzp=ee/2+gam*q*z
        pzm=ee/2-gam*q*z
        pt2=cv(q2)*(1-z*z)
        fmt=lambda v:mp.nstr(v,dps-12)
        return {'E_plus_MeV':fmt(ep),'E_minus_MeV':fmt(em),
                'p_z_plus_c_MeV':fmt(pzp),'p_z_minus_c_MeV':fmt(pzm),
                'p_transverse_sq_c2_MeV2':fmt(pt2),
                'E_sum_residual_MeV':fmt(ep+em-(m+ee)),
                'pz_sum_residual_MeV':fmt(pzp+pzm-ee),
                'mass_shell_plus_residual_MeV2':fmt(ep*ep-pzp*pzp-pt2-md*md),
                'mass_shell_minus_residual_MeV2':fmt(em*em-pzm*pzm-pt2-md*md),
                'numeric_rounding_certified':False}


def record(e,theta,source_path=None):
    """Compare BOTH conventions without selecting either as physical."""
    out={}
    for convention in (ORDERED,FULL_EVENT):
        x=conditional_inverse_DA(e,theta,convention,source_path)
        out[convention]={k:(str(v) if isinstance(v,F) else v) for k,v in x.items()}
    return out
