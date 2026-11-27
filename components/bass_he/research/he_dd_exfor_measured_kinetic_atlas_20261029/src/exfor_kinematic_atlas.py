"""Source-exact EXFOR M0475 experimental kinetic observable atlas.

The output multiplies published EXFOR DA or SIG by the *exact per-event*
pair kinetic energy for 4He(gamma,d)d, and evaluates exact two-body
kinematics at measured DA angles. It is NOT a measured total SIG at 330
MeV, a detector-normalised event rate, or a caloric/thermalisation kernel.

Physical rest energies are the frozen parent PR104 convention in MeV.
Photons strike a stationary 4He target; metric (-,+,+,+). Source ERR-S
is statistical per coordinate, not a joint confidence law.
"""
from __future__ import annotations
import hashlib
import json
import csv
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import mpmath as mp

RAW_SHA256 = 'b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'
RAW_GIT_BLOB = 'c49433293921dbb012d7f1b0387745732a598efa'
SOURCE_COMMIT = '939a14d7bba1ddce51975cb5e8711ce96b3b0871'
SOURCE_PATH = 'exforall/M04/M0475.x4'
M_ALPHA = Fraction('3727.3794118')  # frozen M_alpha*c^2, MeV
M_D = Fraction('1875.61294500')     # frozen m_d*c^2, MeV
Q = 2*M_D-M_ALPHA
E_THRESHOLD = ((2*M_D)**2-M_ALPHA**2)/(2*M_ALPHA)
_EXPECTED_DA = {(213,46),(213,61),(213,73),(213,87),
                (258,46),(258,61),(258,73),(258,87),
                (330,46),(330,61),(330,73),(330,87)}
_EXPECTED_SIG = {201,225,253,285,320,359}


def _frac_str(x):
    return str(x.numerator) + '/' + str(x.denominator)


def _str_mp(x, decimals=14):
    return mp.nstr(x, max(42, decimals+18))


def parse_exfor(raw: bytes):
    if hashlib.sha256(raw).hexdigest()!=RAW_SHA256:
        raise ValueError('SOURCE_BYTE_IDENTITY_MISMATCH: immutable M0475.x4')
    if len(raw)!=3349:
        raise ValueError('SOURCE_SIZE_MISMATCH')
    text=raw.decode('ascii')
    if 'METHOD     (COINC,TOF)' not in text or 'DETECTOR   (SCIN)' not in text:
        raise ValueError('source experiment semantics changed')
    if '(2-HE-4(G,D)1-H-2,,DA)' not in text or '(2-HE-4(G,D)1-H-2,,SIG)' not in text:
        raise ValueError('source reaction fields changed')
    out={'DA':[], 'SIG':[]}
    lines=text.splitlines()
    subent=None
    for i,line in enumerate(lines):
        if line.startswith('SUBENT'):
            subent=line.split()[1]
        if line.startswith('DATA '):
            cells=line.split()
            ncols,nrows=map(int,cells[1:3]); header=lines[i+1].split(); units=lines[i+2].split()
            expected=(('M0475002',4,12,['EN','ANG-CM','DATA-CM','ERR-S'],['MEV','ADEG','NB/SR','NB/SR']),
                      ('M0475003',3,6,['EN','DATA','ERR-S'],['MEV','NB','NB']))
            matching=[e for e in expected if e[0]==subent]
            if len(matching)!=1:raise ValueError('unexpected DATA SUBENT')
            _,nc,nr,h,u=matching[0]
            if (ncols,nrows,header,units)!=(nc,nr,h,u):
                raise ValueError('EXFOR HEADER/UNITS/GRAIN MISMATCH')
            for row in lines[i+3:i+3+nrows]:
                values=row.split()
                if len(values)!=nc: raise ValueError('incomplete EXFOR data row')
                cells=[Fraction(x) for x in values]
                if subent=='M0475002':
                    E,theta,v,e=cells
                    out['DA'].append({'E_MeV':E,'theta_CM_deg':theta,'DA_nb_sr':v,'ERR_S_nb_sr':e})
                else:
                    E,v,e=cells
                    out['SIG'].append({'E_MeV':E,'SIG_nb':v,'ERR_S_nb':e})
    if ({(int(z['E_MeV']),int(z['theta_CM_deg'])) for z in out['DA']}!=_EXPECTED_DA
       or {int(z['E_MeV']) for z in out['SIG']}!=_EXPECTED_SIG
       or len(out['DA'])!=12 or len(out['SIG'])!=6):
        raise ValueError('EXFOR row identity/count discrepancy')
    return out


