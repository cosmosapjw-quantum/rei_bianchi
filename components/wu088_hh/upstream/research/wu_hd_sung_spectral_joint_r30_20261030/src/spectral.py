"""R30: original SQM fixed-bath 5-state chemistry + measured HD line photon observables.

New source: REC164 transcription of Sung et al. (2023 print, online 2022) HD
R(0)-R(3) fitted line centers, not full raw lab covariance or cosmic observations.
Upstream R29 is an immutable nested ZIP. All original source claims are rechecked.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import sys
import zipfile
from pathlib import Path
from typing import Any
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
R29_SHA='65ed097acb02f8eb91ff6518c26c8ad61e721e3fadd9b904aa2157e3508cb0ea'
R29_NAME='WU_R29_SOURCE_ORIGINAL_20261030.zip'
SUNG_SOURCE='REC164_SUNG2022_PRIMARY_TABLE4_LOCK.json'
SUNG_SOURCE_SHA = '50d4e6af5cc63afee44177cb0f46838f654f9ff127efe140014ade1e0c2d854f'  # immutable current R30 transcription SHA256
H=6.62607015e-34
C=299792458.
KB=1.380649e-23
CM_TO_J=100*H*C
SOURCE_LINE_VALUES=(89.22792,177.84141,265.24055,350.85401)

class SourceIntegrityError(ValueError): pass

def sha_file(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_r29():
    p=ROOT/'archive'/R29_NAME
    if not p.exists() or sha_file(p)!=R29_SHA:
        raise SourceIntegrityError('R29 parent original ZIP SHA mismatch or missing')
    dst=ROOT/'_parent_restored'
    if not (dst/'src'/'network.py').exists():
        dst.mkdir(exist_ok=True)
        with zipfile.ZipFile(p) as z:
            if z.testzip() is not None: raise SourceIntegrityError('R29 ZIP CRC')
            for member in z.namelist():
                if member.startswith('/') or '..' in Path(member).parts:
                    raise SourceIntegrityError('R29 ZIP unsafe path')
            z.extractall(dst)
    # Need semantic-source safety even if _parent_restored is pre-existing:
    ref_file=dst/'src'/'network.py'
    with zipfile.ZipFile(p) as z:
        if ref_file.read_bytes()!=z.read('src/network.py'):
            raise SourceIntegrityError('R29 extracted network module was changed')
        for n in ['GL2022_700_SOURCE.json','GL2022_1560_INELASTIC_SOURCE_TOKENS.csv','REC161_LAMDA_A_TRANSCRIPTION_REF.json','REC162_CDMS2011V2_PRINTED_LEVELS.json']:
            if (dst/'sources'/n).read_bytes()!=z.read('sources/'+n):
                raise SourceIntegrityError('R29 original source changed: '+n)
    spec=importlib.util.spec_from_file_location('wu_r29_network',ref_file)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

def get_sung():
    p=ROOT/'sources'/SUNG_SOURCE
    if SUNG_SOURCE_SHA and sha_file(p)!=SUNG_SOURCE_SHA: raise SourceIntegrityError('REC164 source transcription modified')
    x=json.loads(p.read_text())
    if x['source_git_blob']!='23626dd9a77aa4e6214f6f9c792ea18270b3940c' or x['reference_doi']!='10.1016/j.jqsrt.2022.108412':
        raise SourceIntegrityError('Sung reference changed')
    lines=x['lines']
    if len(lines)!=4 or tuple(float(t['nu_cm_minus1']) for t in lines)!=SOURCE_LINE_VALUES:
        raise SourceIntegrityError('visible four measured line centers changed')
    for j,line in enumerate(lines,1):
        if (int(line['upper_J']),int(line['lower_J']))!=(j,j-1):raise SourceIntegrityError('line quantum number map')
    return x

def get_grid(source_grid):
    lines=get_sung()['lines']
    en={0:0.}
    for j,l in enumerate(lines,1):en[j]=en[j-1]+float(l['nu_cm_minus1'])
    # New input only spectroscopic energy ladder. All chemistry, collisions, radiative A unchanged.
    g=type(source_grid)(source_grid.q,source_grid.down,source_grid.A,en,dict(source_grid.source_meta))
    return g

def metrics_one(parent,grid_orig,grid_new,T,policy,ratio,start_J):
    nH=parent.reference_density(grid_orig,T,policy)*ratio
    G,GC,Gfirst,kchem=parent.assemble(grid_new,T,policy,nH)
    Gorig,*_=parent.assemble(grid_orig,T,policy,nH)
    e=np.zeros(5);e[start_J]=1.
    m=np.linalg.solve(-G,e)
    m0=np.linalg.solve(-Gfirst,e)
    M=np.column_stack([nH*parent.reaction_vector(grid_new,T,j,policy) for j in range(5)]) # (10, 5)
    all_products=M@m
    no_phot_products=M@m0
    phot_products=all_products-no_phot_products
    ph1=np.array([grid_new.A[j]*m0[j] for j in range(1,5)])
    phmean=np.array([grid_new.A[j]*m[j] for j in range(1,5)])
    centers=np.array(SOURCE_LINE_VALUES)
    energies=CM_TO_J*centers
    radiated_j=float(energies@phmean)
    m_old=np.linalg.solve(-Gorig,e)
    before_old=np.array([grid_orig.A[j]*m_old[j] for j in range(1,5)])
    baseline=parent.run_case(grid_orig,T,policy,ratio,start_J)
    # all returned counts are per ONE initially present HD molecule
    smalltol=1.e-9
    if (np.min(m)<0 or np.min(m0)<0 or
        np.max(np.abs(all_products-(no_phot_products+phot_products)))>2.e-14 or
        np.min(phot_products)<-2e-12 or
        abs(float(all_products.sum())-1)>smalltol or
        abs(float(no_phot_products.sum()+ph1.sum())-1)>smalltol or
        abs(float(phmean.sum())-float(parent.run_case(grid_new,T,policy,ratio,start_J)['expected_photons_before_exchange']))>1e-10):
        raise AssertionError('transient photon/reaction probability or science invariant failed')
    if np.max(np.abs(phmean-before_old))>100:raise AssertionError('spectroscopy sensitivity unbounded')
    key={'T_K':T,'policy':policy,'n_over_ncrit_J2':ratio,'initial_J':start_J,'nHplus_cm3':float(nH)}
    metrics={**key,
       'photons_at_least_one_probability':float(ph1.sum()),
       'no_photon_exchange_probability':float(no_phot_products.sum()),
       'expected_photons':float(phmean.sum()),
       'integrated_photon_energy_J_per_initial_HD':radiated_j,
       'equivalent_integrated_photon_energy_eV_per_initial_HD':radiated_j/1.602176634e-19,
       'lifetime_to_restricted_exchange_s':float(m.sum()),
       'energy_per_event_average_power_W_per_initial_HD':radiated_j/float(m.sum()),
       'Sung_vs_CDMS2011_delta_photons':float(phmean.sum()-baseline['expected_photons_before_exchange']),
       'Sung_vs_CDMS2011_delta_any_photon':float(ph1.sum()-baseline['probability_one_or_more_photons_before_exchange']),
       'source_claim':'SUNG2022_FIT_LINE_SPECTRAL_CENTERS_ON_R29_SQM_TRACER',
       'is_full_cosmological_cooling':False}
    line_rows=[]
    for j in range(1,5):
        line_rows.append({**key,'emission_J_upper':j,'emission_J_lower':j-1,
          'fit_line_wavenumber_cm_minus1':float(centers[j-1]),
          'fit_line_photon_frequency_Hz':float(centers[j-1]*100*C),
          'fit_line_wavelength_um':float(10000/centers[j-1]),
          'fit_line_photon_energy_J':float(energies[j-1]),
          'source_Einstein_A_s_minus1':float(grid_new.A[j]),
          'probability_this_is_first_photon':float(ph1[j-1]),
          'expected_photons_this_line':float(phmean[j-1]),
          'integrated_line_radiation_energy_J':float(energies[j-1]*phmean[j-1]),
          'measured_line_fit_only_sigma_cm_minus1':float(get_sung()['lines'][j-1]['fit_only_sigma_cm_minus1'])})
    product_rows=[]
    for h2 in range(10):
        product_rows.append({**key,'H2_final_Jprime':h2,
           'probability_restricted_product_Jprime':float(all_products[h2]),
           'joint_probability_no_photon_and_product':float(no_phot_products[h2]),
           'joint_probability_at_least_one_photon_and_product':float(phot_products[h2]),
           'probability_product_given_at_least_one_photon':float(phot_products[h2]/ph1.sum())})
    return metrics,line_rows,product_rows

def build_atlas():
    parent=load_r29();old=parent.load_grid();new=get_grid(old)
    rows=[];line_rows=[];product_rows=[]
    for T in parent.TEMPS:
      for policy in parent.POLICIES:
       for ratio in parent.DENSITY_RATIOS:
        for j in parent.LEVELS:
          case,line,product=metrics_one(parent,old,new,T,policy,ratio,j)
          rows.append(case);line_rows.extend(line);product_rows.extend(product)
    assert len(rows)==210 and len(line_rows)==840 and len(product_rows)==2100
    return parent,rows,line_rows,product_rows

def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()),extrasaction='raise');writer.writeheader();writer.writerows(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default=str(ROOT/'results'));o=p.parse_args();dst=Path(o.out);dst.mkdir(parents=True,exist_ok=True)
    par,rows,lines,products=build_atlas()
    write_csv(dst/'R30_PHOTON_ATLAS_840.csv',lines)
    write_csv(dst/'R30_RESTRICTED_H2_JOINT_2100.csv',products)
    write_csv(dst/'R30_CASES_210.csv',rows)
    (dst/'R30_CASES_210.json').write_text(json.dumps({'schema':'wu.r30.sung_spectral_absorbing_markov.v1','rows':rows},indent=2)+'\n')
    example=next(r for r in rows if r['T_K']==105 and r['policy']=='Eq6-7_spin_effective' and r['n_over_ncrit_J2']==1.0 and r['initial_J']==2)
    ex_line=[x for x in lines if all(x[k]==example[k] for k in ['T_K','policy','n_over_ncrit_J2','initial_J'])]
    max_delta=max(abs(row['Sung_vs_CDMS2011_delta_any_photon']) for row in rows)
    summary={'schema':'wu.r30.sung_photon_joint_atlas_summary.v1','original_parent_head':'d0850bd67e20304c566737b7a92bfc45f4849b93','parent_archive_SHA256':R29_SHA,'Sung_git_source_blob':get_sung()['source_git_blob'],
       'cases':len(rows),'line_resolved_rows':len(lines),'joint_H2_photon_product_rows':len(products),
       'source_temperatures':list(par.TEMPS),'Sung_line_centers_cm_minus1':list(SOURCE_LINE_VALUES),
       'example_105K_J2_spin_ncrit':example,'example_four_spectral_line_rows':ex_line,
       'max_absolute_photon_probability_shift_replacing_2011_levels_by_Sung2022_centers':max_delta,
       'central_DAG':{'done':34,'total':49},'auxiliary_R30':{'done':1,'total':1,'claim':'SCOPED_SOURCE_DERIVED_SPECTRAL_BRANCH_ATLAS','canonical_promotions':0},
       'physical_Q':None,'PES_native_threshold':None,'owner_ACK':None,'HH_R10':'OFF','full_A':None,'L4':False,'production':'NOT_ISSUED','distinct_author_R6':'NOT_RUN','distinct_author_C9':'NOT_RUN',
       'EMAA_original_ASCII_bytes_acquired':False,'Sung_raw_paper_PDF_acquired':False,'Sung_lab_covariance_acquired':False,
       'physical_assumption':'Fixed prescribed T,nHp, 5 rotational levels, only source SQM v0 H2 product and H+ HD inelastic plus spontaneous REC161 A; no original EMAA bytes; line centers are 296K measured fit transcription no gas pressure shifts'}
    (dst/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'cases':len(rows),'line_rows':len(lines),'product_rows':len(products),'example':example,'max_delta_any_photon':max_delta},indent=2))
if __name__=='__main__':main()
