# REI 통합 상태 — 2026-10-21, D0/D1 회수 완료
현재 기준은 실제 원격 HEAD, 회수된 source/raw/receipt와 새 실행 계약이다. 대화의 완료 문구는 검색 단서로만 사용했다.

## Lane별 현재 상태
| Lane | 실제 source / 위치 | 실행·검토 상태 | 게시·보존 상태 |
|---|---|---|---|
| A: PR198 | HEAD 8bd35af5f11c7ea5945b656be1c013d1c1933498; reviewed b140170ce0c58159368b6b81be49ac35ca764851 | 625 기존+606 신규, 총1231 unique trajectories, z20→4, half-contraction. PASS_SCOPED_PRELIMINARY 유지 | 기존 Git 게시 및 양쪽 archive/ACK 전체 readback 검증 |
| B: 최초91점 | PR147 kernel 3b85dedce84d37b3e165da00685a8a984950aafe; executed wrappers UNPUBLISHED_WITH_SHA256 | 91 nominal+3 refined, 94개 raw 전부 회수·manifest 검증; Frobenius,40/56 states,121 epochs,z20→4. 기존 C9 PASS_SCOPED_PRELIMINARY 재사용 | 과거 staging은 PENDING_EXPECTED_HEAD_FF, 실제 Git 게시/전체 백업 미완료. 이번 D0/D1 checkpoint로 보존 중 |
| B:175점 | recovered COMPONENT_CONTRACT 및 component_adapter.py; 원본91과 같은 vendor | PARTIAL_WITH_VERIFIED_RAW:35 exact reusable,140 new nominal 미실행,3 new refined 미실행 | 계약 backup만 과거 확인; 새 source/result 게시 예정 |
| C:PR199 AGE | HEAD964b2e3c098f6e475999a4eddc7a6aa0f8f053cc, task tree0a45ca2d8fec1381d4cc1c0852f2ca3b0721c44c | NATIVE_AGE_TIME_CONVERGENCE=HOLD; NONLINEAR_GRACKLE_RESPONSE_BOUND=NOT_ESTABLISHED | 역사적 결과 보존; 이번에 AGE재실행 없음 |
| D:PR213 split729 | HEADd32cd99fa19c65aa1ca63dbc8aab8741834270e8 | a=.1999→.2 native warm slice; z20→2와 다른 모형/구간 | 기존source 참고, 과학raw 통합하지 않음 |

공통 production admission은 NOT_ISSUED. PR198/199 전체 CI verify는 failure이며 scoped pilot review와 구분한다. V12 cap180/debit200.39897231891518/remaining100 NOT_AUTHORIZED 유지.

## 실제 회수 결과
PR198 final archive:37,945,383B, SHA2562c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d. Drive/Dropbox 전체GET 동일;5747payload+manifest 모든 member size/SHA 검증.
LaneB original RAW_RESULTS:4,494,862B,SHA2564699dfe6f559ae4011b7ccfed1936ac35e80163cd54f6bfd9a9853aabd96d6c9,376members. 이전 scratch의 source/raw/review를 읽기 전용으로576files/11,832,521B 복구; source 변동0. 그 경로는 계약 review에서 실제 발견했고 임의 추정하지 않았다.

## 비교 및 재사용
A/B의 canonical_fv.py,lrs_boltzmann.py,species_hierarchy.py,cosmology lock은 byte-identical. A half→B Frobenius는 sqrt2 사상이다. A 8-state reduced source와 B40/56-state source, case axes/output grid/실행 wrapper는 다르다. 관계 COMPARABLE_AFTER_EXPLICIT_TRANSFORM; 동일IVP raw 자동대체 없음.
B내부35는 실제 config/raw/input/receipt hash로 IDENTICAL_REUSABLE_CASE. PR213은 QUALITATIVE_COMPARISON_ONLY; AGE→collisionless science admission은 NOT_COMPARABLE.

## 다음 승인 실행
B1:이미 승인된 미완료140 nominal+3 refinement만 수행,35점은 exact reuse.
B2:94 original+143 new=237unique full states를z4→2만 연장;121prefix+32new=153epochs.175joint와91radiation grid는35점을 공유하므로 nominal unique count231.
정확한 계약과 사전 PHYS-MATH review는 UNIFIED_EXECUTION_CONTRACT.md와 PHYS_MATH_CONTRACT_REVIEW.json에 있다. 과거94/PR1981231/AGE계산 재실행0.

## 검색 범위와 현재 환경
REI254branches/212PR entries, BASS261branches,VigilODE184branches 전체pagination 완료. 관련4개 REI recursive trees는 nontruncated. 개별 source/receipt는 관련 경로를 선별했고 모든branch bytes/모든대화를 읽었다고 주장하지 않는다. 연결 대화검색도 실제 수행했으며 결정적인 원자료는백업→계약review→이전scratch 경로로 회수했다.
Current-turn Python=PYTHON_PASS,C++=CPP_PASS. 로컬 quota8CPU,8GiB. NCP owner checkout/affinity/RAM/disk/process 상태는 NOT_OBSERVED:local key없음;현재 DesktopCommanderget_config가월사용량 SERVICE_ERROR와 do-not-retry를 반환했다.재접속하지않고 로컬 bounded 실행 계속.

