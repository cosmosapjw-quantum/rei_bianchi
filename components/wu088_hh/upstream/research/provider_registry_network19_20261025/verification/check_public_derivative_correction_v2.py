"""Close only the R2 public-derivative checker expectation defect.

The first nine passed groups and their original failure record are immutable.
No project scientific code, source parser, builder or prior checker is imported.
"""
from pathlib import Path
import hashlib
import json
import time

BASE = Path('/workspace/scratch/3ffa3d77ca37')
PRIVATE = BASE/'network19_intake'
PUBLIC = BASE/'WU088_HH/research/provider_registry_network19_20261025/sources/primary'
REVIEW = BASE/'network19_review'
OUTPUT = REVIEW/'PUBLIC_DERIVATIVE_CORRECTION_RESULTS.json'
PINS = {
    REVIEW/'independent_r2_check.py': '9086e493d65125df474657668d2e4d14221ba3c47668c7f1a1b432c06eb2dc21',
    PRIVATE/'PROVIDER_ROWS.json': 'be8a66c04f662c00e779d6aebe1245da72c0d868625264881cb18f6c83e6b39e',
    PUBLIC/'PROVIDER_ROWS.json': '9878f53c509ddaaa0317df2349913040dfd01425bc318d66cca0fd307bed33e3',
    PUBLIC/'PUBLICATION_SUBSET_MANIFEST.json': '8657e0572ba0a759e13771ee1c924b32d774156c34bd367bd430f2e13a89c542',
}
INPUTS = {}
CHECKS = []


def sha(path):
    value = hashlib.sha256(path.read_bytes()).hexdigest()
    INPUTS[str(path)] = value
    return value


def ck(condition, label):
    CHECKS.append({'check':label,'pass':bool(condition)})
    if not condition:
        raise AssertionError(label)


def read(path):
    sha(path)
    return json.loads(path.read_text())


def clean(value):
    removed = {'raw_literal','native_table_literal','S0_printed_literal','source_statement'}
    if isinstance(value,dict):
        return {k:clean(v) for k,v in value.items() if k not in removed}
    if isinstance(value,list):
        return [clean(v) for v in value]
    return value


