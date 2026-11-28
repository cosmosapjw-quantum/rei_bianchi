# HE29 → REI 최신 백업·다른 대화 intake

## 결론

2026-10-21에 접근 가능한 백업의 변경분과 기존 intake 경계를 읽었다. **새 BASS S12 실제 실행 반환을 발견했고, archive 전체 바이트와 포함된 두 native binary의 identity를 읽었다.** 저장된 재개 SUMMARY는 `PASS`이며, 16개 완료 작업을 `SKIPPED_EXACT_PASS`로 재사용하고 실패한 `case_parallel`만 완료했다. PR 본문의 `NOT_RUN`만으로 현재 상태를 판단하면 이 반환을 놓친다.

HE29의 완료 reference **4/4**와 packed canary **1/1**은 그대로 재사용한다. 이 intake에서 NCP 제출·시작·native 호출·과학 검사·벤치마크는 모두 **0**이다. 기존 HE29 `a00990e5…` 반환과 `dc188d52…` closeout은 다시 내려받거나 검증하지 않았다.

기계 판독용 전체 기록은 `BACKUP_CONTEXT_INTAKE.json`, 실제 변경 metadata는 `BACKUP_METADATA_DELTA.json`, provider 응답은 `metadata_pages/`에 있다. 아래 완료 수는 각각의 원래 계약 안에서만 유효하며 HE29 완료 수에 합산하지 않는다.

## 새 실제 반환과 재사용할 수 있는 근거

| Lane | 실제 관측 | 현재 해석 |
|---|---|---|
| BASS S12 | 새 ZIP 157,420,884 bytes, SHA256 `eb522092a7e466d95d87797795fb080583dc0b987555dcaba00ea2fd62813709`; Dropbox content hash 일치 | 새 전체 raw GET과 제한된 identity 읽기 완료. 과학적 admission을 새로 실행한 것은 아니다. |
| BASS S12 initial | 2026-10-21 03:21:30 UTC: 17개 job 중 16 PASS, `case_parallel` FAIL | 실패 기록을 보존한다. |
| BASS S12 resume | 03:24:22 UTC: 16 `SKIPPED_EXACT_PASS`, `case_parallel` PASS, 전체 PASS | 완료한 16개를 재실행하지 않은 실제 재개 근거다. |
| BASS S12 ensemble | `PASS_NEW_EXTENDED_ENSEMBLE`, 14/14 cases = 11 full + 3 omission controls, 30/30 저장 검사 PASS | 고정 k16/n64 manufactured histories, FD/Richardson, GL gauge, MF6/clock7, baseline/fused, omission 식별 범위다. continuum/full spectral certification은 false다. |
| REC U4B | 16,076,737-byte 새 반환의 raw GET; 32 steps, 74443→74475, `PASS_SCOPED_U4B_NUMERICAL_RESTART` | `NO_EVENT_WITHIN_BOUND`. REI activation false, 전체 allocation CPU/wall unresolved, 기존 cap CLOSED_HOLD_NOT_RESET. 새 allocation을 승인하지 않는다. |
| bass_cr C21K | source `bab323983dad5206e162dbfdaefc167f2fabea45`, 문서 `dc1c0c0721b74454958e5d16264c24ec465ba1d8`, PR89 | 새로운 구현·가벼운 검증 완료 기록. C21K native/IVP 실행은 0. epoch cache 설계 재사용 후보다. |
| HH PHYS73 | `REPORTED_EXECUTION_PRESERVED_RAW_RETURN_INTAKE_BLOCKED`, PR126 `c928d7876c59d87ae496d6f0873b42d15f563884` | 보고된 결과와 raw 미확보를 구분한다. exact-name Dropbox 검색 0건이 모든 저장소의 부재를 뜻하지 않는다. 기존 실행을 재개하지 말고 이미 존재하는 raw ZIP/ACK를 확보하는 문제다. |
| REI LRS | PR198 결과 `444f9d806a4070668e1e6d15b79b75db2b110e62`; planned246 / complete144 / cap-not-run100 / dependency-blocked2 | scientific HOLD, production NOT_ISSUED. receipt의 dual raw PASS를 재사용한다. |
| REI age | 기존 v10 delivery 실제 읽기, 이후 v11 TASK 120,441,887 bytes와 DELTA 164,639 bytes 존재 확인 | v10을 최신 결과로 취급하지 않는다. 현재 Git 분석 담당자가 v11의 결과/코드 범위를 연결한다. |

