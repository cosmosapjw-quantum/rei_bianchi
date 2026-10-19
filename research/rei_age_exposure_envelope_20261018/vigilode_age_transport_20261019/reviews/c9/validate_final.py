"""Bind final C9 review to final grouped outputs, exact source bytes and independent data."""
import csv, hashlib, json, math, time, tomllib
from collections import defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
ROOT=Path('/workspace/scratch/36ed695112a9')
LANE=ROOT/'rei_bianchi/research/rei_age_exposure_envelope_20261018/vigilode_age_transport_20261019'
OUT=ROOT/'vigilode_intake_20261019/c9_review'
SNAP=ROOT/'vigilode_intake_20261019/all_dag_snapshot'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def D(x): return Decimal.from_float(x)
def F(x): return Fraction.from_float(x)
study=json.loads((LANE/'results/STUDY.json').read_text())
reference=json.loads((OUT/'DECIMAL_ACTUAL_DATA_REFERENCE.json').read_text())
model=json.loads((LANE/'inputs/model.json').read_text())
assert reference['nodes_sha256']==sha(LANE/'inputs/nodes.csv')
assert reference['model_sha256']==sha(LANE/'inputs/model.json')
assert study['PRODUCTION_SCIENTIFIC_ADMISSION']=='NOT_ISSUED'
assert len(study['cases'])==4 and len(study['paired_bounds'])==4
assert [c['birth_groups'] for c in study['cases']]==[8,16,32,64]
checks=[]
for actual,ref in zip(study['cases'],reference['cases']):
    assert actual['birth_groups']==ref['birth_groups']
    for key,value in ref['values_decimal100'].items():
        interval=actual['species_photoevents'][int(key[-1])] if key.startswith('photo') else actual[key]
        value=Decimal(value)
        assert D(interval[0])<=value<=D(interval[1]), (actual['birth_groups'],key)
        checks.append({'birth_groups':actual['birth_groups'],'observable':key,'interval':interval,
                       'independent_decimal100':str(value),'enclosed':True})
    assert D(actual['initial_mass'][0])<=Decimal(ref['source_mass_decimal100'])<=D(actual['initial_mass'][1])
    assert actual['photon_ledger_residual'][0]<=0<=actual['photon_ledger_residual'][1]
with (LANE/'inputs/nodes.csv').open(newline='') as f:
    rows=[{k:(int(v) if k in ('cohort','cell','node') else float(v)) for k,v in r.items()} for r in csv.DictReader(f)]
rate_ids={}
rate_fractions=[]
for r in rows:
    key=tuple(r[f'lambda{j}'] for j in range(3))
    if key not in rate_ids:
        rate_ids[key]=len(rate_ids)
        rate_fractions.append(sum(map(F,key),Fraction(0)))
    r['rate_id']=rate_ids[key]
