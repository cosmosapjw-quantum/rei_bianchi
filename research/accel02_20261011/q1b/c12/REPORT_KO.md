# C12 — 전구간 이력 연결과 중단 가능한 실행

## 결론과 결과의 범위

C12는 C11에서 허용된 FLRW 국소 수치 경로를 전구간 목표에 연결하는 구현을 완료하고, 기존 PILOT02 generation 3에서 실제 연속 계산을 시작했다. 기존 상태를 초기화하지 않고 실행 계약을 명시적으로 전환했으며, 전구간 일정·24개 관측량·수용 및 거부 이력의 원자적 저장을 연결했다. 독립 검토는 연결 구현과 최초 실제 chunk를 확인했다. 이후 실제 source-band 경계에서 발생한 moment-domain 실패를 보존하고, 같은 물리 식의 양쪽 경계 offset arithmetic을 별도 source identity로 도입한 child에서 계산을 재개했다. 원래 경로와 수리 경로의 검토를 구분하며, 어느 판정도 전구간 과학적 허용이나 비등방 Bianchi 계산의 완료를 뜻하지 않는다.

**실행 결과의 유일한 최신 요약은 `STATE.json`이다.** 현재 generation, 수용 시각, 누적 attempt/macro 수, 실제 native 호출 수, 출력 epoch 수, 마지막 chunk, 실패 또는 종료 사유는 그 파일과 연결된 실제 `RESULT.json`·checkpoint manifest를 읽어야 한다. 이 보고서는 추가 chunk가 진행되는 동안 갱신되는 마지막 수치를 별도로 복제하지 않는다. `review/ACTUAL_CHUNK_ADDENDUM.json`은 원래 연결 경로의 최초 실제 chunk를 검토한 역사적 증거이다. 수리된 source를 실제 native 경로에서 실행한 새 판정은 `review/FAILURE42_ACTUAL_ADDENDUM.json`이며, 같은 고정 source와 남은 할당 안에서의 제한적 GO이다. 두 문서는 이후 모든 chunk를 개별 재검토했다는 주장을 하지 않는다.

## 고정된 물리·수치 범위

배경의 상위 프로젝트는 non-tilted axisymmetric Bianchi I test-field 체계이지만, 이번 source 정밀도 및 연결 구현은 **r=0 FLRW**에만 허용된다. 평균 체적 척도인자의 redshift는 z=15.9에서 4까지이며, 지정된 최종 경과 시간은 `4.011926941800233e16 s`이다. 방향별 관측 redshift와 혼동하지 않는다. 계량 부호는 (−,+,+,+), 에너지는 eV 또는 erg, 시간은 s, 밀도는 cgs를 사용한다.

HM12 emissivity와 초기 UVB 자료, 10–50000 eV source band, 초기 T=20 K 및 x_HII=2×10⁻⁴·neutral He, homogeneous primary-only Case A escape와 Grackle RR/CI/DR/CE/ff를 유지한다. CMB는 지정된 등방 흑체 bath이며 signed exchange ledger를 유지한다. 이 초기조건은 조건부 모델 입력이며 HyRec 초기조건의 대체 검증이 아니다. 10 eV보다 낮게 redshift된 photon state를 임의로 제거하지 않는다.

CR, RCT, secondary cascade, diffuse radiation 및 backreaction의 OFF 상태는 해당 원자·입자물리 연구의 완료를 뜻하지 않는다. 기존 원자물리 장기 lane과 관련 provider 연구는 별도로 보존한다. 새로운 photon floor, seed, fraction clipping, provider 교체, threshold `nextafter`, endpoint trace의 암묵적 대체는 도입하지 않았다.

