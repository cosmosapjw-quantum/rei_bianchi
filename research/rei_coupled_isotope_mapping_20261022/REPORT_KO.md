# rei_bianchi C2 연구 결과: 이론식·자료·코드의 실제 연결

2026-10-22. 이번 선택 단계는 **C2**다. 이전 C1의 21상태 사건·전하·에너지
계약을 실제 함수와 계수 행에 연결하고, 제한된 수치 진단을 한 번 실행했다.
**214개 점검이 모두 PASS, exit 0**이다. 독립 과학 검토의 최종 판정과 범위는
`REVIEW.md` 및 `evidence/INDEPENDENT_REVIEW.json`에 기록한다.

핵심 성과는 세 가지다. 첫째, 상속한 원자 모듈에서 beta를 중복하지 않는 정확한
재사용 지점을 정했다. 둘째, 복구 RR adapter와 PR220의 Li 재결합 계수가 서로
다르다는 사실을 실제 수치로 확인하여 반응률과 에너지 모멘트의 혼용을 막았다.
셋째, 저장 핵반응 자료의 18개 family와 34개 방향별 물리 채널을 전하 상태
연결에 필요한 입력으로 정리했다. 이것은 새 cosmological IVP의 결과가 아니다.

## 1. 연구를 이어 받은 위치

출발 branch는 `research/rei-coupled-isotope-contract-20261022`, HEAD는
`3e56bbd3d939ab235df2d47f9d012c95674d00fc`다. 완료된 C1은
`9f621b684fedb9b71f2148022f6909d1760ba947`, 원자 donor PR220은
`8be7533cc97b3302bf42608699d6e8313ed6af8a`로 고정했다. 핵반응 원자료는
PR219의 `5a1e5220b301a1c497f2863d6fd823e605faba80` 과학 자료 계보를 따른다.
`SOURCE_IDENTITY.json`과 `CODE_MAP.md`가 파일별 정확한 연결을 보존한다.

이번에 새로 회수한 runtime ZIP에는 과거 RR 코드와 bootstrap 코드가 실제로
있었다. ZIP 안의 bootstrap 로그에 남아 있는 오류는 역사적 상태다. 작업 중
별도 스레드의 수정·검토 결과가 `61e08967832363b611a8e5ba4167ba7b06c06b6b`에
게시된 것을 원문으로 확인했다. 그 provider review는 이번 C2의 RR 코드·행과
동일한 SHA를 기록한다. 따라서 과거 bootstrap 오류를 현재 차단 사유로 삼지
않는다. 새 게시 결과와 적용 범위는 `CONCURRENT_UPDATE.md`에 연결했다.

기존 C1 및 다른 스레드의 작업 파일은 수정하지 않았다. PR219의 83개 원자 기록 /
82개 핵반응 배경, PR220의 127개 main + 2개 full62 oracle, 다른 REC cohort는
서로 합산하지 않았다. 이번 점검 횟수 역시 새 물리 궤적 수가 아니다.

## 2. 실제로 연결한 대상

| 대상 | 매핑 결과 | 실제 재사용 경계 |
|---|---|---|
| 동위원소·전하 상태 | 21개 ordered slot, A/Z/q | `Y_i=n_i/n_B`, `A.Y=1`; 없는 T/n도 절대량으로 표현 |
| 광이온화 | 13개 edge | `AtomicNetwork.rates()`의 `G0`, photo number/energy arrays |
| 복사 재결합 RR | 13개 edge, 6개 electronic row | `rr_m3_s`, `Grr`; 각 행의 자체 미분과 energy moment 연결 |
| 유전 재결합 DR | 6개 edge, 3개 electronic row | `dr_m3_s`, `Gdr`; RR moment를 적용하지 않음 |
| 핵반응 | 18개 family, 34개 방향별 물리 채널 | 전체 JSON registry와 저장 rate/history NPZ |
| 시간·scale | proper seconds에서 x로 변환 | 바깥 `CoupledSystem.rhs/jac`가 H와 abundance scale을 한 번 적용 |

원자 generator의 재사용은 `rates()`가 가장 작고 명확한 경계다. 기존
`evaluate()`는 이미 beta 행렬 D를 더한다. all-thermal 조건에서

    ne = nB * (q @ Y)
    F_atom = (G0 + ne*Gne) @ Y
    J_atom = G0 + ne*Gne + nB*outer(Gne @ Y, q)

로 조립하면 D를 제외할 수 있다. coupled beta는 C1에서 지정한 evaluated
nuclear decay 입력이 한 번만 소유한다. 기존 donor 소스와 model JSON은
그대로 둔다. 실제 positive n/T를 가진 manufactured state에서
`F_atom+D.Y` 및 `J_atom+D`가 과거 `evaluate()`와 일치함을 확인했다.

전하별 daughter probability와 사건별 에너지 배분은 여전히 명시적으로 공급할
입력이다. 이번 매핑은 이 값들을 추측하거나 H의 전하 fraction을 T에 복사하지
않는다. 전자가 thermal/fast로 나뉘면 recombination에는 thermal electron
density를 쓰고 그 상태 정의에 맞는 Jacobian을 구성해야 한다.

