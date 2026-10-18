# NCP 제한 실행 결과 — 2026-10-18

## 식별자와 판정 범위

- 저장소 / Draft PR: `cosmosapjw-quantum/rei_bianchi` / #199
- 기준 브랜치 HEAD: `604c22823aed09063d27c68de5fe1c3e21b6d076`
- native physics source: `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`
- 판정: `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`
- 작업 디렉터리: `/root/REI_AGE_ENVELOPE_20261018T132700Z`

기존에 같은 frozen task identity의 실행이 진행 중인 것을 확인해 그 scratch와 native binary를 이어 사용했다. 원본 7개 native owner 파일은 원 commit과 일치했고, 수송 파일은 원본 prefix SHA를 확인한 뒤 read-only accessor suffix를 포함한 준비 identity를 기록했다. 빌드는 offline release, `-j 2`로 성공했다. 최초 별도 컴파일 실패나 물리식·tolerance 수정은 없었다. `run_ncp.sh` 자체는 이 controller 세션에서 재호출하지 않았고, 해당 실행기의 빌드 영수증 및 `run_refinement.py` 단계에서 사례를 실행했다.

## 실행 전 확인과 샌드박스 검증

- 호스트 `s1a0e5abed09`; 64 logical CPU, RAM 125 GiB, 루트 디스크 99 GiB 중 21 GiB 여유. Rust/Cargo 1.99.0. 조사 당시 활성 VIGILODE Julia compile은 유지했다.
- donor ZIP SHA-256: `535a4fce4b52660bc3025fdab8e4159cd9a41173f9c1cf1fa0dc524a099de83a`.
- `PATH=<task-venv>/bin:$PATH bash scripts/verify.sh`: **83 passed in 4.94s**. 이는 Python 샌드박스 검증이며 Rust/NCP 수치 성공을 뜻하지 않는다.
- Cargo build exit 0, wall 12.294 s, binary SHA-256 `002d08ac0058864a62e62b8921f52edd065ac34c1d8ef22b0b5c9768f0523778`.

## 다섯 사례

모든 time 사례는 새 common birth levels `[8,16,32,64]`를 사용했다. 기존 `[8,16,32]` mesh와 동일한 mesh로 간주하지 않았다.

| 사례 | 조건 | exit / wall | 관측 결과 |
|---|---|---:|---|
| `age64` | q=0, birth64, angular8, source8, transport16, time factor1 | 1 / 1800.914 s | 14,691 RHS, peak RSS 128,440 KiB. 1800 s 제한 도달, `frozen RHS/time cap`; endpoint 미완성, 60 state/unit-domain errors |
| `time8` | q=0, birth32, angular8, source8, transport16, factor8 | 1 / 11.696 s | `AXBI_COVARIANT_MOMENT_FIT` |
| `time16` | 위와 동일, factor16 | 1 / 12.847 s | `AXBI_COVARIANT_MOMENT_FIT` |
| `time32` | 위와 동일, factor32 | 1 / 17.107 s | `AXBI_COVARIANT_MOMENT_FIT` |
| `spectral128` | q_ref=+0.1, birth8, angular8, source8, transport128 | 0 / 250.119 s | 2,811 RHS, solver wall249.400 s, peak RSS127,840 KiB, solver errors 없음 |

모든 명령과 exit 코드는 각 사례 `RECEIPT.json`에 보존했다. age64는 같은 1800초 cap으로 반복하지 않았다. time 사례는 native covariance moment fit에서 종료됐으므로 reference endpoint와 비교할 자료가 없다.

## 완료된 spectral128 상태와 보존 잔차

