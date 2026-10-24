# 새 스레드 실행 인계: sandbox physics orchestration 2026-10-22

이 문서는 현재 사용자가 승인한 연구를 새 스레드에서 이어가기 위한 작업 계약입니다. 필요한 자료를 연결 도구로 직접 읽고 복구하세요. 사용자가 별도 파일을 내려받거나 업로드할 필요가 없습니다.

## 먼저 읽을 파일

같은 commit의 REPORT_KO.md, DAG.json, PUBLICATIONS.json, FINAL_DELIVERY.json, CLOSEOUT_DELTAS.md, theory/SHARED_PHYSICS.md, review/를 읽습니다. FINAL_DELIVERY.json은 최종 전달 commit에 추가되므로 고정 source commit에 없으면 이 문서의 branch 최신 전달 commit에서 찾습니다. 과학 source pin은 PUBLICATIONS.json 그대로입니다.

현재 tagged physmath-research-loop1.3.0을 적용합니다. 최신 버전이면 변경된 단계 선택·보존 규칙만 읽고 실제 요청 범위에 적용합니다. 이 요청은 작은 이론 유도→구현→판별 검증→게시/백업 단위입니다. 큰 전체프로젝트를 완료로 선언하거나 자동으로 다음10단계 루프를 무한 시작하지 않습니다.

## 시작 순서

1. 실행 환경의 실제 Python/NumPy/SciPy/C/Node/Rust 가용성을 확인합니다. 현재 스레드는 Python3.12.14/NumPy/SciPy/GCC/Node를 사용했고 rustc/cargo/gfortran은 PATH에 없었습니다. 새로운 환경은 다시 관측합니다.
2. 연구 전에 최근48시간 및 이 체크포인트 이후의 Git refs/PR 실제 파일, backup receipts, 접근 가능한 대화를 먼저 확인합니다. 각 DAG 노드 실행 직전 해당 의존성의 delta를 다시 확인합니다. 전체 대화 전수열람이나 미게시 NCP 프로세스 관측을 할 수 없으면 그 범위를 정확히 기록합니다.
3. 원본 branch의 AGENTS.md와 선택한 owner 계약을 읽습니다. rei_bianchi는 Astra 계약→하위 모델 구현→fresh Astra 판정을 요구합니다. 현재 C3 probe는 이미 이 경로로 완료됐으므로 재실행하지 않습니다.
4. 아래 source pin의 파일을 GitHub 연결 도구로 가져옵니다. 기존 checkout이 있으면 그곳의 branch/HEAD/status를 확인해 작업합니다. 이미 완료된 계산을 복구 목적으로 다시 돌리지 않습니다.
5. DAG의 N1–N7에서 입력이 실제 확보된 작은 단위를 병렬/순차로 실행합니다. N8은 물리 입력의 의존성을 기다립니다. 각 단위 완료 후 코드·실제 raw·검증·scope·다음 행동을 남겨 additive branch에 push하고 기존 백업 폴더에 저장합니다. 강제 push나 merge는 하지 않습니다.

## 저장소별 exact anchor

