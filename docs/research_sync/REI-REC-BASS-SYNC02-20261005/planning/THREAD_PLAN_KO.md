# 두 연구 루프와 여섯 저장소의 조정 계획

이 파일은 **두 루프의 실제 실행과 독립 검토를 반영한 조정 계획**이다. 1차 루프는 actual final receipt와 독립 검토를 합쳐 `state/LOOP1_SYNC.json`으로 동기화했다. 이어서 2차 prescribed FLRW benchmark를 실행하고, 그 결과에 맞추어 아래 상태를 root가 확정한다. 두 번째 루프는6회 native 실행과91검사를 통과했고 독립 scoped PROMOTE를 받았다. Git/Drive/Dropbox 완료는 별도 최종 receipt에서 확인한다.

네 연구 스레드는 REI·HH·HE·CR이고, REC와 BASS는 별도 공급기·소비기 저장소다. 최신 조사 근거는 `../survey/rei_rec/INTAKE_REPORT_KO.md`, `../atomic_analysis/ATOMIC_SYNC_KO.md`와 각 exact source lock이다. 기계 실행 계획 `REVISED_DAG.json`에는 입력·출력·의존관계·write boundary·종료 조건이 있다.

## 이번 1차 루프 → 동기화 → 2차 루프

| 단계 | 현재 초안 상태 | 확정할 실제 증거 | 완료 의미 |
|---|---|---|---|
| REC→REI pure-H Peebles consumer | 10 native tests/2,170 Decimal checks PASS, scoped PROMOTE | `../loop1/peebles_consumer/` 최종 source/binary/oracle receipt | 별도 crate의 실제 REC public API 호출과 점별 환원 |
| BASS explicit clock adapter | 30 scoped tests/Decimal PASS, scoped PROMOTE | `../loop1/bass_clock/evidence/DECIMAL_RESULT.json`: 151 cases/5,001 checks | 동일 frozen cell에서 normal/conformal-seconds/conformal-length 광학깊이 일치 |
| HE mixed native gate | 2 tests/274 비교 PASS, scoped PROMOTE; HE ACK 대기 | `../loop1/he_mixed/NATIVE_RESULT.json` | 공급기 frozen reference를 실제 REI public 함수로 소비 |
| 1차 결과 종합 | actual 결과 동기화 완료, loop2 ready | unit/clock/source/실패 보존과 loop2 사전등록 | old status와 new evidence를 혼동하지 않은 공통 입력 |
| 2차 PB FLRW→BASS visibility | 6회 native/91 checks PASS, scoped PROMOTE | `../loop2/` actual history, independent matched oracle, refinement, figure | prescribed pure-H one-T expanding FLRW 검증 그림 |
| 최종 검토·전파 | 두 독립 검토 완료; 게시 receipt 별도 | independent decision, repo별 exact commit, 이중 백업 receipt | 각 repo에 맞는 bounded return과 다음 작업 갱신 |

Peebles consumer의 최초 test failure 및 각 component의 missing-API/missing-target RED는 지우지 않는다. PB 최초 9/1 failure는 exact binary input arithmetic 대신 다른 decimal literal을 비교한 test expectation 문제였고, production source/tolerance를 바꾸지 않은 10/0 correction과 원 실패가 보존됐다. 독립 `LOOP1_REVIEW.json`은 세 component를 scoped loop2 input으로 PROMOTE했다. BASS clock은 piecewise frozen normal-rate surrogate에 대한 변환이다. 변하는 a에서 a_eff=Δt/Δη를 사용하더라도 실제 q(t)의 연속체 적분 정확성을 인증하는 것은 아니다.

2차 루프는 H(z), proper nH(z), Tm=Tr(z), IC, 적분 구간과 기준을 먼저 고정한다. Source-rounded REC 상수를 유지하고 pure-H fraction에 -3Hx를 붙이지 않는다. electron density→Thomson opacity에서는 SI 변환, ray Doppler factor, clock Jacobian을 각각 한 번만 적용한다. Chemistry 적분 오차와 visibility quadrature 오차는 분리한다. 이 결과를 coupled EoR, retained-shell와 collapsed history의 동등성, 관측 우주론 또는 CMB 예측이라고 부르지 않는다.

## 저장소별 blocker와 조정

