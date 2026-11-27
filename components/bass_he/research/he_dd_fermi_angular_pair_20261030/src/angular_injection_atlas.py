"""Source-owned Fermi×EXFOR measured-coordinate angular D-pair response atlas.

These are reported-DA-weighted, *spectral-model-conditional*, z~0
observer/He-frame coincident direction responses, NOT calibrated exclusive
rates, direct Fermi differential intensity measurements, or thermal heat.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import mpmath as mp
from scipy.integrate import quad

EXFOR_SHA256='b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'
EXFOR_BLOB='c49433293921dbb012d7f1b0387745732a598efa'
FERMI_SHA256='a78ced8234a7eb104a5f5b406a6bc609591ec2c323a26008625b239b5dccc0e5'
FERMI_BLOB='794cb6fcbef243be950613475c4254d6ab3877a4'
M_ALPHA=F('3727.3794118') # M_alpha*c^2 in MeV
M_D=F('1875.61294500') # m_d*c^2 in MeV
Q=2*M_D-M_ALPHA
E_THRESHOLD=Q+Q*Q/(2*M_ALPHA)
NB_TO_CM2=1e-33
EXPECTED_COORDS={(e,a) for e in (213,258,330) for a in (46,61,73,87)}
FERMI_SHAPES={'A':(2.32,279_000.),'B':(2.28,206_000.),'C':(2.26,233_000.)}
FERMI_NAMES=('IGRB','EGB')


def _gitblob(raw:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def _exact_source(path:Path, sha:str, blob:str)->bytes:
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha or _gitblob(raw)!=blob:
        raise ValueError('IMMUTABLE_SOURCE_BYTES_MISMATCH: '+str(path))
    return raw


def source_da(path:Path):
    raw=_exact_source(path,EXFOR_SHA256,EXFOR_BLOB)
    lines=raw.decode('ascii').splitlines()
    sub=None; records=[]
    for i,line in enumerate(lines):
        if line.startswith('SUBENT'):
            sub=line.split()[1]
        if line.startswith('DATA '):
            words=line.split()
            if sub=='M0475002':
                if words[1:3]!=['4','12'] or lines[i+1].split()!=['EN','ANG-CM','DATA-CM','ERR-S'] or lines[i+2].split()!=['MEV','ADEG','NB/SR','NB/SR']:
                    raise ValueError('EXFOR_DA_GRAIN_UNITS')
                for l in lines[i+3:i+15]:
                    e,a,v,err=map(F,l.split())
                    records.append((e,a,v,err))
            elif sub=='M0475003':
                if words[1:3]!=['3','6']:
                    raise ValueError('EXFOR_SIG_GRAIN')
    if len(records)!=12 or {(int(e),int(a)) for e,a,_,_ in records}!=EXPECTED_COORDS:
        raise ValueError('EXFOR_DA_COORDINATES')
    if any(e<E_THRESHOLD or v<0 or err<0 for e,a,v,err in records):
        raise ValueError('INVALID_EXFOR_VALUES')
    return records


def source_fermi(path:Path):
    raw=_exact_source(path,FERMI_SHA256,FERMI_BLOB)
    records=[]
    for line in raw.decode('ascii').splitlines():
        if not line.startswith(('A ','B ','C ')):
            continue
        v=line.split()
        if len(v)!=16:
            raise ValueError('FERMI_SCHEMA')
        m=v[0]
        row={'FG':m,'energy_min_MeV':float(v[1]),'energy_max_MeV':float(v[2])}
        for k,val in zip(('IGRB','IGRB_basic_plus','IGRB_basic_minus','IGRB_fg_plus','IGRB_fg_minus',
                          'EGB','EGB_basic_plus','EGB_basic_minus','EGB_fg_plus','EGB_fg_minus',
                          'fsrc','fsrc_basic_plus','fsrc_basic_minus'),v[3:]):
            row[k]=float(val)
        records.append(row)
    counts=Counter(x['FG'] for x in records)
    if dict(counts)!={'A':26,'B':26,'C':26}:
        raise ValueError('FERMI_ABC_78_ROWS')
    signatures={m:tuple((r['energy_min_MeV'],r['energy_max_MeV']) for r in records if r['FG']==m) for m in 'ABC'}
    if not signatures['A']==signatures['B']==signatures['C']:
        raise ValueError('FERMI_ENERGY_BINS_DIFFER')
    selected=[r for r in records if (r['energy_min_MeV'],r['energy_max_MeV']) in ((200.0,282.8),(282.8,400.0))]
    if len(selected)!=6:
        raise ValueError('FERMI_REQUIRED_BINS')
    # fsrc published once, repeated across foreground models; don't treat as 3 independent measurements.
    for k in ('fsrc','fsrc_basic_plus','fsrc_basic_minus'):
        if not selected[0][k]==selected[2][k]==selected[4][k] or not selected[1][k]==selected[3][k]==selected[5][k]:
            raise ValueError('RESOLVED_SOURCE_NOT_REPEATED')
    return records


def _norm_shape(E,lo,hi,model,fg):
    if model=='flat': return 1.0/(hi-lo)
    gamma,cutoff=FERMI_SHAPES[fg]
    def fn(x):return (x/100.0)**(-gamma)*math.exp(-x/cutoff)
    integral=quad(fn,lo,hi,epsabs=1e-12,epsrel=1e-12)[0]
    return fn(E)/integral


def two_body(E:F,angle:F):
    """The + and - are symmetric kinematic labels, NOT measured detector-arm names.
    The photon is along +z. Outputs E[MeV], pc[MeV] and cos(theta_cm).
    """
    if E<E_THRESHOLD or not F(0)<=angle<=F(180):
        raise ValueError('KINEMATIC_DOMAIN')
    mp.mp.dps=80
    conv=lambda x:mp.mpf(x.numerator)/x.denominator
    M,m,e,th=map(conv,(M_ALPHA,M_D,E,angle))
    s=M*M+2*M*e
    q=mp.sqrt(s/4-m*m)
    mu=mp.cos(mp.pi*th/180)
    a=e*q*mu/mp.sqrt(s)
    bx=(q*mp.sqrt(1-mu*mu))
    bz=(M+e)*q*mu/mp.sqrt(s)
    plus=((M+e)/2+a,(bx,mp.mpf('0'),e/2+bz))
    minus=((M+e)/2-a,(-bx,mp.mpf('0'),e/2-bz))
    labang=lambda p:mp.degrees(mp.atan2(abs(p[1][0]),p[1][2]))
    shell=lambda p:p[0]**2-sum(v*v for v in p[1])-m*m
    return {'Kplus':plus[0]-m,'Kminus':minus[0]-m,
            'Pplus':plus,'Pminus':minus,'theta_lab_plus':labang(plus),'theta_lab_minus':labang(minus),
            'shell_plus':shell(plus),'shell_minus':shell(minus),'CM_cos':mu}


def generate(root:Path):
    da=source_da(root/'sources/M0475.x4')
    fermi=source_fermi(root/'sources/fermi_igrb_2015_AB_C_78row_mirror.csv')
    subset={(r['FG'],r['energy_min_MeV']):r for r in fermi if r['energy_min_MeV'] in (200.,282.8)}
    omega_high=4*math.pi*(1-math.sin(math.radians(20)))
    data=[]
    for e,ang,reported,err in da:
        ev=float(e)
        lo=200. if ev<282.8 else 282.8
        hi=282.8 if lo==200. else 400.
        kine=two_body(e,ang)
        pairK=e-Q
        for fg in 'ABC':
            original=subset[(fg,lo)]
            for component in FERMI_NAMES:
                for shape in ('flat','model_ple_igrb'):
                    fI=original[component]*_norm_shape(ev,lo,hi,shape,fg)
                    omega=4*math.pi # isotropic sky assumed, not observed anisotropy-free EGB.
                    val=omega*fI*float(reported)*NB_TO_CM2
                    errda=omega*fI*float(err)*NB_TO_CM2
                    data.append(make_row(e,ang,reported,err,kine,pairK,fg,component,shape,lo,hi,
                                         omega,fI,val,errda,original,
                                         'local_observer_isotropic_He_rest_ASSUMPTION'))
        # Fermi resolved source, only ONE original fsrc spectrum, no independent FG duplicates.
        original=subset[('A',lo)]
        for shape in ('flat','model_ple_igrb'):
            fI=original['fsrc']*_norm_shape(ev,lo,hi,shape,'A')
            val=omega_high*fI*float(reported)*NB_TO_CM2
            errda=omega_high*fI*float(err)*NB_TO_CM2
            data.append(make_row(e,ang,reported,err,kine,pairK,'COMMON','fsrc_high_lat',shape,lo,hi,
                                 omega_high,fI,val,errda,original,
                                 'uniform_within_high_latitude_mask_He_rest_ASSUMPTION'))
    if len(data)!=168:raise ValueError('OUTPUT_168_ROW_GRAIN')
    result={'schema':'BASS_HE_FERMI_M0475_ANGULAR_DPAIR_LIFT_V1','citation':{
        'exfor':'IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4',
        'exfor_sha256':EXFOR_SHA256,'exfor_git_blob':EXFOR_BLOB,
        'fermi':'Ackermann et al. ApJ 799:86 (2015) Table3, DOI:10.1088/0004-637X/799/1/86',
        'fermi_mirror':'82492749123082/KM3-230213A_UHECR_TA@774174d9faaa5df40b67af5fa42b4191f09d38c6',
        'fermi_sha256':FERMI_SHA256,'fermi_git_blob':FERMI_BLOB,
        'original_CDS_byte_verified':False},
        'units':{'energy':'MeV','reported_DA':'nb/sr_CM','Fermi_bin_flux':'photons cm^-2 s^-1 sr_sky^-1',
        'Gamma_like':'s^-1 MeV^-1 sr_CM^-1 per He (conditional, NOT event rate)',
        'GammaK_like':'MeV s^-1 MeV^-1 sr_CM^-1 per He (conditional, NOT heat)',
        'momenta':'p*c in MeV; energies in MeV'},
        'science':{'measured_DA_rows':12,'contexts_per_DA':14,'rows':len(data),
            'measured_gamma_flux_bins_per_fg':2,'observed_gamma_fgs':3,
            'resolved_fsrc_is_single_shared_measurement':True,
            'identical_daughter_pair_count_per_event':2,
            'DA_exclusive_event_normalization':'UNRESOLVED',
            'pointwise_gamma_shape':'MODEL_DEPENDENT_NOT_MEASURED',
            'photon_He_rest_frame':'ASSUMED_NOT_SOURCE_QUALIFIED',
            'kappa':None,'R_event':None,'heat_rate':None,'physical_activation':False,
            'L4':False,'production':'HOLD'},
        'masses':{'Q_MeV':str(Q),'threshold_MeV':str(E_THRESHOLD),'M_alpha_c2_MeV':str(M_ALPHA),'m_d_c2_MeV':str(M_D)},
        'data':data}
    out=root/'results';out.mkdir(exist_ok=True)
    (out/'ANGULAR_DPAIR_FERMI_168.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    cols=[k for k in data[0] if not isinstance(data[0][k],dict)]
    with (out/'ANGULAR_DPAIR_FERMI_168.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for r in data:writer.writerow({k:r[k] for k in cols})
    # Source-observed *measured DA*, not rate-like spectrum model outputs.
    observed=[{'E_gamma_MeV':str(e),'theta_CM_deg':str(ang),'DA_reported_nb_sr':str(rep),'ERR_S_nb_sr':str(err),
                'pair_Ksum_MeV':str(e-Q),'pair_Ksum_exact_fraction':str(e-Q),
                'Kplus_MeV':mp.nstr(two_body(e,ang)['Kplus'],40),
                'Kminus_MeV':mp.nstr(two_body(e,ang)['Kminus'],40)} for e,ang,rep,err in da]
    (out/'MEASURED_ANGULAR_DPAIR_12.json').write_text(json.dumps(observed,indent=2)+'\n')
    print(json.dumps({'rows':len(data),'observed_DA':len(observed),'contexts':len(data)//len(observed),
                      'sample_330_FG_A_IGRB_flat':next(x for x in data if x['E_gamma_MeV']=='330' and x['theta_CM_deg']=='46' and x['FG']=='A' and x['component']=='IGRB' and x['shape']=='flat')['Gamma_reported_like_per_MeV_per_srCM_s_He']},indent=2))
    return result


def make_row(e,ang,da,err,kin,pairK,fg,component,shape,lo,hi,omega,flux,val,valerr,src,geometry):
    if component=='fsrc_high_lat': keys=('fsrc_basic_plus','fsrc_basic_minus'); fgkeys=(None,None);I=src['fsrc']
    else:keys=(component+'_basic_plus',component+'_basic_minus');fgkeys=(component+'_fg_plus',component+'_fg_minus');I=src[component]
    def scaled(s): return val*(s/I)
    return {'E_gamma_MeV':str(e),'theta_CM_deg':str(ang),'FG':fg,'component':component,'shape':shape,
            'Fermi_lower_MeV':lo,'Fermi_upper_MeV':hi,
            'gamma_energy_spectral_intensity_model_photons_cm2_s_sr_MeV':flux,
            'sky_solid_angle_sr_assumed':omega,'target_geometry':geometry,
            'DA_reported_nb_per_sr_CM':str(da),'DA_ERR_S_nb_per_sr_CM':str(err),
            'Gamma_reported_like_per_MeV_per_srCM_s_He':val,
            'Gamma_ERR_S_DA_only_abs_scale':valerr,
            'Gamma_Fermi_basic_plus_only_scale':scaled(src[keys[0]]),
            'Gamma_Fermi_basic_minus_only_scale':scaled(src[keys[1]]),
            'Gamma_Fermi_fg_plus_only_scale':None if fgkeys[0] is None else scaled(src[fgkeys[0]]),
            'Gamma_Fermi_fg_minus_only_scale':None if fgkeys[1] is None else scaled(src[fgkeys[1]]),
            'pair_Ksum_MeV':str(pairK),'Kplus_target_rest_MeV':mp.nstr(kin['Kplus'],40),
            'Kminus_target_rest_MeV':mp.nstr(kin['Kminus'],40),
            'theta_lab_plus_deg':mp.nstr(kin['theta_lab_plus'],25),
            'theta_lab_minus_deg':mp.nstr(kin['theta_lab_minus'],25),
            'p_plus_pc_MeV':','.join(mp.nstr(x,25) for x in kin['Pplus'][1]),
            'p_minus_pc_MeV':','.join(mp.nstr(x,25) for x in kin['Pminus'][1]),
            'GammaK_reported_like_MeV_per_MeV_per_srCM_s_He':val*float(pairK),
            'K_single_D_marginal_mean_MeV':mp.nstr((kin['Kplus']+kin['Kminus'])/2,30),
            'K_single_D_marginal_variance_MeV2':mp.nstr((kin['Kplus']-kin['Kminus'])**2/4,30)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
    generate(a.root)
