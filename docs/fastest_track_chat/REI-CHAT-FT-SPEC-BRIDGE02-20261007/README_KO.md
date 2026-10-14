# BRIDGE02: 실제 F08 점값 순서와 시간·방출 오차 분리

판정: F08_POINT_ORDER_REPRODUCED_AND_TIME_SOURCE_ERRORS_SEPARATED_SCOPED.
Source/read parent: 84afbe7660ec79e5e43822e7aea49a0a9ee8daea.

원 scientific source 13개를 변경하지 않고 CharacteristicRay::pullback과 primary_stage_step_conservative를 실행했다. paired_runtime.rs 자체의 전체 실행은 아니다. 새 opt-in 연구 호출부의 F08 transport→endpoint source→endpoint BE 순서를 실제 첫 두 committed half 기록에 대조했고, 세 이온화분율은 각각 같았다. 열에너지 차이는 1.7763568394002505e-15 eV/H, photon별 최대 차이는 1.0567935415650709e-14/H다. 계승한 gas root box에는 들어가지만 새 root certificate는 계산하지 않았다.

## 같은 T0 시계

0..1e12 s, H=1e-14/s, S0 초기 gas/13.7eV .05 photon/H, 연속 source5e-15/H/s, FT03 HG CaseA CI/RR/2DR를 유지했다. T0 macro1.25e9 s의 half6.25e8 s를 1600번 사용한 별도 점값 진단이다. Grid8 T=47942.77067098594 K, cohort T=47917.90527278305 K. 계승한 continuous-energy/source 수치참조47917.6292226325 K와의 차이는25.14144835345 K 및0.27605015056 K다. 이후 전 구간이 과거 raw와 byte-identical하다는 주장이나 production default 교체는 없다.

## 시간과 방출의 독립 교차시험

중점 birth M=16/32/64의 각 유한 source measure를 고정하고, 모든 M의 birth·cutoff·binding 시각을 합친 동일188구간을 r=1/2/4로 세분했다. 동일 M의 continuous-time impulse 해를 독립 Python FT03 방정식으로 계산했다. 같은 r에서는 source만, 같은 M에서는 time만 바뀌므로 이전 동시세분화와 다르다. 이 실험의 Ghalf→BE→Ghalf는 원 F08 끝점 map과 별도임을 유지한다.

M64/r4의 시간·splitting 차이는 +0.7787622641044436 K, source quadrature 차이는 -0.000910905800992623 K, 합은0.777851358303451 K다. 현재 이 진단은 시간오차가 지배한다. Source 개수만 늘리지 않는다. 모든 참조는 수치해이며 uniform interval certificate가 아니다.

실제 F08의 p_new=(p_old+hS)/(1+hk)는 implicit source quadrature다. 이를 정확한 endpoint Dirac birth와 동일시하거나 pre-birth absorption 버그로 단정하지 않는다. Cutoff가 만드는 birth-response 도함수 점프로 인해 midpoint 오차계수는 격자 내 frontier 위치에 의존한다. 정확 ramp 오차와81개 Fraction phase를 검산했다.

## 실행 증거와 한계

Native13이력/8348 source단계/max1601 packets. 독립4변수BE roots43개,scalar20470개 비교. 최대gas차2.22044604925e-16,event상대차6.00176894590e-15,독립nativeBE잔차1.76829555451e-16. 최대number잔차2.37171393636e-14/H,energy잔차1.06581410364e-14 eV/H. 새로운 reference4이력/231개짧은IVP구간/max77변수. M64 DOP853/Radau T차6.54836185277e-11 K.

새6개단위시험 통과: clock3개 red/green, 나머지3개 tests-after. 마지막 verifier는 source/binary/stdout identity와실행증거를 새로 확인해exit0. Native/참조 구성단계는실행했으나 reproduce.py를 추가폴더에서 end-to-end 재실행하지는 않았다. Launcher는py_compile만별도확인했다. 공식toolchain서명 진본성은미검증이다. Cargo/기존campaign/부모proof재실행0.

전체 F08 interval parent/root/local/width/adaptive transaction/restart 경로, 시간·source uniform certificate, Bianchi 방향상태, 물리fit/생략과정의 승인 없음. Local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD보존.

## 다음 단계와 재현

다음 bounded gate: BRIDGE02_COHORT_PARENT_BOX_AND_TRANSACTION_ADMISSION. 실제 primary_stage_root에 growing cohort의 parent boxes와 geometry/birth uncertainty를 연결하고 첫 macro transaction 하나에서 reject/commit을 검사한다. Source 시계를 보존하고 opt-in을 유지하며 전체campaign은 재실행하지 않는다.

전체 report/source/binary/stdout/reference/checker는 sealed ZIP에 있다. 압축 해제 후 python reproduce.py --output NEW_DIRECTORY --rustc /path/to/rustc. Pinned Rust1.94.1, numpy/scipy/mpmath/sympy 필요. Network/Cargo 없음. 상세 NEXT_HANDOFF_KO.md와 INTEGRATION_CONTRACT.json 참조.
