# REC–REI–BASS 통합 연구 루프 및 네 스레드 동기화

Task: `REI-REC-BASS-SYNC02-20261005`. 두 연구 루프를 순서대로 실행했고 각각 독립 검토에서 **범위 한정 PROMOTE, blocker 0**을 받았다. 네 스레드(REI·HE·CR·HH)의 최신 결과를 읽고 REC·BASS를 포함한 여섯 저장소의 후속 계획을 조정했다. 공개 전환된 BASS의 결과를 이제 다른 공개 저장소의 인계에 직접 연결한다.

첫 루프에서 REC→REI Peebles 소비자, BASS 시간좌표 API, HE 혼합 native 실행 공백을 닫았다. 결과를 `state/LOOP1_SYNC.json`에 동기화한 뒤 두 번째 루프에서 **실제 REC 원천→REI 소비자→팽창 FLRW 수소 이력→BASS Thomson 광학깊이·visibility**를 실행했다. 이 과학 완료와 Git 게시·백업 완료는 별도이며 최종 전파는 `publication/GITHUB_PUBLICATION_RECEIPT.json`, 백업은 `publication/BACKUP_RECEIPT.json`에서 확인한다.

## 이번에 실제로 완료한 연구

| 루프 / 연결부 | 실제 실행 근거 | 완료한 범위 |
|---|---|---|
| 1 / REC→REI | native 10 tests, Decimal70 독립 72 정상·8 거절 입력 / 2170 checks | 별도 `rust/rei_peebles_reference` crate에서 실제 REC public API 호출. collapsed 표준 source와 actual-ground retained source·closure defect 분리 |
| 1 / BASS clock | scoped 30 tests(기존20 포함), Decimal70 151 cases / 5001 checks | normal seconds, conformal seconds, conformal meters를 명시한 동일 cell opacity 적분 |
| 1 / HE mixed | 공급자 test bytes 그대로, actual REI 2 tests / 274 comparisons | 5 mixed H/He source cases와 scale-factor 변환의 고정 `5e-14 + 1e-300` gate |
| 동기화 | `state/LOOP1_SYNC.json` | 최신 source·범위·실패·owner 작업을 다음 루프의 고정 입력으로 사용 |
| 2 / expanding pipeline | 3 native Peebles 이력 +3 constant-x analytic fixture, 독립 DOP853·Decimal / 91 checks | 지정된 pure-H one-T matter-only FLRW benchmark, 세 시간좌표와 finite-cell probability 일치 |

HE source anchor 최대 상대차는 2.81e-15다. BASS clock 검산의 tolerance는 상대·절대 혼합 조건이며, underflow 구간까지 순수 상대오차가 작다는 주장은 하지 않는다. 이번 실행 수에 과거 원자·FT03 시험 수를 합산하지 않았다.

### 두 번째 루프의 수치 결과

모형: z=1200→1000, xHII 초기값0.8, H(z=1200)=5e-14 s⁻¹, nH0=0.2 m⁻³, Tm=Tr=2.7255(1+z) K. 배경·초기조건은 검증용 지정값이며 관측 적합값이 아니다. 원천 profile은 `HYREC2_TLA_2020_PEEBLES_FUDGE1`. observer tail0.2, RCT OFF, He nuclei0이다.

| cell 수 | 최종 xHII | 추가 광학깊이 | 독립 기준 대비 최대 x 절대차 | 광학깊이 상대차 |
|---:|---:|---:|---:|---:|
| 400 | 0.04560110416409 | 5.195088895425 | 5.27e-9 | 5.73e-6 |
| 800 | 0.04560110417383 | 5.195111209128 | 3.19e-10 | 1.43e-6 |
| 1600 | 0.04560110417441 | 5.195116786234 | 1.96e-11 | 3.58e-7 |

광학깊이 오차는 두 refinement에서 약4배씩 줄었다. 세 clock의 최대 광학깊이 차는4.44e-15, 유한 구간 확률 질량 잔차는5.55e-16이었다. 고정 분율 analytic 희석 fixture의 최종 상대차는4.86e-9였다. 단위변환 누락, 밀도 희석 이중 적용, clock a 누락은 별도 oracle sensitivity 검사에서 모두 탐지됐다. Production source를 의도적으로 변조한 mutation test는 아니다.