## 3. Li RR의 실제 provider 차이

복구 adapter는 H/He/Li 모두 Verner–Ferland 계수를 사용한다. PR220은 H/He에
같은 VF 계수를 사용하지만 Li에는 Badnell 계수를 사용한다. 두 자료의 이름도
구분해야 한다. VF의 N은 **재결합 생성물**의 전자 수이고 Badnell의 N은
**초기 target ion**의 전자 수다. donor의 `Z:q`는 초기 양이온 전하 q다.
이 연결은 `BINDINGS.json`에 endpoint와 함께 명시했다.

H/He의 3개 electronic channel × 3개 온도에서 alpha와 자체-fit lambda의
최대 상대 차이는 `2.303380110673309e-16`이었다. Li에는 동일성 기준을
적용하지 않고 실제 차이를 기록했다. 아래 비율은 모두 **Badnell / VF**다.
lambda는 해당 alpha를 미분해 얻은 조건부 kinetic energy coefficient다.

| 전이 | T [K] | alpha 비율 | lambda 비율 |
|---|---:|---:|---:|
| Li II -> Li I | 100 | 1.010346376 | 1.017385109 |
| Li III -> Li II | 100 | 1.037824854 | 1.044410558 |
| Li IV -> Li III | 100 | 1.006274712 | 1.006290170 |
| Li II -> Li I | 1000 | 1.017221844 | 1.015745809 |
| Li III -> Li II | 1000 | 1.047671053 | 1.050565339 |
| Li IV -> Li III | 1000 | 1.004906943 | 1.003613034 |
| Li II -> Li I | 10000 | 1.002924358 | 0.986792931 |
| Li III -> Li II | 10000 | 1.049358592 | 1.048176060 |
| Li IV -> Li III | 10000 | 1.001542018 | 0.999584937 |

예를 들어 10000 K의 Li III -> Li II에서는 alpha가 약 4.94%, lambda가
약 4.82% 크다. 같은 온도의 Li II -> Li I에서는 alpha가 약 0.29% 크지만
lambda는 약 1.32% 작다. 따라서 rate와 energy coefficient를 각각 다른
provider에서 가져오는 방식은 명시되지 않은 혼합 모델을 만든다. 이 차이는
두 fit의 차이이며 어느 쪽의 실험적 정확도가 더 높은지를 판정하는 결과가 아니다.
전체 정밀도 값은 `evidence/RR_PROVIDER_COMPARISON.json`에 있다.

## 4. RR energy moment와 필요한 미분항

온도와 독립인 동일 cross section을 Maxwellian 전자 분포로 평균한다는
조건에서 직접 미분하면

    lambda = k_B T alpha [3/2 + d ln(alpha)/d ln(T)]