def two_body(E:Fraction,theta_deg:Fraction):
    """CM angle, target-alpha-rest LAB momenta pc and kinetic energies MeV.

    Returns high precision numbers from the parent frozen exact decimal rest
    energies. +/- denotes only a chosen CM labelling, not a measured arm tag.
    """
    if E<E_THRESHOLD:raise ValueError('below exact recoil threshold')
    if not 0<=theta_deg<=180:raise ValueError('CM angle out of range')
    mp.mp.dps=90
    M,m,e,theta=(mp.mpf(x.numerator)/x.denominator for x in (M_ALPHA,M_D,E,theta_deg))
    s=M*M+2*M*e
    q=mp.sqrt(s/4-m*m)
    beta=e/(M+e)
    gamma=(M+e)/mp.sqrt(s)
    mu=mp.cos(mp.pi*theta/180)
    sint=mp.sin(mp.pi*theta/180)
    delta=beta*gamma*q
    K0=(M+e)/2-m
    Kplus=K0+delta*mu
    Kminus=K0-delta*mu
    pzplus=e/2+gamma*q*mu
    pzminus=e/2-gamma*q*mu
    pt=q*sint
    Eplus=m+Kplus
    Eminus=m+Kminus
    mass1=Eplus**2-pzplus**2-pt**2-m*m
    mass2=Eminus**2-pzminus**2-pt**2-m*m
    lab_theta_plus=mp.degrees(mp.atan2(pt,pzplus))
    lab_theta_minus=mp.degrees(mp.atan2(pt,pzminus))
    return {'Kplus':Kplus,'Kminus':Kminus,'K0':K0,'delta':delta,'p_parallel_plus_c':pzplus,
            'p_parallel_minus_c':pzminus,'p_transverse_c':pt,
            'theta_lab_plus_deg':lab_theta_plus,'theta_lab_minus_deg':lab_theta_minus,
            'shell_residual_plus_MeV2':mass1,'shell_residual_minus_MeV2':mass2,
            'pair_total_energy_residual_MeV':Eplus+Eminus-M-e,
            'pair_momentum_parallel_residual_MeV':pzplus+pzminus-e,
            's_MeV2':s,'q_CM_MeV':q,
            'p_cm_ratio_recoil':beta}