| 구분 | 유지된 허용 기준 | 적용 의미 |
|---|---:|---|
| 전구간 시간 수렴 | 9개 관측량 2×10⁻⁶ | 실제 시간 해상도 쌍 필요 |
| spectral/angular 비교 | 전체 24개 관측량 10⁻³ | 실제 대응 이력 쌍 필요 |
| energy ledger | 초기 전체 energy 기준 10⁻⁹ | 순간 큰 항이나 source budget으로 분모 교체 금지 |
| photon-number ledger | 초기 n_H 기준 10⁻⁹ | 초기 기준 고정 |
| geometry identity | 10⁻¹¹ | ray scale·방향·angular volume |
| gas implicit residual | 10⁻¹¹ | 기존 고정 residual scales |
| source 시간 적분 | cell별 10⁻¹⁰ | 기존 order-pair 비교 |
| moment fit·source pairing | 10⁻¹² | 기존 정의 유지 |
| opacity 및 direct/ABI heat | 성분별 자체 scale 10⁻⁷ | zero reference에는 exact zero difference |
| local temporal controller | 고정 scale defect 2×10⁻⁷ | 전구간 과학적 수렴 판정의 대체 기준이 아님 |

65개 epoch 부분집합과 129개 전체 epoch는 각각 별도로 비교한다. 각 field의 분모는 **동일한 선택 부분집합에 있는 fine 이력의 max abs**이다. fine 값이 모두 정확히 0이면 차이도 정확히 0이어야 한다. strict physical fraction domain, photon positivity 및 gas EOS 범위 1–10⁶ K를 유지한다. 기존 RUN002·EVENT003·Q0, 완료된 C10/C11 검사와 PILOT02 수용 prefix는 다시 실행하지 않았다.

## P0: 이전 checkpoint에서 새 실행 계약으로의 명시적 전환

이 절은 최초 C2_FULL001 child의 전환을 설명한다. 뒤에 기술한 source 수리는 마지막 정상 gen39를 donor로 사용한 별도 C2_FULL002 전환이며, 원래 child를 덮어쓰지 않는다.

원본 donor는 `c11/integration/evidence/PILOT02/CHECKPOINTS/gen-00000003`이며 manifest SHA-256은 `6df321273a05b681ea29a396017029a10be5968319c280591b2a3254d82d1c73`이다. donor의 수용 시각은 `4539815858.150909 s`, cursor는 attempts=5, accepted macros=3, rejected macros=2, accepted half boundaries=6이다. 초기 상태를 포함한 7개 상태 prefix 전체를 가져온다.

`prepare_production_transition.py`는 donor의 기존 six-slot identity, manifest와 payload, 기존 41개 dependency를 확인한 뒤 donor를 원래 identity로 읽는다. 새로운 child의 end·runtime control·event/output binding만 선언적으로 전환한다. 물리 상태, N/U, R, support, counter origins, scales, extrema, 누적 cursor 및 기존 prefix를 바이트 단위로 보존한다. 이전 pilot의 end=10¹⁰ s와 빈 event 목록을 덮어써서 전구간 checkpoint였던 것처럼 재해석하지 않는다.

전환 기록 `IDENTITY_TRANSITION.json`에는 부모 payload 및 dependency identity, 전후 runtime binding, 보존된 cursor와 array identity를 남긴다. child generation 3을 새 control identity로 원자적으로 게시한 뒤 다음 수용 generation을 4로 시작한다. identity 전환 자체의 native map 수는 0이다. source/provider/gas·opacity binary와 기존 numerical criteria를 바꾸는 전환은 이 기능의 허용 범위가 아니다.

## P1: 물리 경계, 출력 경계, 내부 quadrature 경계의 분리

전구간 일정은 `schedule/SCHEDULE_C2.json`에 고정한다. 129개 출력 시각은 기존 저장 epoch의 binary64 값을 그대로 재사용하며, 65개 부분집합은 index 0,2,…,128이다. 출력 시각을 새 부동소수점 식으로 다시 생성하지 않고, 미래 출력 시각을 실제 accepted macro endpoint로 삼아 임의 dense-output interpolation을 피한다.

서로 다른 수치 역할의 경계를 구분한다.