- endpoint: N=`1.1236721874729468e-12`, U=`8.800692924010545e-11`, T=`7963.192828679071 K`, proper time=`16840559206146.78 s`.
- signed convention은 `PhysicalDensityFixed`에서 `s=q_ref H_FLRW(a_ref)(a_ref/a)^3`; `a_ref`에서 sigma=`q_ref/sqrt(1+q_ref²)`. 따라서 q_ref=+0.1의 signed shear는 양수이고 sigma≈+0.099503719이다.
- energy residual `4.462874514388204e-12` (normalized `1.7252876758810595e-12`); photon residual `2.6022515034734156e-13` (normalized `1.7923881433942952e-9`); charge residual `2.7438988581263146e-15`; species residual `[2.7393587615290316e-15, 4.48503945571152e-18, 9.739555404444369e-20]`.
- 순간 Gamma와 heat, species별 순간 photo/RR/CI, thermal 및 누적 ledger 원값은 `spectral128/.../endpoint.json` 및 `ledgers.json`에 보존했다. native DR은 scalar 0으로만 기록되며 세 종별 DR vector가 아니다.

## transport64와 비교

같은 q_ref=+0.1, birth8/angular8/source8 및 proper-time 구간의 기존 transport64 reference와 비교했다. 18/18 관측이 pre/post side를 분리해 일치했고 누락/모호 관측은 없었다. endpoint 상대차는 N `6.3940e-5`, U `6.9558e-5`, T `1.3893e-7`; 순간 Gamma 상대차 `[4.9875e-5,5.2223e-5,7.6481e-5]`, heat 상대차 `[5.4874e-5,5.8701e-5,6.6557e-5]`였다. 누적 photo 상대차는 HI `2.1194e-4`, HeI `2.6608e-3`, HeII `1.3032e-4`; HeI 누적 event의 0.5% 기준은 이 유한 neighbor 쌍에서 충족한다. 누적 RR 상대차 `[5.9858e-7,7.9848e-6,4.6901e-8]`, CI `[1.1434e-6,7.9363e-8,7.9405e-6]`. gas fraction 절대차 `[1.4249e-8,1.7526e-7,4.0762e-13]`, thermal 절대차 `1.5621e-7 eV/H`, birth-age W1 `127924.08 s`.

DR 비교기의 기존 0/0 표기는 분모가 0이며 양쪽 자료도 species aggregate scalar이므로 성공으로 인정하지 않는다. 따라서 관측 endpoint target 충족은 **finite neighbor 결과만** 뜻한다. native nonlinear opacity certificate나 continuum 오차 경계가 아니다. transport64 자체 normalized residual은 energy `1.2446724364539223e-12`, photon `1.2957764786823694e-9`, species `[1.83433455e-15,2.63427247e-18,2.53845186e-20]`이며, 여기서는 reference residual floor의 운영적 기록으로 표시한다. 독립 continuum floor는 측정하지 않았다.

q=0의 신규 age/time endpoint가 완성되지 않아 기존 age32 결과와 새 실행을 비교할 수 없다. 기존 age32는 q=0, birth32, transport16이며 과거 `[8,16,32]` mesh이고 event 10,11,12,32에서 state/unit-domain errors가 기록된 reference다.

## 게시 및 백업 상태

코드, donor/source identity, 빌드 receipt, 원시 성공/실패 사례, 기준 입력, 비교 JSON, 실행 요약과 DAG를 이 PR 경로에 게시한다. Dropbox와 Google Drive의 새 archive 업로드 및 원격 재읽기 SHA/CRC/payload 검증은 미완료다. 현재 host에는 승인된 rclone binary/config가 없고, Dropbox connector는 대화 첨부 파일만 받고 생성된 local 파일 경로를 직접 허용하지 않는다. Google Drive도 이 런타임에서 local artifact file reference를 제공하지 않았다. 따라서 클라우드 SHA를 생성하거나 확인한 것으로 보고하지 않는다.

### 다음 READY

실행 결과 기준으로 다음 READY는 `age64`의 원인 진단 및 시간/상태 event 경계의 최소 재현이며, 검증된 source와 기존 tolerance를 유지해야 한다. `AXBI_COVARIANT_MOMENT_FIT` 실패는 physics/closure/tolerance 변경 없이 source owner 진단이 선행되어야 한다. DR 종별 누적/순간량 기록이 가능한 경우 species-resolved comparator를 추가로 실행한다. production admission, full nonlinear opacity certificate 및 continuum claim은 계속 HOLD다.
