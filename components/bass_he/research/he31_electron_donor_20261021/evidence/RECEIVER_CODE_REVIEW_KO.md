# HE31 receiver·campaign·bindings 독립 코드 검토

**판정: PASS_SCOPED_READY.** 최종 source readback에서 검토 범위의 실행 차단 결함은 남아 있지 않다. 이 판정은 준비된 driver와 실행 계약에 관한 것이며, 실제 paired 결과의 과학적 판정은 별도 단계다. 리뷰어는 새 ODE, campaign, benchmark, 전체 suite 또는 worker subprocess를 실행하지 않았다.

## 최종 코드 identity

| 파일 | SHA256 |
|---|---|
| src/receiver.py | b98de4d68155c2a3a679cce3f267fe77facd4ce1ef713d366ba041427a4f7753 |
| src/campaign.py | 4808ea4474805ade3276d47535c9ad14cced09e9e64680cfbf306f0b06a785ef |
| src/bindings.py | 82d6becb04e722aa1aa62c353d93b357bc368f5421ab799dc11211655aa9adcf |
| src/electron_donor.py | 3c95da58c074f919f96477a823f8d907bb79dc4810c61e7f19bbca5becc517c6 |
| src/prepared_moments.py | ee552a09c9b10e72f82105f071af7c6f9ccfaae64407932b0844f70b1e4328ed |

원본 canonical3/clock/HE30 runner/resource source는 BASELINE_MANIFEST로 별도 검증된다. 전체 검토 항목과 hash는 RECEIVER_CODE_REVIEW.json에 있다.

## 1. 40개 물리 상태와 tau

Lmax8에서 원본 물리 상태는4+4×9=40이다. 초기 상태 뒤에 tau=0을 붙이고, 원본 RHS에는 앞40개만 전달한다. 새 성분은 Gamma_T×(H_ref/H)/H_ref=Gamma_T/H이다. tau는 원래40개 방정식으로 되먹임되지 않는다. 따라서 처방된 donor를 사용하면서 원래 Einstein/photon/neutrino 동역학을 보존한다.

광학깊이는 donor가 생성된 과거 H를 복사하지 않고 **현재 receiver의 H**로 적분한다. 같은 canonical RHS의 시간성분을 사용하므로 두 번째 moments 평가를 추가하지 않는다. photon의 energy/number multipole에만 Thomson이 적용되고 neutrino에는 적용되지 않는 원본 소유권도 유지된다.

## 2. signed axes와 정규화

Sigma_F에서 q=Sigma_F/sqrt(6-Sigma_F²)를 계산하고, 원본 Sigma_ref=Sigma_F/sqrt2를 전달한다. 이는 기존 D3의 Frobenius 정규화와 일치한다. 초기 Sigma_F>0이면 양의 shear orientation을 사용하는 D3 family이며, 이후 signed_Sigma를 별도로 보존한다.

radiation amplitude와 matter amplitude는 각각 signed P_r와 P_m에서 역산된다. matter calibration은 동일한mass30,24×12,Gauss3의 amplitude1 moment를 재사용한다. 음수 stress를 magnitude로 바꾸어 초기화하지 않는다. 저장 관측량도 P_r=P_gamma+P_nu를 먼저 합한 후 Pi_r=abs(P_r)를 취하고, Pi_total=abs(P_m+P_r)를 취한다. matter/radiation 상쇄를 잃지 않는다.

## 3. donor와 case identity

opacity=off이면 donor 파일을 읽기 전에None을 반환하고 scientific identity에도 donor_identity=None을 넣는다. 따라서 같은off물리case가 donor경로나내용만 다르다는 이유로 다른 물리가 되지 않는다.

opacity=on이면 manifest SHA, 실제 NPZ SHA와 content identity, manufactured-control의 명시적 purpose, 실제 시작/끝 support를 검사한다. actual_history 준비 단계는 manufactured 입력을 거절한다. 기존R15 z20→4 donor는 z20→2 support를 통과할 수 없다. Cache는 path+expectedmanifestSHA에 결속된 immutable donor snapshot이다.

초기 구현은 모든src와 runner/resource hashes를 scientific digest에 넣었다. 지적 후 저자가 수정했으며, 최종본은 receiver를 구성하는4개 scientificsrc와 canonical3+cosmologylock만 science digest에 포함한다. 실행 resource 파일은 계속 검증하고 결과의 execution_resource_sha256에 별도로 기록한다. plot/campaign/report 수정이 기존 물리 결과를 불필요하게 무효화하는 범위를 줄였다.

## 4. 실제 발견하여 교정된 실행 문제

### CLI 실패 exit status

초기 campaign.main은 FAILED/DEFERRED/TIMED_OUT를 포함한 report를 출력해도 implicit exit0을 반환했다. 수정된 코드는 실제run에서 COMPLETE/REUSED_COMPLETE 이외 상태가 있으면2를 반환하고, entrypoint가 raise SystemExit(main())을 사용한다. dry-plan과 successfulprepare는0이다. 이 수정은 최종 원문으로 확인했다.

### 이미 존재하는 PYTHONPATH에서의 source shadow

초기 load_model은 VENDOR가 sys.path의 뒤쪽에 이미 있어도 앞에 이동하지 않았고, import 후 경로 검사가 없었다. 따라서 다른 아직미로드 canonical모듈이 앞에 있으면 baseline파일의SHA를 확인한 뒤 다른 모듈을 import할 여지가 있었다.

