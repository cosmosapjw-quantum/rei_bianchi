#!/usr/bin/env python3
"""Source-locked IAEA EXFOR inverse DD radiative capture laboratory data atlas.

Imports original experimental measurements without changing relative/partial/
polarization observable authority. Derived energies are exact relativistic
kinematics in target-alpha rest frame, NOT event-rate cross sections.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
import math

getcontext().prec = 38
Q = Decimal('23.84647820')
M_ALPHA = Decimal('3727.37941180') # MeV/c^2 mass-energy equivalent
M_D = Decimal('1875.61294500')
SOURCE = {
 'C0122': ('d8607f894d437ae8113f2c230b7d08b13ff49521c589791200564f1ff1a943c7','ac638ddbea7795b281ab8494d3e75a62606b3f6d'),
 'A1256': ('456fe18134fec0a25d981148989c9af3faae447f4881dddb6f6f7dd102bfe9e4','b4dba8ecb9ce5eb44501b9afba4c40db329b826b'),
 'M0011': ('8d45af5ca4f0df3c000a5cf672cd84e2e8512b65b52b03a912c5080d2bf5d9b2','20804471fb7584e07ab979ecad6a3e96cba0c6a2'),
 'M0826': ('05ea65eaa1a7245f19fd47aa14e91bef3d706fe2a55c6d70a512808ee4e9284c','95010842754215e98eea8d99eff5f3de0799c666')
}
# Values are group labels only, NEVER allowed to substitute for another observable.
REGISTRY = {
 'C0122002': ('capture_REL_DA', 'NO-DIM', 30, 3, 6),
 'C0122003': ('capture_REL_DA', 'NO-DIM', 50, 3, 8),
 'C0122004': ('capture_POL_ANA_two_components', 'NO-DIM', None, 6, 11),
 'C0122005': ('capture_POL_ANA_two_components', 'NO-DIM', 20, 5, 4),
 'A1256002': ('capture_PAR_DA', 'MB/SR', Decimal('9.7'), 3, 6),
 'A1256003': ('capture_TAP_polarization', 'NO-DIM', Decimal('9.7'), 3, 6),
}

def git_blob(b: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()

def checked_sources(root: Path) -> dict[str,str]:
    out={}
    for entry,(sha,blob) in SOURCE.items():
        b=(root/'sources'/f'{entry}.x4').read_bytes()
        assert hashlib.sha256(b).hexdigest()==sha, f'Immutable source SHA: {entry}'
        assert git_blob(b)==blob, f'Immutable source Git blob: {entry}'
        assert b.startswith(b'ENTRY') and b.rstrip().endswith(f'ENDENTRY'.encode()+b' '*0+b'             '+str({'C0122':5,'A1256':3,'M0011':3,'M0826':3}[entry]).encode()), f'End EXFOR: {entry}'
        out[entry]=b.decode('utf-8')
    return out

def blocks(txt: str) -> dict[str,list[str]]:
    out={}; key=None
    for line in txt.splitlines():
        if line.startswith('SUBENT '):
            key=line.split()[1];out[key]=[]
        if key:out[key].append(line)
        if line.startswith('ENDSUBENT'):key=None
    return out

def get_data(block: list[str], ncol: int, expected_n: int) -> list[list[Decimal]]:
    j=next(i for i,l in enumerate(block) if l.startswith('DATA '))
    hdr=block[j].split(); assert len(hdr)>=3 and int(hdr[1])==ncol and int(hdr[2])==expected_n
    # Two lines (labels and units) precede actual DATA rows. Each kept row is source exact.
    units=block[j+2]
    assert len(block)>=j+3+expected_n
    numeric=block[j+3:j+3+expected_n]
    values=[]
    for line in numeric:
        tokens=line.split()
        assert len(tokens)==ncol,(len(tokens),line)
        values.append([Decimal(z) for z in tokens])
    assert block[j+3+expected_n].startswith('ENDDATA')
    return values

def energies(td: Decimal) -> dict[str,str]:
    # Invariant s for incident deuteron kinetic Td on stationary D target.
    s=(2*M_D)**2+2*M_D*td
    q=((s/Decimal(4)-M_D**2)).sqrt()
    sq=s.sqrt()
    km=(s-M_ALPHA**2)/(2*sq) # photon momentum energy in capture CM (MeV)
    eg=(s-M_ALPHA**2)/(2*M_ALPHA) # gamma energy in stationary alpha rest (MeV)
    return dict(incident_D_lab_MeV=str(td),s_MeV2=str(s),equivalent_Egamma_He_rest_MeV=str(eg),capture_CM_D_momentum_MeV_over_c=str(q),capture_CM_photon_momentum_MeV_over_c=str(km),phase_space_q2_over_k2=str(q*q/(km*km)))

def records(root: Path):
    raw=checked_sources(root)
    rows=[]
    for entry in ('C0122','A1256'):
        ss=blocks(raw[entry]); expected=[k for k in REGISTRY if k.startswith(entry)]
        for sub in expected:
            kind,unit,common,ncol,nrows=REGISTRY[sub]
            b=ss[sub]
            data=get_data(b,ncol,nrows)
            j=next(i for i,l in enumerate(b) if l.startswith('DATA '))
            units=b[j+2]
            assert (unit in units),f'Unexpected EXFOR units {sub}: {units}'
            assert any('REACTION' in l for l in b[:j]),sub
            for idx,d in enumerate(data,1):
                if sub=='C0122004':td,angle,*v=d
                else:td=Decimal(str(common));angle=d[0];v=d[1:]
                assert td>0 and Decimal('0')<angle<Decimal('180')
                item={
                    'EXFOR_entry':entry, 'EXFOR_subentry':sub, 'original_row_index':idx,
                    'reaction_direction':'D + D -> He4 + gamma',
                    'observable_source_type':kind, 'source_data_unit':unit,
                    'incident_D_lab_MeV':str(td), 'source_CM_angle_deg':str(angle),
                    'original_data_tokens':[str(x) for x in d],
                    'mapped_Egamma_He_rest_MeV':energies(td)['equivalent_Egamma_He_rest_MeV'],
                    'source_is_measured':True, 'mapped_Egamma_is_derived':True,
                    'source_absolute_breakup_sigma':False, 'source_absolute_capture_sigma':False,
                    'source_measured_capture_partial_DA':sub=='A1256002',
                }
                if kind=='capture_REL_DA':
                    item.update(value=str(v[0]),reported_uncertainty=str(v[1]),source_norm='REL only',component='REL_DA')
                elif kind=='capture_PAR_DA':
                    item.update(value=str(v[0]),reported_uncertainty=str(v[1]),source_norm='PAR,DA partial capture; not unpolarized total',component='PAR_DA',value_nb_per_sr=str(v[0]*Decimal(10)**6),err_nb_per_sr=str(v[1]*Decimal(10)**6))
                elif kind=='capture_TAP_polarization':
                    item.update(value=str(v[0]),reported_uncertainty=str(v[1]),component='20/PAR,TAP',source_norm='polarized tensor observable')
                else:
                    assert len(v)==4
                    item.update(value=str(v[0]),reported_uncertainty=str(v[1]),value_component2=str(v[2]),reported_uncertainty_component2=str(v[3]),component='EXFOR REACTION pointers 1,2',source_norm='analyzing powers (pointer 1 and 2), not cross sections')
                rows.append(item)
    assert len(rows)==41 and {k:sum(r['EXFOR_subentry']==k for r in rows) for k in REGISTRY}=={k:v[-1] for k,v in REGISTRY.items()}
    return rows

def symmetry_witnesses(rows):
    result=[]
    for sub in ('C0122002','C0122003'):
        rs=[x for x in rows if x['EXFOR_subentry']==sub]
        assert len(rs)%2==0
        for j in range(len(rs)//2):
            f,b=rs[j],rs[-j-1];a=Decimal(f['source_CM_angle_deg']);c=Decimal(b['source_CM_angle_deg'])
            df=Decimal(f['value']);db=Decimal(b['value']);u=Decimal(f['reported_uncertainty']);v=Decimal(b['reported_uncertainty'])
            assert abs((a+c)-180) <= Decimal('.5')
            contrast=(df-db)/(df+db)
            # no assertion pairs are statistically independent: exact mirrored values likely source-symmetrized.
            result.append({'energy_lab_MeV':f['incident_D_lab_MeV'],'CM_theta_left_deg':str(a),'CM_theta_right_deg':str(c),'angle_sum_deg':str(a+c),'REL_left':str(df),'REL_right':str(db),'odd_contrast_fraction':str(contrast),'source_unc_left':str(u),'source_unc_right':str(v),'uncertainties_correlated_unknown':True,'mirror_rows_independent_measurements':'NOT_ESTABLISHED'})
    return result

def near_ninety_suppression(rows):
    """Two measured relative-DA within-energy shape ratios; never absolute sigma."""
    out=[]
    for sub,shoulder,near90 in [('C0122002','50.8','85.0'),('C0122003','42.2','90.6')]:
        sub_rows=[r for r in rows if r['EXFOR_subentry']==sub]
        high=next(r for r in sub_rows if Decimal(r['source_CM_angle_deg'])==Decimal(shoulder))
        low=next(r for r in sub_rows if Decimal(r['source_CM_angle_deg'])==Decimal(near90))
        h=Decimal(high['value']);lo=Decimal(low['value']);dh=Decimal(high['reported_uncertainty']);dl=Decimal(low['reported_uncertainty'])
        assert h>dh>0 and lo>dl>0
        out.append({'EXFOR_subentry':sub,'capture_D_lab_MeV':high['incident_D_lab_MeV'],
                    'source_near90_theta_deg':near90,'source_shoulder_theta_deg':shoulder,
                    'measured_relative_DA_near90':str(lo),'measured_relative_DA_shoulder':str(h),
                    'dimensionless_near90_to_shoulder':str(lo/h),
                    'source_cartesian_1sigma_box_lower':str((lo-dl)/(h+dh)),
                    'source_cartesian_1sigma_box_upper':str((lo+dl)/(h-dh)),
                    'claimed_joint_confidence_interval':False,
                    'original_measured_rows_not_independent_of_mirrors':True})
    return out

def lowE_forward_map(raw):
    mb=blocks(raw['M0011'])['M0011002']
    vals=get_data(mb,3,14)
    energies_meas=[p[0] for p in vals]
    assert energies_meas==[Decimal(x) for x in ('26','28','30','32','34','36','38','40','42','44','47.5','52.5','57.5','65')]
    mb2=blocks(raw['M0826'])['M0826002']
    bins=get_data(mb2,4,4)
    witness=[]
    for td in [Decimal('9.7'),Decimal('20'),Decimal('30'),Decimal('50')]:
        en=Decimal(energies(td)['equivalent_Egamma_He_rest_MeV'])
        left=max([v for v in energies_meas if v<=en],default=None)
        right=min([v for v in energies_meas if v>=en],default=None)
        inside=[{'Emin':str(b[0]),'Emax':str(b[1]),'source_value_microbarn':str(b[2]),'ERRS_microbarn':str(b[3])} for b in bins if b[0]<=en<=b[1]]
        witness.append({'inverse_lab_D_energy_MeV':str(td),'equivalent_photon_E_MeV':str(en),
           'M0011002_bracketing_measured_SIG_energies_MeV':[str(left) if left is not None else None,str(right) if right is not None else None],
           'M0826002_reported_original_SIG_bins_containing_energy':inside,
           'comparison_scope':'ONLY energies crosswalk, no interpolation of cross-section or replacing relative/polarized observables'})
    return witness

def write_result(root:Path):
    data=records(root);raw=checked_sources(root)
    sym=symmetry_witnesses(data)
    near90=near_ninety_suppression(data)
    cross=lowE_forward_map(raw)
    es=[energies(Decimal(x)) for x in ('9.7','20','30','50')]
    counts={sub:sum(x['EXFOR_subentry']==sub for x in data) for sub in REGISTRY}
    meta={'schema':'HE_DD_EXFOR_INVERSE_SOURCE_NATIVE_41_V1','source_snapshot':'IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871',
       'original_source_records':41,'counts_by_subentry':counts,'C0122_original_rows':29,'A1256_original_rows':12,
       'source_genuine_absolute_unpolarized_dd_cross_sections':0,
       'source_partial_capture_DA_rows':6,'source_relative_capture_DA_rows':14,
       'source_polarized_observable_rows':21,
       'new_independent_experiment_count':'not derivable from rows',
       'assertions':{'original_measured_rows':True,'inverted_photon_energy_is_kinematics_not_new_experiment':True,
           'photo_disintegration_absolute_sigma':None,'event_rate':None,'heat_rate':None,'L4':False,'production':'HOLD'},
       'source_sha256':{k:SOURCE[k][0] for k in SOURCE},'original_records':data,
       'inverse_energy_map':es,'mirror_relative_DA_pairs':sym,'measured_near90_suppression':near90,'forward_lowE_energy_coverage_map':cross}
    out=root/'results';out.mkdir(exist_ok=True)
    (out/'INVERSE_DD_EXFOR_REAL_MEASUREMENTS_41.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    with (out/'INVERSE_DD_EXFOR_REAL_MEASUREMENTS_41.csv').open('w',newline='') as f:
        keys=['EXFOR_entry','EXFOR_subentry','original_row_index','observable_source_type','incident_D_lab_MeV','source_CM_angle_deg','source_data_unit','value','reported_uncertainty','value_component2','reported_uncertainty_component2','value_nb_per_sr','err_nb_per_sr','mapped_Egamma_He_rest_MeV','source_norm']
        wr=csv.DictWriter(f,keys,lineterminator='\n',extrasaction='ignore');wr.writeheader();wr.writerows(data)
    (out/'SOURCE_ENERGY_CROSSWALK.json').write_text(json.dumps({'equivalent_reaction_energy':es,'original_exfor_forward_lowE_crosswalk':cross,'capture_REL_mirror_pairs':sym,'source_near90_suppression':near90},indent=2)+'\n')
    return meta

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('.'));args=ap.parse_args()
    o=write_result(args.root)
    print(json.dumps({'rows':len(o['original_records']),'types':o['counts_by_subentry'],'Egamma_MeV':{i['incident_D_lab_MeV']:i['equivalent_Egamma_He_rest_MeV'] for i in o['inverse_energy_map']},'source_sigma_abs_photo':None,'production':'HOLD'},indent=2))
