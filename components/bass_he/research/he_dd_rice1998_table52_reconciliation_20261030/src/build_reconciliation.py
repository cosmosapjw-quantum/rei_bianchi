#!/usr/bin/env python3
"""Source-qualified (NOT independent experiment) Rice 1998/2000 comparison.

Pure Python standard library. Reads two frozen Git-authenticated source JSON
files and one six-row user-image transcription. Emits deterministic results.
"""
import argparse
import csv
import hashlib
import io
import json
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLISHED_SOURCE_GIT_BLOB = '9cdec4449b22bdba2797bbdfb815e98901b85636'
PRELIMINARY_LOW_GIT_BLOB = '266859bb62ef0929b098928b686f945aca600cb9'
MASS_ALPHA = 3727.3794118
MASS_D = 1875.61294500
Q = 2*MASS_D - MASS_ALPHA
BIN_RANGES = {'150-190':(150.,190.),'190-250':(190.,250.)}


def git_blob(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def build(root=ROOT):
    root=Path(root)
    paths={
      'low':root/'inputs/RICE1998_TABLE_5_1_PRELIMINARY_PR125.json',
      'high':root/'sources/RICE1998_TABLE_5_2_PRELIMINARY.json',
      'final':root/'inputs/RICE2000_TABLE_I_AUTHORITATIVE_PR126.json'
    }
    assert git_blob(paths['low']) == PRELIMINARY_LOW_GIT_BLOB, 'PR125 low-source drift'
    assert git_blob(paths['final']) == PUBLISHED_SOURCE_GIT_BLOB, 'PR126 final-source drift'
    low=json.loads(paths['low'].read_text())
    high=json.loads(paths['high'].read_text())
    published=json.loads(paths['final'].read_text())
    assert len(low['entries'])==len(high['entries'])==6 and len(published['observations'])==12
    assert high['source_image_sha256']=='103022f4d890519ee9273e8ddc5d7a632a93ada30ab4a5259216f600b2e10de2'
    assert published['source_count']==1 and published['independent_experiments']==1
    assert high['not_independent_experiment'] is True
    assert abs(Q-23.8464782)<1e-9
    rows=[]
    high_source_exposure=[]
    for i, row in enumerate(published['observations']):
        is_high=(i>=6)
        t=(high['entries'][i-6] if is_high else low['entries'][i])
        tlab=t['theta_lab_deg'] if is_high else t['lab_angle']
        tcm=t['theta_cm_deg'] if is_high else t['cm_angle']
        p=t['dsdo_nb_sr'] if is_high else t['sigma']
        pe=t['dsdo_stat_sd_nb_sr'] if is_high else t['stat_sd']
        y=t['yield']; ye=t['yield_stat_sd'] if is_high else t['yield_sd']
        assert abs(tlab-row['theta_lab'])<1e-8 and abs(tcm-row['theta_cm'])<1e-8
        assert p>0 and row['sigma']>0 and pe>0
        if is_high:
            assert abs(t['theta_cm_reflected_deg']+tcm-180)<1e-10
        ratio=row['sigma']/p
        bin_tag=row['bin']
        emin,emax=BIN_RANGES[bin_tag]
        ymismatch=abs(ye/y-pe/p)
        entry={
          'record':i+1,'bin':bin_tag,'theta_lab_deg':tlab,'theta_cm_deg':tcm,
          'theta_cm_reflected_deg':t['theta_cm_reflected_deg'] if is_high else None,
          'thesis_yield':y,'thesis_yield_stat_sd':ye,
          'prelim_1998_DA_nb_sr':p,'prelim_1998_stat_nb_sr':pe,
          'published_2000_DA_nb_sr':row['sigma'],'published_2000_stat_nb_sr':row['stat_sd'],
          'publication_to_prelim_central_ratio':ratio,
          'published_minus_prelim_DA_nb_sr':row['sigma']-p,
          'reported_yield_per_prelim_DA_sr_per_nb':y/p,
          'yield_vs_DA_fractional_stat_sd_abs_residual':ymismatch,
          'prelim_pair_birth_energy_weighted_DA_interval_nb_MeV_sr':[p*(emin-Q),p*(emax-Q)],
          'published_pair_birth_energy_weighted_DA_interval_nb_MeV_sr':[row['sigma']*(emin-Q),row['sigma']*(emax-Q)],
          'daughter_multiplicity_per_dd_event':2,
          'primary_experiment_id':'Rice_Duke_1998_to_2000_same_campaign',
          'source_status':'1998_PRELIMINARY_SUPERSEDED_BY_2000_PUBLICATION',
          'probabilistic_independence_asserted':False,
          'whole_experiment_joint_covariance':None,
          'photon_history':None,'event_rate':None,'thermal_deposition':None
        }
        rows.append(entry)
        if is_high: high_source_exposure.append(entry)
    leading=[r['publication_to_prelim_central_ratio'] for r in rows[:11]]
    last=rows[-1]['publication_to_prelim_central_ratio']
    mean11=sum(leading)/len(leading)
    # Report rounding-robust nonoverlap of the printed last row vs first five high-bin rows.
    # Last published 0.43 +/- .005 printing interval, prelim 0.594 +/- .0005.
    # These are *printing* intervals, not error bars or confidence intervals.
    last_ratio_printing=[.425/.5945,.435/.5935]
    first_high_printing_min=.135/.1185
    assert last_ratio_printing[1]<first_high_printing_min
    summary={
      'schema':'BASS_HE_RICE1998_2000_TABLE52_SOURCE_VERSION_RECONCILIATION_V1',
      'parent_pr':126,'parent_head':'3305c4579221edde36c14f941b3530375aca4f7a',
      'source_table_1998_52_image_sha256':high['source_image_sha256'],
      'historical_1998_preliminary_high_rows_newly_transcribed':6,
      'historical_1998_preliminary_low_rows_reused':6,
      'rice_2000_published_canonical_rows_reused':12,
      'independent_experimental_campaigns':1,
      'empirical_ratio_first_11_mean_unweighted':mean11,
      'empirical_ratio_first_11_min_max':[min(leading),max(leading)],
      'last_high_angle_ratio':last,
      'last_high_angle_ratio_vs_first_11_mean':last/mean11,
      'last_high_angle_differs_from_single_global_scale_in_central_values':True,
      'last_high_angle_ratio_printing_only_bounds':last_ratio_printing,
      'first_high_angle_ratio_printing_only_lower_bound':first_high_printing_min,
      'publication_rounding_alone_cannot_reconcile_all_12_ratios':True,
      'max_fractional_stat_sd_ratio_difference_high_bin':max(r['yield_vs_DA_fractional_stat_sd_abs_residual'] for r in high_source_exposure),
      'ratio_inference_scope':'DESCRIPTIVE_ONLY_no_joint_1998_2000_covariance_no_chi2_or_pvalue',
      'source_version_discrepancy':'1998_high_bin_139.7deg_0.594_vs_2000_0.43; NOT a verified erratum',
      'observed_source_yield_normalization':'yield/DA is a combined yield response proxy, NOT detector efficiency; observed yield and DA uncertainties are dependent',
      'birth_kinematic_interval_contract':'energy weights SAME as source and fixed effective CM angle; endpoints are NOT observed photons, event rate or heat',
      'nuclear_multiplicity_contract':'sigma_D_effective contains 2*sigma_event_dd for deuterium production from dd, distinct from event rate; Protheroe et al PRD51 (1995) Eq21',
      'central_DAG':'28/88','HE_physical_DAG':'14/18','RICE_BIRTH_AUXILIARY':'1/2',
      'new_Rice_1998_source_reconciliation_micro':'2/2',
      'canonical_physical_delta':0,
      'kappa':None,'R_event':None,'heat_rate':None,'L4':False,'PRODUCTION':'HOLD',
      'independent_author_R6_C9':'NOT_RUN','native_subagent':'NOT_RUN',
      'measured_vs_derived':'1998 thesis/source observed yield+DA 6 added to evidence (same campaign), computed ratio and birth-support conditional; no new independent observation',
      'rows':rows
    }
    # Deterministic byte outputs, no generated timestamps.
    (root/'results').mkdir(exist_ok=True)
    write_json(root/'results/RICE1998_2000_MATCHED_12.json',summary)
    out=io.StringIO(newline='')
    fields=['record','bin','theta_lab_deg','theta_cm_deg','thesis_yield','thesis_yield_stat_sd','prelim_1998_DA_nb_sr','prelim_1998_stat_nb_sr','published_2000_DA_nb_sr','published_2000_stat_nb_sr','publication_to_prelim_central_ratio','published_minus_prelim_DA_nb_sr','reported_yield_per_prelim_DA_sr_per_nb','yield_vs_DA_fractional_stat_sd_abs_residual']
    w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader()
    for r in rows:w.writerow({f:r[f] for f in fields})
    (root/'results/RICE1998_2000_MATCHED_12.csv').write_text(out.getvalue(),encoding='utf-8')
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(ROOT));ns=ap.parse_args()
    res=build(ns.root)
    print(f"one campaign; matched {len(res['rows'])} historical source rows; first11 mean ratio {res['empirical_ratio_first_11_mean_unweighted']:.12f}; 139.7 degree ratio {res['last_high_angle_ratio']:.12f}; production HOLD")
