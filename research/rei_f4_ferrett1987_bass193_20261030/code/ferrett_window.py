#!/usr/bin/env python3
"""Experimental 1987 Li I K-shell branching on original BASS193 native photon-event rows.

Not a new IVP, nor a claim that the experimental and native K-shell cross sections
are the same source owner. Explicitly retain 1s2s(1S)+1s2p(3P) unresolved.
Use only complete Table IV 80..99eV measurements, never extrapolate.
"""
from __future__ import annotations
import csv, hashlib, io, json, math, pathlib, zipfile
from collections import defaultdict
from dataclasses import dataclass
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'source/PR287_FULL.zip'
SHA_PR287 = 'cb7593462c228278c3bdea79338271a1c1518b1b32632d4806aea6ca1ce683ef'
SHA_PR284 = 'fa3e5f2a5cc0eaaa458372dbd2d926ad6829451a16a04b1bd220b3abb26747c9'
SHA_PR283 = '91c4c9f8cc5daa12f65e41e910b7de6d402096c13a817d88f72c7ac68d52355a'
SHA_PR282 = 'a0f15cab2a283c1cfdf5c2a1fa8d2bc1fe9e232c1754cdaf4625ca0ff65107c0'
SHA_PR280 = 'fd9b8343ed2ea48b6caa9eff8aa5592d34a75fb77cfe223c81af3afbd8a21a91'
SOURCE_OWNER = 'cc602e209e7deeb511ab2a1f3b2268d55206c43c'
SOURCE_DOI = '10.1103/PhysRevA.36.3172'
SOURCE_PREPRINT = 'https://escholarship.org/uc/item/8k72s0qj'
# Ferrett et al. Phys Rev A 36 (1987) 3172, author's LBL-22068 manuscript Table IV.
# Mb = 1e-22 m^2, table is measured 1s electron ejection into Li+ states.
# energies 75, 77.5 omitted because paper did not tabulate n=3 there.
# columns: photon_eV, n2_MB, n3_MB, triplet_1s2s_MB, unresolved_singlet_1s2s_plus_triplet_1s2p_MB
TABLE = np.array([
 [80,1.86,.32,1.15,.63],
 [82.5,1.67,.31,1.05,.54],
 [85,1.58,.30,.99,.53],
 [87,1.45,.30,.89,.51],
 [87.5,1.43,.29,.92,.46],
 [90,1.41,.29,.89,.47],
 [92.5,1.30,.31,.79,.46],
 [93,1.29,.27,.81,.45],
 [95,1.28,.28,.80,.44],
 [97,1.18,.27,.74,.41],
 [99,1.09,.26,.68,.38],
],float)
# Published uncertainties: Table IV parentheses denote statistical errors
# in last displayed digits; total absolute calibration has additional ~20%.
# They are NOT independent perfect measurement of Li+ 1s2s(1S) alone.
SIG3S_STAT_MB = np.array([.07,.07,.07,.05,.06,.06,.04,.09,.09,.08,.08])
SIG_UNRES_STAT_MB = np.array([.05,.04,.04,.03,.04,.04,.03,.06,.06,.05,.05])


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def nested_bytes(z: zipfile.ZipFile, name: str, expected: str) -> bytes:
    result = z.read(name)
    if sha(result) != expected:
        raise ValueError('IMMUTABLE_SOURCE_SHA_' + name)
    return result