def generate(input_path:Path,output:Path):
    data=parse_exfor(input_path.read_bytes())
    output.mkdir(parents=True,exist_ok=True)
    mp.mp.dps=90
    da=[];sig=[]
    for row in data['DA']:
        E,theta,v,err=(row[k] for k in ('E_MeV','theta_CM_deg','DA_nb_sr','ERR_S_nb_sr'))
        kin=two_body(E,theta)
        Qkin=E-Q
        d={'source_subent':'M0475002','gamma_E_lab_MeV':str(E),
           'theta_d_CM_deg':str(theta),'DA_nb_per_sr':str(v),'DA_ERR_S_nb_per_sr':str(err),
           'pair_Ksum_MeV':str(Qkin),'pair_Ksum_fraction':_frac_str(Qkin),
           'DA_times_pairK_nb_MeV_per_sr':str(v*Qkin),
           'DA_ERR_S_times_pairK_nb_MeV_per_sr':str(err*Qkin),
           'DA_times_pairK_fraction':_frac_str(v*Qkin),
           'Kplus_target_rest_MeV':_str_mp(kin['Kplus']),
           'Kminus_target_rest_MeV':_str_mp(kin['Kminus']),
           'theta_lab_plus_deg':_str_mp(kin['theta_lab_plus_deg']),
           'theta_lab_minus_deg':_str_mp(kin['theta_lab_minus_deg']),
           'p_parallel_plus_c_MeV':_str_mp(kin['p_parallel_plus_c']),
           'p_parallel_minus_c_MeV':_str_mp(kin['p_parallel_minus_c']),
           'p_transverse_c_MeV':_str_mp(kin['p_transverse_c']),
           'DA_times_Kplus_nb_MeV_per_sr':_str_mp(mp.mpf(v.numerator)/v.denominator*kin['Kplus']),
           'DA_times_Kminus_nb_MeV_per_sr':_str_mp(mp.mpf(v.numerator)/v.denominator*kin['Kminus']),
           'stat_err_times_Kplus_nb_MeV_per_sr':_str_mp(mp.mpf(err.numerator)/err.denominator*kin['Kplus']),
           'stat_err_times_Kminus_nb_MeV_per_sr':_str_mp(mp.mpf(err.numerator)/err.denominator*kin['Kminus']),
           'max_abs_mass_shell_residual_MeV2':_str_mp(max(abs(kin['shell_residual_plus_MeV2']),abs(kin['shell_residual_minus_MeV2'])))
           }
        da.append(d)
    for row in data['SIG']:
        E,v,err=(row[k] for k in ('E_MeV','SIG_nb','ERR_S_nb'))
        Kpair=E-Q
        sig.append({'source_subent':'M0475003','gamma_E_lab_MeV':str(E),
                    'SIG_reported_nb':str(v),'SIG_ERR_S_nb':str(err),
                    'pair_Ksum_MeV':str(Kpair),'pair_Ksum_fraction':_frac_str(Kpair),
                    'SIG_reported_times_pairK_nb_MeV':str(v*Kpair),
                    'ERR_S_times_pairK_nb_MeV':str(err*Kpair),
                    'SIG_times_pairK_fraction':_frac_str(v*Kpair)})
    root={'schema':'BASS_HE_EXFOR_M0475_PHYSICAL_DATA_ATLAS_V1','source':{
          'repository':'IAEA-NDS/exfor_master','commit':SOURCE_COMMIT,'path':SOURCE_PATH,
          'raw_sha256':RAW_SHA256,'raw_git_blob':RAW_GIT_BLOB,'raw_size':3349,
          'differential_subent':'M0475002','total_subent':'M0475003','stat_error_type':'ERR-S'},
          'masses':{'convention':'PR104 frozen rest-energy MeV; not an independent new mass evaluation',
                    'M_alpha_c2_MeV':str(M_ALPHA),'m_deuteron_c2_MeV':str(M_D),
                    'mass_gap_Q_MeV':str(Q),'photon_threshold_E_MeV':str(E_THRESHOLD),
                    'mass_gap_Q_fraction':_frac_str(Q),'threshold_E_fraction':_frac_str(E_THRESHOLD)},
          'derivation':{'pair_kinetic':'E_gamma-(2m_d-M_alpha)c²',
                        's_MeV2':'M²+2ME_gamma',
                        'CM_q2_MeV2':'s/4-m²',
                        'E_lab_pm_MeV':'(M+E)/2 +/- E/sqrt(s)*sqrt(s/4-m²)*cos(theta_cm)',
                        'DA_pairK':'DA_reported * pair_kinetic',
                        'SIG_pairK':'SIG_reported * pair_kinetic',
                        'ERR_S':'same deterministic multiplication; not a joint confidence law'},
          'interpretation':{'event_sigma_normalization':'UNRESOLVED',
                            '330MeV_total_SIG':'NOT_MEASURED_IN_SOURCE',
                            'DA_azimuth_polarization_response':'UNRESOLVED',
                            'pair_Ksum':'kinematic identity, NOT heat',
                            'physical_gamma_history':'MISSING','D_fast_deposition':'MISSING',
                            'R_event':None,'kappa':None,'heat_rate':None,
                            'physical_activation':False,'L4':False,'production':'HOLD'},
          'row_count':{'DA':len(da),'SIG':len(sig)},'data':{'DA':da,'SIG':sig}}
    (output/'ATLAS.json').write_text(json.dumps(root,ensure_ascii=False,indent=2)+'\n')
    for name,rows in [('DA',da),('SIG',sig)]:
        with (output/(name+'_ENERGY_WEIGHTED.csv')).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return root


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    root=generate(a.source,a.out)
    print(f"ACTUAL_SOURCE_DATA_ROWS DA={len(root['data']['DA'])} SIG={len(root['data']['SIG'])}; bytes={root['source']['raw_size']}")
    for x in root['data']['SIG']:
        print('SIG',x['gamma_E_lab_MeV'],x['SIG_reported_times_pairK_nb_MeV'],x['ERR_S_times_pairK_nb_MeV'])
