#!/usr/bin/env python3
"""Finalize recovered theory documents from completed evidence only.

This is document/receipt assembly, with no additional numerical integration.
It requires the fixed nine-case runner to have completed successfully.
"""
from __future__ import annotations
import argparse
import csv
import datetime
import json
import re
from pathlib import Path
from independent_birth_reference import sha


def read(path):return json.loads(path.read_text())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--theory',type=Path,required=True)
    ap.add_argument('--matrix',type=Path,required=True)
    ap.add_argument('--source-identity',type=Path,required=True)
    ap.add_argument('--author-verification',type=Path,required=True)
    ap.add_argument('--fresh-verification',type=Path,required=True)
    ap.add_argument('--fresh-addendum',type=Path,required=True)
    ap.add_argument('--c9-review',type=Path,required=True)
    args=ap.parse_args();b=args.theory
    aggregate_path=b/'evidence/rust_comparison_r1_final/RUST_INDEPENDENT_COMPARISONS.json'
    aggregate=read(aggregate_path);matrix_path=args.matrix/'MATRIX_EXECUTION.json';matrix=read(matrix_path)
    if aggregate['completed_case_count']!=9 or aggregate['pending_cases'] or aggregate['failed_or_refused_cases']:
        raise ValueError('all nine fresh case comparisons required')
    if matrix['completed_programs']!=9 or not matrix['binary_unchanged'] or not matrix['source_identity_unchanged']:
        raise ValueError('completed unchanged-source matrix required')
    identity=read(args.source_identity)
    if sha(args.source_identity)!=aggregate['source_identity']['sha256']:raise ValueError('final source identity mismatch')
    runs={r['label']:r for r in aggregate['runs']}
    low=runs['gauss_r1_d8_m4_o8_e16'];high=runs['gauss_r1_d8_m8_o8_e16']
    split=aggregate['split_representation_comparisons'][0]
    diag=[]
    for r in aggregate['completed_cases']:
        directory=args.matrix/r['label']/'data'
        with (directory/'SUMMARY.csv').open() as stream:summary=next(csv.DictReader(stream))
        path=directory/'DIAGNOSTICS.json';d=read(path)
        diag.append({'case':r['label'],'summary_sha256':sha(directory/'SUMMARY.csv'),
                     'diagnostics_sha256':sha(path),'threshold_crossings':int(summary['threshold_crossings']),**d})
    diagnostic_path=b/'evidence/PHYSICAL_DIAGNOSTICS_FINAL_R1.json'
    diagnostic_path.write_text(json.dumps({'revision':'BR06_THEORY_RECOVERY_R1','historical_pass_inherited':False,
      'status':'READBACK_OF_FINAL_FRESH_MATRIX','no_new_physics_execution':True,'rows':diag,
      'scope':'Original384-label cases have zero threshold crossings; split1176-label case has144 actual recorded crossings. The spectral representation shift therefore also samples near-edge rays. Manufactured24ray controls and spectral shift have different scopes.'},indent=2)+'\n')
    bound_paths={'source_identity':args.source_identity,'author_verification':args.author_verification,
        'fresh_restore_verification':args.fresh_verification,'fresh_restore_addendum':args.fresh_addendum,
        'independent_C9_review':args.c9_review,'matrix_execution':matrix_path}
    bindings={k:{'path':str(p),'sha256':sha(p)} for k,p in bound_paths.items()}
    (b/'evidence/FINAL_UPSTREAM_VERIFICATION_BINDINGS.json').write_text(json.dumps({
       'revision':'BR06_THEORY_RECOVERY_R1','historical_pass_inherited':False,
       'status':'FRESH_EVIDENCE_BOUND_BY_HASH','bindings':bindings,
       'source_recovery_scope':identity['scope'],'binary':identity['binary'],
       'fresh_restore_scope':'New Cargo home/target, unchanged parent233tests, BR06 sixteen tests, both strict Clippy gates, eight-template exact-prefix replay and independent64/128 result-field replay. Replay uses exact step1 CSV subsets; hashes differ from full original BR05 CSVs.',
       'no_new_physics_execution':True},indent=2)+'\n')
    old_science_path=b/'evidence/SCIENCE_RESULTS_RECOVERY_R1.json';science=read(old_science_path)
    science.update({'status':'COMPLETE_SCOPED_FROZEN_OPERATOR_REFERENCE_RECOVERY_R1',
       'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'historical_pass_inherited':False,
       'native_rust_disposition':'NINE_FRESH_DECLARED_CASES_COMPLETED_AND_INDEPENDENTLY_COMPARED',
       'comparison':{'path':str(aggregate_path),'sha256':sha(aggregate_path)},
       'completed_cases':9,'cohort_evaluations':aggregate['total_cohort_evaluations'],
       'bounded_target_dispositions':{name:r['target_disposition'] for name,r in runs.items()},
       'spectral_representation_shift':split,'final_upstream_bindings':bindings,
       'hypotheses':{
         'H1_clock_or_native_path_dominance':'NOT_SUPPORTED_FOR_RECORDED_STEP1; matched parent path count agrees3.7338e-14; actual clock intervention4.3091e-17. C0/C1/C2 shifts include source/physical changes.',
         'H2_fitted_mass_implies_age_accuracy':'REJECTED; fittedr4/r8 count targets pass but raw age1/2 targets fail.',
         'H3_positive_gauss_birth_reference':'SUPPORTED_WITHIN_THIS_FINITE_FROZEN_OPERATOR; Gauss8/16 and plus satisfy declared count/age/main-energy/q2 targets, not an arbitrary-tau AP proof.',
         'H4_threshold_dominance':'UNESTABLISHED_FOR_ORIGINAL_GRID; zero original crossings.24manufactured BASSredshift-exit controls are verified; splitgrid144crossings recorded separately.',
         'H5_work_from_small_energy_residual':'REJECTED_AS_OWN_SCALE_ACCURACY_ARGUMENT; directW and ledgerW normalized independently.'},
       'remaining_limits':['No new nonlinear H/He/D evolution','Fittedr4/r8 birth-age representation not admitted at1e-7 rawmoment target','Whole-operator rigorous interval certification absent','Ledger-derived photonW remains inaccurate relative to its own scale','Full birth/time/spectral/angular convergence not established','One-way BASS only; no Einstein backreaction','LONGSPAN_SOLUTION and FULL_EOR remain not admitted'],
       'science_assembly_script_sha256':sha(__file__)})
    science['references'].update({'final_matrix_comparison':{'path':str(aggregate_path.relative_to(b)),'sha256':sha(aggregate_path)},
       'thin_probe':{'path':'evidence/thin_probe_r1/THIN_PROBE_DECIMAL_RECOVERY_R1.json','sha256':sha(b/'evidence/thin_probe_r1/THIN_PROBE_DECIMAL_RECOVERY_R1.json')},
       'physical_diagnostics':{'path':str(diagnostic_path.relative_to(b)),'sha256':sha(diagnostic_path)}})
    old_science_path.write_text(json.dumps(science,indent=2)+'\n')
    report_path=b/'docs/REPORT_KO.md';report=report_path.read_text()
    report=report.replace('**현재 판정: 독립 기준해·스칼라 검산은 새로 실행 완료. 복구판 Rust 전체 비교와 최종 admission은 대기 중이다.**',
      '**판정: BR06 복구 R1의 동결 기체 기준해 연구 단위는 검증을 마쳤다. 새 Rust 9사례, 169,616 cohort 평가와 독립 기준해 대조가 완료됐다. 진화하는 장구간 해는 승인하지 않는다.**')
    report=report.replace('이들은 새로 계산한 원 parent 출생표의 성질이며, 아직 대기 중인 복구판 Rust matrix의 통과 수를 대신하지 않는다.',
      '이들은 새로 계산한 원 parent 출생표의 성질이며, 아래 복구판 Rust matrix와 구별해 기록한다.')
    report=report.replace('복구판 Rust 전역 실행은 새 파일 도착 후 별도로 결합한다.',
      '복구판 Rust의 아래9사례는 동일한 최종 source manifest에 묶어 별도로 검증했다.')
    report=report.replace('이것이 아직 새 Rust thin-branch 재현을 대신하지는 않는다.',
      '새로 선언한 R1 Rust thin-hazard22사례도 Decimal400과 대조해22/22통과했다.20개 thin-route의 HI absorption은 올바르게 반올림됐고, normal-route $\\tau=10^{-7}$ 두 경우는 최대2ULP차이였다. 직접 geometry work의 최대 상대오차는 $3.91659\\times10^{-16}$이다. 정확한 binary64 $h=.05$와 $E_0=100$ eV, $T=1$의 닫힌형 통제 결과다. 원 probe의 삭제된 바이트를 복원한 격자라는 주장은 하지 않는다. [새 thin probe 독립 검산](../evidence/thin_probe_r1/THIN_PROBE_DECIMAL_RECOVERY_R1.json)')
    report=report.replace('삭제 전 발견한 near-zero opacity 산술 결함과 수정은 historical failure record이다. 복구판 Rust의 원 counterexample 재실행 전까지 그것의 PASS를 계승하지 않는다.',
      '삭제 전 near-zero opacity 산술 결함의 원 실행 파일·출력은 historical record로만 남았다. 복구판의 새22사례는 최소 양의 subnormal을 포함하여 같은 결함 메커니즘을 실제 다시 검사했다. 복구 중 발견한 중복 source-label admission 결함은 추가 guard와 실제 malformed CSV 테스트로 수정했고, 유효 입력의 수치 parity를 별도로 확인했다.')
    table=['| 출생 규칙 | 생존수 상대오차 | raw age1 상대오차 | raw age2 상대오차 | 선언 목표 |',
           '|---|---:|---:|---:|---|']
    display=[('fitted_r4_m4_o8_e16','Fitted r4'),('fitted_r8_m4_o8_e16','Fitted r8'),
             ('gauss_r1_d8_m4_o8_e16','Gauss8'),('gauss_r1_d16_m4_o8_e16','Gauss16')]
    for key,label in display:
        r=runs[key];v=r['continuous_comparison']
        table.append(f"| {label} | {v['survivor_com3']['relative']:+.8e} | {v['age_sum_com_s']['relative']:+.8e} | {v['age2_sum_com_s2']['relative']:+.8e} | "+('충족' if r['target_disposition']['status']=='MEETS_BOUNDED_CONTINUOUS_REFERENCE_TARGETS' else 'age 미충족')+' |')
    q=low['continuous_comparison'];h=high['continuous_comparison']
    matched=runs['fitted_r4_m4_o8_e16']['matched_path_comparison']
    section=f'''## 7. 복구판 Rust의 정량 결과와 한계

실제9사례,169,616 cohort 평가를 완료했다. 원 분광의8사례는 독립384-label 연속 birth 기준해와 비교했고,1176-label split사례는 같은 underlying source owner의 원 분광 control에 대한 표현 변화로만 비교했다. 모든 실행의 source manifest·binary·출력 hash를 묶었다. 최종 source manifest SHA-256은 `{sha(args.source_identity)}`, binary SHA-256은 `{identity['binary']['sha256']}`이다. path core와 `tests/reference_tests.rs`는 이전V2의 정확한 바이트이고, fixture·quadrature·CLI·scalar adapter/export·manifest는 명시적으로 재구성한R1이다. 새전체 BR0616tests, strict Clippy, scoped rustfmt와 별도 fresh-restore gate는 실제 실행 기록에 따른다. [최종 실행 결합](../evidence/FINAL_UPSTREAM_VERIFICATION_BINDINGS.json)

현재 bounded 진단 목표는 생존수 상대 $10^{{-8}}$, raw age1·2 상대 $10^{{-7}}$, 주요 에너지 상대 $10^{{-8}}$, 에너지 가중 $P_2$ 절대 $10^{{-11}}$이다. 사용자 전체 우주론 해의 허용오차를 새로 정의한 수치가 아니다. 아래 표는 path slabs4, opacity degree8, event degree16을 고정했다.

{chr(10).join(table)}

fitted count의 정확도만으로 birth-age 분포를 승인할 수 없다. 반면 이 유한 opacity·기체 구간의 Gauss8/16은 선언한 count·rawage·주요에너지·각도 목표를 함께 충족했다. Gauss16의 $10^{{-13}}$ 부근 일치는 독립 기준해의 부동소수점·차수변경 규모에서 해석해야 한다. 다른 규칙을 단순 나열한 이 비교로 보편적 수렴차수를 계산하지 않는다.

최종R1 fittedr4 출생표10,560행을 그대로 고정한 독립 matched-path 계산에서 생존수 경로 상대차이는 {matched['survivor_com3']['relative']:+.6e}, rawage1은 {matched['age_sum_com_s']['relative']:+.6e}였다. 같은 행의 heat 경로 차이는 {matched['thermal_j']['relative']:+.6e}다. 출생 표현과 event/path 오차를 분리한 직접 대조이다. [최종r4 matched-path](../evidence/rust_r4_matched_final_r1/MATCHED_PATH_REFERENCE.json)

opacity degree4→8만 바꾼 r4사례에서 생존수와 heat는 기록된 정밀도에서 같았다. event degree8→16은 r4 heat 상대오차를 $1.55020\\times10^{{-8}}$에서 $2.70383\\times10^{{-9}}$로 줄였다. Gauss8 출생을 고정하고 path slabs4→8로 바꾸면 heat 상대오차는 {q['thermal_j']['relative']:+.6e}에서 {h['thermal_j']['relative']:+.6e}로, binding은 {q['chemical_j']['relative']:+.6e}에서 {h['chemical_j']['relative']:+.6e}로 줄었다.

| Gauss8 경로 | 직접 적분 $W$ 상대오차 | energy subtraction $W$ 상대오차 | 후자의 오차/source energy |
|---|---:|---:|---:|
| 4 slabs | {q['work_independent_j']['relative']:+.8e} | {q['work_ledger_j']['relative']:+.8e} | {q['work_ledger_j']['difference_over_source_energy']:+.8e} |
| 8 slabs | {h['work_independent_j']['relative']:+.8e} | {h['work_ledger_j']['relative']:+.8e} | {h['work_ledger_j']['difference_over_source_energy']:+.8e} |

source energy가 $|W_{{\\rm ref}}|$보다 약 $6.4213\\times10^5$배 크다. 따라서8slabs에서 source-energy-normalized 차이가 약 $10^{{-10}}$이어도 ledger $W$의 자체 상대오차 약 $6.84\\times10^{{-5}}$를 숨길 수 없다. 정확도와 보존은 별도 판정이며 이 한계는 남는다.

split분광은 총 방출수 상대변화 {split['fields']['born_com3']['relative']:+.6e}에서 생존수 {100*split['fields']['survivor_com3']['relative']:+.9f}%, DI사건수 {100*split['fields']['DI']['relative']:+.9f}%의 변화를 보였다. 이것은 절대오차 추정이나 분광 수렴 증명이 아니다. 원384-label grid의 crossing은0이지만, split1176-label grid에는 실제144개 threshold crossing이 기록됐다. 원 grid의 관찰을 split grid에 확대하지 않는다. [경로 flags·root 진단](../evidence/PHYSICAL_DIAGNOSTICS_FINAL_R1.json)

![Birth age and photon geometry work errors](../figures/final_r1/BR06_BIRTH_AGE_AND_WORK_R1.png)

왼쪽 그림은 count·rawage moment와 각각의 목표를, 오른쪽은 동일 Gauss8 birth에서 path slab만 바꾼 직접 $W$와 차감 $W$의 자체 상대오차를 보여 준다. source-energy-normalized 잔차는 위 표에 별도로 적었다. [벡터 SVG](../figures/final_r1/BR06_BIRTH_AGE_AND_WORK_R1.svg), [그림 데이터·해시](../figures/final_r1/FIGURE_RECEIPT_R1.json), [전체 수치 비교](../evidence/rust_comparison_r1_final/RUST_INDEPENDENT_COMPARISONS.json)

이 단위는 원 H/He/D 입력을 사용하는 동결 기체의 복사 연산자 기준해를 완성했다. 새 비선형 H/He/D 이력, full-EoR 초기조건, 보편적2차 정확도, 완전한 birth/time/spectral/angular 수렴, 양방향 Einstein feedback은 입증하지 않았다. LONGSPAN_SOLUTION의 미승인 상태도 유지한다. 다음 연구에서는 실제 진화 기체와 결합하기 전에, birth-age moment오차를 제어하는 출생 표현과 work의 수치 소유권을 별도로 다뤄야 한다.

'''
    pre,rest=report.split('## 7. ',1);_,tail=rest.split('## 8. ',1)
    report=pre+section+'## 8. '+tail
    fresh_note='''
별도 fresh restore는 빈 Cargo home·새 target에서 parent233tests와 BR0616tests, 양쪽 strict Clippy를 실제 통과했다. 원 source와 donor, 정확한 step1 CSV 부분집합으로 독립64/128 계산을 다시 실행했고 모든 result field가 기존R1계산과 binary64로 같았다. 복원한8-template Rust 출력의 BIRTHS/TEMPLATES_RESULT/PATH_FLAGS는 전체 matrix의 정확한 prefix였다. 이는 전체9사례를 fresh restore에서 다시 실행했다는 뜻이 아니다. 부분집합CSV는 원전체 BR05 CSV와 파일 hash가 다르며, 같은 step1행을 쓴다는 계약과 결과 재생을 별도로 확인했다. [fresh restore와 원본 입력의 결합](../evidence/FINAL_UPSTREAM_VERIFICATION_BINDINGS.json)

'''
    if '별도 fresh restore는 빈 Cargo home' not in report:
        report=report.replace('## 8. 재현과 문헌 근거\n\n','## 8. 재현과 문헌 근거\n\n'+fresh_note)
    report=report.replace('전체 parent archive가 `parent_archive`에 복원돼 있을 때 저장소 루트에서 실행한다. 출력 경로는 기존 evidence를 덮어쓰지 않는 새 경로로 지정한다.',
       '전달된 연구 단위의 루트에서 아래명령을 사용할 수 있다. `verify`가 준비하는 `reference_parent`는 정확한 첫단계 부분집합이다. 출력 workspace는 기존 evidence를 덮어쓰지 않는 새 절대경로로 지정한다. 아래경로는 사용자가 선택할 새 경로를 나타낸다; 이번 검증을 사용자 계산으로 위탁한 것이 아니다.')
    commands='''```bash
bash RUN_STAGE.sh verify /absolute/new/br06_verify
bash RUN_STAGE.sh matrix /absolute/new/br06_matrix
python3 scripts/independent_birth_reference.py --parent /absolute/new/br06_verify/reference_parent --orders 64:64:8,128:128:16 --output /absolute/new/independent_minus
python3 scripts/independent_birth_reference.py --parent /absolute/new/br06_verify/reference_parent --case SIGNED_PLUS --orders 64:64:8,128:128:16 --output /absolute/new/independent_plus
python3 scripts/matched_paths_r1.py --parent /absolute/new/br06_verify/reference_parent --output /absolute/new/parent_matched
python3 scripts/decimal_oracles_r1.py --output /absolute/new/scalar_controls
BR06_PARENT=/absolute/new/br06_verify/reference_parent python3 scripts/test_independent_reference.py
```'''
    report=re.sub(r'```bash\n.*?```',lambda _:commands,report,count=1,flags=re.S)
    # Navigational links use the root agent's delivered package layout.
    # Raw execution paths in JSON receipts are preserved unchanged.
    report=re.sub(r'\.\./evidence/(?!theory_r1/)', '../evidence/theory_r1/', report)
    report=report.replace('../figures/final_r1/','../figures/')
    report_path.write_text(report)
    contract=b/'docs/THEORY_CONTRACT_RECOVERY_R1.md'
    review={'revision':'BR06_THEORY_RECOVERY_R1','status':'PASS_WITH_DECLARED_BOUNDED_SCIENTIFIC_SCOPE',
       'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'historical_pass_inherited':False,
       'R8_R10_scientific_disposition':'Fresh theory, controlled numerical calculations, independent Rust comparisons, limitations and next conditions completed for the frozen operator only.',
       'independence':{'Rust_path_author':'br06_implementation','scalar_adapter_author':'vigilode_review','independent_Decimal_direct_time_reference_and_adapter_math_review':'br06_theory','separate_compiled_code_C9':'vigilode_review; own adapter mathematical review was performed by br06_theory'},
       'hypotheses':science['hypotheses'],'targets':aggregate['targets'],
       'target_dispositions':science['bounded_target_dispositions'],'remaining_limits':science['remaining_limits'],
       'inputs':bindings,'outputs':{str(p.relative_to(b)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in
           (report_path,contract,old_science_path,aggregate_path,diagnostic_path,b/'figures/final_r1/FIGURE_RECEIPT_R1.json')},
       'assembly_script_sha256':sha(__file__),'extra_science_runs_during_finalization':0,
       'overall_publication_and_DAG':'Owned by root; this receipt does not claim GitHub/Drive/Dropbox publication.'}
    out=b/'THEORY_REVIEW_FINAL.json';out.write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps({'report':str(report_path),'report_sha256':sha(report_path),'science':str(old_science_path),'science_sha256':sha(old_science_path),
                     'review':str(out),'review_sha256':sha(out),'matrix_sha256':sha(aggregate_path)}))


if __name__=='__main__':main()
