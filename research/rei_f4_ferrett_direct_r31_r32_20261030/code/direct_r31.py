#!/usr/bin/env python3
"""Ferrett 1987 *direct R31 and n3/n2 measured ratios* × original BASS193.

Scientific scope: source-owned 193-epoch saved chemistry + Li I K-shell event rates;
publication-source direct R31 (Table II) and R32 (Table III) in 80–92.5 eV.
This code intentionally does not consume the model-assisted Table IV sigma_3S,
its extrapolated R_p above 80 eV, or any photon bins above 92.5 eV.

Every branching result is a CONDITIONAL cross-owner reweighting of the native
BASS photoevent rate, not an empirical absolute event rate, radiation field or
chemical/thermal solution. No new IVPs. Exact PDF and parent ZIP SHA enforced.
"""
from __future__ import annotations
import csv, hashlib, io, json, math, pathlib, zipfile
from collections import defaultdict
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
PARENT_PATH = ROOT/'source/PR289_full_source.zip'
PDF_PATH = ROOT/'source/Ferrett1987_LBL22068_user_source.pdf'
PARENT_SHA='f5fa78b9087a60051bb7161d69ada6019f42cfa093674a2fc07c7ed9cc7cdd4f'
PDF_SHA='7fbabb1fe8c77a2fb561c7900e198f40f4c16125dd12ac3d08505b997a93b6a9'
ORIGINAL_OWNER='cc602e209e7deeb511ab2a1f3b2268d55206c43c'
SOURCE_DOI='10.1103/PhysRevA.36.3172'
NESTED_PREFIX='REI_F4_FERRETT1987_BASS193_20261030/'

# User-supplied PDF, manually visually verified: PDF page 35 (printed -29-) Table II
# and page 36 (printed -30-) Table III. Parentheses are last-digit statistical
# uncertainties, NOT a full covariance matrix nor proof of independent Gaussian errors.
R31=np.array([
    [80.0,1.62,.05], [82.5,1.71,.05], [85.,1.66,.05],
    [87.,1.59,.03],[87.5,1.80,.04],[90.,1.71,.05],[92.5,1.56,.04],
],dtype=float)
R32=np.array([
    [80.0,.172,.010],[82.5,.187,.008],[85.,.187,.005],
    [87.,.209,.005],[87.5,.207,.007],[90.,.209,.008],[92.5,.234,.008],
],dtype=float)
assert np.array_equal(R31[:,0],R32[:,0])

# Literal Ferrett PDF p.34, Table I, binding thresholds in eV for neutral Li I:
# 1s2s(3S) 64.41; 1s2s(1S) 66.15; 1s2p(3P) 66.67;
# 1s2p(1P) 67.61; 1s3l states 74.17..75.04.
# These are HISTORICAL printed values, not substituted for modern NIST corrections.
CHI_TRIPLET=64.41
CHI_N2_REST_MIN=66.15
CHI_N2_REST_MAX=67.61
CHI_N3_MIN=74.17
CHI_N3_MAX=75.04
E_M1_NIST=59.02072367315768
E_2E1_NIST=60.922559447552


def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()


def read_frozen_sources():
    if sha(PARENT_PATH.read_bytes())!=PARENT_SHA:
        raise ValueError('PARENT_PR289_IMMUTABLE_SOURCE_SHA_MISMATCH')
    if sha(PDF_PATH.read_bytes())!=PDF_SHA:
        raise ValueError('ORIGINAL_FERRETT_PDF_BYTE_IDENTITY_MISMATCH')
    with zipfile.ZipFile(PARENT_PATH) as archive:
        if archive.testzip() is not None:raise ValueError('PARENT_CRC_INVALID')
        events=list(csv.DictReader(io.StringIO(archive.read(NESTED_PREFIX+'results/FERRETT_MEASURED_BASS_EVENT_1544.csv').decode())))
        epochs=list(csv.DictReader(io.StringIO(archive.read(NESTED_PREFIX+'results/FERRETT_BASS_EPOCH_193.csv').decode())))
        old=json.loads(archive.read(NESTED_PREFIX+'results/RESULTS.json'))
    if len(events)!=1544 or len(epochs)!=193 or old['original_li1s_source_rows']!=8492:
        raise ValueError('ORIGINAL_BASS_ARCHIVE_SHAPE')
    if old['source_owner']!='cosmosapjw-quantum/bass@'+ORIGINAL_OWNER:raise ValueError('SOURCE_OWNER')
    return events,epochs,old


