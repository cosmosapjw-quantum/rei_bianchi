# HE29 추가 진행: VigilODE Rust 연결까지 완료

새 구현 publication은 `57642252991b5c453db66eb5a078e6a62cc6f4ea`이며 54/54 GitHub readback과 완전 archive의 Drive·Dropbox raw bytes/229개 payload 해시 일치를 확인했다. 고정 실행 코드와 후속 문서 commit을 구별한다.

2026-10-19 추가 연구에서 VigilODE a21d의 실제 RODAS5P/GMRES와 faer 의존성을 연결했다. 새 Rust bridge 실제 빌드 및 작은 FFI 3개, 새 Python 연결 96개 검증이 통과했다. 큰 source suite는 반복하지 않았다. HE29 물리 기준해는 여전히 관측된 새 반환 0/4이며, 이를 먼저 끝낸 뒤에만 단일 r4/table512 VigilODE canary를 허용한다. 원래 과학·테스트 revision1569와 native owner f7830e2, 물리·반응률·허용치는 그대로다.

현재 새 코드·이론·실행 지침은 [vigilode_20261019/README_KO.md](vigilode_20261019/README_KO.md), [NCP_HANDOFF_KO.md](vigilode_20261019/NCP_HANDOFF_KO.md)에 있다. 실제 게시·백업 정체성은 해당 [DELIVERY.json](vigilode_20261019/DELIVERY.json)과 두 DAG를 따른다. R2 체크포인트 c0dc267은 GitHub readback7/7 및 Drive/Dropbox raw-byte SHA256 일치까지 확인했다. 새 구현은 별도 commit/백업으로 구별한다.

NCP 제출은 현재 도구의 월간 quota로 BLOCKED다. 접근 가능한 실행자는 최신 반환과 프로세스를 확인한 뒤 기존 네 기준해만 이어간다. 기존 transport6개, source-only50개 검증 및 과거 PUBLISH.sh를 재실행하지 않는다. 아래 기록은 이전 시점의 재사용 근거다.

---

# 2026-10-19 HE29 재개 상태

GitHub PR78/83개 branch 목록/최신20개 PR 및 백업 폴더를 실제로 읽었다. 새 HE29 native 반환은 관측되지 않았으며 마지막 알려진 기준해 상태0/4 NOT_RUN을 유지한다. NCP의 미게시 실행 여부는 원격 접근 한도로 관측하지 못했다.

완료된 HE28 연구와 HE29 source-only 검증은 재실행하지 않았다. 원본 bootstrap의 일괄 pytest 재실행을 현재 사용자 지시에 맞춰 생략하는 작은 `ncp/REUSE_SOURCE_VALIDATION_20261019.patch`를 별도 identity로 준비했다. 1569 과학·테스트 소스와 원본 bootstrap은 Git에서 그대로 유지한다. 패치의 신규 적용/중복·변경 거절/Bash 구문만 확인했다. native 호출은0이다.

**실행자는 갱신한 CODEX_HANDOFF_PROMPT_KO.md의 fresh Git checkout → 1569 고정 → pinned patch 적용 → START_REFERENCES.sh 절차를 따른다.** 네 case (r2,512),(r4,512),(r8,512),(r4,1024), 각각 Radau+DOP853을 유지한다. source-only50개 tests와 기존 transport6개를 반복하지 않는다. 실제 NCP 제출은 Remote Desktop Commander 월간 사용량 한도로 BLOCKED이며 제출·접수·실행을 주장하지 않는다.

현재 DAG와 조회·실행 경계 근거는 DAG_STATUS.json 및 results/continuation_20261019/에 있다. 과거 패키지와 receipt는 아래 날짜의 보존 근거로 재사용한다.

---

## 2026-10-18 보존 기록

# HE29 게시 복구 완료 및 실행 진입점

2026-10-18. Draft PR78에 미게시였던 S2를 반영했다. 실행 source/test revision은 `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`다. 이후 문서·백업 receipt 커밋과 실행 identity를 구별한다. 원본 microphysics·물리 상수·tolerance·HE28 결과는 변경하지 않았다. 이번 작업의 native 호출0.

## 바로 시작

Git checkout에서 `bash research/he29_survival_budget_20261018/ncp/START_REFERENCES.sh`를 사용한다. 기존 archive를 사용자가 내려받을 필요가 없다. 인증된 rclone dbx:/gdrv:에서 원본 입력 archive를 자동 확보하거나 Codex가 직접 받은 경로를 HE29_INPUT_ARCHIVE로 준다. 과거 PUBLISH.sh는 최초 미게시 복구 도구이므로 현재 branch에는 재실행하지 않는다.

전체 코드와 테스트는 Git에 있으며 exact native DATA22개는 별도 cloud archive에서 복원한다. 원본 archive는129635bytes, SHA256 `a70d320c7ead5f1fd93170c18f1f80ae5eb58a293a6045a0f728bb7ae2743205`. 각 입력의 개별SHA는 provenance/INPUT_SHA256.json에 고정했다. 선택필드 PARENT_SCIENCE.json과 실제 원본 바이트를 혼동하지 않는다. RESTORE_VERIFIED_INPUTS.py는 data만 추출하고 충돌 시 overwrite하지 않는다.

Drive original id `1I31wE6A3laYE6nxMcKNmm5rNMeESIsXi`, Dropbox original id `id:BSpOijBcT10AAAAAAD_Ncg`. 원본 Drive 전체 readback 일치. Dropbox 업로드 및 provider content_hash 일치, raw readback은 URL 경계로 미검증. 최신 code/prompt 완전 패키지의 보존은 results/publication_retry/DELIVERY.json을 기준으로 확인한다.

## 검증 및 과학 범위

원본47개+신규 포장3개, 총50/50 tests PASS. 포장 테스트의 실제 failing behavior3개를 확인 후 구현했다. native fake를 과학 증거로 사용하지 않는다. 신규 네 기준해는0/4 NOT_RUN이다. 6개 src 및3개 실행보조 파일의 Git blob SHA가 로컬 실제 파일과 일치했다.

유한 positive donor의 Jensen/chord survival bound는90사례/720nested 구간을 포함하며 최종 최대폭2.2487671447191104e-12다. 이는 엄밀한 continuum quadrature나 nonlinear gas-temperature bound가 아니다. 시간/strip 효과가 섞이는 저장 HE28 결과를 추가 적분 없이 분석했고, 같은-r/table의 새 Radau+DOP853만 준비했다. m8/GL4/q0의 (r2,512),(r4,512),(r8,512),(r4,1024). 기존 transport6개는 반복하지 않는다.

조건부 Jensen 하한 M exp(-t mean), endpoint chord 상한 M[(b-mean)exp(-ta)+(mean-a)exp(-tb)]/(b-a)는 동결 흡수율의 mass/mean/support에 관한 정리다. 참조 격자 정제는 안정성이지 연속 오차 증명이 아니다. 상세 수식과 이전 원시 기록은 stages/S1_THEORY.md와 원본 완전 백업에 보존되어 있다.

실제 실행 범위와 제약은 CODEX_HANDOFF_PROMPT_KO.md, 새 ChatGPT 재개는 NEW_CHAT_HANDOFF_KO.md를 따른다. full EoR·continuous spectrum·upstream Grackle runtime parity·관측 Bianchi/CMB는 독립 검증 전 HOLD다.

