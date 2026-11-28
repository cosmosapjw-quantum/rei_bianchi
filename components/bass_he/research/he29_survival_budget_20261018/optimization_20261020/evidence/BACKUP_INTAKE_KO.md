# HE29 관련 백업 및 교차 저장소 입력 확인 — 2026-10-20

## 판정

이 조회에서 HE29 새 native 반환은 **0건**, 요청한 기준해 네 쌍의 새 인정 결과는 **0/4**이다. 인정하려면 고정 실행 source revision, 실제 binary identity, source-table identity, 실행 출력이 함께 있어야 한다. 기준은 m8/GL4/q0의 `(r2,512)`, `(r4,512)`, `(r8,512)`, `(r4,1024)`이며 각각 Radau와 DOP853 결과를 요구한다.

직전 publication `329f838399f24d3952f780d469ad657d8630c4e2`의 게시 시점인 2026-10-19 13:49 UTC 이후 반환을 우선 조사했다. 이 담당자의 조회는 2026-10-20 02:38:46–03:07:35 UTC에 수행했다. 이전 handoff의 `0/4 NOT_RUN`을 재사용하며, 백업에서 인정할 반환을 찾지 못했다는 관찰이 현재 원격 프로세스 상태를 독립적으로 증명하지는 않는다.

## 실제 조회 범위

| 경계 | 실제 확인 | 완전성 및 한계 |
|---|---:|---|
| Drive 관련 폴더 | 관련 폴더 직접 목록 264회 + 루트 발견 1회 | 식별된 관련 하위 트리를 잎까지 확인; 남은 재귀 큐 0, 오류 0, 재귀 목록 cap 0 |
| Drive 초기 하위 폴더 | 40폴더 / 885개 직접 항목 | canonical 27개와 REI 13개 하위 폴더 |
| Drive 추가 재귀 | 214폴더 / 733개 직접 항목 | 처음 관찰한 68개 하위 폴더 및 다른 관련 루트의 45개 하위 폴더에서 이어진 전체 관련 트리 |
| Drive canonical 직접 파일 | 수정 시각 내림차순 최신 1,000개 | 2026-09-26 07:04:33–2026-10-19 20:04:08 UTC로 cutoff 이전까지 포괄; 도구에 직접 목록 pagination이 없어 전체 역사 목록으로 표현하지 않음 |
| Dropbox canonical 직접 목록 | 6페이지 / 3,244개 고유 항목 | 마지막 `has_more=false` |
| Dropbox canonical 전체 재귀 | 8페이지 / 4,607개 고유 항목 | 마지막 `has_more=false` |
| Dropbox 기타 관련 저장 경계 | BASS 50, REI 41, REI hierarchy 28, bass_cr 15, rec 보존 57, rec 날짜 백업 54+4, ODE 3, Rust 루트 9·bundles 6, WU 1 | 각 지정 경계의 직접/재귀 구분은 동봉 공개 JSON에 기록 |
| Dropbox 제목 검색 | HE29 7개, VigilODE 13개 | 두 검색 모두 마지막 `has_more=false`; BASS_HE 검색은 알려진 HE29 이름을 재현하지 못해 부재 근거에서 제외 |
| 추가 Git 읽기 | rec_bianchi 최신 PR 10개, PR109 변경 파일명 431개, REI PR208 변경 파일명 896개 및 지정 immutable receipts | root와 다른 담당자의 저장소 조회를 중복하지 않은 이 담당자의 범위 |

Rust 설치 내부의 별도 부분 목록은 완전한 toolchain inventory로 주장하지 않는다. 접근 가능한 지정 관련 경계에 대한 결과이며 다른 계정이나 알려지지 않은 저장 표면의 전체성을 주장하지 않는다.

## 새 업로드와 실제 새 실행의 구분

| 후보 | 실제 읽기 및 identity | HE29 판정 |
|---|---|---|
| BASS S9 ZIP | 604,752 bytes 전체 GET, SHA256·141개 ZIP member·README와 handoff 읽음 | bass PR174의 S9 source/preregistration; 8 histories NOTRUN |
| 새 임시 보존 archive 15개 | 합계 122,748,018 compressed bytes 전체 GET; 15/15 TAR 전체 목록·선택 provenance 읽기, 오류 0 | HE18 C3–C9, E13 captured-step enclosure, 2026-10-10 REI physical-provider 묶음; HE29 이름의 내부 member 0 |
| REI RUN18 | resume 문서를 직접 읽어 source `6c0ae2a2ba63d42e23c7b79f989fa64639f4c942`와 범위 확인 | exact depth 표현 수리; 새 gas RHS/IVP/quadrature 실행 0 |
| REI LRS V14 | 병렬 담당자의 immutable PR198 실행 receipt 읽기를 재사용 | q0/cells8/n_mu8의 LRS Radau·SSPRK2 19/19; HE29 네 기준해 쌍과 model/solver identity가 다름 |
| REACTIVE06 | PR208 immutable publication·raw-readback·science receipt와 archive 이름·크기·provider identity를 정확히 연결 | frozen BR05 gas operator; nonlinear histories 0, macrosteps 0; 기존 70,567,867-byte readback 근거 재사용 |
| rec R3O 보존본 | PR109 immutable 보존·복구·백업·입력 receipts 및 복사된 HE29 DAG 두 개 직접 읽음 | recombination grid 작업; 복사된 HE29 handoff는 기존 24,809-byte 묶음이며 native 0/4·calls 0 |