1. **Hard integration/output 경계:** 10 eV 및 50000 eV source-band와 고정 cell edge의 교차, HM12 emissivity redshift-table knot, 정확한 출력 시각 및 최종 시각이다. 현재 C2 일정에는 초기 시각을 제외한 서로 다른 hard stop 208개가 있다. 물리 band/z event는 81개이며, 중복된 label은 같은 시각에 함께 보존한다.
2. **Source 내부 적분 경계:** HM12 energy knot와 cell edge 교차는 기존 `provider_event_times`가 각 map 안에서 제공한다. 해당 목록 전체를 global ODE hard stop으로 올리지 않는다. 기존 source 적분의 분할과 정밀도 기준은 유지한다.
3. **Opacity 내부 경계:** HI/HeI/HeII cross-section threshold는 기존 cell quadrature 분할이 처리한다. native smooth-support certificate가 threshold-crossing support까지 허용하도록 넓히지 않았다. 실제로 해결되지 않는 support/threshold 실패는 그대로 보존하고 멈춘다.

서로 가까운 서로 다른 event를 자의적 rounding으로 합치지 않는다. 0은 초기 boundary label에 보존하되 미래 hard-event 목록에서 제외한다. 최종 경계의 float 값도 저장 target과 정확히 일치시킨다.

## P2: gas가 실제로 사용한 24개 관측량의 수학적 연결

C2 radiation state의 cell moments는 초기 물리 체적 기준 밀도 N_c와 U_c이며, E=R q이다. 각 gas Newton 평가에서 positive incident measure를 backward-Euler absorption으로 감쇠시킨 동일한 measure를 dN_c⁺라 쓰면,

\[
K^0_{ca}=c\int \sigma_a(E)\,dN_c^+,
\qquad
K^E_{ca}=c\int E\sigma_a(E)\,dN_c^+ .
\]

V=a_rel³, χ_a를 기존 chemical ionization energy라 할 때 gas에 전달되는 값은

\[
\Gamma_a=\sum_c K^0_{ca}/V,
\qquad
\mathcal H_a=\frac{\mathrm{eV}_{\rm erg}}{V}
\sum_c\left(K^E_{ca}-\chi_a K^0_{ca}\right).
\]

여기서 \(\mathcal H_a\)는 absorber 하나당 primary photoelectron heating power이다. proper-volume heat는 \(n_{a,\mathrm{abs}}\mathcal H_a\)이며, absorber densities는 각각 n_H(1−x_HII), n_He(1−x_HeII−x_HeIII), n_He x_HeII이다. 합계 heat에는 cooling, collisional ionization, Compton exchange 및 expansion work를 섞지 않는다. χ_a와 cross-section threshold의 서로 다른 기존 수치를 동일시하지 않는다.

`native_step_v4_diagnostics.py`는 기존 v3 map을 그대로 호출하는 pass-through adapter이다. 기존 prepare/absorb/RHS 호출의 인자·반환값·순서를 바꾸지 않으면서 마지막으로 수렴한 gas 평가의 K0/KE/direct heat와 native Gamma를 보존한다. 반환된 gas, N, U, 시각과 그 마지막 평가의 입력이 일치해야 한다. **Evolved N/U를 새 power-law 분포로 재구성하여 Gamma나 heat를 다시 계산하지 않는다.** 최종 감쇠 measure는 다음 map에서 사용할 moment closure와 일반적으로 다르기 때문이다.

직접 계산한 heat는 \(c\int(E-\chi_a)\sigma_a\,dN_c^+\)이고, ABI subtraction heat와의 자체 성분 scale 10⁻⁷ 검사를 유지한다. 실제 native Gamma가 authority이다. Rust `powi(3)`와 Python `**3`의 반올림 차이에 대한 새 진단 구현 실패는 보존했으며, heat 계산에는 native multiplication 및 cell accumulation 순서를 사용한다. 별도의 64×machine-epsilon Gamma arithmetic diagnostic은 science gate가 아니며 기존 허용 기준을 대신하지 않는다.

24개 field는 기존 q1a 정의 및 순서를 그대로 사용한다.