| 저장소 | 과학/구현 pin | 단위 | 게시 |
|---|---|---|---|
| cosmosapjw-quantum/BASS_HE | `0868889acebeb4d9b70d38313a9a694d12bf8766` | `research/he34_lorentz_transport_20261022` | https://github.com/cosmosapjw-quantum/BASS_HE/pull/87 |
| cosmosapjw-quantum/WU088_HH | `6c3b12554288893d5d7e221d77be943324285ceb` | `research/hh1_d_energy_adapter_20261022` | https://github.com/cosmosapjw-quantum/WU088_HH/pull/135 |
| cosmosapjw-quantum/bass_cr | `15fd250ab91574bd4f3348e91d739a15a6ed6005` | `research/cr_c22c_excitation_diagnostic_20261022` | https://github.com/cosmosapjw-quantum/bass_cr/pull/97 |
| cosmosapjw-quantum/rec_bianchi | `02f3286ee39d99444777ed029844b74bc00cb053` | `research/orchestration_sandbox_20261022/rec_bianchi` | https://github.com/cosmosapjw-quantum/rec_bianchi/pull/123 |
| cosmosapjw-quantum/bass | `797d66580448dad7fc41f2c2db31fe0eb37908bf` | `research/sandbox_affine_chemistry_20261022` | https://github.com/cosmosapjw-quantum/bass/pull/181 |
| cosmosapjw-quantum/vigilode | `f9da4aae865623d71bff20c6157318cbaf19ba6c` | `research/lifted_error_norm_20261022` | https://github.com/cosmosapjw-quantum/vigilode/pull/79 |
| cosmosapjw-quantum/rei_bianchi | `20539a00d3fb5dcdb4165b1c90b4d5d5d1f8ebb3` | `research/rei_c3_zero_tiny_source_20261022` | https://github.com/cosmosapjw-quantum/rei_bianchi/pull/222 |

원본 owner와 같은 물리조건인지를 확인한 뒤에만 코드를 결합합니다. HE의 stationary-heavy-target 순간 Grad functional, HH의 per-Href eV ledger, REC의 per-baryon SI Compton 예산, REI의 absolute per-baryon isotope source를 단위 변환 없이 혼합하지 않습니다.

## 즉시 사용할 후속 작업 패킷

- BASS+VigilODE / N1: affine30 RHS/Jacobian과 full33 WRMS를 opt-in adaptive client에 연결합니다. 미완료 지점은 driver hook과 작은30/33 paired trajectory입니다. norm32ulp 검증을 반복하는 것만으로 새 성과로 삼지 않습니다. 재래 norm을 그대로 적용하면 물리 오차예산이 달라집니다.
- REC / N2: PR12211897e09의 NEXT_UNIT_CONTRACT를 먼저 읽고 actual-hot/Planck reference field를 분리한8개 full63 Compton 실행 준비를 이어갑니다. 기존 상한240s/case·1200s serial aggregate를 재설정하지 않습니다. 우선 작은 대표 케이스로 구현/회귀를 판별하고 누적예산을 유지합니다. 이미 있는8개 thermal-moments와 THERM01의별도8개는 재실행하지 않습니다.
- bass_cr / N3: 새 C22C의2000K 이상 진단을 재사용하고 실제 저온 source/단면적/정규화로 공백을 메웁니다. SW91 fit을2000K 아래로 연장해 통과값을 만들지 않습니다. 새 source가 확보되면 rate/energy/derivative를 경량 적분으로 검증합니다.
- WU088_HH / N4: D energy ledger를 source-qualified isotope PI/RR 수·열 모멘트와 연결합니다. CX defect와 threshold convention을 일치시킵니다. 에너지 보존만으로 미확보 rate를 승인하지 않습니다.
- BASS_HE / N5: 실제 l=2 수송자료와 유한질량 pair exchange를 도입합니다. 총 event rate를 압력 relaxation rate로 대체하지 않습니다. B2 reactive moments→B3 closure→saved-HE32 control→feedback 순서가 뒤따릅니다.
- REI / N6: 이미 완료된 C3 exact-zero/tiny-stock kernel을 재사용하고 off-grid coefficient policy와 rank-one electron-density Jacobian, 실제 event assembly를 채웁니다. 다른 스레드가 C3에 착수했다는 신호가 있으므로 새 commit/results를 먼저 통합해 중복 구현을 피합니다. 원전 없는 daughter branching은 제조하지 않습니다.
- REI / N7: PR199의 D10 zero-initial matter-stress35 saved histories를 현재 owner 계약에 맞춰 분석합니다. 별도 source가 없는 새IVP를 시작하지 않습니다.

## 이미 완료되어 재실행할 필요 없는 결과

