"""Read-only document/hash/receipt/table checks; imports no scientific model."""
from pathlib import Path
import ast
import csv
import datetime
import difflib
import hashlib
import json
import os
import statistics

HERE=Path(__file__).resolve().parent
OUT=HERE/'SAVED_PAYLOAD_OBSERVATIONS.json'
if OUT.exists():
    raise SystemExit('Saved audit exists; reuse it')
UNIT=Path('/tmp/he32_resume_20261022/repos/BASS_HE/research/he37_h1_differential_gain_20261023')
DIAG=Path('/tmp/he37_diagnostic')
BRIDGE=Path('/tmp/he37_net_bridge')
PROVIDER=Path('/tmp/he37_source_implementation')
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p: json.loads(Path(p).read_text())
bindings=[]
def bind(p):
    p=Path(p)
    row={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
    bindings.append(row)
    return row
def manifest(root,expected_count):
    value=read(root/'FILE_MANIFEST.json')
    assert len(value['files'])==expected_count
    rows=[]
    for recorded in value['files']:
        current=bind(root/recorded['path'])
        assert current['sha256']==recorded['sha256'],recorded['path']
        assert current['bytes']==recorded['bytes'],recorded['path']
        rows.append({'path':recorded['path'],'sha256_match':True,'bytes_match':True})
    bind(root/'FILE_MANIFEST.json')
    return rows

doc=read(UNIT/'evidence/docfix/CORRECTION.json')
before=UNIT/'evidence/docfix/DERIVATION_before.md'
after=UNIT/'theory/DERIVATION.md'
old_title='H. P. Le and J.-L. Cambier, *Modeling of ionization/recombination processes\nusing a multifluid framework*, Physics of Plasmas 23, 063505 (2016),'
new_title='H. P. Le and J.-L. Cambier, *Modeling of Inelastic Collisions in a Multifluid Plasma:\nIonization and Recombination*, Physics of Plasmas 23, 063505 (2016),'
assert before.read_bytes()==Path('/tmp/he37_gain_theory/DERIVATION.md').read_bytes()
assert before.read_text().count(old_title)==1
assert after.read_text()==before.read_text().replace(old_title,new_title)
r2=next(r for r in doc['items'] if r['finding']=='R2')
assert sha(before)==r2['old_sha256'] and sha(after)==r2['new_sha256']
assert doc['affected_scientific_execution']==0
clarification=UNIT/'components/lc_provider/INPUT_COERCION_CLARIFICATION.md'
assert 'Mixed Boolean/numeric sequences follow NumPy numeric' in clarification.read_text()
assert sha(UNIT/'components/lc_provider/lc_ionization.py')==sha(PROVIDER/'lc_ionization.py')=='9d40436fbebd2e99666cf15ed069ba4041693de32da843dc23b9672d59b12a16'
assert sha(UNIT/'components/lc_provider/verify_provider.py')==sha(PROVIDER/'verify_provider.py')
for p in (UNIT/'evidence/docfix/CORRECTION.json',before,after,clarification,UNIT/'components/lc_provider/lc_ionization.py',UNIT/'components/lc_provider/verify_provider.py'):
    bind(p)

diag_manifest=manifest(DIAG,22)
bridge_manifest=manifest(BRIDGE,13)
diagnostic=read(DIAG/'outputs/DIAGNOSTIC.json')
identity=diagnostic['identity']
for field,rel in [('script_sha256','run_diagnostic.py'),('provider_sha256','vendor/lc_ionization.py'),('CCC_saved_csv_sha256','reused/ccc_moments.csv'),('contract_sha256','CONTRACT.json')]:
    assert identity[field]==sha(DIAG/rel),field
for row in diagnostic['payloads']:
    assert row['sha256']==sha(DIAG/row['path'])
assert diagnostic==read(DIAG/'attempts/attempt_20261023T021354242787Z/RESULT.json')
ccc_original=Path('/tmp/he32_resume_20261022/repos/BASS_HE/research/he36_reactive_moment_bridge_20261023/components/diagnostic/outputs/ccc_moments.csv')
assert sha(ccc_original)==sha(DIAG/'reused/ccc_moments.csv')
bind(ccc_original)
with (DIAG/'outputs/h1_gain_moments.csv').open() as f:
    rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
with (DIAG/'reused/ccc_moments.csv').open() as f:
    old=list(csv.DictReader(f))
assert len(rows)==len(old)==129
assert rows==read(DIAG/'outputs/h1_gain_moments.json')['rows']
assert [r['temperature_K'] for r in rows]==[float(r['temperature_K']) for r in old]
assert [rows[i] for i in (0,64,128)]==diagnostic['endpoint_and_center_rows']
ratios=[r['native_over_CCC_rate'] for r in rows]
assert [min(ratios),max(ratios)]==diagnostic['native_over_CCC_rate_range']
assert all(r['net_cooling_energy_eV']==13.6 for r in rows)
assert all(r['nu_lower_per_nH_m3_s']<=r['kappa2_native_m3_s']<=r['nu_upper_per_nH_m3_s'] for r in rows)
assert [r['order'] for r in diagnostic['resolution']]==[64,96]
assert diagnostic['resolution'][0]['max_relative']>3e-12
assert diagnostic['resolution'][1]['max_relative']<3e-12
assert diagnostic['selected_GL_order']==96
bench=read(DIAG/'outputs/BENCHMARK.json')
ratios=[p['quadrature_over_analytic'] for p in bench['pairs']]
assert len(ratios)==bench['paired_trials']==5
assert bench['warmup_pairs']==2 and bench['batches_per_lane_per_trial']==64
for p in bench['pairs']:
    timing=p['seconds_per_129T_batch']
    assert p['quadrature_over_analytic']==timing['quadrature']/timing['analytic']
    expected=['analytic','quadrature'] if p['trial']%2 else ['quadrature','analytic']
    assert p['order']==expected
assert statistics.median(ratios)==bench['median_paired_ratio']
assert [min(ratios),max(ratios)]==bench['paired_ratio_range']
for lane,key in [('analytic','median_analytic_seconds_per_batch'),('quadrature','median_GL_seconds_per_batch')]:
    assert statistics.median(p['seconds_per_129T_batch'][lane] for p in bench['pairs'])==bench[key]
assert bench['ratio_of_medians']==bench['median_GL_seconds_per_batch']/bench['median_analytic_seconds_per_batch']
counts=diagnostic['execution_counts']
assert counts['native_analytic_primary_batches']==1
assert counts['raw_GL_resolution_batches']==2
assert counts['native_analytic_warmup_batches']==counts['raw_GL_warmup_batches']==2
assert counts['native_analytic_timed_batches']==counts['raw_GL_timed_batches']==5*64
assert counts['old_CCC_model_evaluations']==counts['new_IVP']==counts['old_IVP_or_suite_replay']==0
render=read(DIAG/'plots/RENDER_RECEIPT.json')
assert render['input_csv_sha256']==sha(DIAG/'outputs/h1_gain_moments.csv')
assert render['script_sha256']==sha(DIAG/'render_diagnostic.py')
for p in render['payloads']:
    assert p['sha256']==sha(DIAG/p['path'])
oldrender=read(DIAG/'plots/attempts/render_001/RENDER_RECEIPT.json')
assert oldrender['input_csv_sha256']==render['input_csv_sha256']
old_script=(DIAG/'plots/attempts/render_001/render_diagnostic.py').read_text()
new_script=(DIAG/'render_diagnostic.py').read_text()
render_diff=''.join(difflib.unified_diff(old_script.splitlines(True),new_script.splitlines(True),fromfile='render_001',tofile='render_002'))

receipt=read(BRIDGE/'attempts/attempt_20261023T022026748127Z/RESULT.json')
start=read(BRIDGE/'attempts/attempt_20261023T022026748127Z/START.json')
assert all(receipt[k]==v for k,v in start.items())
for name,digest in receipt['hashes'].items():
    assert sha(BRIDGE/name)==digest,name
assert receipt['passed']==7 and receipt['failed']==0 and receipt['exit_code']==0
assert all(r['status']=='PASS' for r in receipt['results'])
assert receipt['groups']==[r['group'] for r in receipt['results']]
tree=ast.parse((BRIDGE/'verify_net_bridge.py').read_text())
groups=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GROUPS' for t in n.targets))
assert [k.value for k in groups.keys]==receipt['groups']
donor=read(BRIDGE/'DONOR_PROVENANCE.json')
donor_matches=[]
for d in donor['source_files']:
    assert sha(d['source'])==sha(BRIDGE/d['path'])==d['sha256']
    donor_matches.append({'path':d['path'],'source':d['source'],'sha256':d['sha256'],'byte_identical_confirmed':True})
assert sha(donor['species_index_source'])==donor['species_index_source_sha256']
public_net=UNIT/'components/net_bridge/h1_net/net_source.py'
assert sha(public_net)==sha(BRIDGE/'h1_net/net_source.py')
bind(public_net)
public_bridge_matches=[]
for recorded in read(BRIDGE/'FILE_MANIFEST.json')['files']:
    p=UNIT/'components/net_bridge'/recorded['path']
    assert sha(p)==recorded['sha256'],str(p)
    public_bridge_matches.append({'path':str(p),'sha256':sha(p),'match':True})

result={
 'schema':'he37.independent_followup_saved_payload_audit.v1',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'PASS',
 'script_sha256':sha(__file__),
 'new_model_evaluations':0,'new_IVPs':0,'new_benchmarks':0,'new_renders':0,'unchanged_suite_replays':0,
 'documentary_disposition':{'R1':'closed_by_precise_coercion_contract_with_original_code_retained','R2':'closed_by_exact_title_only_replacement','old_derivation_sha256':sha(before),'new_derivation_sha256':sha(after),'provider_code_unchanged':True,'verifier_code_unchanged':True},
 'diagnostic_manifest':diag_manifest,'bridge_manifest':bridge_manifest,
 'diagnostic_saved_rows':129,'csv_json_rows_exact_match':True,'CCC_grid_and_bytes_match_HE36':True,
 'diagnostic_identity_and_payload_hashes_match':True,
 'benchmark_saved_statistics_match':True,'benchmark_counts_match_source_loops':True,
 'execution_counts_reused':counts,
 'render_receipt_payloads_and_code_match':True,'both_renders_same_csv':True,'render_script_diff':render_diff,
 'bridge_all_nine_receipt_hashes_match':True,'bridge_seven_groups_match_current_verifier':True,
 'bridge_donor_byte_matches':donor_matches,'public_bridge_copy_matches':public_bridge_matches,
 'reviewed_file_bindings':bindings,
}
with OUT.open('x') as f:
    json.dump(result,f,indent=2,ensure_ascii=False,allow_nan=False)
    f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'status':'PASS','diagnostic_manifest_entries':len(diag_manifest),'bridge_manifest_entries':len(bridge_manifest),'diagnostic_rows':len(rows),'bridge_receipt_hashes':len(receipt['hashes']),'doc_findings_closed':['R1','R2'],'model_evaluations':0,'saved':str(OUT)}))