| field 묶음 | 수 | 단위·정의 |
|---|---:|---|
| x_HII, x_HeII, x_HeIII, T, n_e, photon density, 3개 Gamma | 9 | fraction, K, proper cm⁻³, s⁻¹ |
| 순간 source number/energy의 reference·proper 값 | 4 | cm⁻³ s⁻¹, erg cm⁻³ s⁻¹ |
| 누적 source number/energy | 2 | reference cm⁻³, erg cm⁻³ |
| radiation energy의 reference·proper 값 | 2 | erg cm⁻³ |
| 3개 absorber별 primary heat | 3 | erg s⁻¹ absorber⁻¹ |
| 3개 species별 proper heat와 합계 | 4 | erg cm⁻³ s⁻¹ |

순간 source는 기존 stable same-formula `StableCellSource.source(t)`의 N/U를 합산한다. 누적 source는 기존 paired counters Nsource 및 Esource_eV에서 가져온다. 누적량을 timestep으로 나눠 순간값을 대신하지 않는다. radiation energy는 EV_ERG×ΣU이며, proper 값은 reference 값을 V로 나눈다.

각 output record는 정확한 epoch index·시각, accepted generation, physical-state hash, original-IC ledger, geometry diagnostics와 같은 map의 raw kernels를 결합한다. physical-state hash는 gas/N/U/R/support와 시각·reference H/He densities·counters를 묶으며 diagnostics 자체는 제외한다. 이 hash는 콘텐츠 identity이지 물리적 타당성의 증명은 아니다.

초기 epoch에는 이전 map의 감쇠 kernel이 없으므로, 원래 저장 C2 moments에 h=0 output-only absorption evaluation을 한 번 적용했다. 이 경로는 t=0으로 제한되고 native SIGMA만 사용하며 gas RHS를 호출하지 않는다. 물리 상태 및 counters를 바꾸지 않는다. 완료된 초기 acceptance campaign의 재실행이 아니라 새 관측량 연결에 필요한 평가이다. 실제 초기 record, kernel/state identity와 DONE receipt는 실행 증거에 보존된다.

Geometry는 실제 boundary에서 |R a_rel−1|, 방향 불변성, 그리고 정규화 angular weights에 대한 \(|\sum_j w_j/R_j^3\,/a_{\rm rel}^3-1|\)을 기록한다. 현재 r=0 범위에서 각 검사가 기존 10⁻¹¹ 한계를 만족해야 한다.

## P3: 전구간을 향하는 chunk 실행과 복구 의미

매 chunk는 동일한 최종 시각을 목표로 한다. 짧은 pilot의 끝을 반복해서 바꾸거나 초기 구간부터 재시작하지 않는다. 기존 positive first-order full-step versus two-half-step controller를 유지하며 수용되는 물리 경로는 두 half-step이다. Richardson extrapolation이나 물리 상태 projection을 도입하지 않았다.

한 invocation은 최대 새 attempt 3개 및 cooperative wall 45 s를 사용한다. wall 제한은 완결된 attempt 사이에서만 검사하므로 진행 중 synchronous native 계산을 45 s에 강제로 잘라내는 hard timeout이 아니다. 실제 workload의 증가 또는 실패로 한 attempt가 이를 넘을 수 있다. 초기 구간 측정 시간을 전구간 소요 시간의 상한으로 해석하지 않는다.

수용 시 두 half-step의 전체 prefix, 갱신 cursor, 원래 IC 기준 ledger/extrema/scales, 새 native kernels 및 생성된 output records를 새 generation에 원자적으로 저장한다. 출력 파일은 checkpoint에 내장된 authoritative record에서 복구할 수 있다. 존재한다는 이유만으로 이전 output을 건너뛰지 않으며, 같은 시각과 key를 가진 내용이 달라진 record도 거부한다. 초기 output은 DONE receipt와 record/hash/state/kernel 일치를 함께 요구한다.