assert len(rate_ids)==study['unique_rate_tuples']==1113
assert min(x for x in rate_fractions if x>0)==Fraction(int(study['paired_bounds'][0]['lambda_min_exact_numerator']),int(study['paired_bounds'][0]['lambda_min_exact_denominator']))
group_rows=[]
pair_rows=[]
prefix_checks=0
with localcontext() as ctx:
    ctx.prec=100
    rate_values=[Decimal(f.numerator)/Decimal(f.denominator) for f in rate_fractions]
    tail_cache={}
    gap_cache={}
    for pair,ref in zip(study['paired_bounds'],reference['pairs']):
        n=pair['coarse']
        assert n==ref['coarse']
        signed=Decimal(ref['signed_N_difference_decimal100'])
        sharp=Decimal(ref['nodewise_absolute_difference_sum_decimal100'])
        assert D(pair['signed_N_difference'][0])<=signed<=D(pair['signed_N_difference'][1])
        grouped=pair['grouped_affine']
        for bound in [pair['sharp_per_node_final_upper'],pair['affine_prefix_final_upper'],grouped['final_upper'],grouped['final_min_valid_upper']]:
            assert D(bound)>=sharp and D(bound)>=abs(signed)
        oracle=Fraction(0)
        assert pair['prefix_radii'][0]==0
        assert len(pair['prefix_radii'])==len(pair['leaf_gain_upper'])+1
        assert len(pair['leaf_gain_upper'])==len(pair['leaf_defect_upper'])
        assert all(0<=g<=1 for g in pair['leaf_gain_upper'])
        assert all(d>=0 for d in pair['leaf_defect_upper'])
        for gain,defect,bound in zip(pair['leaf_gain_upper'],pair['leaf_defect_upper'],pair['prefix_radii'][1:]):
            oracle=F(gain)*oracle+F(defect)
            assert F(bound)>=oracle
            prefix_checks+=1
        assert pair['thread_byte_parity'] and grouped['thread_byte_parity']
        assert pair['workspace_matches_allocating_api']
        assert pair['rayon_thread_counts']==[1,2,4]
        by_group=defaultdict(lambda:Decimal(0))
        for r in rows:
            rid=r['rate_id']
            if not rate_fractions[rid]:continue
            a=model['clocks'][str(n)][r['cohort']*n//64]
            b=r['birth_time_s']
            later=max(a,b);earlier=min(a,b)
            kt=(rid,later);kg=(rid,later,earlier)
            if kt not in tail_cache:tail_cache[kt]=(-rate_values[rid]*(D(model['observe_time_s'])-D(later))).exp()
            if kg not in gap_cache:gap_cache[kg]=(-rate_values[rid]*(D(later)-D(earlier))).exp()
            by_group[rid]+=D(r['mass'])*(1-gap_cache[kg])*tail_cache[kt]
        expected_ids=sorted(by_group,key=lambda rid:(rate_fractions[rid],rid))
        assert grouped['rate_ids_in_fixed_sorted_order']==expected_ids
        assert grouped['groups']==len(expected_ids)==1112
        assert len(grouped['group_final_uppers'])==1112
        for rid,bound in zip(expected_ids,grouped['group_final_uppers']):
            assert D(bound)>=by_group[rid], (n,rid,bound,by_group[rid])
            group_rows.append({'birth_groups':n,'rate_id':rid,'group_upper':bound,
                               'independent_decimal100':str(by_group[rid]),'enclosed':True})
        assert F(grouped['final_upper'])>=sum(map(F,grouped['group_final_uppers']),Fraction(0))
        pair_rows.append({'coarse':n,'signed_N_difference_decimal100':str(signed),'D_decimal100':str(sharp),
                          'grouped_upper':grouped['final_upper'],'independent_groups_checked':len(expected_ids),
                          'grouped_relative_excess_decimal100':str((D(grouped['final_upper'])-sharp)/sharp) if sharp else '0',
                          'enclosed':True})
lock=tomllib.loads((LANE/'rust/Cargo.lock').read_text())
versions={p['name']:p['version'] for p in lock['package']}
expected_versions={'num-rational':'0.4.2','num-bigint':'0.4.6','num-traits':'0.2.19','rayon':'1.12.0','serde':'1.0.228','serde_json':'1.0.145'}
for name,version in expected_versions.items(): assert versions[name]==version
vendor_count=vendor_files=0
for package in lock['package']:
    if 'checksum' not in package:continue
    folder=LANE/'rust/vendor'/package['name']
    checksum=json.loads((folder/'.cargo-checksum.json').read_text())
    assert checksum['package']==package['checksum'],package['name']
    assert tomllib.loads((folder/'Cargo.toml').read_text())['package']['version']==package['version']
    for name,digest in checksum['files'].items():
        assert sha(folder/name)==digest,(package['name'],name)
        vendor_files+=1
    vendor_count+=1
assert vendor_count==22
for local,upstream in [('src/vendor/directed.rs','crates/rodas5p-core/src/directed.rs'),('src/vendor/affine_transport.rs','crates/rodas5p-integrators/src/affine_transport.rs'),('LICENSE-VigilODE','LICENSE')]:
    assert (LANE/'rust'/local).read_bytes()==(SNAP/upstream).read_bytes()
offline=json.loads((LANE/'results/OFFLINE_VENDOR_TEST_RECEIPT.json').read_text())
assert offline['exit_code']==0 and '--locked' in offline['command'] and '--offline' in offline['command']
assert offline.get('cargo_home_has_no_registry') is True
commands=json.loads((LANE/'results/RUN_COMMANDS.json').read_text())
assert all(c['exit_code']==0 for c in commands)
old=json.loads((LANE/'results/global_min_before_grouping/STUDY.json').read_text())
assert old['cases']==study['cases'],'Grouped replay changed physical setting outputs'
def finite_tree(v):
    if isinstance(v,dict):
        for x in v.values():finite_tree(x)
    elif isinstance(v,list):
        for x in v:finite_tree(x)
    elif isinstance(v,float):assert math.isfinite(v)
finite_tree(study)
owned=['prepare_export.py','run_study.py','verify.py','summarize.py','THEORY_KO.md','README.md',
       'rust/Cargo.toml','rust/Cargo.lock','rust/VENDOR_PROVENANCE.json','rust/LICENSE-VigilODE','rust/.cargo/config.toml',
       'rust/src/lib.rs','rust/src/certified.rs','rust/src/main.rs','rust/src/vendor/directed.rs','rust/src/vendor/affine_transport.rs',
       'inputs/nodes.csv','inputs/model.json','inputs/native_setup.json','inputs/EXPORT_RECEIPT.json',
       'results/STUDY.json','results/RUN_COMMANDS.json','results/VERIFICATION.json','results/EXP_FIXTURES.json',
       'results/OFFLINE_VENDOR_TEST_RECEIPT.json','results/cargo_test.stdout','results/cargo_test.stderr',
       'results/fixed_data_study.stdout','results/fixed_data_study.stderr','results/FAILED_ATTEMPTS.json']
files={name:sha(LANE/name) for name in owned}
result={'status':'PASS_SCOPED_C9_INDEPENDENT_REVIEW','source_sha':'35d9747a0bbedcafdb568467ce7c1e7a25f965b6',
        'vigilode_pin':'ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406','reviewed_files_sha256':files,
        'export_audit_sha256':sha(OUT/'EXPORT_NODE_AUDIT.json'),'decimal_reference_sha256':sha(OUT/'DECIMAL_ACTUAL_DATA_REFERENCE.json'),
        'actual_observable_enclosures_checked':len(checks),'actual_group_enclosures_checked':len(group_rows),
        'all_reported_global_prefix_exact_dyadic_checks':prefix_checks,
        'actual_global_and_grouped_thread_parity_exercised_by_checked_source_and_successful_run':True,
        'all_reported_float_values_finite':True,'upstream_algorithm_bytes_and_mit_license_exact':True,
        'direct_package_versions':expected_versions,'vendored_registry_packages_checked':vendor_count,'vendored_source_files_rehashed':vendor_files,
        'offline_locked_test_exit_code':offline['exit_code'],'offline_locked_test_no_registry':True,
        'stale_offline_failure_receipt_issue':'CLOSED: canonical receipt corrected using existing successful evidence; failed attempt preserved.',
        'same_four_physical_settings_unchanged_by_grouped_replay':True,'native_exports':1,'native_reexecutions_in_review':0,
        'new_nonlinear_campaigns':0,'independent_reference_kind':'Decimal100 numerical cross-check; mathematical enclosure proof separately reviewed against exact dyadic model.',
        'model_scope_review':'PASS: source packets, frozen endpoint gas/geometry, exact exported dyadic coefficients/clocks, closed-pair prefix domain, separate age moments, no nonlinear trajectory admission.',
        'pairs':pair_rows,'production_scientific_admission':'NOT_ISSUED'}
(OUT/'ACTUAL_OBSERVABLE_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
(OUT/'ACTUAL_GROUP_CHECKS.json').write_text(json.dumps(group_rows,indent=2)+'\n')
(OUT/'C9_FINAL_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='reviewed_files_sha256'},indent=2))