### BASS S12 source / binary identity

실행 과학 코드 source는 `f4cd0d53760783e6a58c3b0a98c64311ca489d28`, tree는 `a9048818707ef3f446528631c3b5d6c8171116cc`다. 실행 package의 파일명 pin은 `8247645d…`로 과학 source pin과 구분한다. manifest SHA256은 `ef4d8210e43341ba3cbb2dbe2ee81cfe1894a1356473851e01d17205b56b2965`다.

ZIP 안의 실제 binary bytes를 읽어 build receipt와 직접 대조했다. 실행하지 않았다.

| Binary | Bytes | 실제 SHA256 |
|---|---:|---|
| s12-core | 551,856 | `ca03440428c1a1c4397c19200367084f202685d3913581cbaafbd7b79f33104c` |
| s12-history | 5,921,552 | `ad74ec3629afc0934a297ea4fa5159f681f254b20431d704a1fb5cb38b4d794e` |

VigilODE는 기존 `a21d573980f66fe02891bd216153443b5352f921`다. 새 실제 raw archive의 member index는 9,902개 regular files로 Cargo/build 자료까지 포함한다. 이는 9,902개 새로운 과학 결과라는 뜻이 아니다. 선택 원문은 `new_archives/bass_selected/`의 `ENSEMBLE_RETURN.json`, `entry_00.json`(build), `entry_13.json`(initial), `entry_14.json`(resume), `BINARY_BYTE_INTAKE.json`이다.

이 기록에서 재사용할 수 있는 것은 전체 독립 case 병렬화, 원래 reduction 순서 보존, 완료 artifact의 정확한 identity 기반 재개, source-bound binary와 결과를 함께 남기는 구조다. 당시 CPU 0..62 고정 할당은 현재 다른 작업과 공유하는 서버에 그대로 옮기지 않는다. 현재 가용 cpuset·quota·RAM과 lane별 CPU 제외 규칙을 읽어 새로운 자원 배정을 계산해야 한다.

### C21K에서 바로 참고할 최적화 설계

고정 fixture/source/globals 계약 안에서 cell별 epoch opacity 계수를 캐시한다. binary64 bit key가 signed zero를 보존하고, cell/kernel별 LRU16과 finite-success-only 삽입으로 메모리 사용과 실패 상태 재사용을 제한한다. immutable byte backing에서 독립 writable 결과 사본을 반환하고, 기존 left-associated 계산 순서를 유지한 공통 항 계산을 사용한다.

기록된 M9 exp 표현 28→2, M81 244→2는 구조적 연산 수 변화다. 캐시 hit는 native 호출 생략 수나 측정 속도 배율이 아니다. 다른 lane의 69개 full RHS 제거와 합산하지 않는다. 신규 C21K native 속도와 NCP64 scaling은 NOT_EVALUATED다. 52개 logical slots에서 historical 완료 3개를 제외한 nominal49도 모든 분기를 동시에 실행하라는 승인이 아니다.

C21K 백업은 receipt 자체가 remote payload raw readback false라고 기록한 **R2 manifest/provider metadata**다. 여기서 archive를 다시 받아 R3으로 승격하지 않았다. 가용 자원 정책의 host identity·expiry·effective CPU·RAM 예약 아이디어만 현재 코드에 맞게 검토할 수 있다.

## 실제 조사 범위와 한계

기존 `INTAKE_BOUNDARIES.json`, `BACKUP_DELTA_INTAKE.json`, `PERSONAL_CONTEXT_INTAKE.json`을 먼저 읽었다. 변경 metadata 기준은 `2026-10-20T06:00:00Z`이며, 수정 시각이 이후라는 사실만으로 새로운 과학 실행이라고 분류하지 않았다. provider 간 복사본과 폴더 범위가 겹치므로 아래 수를 고유 결과 수로 합산하지 않는다.

