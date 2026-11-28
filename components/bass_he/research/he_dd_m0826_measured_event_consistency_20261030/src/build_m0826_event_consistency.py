#!/usr/bin/env python3
"""EXFOR source-locked M0826 DD angular/event normalization consistency.

Physical output is a conditional source cross-comparison, not a photonuclear
reaction rate nor a detector-efficiency calibration. No artificial covariance.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

SOURCE_SHA256 = {
    'M0826': '05ea65eaa1a7245f19fd47aa14e91bef3d706fe2a55c6d70a512808ee4e9284c',
    'M0011': '8d45af5ca4f0df3c000a5cf672cd84e2e8512b65b52b03a912c5080d2bf5d9b2',
}
SOURCE_GIT_BLOBS = {
    'M0826': '95010842754215e98eea8d99eff5f3de0799c666',
    'M0011': '20804471fb7584e07ab979ecad6a3e96cba0c6a2',
}

def source_bytes(root: Path, entry: str) -> bytes:
    b = (root / 'sources' / (entry + '.x4')).read_bytes()
    if hashlib.sha256(b).hexdigest() != SOURCE_SHA256[entry]:
        raise ValueError('SOURCE_SHA256_MISMATCH:' + entry)
    git = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
    if git != SOURCE_GIT_BLOBS[entry]:
        raise ValueError('GIT_BLOB_MISMATCH:' + entry)
    return b

def parse_subentry(b: bytes, subentry: str, expected_header: str, expected_unit: str, n: int):
    txt = b.decode('ascii')
    first = 'SUBENT        ' + subentry
    i = txt.index(first)
    block = txt[i:txt.index('ENDSUBENT', i)]
    lines = block.splitlines()
    idx = next(j for j,line in enumerate(lines) if line.startswith('DATA '))
    assert lines[idx].split()[1:3] == [str(len(expected_header.split())), str(n)]
    assert lines[idx+1].split() == expected_header.split(), (subentry, lines[idx+1])
    assert lines[idx+2].split() == expected_unit.split(), (subentry, lines[idx+2])
    raw = [line.split() for line in lines[idx+3:idx+3+n]]
    assert len(raw)==n and all(len(row)==len(expected_header.split()) for row in raw)
    assert lines[idx+3+n].startswith('ENDDATA')
    return [[float(v) for v in row] for row in raw]

def build(root: Path) -> dict:
    m82 = source_bytes(root, 'M0826')
    m11 = source_bytes(root, 'M0011')
    da = parse_subentry(m82,'M0826003', 'ANG-CM-MIN ANG-CM-MAX DATA-CM ERR-S',
                        'ADEG ADEG MU-B/SR MU-B/SR', 9)
    sig = parse_subentry(m82,'M0826002', 'EN-MIN EN-MAX DATA ERR-S',
                         'MEV MEV MICRO-B MICRO-B', 4)
    m11sig = parse_subentry(m11,'M0011002','EN DATA ERR-S',
                            'MEV MICRO-B MICRO-B', 14)
    assert [(r[0],r[1]) for r in sig]==[(30.,40.),(40.,50.),(50.,60.),(60.,75.)]
    assert da[0][0]==0. and da[-1][1]==180.
    assert all(da[i][1]==da[i+1][0] for i in range(8))
    assert all(r[2]>=0 and r[3]>=0 for r in da)
    assert all(r[1]>=0 and r[2]>=0 for r in m11sig)
    assert [r[0] for r in m11sig]==[26.,28.,30.,32.,34.,36.,38.,40.,42.,44.,47.5,52.5,57.5,65.]
    contributions=[]
    weights=[]
    for i,(lo,hi,datum,err) in enumerate(da):
        weight=2*math.pi*(math.cos(math.radians(lo))-math.cos(math.radians(hi)))
        assert weight>0
        weights.append(weight)
        contributions.append({
            'source_id': 'M0826003','row':i+1,
            'theta_cm_min_deg':lo,'theta_cm_max_deg':hi,
            'DA_microbarn_per_sr':datum,'ERR_S_microbarn_per_sr':err,
            'solid_angle_sr':weight,
            'inclusive_daughter_integral_microbarn':weight*datum,
            'conditional_one_event_contribution_microbarn':0.5*weight*datum,
            'independent_stat_sd_contribution_microbarn':0.5*weight*err,
        })
    assert math.isclose(sum(weights),4*math.pi,rel_tol=0,abs_tol=1e-12)
    inclusive=sum(z['inclusive_daughter_integral_microbarn'] for z in contributions)
    event=0.5*inclusive
    independent_da_sd=math.sqrt(sum(z['independent_stat_sd_contribution_microbarn']**2 for z in contributions))
    covariance_unknown_max=sum(z['independent_stat_sd_contribution_microbarn'] for z in contributions)
    # Equal-width averaging is a comparison convention, NOT a recovered beam-energy spectrum.
    source_sig_overlap=[r for r in sig if r[0]>=30 and r[1]<=50]
    assert len(source_sig_overlap)==2
    width=sum(row[1]-row[0] for row in source_sig_overlap)
    comparison_sig=sum((r[1]-r[0])*r[2] for r in source_sig_overlap)/width
    comparison_sd_independent=math.sqrt(sum(((r[1]-r[0])/width*r[3])**2 for r in source_sig_overlap))
    comparison_sd_corrmax=sum((r[1]-r[0])/width*r[3] for r in source_sig_overlap)
    return {
        'schema':'HE_DD_M0826_MEASURED_ANGULAR_TOTAL_EVENT_CONSISTENCY_V1',
        'authority':'IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871',
        'original_git_blobs':SOURCE_GIT_BLOBS,'original_sha256':SOURCE_SHA256,
        'source_observation_counts':{'M0826003_angular_bin_DA':9,'M0826002_total_SIG_energy_bins':4,
                                     'M0011002_total_SIG_energy_points':14},
        'angular_bin_observations':contributions,
        'original_M0826_SIG_energy_bins':[{'EN_MIN_MeV':r[0],'EN_MAX_MeV':r[1],
                                           'SIG_microbarn':r[2],'ERR_S_microbarn':r[3]} for r in sig],
        'original_M0011_SIG_points':[{'EN_MeV':r[0],'SIG_microbarn':r[1],
                                      'ERR_S_microbarn':r[2]} for r in m11sig],
        'cross_comparison':{
            'angular_energy_support_MeV':[30.,50.],
            'inclusive_daughter_4pi_microbarn':inclusive,
            'conditional_event_one_half_angular_microbarn':event,
            'conditional_independent_DA_STAT_SD_event_microbarn':independent_da_sd,
            'arbitrary_positive_covariance_DA_STAT_SD_event_upper_microbarn':covariance_unknown_max,
            'equal_width_SIG_energy_bin_mean_microbarn':comparison_sig,
            'conditional_independent_SIG_STAT_SD_mean_microbarn':comparison_sd_independent,
            'arbitrary_positive_covariance_SIG_STAT_SD_mean_upper_microbarn':comparison_sd_corrmax,
            'DA_integral_divided_by_SIG_mean':inclusive/comparison_sig,
            'event_minus_SIG_mean_microbarn':event-comparison_sig,
            'event_divided_by_SIG_mean_minus_one':event/comparison_sig-1,
            'source_gammaphoton_intensity_systematic_upper_fraction_M0826':0.05,
            'source_DA_status':'CURVE_FROM_1972_FIGURE_1',
            'source_SIG_status':'TABLE_FROM_1972_TABLE_1',
            'source_stat_error_label':'ERR-S',
            'DA_source_inclusive_daughter_interpretation':'SUPPORTED_BY_CONSISTENCY_NOT_ORIGINALLY_CONFIRMED',
            'equal_energy_width_comparison':'ASSUMPTION_NO_FLUX_HISTORY',
            'joint_experimental_covariance':'UNKNOWN',
            'detector_acceptance':'NOT_SOURCE_QUALIFIED',
            'spin_and_identical_D_absolute_reciprocity':'NOT_PROMOTED',
        },
        'physical_claims':{'new_source_rows':0,'new_source_derived_statistic':1,
                           'real_absolute_inverse_sigma_data':False,
                           'sigma_event_gamma_He4_dd':None,
                           'kappa':None,'R_event':None,'heat_rate':None,
                           'physical_activation':False,'L4':False,'production':'HOLD'},
        'DAG':{'central':'28/88','HE_physical':'14/18',
               'scoped_event_consistency':'2/2','canonical_physical_delta':0},
    }

def write_outputs(root:Path):
    result=build(root)
    out=root/'results';out.mkdir(parents=True,exist_ok=True)
    (out/'M0826_MEASURED_EVENT_CONSISTENCY.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    with (out/'M0826_SOURCE_DA_EVENT_CONTRIBUTIONS.csv').open('w',newline='') as f:
        rows=result['angular_bin_observations']
        wr=csv.DictWriter(f,list(rows[0]),lineterminator='\n')
        wr.writeheader();wr.writerows(rows)
    return result

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--root',type=Path,default=Path('.'))
    a=cli.parse_args()
    d=write_outputs(a.root)
    print(json.dumps(d['cross_comparison'],sort_keys=True,indent=2))
