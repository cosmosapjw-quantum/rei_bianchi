#!/usr/bin/env python3
"""Pitts 1989 EXFOR C0621: source-exact measured capture and conditional inverse.

No source interpolation, experimental photon field, thermalization or event-rate claims.
Mass energies in MeV, p*c in MeV, metric (-,+,+,+).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from fractions import Fraction as F
from decimal import Decimal, localcontext
from pathlib import Path

SOURCE_BYTES = 3269
SOURCE_SHA256 = '9c3b49e979e9bb389b2e046e33dec3eb95ebbbed9772a3a47391d5529aaac2ea'
SOURCE_GIT_BLOB = 'ddeb728a59905ca669b3408e9338b8d300d5c96e'
SOURCE_COMMIT = '939a14d7bba1ddce51975cb5e8711ce96b3b0871'
M = F('3727.3794118')  # M_alpha*c^2, MeV (frozen PR104)
m = F('1875.61294500')  # m_d*c^2, MeV
T = F(95)
C = 299792458  # m/s retained for SI conversion via 1 nb = 1e-37 m^2
NORM = F(4, 100)
KIND = {'C0621002': ('DA', 'NB/SR', 'NB/SR', '(1-H-2(D,G)2-HE-4,,DA)'),
        'C0621003': ('Ay', 'NO-DIM', 'NO-DIM', '(1-H-2(D,G)2-HE-4,,POL/DA,,ANA)'),
        'C0621004': ('Ayy', 'NO-DIM', 'NO-DIM', '(1-H-2(D,G)2-HE-4,NN,POL/DA,,ANA)')}


def source(path: Path) -> tuple[bytes, dict]:
    raw = path.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if len(raw)!=SOURCE_BYTES or hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256 or blob!=SOURCE_GIT_BLOB:
        raise ValueError('SOURCE_IDENTITY_MISMATCH')
    text=raw.decode('ascii')
    if '95.' not in text.split('SUBENT        C0621002')[0] or 'exclusive of normalization uncertainty of 4%' not in text:
        raise ValueError('SOURCE_BIB_MISSING')
    data={}
    for sub, (kind, unit, errunit, reaction) in KIND.items():
        sec=text.split('SUBENT        '+sub, 1)[1].split('ENDSUBENT', 1)[0]
        if reaction not in sec:
            raise ValueError('SOURCE_UNITS_OR_REACTION')
        lines=sec.splitlines()
        header_pos=next((j for j,line in enumerate(lines) if line.split()==['ADEG',unit,errunit]),None)
        if header_pos is None:
            raise ValueError('SOURCE_UNITS_OR_REACTION')
        rows=[]
        dat='\n'.join(lines[header_pos+1:]).split('ENDDATA',1)[0]
        for line in dat.splitlines():
            fields=line.split()
            if len(fields)==3:
                try:
                    th,val,err=map(F,fields)
                except ValueError:
                    raise ValueError('SOURCE_NUMERIC_PARSE') from None
                rows.append({'theta':th,'value':val,'data_err':err})
        if len(rows)!=8 or len(set(r['theta'] for r in rows))!=8:
            raise ValueError('SOURCE_ROW_COUNT')
        if any(r['data_err']<=0 for r in rows):
            raise ValueError('SOURCE_NONPOSITIVE_ERROR')
        if kind=='DA' and any(r['value']<=0 for r in rows):
            raise ValueError('SOURCE_NONPOSITIVE_DA')
        data[kind]=rows
    if not [r['theta'] for r in data['DA']]==[r['theta'] for r in data['Ay']]==[r['theta'] for r in data['Ayy']]:
        raise ValueError('ANGLE_ALIGNMENT')
    return raw,data


def invariants():
    s=4*m*m+2*m*T
    q2=(s-4*m*m)/4
    k2=(s-M*M)**2/(4*s)
    e=(s-M*M)/(2*M)
    if not s>4*m*m or not k2>0 or not q2>0: raise ValueError('BELOW_THRESHOLD')
    ordered=F(9,2)*q2/k2  # inverse/forward, spin 9/2
    event=ordered/2  # full-sphere (identical final D) differential convention
    reverse=F(2,9)*k2/q2  # forward/inverse, NOT inverse/forward
    if ordered*reverse!=1 or event*2!=ordered: raise AssertionError('RECIPROCITY')
    return {'s':s,'q2':q2,'k2':k2,'Egamma':e,'ordered':ordered,'event':event,
            'capture_over_photo_ordered':reverse,'Q':2*m-M}


def decimal_str(x: F, digits: int=19) -> str:
    with localcontext() as ctx:
        ctx.prec=45
        v=Decimal(x.numerator)/Decimal(x.denominator)
        return format(v, f'.{digits}g')


def generate(root: Path) -> dict:
    raw,entries=source(root/'sources/C0621.x4')
    k=invariants()
    with localcontext() as ctx:
        ctx.prec=42
        sqrts= (Decimal(k['s'].numerator)/Decimal(k['s'].denominator)).sqrt()
        rootq=(Decimal(k['q2'].numerator)/Decimal(k['q2'].denominator)).sqrt()
        energy=Decimal(k['Egamma'].numerator)/Decimal(k['Egamma'].denominator)
        amp=energy*rootq/sqrts
        cen=Decimal((k['Egamma']-k['Q']).numerator)/Decimal((k['Egamma']-k['Q']).denominator)/Decimal(2)
    outcomes=[]
    for i,obs in enumerate(entries['DA']):
        angle=int(obs['theta']);s=float(obs['value']);e=float(obs['data_err'])
        import math
        cth=math.cos(math.radians(angle))  # diagnostic angle evaluation only
        # Labeling of identical deuterons is arbitrary; ordered pair is symmetric.
        e_plus=float(cen)+float(amp)*cth
        e_minus=float(cen)-float(amp)*cth
        if abs((e_plus+e_minus)-float(k['Egamma']-k['Q']))>1e-10:
            raise AssertionError('PAIR_KINETIC_ENERGY_NONCONSERVATION')
        out={'source_subentry':'C0621002','source_row_1based':i+1,
             'theta_cm_deg':angle,
             'measured_capture_DA_nb_per_sr':decimal_str(obs['value']),
             'source_DATA_ERR_nb_per_sr_excludes_norm':decimal_str(obs['data_err']),
             'unpolarized_DA_status':'SOURCE_REPORTED_ABSOLUTE',
             'Ay_measured':decimal_str(entries['Ay'][i]['value']),
             'Ay_ERR_S':decimal_str(entries['Ay'][i]['data_err']),
             'Ayy_measured':decimal_str(entries['Ayy'][i]['value']),
             'Ayy_ERR_S':decimal_str(entries['Ayy'][i]['data_err']),
             'conditional_ordered_photo_DA_nb_per_sr':decimal_str(obs['value']*k['ordered']),
             'conditional_ordered_DATA_ERR_nb_per_sr':decimal_str(obs['data_err']*k['ordered']),
             'conditional_event_fullsphere_photo_DA_nb_per_sr':decimal_str(obs['value']*k['event']),
             'conditional_event_fullsphere_DATA_ERR_nb_per_sr':decimal_str(obs['data_err']*k['event']),
             'conditional_photo_Kplus_MeV':format(e_plus,'.14g'),
             'conditional_photo_Kminus_MeV':format(e_minus,'.14g'),
             'conditional_photo_Ksum_MeV':decimal_str(k['Egamma']-k['Q']),
             'source_4pct_common_norm_component_nb_per_sr':decimal_str(obs['value']*NORM),
             'photo_measured':False,'event_rate':None,'heat_rate':None}
        outcomes.append(out)
    # One source-reported correlated 4%-scale component; other covariance not supplied.
    norm_cov=[[decimal_str(NORM*NORM*ai['value']*aj['value']) for aj in entries['DA']] for ai in entries['DA']]
    capture_shape=entries['DA'][2]['value']/entries['DA'][7]['value']
    model={'schema':'HE_DD_PITTS95_C0621_SOURCE_QUALIFIED_CAPTURE_CONDITIONAL_PHOTO_V1',
           'original_source':{'repository':'IAEA-NDS/exfor_master','snapshot':SOURCE_COMMIT,
             'path':'exforall/C06/C0621.x4','sha256':SOURCE_SHA256,'git_blob':SOURCE_GIT_BLOB,'bytes':len(raw),
             'source_experiment':'Pitts et al. 1989 Physical Review C 39 1679',
             'doi':'10.1103/PhysRevC.39.1679','status':'AUTHOR_APPROVED_EXFOR',
             'target':'D on D','incident_Td_lab_MeV':'95',
             'measured_original_rows':24,'DA_absolute_rows':8,'Ay_rows':8,'Ayy_rows':8,
             'measured_photodisintegration_rows':0,
             'DA_DATA_ERR':'statistical+systematic, exclusive separate 4pct normalization'},
           'kinematics':{'M_alpha_c2_MeV':decimal_str(M),'m_deuteron_c2_MeV':decimal_str(m),
             'Q_MeV':decimal_str(k['Q']), 's_MeV2':decimal_str(k['s']),
             'matched_alpha_rest_gamma_MeV':decimal_str(k['Egamma']),
             'cm_photon_pc_MeV':format(float(k['k2'])**.5,'.16g'),
             'cm_deuteron_pc_MeV':format(float(k['q2'])**.5,'.16g'),
             'inverse_ordered_over_capture':decimal_str(k['ordered']),
             'inverse_event_fullsphere_over_capture':decimal_str(k['event']),
             'capture_over_inverse_ordered':decimal_str(k['capture_over_photo_ordered']),
             'pair_kinetic_sum_MeV':decimal_str(k['Egamma']-k['Q']),
             'momentum_convention':'q and k represent p*c in MeV'},
           'measured_shape':{'DA_90deg_over_DA_149deg':decimal_str(capture_shape),
             'common_4pct_norm_cancels_in_shape_ratio':True,
             'ratio_uncertainty_unknown_covariance':True},
           'data':outcomes,
           'source_normalization_covariance_component_nb2_per_sr2':norm_cov,
           'covariance_policy':{'common_4percent_component':'rank_one_if_single_multiplicative_source_scale',
             'residual_covariance':'UNKNOWN_NOT_DIAGONAL_BY_DEFAULT',
             'source_DATA_ERR_includes_stat_plus_other_systematic':'DO_NOT_DOUBLE_COUNT',
             'total_matrix_certified':False},
           'physical_claims':{'absolute_capture_measured':True,'conditional_photo_ordered_data':8,
             'conditional_photo_fullsphere_data':8,'physical_photo_measured':False,
             'identical_D_event_convention_verified':False,'beam_polarization_correction_source_fulltext_verified':False,
             'angular_acceptance_full_4pi':False,'R_event':None,'heat_rate':None,'kappa':None,'L4':False,'production':'HOLD'},
           'DAG':{'central':'28/88','HE_physical':'14/18','new_source_scoped':'2/2','physical_delta':0},
           'model_warning': 'The conditional inverse values are not Rice measurements, total cross sections, cosmological rates, or independently normalized photon bath.'}
    result=root/'results';result.mkdir(parents=True,exist_ok=True)
    (result/'PITTS95_SOURCE_RECIPROCITY_ATLAS.json').write_text(json.dumps(model,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    import csv
    with (result/'PITTS95_CAPTURE_TO_PHOTO_CONDITIONAL_8.csv').open('w',newline='',encoding='utf-8') as fh:
        keys=['theta_cm_deg','measured_capture_DA_nb_per_sr','source_DATA_ERR_nb_per_sr_excludes_norm',
              'Ay_measured','Ayy_measured','conditional_ordered_photo_DA_nb_per_sr',
              'conditional_event_fullsphere_photo_DA_nb_per_sr','conditional_photo_Kplus_MeV',
              'conditional_photo_Kminus_MeV']
        w=csv.DictWriter(fh,fieldnames=keys);w.writeheader();w.writerows([{k:r[k] for k in keys} for r in outcomes])
    return model

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',default='.',type=Path);args=a.parse_args()
    x=generate(args.root)
    print(json.dumps({'source':x['original_source'],'kinematics':x['kinematics'],
                      'n_data':len(x['data']),'dag':x['DAG']},ensure_ascii=False,indent=2))
