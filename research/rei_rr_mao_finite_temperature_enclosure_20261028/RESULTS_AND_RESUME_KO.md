# RR/Mao 결과와 재개 상태

2026-10-28. Project: cosmosapjw-quantum/rei_bianchi. 현재 단위는 `rei_rr_mao_finite_temperature_enclosure_20261028`이며, 이 문서는 이미 보존된 유도·원자료·실제 검토·이전 실행 기록을 종합한 최종 설명이다. 모든 실제 완료 R1–R10/C1–C5의 Git 게시·원문 blob과 Drive/Dropbox의 completed ACK 및 size metadata를 확인했다. 상세 전달 원장은 `delivery/STAGE_DELIVERY_ACKS_FINAL.json`, 각 단계 진행표는 `STAGE_PROGRESS.md`, 최신 비용은 `CURRENT_BUDGET.json`을 따른다. 이 설명을 작성하면서 추가 과학 검토나 수치 계산을 수행하지 않았다.

현재 RR/Mao 단위는 **R1–R10 및 C1–C5의 15/20**, 즉 수학적 결과와 실제 검토된 준비 소스까지 완료한 상태다. **C6–C10의 수치 실행·실제 그림·실행 후 독립 검토·최종 실행 인계는 NOT_RUN 또는 미완료**다. 이전 DR 단위의 **17/20**은 실제 전달된 선택 실행 근거의 역사적 범위를 가리킨다. DR의 전체 C8/C9/C10은 그림 의무 등이 남아 미완료이며, 뒤에서 설명하는 near-equal Decimal 입력의 반환 보장 제한도 함께 적용한다.

원래 통합 DAG는 계속 **working33/88, central last28/88, 88 IDs/17 edges, delta0**다. 두 단위의 내부 R/C 단계 수를 원래 DAG 완료 노드로 더하지 않는다. 실제 REI recipient 온도·native25·물리적 반경은 null, `L4_ready=false`, `global_physical_completion=null`을 유지한다.

## 1. 이번에 구성한 대상

이번 결과는 실제 native source가 사용하는 여섯 RR rate와 Mao2017 kinetic-loss factor의 유한 온도 구간 enclosure다. 정의역은 공통으로 **100–1,000,000 K**이며, source의 JSON 숫자와 변환 상수는 각각 native binary64로 해석한 후 그 정확한 실수상을 parameter로 사용한다. 따라서 이상적인 십진 계수로 몰래 바꾸지 않으며, 동시에 NumPy/native callback의 모든 중간 floating 연산을 그대로 감싸는 정리라고 주장하지도 않는다.

실제 `ThermalSources`의 기본 선택은 `rr_closure='mao2017'`다. 이때 loss는

\[
L(T)=k_B\,T\,\alpha_{\rm native}(T)\,f_{\rm Mao}(T)
\]

이다. 다른 선택인 rate-derivative moment `k_B T(3 alpha/2 + D alpha)`로 대체하지 않았다. 두 식은 source에서 구별되는 conditional closure다. Source에 이미 있는 point derivative를 새로 발견했다고 주장하는 작업도 아니다. 추가한 것은 이 실제 선택 함수의 **finite temperature box와 finite log-temperature step bound**다.

계수·native 함수·Mao selected JSON·원본 lock/tables는 `source/`에 원문으로 보존했고, `SOURCE_IDENTITIES.json`이 bytes/SHA256/Git blob과 origin을 연결한다. 특히 full Mao selected JSON에는 기존 table 비교, unfavorable closure 차이, `f_at12000` 등의 계산값이 들어 있다. 이를 원자료에 포함된 역사적 평가 노출로 명시했다. 이번 RR 실행 결과나 새 reviewer의 독립 발견으로 다시 세지 않는다. 그 fit residual percentage도 엄밀한 derivative/혼합 loss/물리적 온도 불확실성으로 승격하지 않는다.

## 2. 수학적 구성과 유효범위

