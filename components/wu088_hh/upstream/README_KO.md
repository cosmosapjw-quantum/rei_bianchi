# WU088_HH 현재 결과: PHYS19 순수 매개변수 곡률

[PHYS19 draft PR54](https://github.com/cosmosapjw-quantum/WU088_HH/pull/54) · [완료된 게시·백업 영수증](research/r31ao_unequal_ladder/hh_phys19_parameter_curvature_theory_20261013_v1/publication/PUBLICATION.json)


같은 COMMON에서 출발한 two-half minus Full 온도 결함의 순수 곡률 application을 원 저장 입력으로 완료했다. 독립 과학 검토 **pass_scoped**를 거쳐 **PROMOTE_SCOPED**로 채택했다. 현재 채택 이론과 과학 기준점은 PHYS19다.

보통 두 번째 도함수는 **F_lambda_lambda ∈ [-4.510292217171e-14, -3.084478303660e-14] K**, **F_b_b ∈ [-4.912098573204e-11, -4.450662359403e-11] K**다. 두 좌표축 응답은 모두 엄격히 오목하다. 확립된 음의 mixed response를 결합하면 Hessian은 indefinite이며, 고정 방향 (1,-1/24)에서는 양의 곡률, lambda축에서는 음의 곡률을 갖는다.

단위 사각형 전체의 bilinear interpolation remainder는 **6.145761081776e-12 K 이하**다. 정확한 pure-curvature midpoint를 사용해 보정하면 **2.892887673208e-13 K 이하**로 줄어든다. 두 표현은 정확한 같은-family corner coefficients와 그 결박 관계를 유지한다. 절대 anchor와 chord 계수의 불확실성까지 포함한 구체적 고정 계수 모델의 전체 오차는 **0.0001557338140092 K 이하**다. PHYS18의 mixed derivative와 네 모서리 interaction은 확립된 입력으로 재사용했다.

[연구 개요](research/r31ao_unequal_ladder/hh_phys19_parameter_curvature_theory_20261013_v1/README_KO.md), [실제 application](research/r31ao_unequal_ladder/hh_phys19_parameter_curvature_theory_20261013_v1/checks/application/run01/results/SUMMARY.json), [곡률·오차 readout](research/r31ao_unequal_ladder/hh_phys19_parameter_curvature_theory_20261013_v1/checks/application/readout02/results/SUMMARY.json), [판정 기록](research/r31ao_unequal_ladder/hh_phys19_parameter_curvature_theory_20261013_v1/review/DECISION.json), [다음 DAG](research/r31ao_unequal_ladder/hh_phys19_parameter_curvature_theory_20261013_v1/NEXT_DAG.json)를 참조한다. 독립 Fraction 심사는 **362/362개 검사**를 통과했다. 구간 대조 265개로 scalar 포함 2,057개를 비교했고, 바깥 방향 decimal 3,174개와 계약 결박 23개를 검증했다. 실제 Wolfram/xAct는 tensor 6개·scalar 13개·matrix component 14개에서 정확한 0을, Peano 관련 조건 4개에서 True를 반환했다. 실행 기록에는 과학 application 1회, 독립 심사 성공 1회와 보존한 checker-only 실패 2회, geometry readout 2회, Wolfram 2회를 구별해 기록했다.

**다음 단위 PHYS20은 실제 이름을 가진 rei_bianchi consumer interval을 찾아 결박한다.** 그 입력에서 `HH_DOMAIN_SCREEN`과 `HH_MATERIALITY`를 수행하고 순간 `dotT_HH` 및 HH 전자 source table을 제공한다. 현재 consumer binding은 **UNVERIFIED**다. 원 RUX DAG와 독립 `HH_STRICT_NATIVE`·`HH_SINGLET` 경로는 기존 범위를 유지한다.

## PHYS18과 이전 연구 개요 보존

# WU088_HH 현재 결과: PHYS18

같은 COMMON과 공유 전역 HH·birth 매개변수에서 실제 endpoint 결함의 혼합 응답을 유도·계산했다. 독립 판정은 **PROMOTE_SCOPED**, 이론 정리 **8개**, 따름정리 **4개**, 별도 exact Fraction 산술은 **22/22 PASS**다.

온도 결함의 혼합 미분과 네 모서리 interaction은 모두 **[-2.668505746423E-12, -2.118796636045E-12] K**에 포함된다. 원 C2 Hessian과 U/V/W carry에서 직접식·상관식을 구성했고, 같은 Full inverse와 온도 covector에서 HH gradient의 음의 기여가 가장 크다는 것을 확인했다. 실제 Wolfram/xAct의 7개 tensor·14개 scalar component 검산은 모두 정확히 0이다.

모든 양의 면적 subrectangle의 interaction이 음수이며 HH·birth marginal response의 정렬이 결정된다. 축 응답을 그대로 보존하면 교차항 -2.393651191234e-12*lambda*b K의 잔여 오차는 2.748545551890e-13*lambda*b K 이하이다.

[연구 개요](research/r31ao_unequal_ladder/hh_phys18_mixed_response_theory_20261013_v1/README_KO.md), [PDF 보고서](research/r31ao_unequal_ladder/hh_phys18_mixed_response_theory_20261013_v1/report/WU088_HH_PHYS18_THEORY_20261013.pdf), [채택 기록](research/r31ao_unequal_ladder/hh_phys18_mixed_response_theory_20261013_v1/review/DECISION.json), [다음 DAG](research/r31ao_unequal_ladder/hh_phys18_mixed_response_theory_20261013_v1/NEXT_DAG.json)를 참조한다. 다음은 [HH_DEFECT_PARAMETER_CURVATURE](research/r31ao_unequal_ladder/hh_phys18_mixed_response_theory_20261013_v1/contracts/CURVATURE_CONTRACT.json)에서 두 pure curvature와 bilinear 재구성 오차를 계산하는 일이다. 첫 half의 선형 inverse 준비는 완료했으며 새 pure response application은 not_run이다. 원 source·root·history 재실행 및 NCP launch는 모두 0회다.

## 이전 연구 개요 보존

# WU088_HH 현재 결과: PHYS17

같은 COMMON과 공유 전역 매개변수에서 실제 endpoint 결함의 1차 응답을 유도·계산했다. 독립 판정은 **PROMOTE_SCOPED**, 별도 Fraction 산술은 **29/29 PASS**다.

온도 결함의 lambda 미분은 **[-1.009599125635e-8, -8.137506081166e-9] K**, b 미분은 **[6.776348385589e-5, 7.185335549648e-5] K**다. 원 C2 nonphoto Jet에서 He 열원 도함수를 직접 구성하여 density pullback을 닫았다. 같은 Full inverse와 온도 covector에서 lambda의 직접·feedback 기여는 모두 음수, b의 직접 기여는 양수이고 feedback은 작은 음수다.

[연구 개요](research/r31ao_unequal_ladder/hh_phys17_defect_parameter_response_theory_20261013_v1/README_KO.md), [19쪽 PDF](research/r31ao_unequal_ladder/hh_phys17_defect_parameter_response_theory_20261013_v1/report/WU088_HH_PHYS17_THEORY_20261013.pdf), [채택 기록](research/r31ao_unequal_ladder/hh_phys17_defect_parameter_response_theory_20261013_v1/review/DECISION.json), [다음 DAG](research/r31ao_unequal_ladder/hh_phys17_defect_parameter_response_theory_20261013_v1/NEXT_DAG.json)를 참조한다. 다음은 기존 mixed carry와 C2 Hessian을 사용하는 HH_DEFECT_MIXED_RESPONSE이며, 네 모서리 HH/birth contrast의 현재 상한은 1.958485175177039e-9 K다. 원 source·root·history 재실행 및 NCP launch는 모두 0회다.

## 이전 연구 개요 보존

# WU088_HH 현재 결과: PHYS16

같은 COMMON에서 출발한 실제 두 half와 Full의 상관 endpoint 차이를 계산하고 C² endpoint remainder 및 공통 adjoint 정리를 완성했다. 독립 판정은 **PROMOTE_SCOPED**이며 적용 범위는 기존 source-aligned geometric-isotropic 계열과 동일한 전역 lambda,b다.

온도 차이 T₂−T_F는 **[-0.001585967387181453, -0.001210819969055199] K**다. 이온화 H·전자 수는 증가하고 열에너지·잔존 광자 수와 에너지는 감소한다. b>0에서 birth redshift의 온도 기여는 음수, birth backward Euler는 양수이며, 두 부호는 같은 기체의 암시적 응답을 포함한다.

[연구 개요](research/r31ao_unequal_ladder/hh_phys16_endpoint_remainder_theory_20261013_v1/README_KO.md), [PDF 보고서](research/r31ao_unequal_ladder/hh_phys16_endpoint_remainder_theory_20261013_v1/report/WU088_HH_PHYS16_THEORY_20261013.pdf), [독립 판정](research/r31ao_unequal_ladder/hh_phys16_endpoint_remainder_theory_20261013_v1/review/DECISION.json), [다음 DAG](research/r31ao_unequal_ladder/hh_phys16_endpoint_remainder_theory_20261013_v1/NEXT_DAG.json)를 참조한다. 다음 이론 단위는 원 mixed Hessian과 U/V carry를 이용한 HH_DEFECT_PARAMETER_RESPONSE다. 현재 단계의 원 source·root·history 재실행 및 NCP launch는 모두 0회다.

## 이전 연구 개요 보존

# WU088_HH 최신 연구: PHYS15 상관된 endpoint 결함 이론

PHYS15는 같은 COMMON에서 출발한 Full과 PHYS14의 실제 two-half 경로를 하나의 잔차로 연결한다. 기체 잔차, 광자 흡수 결함의 일곱 항과 원 격자의 부호 관계, 밀도·fhat source 정규화 연결, 유한 온도 차이와 공통 adjoint 기여를 유도했다. 원 Full의 fixed_C·B·radius·q=0.00011736830563768177을 함께 재사용해 전처리 잔차에서 endpoint 차이로 가는 포함식을 구성했다.

**현재 상태:** 독립 검토에서 이론 주장 9개를 PROMOTE_SCOPED로 채택했고 남은 차단 지적은 0개다. 현재 채택된 이론은 PHYS15이며, PHYS14는 재사용하는 물리 계산 기준점으로 유지한다. 이 이론 단위의 새 원자 source 평가, 물리적 root solve와 물리 history 실행은 모두 0회다.

- [PHYS15 상세 유도](research/r31ao_unequal_ladder/hh_phys15_correlated_endpoint_theory_20261013_v1/theory/CORRELATED_ENDPOINT_THEORY_KO.md)
- [현재 개발계획](CURRENT_DEVELOPMENT_PLAN.json)
- [독립 판정](research/r31ao_unequal_ladder/hh_phys15_correlated_endpoint_theory_20261013_v1/review/DECISION.json)
- [endpoint 포함 계산 계약](research/r31ao_unequal_ladder/hh_phys15_correlated_endpoint_theory_20261013_v1/contracts/ENDPOINT_ENCLOSURE_CONTRACT.json)
- 다음 계산: **HH_CORRELATED_ENDPOINT_ENCLOSURE**. 같은 입력의 상관관계를 유지해 잔차, 기체·광자 endpoint 차이, ΔT/e/w/ne와 공통 inverse를 거친 항별 기여를 포함한다.

정식 보고서와 최종 전달 기록은 현재 마무리 중이다.

현재 운영 규약은 physmath-research-loop built-in 1.0.0의 THEORY R1–R10이다. 기존 과학 원본과 source·C²·근 전제를 재사용하고, PR49 위에 연구 브랜치를 추가하는 방식으로 게시한다. 원 전역 REI DAG와 기존 연구 기록은 각 시점의 근거로 보존한다.

## 보존된 PHYS14 및 이전 안내

# WU088_HH 최신 연구: PHYS14 공동 carry의 두 번째 half

PHYS14를 독립 검토 후 PROMOTE_SCOPED로 채택했다. 같은 COMMON과 전역 λ,b를 유지한 실제 두-half 계열에서 새 두 번째 implicit 단계의 유일 근과 일차·혼합·유한 온도·전자 응답을 포함했다. 유한 HH 온도 응답은 [-18.93685,-9.75153] μK, mixed 온도 interaction은 [1.96632,3.44806] pK다. 첫 half의 광자 기억은 열에너지를 늘리면서 온도를 추가로 낮춘다.

원 등방 기하학에서 gas4+group33+guard2의 정확한39-state closure와 원 비균일격자의 R(rho)^2−R(rho²) 차이식을 얻었다. 기존 Full nonphoto/q source와 첫-half carry를 재사용했고 새 암시적 stage한개가첫실행에통과했다.

- 보고서: [research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/REPORT_KO.md](research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/REPORT_KO.md)
- LaTeX/PDF: [research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/report/](research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/report/)
- 결과와독립판정: [research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/results/advance01/](research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/results/advance01/), [research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/review/DECISION.json](research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/review/DECISION.json)
- 다음연구: [research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/HANDOFF_KO.md](research/r31ao_unequal_ladder/hh_phys14_carried_second_half_20261012_v1/HANDOFF_KO.md), 같은COMMON의Full대실제two-half endpoint결함을상관된잔차차이로포함

원 source/C2 첫단계 전제와 geometric subfamily scope를 함께읽는다. 기존전역DAG와9개HHnodes를보존하고provider결과와구체적후속작업만추가했다. 과학원본과완료실행을기본적으로반복하지않는다.

## 보존된 PHYS13 및 이전 안내

# WU088_HH — PHYS13 유한 온도·전자 응답

PHYS13에서 같은 source family의 HH 온도·전자 응답과 냉각 원인을 계산했다. [연구보고서](research/r31ao_unequal_ladder/hh_phys13_thermodynamic_response_20261012_v1/REPORT_KO.md), [상세 유도](research/r31ao_unequal_ladder/hh_phys13_thermodynamic_response_20261012_v1/theory/THERMODYNAMIC_RESPONSE_THEOREM_KO.md), [정확한 결과](research/r31ao_unequal_ladder/hh_phys13_thermodynamic_response_20261012_v1/results/thermo_v2/THERMO_RESULTS.json), [독립 판정](research/r31ao_unequal_ladder/hh_phys13_thermodynamic_response_20261012_v1/review/DECISION.json)을 참조한다.

Full 첫 단계에서 HH ΔT는 [-2.283422272e-5,-7.460984727e-6] K이며, 선택한 HH 강도 경로의 냉각 중 입자 수 증가 비중은 [31.67901824,31.98634497]%다. 같은 계열의 추가 birth는 열에너지를 늘리면서 온도를 낮춘다. 새 전자당 순 열에너지 증가가 기존 입자당 평균 열에너지보다 작기 때문이다.

이 결과는 상속한 source/C² root 조건 아래 PROMOTE_SCOPED다. Full과 first_half는 같은 COMMON에서 따로 출발하며, 실제 소비자 적용성이나 전체 시간 이력을 새로 인증하지 않는다. 새 source/native/root 호출과 NCP 작업은 0이다.

현재 진입점은 [CURRENT_DEVELOPMENT_PLAN.json](CURRENT_DEVELOPMENT_PLAN.json), [DAG](research/r31ao_unequal_ladder/hh_phys13_thermodynamic_response_20261012_v1/NEXT_DAG.json), [후속 인계](research/r31ao_unequal_ladder/hh_phys13_thermodynamic_response_20261012_v1/HANDOFF_KO.md), [제공 계약](research/r31ao_unequal_ladder/hh_phys13_thermodynamic_response_20261012_v1/contracts/HH_THERMODYNAMIC_RESPONSE_EXPORT.json)이다. 기존 atomic/native 연구 및 PHYS12 결과를 보존한다.

## 이전 계획·native 사용 안내의 보존

아래 원문은 이전 계획과 각 native lane의 보존 기록이며, 현재 다음 작업은 위 PHYS13 인계를 따른다.

# WU088_HH — HH Atomic-Reuse 연구계획 v2 (2026-10-12)

첨부 REI Atomic-Reuse DAG의 17개 노드를 [새 연구계획](research/r31ao_unequal_ladder/hh_atomic_reuse_plan_20261012_v2/DEVELOPMENT_PLAN_KO.md)과 [HH 로컬 DAG](research/r31ao_unequal_ladder/hh_atomic_reuse_plan_20261012_v2/NEXT_DAG.json)의 8개 작업에 대응시켰다. 현재 진입점은 [CURRENT_DEVELOPMENT_PLAN.json](CURRENT_DEVELOPMENT_PLAN.json), [제공 계약](research/r31ao_unequal_ladder/hh_atomic_reuse_plan_20261012_v2/contracts/HH_REI_EXPORT_CONTRACT.json), [후속 인계문](research/r31ao_unequal_ladder/hh_atomic_reuse_plan_20261012_v2/HANDOFF_KO.md)이다.

과학 기준점은 [PHYS12 보고서](research/r31ao_unequal_ladder/hh_phys12_absolute_response_20261012_v1/REPORT_KO.md)와 기존 PROMOTE_SCOPED 판정이다. PHYS12를 S14_PHYS12로 등록하고 원 첨부와 기존 과학 파일을 보존했다. 이번 변경은 계획과 계약 작성이며 새 과학 실행·외부 RUX 완료를 뜻하지 않는다.

실제 소비자의 소스 계열·시나리오·적용영역이 주어지면 HH_DOMAIN_SCREEN부터 진행한다. 제공 계약과 적용성·관측량 screening은 RUX11 전에 준비할 수 있다. 실제 EoR HH ON/OFF 이력 비교는 RUX11 증거를 요구하며 같은 조건의 보존 이력은 재사용한다. 기본 REI 이력은 선택 HH 정밀 계산을 기다리지 않는다. 독립 singlet 충돌·FT03 strict-native 연구에는 각각의 원래 승인 조건을 적용한다.

**NCP heavy_queue=[] / launch=false / NO_HEAVY_JOB_READY.** [경로별 NCP 정책](research/r31ao_unequal_ladder/hh_atomic_reuse_plan_20261012_v2/NCP_TASKS.json)을 따른다. 현재 소비 runtime은 결박되지 않았고 새 HH rate table·전체 우주론 이력·production 판정은 없다. 완료된 과학 계산이나 빈 큐 benchmark를 자동 재실행하지 않는다.

## 아래 문서의 범위: 보존된 R31K-B/R31M native 안내

아래 원문은 해당 과거 native 작업의 절차로 보존한다. 아래의 ‘현재 릴리스’·‘다음 benchmark’는 그 시점의 설명이며 현재 root 계획을 대체하지 않는다. Git fetch/pull 직후 자동 benchmark를 실행하라는 현재 지시가 아니다.

# WU088_HH

Frozen107 두 전자 H-H 연구의 source-bound 계산·성능 진단 저장소. 현재 릴리스는 **R31K-B 연구 결과와 검증된 범위의 최적화 후보**이며 완성된 scattering/production solver가 아니다.

다섯 anchor의 H order-comparison은 통과했다. full49는 새 z의 독립 dotO/ionic 입력이 필요하다. 상세 판정: `docs/research/RESULTS_KO.md`, 유도: `docs/research/MATHEMATICS.md`, 검증: `evidence/FINAL_VERIFICATION.json`.

## 기존 runtime을 유지한다

이 저장소는 현재 설치한 runtime을 삭제·교체하지 않는 overlay다. `native/reference`와 `vendor/orchestration`은 회수한 원본 bytes를 보존한다. 완성된 1,440개 pair는 다시 계산하지 않는다. 저장소의 raw ASSEMBLED 배열과 identity/event 자료로 가벼운 수렴·성능 분석을 재현할 수 있다. 전체 pair ZIP은 원래 Drive/Dropbox 백업에 남아 있다.

Local scientific runtime 기본 위치:

```bash
export WORK=/mnt/sn850x2t/hh_heavy_manual_20260926
export RUNTIME="$WORK/runtime/WU088_HH_LOCAL_RUNTIME_SEED_20260926_v2"
source "$WORK/venv/bin/activate"
```

## R31M topology-aware host autotune

저장소 root에서:

```bash
bash scripts/benchmark_host.sh
```

실제 affinity/core/SMT/L3 topology와 quota/memory를 기록하고, 동일 frozen107의 B32/g80 component에서 physical-core 및 SMT process/thread 조합을 비교한다. 각 worker는 disjoint CPU set에 pin한다. 결과는 `$WORK/wu088_hh_bench_<UTC>_<pid>/`에 쓰며 `HOST_TUNING_PROFILE.json`까지 생성한다. 기존 pair를 덮어쓰거나 candidate `.so`를 runtime에 설치하지 않는다. 상세 계약은 `docs/coding/R31M_HOST_AUTOTUNE.md`를 참조한다.

튜닝 profile 생성 뒤 native candidate의 science-resolution exactness는 별도 `scripts/representative_native_regression.py`로 확인한다. 이 gate도 production provider를 자동 승격하지 않는다.

## 여기서 이미 실행한 가벼운 분석의 재현

```bash
python scripts/analyze_anchors.py --out local_runs/anchor_h.json
python scripts/analyze_costs.py --out local_runs/scheduling.json
python -m pytest -q
```

같은 output 파일은 덮어쓰지 않는다. 재현이 필요한 경우에만 새 경로를 지정한다. 기존 과학 full suite를 반복 실행하는 명령은 아니다.

## 후속 승인된 H wave에 적용할 scheduler

**지금 midpoint/propagation을 시작하라는 명령이 아니다.** 먼저 새 anchor의 독립 입력 및 full49 gate를 닫아야 한다. 허가된 새 wave를 실행할 때의 진입점은 `scripts/wide_hybrid_orchestrator_cost.py`다. 기존 frozen kernel을 쓰며 별도의 new native candidate는 자동 적용하지 않는다.

```bash
export R31K_RUNTIME_ROOT="$RUNTIME"
python scripts/wide_hybrid_orchestrator_cost.py \
  --n 160 --g 80 --z 16 --gamma-scale unit \
  --workers 12 --max-new-pairs 12 --max-wall-seconds 300 \
  --execution-lane local \
  --legacy-runner vendor/orchestration/r31k_generic_local_adapter.py
```

위 z16 state가 이미 완료되고 동일 identity라면 `SOURCE_COMPLETE_REUSED_NOT_REASSEMBLED`로 반환한다. 다른 compiler/native identity가 발견되면 섞어서 재개하지 않고 중단한다. pending delta가 있으면 return code74로 먼저 백업을 요구한다. 실제 시간 제한은 in-flight wave의 안전 경계에서 작동하며 300초 hard kill이 아니다.

Pending delta helper:

```bash
python scripts/backup_pending.py \
  --folder "$RUNTIME/completion/mixed_h/wide_hybrid12/B160_g80_sunit_z4030000000000000" \
  --drive gdrv: --dropbox dbx: \
  --receipts "$WORK/wu088_hh_backup_receipts"
```

여기서 drive/dropbox 이름은 사용자가 이미 구성한 raw rclone remote다. 두 provider를 병렬 전송하되 모두 raw SHA/size readback을 통과해야 원래 ACK contract를 호출한다. 새 계산과 백업을 겹치지 않는다. 이 예시는 z16의 정확한 binary64 경로이며 임의 z에 문자열을 복사해 쓰지 않는다.

## 실행환경

Linux, GCC C++17/OpenMP, NumPy2.3.5. 기존 runtime grid에는 SciPy1.17.0이 필요하다. 테스트에는 pytest, 선택적인 Boys audit에는 mpmath1.3.0이 필요하다. 이번 실제 검증 환경은 Python3.13.5/GCC14.2.0이며 사용자 Ubuntu/Python3.12/GCC13 조합은 host benchmark 결과로 따로 기록해야 한다. `sudo`는 사용하지 않는다.

## Git 작업 흐름

정본 원격은 `cosmosapjw-quantum/WU088_HH`다. 기능 변경은 별도 branch/PR로 진행하고 `main`에 force push하지 않는다. 로컬에서는 `git pull --ff-only` 후 위 benchmark를 실행한다. 기존 runtime 삭제, 완료된 anchor 재계산, 자동 candidate 설치는 하지 않는다.

## R31M scoped tuned heavy route

Host profile과 science-resolution representative exactness gate가 모두 닫힌 이후의 **새 H source run**에서만 tuned sidecar를 사용할 수 있다. 완료된 anchor에는 적용하지 않는다.

```bash
PROFILE=/path/to/HOST_TUNING_PROFILE.json
python scripts/run_tuned_heavy.py \
  --runtime "$RUNTIME" \
  --tuning-profile "$PROFILE" \
  --n 160 --g 80 --z 24 \
  --max-new-pairs 12 --max-wall-seconds 180
```

이 경로는 원 runtime `.so`를 교체하지 않는다. candidate foreign kernel만 sidecar로 로드하며 H0와 assembler는 frozen R30 authority를 그대로 사용한다. 새 checkpoint identity에는 candidate binary/source, build key, tuning profile, science regression이 모두 기록된다. full49/trajectory/production 승격은 별도다.
