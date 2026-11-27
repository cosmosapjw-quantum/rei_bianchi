# HE29 최적화 루프 — 2026-10-20

**구현·경량 검증·합성 성능 측정을 완료했다. 기본값은 순차 packed Rust JVP다.**
새 HE29 native 기준해는 관측상0/4이며 NCP 제출/시작은0이다. 네 원래 기준해 쌍을 먼저 확보한 뒤 optional r4/table512 한 건에서만 새 경로를 비교한다.

## 결과와 실행 가능한 코드

| 변경 | 근거 | 상태 |
|---|---|---|
| 입력 manifest의62자리 SHA 한 항목 보정 | 원본 a70 archive 전체/내부 SHA, 실제22 DATA 복원/preflight, 독립 검토 | 완료; baseline1569에는 별도 patch 적용 |
| 원래 LIL Jacobian 대입 → canonical CSR 배열 조립 | 세 실제 photon geometry의 data/indices/indptr 동일, 제조 RHS로 조립 시간 분리 | 최초 paired8.35–8.78배; 전체 native 속도는 미측정 |
| exact time/interval geometry·sigma 캐시 | 부모 생성 경로와 원래 RHS 일치, endpoint mask 무효화 검증 | opt-in 모델에 구현 |
| 정확한 state/time의 physical Jacobian 저장 및 Rust JVP | 원래 행 누산 순서, 전체4+K+19 state/error norm | ABI2 실제 compile·새 검사 PASS |
| Rayon1.12.0 독립 photon 출력 행1/2/4 workers | 같은 solver/입력/허용치의 합성 IVP, endpoint 비트·attempt 동일 | packed1이1.38–1.53배 빠름;2/4는느려 기본값1 |
| NCP build/canary controller | Git/source/binary/table/4개 baseline admission, bounded process와 실패 기록 | 준비된 코드; native 실행은 별도 |

[연구 유도·외부 재사용](RESEARCH_KO.md), [실제 성능과 한계](PERFORMANCE_KO.md), [NCP 실행 지침](NCP_HANDOFF_KO.md), [DAG](DAG_STATUS.json), [게시·백업 영수증](DELIVERY.json)을 읽는다.

`src/optimized_model.py`는 원래 gas 유한차분 RHS5회와 photon 계수를 보존한다. `rust_bridge/src/packed.rs`는 계수16K+92개와 재사용 workspace를 보관한다. `src/packed_reference.py`는 원래 RHS/partial-time callback을 재사용하며 준비 계수만 전송한다. `ncp/build_bridge.py`는 clean publication Git과 고정 VigilODE a21을 사용하고, `src/run_packed.py`는 네 원래 기준해 admission 뒤 단일 canary만 허용한다. Archive의 source나 binary는 실행 시작점이 아니다.

## 과학적 우선순위

m8/GL4/q0에서 `(r2,512),(r4,512),(r8,512),(r4,1024)` 각각 Radau+DOP853. 원래 여섯 transport와 HE28 pilot/study, HE29 90-case/720-bound/50-test와 기존 VigilODE96/3/Schur23 근거는 재사용하고 반복하지 않았다. 절대 fraction1e-11과 gas-temperature1e-9 K 비교 gate를 포함한 모든 기존 물리·보존 gate를 유지한다.

첫 intake는329f, 첫 checkpoint publication은8cb0ebb91a78d2f1b751caa1c3ffc5d170ddfe41(19파일 actual readback MATCH)다. 현재 코드 publication과 백업은 DELIVERY의 정확한 SHA/provider receipt를 따른다. 과거7bf7398b/88285fa4와 c47/798 묶음은 불변이다.

연속 spectrum·전역 gas-temperature 오차상한·전체 EoR·whole upstream Grackle·관측 Bianchi/CMB는 HOLD다. 합성 Rust JVP 실행 수를 원본 native chemistry 실행 수로 세지 않는다. `physmath-research-loop` standalone1.0.0의 이번 연구 단위와 과거1.3.0 근거 재사용을 구분한다.
