#!/usr/bin/env python3
"""Record provider rows only; no REC-owned radiative/collider evaluator."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

B = Path(__file__).resolve().parent
R = B / 'raw'
HD = Path('/workspace/scratch/d855c1e0c0ed/orchestration_20261025/release/research/orchestration_expansion_20261025/authority/molecular/lamda_hd_20261025.dat')

def sha(b): return hashlib.sha256(b).hexdigest()
def out(name,value): (B/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def main():
    b=(R/'LiH.txt').read_bytes()
    points=[]
    for n,line in enumerate(b.splitlines(keepends=True),1):
        if line.startswith(b'#') or not line.strip(): continue
        c=line.decode().split()
        assert len(c)==4
        points.append({'source_line':n,'raw_line_utf8':line.decode(),'raw_row_sha256':sha(line),
                       'wavelength_nm':c[0],'photoabsorption_cm2':c[1],
                       'photodissociation_cm2':c[2],'photoionisation_cm2':c[3]})
    props=(R/'cross_section_properties.csv').read_bytes()
    header=next(l for l in props.decode().splitlines() if l.startswith('species,'))
    selected=next((n,l) for n,l in enumerate(props.splitlines(keepends=True),1) if l.startswith(b'LiH '))
    fields=[c.strip() for c in next(csv.reader([header]))]
    values=[c.strip() for c in next(csv.reader([selected[1].decode()]))]
    summary={k:v for k,v in zip(fields,values) if k}
    out('lih_photoprocess_provider.json',{
        'provider':'Leiden_photodissociation',
        'source_url':'https://home.strw.leidenuniv.nl/~ewine/photo/data/photo_data/cross_sections/LiH/LiH.txt',
        'source_sha256':sha(b),'source_bytes':len(b),'source_header':[l for l in b.decode().splitlines() if l.startswith('#')],
        'source_reference':'Kirby & Dalgarno1978 per file header; source bibliography key kirby1978',
        'provider_channel':'LiH + photon -> Li + H',
        'channel_basis':'summary source pd_products identifies dominant long-wavelength-threshold fragments',
        'isotope':{'Li':None,'H':None,'qualification':'NOT_SPECIFIED_IN_PROVIDER_FILE; no6Li/7Li orH/D/T substitution'},
        'charge':0,'state':None,'state_status':'NOT_SPECIFIED_IN_PROVIDER_FILE',
        'Q_value':None,'Q_status':'NOT_SUPPLIED; threshold wavelength is not adopted as thermochemicalQ',
        'branch_fraction':None,'branch_status':'DOMINANT_THRESHOLD_PRODUCTS_ONLY; wavelength-dependent branching unresolved',
        'rate_admission':False,'cross_section_source_ingested':True,
        'source_support_nm':[points[0]['wavelength_nm'],points[-1]['wavelength_nm']],
        'sample_count':len(points),'points':points,
        'summary_source':{'file':'cross_section_properties.csv','sha256':sha(props),'source_line':selected[0],
                          'raw_line_utf8':selected[1].decode(),'raw_row_sha256':sha(selected[1]),'fields':summary},
        'uncertainty':{'stellar':'A:within30%','Lyalpha':'C:within factor10','cosmic_ray_UV':'B:within factor2',
                       'covariance':None,'qualification':'PROVIDER_REGIME_CATEGORIES; no per-sample covariance'},
        'source_discrepancy':{'summary_pd_threshold_nm':summary['pd_threshold'],
                              'actual_sample_max_nm':points[-1]['wavelength_nm'],
                              'disposition':'Keep both; no extension of table to the summary threshold'},
        'source_format':{'wavelength':'nm','cross_sections':'cm^2',
                         'line_representation':'Gaussian1.0nmFWHM per header; do not replace with natural linewidth'},
        'interpolation_and_radiation_integral':'NOT_IMPLEMENTED_IN_THIS_EXTRACTION',
        'owner':{'stoichiometry':'WU088_HH','spectral_cross_section':'rec_bianchi','nonthermal_incident_spectrum':'bass_cr'}
    })
    shutil.copyfile(HD,R/'lamda_hd_20261025.dat')
    hb=HD.read_bytes(); rows=[(n,l) for n,l in enumerate(hb.decode().splitlines(),1) if l.strip() and not l.startswith('!')]
    i=0
    def take():
        nonlocal i
        x=rows[i];i+=1;return x
    title=take(); mass=take(); nlevels=int(take()[1]); levels=[]
    for _ in range(nlevels):
        n,l=take(); c=l.split();levels.append({'source_line':n,'raw_line_utf8':l,'level_id':int(c[0]),'energy_cm-1':c[1],'degeneracy':c[2],'J':c[3],'v':None})
    nlines=int(take()[1]); lines=[]
    for _ in range(nlines):
        n,l=take();c=l.split();lines.append({'source_line':n,'raw_line_utf8':l,'transition_id':int(c[0]),'upper_id':int(c[1]),'lower_id':int(c[2]),'A_s-1':c[3],'nu_GHz':c[4],'Eu_over_k_K':c[5]})
    npartners=int(take()[1]); coll=[]
    for _ in range(npartners):
        n,desc=take(); nr=int(take()[1]);nt=int(take()[1]);tn,tl=take();ts=tl.split();assert len(ts)==nt
        for _ in range(nr):
            n,l=take();c=l.split();assert len(c[3:])==nt
            coll.append({'source_line':n,'raw_line_utf8':l,'collider_provider_description':desc,'collider_id':int(desc.split()[0]),'transition_id':int(c[0]),'upper_id':int(c[1]),'lower_id':int(c[2]),'T_nodes_K':ts,'q_cm3_s':c[3:]})
    assert i==len(rows)
    out('hd_provider_rows.json',{
        'provider':'LAMDA_HD','source_url':'https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat',
        'source_sha256':sha(hb),'source_bytes':len(hb),'source_title':title[1],
        'source_reuse':'Exact pinned central authority fixture; no completed scalar calculation rerun',
        'species':'HD','composition':[{'Z':1,'A':1,'count':1},{'Z':1,'A':2,'count':1}],
        'charge':0,'isomer_status':'ground nuclei selected from sourceHD label; no nuclear isomer coverage',
        'electronic_state':None,'vibrational_state':None,
        'state_qualification':'Use suppliedJ only; central authority retains webpagev1 discrepancy',
        'levels':levels,'radiative_lines':lines,'collisions':coll,
        'uncertainty':{'level_covariance':None,'line_uncertainty':None,'collision_covariance':None,'qualification':'NOT_SUPPLIED_IN_PINNED_FILE'},
        'coverage':{'levels':nlevels,'lines':nlines,'collider_species':npartners,'collision_pairs':len(coll),'temperature_points_per_pair':3},
        'chemical_formation_destruction':False,'rate_admission':False,
        'owner':'rec_bianchi spectral provider; WU088_HH consumes isotope/state identities',
        'implementation':'RAW_EXTRACTION_ONLY; no duplicate REC adapter or physical evaluation'
    })
    print(json.dumps({'LiH_sample_count':len(points),'LiH_support_nm':[points[0]['wavelength_nm'],points[-1]['wavelength_nm']],
                      'HD':{'levels':len(levels),'lines':len(lines),'collision_pairs':len(coll)}}))

if __name__=='__main__':main()
