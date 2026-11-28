# HE-EXP-DRIFT-02 공급자 원전 인계

2026-10-27 UTC. 이 묶음은 최신 WU 종·사건 공급자의 **소비자 투영**이다. WU의 종 ID, 상태, 사건 열, 공급자 레코드를 재정의하지 않는다. 원전 JSON 파싱·바이트 식별·참조 관계 검사만 실행했고, 충돌률·Q·질량 환산·transport fit·ODE·기존 compiler 또는 과학 suite는 실행하지 않았다.

## 고정 입력과 현재 관측

| 소유자 | 확인한 branch/HEAD | 이 묶음의 역할 |
|---|---|---|
| WU088_HH | `research/provider-registry-20261025` / `87933da5654bb2e4d93f7de4341df5e0fa0f8716` | 현행 AGENTS, R1/R2 원전 종·사건·공급자·범위 |
| BASS_HE | `research/program-expansion-20261025` / `ac6042a6b0610b09d0576538767ee0299389a5eb` | 기존 32-row fixture 소비자 인벤토리 재사용 |
| rec_bianchi | `research/program-expansion-20261025` / `4a8e541030ee2cbd02e26ba671083b705d309d49` | 최신 HD/H5 결과 재사용 |
| bass_cr | `research/program-expansion-20261025` / `b11b2e9255f2b10fb5582376412e045bd1e9151c` | 완료된 He4 ground capture 및 외부 소비자 결과 재사용 |

WU R1 과학 소스는 `18a6804d7cbe4879701e83631f7e908bbb84cef1`, R2 과학 소스는 `71019bb469c92d1ea665155ed98c472b362d6706`이다. 위 최신 WU metadata HEAD의 원전 파일을 정확히 고정했다. 파일마다 repository, commit, path, Git blob, SHA256, byte 수는 `SOURCE_MANIFEST.json`에 있다. WU branch HEAD는 투영 직전에 다시 조회하여 동일함을 확인했다. 하위 소유자의 과거 completion과 실제 backup 상태를 이전 미완료 상태로 되돌리지 않는다.

## 실제 원전 범위

| 구분 | R1 | R2 추가 | 합계/해석 |
|---|---:|---:|---|
| 종·상태 ID | 92 | 0 | R2는 기존 9개를 동일 레코드로 재사용 |
| 공급자/source variant | 102 | 26 | 128개 원전 참조 |
| 정수 사건 열 | 125 | 24 | 149개 원전 참조; 새 compiler 실행 없음 |
| 사용자의 원래 nuclear target | — | 19 | 19개 ID를 모두 유지 |
| 원래 방향 | — | 28 | 27개에 primary source reference; target6 forward 공백 |

92개의 역할 분류는 atomic70, molecular17, neutron1, anion1, electron3이다. 이는 동시에 진화시켜도 되는 92개 독립 population이라는 뜻이 아니다. WU가 규정한 unresolved aggregate와 resolved states는 partition map 없이 함께 진화시키지 않는다. 원전 historical view의 20개 원자 전하상태와 neutron1을 직접 유지하고, 같은 composition/charge/pool의 상태별 후보는 서로 합치지 않고 나열했다.

분자 17개는 H2 unresolved·ortho-H2·para-H2, H2+, H3+, HeH+, HD J0…8, Li6H1·Li7H1이다. HD의 진동·전자 상태와 일부 UMIST 종의 상태는 원전의 미해결 표시를 유지한다. 음이온은 H- 하나이다. electron thermal 자유종, electron fast 자유종, UMIST의 source-pool-unresolved 종을 구별한다. 마지막 종에 사용된 electron_thermal 좌표를 새 열화 승인으로 읽지 않는다.

기존 HE 32개 fixture는 historical material21 + electron2 + synthetic extension9이다. 현재 source-resolved 상태와 `ground`, `free`, `synthetic`라는 fixture 문자열은 자동 동치가 아니다. `legacy_fixture_crosswalk`는 composition/charge/pool 후보만 제공하고, 상태 차이·synthetic 표식을 보존한다. `92−32`를 새로운 물리 종의 수 또는 coverage 개선량으로 해석하지 않는다. C12·C13·C12m·C12C13 fixture는 현재 원전에 대응하는 종이 없는 synthetic 확장으로 남는다.

원전 nuclear catalogue의 5,843행(ground3,558/non-ground2,285)은 별도 catalogue이다. 이를 활성 network로 확장하지 않는다. 현재 92개 중 비바닥 nuclear isomer는 0개이며, 전자 여기상태를 nuclear isomer로 세지 않는다. catalogue의 모든 non-ground가 isomer라는 주장도 하지 않는다.

R2는 원래 PNG 복원과 19 target 목록 확정이 끝났다. R1의 과거 locator 미복원 상태를 현행 open gap으로 반복하지 않는다. 다만 `TARGET19:06:target_forward`, 즉 He4(gamma,dd)의 수치 원전은 여전히 없다. exclusive deuterium, factorized He3, inclusive Li7, response-averaged He4 공급자를 서로 교환하지 않는다. source reference 존재는 계수·state branch·에너지 소비자 승인과 별개이다.

## 질량 convention

WU 기존 mass packet은 bare nuclear ground mass 5개(p,n,d,t,helion)이다. He4 bare, Li6 bare, Li7 bare 행은 여전히 missing이다. 이 값으로 neutral H나 neutral He의 질량을 채우지 않았다.

