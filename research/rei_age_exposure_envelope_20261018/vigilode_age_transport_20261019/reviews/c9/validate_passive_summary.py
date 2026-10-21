"""Independent read-only final summary audit; no native/Rust/study replay."""
import csv
import hashlib
import json
import math
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

ROOT = Path('/workspace/scratch/36ed695112a9')
LANE = ROOT/'rei_bianchi/research/rei_age_exposure_envelope_20261018/vigilode_age_transport_20261019'
REVIEW = ROOT/'vigilode_intake_20261019/c9_review'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frac(value):
    assert math.isfinite(value)
    return Fraction.from_float(value)


def contains_exact(lo, hi, expected_lo, expected_hi):
    assert frac(lo) <= expected_lo <= expected_hi <= frac(hi)


def dec(value):
    return Decimal(value.numerator)/Decimal(value.denominator)


def main():
    core_path = REVIEW/'C9_CORE_RECEIPT.json'
    if not core_path.exists():
        core_path.write_bytes((REVIEW/'C9_FINAL_RECEIPT.json').read_bytes())
    core = json.loads(core_path.read_text())
    study = json.loads((LANE/'results/STUDY.json').read_text())
    analysis = json.loads((LANE/'results/ANALYSIS.json').read_text())
    original = json.loads((LANE/'results/summary_before_passive_split/ANALYSIS.json').read_text())
    reference = json.loads((REVIEW/'DECIMAL_ACTUAL_DATA_REFERENCE.json').read_text())
    changes = {rel: sha(LANE/rel) for rel, old in core['reviewed_files_sha256'].items() if sha(LANE/rel) != old}
    assert set(changes) <= {'summarize.py', 'README.md', 'THEORY_KO.md'}, changes
    assert sha(LANE/'results/STUDY.json') == core['reviewed_files_sha256']['results/STUDY.json'] == analysis['study_sha256']
    assert sha(LANE/'inputs/nodes.csv') == core['reviewed_files_sha256']['inputs/nodes.csv'] == analysis['coefficient_csv_sha256']
    assert (LANE/'results/BOUNDS.csv').read_bytes() == (LANE/'results/summary_before_passive_split/BOUNDS.csv').read_bytes()
    assert analysis['paired_bounds'] == original['paired_bounds']
    for new, old in zip(analysis['cases'], original['cases']):
        assert all(new[key] == value for key, value in old.items())
    rows = list(csv.DictReader((LANE/'inputs/nodes.csv').open()))
    passive_rows = [r for r in rows if all(float(r[f'lambda{k}']) == 0 for k in range(3))]
    assert len(passive_rows) == 4096 and len(rows) == 57344
    p = sum((frac(float(r['mass'])) for r in passive_rows), Fraction())
    expected_p = Fraction(2567757288181244159093,19807040628566084398385987584)
    assert p == expected_p
    reported_p = analysis['passive_N_exact_dyadic']
    assert Fraction(int(reported_p['numerator']), int(reported_p['denominator'])) == p
    contains_exact(*reported_p['interval'], p, p)
    n64_interval = [frac(v) for v in study['cases'][-1]['N']]
    sensitive64 = [v-p for v in n64_interval]
    assert sensitive64[0] > 0
    contains_exact(*analysis['sensitive_N_reference64_interval'], *sensitive64)
    assert [x['birth_groups'] for x in analysis['cases']] == [8,16,32,64]
    checks = []
    with localcontext() as ctx:
        ctx.prec = 100
        p_decimal = dec(p)
        n64_decimal = Decimal(reference['cases'][-1]['values_decimal100']['N'])
        s64_decimal = n64_decimal-p_decimal
        for case, source, independent in zip(analysis['cases'], study['cases'], reference['cases']):
            groups = case['birth_groups']
            assert source['birth_groups'] == independent['birth_groups'] == groups
            sensitive = [frac(v)-p for v in source['N']]
            assert sensitive[0] > 0
            contains_exact(case['passive_N_lower'],case['passive_N_upper'],p,p)
            contains_exact(case['sensitive_N_lower'],case['sensitive_N_upper'],*sensitive)
            if groups == 64:
                diff = [Fraction(),Fraction()]
                ratios = diff
                assert case['sensitive_N_relative_difference_vs64_lower'] == case['sensitive_N_relative_difference_vs64_upper'] == 0
            else:
                diff = [frac(source['N'][0])-n64_interval[1], frac(source['N'][1])-n64_interval[0]]
                ratios = [x/y for x in diff for y in sensitive64]
            contains_exact(case['sensitive_N_signed_difference_vs64_lower'],case['sensitive_N_signed_difference_vs64_upper'],min(diff),max(diff))
            contains_exact(case['sensitive_N_relative_difference_vs64_lower'],case['sensitive_N_relative_difference_vs64_upper'],min(ratios),max(ratios))
            n_decimal = Decimal(independent['values_decimal100']['N'])
            s_decimal = n_decimal-p_decimal
            r_decimal = (s_decimal-s64_decimal)/s64_decimal
            assert Decimal.from_float(case['sensitive_N_lower']) <= s_decimal <= Decimal.from_float(case['sensitive_N_upper'])
            assert Decimal.from_float(case['sensitive_N_relative_difference_vs64_lower']) <= r_decimal <= Decimal.from_float(case['sensitive_N_relative_difference_vs64_upper'])
            assert case['sensitive_reference_denominator_strictly_positive'] is True
            checks.append({'birth_groups':groups,'sensitive_N_decimal100':str(s_decimal),'sensitive_relative_difference_decimal100':str(r_decimal),'total_relative_difference_decimal100':str((n_decimal-n64_decimal)/n64_decimal),'exact_fraction_interval_checks':'PASS','independent_decimal_reference_enclosed':True})
        archived = analysis['archived_native_endpoint']['N']
        native_ratio = n64_decimal/Decimal.from_float(archived)
        passive_fraction = p_decimal/n64_decimal
        sensitive_native_ratio = s64_decimal/Decimal.from_float(archived)
    csv_rows = list(csv.DictReader((LANE/'results/CASES.csv').open()))
    assert len(csv_rows) == 4
    for csvrow, case in zip(csv_rows,analysis['cases']):
        assert set(csvrow) == set(case)
        for key,value in case.items():
            assert (csvrow[key] == str(value)) if isinstance(value,bool) else (float(csvrow[key]) == value)
    assert analysis['PRODUCTION_SCIENTIFIC_ADMISSION'] == 'NOT_ISSUED'
    assert analysis['reaggregation_only_no_native_or_rust_execution'] is True
    out={'status':'PASS_FINAL_PASSIVE_SENSITIVE_SUMMARY','method':'Exact Fraction endpoint/corner checks plus independent previously computed Decimal100 actual-model reference; no exponential/native/Rust execution.','passive_exact':{'numerator':str(p.numerator),'denominator':str(p.denominator),'decimal100':str(p_decimal),'nodes':4096},'reference_sensitive_denominator_strictly_positive':True,'cases':checks,'frozen_age64_total_over_archived_native_N_decimal100':str(native_ratio),'frozen_age64_sensitive_over_archived_native_N_decimal100':str(sensitive_native_ratio),'passive_fraction_of_frozen_age64_N_decimal100':str(passive_fraction),'native_comparison_scope':'Diagnostic numerical ratios only; neither total nor sensitive subset is a native trajectory closeness certificate.','study_sha256_unchanged':sha(LANE/'results/STUDY.json'),'coefficient_sha256_unchanged':sha(LANE/'inputs/nodes.csv'),'original_case_fields_unchanged':True,'original_paired_bounds_unchanged':True,'original_BOUNDS_csv_unchanged':True,'CASES_csv_matches_analysis':True,'summary_source_changed_since_core':changes,'reviewed_summary_files_sha256':{rel:sha(LANE/rel) for rel in ['summarize.py','README.md','THEORY_KO.md','results/ANALYSIS.json','results/CASES.csv','results/BOUNDS.csv','results/summary_before_passive_split/ANALYSIS.json','results/summary_before_passive_split/CASES.csv','results/summary_before_passive_split/BOUNDS.csv']},'new_native_exports':0,'new_nonlinear_campaigns':0,'new_Rust_study_runs':0,'PRODUCTION_SCIENTIFIC_ADMISSION':'NOT_ISSUED'}
    (REVIEW/'PASSIVE_SUMMARY_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
    final=core.copy()
    final['reviewed_files_sha256']=dict(core['reviewed_files_sha256'])
    final['reviewed_files_sha256'].update(out['reviewed_summary_files_sha256'])
    final['passive_summary_audit_sha256']=sha(REVIEW/'PASSIVE_SUMMARY_AUDIT.json')
    final['passive_exact_identity_sha256']=sha(REVIEW/'PASSIVE_EXACT_IDENTITY.json')
    final['passive_summary_audit_status']=out['status']
    final['passive_summary_cases_checked']=4
    final['passive_mass_normalization_disclosure']='CLOSED: exact invariant passive mass and strictly-positive sensitive denominator are now reported. Large sensitive birth-clock response is explicit; no native trajectory closeness assertion.'
    final['core_receipt_sha256']=sha(core_path)
    final['independent_review_artifacts_sha256']={p.name:sha(p) for p in REVIEW.iterdir() if p.is_file() and p.name not in {'C9_FINAL_RECEIPT.json','C9_REVIEW_REPORT.md'}}
    (REVIEW/'C9_FINAL_RECEIPT.json').write_text(json.dumps(final,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'cases':checks,'frozen_total_over_native':str(native_ratio),'frozen_sensitive_over_native':str(sensitive_native_ratio),'passive_fraction':str(passive_fraction),'changed_files_since_core':list(changes)},indent=2))

if __name__ == '__main__':
    main()