최종본은 VENDOR를 index0으로 이동시키고 canonical_fv/species_hierarchy/lrs_boltzmann의 __file__를 import전후 확인한다. load_runner도 cached/신규 resource module의 경로를 확인한다. 이 조건은 source readback으로 닫았으며, root가 별도작은 fresh-process shadow 검사를 맡는다. 리뷰어가 추가 실행을 겹치지 않았다.

### donor scalar interval

uniform-loggrid floor estimate 뒤 실제 knot interval에 속하는지 확인하고, 다르면 searchsorted로 보정하는 변경도 확인했다. 거의균일한 knot 및 binary64 log 차이로 이웃 interval polynomial을 적용하는 경계를 닫는다.

### NumPy scalar의 JSON 직렬화

Root가 수행한 첫 실제 paired worker 시도 2건은 payload를 해시하기 위한 JSON 직렬화에서 NumPy boolean을 처리하지 못해 실패했다. `evidence/failed/serialization/CORRECTION.json`과 두 `WORKER_FAILURE.json`을 직접 읽어 확인했다. 완료 case receipt는 저장되지 않았으므로 이 시도를 완료된 과학 결과로 계산하지 않는다. 원래 실패 receipt와 로그는 그대로 보존되어 있다.

수정된 `run_case`는 payload SHA를 계산하기 전에 `plain(result)`를 적용한다. NumPy scalar는 `item()`, 수치 array는 `tolist()`로 변환하고 dict/list/tuple은 재귀 처리한다. 이는 현재 결과에 사용되는 수치·scalar·container 형식을 포함한다. Canonical JSON의 `allow_nan=False`는 유지되므로 비유한 값을 정상 결과로 허용하는 변경은 아니다. RHS, solver tolerance, 정규화와 통과 기준은 이 교정에서 바뀌지 않았다.

저자의 `SERIALIZATION_RECHECK.json`은 NumPy bool/float/int/array 변환에 대해 **PASS_SCOPED**, ODE 호출 **0**을 기록한다. 이 근거를 읽어 재사용했으며 리뷰어는 추가 검사를 실행하지 않았다. 최종 `receiver.py` SHA는 위 표에 갱신했고, 이전 readback SHA는 JSON의 `previous_readback`에 보존했다. `bindings.py`의 import 순서 및 import 전후 provenance 검사는 최종 원문으로 다시 확인했다.

교정 후 root가 선택한 별도 결과 경로는 `results/light_actual_pair_v2`이다. 이 경로의 실제 paired 결과 판정은 독립 결과 검토에서 수행하며, 이 코드 문서는 그 결과를 미리 통과로 표시하지 않는다.

## 5. HE30 worker와 결과 보존

HE30 coordinator의 API는 case_grid/case_identity/completed_result/write_case이며 receiver가 모두 구현한다. campaign은 api_module=receiver로 호출한다. coordinator가 receiver.__file__의 directory를 child PYTHONPATH에 넣고 --_worker-module receiver를 전달하므로 HE30 script에서 출발하는 worker도 HE31 API를 찾는다. HE31_CAMPAIGN은 절대경로로 상속된다. 한 worker당 수치thread1, CPU lease, globalcaseidentity lock을 사용한다.

completed_result는 payloadSHA, schema/identity/completedstatus/gates, finite41×121 shape, monotonic time 및 endpoint를 확인한다. 기존partial/failed/invalid 파일은 덮어쓰지 않고 보존한다. 쓰기는 replace=False atomiclink를 사용한다. 다른case가 실행중이면 해당case를 건너뛰고 가용capacity에서 나머지를 진행하는 HE30 계약도 유지된다.

**후속 plot/analysis 주의점:** globalregistry가 다른directory의 완료case를 재사용하면 새out에 중복JSON을 만들지 않는다. 따라서 RUNNER_REPORT의 statuses[case].path를 따라 읽어야 한다. 새out의 caseJSON만glob하면 올바르게 재사용된 결과가 누락될 수 있다. 이 점은 root에 전달했다.

## 6. 이미 존재하는 검사 증거의 재사용

초기 CONTRACT_CHECKS.json은8개검사 중1failure를 그대로 보존하고 있다. 이를8개모두통과로 바꾸어 서술하지 않는다. 저자가 binary64 roundoff criterion을 문서화해 교정한 뒤 affected target-clock check만 다시 실행했고, TARGET_CLOCK_RECHECK.json은1개검사통과다.

해당 receipt의 수치는 gamma-only RHS 최대차1.0842021724855044e-19, augmented RHS당 moments call1, tau RHS 상대차1.1102230246251565e-16이다. 이 기록을 읽어 재사용했으며 reviewer는 과학 계산을 반복하지 않았다. 독립prepared-moment review는 PREPARED_INDEPENDENT_REVIEW.json에 별도로 있다.

## 결론의 범위

준비된 driver·identity·worker·보존계약은 검토 범위에서 적합하다. 실제 확보된R15 donor는z20→4 조건부 Q/HeII closure이며, 이번 코드검토는 fullH/He chemistry 또는z20→2donor 완료를 승인하지 않는다. 직렬화 교정 후 root가 수행하는 작은 actual on/off paired 실행 결과도 이 문서에서 미리 과학 판정하지 않는다. 속도배수나 전체RSS를 측정하지 않았다.

