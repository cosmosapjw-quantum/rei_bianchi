# q0 age64 block-max 단일 실행 결과 | 2026-10-19

## 결론

기존 RMS age64가 실패했던 고정 photon gate를 **동일 rtol/atol·RK 계수·source schedule·물리식·gate**에서 opt-in `--error-norm block-max`가 통과했다. 이것은 단일 사례의 gate 통과이며 age 수렴성이나 연속극한 정확도의 증명이 아니다. **`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`**.

| 항목 | 기존 RMS age64 (0c6b046 기록) | 새 block-max age64 |
|---|---:|---:|
| photon `abs(r)/gross` (gate ≤1e-8) | 1.0081783527976493e-8 **FAIL** | 2.002711130429069e-10 **PASS** |
| energy normalized (gate ≤1e-8) | 8.61600304298541e-12 PASS | 1.929660553608937e-13 PASS |
| RHS calls | 15007 | 19756 |
| case wall | 592.331 s | 782.731 s |
| 후반 구간(event61–63) solver steps | 11 | 16 |
| 마지막 세 구간 signed residual 증가 | 6.67e-14, 5.54e-14, 5.39e-14 (event64,63,62) | 8.34e-16, 8.29e-16, 8.22e-16 (event63,64,62) |

새/기존 photon 비율은 0.01986이다. 정확한 유리수 재합산(`PHOTON_LEDGER_DIAGNOSIS.json`)도 gate PASS이며, 저장값과 재합산 차이는 마지막 합산 경계 1.10e-18 안이다.

## 해석의 범위 (독립 검토 반영)

- **가설 판별 불가.** 정확한 산술에서 같은 stage의 `E_block ≥ E_rms`이므로 block-max는 항상 더 엄격한 제어다. 따라서 이 실행은 RMS 희석 가설을 반박할 수 없었다. 후반 step 수 약 1.45배는 DOP853에서 1.45^8≈20 정도의 국소 오차 감소를 주며 관측된 약 80배 감소와 같은 차수다. energy와 charge residual도 photon과 비슷하게 크게 줄었다. 결론은 "per-ledger 제어가 더 엄격해진 결과와 일치하며, RMS 희석과 일반적 step 축소를 판별하지 않는다"이다. 어느 block이 step을 제한했는지는 기록되지 않았다.
- charge residual `-9.934e-18`, species residual `[-7.63e-18, -3.16e-18, 3.03e-19]`는 저장 값일 뿐이다. frozen solver에는 이에 대한 assert가 없으므로 gate PASS로 표시하지 않는다.
- `observations.json`의 18개 기록은 **9개의 서로 다른 상태**다. 각 시점의 pre/post가 같은 상태를 두 번 기록한다. 각 상태의 photon budget은 1e-8 기준 안이지만 이는 dense-output 시점에서 같은 기준을 진단적으로 다시 적용한 것이며 frozen endpoint gate가 아니다. age 수렴 관측도 아니다.
- 실제 source birth jump의 paired pre/post snapshot은 여전히 없다(`source_jumps.status=MISSING_DATA`). birth-jump side 검사는 성공이 아니다.
- 60개 `IGM_STATE_OR_UNIT_DOMAIN` 기록(event4–63 각 retry0)은 SciPy controller의 reject가 아니다. native RHS가 구간 끝점(event5–63은 fraction 1.0, event4는 0.9958)의 trial state를 domain 오류로 거부한다. solver는 구간 입력을 그대로 복원하고 `max_step=Δ/4`로 재시작했으며 모든 구간이 retry1에서 완료됐다. 기존 RMS 실행도 같은 패턴(60회, event4–63)이므로 두 실행 사이의 차이 원인은 아니다. 다만 이 max_step 제한이 두 실행의 step 경로를 함께 결정한다. 근본 원인은 미규명이다.

## endpoint 관측량 (참값 아님, 비교 없음)