def measured_ratios(energy:float):
    """Directly observed R31 and R32 with endpoint statistical rectangles.

    A linear interpolation between measured lab energies is an EXPLICIT modeling
    step; its interpolation error is not included in quoted statistical ranges.
    R31 = sigma(3S)/(sigma(1S)+sigma(1P)+sigma(3P));
    R32 = sigma(n3)/sigma(n2).
    """
    if not 80.<=energy<=92.5:raise ValueError('EXPERIMENT_DIRECT_R31_SUPPORT_ONLY_80_92_5_EV')
    r=float(np.interp(energy,R31[:,0],R31[:,1]))
    dr=float(np.interp(energy,R31[:,0],R31[:,2]))
    t=float(np.interp(energy,R32[:,0],R32[:,1]))
    dt=float(np.interp(energy,R32[:,0],R32[:,2]))
    if r-dr<=0 or t-dt<0:raise ValueError('NONPHYSICAL_MEASURED_ERROR_INTERVAL')
    return r,dr,t,dt


def branch(r,t):
    f3=r/((1+r)*(1+t))
    frest=1/((1+r)*(1+t))
    fn3=t/(1+t)
    assert abs((f3+frest+fn3)-1.0)<1.3e-15
    return f3,frest,fn3


def branch_enclosure(e):
    r,dr,t,dt=measured_ratios(e)
    f3,fr,fN=branch(r,t)
    # Mathematical monotonicity independently proved in THEORY_KO.md and Wolfram.
    f3lo=branch(r-dr,t+dt)[0]
    f3hi=branch(r+dr,t-dt)[0]
    frestlo=branch(r+dr,t+dt)[1]
    fresthi=branch(r-dr,t-dt)[1]
    fn3lo=(t-dt)/(1+t-dt)
    fn3hi=(t+dt)/(1+t+dt)
    # Both the unknown n2-rest fine-structure channel and n3 satellites have
    # energy brackets; search all four measured-endpoint rectangles.
    values=[]
    for rv in (r-dr,r+dr):
        for tv in (t-dt,t+dt):
            a,b,c=branch(rv,tv)
            for cRest,cN3 in ((CHI_N2_REST_MIN,CHI_N3_MIN),(CHI_N2_REST_MAX,CHI_N3_MAX)):
                ionization=a*CHI_TRIPLET+b*cRest+c*cN3
                photoelectron=e-ionization
                assert photoelectron>=0 and abs((photoelectron+ionization)-e)<2e-14
                values.append(photoelectron)
    return dict(R31=r,R31_stat=dr,R32=t,R32_stat=dt,
        triplet_fraction=f3,triplet_fraction_min=f3lo,triplet_fraction_max=f3hi,
        n2_rest_fraction=fr,n2_rest_fraction_min=frestlo,n2_rest_fraction_max=fresthi,
        n3_fraction=fN,n3_fraction_min=fn3lo,n3_fraction_max=fn3hi,
        conditional_photoelectron_eV_min=min(values),conditional_photoelectron_eV_max=max(values),
        triplet_photoelectron_eV=e-CHI_TRIPLET,
        max_possible_pure_singlet_fraction=fresthi,
        nominal_singlet_max_fraction=fr)