`THEORY_AND_CONTRACT.md`는 RR0–RR6, M0–M3, L0–L2, B0, T0–T1의 전체 유도를 보존한다. RR에서는 temperature-dependent exponent `b=B+C exp(-T2/T)`의 변화까지 미분한다. Li 두 row의 C를 고정한 채 derivative를 취하면 실제 nonzero correction term을 빠뜨린다. 유도는 그 항을 포함한 첫째·둘째 log derivative를 제공한다.

여섯 실제 row는 양의 coefficient/domain 조건을 만족한다. C=0인 row는 RR log slope가 음수이며, nonzero-C인 Li row에도 exact coefficient images와 느슨한 유리수 부등식으로 `C ln(T1/T0)<e`를 증명한다. 따라서 실제 RR rate는 엄밀히 감소한다. Rate의 유한 구간 image는 양 끝의 point value로 감쌀 수 있다. 이 결론을 Mao factor나 loss에 무단 확장하지 않는다.

Mao에서는 natural log의 argument가 `k_B T/eV_J`라는 dimensionless numerical temperature다. `c0*ell²`과 numerator의 `a2 exp(-b2 ell)`을 모두 유지한다. 실제 Li+의 nonzero c0, He+/Li+의 nonzero a2 경로가 포함된다. Factor와 RR가 양수이므로 선택 loss도 양수다. 유한 loss box는 `k_B*T*alpha*f`의 inclusion-preserving interval product로 구성하며, loss가 단조라고 가정해 endpoint만 취하지 않는다.

둘째 log derivative의 interval magnitude를 공통 B2로 잡으면, anchor와 target 사이의 전체 log segment가 domain에 있는 조건에서

\[
|y(T_{\rm target})-y(T_\star)-Dy(T_\star)h|\le B_2h^2/2,
\qquad h=\ln(T_{\rm target}/T_\star)
\]

가 두 부호의 h에 성립한다. 구현은 analytic remainder뿐 아니라 base value·첫 derivative·h 자체의 outward arithmetic uncertainty도 최종 enclosure에 포함하도록 준비했다. Exact 같은 endpoint에는 h=0과 radius0을 사용한다. Positive finite function box와 별개로 derivative box나 standalone Taylor enclosure는 0을 가로지를 수 있으며, 모든 Taylor 하한이 양수라고 주장하지 않는다.

이 구성은 source의 represented-real RR/Mao component에 관한 것이다. Physical fitting uncertainty, 누락 channel, 비-Maxwellian 효과, 전체 thermal feedback, 실제 recipient state/EOS와 물리적 오차반경은 이 정리에서 공급되지 않는다. 새로운 literature novelty나 strong no-go 주장도 없다.

## 3. 실제 독립 검토의 순서와 노출 한계

새 native reviewer의 실제 task는 **`/root/rr_mao_native_reviewer`**다. Root의 dispatch는 `fork_turns=none`으로 이루어졌고, reviewer도 inherited parent conversation이 보이지 않는 별도 task였다고 기록했다. 다만 shared filesystem이며 hardware/security isolation은 아니다. Source의 역사적 평가값과 author proof의 proposed controls도 노출되어 있었다. 따라서 이를 모든 기대·역사 자료에서 완전히 blind인 검토라고 부르지 않는다. 실제 읽은 파일·범위·노출·seal 순서는 각 report와 ledger에 남겼다.

첫 **`review/R6_PHASE1_SOURCE_ONLY.md`**에서는 implementation/tests를 읽기 전에 source equation과 proof를 검토했다. RR의 temperature correction, 실제 selected Mao closure, 엄밀 감소와 positive mathematical function, 양/음 log step의 uniform Taylor theorem에서 source-algebra 반례를 찾지 않았다는 scoped 수학 판정을 냈다. 이는 실행 검증이 아니라, 이후 실제 arithmetic primitive가 inclusion을 구현해야 한다는 조건이 붙은 유도 판정이다.