| Dropbox 범위 | 응답 항목 | 페이지 | 마지막 has_more |
|---|---:|---:|---|
| Root immediate index | 454 | 1 | false |
| BASS_DERIVATION_DOSSIERS_20260912 recursive | 4,664 | 8 | false |
| BASS_BACKUPS recursive | 78 | 1 | false |
| bianchi/research_backups/rei_bianchi recursive | 59 | 1 | false |
| REI_POSITIVE_AGE_REFERENCE_BACKUPS recursive | 38 | 1 | false |
| bianchi/rec_bianchi/20261016 recursive | 76 | 1 | false |
| ode_solver recursive | 3 | 1 | false |
| `20261021` 검색 | 56 | 1 | false |

Drive에서는 관련 이름의 folder index 34개를 읽고 7개 실제 folder의 direct children을 읽었다. BASS dossier1000, BASS58, REI age141, REI13, REC17, bass_cr69, VigilODE8이다. **Dossier1000은 요청 상한에 도달했고 list_folder는 continuation 인자를 제공하지 않았다.** 가장 오래 반환된 수정 시각은 2026-09-26으로 이번 변경 기준보다 이전이지만, 완전한 recursive Drive 전수조사라고 주장할 수 없다. 관련 이름 filter에서 빠진 폴더, 별도의 HH 루트 하위, 미게시 NCP 파일시스템은 미관측이다.

다른 대화의 이번 실제 응답은 `Personal context is unavailable for this conversation.`이며 isError=true다. 한 번만 요청하고 재시도하지 않았다. 이전 bounded query가 성공해 오래된 pre-canary 문맥을 반환했던 이력과 별개다. 모든 대화나 미게시 원격 결과가 없다고 주장하지 않는다.

## 실패 이력과 이번 조치

Drive의 첫 metadata query가 `contains(name,...)` 문법 때문에 INVALID_ARGUMENT를 반환했다. `name contains ...`로 수정한 read-only query는 성공했다. 이는 UNKNOWN upload 재시도와 무관하다.

새 BASS/REC archive GET의 첫 sandbox 요청은 URLError, 0 bytes였다. 허용된 network escalation으로 동일한 read-only GET을 수행한 두 번째 시도에서 HTTP200, 전체 크기와 Dropbox content_hash가 일치했다. 두 시도의 실제 영수증을 모두 남겼다. REC는 요청이 진행되는 동안 다른 담당자가 같은 작은 Git 결과를 읽었으므로 독립 과학 검증을 추가하지 않았다.

Remote Desktop Commander 호출, Drive upload/UNKNOWN retry, 프로세스 signal, Git 변경, 클라우드 write는 모두 0이다. 큰 새 archive는 로컬 intake 근거로만 보유하며 Git에 포함할 대상은 선택 원문·metadata·요약이다.

## DAG / 게시 / 백업 상태

| 단계 | 상태 | 근거 / 다음 연결 |
|---|---|---|
| I0 기존 실제 범위·실패 이력 읽기 | DONE | 기존 3개 intake 파일 재사용 |
| I1 다른 대화 변경분 | DONE_WITH_UNAVAILABLE_ERROR | 실제 오류 응답 보존, 전면 부재 주장 없음 |
| I2 접근 가능한 backup delta | DONE_WITH_SCOPED_COVERAGE_GAPS | Dropbox pagination 완료, Drive cap 및 비재귀 한계 명시 |
| I3 새 반환 identity 읽기 | DONE | BASS/REC 새 raw GET, BASS 실제 binary bytes 일치, 선택 saved records |
| 새 이론·코드 연구 | 이 intake 담당 범위 밖 | 부모 연구 루프가 새 결과를 반영하여 진행 |
| Git 게시 | LOCAL_EVIDENCE_READY_FOR_PARENT | intake 담당은 remote mutation을 수행하지 않음 |
| 이번 보존 | 기존 provider backup 존재 및 새 local evidence | 부모의 새 단계별 보존에 포함할 compact evidence 준비 |

다른 Codex 세션이 존재한다는 이유만으로 전체 작업을 HOLD하지 않는다. 실행자는 해당 lane에 허용된 미완료 작업만 현재 가용 자원 안에서 배정하고, 실제 source·결과 identity가 같은 완료 작업은 건너뛴다. Σ/Π preliminary plot으로 연결할 때에도 이들 유한 모델 결과를 연속 스펙트럼·전체 EoR·Grackle 동등성 또는 관측 Bianchi/CMB 승인으로 확대하지 않는다.