def simpson_weights(x):
    x=np.asarray(x,float)
    if len(x)!=193:raise ValueError('SOURCE_EPOCHS_NOT_193')
    d=np.diff(x)
    if max(abs(d-d[0]))>5e-12:raise ValueError('SOURCE_TIME_NONUNIFORM')
    w=np.ones(len(x),dtype=float);w[1:-1:2]=4;w[2:-1:2]=2
    return w*d[0]/3


def generate():
    original,epochs,parent=read_frozen_sources()
    x=np.log(21./(1+np.array([float(z['z']) for z in epochs])))
    H=np.array([float(z['H_s']) for z in epochs]);assert np.all(H>0)
    weights=simpson_weights(x)
    selected=[row for row in original if 80<=float(row['photon_eV'])<=92.5]
    if len(selected)!=193*2*3 or {int(r['bin_index']) for r in selected}!={54,55,56}:
        raise ValueError('MEASURED_BIN_UNEXPECTED')
    results=[]
    cols=['original_K_rate','triplet_rate','triplet_rate_lo','triplet_rate_hi',
          'rest_rate','rest_upper_rate','n3_rate','photoelectron_eV_rate_lo','photoelectron_eV_rate_hi',
          'M1_potential_eV_rate','twoE1_possible_eV_rate_upper']
    aggregates={k:0.0 for k in ['source_events','triplet','triplet_min','triplet_max',
        'n2_rest','n2_rest_upper','n3','photoelectron_eV_min','photoelectron_eV_max',
        'M1_potential_eV','twoE1_possible_eV_upper']}
    by_epoch=defaultdict(lambda:{k:0.0 for k in cols})
    for row in selected:
        epoch=int(row['epoch']);E=float(row['photon_eV']);q=float(row['native_K_events_per_baryon_s'])
        if q<0:raise ValueError('NEGATIVE_NATIVE_PHOTO_RATE')
        b=branch_enclosure(E)
        r={
         'epoch':epoch,'z':float(row['z']),'isotope':row['isotope'],'bin_index':int(row['bin_index']),
         'photon_eV':E,'native_K_events_per_baryon_s':q,
         **b,
         'conditional_triplet_rate':q*b['triplet_fraction'],
         'conditional_triplet_rate_min':q*b['triplet_fraction_min'],
         'conditional_triplet_rate_max':q*b['triplet_fraction_max'],
         'conditional_singlet_2E1_rate_lower':0.0,
         'conditional_singlet_2E1_rate_upper':q*b['max_possible_pure_singlet_fraction'],
         'conditional_n3_rate':q*b['n3_fraction'],
         'conditional_photoelectron_eV_rate_min':q*b['conditional_photoelectron_eV_min'],
         'conditional_photoelectron_eV_rate_max':q*b['conditional_photoelectron_eV_max'],
         'conditional_M1_radiation_eV_rate_if_vacuum_decay':q*b['triplet_fraction']*E_M1_NIST,
         'conditional_2E1_radiation_eV_rate_upper_if_vacuum_decay':q*b['max_possible_pure_singlet_fraction']*E_2E1_NIST,
        }
        results.append(r)
        ed=by_epoch[epoch];base={
          'original_K_rate':q,'triplet_rate':r['conditional_triplet_rate'],
          'triplet_rate_lo':r['conditional_triplet_rate_min'],'triplet_rate_hi':r['conditional_triplet_rate_max'],
          'rest_rate':q*b['n2_rest_fraction'],'rest_upper_rate':r['conditional_singlet_2E1_rate_upper'],
          'n3_rate':r['conditional_n3_rate'],
          'photoelectron_eV_rate_lo':r['conditional_photoelectron_eV_rate_min'],
          'photoelectron_eV_rate_hi':r['conditional_photoelectron_eV_rate_max'],
          'M1_potential_eV_rate':r['conditional_M1_radiation_eV_rate_if_vacuum_decay'],
          'twoE1_possible_eV_rate_upper':r['conditional_2E1_radiation_eV_rate_upper_if_vacuum_decay']}
        for k,v in base.items():ed[k]+=v
        w=weights[epoch]/H[epoch]
        for k,s in zip(aggregates,('original_K_rate','triplet_rate','triplet_rate_lo','triplet_rate_hi',
            'rest_rate','rest_upper_rate','n3_rate','photoelectron_eV_rate_lo','photoelectron_eV_rate_hi',
            'M1_potential_eV_rate','twoE1_possible_eV_rate_upper')):aggregates[k]+=w*base[s]
    epoch_records=[]
    for i in range(193):
        a=by_epoch[i]
        if abs(a['original_K_rate']-a['triplet_rate']-a['rest_rate']-a['n3_rate'])>1.2e-13*max(a['original_K_rate'],1e-100):
            raise AssertionError('EVENT_NUMBER_CLOSURE')
        epoch_records.append(dict(epoch=i,z=float(epochs[i]['z']),H_s=float(H[i]),**a))
    result={
        'schema':'REI_F4_FERRETT_R31_R32_DIRECT_OBSERVABLE_V1',
        'measurement_source':'Ferrett et al, Phys Rev A 36 3172 (1987), Tables II/III, user-provided LBL-22068 PDF pages 35/36, Table I page34',
        'DOI':SOURCE_DOI,'source_pdf_sha256':PDF_SHA,
        'parent_source_zip_sha256':PARENT_SHA,'BASS_owner':ORIGINAL_OWNER,
        'rows_science':len(results),'epochs':193,'isotopes':['Li6I','Li7I'],
        'measured_photon_bins':sorted(set(float(z['photon_eV']) for z in results)),
        'measured_energy_window_eV':[80,92.5],
        'assumption':'Original BASS conditional K photo-event rates reweighted by Ferrett ratios; linear interpolation of observed R31 and n3/n2; one-sigma rectangles nonprobabilistic, unknown joint covariance',
        'limits':'True singlet unknown, upper bound only; no 93–99 model-assisted R31/Rp, no new IVP, no chemistry/heat or actual radiation',
        'table_IV_model_assisted_not_source_of_ratios':True,
        'absolute_calibration_20pct_not_reported_as_fraction_statistical_sigma':True,
        'original_parent_direct_inferred_rate_for_comparison_events':parent['direct_R31_measured_regime_80_to_92_5_eV']['triplet_M1_conditional_events'],
        'source_integrals_per_original_baryon':aggregates,
        'new_ivps':0,
        'original_DAG':{'working':'33/88','central':'28/88','F4':'4/7','physical_delta':0},
        'source_owner_common_REI17_not_established':True,'F4':'PARTIAL','L4_ready':False,'production':'HOLD'
    }
    if not 0<=aggregates['triplet_min']<=aggregates['triplet']<=aggregates['triplet_max']<=aggregates['source_events']:
        raise AssertionError('INTEGRAL_TRIPLET_INTERVAL')
    if abs(aggregates['triplet']+aggregates['n2_rest']+aggregates['n3']-aggregates['source_events'])>1e-13*aggregates['source_events']:
        raise AssertionError('INTEGRAL_TOTAL_CLOSURE')
    return results,epoch_records,result


def write_csv(path,rows):
    with pathlib.Path(path).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    rows,epochs,summary=generate();out=ROOT/'results';out.mkdir(exist_ok=True)
    write_csv(out/'FERRETT_DIRECT_R31_R32_BASS_EVENT_1158.csv',rows)
    write_csv(out/'FERRETT_DIRECT_R31_R32_EPOCH_193.csv',epochs)
    calib=[]
    for E in R31[:,0]:
        b=branch_enclosure(float(E))
        calib.append(dict(E_eV=E,PDF_page_R31=35,PDF_page_R32=36,**b))
    write_csv(out/'FERRETT_TABLE_II_III_DIRECT_7.csv',calib)
    (out/'RESULT.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