HE29reference4/4+packedcanary, HE32 394history, HH PHYS79, CR C22A/B, REC R3S NCP5jobs/REC126/THERM01eight/thermal-momentseight, REI D9/C1/C2/finiteC3, BASS compact127, VigilODE saved heat1046은 해당 exact evidence를 재사용합니다. 이번 seven-kernel 작업의 새 cosmological IVP와 NCP 제출은0회입니다. 서로 다른 모델/cohort 수를 합치지 않습니다.

VigilODE port의 마지막 확인7647d545d79ed8723331194a36c68e6adf4d80f7: NCP C1attempt2 완료1034s,1212typedrows, G1–G7PASS; JuliaHOLD 당시기록 보존. Julia1.12.7 설치 후 attempt3가07:00:04UTC 시작된 상태였습니다. 최신 완료 반환을 먼저 확인하고 중복 제출하지 않습니다.

REC PR122 Planck저장경로 예산과 우리 REC1은 같은8이력을 사용하며 최대1.78e−15eV/baryon 차이로 일치합니다. 독립 C구현은 새 성과지만 새8개 우주론해로 세지 않습니다.

## 자동 복구할 백업

- 새 모든 kernel/입력/근거: Drive1Uqx2do4-trSzEpI4U8SkBQaFLHQA_TRe 또는 Dropboxid:BSpOijBcT10AAAAAAD_h5g, ORCHESTRATION22_S1_REVIEWED_KERNELS.zip,2311953B,SHA256e400dee883c0cce8f30c1504e5428c2beb1922f8b8ee349be33371bcf1090f19.204payload,localCRC PASS; remoteACK+size.
- 초기 조사: Drive15U4wmh0XGula9rzv1yPI_R-M4XsW_ZTm 또는 Dropboxid:BSpOijBcT10AAAAAAD_h4g, ORCHESTRATION22_S0_INTAKE.zip,43462B,SHA256834a65a3db3991decd2b7eae485cb6ea18b48a8f56326758c4c4c0bfb418f59a.
- CR 원 full raw+source+gitbundle: Dropboxid:BSpOijBcT10AAAAAAD_h3g 또는 Librarylibfile_cb882db86828819185c4385ab1681af3, BASS_CR_C22B_COMPTON_20261022T124113KST.zip,69915429B,SHA256e35325402897a8f993120f7f5c37738170eb7ea343115dab4f0669e3045ce6f9.411payload를 이번에 실제 복구했습니다. 원bundle prerequisite는a5e12c5f3e6d323e211d65fefad34060ec07eff0, tipf03fdf71fb2ea995ce16b68d81ef4f47ecb00685. 새 PR97은 source content를 보존한 부분 게시이며 원commit identity가 아닙니다.
- C3 full RESULT.json은 repo의 RESULT.json.gz에 losslessly 보관됩니다. Python표준 gzip으로 풀면978354B/SHA2569e95da5c376061da78cb58060763d7bfed1e0fd81e934cb4d63f4898ff70f957. 검증을 다시 실행할 필요가 없습니다.
- 최종 S2 전달문서 백업 ID는 FINAL_DELIVERY.json을 읽습니다.

백업 대상은 사용자가 이미 승인한 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/ 와 Drive folder1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI입니다. 자료를 연결 도구로 직접 복구하고 사용자에게 수동 다운로드를 요청하지 않습니다. 접근이 실제 차단되면 정확한 작업·오류·남은 입력만 기록하고 가능한 독립 노드를 이어갑니다.

## 종료 기준

선택한 작은 단위에서 실제 유도/코드/판별 결과, 과학적 적용 범위, 필요한 남은 source/closure를 남깁니다. 한 verification pass와 필요한 한 fresh review로 충분하면 게시로 전환합니다. 실패는 원본을 보존하고 구체적 원인이 있는 작은 수정을 합니다. source불명·원전미확보·CI실패를 서로 구별합니다. 기존REI cargo fmtFAIL/testsSKIP를 CI통과로 보고하지 않습니다.
