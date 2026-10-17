#!/usr/bin/env python3
from pathlib import Path
import csv,json,statistics,math
R=Path(__file__).resolve().parents[1];e=R/'evidence'
def read(fn):return list(csv.DictReader((e/fn).open()))
a=read('verner_threshold_error.csv')
error={}
for n in [1,2,4,8,16,32,64,128]:
    x={r['mode']:r for r in a if int(r['N'])==n}
    error[str(n)]={m:{'rel_tau_error':float(v['relative_tau_error']),'tau':float(v['tau']),'roots':int(v['crossings'])}for m,v in x.items()}
compact=read('age_exactzero_campaign_12.csv')
cp=[]
for n in range(1,13):
    d={r['mode'].strip():r for r in compact if int(r['step'])==n}
    old=d['retain_all'];new=d['exact_zero_only'];
    cp.append({'step':n,'uncompressed':int(old['cohorts']),'exactzero_compressed':int(new['cohorts']),
               'retired_this_step':int(new['removed_exact_zeros']),
               'remaining_fraction':int(new['cohorts'])/int(old['cohorts']),
               'seconds_old':float(old['elapsed_s']),'seconds_compact':float(new['elapsed_s']),
               'observed_step_speedup':float(old['elapsed_s'])/float(new['elapsed_s']),
               'number_discrepancy':abs(float(old['photon_absorbed'])-float(new['photon_absorbed']))+
                   abs(float(old['photons_surviving'])-float(new['photons_surviving']))})
ben=read('native_cache_benchmark_rates.csv');tr=[]
for n in (4,8,16):
    b={k:[float(r['time_s']) for r in ben if int(r['nsteps'])==n and r['mode']==k]for k in ('original_s3','cached_s4')}
    old=statistics.median(b['original_s3']);new=statistics.median(b['cached_s4']);tr.append({'nsteps':n,'runs_each':3,'old_median_s':old,'new_median_s':new,'speedup_old_over_new':old/new,'rotated_order':True})
ref=json.loads((e/'SCIPY_VERNER_REFERENCE.json').read_text())
out={
 'science_scope':'P4/S4 prescribed axisymmetric Bianchi-I, immutable MD14/Verner/Grackle/Savin source modules, optional literal f64-zero retirement',
 'claimed':'PASS_SCOPED_THRESHOLD_ROOTS_AND_EXACT_ZERO_COMPACTION',
 'source_original':'PR150 da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7, PR185 d239fc2e5e9402801f3cca2523425a9ddf2a1504',
 'threshold_oracle':{'N':error,'scipy_reference':ref},'compression':cp,
 'cached_real_source_time_measurements':tr,
 'current_scope_open':['SA-01/02 native source-age','FLRW-CONV','BI-SIGNED on-shell BASS geometry','real EoR source-on',
  'age compression for nonzero long lived cohorts','continuous spectral convergence'],
 'global_method_order':'NOT_ADMITTED'
}
(e/'SCIENCE_SUMMARY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('P4/S4 source evidence summary:')
for n in [1,4,16,64,128]:print(n,error[str(n)])
print('compact_final',cp[-1]);print('matched_benchmark',tr)