거부된 temporal attempt는 accepted physical history에 들어가지 않지만, append-only cursor journal에 실제 attempt와 다음 step을 남긴다. 수용 checkpoint의 게시 이후 output/journal 작업이 실패하면 새 generation을 없었던 것으로 되돌리지 않고, 내장 transaction에서 정확한 cursor를 조정한 뒤 안전한 경계에서 멈춘다. 반대로 committed accepted checkpoint가 없는 unresolved inflight attempt는 임의로 수용하거나 자동 재실행하지 않는다. 입력·예외·traceback·관측된 실행 상태를 보존한다.

종료 상태를 구분한다. `CHUNK_ATTEMPT_BOUNDARY` 또는 `CHUNK_WALL_BOUNDARY`는 같은 고정 계약으로 다음 미실행 attempt를 이어갈 경계이다. `ALLOCATION_EXHAUSTED`는 선언된 할당의 소진이며 과학적 성공이나 수치 실패가 아니다. `FAILED_ATTEMPT`는 최초 실제 실패의 보존을 뜻한다. 정확한 final target에 도달했더라도 시간·spectral 비교를 수행하기 전에는 history admission을 주장하지 않는다.

최초 할당은 누적 physical attempts 105, accepted macros 103, 즉 이전 5/3 cursor에 새 100/100을 더한 것이다. 이후 source 경계에서 완료되지 못한 실제 실패 1회는 controller의 `attempts=accepted+rejected` invariant 밖의 external debit으로 별도 기록했다. 따라서 active C2_FULL002의 **완료 attempt cap은 104**, accepted-macro cap은 103이며 physical cost cap 105를 늘리지 않았다. 최신 남은 수는 `STATE.json`을 따른다. 실패 후 cursor를 초기화하거나 사용한 비용을 돌려주지 않는다. **이 값은 전구간 완주 예산이 아니다.** 최초 PILOT02 gen3 donor 이후에 있는 서로 다른 mandatory hard stops가 208개이고 각각 macro endpoint여야 하므로, schedule만으로도 새 accepted macro가 최소 208개 필요하다. 여기에 event 사이의 temporal subdivisions와 rejected attempts가 추가될 수 있다. 따라서 최초에 할당한 새 macro 100개만으로 최종 목표에 도달할 수 없으며, 목표를 축소하거나 count를 초기화하는 대신 나중에 명시적인 prospective runtime allocation을 기록해야 한다. source 수리 child도 그 추가 할당을 암묵적으로 만들지 않는다.

전체 prefix를 매 generation에 보존하는 현재 방식은 정확하지만, n개의 수용 경계에 대해 저장된 전체 payload 합계가 일반적으로 O(n²)로 증가한다. raw native kernel history와 누적 output metadata도 함께 복제되므로 serialization, fsync, archive 크기가 실제 처리량 병목이 될 수 있다. 이는 확인된 구현 구조의 비용이며 현재 측정되지 않은 전체 실행 성능을 추정하는 근거가 아니다. 향후 append-only segment 저장과 content-addressed immutable 공유를 고려할 수 있지만, 현재 prefix의 복구 의미와 identity를 보존하는 별도 변경으로 다뤄야 한다. 지금은 history를 조용히 잘라내거나 압축 후 동등성이 확인되었다고 주장하지 않는다.

## 실제 source-band 실패와 별도 identity의 수리

상세 유도, 후보 실패 및 수치 증거는 [REPAIR_ADDENDUM_KO.md](REPAIR_ADDENDUM_KO.md)에 있다. C2_FULL001은 donor 이후 새 macro 36개를 실제 수용하여 gen39의 전체 79-state prefix를 남겼다. 다음 run-local attempt42의 첫 coarse map은 이미 일정에 포함된 50000 eV source-band/cell158 교차에서 `SOURCE_ENTRY_CELL_MOMENT_DOMAIN`으로 중단됐다. 이 실패 구간의 native gas/opacity 호출은 0이었다. 실패한 입력·journal·원래 source 파일과 마지막 정상 checkpoint를 그대로 보존했다.