그림은 `figures/REC_REI_BASS_EXPANDING_VALIDATION.png`와 `.pdf`, 원 이력은 `loop2/evidence/peebles_{400,800,1600}.{json,csv}`다. `loop2/research/plot_expanding_history.py`로 다시 그린다.

**이 그림은 재결합/산란 연결의 팽창 우주 benchmark이며 실제 EoR 재이온화 예측이 아니다.** 지정된 H/T, pure-H collapsed closure와 유한 해상도 범위에서만 검증됐다. retained-shell 강성 이력, full HyRec, 일반 Bianchi 진화, 전체 BASS build, finite-T/KN·편광 generator, 연속체 오차 enclosure는 미완료다. 첫 구간 밖의 tail0.2는 계산 결과가 아닌 경계 입력이다.

## 최신 상태를 잘못된 대기 상태와 분리

| 스레드 / repo | 이번에 해소·수신한 항목 | 남는 blocker와 계획 |
|---|---|---|
| REI | static FT03 F04 인증 완료를 최신 반환에서 확인. PB 소비자와 HE mixed 검증 추가 | 게시 중 실제 F05 첫 구간 완료 반환 수신. F08 conditional stage 구현·검증 수신, 전체 paired history는 미실행. 기존 REI owner의 다음 임계 경로는 F08 |
| HE | F2C 국소 RCT RHS 수락, F2D 직접 exposure 상한 수신. mixed-native 실행 완료 | 새 반환에 대한 HE owner ACK, 실제 RCT stepper/stage·energy ledger. FT03와 GM25 온도영역의 교집합 부재 |
| CR | F04C 온도의존 잔차/J/H와 REI static F04 완료를 연결 | CR_OFF loader/callback 관측. 게시 직전 F04D parent/two-half event jets 완료 반환을 추가 수신. 다음 F04E는 실제 F05 stage·unit·accepted-step binding 필요 |
| HH | F07 S0 HH-OFF owner 반환 수령 완료. 옛 WAIT_F07은 해당 범위에서 대체 | OFF runtime 관측. optional HH는 parked; source/domain/event·heat owner가 필요한 opt-in 때만 재개 |
| REC | PB02 source bytes 보존하며 실제 소비자 연결. selected-He V11 scoped PASS 수신 | E1C와 Gate I, 범위 밖의 He/thermal·native-COM gate 보존 |
| BASS | 공개 전환 확인, clock API 및 expanding PB 이력 소비 | 실제 EoR accepted payload, full build, finite-T/tail·scalar-Q kinetic authority 별도 |

별도 호스트에서 실행 중인 프로세스를 조회한 것은 아니다. 여기서 기존 진행 경로란 최신 owner 문서의 예약·다음 작업을 뜻한다. 같은 native 경로를 동시에 고치는 일을 피하도록 `planning/REVISED_DAG.json`에 write boundary를 넣었다.

## 지금 병렬로 진행할 수 있는 후속 작업

1. **FLRW06 실행 반환 수령**: 게시 직전 compiler 부재 반환을 받아 이 환경에서 준비된 native 회귀를 완료했다. 167 scalar 비교·6 정확 오류 거절이 통과했다. 이 좁은 gate는 다시 실행하지 않고 actual accepted-stage 연결에 사용한다.
2. **Native U/work/edge-energy 소비자 계약**: 새 FLRW06가 완료한 moment-cone·fixed-stage energy/work 유도를 재사용해 actual U/edge 소비 경계와 stage owner를 정한다. 같은 유도를 반복하지 않는다.
3. **CR/HH OFF dispatch 관측**: 실제 receiver 경로에서 loader/source/callback 미호출을 기록한다. flag 또는 null을 0의 실행 증거로 바꾸지 않는다.
4. **CR F04E receiver binding**: 새 F04D의 parent·two-half event jets와25-output 계약을 실제 REI-F05 state/time/units/accepted-stage에 묶는다. 필요한 receiver가 없으면 그 입력만 대기한다.
5. **RCT stepper/response 설계**: 새 write reservation 후 실제 implicit stage와 event·thermal·escape 장부를 연결한다. 직접 exposure 상한을 전체 observable 변화 상한으로 바꾸지 않는다.

우선순위는 **기존 F08 paired-history 경로 유지 + native U/edge 소비자 계약·CR F04E binding 병행**이다. Spectral native 회귀는 이번 말미에 완료했다. PB–BASS benchmark를 원자 계산 완료 대기로 되돌리지 않는다. HE paired campaign을 위해 현재 온도 guard를 완화하거나 GM25를 자동 외삽하지 않는다.