def original_rows():
    raw=ARCHIVE.read_bytes()
    if sha(raw)!=SHA_PR287: raise ValueError('PR287_WHOLE_ARCHIVE_SHA_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(raw)) as z287:
        if z287.testzip(): raise ValueError('PR287_ZIP_CRC')
        pr284 = nested_bytes(z287,'REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030/source/PR284_FULL.zip',SHA_PR284)
    with zipfile.ZipFile(io.BytesIO(pr284)) as z284:
        pr283=nested_bytes(z284,'REI_F4_LII_2E1_PAIR_CORRELATED_20261030/source/PR283_FULL.zip',SHA_PR283)
    with zipfile.ZipFile(io.BytesIO(pr283)) as z283:
        pr282=nested_bytes(z283,'REI_F4_LII_2E1_SOURCE_SPECTRAL_ABSORPTION_20261030/source/PR282_FULL.zip',SHA_PR282)
    with zipfile.ZipFile(io.BytesIO(pr282)) as z282:
        pr280=nested_bytes(z282,'REI_F4_LII_M1_FROZEN_ABSORPTION_20261030/source/REI_F4_LI1S_RADIATIVE_PHOTON_20261030_FULL.zip',SHA_PR280)
    with zipfile.ZipFile(io.BytesIO(pr280)) as z280:
        rows=list(csv.DictReader(io.StringIO(z280.read('REI_F4_LI1S_RADIATIVE_PHOTON_20261030/results/LI1S_VACUUM_PHOTON_CAPACITY_8492.csv').decode())))
        epochs=list(csv.DictReader(io.StringIO(z280.read('REI_F4_LI1S_RADIATIVE_PHOTON_20261030/results/LI1S_PHOTON_CAPACITY_EPOCH_193.csv').decode())))
    if len(rows)!=8492 or len(epochs)!=193: raise ValueError('ORIGINAL_SOURCE_SHAPE')
    if {r['isotope'] for r in rows}!={'Li6I','Li7I'}: raise ValueError('ORIGINAL_ISOTOPE_SCOPE')
    if len({(int(r['epoch']),r['isotope'],int(r['bin_index'])) for r in rows})!=8492:
        raise ValueError('ORIGINAL_SOURCE_DUPLICATED_EVENT')
    return rows,epochs


def fractions(e:float):
    if not 80.<=e<=99.:raise ValueError('MEASURED_ENERGY_SUPPORT_ONLY_80_99_EV')
    cols=np.array([np.interp(e,TABLE[:,0],TABLE[:,i]) for i in range(1,5)])
    n2,n3,t,unres=cols
    if not (n2>0 and n3>0 and t>=0 and unres>=0 and t+unres<=n2+1e-12):
        raise AssertionError('MEASURED_CROSS_SECTION_DOMAIN')
    total=n2+n3
    return dict(sigma_n2_Mb=float(n2),sigma_n3_Mb=float(n3),sigma_triplet_Mb=float(t),sigma_singlet_plus_3P_unresolved_Mb=float(unres),
        ratio_triplet_1s2s_to_measured_core=float(t/total),
        ratio_singlet_1s2s_upper_to_measured_core=float(unres/total),
        ratio_n3_satellite_to_measured_core=float(n3/total),
        ratio_other_unresolved_to_measured_core=float((total-t-unres-n3)/total),
        ratio_triplet_to_n2=float(t/n2),
        ratio_singlet_ub_to_n2=float(unres/n2))


def simpson_weights(x):
    x=np.asarray(x,float)
    assert len(x)==193 and len(x)%2==1
    dx=np.diff(x)
    if np.max(abs(dx-dx[0]))>3e-12: raise ValueError('ORIGINAL_LOG_SCALE_UNIFORMITY')
    w=np.ones(len(x));w[1:-1:2]=4;w[2:-1:2]=2
    return w*dx[0]/3


def generate():
    original, epochs=original_rows()
    x=np.array([float(r['x']) for r in epochs]); H=np.array([float(r['H_s']) for r in epochs])
    if np.any(H<=0):raise AssertionError('HUBBLE_SOURCE_DOMAIN')
    if np.max(np.abs((x-np.log(21./(1+np.array([float(r['z']) for r in epochs]))))))>3e-12:
        raise ValueError('CLOCK_SCALE_MISMATCH')
    selected=[r for r in original if 80<=float(r['photon_eV'])<=99]
    # exactly four original photon bins, each of two Li isotopes, all 193 epochs
    assert len(selected)==193*2*4
    assert {int(r['bin_index']) for r in selected}=={54,55,56,57}
    weights=simpson_weights(x)
    results=[]
    by_epoch=defaultdict(lambda:dict(all_native_window_rate=0.,triplet_weighted_rate=0.,singlet_upper_weighted_rate=0.,n3_weighted_rate=0.,other_rate=0.))
    integral=dict(window_native_events=0.,triplet_M1_conditional_events=0.,singlet_2E1_upper_conditional_events=0.,n3_satellite_conditional_events=0.,other_unresolved_events=0.,observed_window_eV_weighted_events=0.)
    for r in selected:
        k=int(r['epoch']);e=float(r['photon_eV']);rate=float(r['native_K_events_per_baryon_s']);
        if rate<0:raise AssertionError('NEGATIVE_BASS_NATIVE_EVENTS')
        f=fractions(e);a=f['ratio_triplet_1s2s_to_measured_core'];b=f['ratio_singlet_1s2s_upper_to_measured_core'];c=f['ratio_n3_satellite_to_measured_core'];d=f['ratio_other_unresolved_to_measured_core']
        quality='PUBLISHED_MEASURED_R31_WITH_ASSUMED_RP' if e<=92.5 else 'AUTHOR_HIGH_ENERGY_EXTRAPOLATED_R31_RP'
        rec=dict(epoch=k,z=float(r['z']),isotope=r['isotope'],bin_index=int(r['bin_index']),photon_eV=e,evidence_class=quality,
           native_K_events_per_baryon_s=rate,
           empirical_ratio_triplet_1s2s=a, empirical_ratio_singlet_1s2s_upper=b,
           empirical_ratio_n3=c,empirical_ratio_other=d,
           conditional_M1_triplet_event_rate=rate*a,
           conditional_2E1_singlet_event_rate_lower=0.,
           conditional_2E1_singlet_event_rate_upper=rate*b,
           conditional_satellite_n3_event_rate=rate*c,
           conditional_other_event_rate=rate*d)
        results.append(rec)
        ep=by_epoch[k];ep['all_native_window_rate']+=rate;ep['triplet_weighted_rate']+=rate*a;ep['singlet_upper_weighted_rate']+=rate*b;ep['n3_weighted_rate']+=rate*c;ep['other_rate']+=rate*d
        factor=weights[k]/H[k]
        integral['window_native_events']+=factor*rate
        integral['triplet_M1_conditional_events']+=factor*rate*a
        integral['singlet_2E1_upper_conditional_events']+=factor*rate*b
        integral['n3_satellite_conditional_events']+=factor*rate*c
        integral['other_unresolved_events']+=factor*rate*d
        integral['observed_window_eV_weighted_events']+=factor*rate*e
    for k in range(193):
        ep=by_epoch[k]
        if abs(ep['all_native_window_rate']-(ep['triplet_weighted_rate']+ep['singlet_upper_weighted_rate']+ep['n3_weighted_rate']+ep['other_rate']))>1e-11*max(ep['all_native_window_rate'],1e-100):
            raise AssertionError('SOURCE_FRACTION_SUM')
    strict=[r for r in results if r['photon_eV']<=92.5]
    strict_exposure=lambda key:float(sum(weights[r['epoch']]/H[r['epoch']]*r[key] for r in strict))
    strict_integrals={'native_window_source_events':strict_exposure('native_K_events_per_baryon_s'),'triplet_M1_conditional_events':strict_exposure('conditional_M1_triplet_event_rate'),'singlet_2E1_upper_conditional_events':strict_exposure('conditional_2E1_singlet_event_rate_upper')}
    native_total=np.array([float(r['K_events_per_baryon_s']) for r in epochs])
    total_original=float(np.dot(weights,native_total/H))
    if integral['window_native_events']>total_original*(1+3e-12):raise AssertionError('MEASURED_BIN_SUBSET_EXCEEDS_ORIGINAL')
    summary={'schema':'REI_F4_FERRETT1987_BASS193_SCOPED_MEASURED_WINDOW_V1',
      'source_owner':'cosmosapjw-quantum/bass@'+SOURCE_OWNER,'source_pr287_zip_sha256':SHA_PR287,
      'original_li1s_source_rows':8492,'source_epoch_count':193,'original_21_ionic_photo_species':21,
      'measured_table_iv_rows_complete_n3':len(TABLE),'measured_energy_eV':[80.,99.],
      'original_photon_bins_in_measured_window':4,'new_science_rows':len(results),
      'measured_table_IV_ratio_semantics':'Measured sigma_triplet/(sigma_n2+sigma_n3); (singlet_1s2s+triplet_1s2p) is only an UPPER BOUND on singlet, NOT singlet itself.',
      'conditional_native_BASS_fraction_projection_not_same_cross_section_source_owner':True,
      'do_not_extrapolate':True,'original_K_allbins_simpson_events_per_baryon':total_original,
      'measured_window_over_all_K_native_event_fraction':integral['window_native_events']/total_original,
      'integrals_per_original_baryon':integral,'direct_R31_measured_regime_80_to_92_5_eV':strict_integrals,
      'higher_e_93_to_99_regime_natively_selected_rows':len(results)-len(strict),
      'raw_experimental_cross_section_calibration_systematic_fraction_about':.20,
      'source_table_iv_doi':SOURCE_DOI,'author_preprint':SOURCE_PREPRINT,
      'document_stability':'Text-extracted publisher/preprint; exact PDF pixels not directly read; 93..99 includes assumed branch extrapolation by author.',
      'new_ivps':0, 'physical_DAG_before_after':{'working':'33/88','central':'28/88','F4_fast':'4/7','canonical_delta':0},
      'thermal_port':'UNBOUND','production':'HOLD'}
    epoch_rows=[dict(epoch=k,z=float(epochs[k]['z']),H_s=float(H[k]),**by_epoch[k]) for k in range(193)]
    return results,epoch_rows,summary


def write_csv(path,rows):
    with pathlib.Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    r,e,s=generate()
    out=ROOT/'results';out.mkdir(exist_ok=True)
    write_csv(out/'FERRETT_MEASURED_BASS_EVENT_1544.csv',r)
    write_csv(out/'FERRETT_BASS_EPOCH_193.csv',e)
    write_csv(out/'FERRETT_TABLE_IV_EXPERIMENT.csv',[dict(E_eV=float(row[0]),n2_MB=float(row[1]),n3_MB=float(row[2]),triplet_1s2s_MB=float(row[3]),unresolved_1s2s_singlet_plus_1s2p_triplet_MB=float(row[4]),**{k:v for k,v in fractions(float(row[0])).items() if k.startswith('ratio_')}) for row in TABLE])
    (out/'RESULTS.json').write_text(json.dumps(s,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(s,indent=2))

if __name__=='__main__':main()