| Repo / 현재 pin | 이번에 해소하거나 전달할 것 | 남은 blocker / 소유자 | 계획 조정 |
|---|---|---|---|
| rei_bianchi `b553698a` / PR83 | static F04 완료 수신; PB 별도 consumer; HE mixed finite native 실행 | F05 첫 구간·실제 expanding coupled adapter·F08 paired history / 기존 REI owner | **F05 임계 경로 유지**. 새 PB crate와 spectral regression은 source 충돌 없이 병렬 |
| rec_bianchi `cd68764a` / PR81 | PB02 source가 그대로임을 확정; actual receiver call-site return | pure-H matched benchmark 밖의 thermal/He/native-COM/E1C gate / REC | PB 점별 모듈을 재작성하지 않는다. 이번 연결로 E1C 또는 Gate I를 승격하지 않는다 |
| bass `fecfae3c` / PR132 | 공개 repo 전환 확인; explicit clock native gap 해소; PB electron history 소비 | actual accepted EoR payload, full build, finite-T/tail 및 scalar-Q kinetic authority / BASS | 공개 per-repo return 가능. Cold-Thomson visibility와 original kinetic gate를 구분 |
| BASS_HE `28c3da14` / PR17 | F2C local RHS 수락, F2D exposure 결과 수신; mixed native 공백 해소 | RCT stepper 실제 stage/energy ledger; mixed receipt ACK; HE-F3 common-domain 불가 / REI+HE | F2D 상한 반복 계산 중지. RCT OFF baseline 유지. 동일 FT03에서 GM25 강제 사용 금지 |
| bass_cr `3c7d7d4b` / PR23 | F04C residual/J/H와 새 REI static F04 완료 연결 | 실제 CR_OFF loader/callback 관측; F04D parent/half 범위 / REI runtime+CR | F04D는 문서상 다음 작업이며 실제 dispatch 미관측. 이미 해결된 static full-map 인증을 중복하지 않음 |
| WU088_HH `3b5e7c3d` / PR33 | F07 S0 HH-OFF owner 결정 이미 수신됨을 동기화 | OFF runtime 관측; optional opt-in 때만 domain/provider/event owner / REI+HH | 옛 WAIT_F07를 반복하지 않는다. HH F1/F2는 parked이며 S0 baseline을 막지 않음 |

현재 문서의 next-task 지정은 외부 호스트 프로세스가 실행 중이라는 관측이 아니다. 다른 실행자가 같은 소유 경로에서 작업하는지 먼저 확인하고, 별도 루프를 복제하지 않는다. Root만 통합·게시 mutation을 수행하며, 후보 생성자와 다른 reviewer가 최종 bounded 승격을 판정한다.

## 진행 중 경로 밖에서 가능한 병렬 작업

1. **FLRW06 native spectral-stage 회귀**: FLRW05 immutable ZIP의 3-bin/96 positive-node 벡터를 actual `homogeneous_photo_rates`와 same-stage `PhotonInput`으로 검산한다. 새 isolated harness/결과 packet만 쓴다. 기존 F06 collisionless geometry를 다시 구현하지 않는다. 이 결과는 F08의 도움이 되는 입력이며 새 전역 필수 gate를 임의로 추가하지 않는다.
2. **Photon U/work/edge-energy 계약**: 현재 N-only balance와 별도인 U 소유권을 유도하고 적분 stage별 열·binding·redshift work를 명시한다. N/U 두 수만으로 미해결 spectrum/edge authority를 생성하거나 FT03의 photo 항을 이중 합산하지 않는다.
3. **CR/HH OFF dispatch 관측 설계**: F05의 실제 dispatch 경로가 확인될 때 REI owner가 source/provider load와 callback의 0을 직접 관측한다. flag 또는 null이 0의 증거가 아니다. 별도 원자 계산을 시작할 이유는 없다.
4. **F04D parent/half 보조 이론**: CR에서 실제 새 parent와 half1→half2 의존관계를 대상으로 mixed derivatives를 준비할 수 있다. F05의 production source에 동시 수정하지 않는다. 이미 static F04가 닫은 범위를 다시 인증하지 않는다.
5. **RCT stepper/response 사전 설계**: 현재 local RHS와 conditional energy ledger를 actual implicit source-site에 어떻게 넣을지 분리된 계약으로 준비한다. 실행은 별도 write reservation 이후다. Direct exposure→전체 observable 변화의 전파에는 admitted baseline stability/Jacobian 정보가 필요하다.
6. **BASS actual-history receiver**: REI에서 accepted expanding history가 반환되면 proper ne/time/frame/observer-tail을 검증하는 소비기 작업만 수행한다. Chemistry owner를 새로 만들지 않는다.

HE의 현재 FT03 온도창 30,000–110,000 K와 GM25 200–10,000 K는 교집합이 없다. 따라서 OFF/KF96 감도 비교는 가능 범위에서 별도 의미를 갖지만 HE-F3의 OFF/KF96/GM25 완료가 아니다. 온도를 clamp하거나 provider를 자동 교체해 이 blocker를 없애면 안 된다. F09의 matched optional atomic campaign은 REI에서 한 번만 실행하고 HH/HE는 동일 receipt를 받아 검토한다.