그다음 **`review/R6_PHASE2A_STATIC_CODE.md`**는 core와 inherited arithmetic을 읽은 뒤 tests/wrappers와 대조하기 전에 별도의 실제 구현 반례를 봉인했다. 마지막 **`review/R6_PHASE2_FINAL_STATIC.md`**는 수정 diff, 준비된 tests·wrappers·record envelope와 실제 CAS error를 읽어 static disposition을 내렸다. 과학 소스를 import하거나 테스트·oracle·plot을 실행하지 않았다. CAS 실제 응답도 internal tool error였고 scientific result는 없었으므로, 이를 zero residual이나 검증 성공으로 바꾸지 않는다.

## 4. Tiny ln(1) 반례와 한정된 수정

실제 반례는 key1:1, alpha, anchor100, exact target100+10^-100, domain[100,101]이다. 이 입력은 양수·정렬·domain 조건을 모두 만족하며 anchor와 다르다. 그러나 nominal60-digit directed ratio의 lower endpoint는 정확히1로 반올림될 수 있다. 기존 log primitive가 exact ln1=0에도 무조건 predecessor를 취하면 least-subnormal 음수를 만든다. 이것에 절댓값이1보다 작은 nonzero derivative를 곱하면 활성화된 Underflow/Subnormal trap이 작동하여 유효 입력에서 반환하지 못하는 경로가 생긴다.

이 finding은 실행한 실패 로그가 아니라 **구체적 입력을 갖춘 analytic source-path counterexample**다. 수학적 Taylor theorem의 실패와도 구별한다. Arithmetic representation이 불필요한 subnormal endpoint를 만들어 구현의 return obligation을 깨는 문제다.

한 scoped author repair는 새 RR module 안에 `natural_log`를 추가했다. Endpoint가 정확히1이면 그 log endpoint는 정확한0으로 반환하고, 다른 endpoint에는 correctly-rounded HALF_EVEN logarithm과 outward neighbour를 유지한다. Pinned DR dependency는 바꾸지 않았고, RR/Mao의 모든 관련 log call site만 새 helper로 연결했다. 이는 exact endpoint identity를 사용하는 수정이며, tiny h를 tolerance로0 취급하거나 원래 함수를 변경하는 수정이 아니다.

같은 수정 과정에서 opposite-sign regression의 anchor101은 reciprocal1/101의 outward 오차 때문에 valid h interval이0을 가로지를 수 있다는 controller/static 지적을 반영했다. Negative control은 terminating reciprocal을 가진 anchor125, target125−10^-100, domain[124,125]로 정렬했다. Positive anchor100 control은 유지했다. 두 quantity의 준비된 tiny-step 기록에는 domain,h,f0,d0,B2,radius,enclosure를 모두 담는다. 중간 unexecuted drafts와 최초 before-fix bytes는 보존했다. 이는 새로운 trial campaign이 아니라 한 finding에 대한 static fixture/record 정렬이다.

Reviewer의 최종 결론은 core의 해당 경로와 fixture·record format에 대한 **CLOSED_STATIC**이다. 최종 core SHA256은 `028b854a68e5d3e2ac64f3e3ff4a5b531416fc00610dbe7901563808f26541e7`, test SHA256은 `08bc50acd6a6baca563e3bf7a259ff39f7c86d4c2c13a50f18a58421fc6f48f5`다. 실제 tiny-step regression을 실행해 닫았다는 의미는 아니다. 아주 작은 step에서는 nominal ratio enclosure가 상대적으로 넓을 수 있어 tightness도 주장하지 않는다.

## 5. 이전 DR 결과의 보존과 scope 교정

RR의 local helper는 unchanged DR implementation을 고치지 않는다. **`review/R6_DR_DEPENDENCY_SCOPE_ADDENDUM.md`**는 같은 arithmetic 문제의 DR witness를 present channel **2:1**에서 제시했다. DR key1:1은 structural absence이므로 이 문제를 보이는 witness로는 적절하지 않다. 이 구분은 핵심이다. Present2:1의 작은 nonzero derivative가 만들어 내는 arithmetic 경로와 absent1:1의 정확한 zero를 혼동하면 실제 반례의 조건이 사라진다.