를 얻는다. `THEORY.md`는 number/energy 적분에서 이 식을 유도한다. 에너지
가중 정의는 [Mao, Kaastra & Badnell (2017)](https://arxiv.org/abs/1612.01017)
의 식 (1)–(4)와 대응한다. 이 논문의 독립 에너지 자료를 가져와 비교한 것은 아니다.

[Badnell RR 공식](https://amdpp.phys.strath.ac.uk/tamoc/RR/)의
`b(T)=B+C exp(-T2/T)`를 적용하면, `u=sqrt(T/T0)`, `v=sqrt(T/T1)`에 대해

    D = -1/2 -(1-b)u/[2(1+u)] -(1+b)v/[2(1+v)]
        + C exp(-T2/T)(T2/T) ln[(1+u)/(1+v)]

다. 마지막 항은 지수 b 자체의 온도 미분에서 나온다. 현재 100–10000 K에서는
매우 작으므로 Li+의 1e6 K 수식 대조점을 추가했다. 이는 donor component의
온도 범위 안에서 수행한 미분 점검이고, 새 고온 pilot나 domain 밖 API 호출이
아니다. 그 항을 의도적으로 누락하면 slope 오차가 약 0.21666으로 커져
고정한 `1e-8` 기준에서 명확히 거부된다.

분류는 **conditional derivative-of-fit moment**다. 반응률 fit 오차가 작아도
그 오차의 온도 미분까지 작다는 보장은 없으므로 energy accuracy를 자동으로
물려받지 않는다. RR의 total cascade spectrum, metastable storage, photon
escape/reabsorption을 이 식 하나로 결정하지도 않는다. DR number fit에는
signed coefficient가 있어 각 항을 physical branch로 읽을 수 없으며,
`Gne=Grr+Gdr` 전체에 RR의 kinetic factor를 곱해서는 안 된다.

## 5. Photo energy와 저장 핵반응 자료

실제 donor의 60/200 eV cutoff 각각에서 13개 photo edge를 계산했다.

    absorbed = threshold*photo_rate + primary_kinetic + unresolved_core

의 26개 ledger는 최대 정규화 잔차 `1.3950455899595689e-16`으로 통과했다.
60 eV에서는 Li1s, Li II, Li III의 해당 외부 광장 반응률이 정확히 0이고,
200 eV에서는 모두 양수임을 확인했다. 이 지원 조건은 지정 외부 광장에만
적용되며 핵반응이 만드는 hard photon의 transport를 대신하지 않는다.
이번 검사는 고정 quadrature의 내부 등식이고 연속 적분 수렴시험은 아니다.

핵반응 자료는 rate builder나 T/n propagator를 호출하지 않고 NPZ에서 직접
읽었다. 원자료는 82개 background × 257개 epoch × 18개 family × 2개 방향의
flux/cumulative 배열을 보존한다. case 0의 epoch 0,128,256을 작은 NPZ와
`evidence/NUCLEAR_SAVED_SAMPLE.json`으로 추출했고 원본 slice와 일치했다.
자연로그 convention, family 순서, 공통 온도 grid도 확인했다.

36개 배열 칸은 34개 물리 채널과 같지 않다. reverse beta 두 칸은 absent로
구분한다. 8개 external photodissociation 역방향은 s^-1, 2개 forward beta는
s^-1, 나머지 24개 binary 방향은 m^3/s다. 과거 파일명의
`log_reverse_rate_m3_s` 문자열만 보고 모든 방향에 같은 단위를 부여하지 않는다.
음의 무한대 역시 지원 영점·부재 채널·초기 population 0의 의미를 단독으로
표현하지 않으므로 별도의 applicability를 함께 기록했다.

저장 F(Y_old)를 다른 Y의 self-consistent source로 사용할 수는 없다. 같은
provider와 같은 sampled T에서는 저장 k를 읽어 새 Y의 사건률을 구성할 수
있지만 off-grid rate 처리는 다음 C3의 수치 설계 대상이다.

## 6. 실제 검증 결과와 실행량

| 점검 | 최대 잔차 | 기준 |
|---|---:|---:|
| donor alpha 공식과 실제 API, 18개 | 3.05853e-16 | 128 epsilon |
| recovered alpha 공식과 API, 18개 | 1.92246e-16 | 128 epsilon |
| 같은 VF H/He alpha·lambda, 9개 | 2.30338e-16 | 128 epsilon |
| log T five-point 미분, 39개 | 7.26186e-12 | 절대 1e-8 |
| photo energy ledger, 26개 | 1.39505e-16 | 128 epsilon |
| beta 분리 RHS 합성과 old evaluate | 4.72732e-24 | 128 epsilon |
| beta 분리 Jacobian 합성과 old evaluate | 0 | 128 epsilon |

`128 epsilon = 2.842170943040401e-14`. 두 음성 대조군은 미분항 누락
잔차 `0.21665764584750102`, beta가 남은 조립 잔차 `0.9999999535576315`로
의도대로 거부되었다. 214개 총 점검에는 source identity, endpoint mapping,
저장 배열 연결과 이러한 거부 점검이 포함된다. 독립 물리 실험 214개라는 뜻이
아니다. `evidence/BINDING_CHECKS.json`은 개별 입력·출력·허용치·원잔차를 담는다.

실제 진단 invocation은 **1회**, wall **0.948761436 s**, CPU
**0.897878138 s**, peak RSS **41952 KiB**였다. donor 생성 2회, `rates()`
7회(`evaluate()` 내부 1회 포함), `evaluate()` 1회, recovered `rr_rate()`
18회다. ODE/IVP, 과거 campaign, 핵반응 rate 재계산, propagator 호출은
각각 **0회**다. 모델 identifier가 실행 도구에서 별도로 노출되지 않았으므로
실제 runtime model identity를 추측해서 적지 않았다.

## 7. 판정 범위와 다음 실행

C2는 실제 source mapping과 제한된 수치 binding을 완성한다. 다음은 **C3의
conditional local source adapter 수치 설계**다. 첫 실행 대상은 아래 입력을
받아 순간 source를 반환하는 모듈이다.

- 21개 절대 abundance와 thermal/fast 구분, n_B, T, 명시된 UV.
- 공급된 charge-resolved 사건 목록 및 energy allocation.
- provider별 alpha와 그 자체 moment, 방향별 단위와 applicability.

이를 통해 `dotY`, total/thermal electron source, 핵 개수 source, thermal
particle source, reservoir별 energy source를 구성한다. 새 T/n 주입을 표현할
수 없는 기존 compact33 lift는 적용하지 않는다. 과거 `zero_inventory_scale=1e-20`
만으로 대략 `1e-104` 수준의 saved stock 해상도를 보장할 수도 없으므로,
zero-inventory onset과 미량 stock의 수치 표현을 C3에서 정한다.

물리 daughter branch, charge-conditioned nuclear rates, 일관된 질량·binding
자료, RR moment의 실증 오차, DR energy/cascade, fast-product stopping 및
generated-photon closure는 각자 남은 입력이다. 이들은 conditional local
구현의 시작을 막지 않지만 완결된 coupled physical production 주장의 범위를
제한한다. C3–C10 전체를 이번 C2 진단으로 완료 처리하지 않는다.