## 원래 연구 lane과 실패 보존

각 repo의 원래 atomic/REC/BASS 확장 계획·source·실패는 그대로 남는다. 실제 source-domain 초과, 명시적 opt-in, 관측량 감도에서 확인된 precision 필요가 생기면 해당 lane을 호출한다. 단순 새 게시나 unchanged OFF 상태는 재실행 이유가 아니다.

HH의24/289·265 unbounded·epsilon null·B22 OPEN, CR의 G02 unresolved·capture=false·all_bound OPEN·b_grid NO_GO, REC E1C/Gate I, BASS finite-T 및 scalar-Q gate를 보존한다. REI strict local<2e-4/public width<2e-3, [160,161] 기존 FAIL=2.1245050576368385e-4와 prefix160도 지우지 않는다.

이번 초기 missing API/target 실패와 Peebles 시험의 잘못된 decimal 기대값으로 발생한1 ULP 실패도 원본 보존했다. 후자는 정확한 binary 입력 연산으로 기대값을 고쳤고 production source나 science tolerance를 바꾸지 않았다.

## 재현·인계

먼저 `publication/LOW_COST_ENTRY.json`, 자신의 `publication/threads/<repo>/SYNC_STATE.json`, 해당 DAG task만 읽는다. 상세 raw evidence는 그 task의 포인터를 따라간다. Native source snapshots는 exact Git blob/SHA256으로 묶여 있으며 upstream 원 논문 PDF나 허용되지 않은 원문 코드 재배포는 포함하지 않는다.

`loop2/native/reproduce.sh`는 packet 상대경로로 source를 빌드한다. Rust1.94.1과 Python의 NumPy/SciPy/Matplotlib을 사용했다. Git-pinned Cargo 배포 설정과 이번 offline rustc/source harness 실행을 구분한다. 전체 BASS dependency build나 원격 CI를 실행했다는 주장은 없다.

각 repo 기존 branch/PR에 source 변경과 successor handoff를 게시한다. main merge·force push·RCT 자동 활성화는 하지 않는다. Git 게시와 다른 ChatGPT 스레드의 실제 수신 ACK는 별개다. 직접 채팅 쓰기 기능이 없어 스레드별 문서·machine-readable 인계를 repo/PR에 전파하며, 수신하지 않은 owner ACK는 대기로 유지한다.

## 게시 직전 동시 결과 수신

REI의 새 FLRW06 compiler blocker는 준비된 driver/input/reference와 scientific module을 그대로 사용해 해소했다. 1회 compile/1개 native process의18개 command record(11 valid photo+6 error+1 photon),167 scalar를 비교했고 최대 상대차3.777652226439761e-15였다. Git source 취득만 이미 materialize한 동일6blob을 읽는 명시적 adapter로 바꿨다. 원 runner·실패·diff를 보존했으며 full crate/independent U/history admission은 아니다. 결과와 별도 bounded review는 `late_flrw06/` 및 `review/LATE_FLRW06_REVIEW.json`에 있다.

CR의 F04D24tests와 event-jet 결과, HE의 후속 receipt/intake 갱신도 수신했다. 이는 새 owner 결과를 읽은 것이며 여기서 해당 원자 계산을 다시 실행한 것이 아니다. 최신 상태·게시 parent는 `publication/atomic_publish/`와 최종 Git receipt가 기록한다.

최종 수신 cutoff는 REI `bda0feefd4957dc59ebf4b068d01690942aa0a2a`다. F05는 실제 static FT03 첫 구간의 3 refinement/7000 accepted/0 rejected와 MPFI200 whole-history PASS를 반환했다. F08은 conditional coupled stage와 140tests PASS를 반환했지만 전체 paired history는 아직 실행하지 않았다. 이 owner 결과는 여기서 재실행하지 않았으며 final-byte 두 번째 독립 review도 수신되지 않았다. 우리의 두 benchmark 루프와는 다른 증거다. FLRW06은 양쪽에서 동시에 native 실행이 끝났으므로 하나의 완료 항목으로 합치며 반복하지 않는다. 후속 source delta는 다음 intake에서 받는다. 상세는 `late_rei_final/FINAL_DELTA.json`.