15개 보존 묶음에는 실제 실행이라는 옛 파일명이 있어도 업로드 시각을 새 HE29 실행 시각으로 취급하지 않았다. HE18 staged source가 있는 문서는 `a5c958c414dea41216b445c05f58df837f05cacb`를 가리키고 source ODE 호출 0을 기록한다. E13C6 source는 `d06b8066aafab930add24be971b494b591d87257`이고, E13C5의 E13C4 payload manifest는 2026-10-10에 봉인됐다. E13C5 pilot DAG도 native runs·gas advances·old continuous solves가 모두 0이다. physical 보존본은 PR97 integration `7346bea6f6b08165bd64d742ec684bd06caf6318`을 가리킨다.

## 보존 묶음 15개: 실제 관찰한 외부 bytes identity

아래 해시는 이번 전체 GET에서 계산한 archive 자체 SHA256이다. 내부 전체 과학 manifest를 재검증했다는 의미가 아니다. TAR member 목록 및 선택 identity 문서의 byte digest를 보존했고, payload를 추출하거나 내부 코드를 실행하지 않았다.

| Archive | Bytes | 관찰 SHA256 |
|---|---:|---|
| BASS_HE_E13C6_EXECUTION_20261011.wy3yk0s0.tar.zst | 13942364 | `de5297134c40159af84be03807ef08d646159ca8a7e19762c8984cddb74ef6be` |
| E13C5-DyIbg0hn.tar.zst | 10816870 | `8790be524a6b196d733c1408034b89b084525feead7017a0749dc4389fd8ff71` |
| HE-E13C5-first2-branch-cover-20261011.tar.zst | 5501066 | `94b5e15e19413dd3701c1780a636dacf6d77b856a746d647b74be9537d1f363b` |
| HE18_C3_RUN_20261015.tar.zst | 3886026 | `ec4963ba1bd16fca71de7185f34eb3c97280c9a4492a05752991078f26103d70` |
| HE18_C3_STAGE_FIX_CHECK_20261015.tar.zst | 3864463 | `ae44f3f95930435f5a807d678ee17df7829c4dd547ef01fe748665bba554706d` |
| HE18_C5_THIRD_REAL_20261015.tar.zst | 5432513 | `77f1b5650f3dcae61178fa9bd06f6465e619b581a0b078d2da0e02c37170f7e4` |
| HE18_C6_FOURTH_BASELINE_20261015.tar.zst | 5274621 | `90d6e3ea1ca6ba58c26b24dfd85b19c789bd6f9b47d58479d70167dc7e59c5f9` |
| HE18_C6_FOURTH_OPT_20261015.tar.zst | 6905860 | `055d191b33883dc6b7456be8f3e26374e5b15ba53cf09e7f256a6e5a211a7831` |
| HE18_C6_PARALLEL_REAL_20261015.tar.zst | 3431083 | `2104f319432607bf46b7534ce1b7398c33d8beb9f2d5c5c640c58c454f9e9cfc` |
| HE18_C7_FIFTH_BERNSTEIN_20261015.tar.zst | 8443828 | `37afa66019de6342d174228f577ab38d5325647e7fb2eef516229505a0a65042` |
| HE18_C7_FIFTH_REAL_20261015.tar.zst | 6309813 | `bd5425c687d3a234cbc71b0310ec7445805e41b71fdd70837488e5eed7f180e5` |
| HE18_C8_SIXTH_REAL_20261015.tar.zst | 7276543 | `86aafd301e14966c50a5cc2facbfe20defc66ed7b88faa2679f93aadcfcc78d7` |
| HE18_C9_SEVENTH_REAL_20261015.tar.zst | 8457566 | `f21dde1ab65a40188c90ae4cc5996eb368dff60173325a5fcd29bbb135e76c90` |
| physical-input-backup.kQOHTZ.tar.zst | 15759654 | `bbc7d8d778ae85c5058925fa7c4340bf9b45b200f6222038b5065c3ef7ad90b1` |
| physical-v2-backup.TqLNF6.tar.zst | 17445748 | `1c05c74891230eefe6a99091a4c908221cd1e34fac54f50b7a27ed0ad4cbbf10` |

## 재사용 및 보류

완료된 HE28 pilot·6/6 study와 HE29 source-only 과학 suite는 재실행하지 않았다. 새로 읽은 archive는 provenance 확인에만 사용했으며, source·실행 반환·보존 증거를 분리했다. RemoteDesktopCommander의 소진된 경로를 재시도하지 않았고, 이 담당자는 원격 쓰기·archive code 실행·toolchain 설치를 하지 않았다.

finite-donor survival 결과, 연속 스펙트럼, 온도 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB의 승인 범위는 이번 입력 확인으로 확장되지 않는다. 공개용 JSON은 개인 경로·계정 ID·provider 파일 ID·서명 URL·접근 URL을 포함하지 않는다.