따라서 옛 DR에 대해 arbitrary-near unequal exact Decimal endpoint마다 정상 반환한다는 포괄적 구현 보장은 철회했다. Mathematical theorem과 실제 선택되어 반환·전달된 separated-step 결과는 그 이유만으로 반증되지 않는다. 역사적17/20은 이 **선택 실행·전달 범위**로 읽는다. Scope 교정은 `CURRENT_EVIDENCE_INDEX.md`가 연결하는 DR addendum commit에 별도로 게시되며, 기존 numerical originals와 단계 ACK를 소급 편집하지 않는다.

옛 `rei_approved_continuation_20261028/unit/stages/C7.md`와 실제 raw-return review가 보존한 과학 예시는 다음과 같다. He+ alpha의[100,101] 구간 하한은 약 **1.16154273411352556×10^-2024 m³/s**로 엄밀한 양의 support를 유지한다. Exact rewritten coefficient margin은 **411775599910974117/295147905179352825856**이며, binary64 exponential underflow로 관측된0을 structural absence라고 해석하지 않는다.

보존된 represented anchor 약14919.8638392795056K에서 h=−1/128인 He+ alpha case는 direct residual 약 **6.08840646238270760×10^-31**, outward remainder bound 약 **5.48399056366927608×10^-30**를 반환했다. Source 기록은 anchor가 saved background interpolation이라는 점도 유지한다. 이것은 actual recipient temperature를 결정한 결과가 아니다. Actual zero-step alpha/L에서는 h[0,0],radius0,enclosure=f0가 반환되었다. 다른 broad Taylor case의 하한은 음수일 수 있어 모든 Taylor interval의 positivity를 주장하지 않는다.

이 숫자들은 기존 raw scientific return의 구체적 예시다. Test method나 record의 개수를 과학 수용의 근거로 삼지 않는다. 실제 수용은 정의·source identity·outward 연산·독립 reference와 해당 원시값의 대응에 한정된다. 새 RR 수치 결과는 아직 존재하지 않는다.

## 6. 최신 근거와 전달 범위

최신 bounded survey의 상세 근거는 `survey/github/DELTA_SURVEY_FINDINGS.md`, `CENSUS_SUMMARY.json`, 현재 root의 **`CURRENT_EVIDENCE_INDEX.md`**를 따른다. 관측창은2026-10-28 11:58:09.289–12:14:12.750UTC이며 prior cutoff 이후의 fixed-tip delta를 읽었다. Accessible51repos 중 관련15repos의1485refs/1458tips를41branch pages와 명시적 terminal pages로 연결했고, changed7/new7refs와 selected15fullsource originals를 보존했다. 별도 late WU observation은 snapshot을 조용히 덮어쓰지 않고 구분했다.

이 coverage는 non-atomic API 관측과 그 cutoff의 범위다. 모든 역사적 branch body, 삭제·비공개·unsubmitted work, 전체 private conversation, 모든 remote archive bytes를 읽었다는 뜻이 아니다. Conversation retrieval과 backup metadata는 별도 제한이 있고, Drive dossier listing은1000개 cap과 미노출 continuation 때문에 일부 범위다. Source owner의 자체 local completion이나 central backlink를 독립 물리 수용 또는 원래 DAG node 증가로 이월하지 않는다.

원문 query/source/read/identity ledger와 provider ACK가 있는 immutable survey archive의 위치는 `CURRENT_EVIDENCE_INDEX.md`에 연결되어 있다. Provider upload ACK와 별도 size metadata는 확인한 전달 사실이고, remote whole-byte 재다운로드 SHA 비교와는 구분한다. 관련 project-only source와 판단을 공개 문서에 유지하며 불필요한 원문·외부 paper extraction·무관한 개인 자료를 복사하지 않는다.

## 7. 현재 자원과 정확한 남은 작업

