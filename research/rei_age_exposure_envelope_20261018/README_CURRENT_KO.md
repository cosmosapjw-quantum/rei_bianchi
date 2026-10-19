# REI age-exposure/source-age 현재 상태 | 2026-10-19

진입 문서는 이 파일, `RESEARCH_UPDATE_20261019_KO.md`, `contracts/NEXT_DAG_CURRENT.json`이다. 이전 49/74/83-test 복원과 NCP NOT_RUN 표시는 완료된 과거 단계다. 이번 실제 intake는 PR199 HEAD `0c6b0466b10a47788f6415a8538e9d3e7a268163`에서 시작했다. PR199는 draft이며 original physics SHA는 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`다.

## 완료된 실제 결과

- **spectral128 실행 완료, 재사용:** q+0.1/age8의 transport64→128 He I 누적 photoevent 차이 0.2660778682%. 해당 유한 인접 비교는 0.5% 목표 안이다. 18/18 common pre/post 관측이 일치했다. binary64와 text48의 parity 기록도 이미 있다. 재실행하지 않는다.
- **age64 기존 실행은 gate 실패:** binary64/48, 15007 RHS, 592.331 s, endpoint 도달, exit1. 원래 photon ratio `1.0081783527976493e-8 > 1e-8`를 보존한다. 이번 raw70 파일 정확 재합산도 `1.008178364096903740e-8`로 실패하므로 마지막 합산만의 문제가 아니다.
- **native time8/16/32의 기존 실패 보존:** NCP의 `AXBI_COVARIANT_MOMENT_FIT` 이후 같은 캠페인은 반복하지 않았다. 새 failure-only 진단을 넣은 로컬 time8 1회에서 평균 적합 후의 subnormal 저장 양자화를 포착했다. count defect5η가 기존 tolerance3η를 넘었고, energy89η는 tolerance116η 안이었다. 독립 원본 Rust 셀 재생으로 확인했다.
- **reference 오차검사 구현 완료:** `--error-norm block-max`를 명시적으로 선택할 수 있다. 기본 RMS, 원래 rtol/atol와 photon `1e-8` gate는 유지한다. 동일 RK stage에서 새 성분군 최대 검사 ≥ 기존 검사를 증명했고, 해석해가 있는 8개 실험과 독립 검토를 완료했다. 실제 age64 새 모드는 아직 NOT_RUN이다.
- **새 가벼운 검증:** photon 진단11 + block control9 + moment 진단3 + subnormal count 교정3 = 고유26개 targeted unittest PASS. 기존85 PASS/1 optional skip은 원격 이력이며 이번 전체 재실행 결과로 더하지 않는다. Rust1.94.1로 두 task copy 컴파일과 로컬 time8 두 진단 실행을 실제 완료했다. 후기 환경 초기화 후에는 compiler가 없어 추가 재실행하지 않았다.

- **제한적 count 교정도 검증:** 기존 노드 하나의5η 교정으로 첫 셀의 두 gate가 통과했지만 새 time8은 뒤의 energy-only2η>η에서 다시 실패했다. 기본 none, 기존 gate를 유지한다. native time16/32는 HOLD다.
- **증거 복구 범위:** 후기 환경 초기화 후 native153과 age64raw70은 exact hash로 복구했다. D의 두 번째 셀 전체로그는 미복구이며 관측기록 기반 compact 복원임을 명시했다. 상세는 SCRATCH_RESET_RECOVERY_20261019.json.

## 재현과 다음 실행

`HANDOFF_CODEX_CURRENT_KO.md`와 최신 DAG를 먼저 읽는다. 기존 `run_ncp.sh`의 전체 사례 기본값을 그대로 재개 명령으로 사용하지 않는다. 새 실행은 변경된 수치 가설을 검사하는 명시적 단일 사례만 허용한다.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_photon_ledger_diagnosis.py' -v
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_error_control.py' -v
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_moment_fit_diagnostic.py' -v
PYTHONPATH=src python3 src/run_error_control_study.py --out results/ERROR_CONTROL_STUDY.json
```

기존 조건부 paired response bound, 24 prescribed-opacity cases, PR171 양성 source-matched reference 구현은 재사용한다. native nonlinear Grackle response bound, age/source 연속극한 정확도, native time 수렴성은 미확정이다.

게시·백업은 `DELIVERY_RECEIPT_CURRENT.json`에서 실제 성공 응답 범위로 확인한다. owner checkout, PR150/R9, 별도 BASS HHeD lane은 이 연구의 변경 범위가 아니다.

**`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`**.

현재 단일 READY: `bash scripts/run_accuracy_followup.sh "$REI_REPO" "$NEW_SCRATCH" age64-block-max`. 변수와 연결·파일 준비는 Codex가 처리한다. `time8-subnormal-count` mode는 진단 재현용이며 현재 반복 실행 READY가 아니다.