이는 누락된 event나 추가 물리 과정의 문제가 아니라, 극미량의 양의 N에서 독립 계산한 Q가 aN보다 1 ULP 작아지는 **수치 arithmetic 실패**였다. 저장된 R과 edge의 정확한 곱은 source 상한 아래였으므로, binary64의 곱이 상한으로 반올림된다는 이유로 source를 0으로 만드는 처리는 허용하지 않았다.

최종 후보는 셀 [a,b]에서 두 비음수 offset moment

\[
D=\int(q-a)s(q)\,d\log q,\qquad
E=\int(b-q)s(q)\,d\log q
\]

를 직접 적분하고 가까운 경계에 따라 Q=aN+D 또는 Q=bN−E로 조립한다. 상단 offset E를 이미 반올림된 bN−Q의 뺄셈으로 구하지 않고 역방향 log coordinate의 양의 exponential basis로 계산한다. 기존 N, HM12 profile, 배경, source band, raw Q와의 10⁻¹² 상대 일치 검사 및 strict aN≤Q≤bN 조건을 유지한다. floor, clamp, nextafter 또는 endpoint 이동은 없다.

lower-face-only 중간 후보는 실제 첫 실패 구간을 통과했으나 새 arithmetic의 전구간 source-band endpoint 검사에서 upper-face 세 곳에 실패했다. 이 실패도 보존했으며, 최종 two-face 후보는 관련 56개 endpoint를 통과했다. 실제 실패 구간의 16/32 시간 적분 비교·source pairing과 upper-offset basis의 MP80 비교는 addendum에 수치와 범위를 기록했다. 완료된 이전 source 검사 전체를 다시 실행한 결과로 주장하지 않는다.

극미량 endpoint N 자체의 MP80 상대 차이 약 0.001218은 남아 있다. 이는 near-zero support conditioning의 관측된 한계이며, 높은 상대 정확도 PASS로 표시하지 않는다. 기존 cell별 시간 적분 order-pair 기준과 endpoint 점값의 독립 상대 오차는 다른 주장이다. 이번 cell의 해당 구간 적분 dN은 정확히 0이었으며 endpoint 값을 impulse로 넣지 않았다. 이후 실제 positive-source 구간과 incident reconstruction·opacity/heat·gas residual·누적 ledger 검사는 계속 적용한다. 이 한계를 수리 성공이라는 표현으로 지우지 않는다.

선택된 source SHA-256은 `a29207b6ebee37024c35b87723dd64516e528a4f0a160b17ce9965b8dd7e0779`이다. `repair/production_v2` 및 C2_FULL002는 원래 dependency나 gen39를 덮어쓰지 않고 새 source/control identity를 선언한다. gen39의 9개 배열, 전체 prefix, cursor, native kernel history와 출력 기록을 보존한다. 원래 epoch0의 h=0 record와 BEGIN/DONE receipt를 복사하며 초기 opacity 평가도 반복하지 않는다.

수리 후 최초 실제 chunk에서는 새 source 경로를 포함한 native map 9개가 모두 완료됐으나, 세 temporal trial 모두 기존 local defect 기준에 의해 거부됐다. 이 역사적 chunk는 source 예외 수리가 실제 native 경로에서 실행됐다는 근거이지만 **accepted advance의 근거가 아니다**. 거부 cursor를 durable journal에 남기고 동일 기준으로 다음 미실행 trial을 계속한다. 후속 chunk가 실제로 어디까지 수용되었는지와 중단 여부는 이 최초 chunk의 수치로 추정하지 않고 `STATE.json` 및 active child 결과에서 확인한다.

## 실제 근거와 남은 연구

최초 연결 작업의 표적 검증은 transition 4개, schedule 4개, output 4개, runner 7개로 총 19개의 서로 다른 새 case이다. 이후 source 수리와 새 identity 전환의 별도 증거는 repair addendum 및 해당 review에 기록하며, 이 최초 19개를 현재 전체 검증 수로 재해석하지 않는다. 초기 구현 부재, 잘못된 toy-root oracle, volume arithmetic assumption, post-commit reconciliation 및 output-record 연결 문제는 각각 실제 실패·수정 근거와 함께 보존됐다. 이 검증은 저장 상태 연결과 transaction 및 관측량 소유권의 **implementation-verified** 근거이며, 제조된 검증 결과를 새 과학적 trajectory로 올리지 않는다.