## 원래 atomic 연구와 장기 확장

기존 `LEGACY_LANE.json`, source manifest, 오류·실패 및 수락 범위는 보존한다. 재개 조건은 명시적 사용자 범위, actual source-domain 초과, 관측량 감도에서 확인된 precision 필요, 또는 구체적인 spectral/thermal/event 소유권 요구다. 단순 새 게시나 unchanged OFF 상태는 재개 조건이 아니다.

- HH: accepted 24/289, unbounded 265, epsilon_C/epsilon_R null, B22 OPEN 유지. 실제 opt-in/changed consumer evidence가 없으면 helper/toy를 추가하지 않는다.
- HE: 원래 atomic source와 spectrum/heat/recoil 미해결 상태를 유지한다. RCT provider의 수치적 source 차이를 확률적 불확실도로 바꾸지 않는다.
- CR: G02 unresolved, capture=false, all_bound OPEN, b_grid NO_GO 유지. CR_OFF 실행 경계와 원래 CR 물리 문제는 다르다.
- REC: selected-He fixed-input port의 최신 scoped review PASS를 받아들이되 Gate I와 E1C native/COM 중복 owner는 별도다.
- BASS: finite-temperature tail과 scalar-Q collision generator는 원래 gate로 남는다. Visibility 검증만으로 full kinetic/CMB lane을 완료 처리하지 않는다.

## 전파와 상태 기록

각 원자 repo의 기존 branch/PR에 새 `consumer_returns/<이번 root task ID>/`를 추가하고, source binding·bounded result·다음 단계 문서를 게시한다. REI/REC/BASS에는 실제 바뀐 native 파일과 해당 범위의 연구 packet을 연결한다. 원 canonical TASKS와 옛 receipt를 덮어쓰기보다 이 successor가 대체하는 **상태의 범위**를 명시한다. Root가 게시 직전에 live ref와 관련 diff를 확인한다.

`REVISED_DAG.json.publication`은 순환 self-hash를 피하도록 Git/Drive/Dropbox의 최종 receipt를 가리킨다. 실제 provider 완료와 필요한 metadata 검증은 그 receipt에 기록한다. Git 게시, 다른 스레드의 실제 수신 ACK, 직접 ChatGPT 메시지 전달은 서로 다른 상태다. 이 초안에는 후자의 성공 주장이 없다.

끝까지 보존할 기존 gate는 strict local <2e-4, public width <2e-3, [160,161] FAIL=2.1245050576368385e-4 및 prefix160이다. 새 static/finite benchmark로 그 실패나 원래 46,080-node/3-lane history를 소급 승격하지 않는다.

## 게시 직전 successor overlay

이 파일 앞부분의 intake 시점 후보 목록은 아래 최신 결과로 해당 범위에서 대체한다. FLRW06 native 회귀는 prepared driver/source를 그대로 사용한 actual18records/167scalars로 완료했다. 독립 U 소비자·accepted coupled stage/history는 미완료다. CR-F04D는 새 owner의24tests/parent·two-half event jets 완료 반환을 수신했다(여기서 재실행하지 않음). 다음은 실제 F05 stage/time/units/accepted-step을25-output계약에 묶는 F04E다. 따라서 더 이상 FLRW06 native나 F04D를 새 병렬 미실행 작업으로 선택하지 않는다. 현재 병렬 후보는 native U/edge/work 소비자 계약과 실제입력 조건을 만족한 F04E binding이다. Machine-readable REVISED_DAG가 이 successor 상태를 반영한다.

## 최종 동시 owner 반환을 반영한 현재 실행 순서

앞의 intake 표는 역사 기록이다. 현재 우선순위는 REI F08 전체 paired history다. F05 actual static FT03 interval은3grids/7000accepted/MPFI200PASS로 완료 수신했고, F08 conditional coupled stage도 구현·140tests 검증 수신했다. Full paired history 및 physical admission은 미완료이며 owner 반환을 여기서 재실행하지 않았다. CR F04E는 이제 실제 F05 receipt를 읽어 exact stage/time/unit/25-output binding을 준비할 수 있다. U/edge/work consumer contract와 OFF runtime 관측 설계는 다른 write boundary에서 병렬 가능하다. FLRW06 양쪽 동시 실행은 한 완료 gate이며 다시 실행하지 않는다. cutoff `bda0feefd4957dc59ebf4b068d01690942aa0a2a`; machine-readable DAG의 final_received_overlay가 현재 상태다.