최종 보존 직전의 알려진 보수적 원장은 **planning21.957967051/22, presentation64.991845349/62, main605.471450 NO_MORE_IVPs**다. 최종 mechanical materialization의 관측 prefix는 `CURRENT_BUDGET.json`과 별도 receipt에 한 번만 추가한다. Tool/model/network/read/storage와 미계측 tail은 **UNKNOWN_NOT_ZERO**이며, 알려진 부분합을 정확한 whole-session cost나 budget PASS로 표시하지 않는다. 과거 실패·닫힌 예약·이미 확정된 source-owner 비용은 유지한다. PR248의 main700/3IVP exception 및 PR249의 main620/presentation65 exception은 닫힌 다른 thread 권한이므로 이 작업으로 옮겨 쓰지 않는다.

제안된 **absolute cumulative30/75는 아직 NOT_APPROVED**다. 남은 구체적 작업은 새 RR의 표적 numerical invocation target1CPU-s, 이미 저장된 DR 결과만 사용하는 figure target1.5CPU-s, 성공한 RR saved output만 사용하는 figure target2CPU-s와 각 원문·영수증·게시·백업 보존이다. 각 job에는 새 supervisor allowance0.25CPU-s를 별도로 제안했다. 실제 소요시간 보장이 아니라 bounded allocation 제안이다. Full old suite나 새 IVP를 수행하는 계획이 아니다. 각 실제 실행은 새로 확정된 category allowance와 once-only dispatch가 있어야 한다.

RR의 준비된 source는 실제 static review를 받았지만 C6–C10 실행 증거가 되지 않는다. 실행 후에는 실제 scalar enclosure·oracle·tiny-step·source refusal 기록을 읽고, 실패가 있으면 그 실제 원인에 한정해 판단해야 한다. Figure는 saved data로만 만들며 실제 PNG의 units/domain/anchor/step labels를 읽어야 한다. 다른 단위의 그림이나 준비된 SVG source는 그 visual obligation을 대신하지 못한다.

현재 결론은 **RR15/20 prepared-source-reviewed, DR17/20 selected delivered historical scope, original33/88 central28/88 delta0**다. 뒤의 실행·그림·runtime review·delivery ACK가 실제로 생기기 전에는 이 숫자를 올리지 않는다. 복사 가능한 재개 계약과 정확한 명령은 `HANDOFF_20261028.md`, 새 절대누적상한 제안은 `RESOURCE_PROPOSAL_30_75.json`에 있다. 이 제안은 아직 승인이나 실행 사실이 아니다.


## 최종 보존 비용 추가 기록 — 2026-10-28T13:11:36.453130+00:00

이 추가 기록과 `CURRENT_BUDGET.json`이 위의 최종 보존 직전 원장 이후 비용에 대한 기준이다. 단일 필수 metadata 보존 작업 `RR_MAO_FINAL_RECEIPT_METADATA_20261028`의 관측 process CPU **prefix 0.017035768 s**를 presentation에 **한 번만** 추가했다. 기준값 **64.991845349 s → 65.008881117 s**이며, planning **21.957967051/22**, main **605.471450 NO_MORE_IVPs**는 변경하지 않았다. 기존 실패 비용과 닫힌 예약도 유지한다.

측정 범위는 Python time import 이후부터 요청된 원문 byte 취득, 기준값 확인, 수정 전 세 문서 보존과 초기 input identity 준비까지다. 이 문단·budget의 최종 쓰기, 이후 최종 hash·capsule·parts·receipt 쓰기·exit 및 이전 read 준비와 model/tool/network/transport 비용은 **UNKNOWN_NOT_ZERO**다. 따라서 이 prefix나 원장 부분합을 whole-session cost 또는 budget PASS로 제시하지 않는다.

현재 승인 상한은 여전히 **22/62**다. 제안된 **30/75는 NOT_APPROVED**이며, 이 metadata 보존은 새 scientific job·CAS·test·plot 실행이 아니다. RR **15/20 준비·전달**, 원래 DAG **33/88·central28/88·delta0**와 남은 실제 runtime/figure/review 의무는 변경하지 않는다.