`NEUTRAL_H1_HE4_MASS_CANDIDATES.json`은 독립적인 소비자 후보로 다음 두 중성 바닥상태에만 연결한다.

| WU species ID | 상태 | NIST 상대 원자질량 Ar |
|---|---|---|
| `sp_7b3d2e472131e6c645d7` | H1 neutral 1s ground | `1.00782503223(9)` |
| `sp_17efcd73203997543678` | He4 neutral electronic ground | `4.00260325413(6)` |

이 NIST isotope table은 AME2012에서 유래하고 데이터 마지막 갱신은 January2015라고 소개한다. 페이지 자체의 최근 수정일이나 다른 AME 평가를 이 데이터의 vintage로 바꾸지 않는다. 단위 변환 후보는 CODATA2022의 `m_u=1.66053906892e-27 kg`, 표준 불확실도 `0.00000000052e-27 kg`이다. 따라서 isotope mass와 SI unit conversion의 혼합 vintage를 명시한다. kg 곱셈은 이 source intake에서 실행하지 않았고 부모의 별도 검산에 맡긴다.

Ar 사이 또는 Ar와 m_u 사이의 covariance는 공급되지 않았다. 독립성을 가정한 제곱합 불확실도나 transport 모델 오차를 만들지 않는다. neutral mass를 고정했다고 isotope-specific scattering의 empirical calibration, quantum correction, source-fit 오차 또는 전역 물리 정확도가 승인되는 것도 아니다.

이 숫자는 실제 읽은 NIST primary page의 field transcription이다. 직접 HTTPS로 원본을 저장하려던 세 시도는 모두 HTTP403 SERVICE_ERROR였으며 `NIST_HTTP_RECEIPTS.json`에 보존했다. 원본 HTTP bytes는 없고 raw SHA256은 null이다. local transcription의 SHA256과 원본 페이지의 hash를 혼동하지 않는다. 원문 URL과 column/provenance locator는 질량 packet에 있다.

## 재사용 결과와 다음 연결

REC의 HD adapter는 9 levels,8 lines,2 colliders,18 collision pairs,54 rates를 이미 파싱했다. collision temperature는 정확히 50/100/200 K이고 ortho/para H2는 분리된다. 35 Hz line bridge는 J1→0 하나만 통과했고 나머지 7개는 실패하여 `HOLD_SOURCE_DISCREPANCY_UNQUALIFIED`이다. H5의 작은 interpolation 표현 오차를 physical error로 올리지 않는다. 물리 예산은 null이며 313 query의 물리 coverage는 0이다.

CR은 He4+ ground1s +e → He4 ground singlet +spontaneous photon 채널과 외부 소비자 인터페이스까지 완료했다. native threshold24.59 eV, stationary heavy target/recoil0인 scoped 결과를 재사용한다. fast electron의 E, internal binding의 I, photon의 E+I는 단일 사건의 서로 다른 소유 항이다. retained photon과 escaped Case A 처리는 별도다. 일반 finite recoil은 이 결과에서 승인되지 않았다.

HE의 다음 실제 작업은 부모가 수행하는 같은 상대속도 법칙의 Q11/Q12 finite-drift moment 연결이다. 원전 Bruno paper DOI `10.1063/1.3495980`의 classical heavy-particle scattering 및 H–He potential locator를 `PRIMARY_SOURCE_POINTERS.json`에 정리했다. mass-independent classical potential의 isotope-mass 해석은 조건부 모델 유도에 속한다. calibrated source error, joint parameter covariance, full differential final-state law는 이번 intake에서 회수되지 않았다. total/scalar rate, thermal collision integral, A-value 또는 beam-average를 완전 미분 공급자로 승격하지 않는다.

열용량은 독립 population 고정 시 열적 내부에너지의 편미분이고, 입자수 및 그 생성항과 구별한다. 명시적 excitation·binding·molecular·nuclear energy, 비열적 pool, bulk momentum work와 thermal heating에 각자의 소유 항을 둔다. 새로운 source provider가 두 번째 에너지 소유자가 되는 일은 없다.

## 실행과 재현

`build_consumer_projection.py`는 같은 디렉터리의 고정 JSON만 읽는다. source identity 또는 consumer projection 입력이 바뀔 때만 재생성한다. WU registry/compiler를 import하지 않는다. `CONSUMER_PROJECTION.json`과 `SOURCE_INTAKE_RESULT.json`은 한 번의 실행으로 작성했으며17 source files/1,828,583 bytes,340개의 hash·참조·원전 상태 검사 모두 통과했다. 과학 평가0, 질량 환산0, compiler 실행0, 과거 suite replay0이다.

최초 큰 source payload를 shell argument로 쓰려던 호출은 `Argument list too long`으로 process 시작 전 실패했다. 이를 지우지 않고 receipt에 보존했으며, 파일 쓰기 방식만 apply_patch로 바꿔 정확한 Git blob을 검증했다. NIST HTTP403 세 건도 별도 원형 receipt를 유지한다. 이 기계적 실패들이 HE101, PHYS91 또는 기존 완료 과학 예산을 재설정하지 않는다.

부모의 독립 검토·새 finite-drift 검증·expected-SHA non-force publication·ZIP/Dropbox/Drive/DAG 기록은 별도 완료 증거이다. 이 소스 투영 자체는 HE101 C8 OPEN, 기존 소진 예산, HH_R10 OFF, production NOT_ISSUED, L4_ready=false와 global physical completion=null을 유지한다.
