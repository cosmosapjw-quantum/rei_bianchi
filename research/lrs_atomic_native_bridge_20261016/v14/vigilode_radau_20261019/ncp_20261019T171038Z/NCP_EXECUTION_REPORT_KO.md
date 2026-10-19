# LRS V14 VigilODE Radau — NCP 실행 결과 | 2026-10-19 UTC

## 결론

고정 source publication `d87ba9ca25acb8a2a032154fa23057b45acd6207`의 19설정을 NCP에서 실행했다. **19 완료, 실패·중단 0, runner 전체 exit 0.** Endpoint, finite difference, 원시 ledger, 독립 balance가 sandbox 결과와 **모든 비시간 수치에서 bitwise 동일**했다. 이는 다른 compiler(1.99.0 대 1.94.1)와 host에서 같은 discrete-system 결과가 재현됐다는 의미다. 정확도·차수의 새 증거는 아니며 HOLD 항목은 그대로다. **`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`**.

## 실행 identity

- PR198 HEAD `9b55aa2`(이후 commit 없음). 최신 백업은 C10이며 전달 이후 실행 없음.
- NCP `s1a0e5abed09`, Linux 6.8.0-124, 64 CPU, Python 3.12.3, rustc/cargo 1.99.0 (LLVM 23.1.1). Sandbox 1.94.1로 downgrade하지 않았다.
- 기존 LRS checkout `/root/REI_LRS_CASEB_V4_20261016/repo`에서 실행. 새 clone/worktree, reset/clean 없음. 실행 전후 status clean, branch/HEAD 불변.
- Job root `/tmp/rei_lrs_vigilode_20261019T171038Z`.
- 복원: baseline 152 + append 173 bytes + VigilODE 477 files PASS. VigilODE archive SHA `823164c2…` = pin.
- cargo fetch exit0 3.1 s, locked offline release build exit0 335.6 s, focused tests 7 PASS(native 6 + 분류 1).
- Executable `6f0a5382dd10f03850e78e83d91d7930b374c622895f5538316cc21f84e74d12` (sandbox `358d254f…`, toolchain 차이).

## 실패 기록과 최소 수정

1. 지시 명령 그대로 실행 시 exit1: 이 checkout의 fetch refspec이 다른 단일 branch만 추적하므로 `fetch origin BRANCH`가 FETCH_HEAD만 갱신했고 `origin/BRANCH`가 `55d267d`에 머물러 `FINAL_DELIVERY.json`을 찾지 못했다.
2. 같은 실패가 두 번 더 기록됐다. 수정이 실제로 적용되기 전에 실행한 운영 실수이며 과학 실행이 아니다(job root 미생성).
3. 수정: fetch 한 줄을 `+refs/heads/BRANCH:refs/remotes/origin/BRANCH`로 바꿈(`tools/launcher_r1_to_r4.diff`). Source 변경 없음 → 새 source SHA 해당 없음. 회귀: origin = `9b55aa2`, REI_SOURCE_SHA = `d87ba9c` 확인.
4. 수정 후 prepare_and_run exit0. analyze_matrix는 system python에 matplotlib가 없어 그림 단계에서 exit1(CSV/JSON은 이미 기록). job root 안에 분석 전용 venv(matplotlib 3.11.2, NumPy 2.5.4)를 만들어 새 출력 경로로 재실행해 exit0. CSV/JSON은 첫 부분 출력과 동일했다. 실패 출력은 `payload/analysis_attempt1_matplotlib_missing/`에 보존했다.

## sandbox와 비교 (`NCP_VS_SANDBOX.json`)

CSV byte 동일성은 요구하지 않았다. 실제 CSV SHA는 wall 열 때문에 다르다.

| 항목 | 결과 |
|---|---|
| Endpoint 11개 물리 열 × 19 | 모두 bitwise 동일 |
| raw.json 비시간 수치 316,540개 | 불일치 0, 구조 차이 0 (시간 leaf 38개만 다름) |
| Refinement / empirical comparison 수치 435 / 323 | 불일치 0 |
| C9 독립 balance 재적용: 사건 HII/HeII/HeIII·전자, photo binding, binding 변화, 열, escape 분해, CMB input, gas+binding, photon N/U, 전체 photon+gas+binding, source N/U, adiabatic·photon work, layout | 최대값·누적 최대값 모두 sandbox와 동일 |
| macro 198, Radau chemical 198, stage 594, dimension {84:195, 4:3} | 동일 |
| native RHS | 사례별 동일, 합 38,840 |
| native wall / process wall | 15.825 s / 19.06 s (sandbox 9.146 s / 10.91 s) |

비용은 서로 다른 하드웨어에서 각 1회 측정이므로 속도 주장을 하지 않는다. source-disabled 사례의 source N/U는 정확히 0이라 상대 차이가 정의되지 않으며, 성공 지표로 쓰지 않는다. C9 감사는 기존 스크립트를 경로·key 이름만 연결해 그대로 다시 적용했다(`tools/run_c9_audit_on_ncp.py`). 새로운 독립 검토가 아니다.

## 범위

기존 84 이력, 제조 76/Python 57, 이전 SSPRK2/projection, sandbox 19사례를 새 사례로 세지 않는다. General source-on order, uniform stiff, 일반 positivity, Case B, full EoR, signed Bianchi, positive-CMB/비영 boundary는 HOLD다.

## 보존 위치

`payload/`: 사례별 raw·inputs·outcome·stdout·stderr, prepare/build/test receipt, host metadata, 두 분석 출력, launch 4회 기록, SHA256SUMS. 사례별 `sources.tar.gz`(약 44 MB)와 executable은 Git에서 제외하고 백업 archive에 보존한다. SHA는 SHA256SUMS에 있다.