`review/INDEPENDENT_DECISION.json`은 첫 실제 chunk 전 제한적 GO를 기록한다. `review/ACTUAL_CHUNK_ADDENDUM.json`은 명시적 child에서 수행한 첫 실제 continuation을 저장 증거로 확인했다. 그 검토는 원래 7개 상태 prefix의 보존, 기존 41개 및 새 전체 53개 dependency identity, 실제 새 map boundary의 domain/state-kernel 연결, original-IC ledger와 epoch0의 24개 field를 확인했다. 실제 source 경계 실패가 발생한 뒤에는 그 새 실패와 변경된 arithmetic·child 전환만 다시 검토했다. `review/FAILURE42_ACTUAL_ADDENDUM.json`은 원래 실패 비용을 차감한 남은 할당 안에서 수리된 source의 계속 실행을 허용한다. 이후 동일한 고정 구현·계약에서는 매 chunk마다 전체 review를 반복하지 않으며, 구체적 새 실패·finding·구현 변경이 생길 때만 관련 부분을 다시 연다.

다음 과학적 승격에는 다음 항목이 실제로 필요하다.

- C2 이력의 정확한 최종 목표 도달, 129개 출력 및 모든 실제 segment endpoint에서의 domain·보존·geometry 증거.
- 같은 물리 입력과 대응 epoch를 유지한 시간 refinement 이력과 9개 field의 기존 2×10⁻⁶ 비교.
- C3 및 필요한 spectral/angular 대응 이력의 24개 field 비교. 65/129 normalization을 각각 평가하며 이전 source/IC component 결과를 evolved history 수렴으로 대체하지 않는다.
- 위 기준을 충족한 뒤의 비영 shear source/geometry 연결 및 BASS consumer에 대한 별도 검증. 현재 r=0 이력의 허용을 해당 연구 lane에 자동 이전하지 않는다.

최신 실행 상태와 다음 실행 anchor는 `STATE.json`, `HANDOFF.json`, `NEXT_DAG.json`을 기준으로 한다. 원래 경로 및 최초 실패는 `evidence/C2_FULL001/`, 수리된 active child는 `evidence/C2_FULL002/`에 구분하여 보존한다. source 수리의 수학적 범위와 미해결 conditioning은 `REPAIR_ADDENDUM_KO.md`를 함께 읽는다.

게시 범위는 `GIT_EVIDENCE_SCOPE.json`을 따른다. Git에는 구현·문서·review, 전체 파일의 SHA manifest 및 stage별 launch/result/exit/log receipt를 게시한다. 기존 Git의 원시 증거는 유지하며, 새 대용량 native map·checkpoint payload 및 전체 prefix metadata는 immutable Drive/Dropbox 이중백업 archive에 저장하고 Git blob으로 전부 중복하지 않는다. 따라서 Git 저장소만 읽고 새 raw payload가 모두 포함됐다고 가정해서는 안 된다. 복원에는 기준 C11R4 코드 및 native binaries와 해당 stage archive overlay, full manifest 확인이 필요하다. 이 archive는 독립 실행환경 전체를 대체하는 standalone image가 아니다.

실제 게시 상태는 `PUBLICATION_RECEIPTS.json`과 `GIT_EVIDENCE_SCOPE.json`의 provider acknowledgement·object ID·크기/SHA 및 commit identity를 따른다. 최신 archive 이름·hash·remote ID는 이 보고서에 다시 복제하지 않는다. 업로드 검증과 실제 원격 복원 검증은 구별한다. 이 보고서는 receipt가 없는 게시 또는 수행하지 않은 원격 복원 시험을 완료로 선언하지 않는다.
