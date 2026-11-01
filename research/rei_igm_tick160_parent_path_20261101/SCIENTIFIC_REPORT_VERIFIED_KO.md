# REI IGM | 실제 26-event, tick160→161 부모 온도 경로 결과 (2026-11-01)

**원본 소스 보존**: first canonical interval parent accepted `160/131072`; immutable archive `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; state arrays `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`; kernel `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`.

## 신규 source-authentic 계산

- 46,080 unique 원본 노드에 대해 고정된 원본 nuclei-conserving population과 세 log-temperature 경로 α=0.05,0.50,0.95에서 **실제 원본 26-event full, half1, half2 map** 계산.
- 세 source lane 모두 성공: 3×3×46,080 = **414,720 lane-labelled records**, 공유 초기 node×α 조합 138,240; 원본 세 lane은 독립 observational datasets가 아님.
- 최댓값: point-parent independent-output interval gap = `5.949110768455057e-7`; |center ΔlogT| = `2.8423485787243408e-11`. 이전 원본 전체 부모 실패값은 `2.1245050576368385e-4 > 2e-4`이며 여전히 BLOCKED.
- 단일점 선택 원본의 조건부 한 tick 과학: ΔT 약 −4.853K부터 +0.02903K; 중앙값 약 −0.002315 K, ΔUthermal/H midpoint 계열은 모두 음수. **이는 전체 불확실성에서 엄격한 에너지 감소 정리가 아님.**
- 본 실험은 finite path diagnostic으로서 원본 공동 초기조건/광자-원자 source correlation의 rigorous all-X map J/remainder와 동등하지 않음.

## 검증, 실패의 성격

- `GitHub Actions 41274311481`: 3/3 science lane jobs SUCCESS, 각 CSV.gz 46,080행 및 저장된 SHA256 검사 통과. native `verify`도 SUCCESS. 원본 H/He nuclear inclusion PASS. 현재 PR #336 세 번째 HEAD `158317d0c321c1bc9081d2607c3fc079e6fd5be2`에서 수행.
- 실제 앞선 두 GH Actions 실패 `41273886764` 및 `41274114476` 보존: 각각 잘못 전사한 63자리 source hash, 물리 단위 부적합한 1e-12 절대 핵수 비교. 둘 다 source physics map 실행 이전의 provenance/preflight 구현 오류이며 과학적 실패가 아님. 원본 map, 고정 2e-4/2e-3 gate 수정 없이 15/15 일반/15/15 -O 회귀 테스트.
- 한 원래 부모 `run_step`가 source enclosures를 사용한 조건부 점 path를 통과한다는 사실은, 전체 원래 interval을 닫는 증거가 아님. 독립 작성자 R06/C09 NOT_RUN, native subagent NOT_RUN.

## 보존

- 원본 20개 R/C 단계별 checkpoint JSON + 실행코드 + 실패기록은 Draft [PR #336](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/336) 및 Google Drive [corrected source/checkpoint ZIP](https://drive.google.com/file/d/1fOvfCDJFOZ_YZILnBcpMEMMTcwGjPVYx/view)에 저장, 해당 ZIP raw restore SHA256 exact; 단계별 remote *실시간* 게시 20개가 아니라 단계 기록 한 commit 게시였음.
- 상세 9개 실행의 완전한 46k CSV.gz는 GitHub Actions artifact 13071120807,13071000428,13070571986로 보존, 만료 2027-01-30. **아직 Drive/Library 독립 영속 물리 데이터 복원 완료가 아님**. 이 보고서와 compact 9-row summary는 Git에 영속 게시.

## 자기 적대적 감사 판정

(1) 세 α를 전체 parent box의 rigorous sup으로 쓰면 과대 claim. (2) 세 lane의 동일 원본 node를 3개 독립 시료로 세면 중복. (3) thermal-energy midpoint negative를 interval-supported universal sign으로 승격하면 부정확. (4) 인증된 original full-step/half-step local boxes를 원본 canonical acceptance로 승격하면 false PASS. (5) 성공한 GitHub Actions는 수학적 remainder나 독립 저자 심사를 대체하지 않음. 모두 **HOLD**.

**다음 최소 과학 작업**: 원본 26-event 복사 없이 source+parent shared dependence를 보존한 `D_h(X,Θ)=F_h(X,Θ)-F_{h/2}(F_{h/2}(X,Θ),Θ)`의 four-site Jacobian·잔차 및 Hummer-Seaton fixed topology에서 validated all-X enclosure. 먼저 original tick160→161 하나만, 동결 `2e-4` 및 source identity 유지. 증명 전에는 전체 131072 tick 재시작 금지.

**DAG CENTRAL 28/88, WORKING 33/88, FAST 4/7, DELTA=0; FIRST_INTERVAL=BLOCKED_MINIMUM_STEP. NO_MERGE, NO_FORCE_PUSH, NO_PRODUCTION, NO_AUTO_NEXT.**