def main():
    if OUTPUT.exists():
        raise ValueError('APPEND_ONLY_RESULT_EXISTS_NO_REPLAY')
    t0=time.monotonic();c0=time.process_time()
    for path,expected in PINS.items():
        ck(sha(path)==expected,'Unchanged frozen identity '+path.name)
    previous=read(REVIEW/'INDEPENDENT_R2_RESULTS.json')
    passed=[r for r in previous['checks'] if r['status']=='PASS']
    ck(len(passed)==9 and previous['failed_groups']==['public_numeric_derivative_and_redistribution'],
       'Reuse exactly nine originally passed groups; preserve one recorded checker failure')
    private=read(PRIVATE/'PROVIDER_ROWS.json')
    public=read(PUBLIC/'PROVIDER_ROWS.json')
    ck(len(private['rows'])==len(public['rows'])==19,'Nineteen public variants preserved')
    original_s0='Section3 intro: unless specified otherwise, nominal S(0) is at about0.5–1.0keV'
    public_s0='Source section3 usually labels a value near0.5–1.0keV as S0; this is not a new exactzero-energy admission.'
    observed=[]
    for old,new in zip(private['rows'],public['rows']):
        expected=clean(old)
        if old['id'].startswith('NACREII'):
            ck(old['support']['S0_definition']==original_s0,'Exact prior S0 wording '+old['id'])
            expected['support']['S0_definition']=public_s0
            observed.append({'id':old['id'],'allowed_path':'support.S0_definition','kind':'same-meaning public paraphrase'})
        if old['id']=='NACREII2013_t_alpha_gamma_TABLE8':
            expected['branch']['inclusive_daughter_states']=['ground','first_excited']
            observed.append({'id':old['id'],'allowed_path':'branch.inclusive_daughter_states','kind':'explicit source fact formerly in removed source_statement'})
        actual={k:v for k,v in new.items() if k!='publication_source_availability'}
        ck(actual==expected,'Exact complete derivative after only the two explicit metadata rules '+old['id'])
        for key in ['raw_values','units','uncertainty','Q']:
            ck(clean(old[key])==new[key],'Unchanged '+key+' '+old['id'])
        availability=new['publication_source_availability']
        ck(availability['original_source_SHA256']==old['source_SHA256'], 'Original source identity retained '+old['id'])
        ck(availability['original_bytes_bundled'] is (PUBLIC/new['source_file']).exists(), 'Honest publication source availability '+old['id'])
    ck(len(observed)==11,'Ten S0 paraphrases plus one explicit inclusive-state field')
    native_path=PRIVATE/'derived_text/NACREII_1310.7099.txt'
    ck(sha(native_path)=='56da1cb84750073ed6e538bed333f095ef45d4ca60af6b686c009a40dd1e43bd','Native NACRE text identity')
    source=native_path.read_text().split('\n')
    ck('transitions to the ground and the' in source[1763]
       and 'first excited states of 7 Li are considered inclusively' in source[1764],
       'NACRE section 3.7 native lines 1764–1765 directly support inclusive daughter-state annotation')
    manifest=read(PUBLIC/'PUBLICATION_SUBSET_MANIFEST.json')
    bundled={sha(p) for p in PUBLIC.rglob('*') if p.is_file()}
    for excluded in manifest['excluded_original_files']:
        ck(excluded['sha256'] not in bundled,'Excluded original bytes absent '+excluded['path'])
    native_viviani=(PRIVATE/'derived_text/Viviani2023_DD.txt').read_text().split('\f')[0]
    ck('Creative Commons Attribution 3.0' in native_viviani,'Actual Viviani first-page redistribution grant')
    notices=(PUBLIC/'THIRD_PARTY_NOTICES.md').read_text()
    ck(all(x in notices for x in ['Viviani','3.0','2586','012076','10.1088/1742-6596/2586/1/012076']),
       'Viviani authors, source title/journal/DOI and license attribution preserved')
    report={
        'schema':'WU_R2_TARGETED_PUBLIC_DERIVATIVE_CHECKER_CORRECTION_V1',
        'status':'PASS_SCOPED','reviewer':'/root/authority_survey',
        'failure_class':'checker expectation omitted two explicit public metadata transforms',
        'old_scientific_or_source_result_failure':False,
        'first_result':{'path':'INDEPENDENT_R2_RESULTS.json','sha256':sha(REVIEW/'INDEPENDENT_R2_RESULTS.json'),'unchanged':True},
        'first_checker':{'path':'independent_r2_check.py','sha256':sha(REVIEW/'independent_r2_check.py'),'unchanged':True},
        'checker_sha256':sha(Path(__file__)),
        'corrected_group':'public_numeric_derivative_and_redistribution',
        'passed_groups_reused_without_execution':[r['group'] for r in passed],
        'allowed_transforms':observed,
        'checks':CHECKS,'input_sha256':INPUTS,
        'source_numeric_rows_or_registry_changes':0,
        'native_NACRE_ENDF_He4_transcriptions_replayed':0,
        'new_number_columns_replayed':0,
        'new_rate_Q_IVP_calculations':0,'old_suite_replays':0,
        'CPU_s':time.process_time()-c0,'wall_s':time.monotonic()-t0,
        'composed_acceptance':'nine original passed groups plus this corrected group = ten accepted scoped groups; not a new ten-group rerun',
        'physical_admission':False}
    with OUTPUT.open('x') as out:
        json.dump(report,out,ensure_ascii=False,indent=2);out.write('\n')
    print(json.dumps({'status':report['status'],'checks':len(CHECKS),'output':str(OUTPUT),'sha256':sha(OUTPUT)},indent=2))


if __name__=='__main__':
    main()