proper time 1.6924302009133814e13 s, N 1.2909104481275381e-9, U 5.999589648241735e-8, T 7963.159582677747 K.
species별 누적 photo `[6.7458e-5, 5.4934e-6, 2.7605e-10]`, RR `[1.6051e-6, 1.3248e-7, 6.3727e-8]`, CI `[5.1811e-9, 2.6261e-13, 2.6643e-15]`. DR은 aggregate scalar 0.0이며 species별 성공으로 해석하지 않는다. Gamma_s `[1.642e-20, 1.741e-19, 1.426e-20]`, heat `[7.397e-31, 5.228e-30, 1.253e-31]` erg/s per absorber. source-age W1은 비교 대상이 없어 계산하지 않았다.

## age32 비교: 수행하지 않음 → age 수렴성 HOLD

유일한 기존 age32 reference는 PR171 producer(`research/rei_source_age_positive_native_intake_20261016/evidence/matrix/age32`, RMS controller, 9179 RHS)다. solver/binary bytes와 error norm이 이번 block-max source와 다르므로 동일 source가 입증되지 않는다. 따라서 `compare_results.py`를 수렴 판정에 사용하지 않았다. 현재 runner `plan()`에는 age32 reference 사례가 없다. 같은 source의 age32 block-max가 필요하며, 이는 runner identity를 바꾸는 계획 항목 추가와 로컬 검증 후에만 READY가 된다.

## 실행 identity

- PR199 HEAD `18aae24bd1d102c50164bd6224a09ec5c4eaf45d`, 과학 코드 `db87456e6b2b528a046f7856c04c73c7b4b43a54`, native physics `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`.
- NCP `s1a0e5abed09`, 64× Xeon Gold 5220, 125 GiB. 사전 load 0.11. 기존 작업 종료 없음.
- task-owned blobless clone(`REI_REPO`)에서 153 native 입력을 SHA 검증했다. prepared 156 files, identity `e376b58ee3ef2b14cda70bc8d966d686db52aabc0a832cab0b8cc0ea8a430bfd`.
- cargo/rustc 1.99.0, build exit0 12.39 s, binary `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4`, solver `78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620`, fingerprint `facda29d5f123098994492422e3a7a1492b3e43ccf70fd6d64f1c9ef9d1a83c0`.
- venv Python3.12.3/NumPy2.3.5/SciPy1.17.0 (기존 venv 읽기 전용 재사용), `REI_TRANSPORT_THREADS=48`, BLAS 1, moment-rounding none, rpc binary64.
- 전체 명령 exit0, `/usr/bin/time` wall 14:44.88 (prepare lazy fetch 포함), max RSS 341496 KiB, Python peak RSS 133176 KiB.
- NCP preflight targeted tests: 24 PASS, 2 SKIP. 26 PASS로 표시하지 않는다.

근거: `evidence/ncp_blockmax_20261019T084150Z/` (`run/AGE64_BLOCK_MAX_COMPACT_20261019.json`, `run/PHOTON_LEDGER_DIAGNOSIS.json`, raw attempt data, SHA256SUMS). compact JSON의 `common_observations.count=18`은 위의 9개 고유 상태로 해석한다. 독립 검토: `evidence/independent_review_blockmax_20261019/REVIEW.json`. binary는 Git에 넣지 않고 백업 ZIP에 보존한다.

## 다음 단계

1. **binding block 기록**: 수치 변경 없이 accepted step마다 최대 block을 기록하는 진단을 추가한다. RMS 희석과 일반적 step 축소를 판별하는 최소 증거다. 로컬 테스트와 검토 후 단일 실행만 허용한다.
2. **같은 source의 age32 block-max**: runner plan 항목 추가가 필요하다. age 수렴성 판단의 전제다.
3. **source-jump paired snapshot**: birth-jump side 검사를 위한 계측 설계.
4. native count/energy 저장 표현 연구는 계속 THEORY_REQUIRED다.

동일 age64 block-max 재실행, gate·rtol·cap 완화는 하지 않는다. 같은 RHS 수에 맞춘 RMS rtol 비교는 rtol 변경이므로 owner 결정 없이는 실행하지 않는다.
