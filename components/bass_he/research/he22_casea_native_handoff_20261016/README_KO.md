# BASS_HE HE22: source-age photon to native H/He Case-A coupling

작성 및 로컬 테스트: 2026-10-16 KST. **새로 구현한 실제 코드**이지만 여기서 성공한 부분은 Python 인터페이스/보존법칙 테스트에 한정한다. 64-vCPU/125-GiB NCP 명령 실행은 원격 Desktop Commander 월간 사용 한도 때문에 이번 세션에서 시행하지 못했다. NCP Rust/원본 `rei_microphysics` 구동 PASS나 fully coupled EoR를 주장하지 않는다.

## 구성

- `src/he21_photo.py`: 변경하지 않은 HE21 v3 source-age BB50K + Verner photo-only 기준 (SHA와 원본 v3 tar 동봉).
- `src/he22_contract.py`: 현재 광자 stock의 한 chemical midpoint에서 양의 competing-H/He photoevent 생성, native-photo 단위 변환, native micro 에너지 항등식, 물리 영역 안의 damped 4D Newton, 예외/HOLD.
- `src/he22_coupled.py`: HE21 원래 방출시각/방향/지지집합/적색편이와 Strang gas half-step을 유지하면서 chemical midpoint만 native backend 호출로 교체. 계량은 photon/thermal/binding/work/escape/CMB로 귀속; 실재 Grackle 입력은 native factory가 책임진다.
- `src/he22_owner_point.rs`: 원본 `rei_microphysics::igm_point_rhs`에 *단일* native 물리 평가를 수행하는 Rust CLI. `h=0`으로 geometry source 중복을 방지. 컴파일 대상 실제 소스 커밋은 `SOURCE_LOCK.json`으로 고정.
- `src/he22_native_client.py`: 원본 Rust 출력/밀도/헬륨 비율을 검증한 후 Python 계산으로 반환. 오류 시 대체/가짜 physics로 진행하지 않는다.
- `src/run_native.py`: bounded, independent original Rust case pilot→matrix 및 원자적 JSON 체크포인트; 실패 최초 기록 보존.
- `tests`: original HE21 baseline 포함하여 로컬 24개 Python 검사 PASS. HE22 mock은 **오직 데이터형과 conservation path 테스트**이며 Native Grackle 인증이 아니다.
- `ncp/NCP_BOOTSTRAP_AND_TEST.sh`: 비침습적 별도 Git clone, 원본 rlib 빌드, native wrapper 빌드, tests/pilot/opt-in matrix 실행. 시스템 Python 설치 금지. 네트워크/툴체인 실패 분류.
- `ncp/LOCAL_RETRIEVE_AND_BACKUP.sh`: 사용자 Ubuntu에서 NCP raw archive를 가져온 뒤 Dropbox+Google Drive를 create-only로 업로드하고 두 원격 스트림 SHA-256 재검증.
- `CODEX_HANDOFF_PROMPT_KO.md`: 선택된 실행 DAG와 실패 분류, 발표 주장의 범위, 게시 및 백업 요구.
- `inputs/`: 원본 HE21 v3 15,251-byte archive 및 독립 REI LRS dynamic chemistry 참고 ZIP. 원본 repo와 독립 실험은 각각 다른 authority. 원본 `rei_microphysics` 소스 전체는 Git SHA로 고정하고 NCP에서 clone하며, 개인 인증키는 동봉하지 않는다.

## 실제 이론·수치 계약

HE21에서 방출 코호트는 proper source midpoint마다 이미 **한 번** 생성된다. CR72의 내부 연속 source `s_p dt phi1`를 이 photo step에 다시 넣으면 source를 두 번 계상한다. 따라서 HE22의 midpoint photo map은 `s=0`의 보존적 감쇠와 경쟁 H/He 흡수 분배를 사용하고, 배경/기체 두 half map의 일은 외부 HE21 한 코드가 소유한다.


a) `Lambda_j = c n_H alpha_j sigma_j(E)`, `alpha=(1-x_HII,Y(1-x_HeII-x_HeIII),Y x_HeII)`, `Delta N_j = N(1-exp(-Lambda_total dt)) Lambda_j/Lambda_total`.

b) native inputs: `Gamma_j=sum(Delta N_j)/(dt alpha_j)` [s^-1], `h_j=EV_ERG sum[(E-I_j)Delta N_j]/(dt alpha_j)` [erg absorber^-1 s^-1]. If `alpha_j=0`, require the actual event=0 and set native input zero. No arbitrary rate floor.

c) original native `igm_point_rhs` solves the same endpoint `g1-g0-dt F(g1,Gamma(g1),h(g1))=0` with gas `(xHII,xHeII,xHeIII,u_eV/H)`. It owns CI/RR/DR, cooling, CMB, Case-A escape. Physical binding energies `I_j` are distinct from Verner fit lower-cut energies.

d) Number: `N_old+N_birth=N_survive+sum A_j` when source cohorts are born once before the chemical step. With all outer half maps and source events:

`U_gamma,init + U_birth + u_init + E_CMB = U_gamma,end + u_end + Delta B + W_gamma + W_gas + E_escape`.

`B=I_H xHII + Y[I_HeI(xHeII+xHeIII)+I_HeII xHeIII]`. Rate identity `thermal_micro+binding_micro+escape-cmb-photo_input=0` must hold for **the actual original native RHS**. Neutral nuclei support and nonnegative photon/heat must survive. Photon birth ages/directions remain distinct. A stored `source_count` normalized in log(a) is a **declared surrogate**, not actual original MD14 time-dependent emissivity.

## 로컬 검증과 실행 규칙

`OPENBLAS_NUM_THREADS=1 PYTHONPATH=src pytest -q -p no:cacheprovider tests` → 23 PASS (see `results/LOCAL_TEST_LOG.txt`). `tests/test_he22_coupled.py` performs a photo-only constructed-owner comparison with HE21; `ConstructedCaseAEscapeTestDouble` separately checks mock recombination energy ownership. Neither uses original Grackle. `he22_owner_point.rs` is source-complete but **NOT COMPILED** in this ChatGPT environment (`rustc` absent). Need original Python deps/rustc on NCP.

Current claim gate: **DERIVED, LOCAL_PYTHON_IMPLEMENTATION_VERIFIED; NCP_RUST_NOT_RUN; NATIVE_CHEM_PHYSICS_UNRESOLVED; COSMOLOGICAL_EOR_HOLD.** Do not mark a native test PASS from printed scripts, or repeat historical HE20 tests without an affected dependency.

Follow the ready-to-use `CODEX_HANDOFF_PROMPT_KO.md`. Run the compiled source in a new NCP scratch directory; do not modify the owner's production worktree or change existing PR150 full-history campaigns. When native RHS fails, preserve the first raw output and exact command before repairing **only** a diagnosed defect. A source mismatch is not a reason to adjust physical tolerances.

## Primary methods

Mellema et al. (2006), DOI 10.1016/j.newast.2005.09.004; Friedrich et al. (2012), DOI 10.1111/j.1365-2966.2012.20449.x; Verner et al. (1996), ApJ 465, 487; Grackle 3.4.1 docs `https://grackle.readthedocs.io/en/grackle-3.4.1/Parameters.html`. Origin of the physics is literature-supported; new coupler, mock tests, and expected NCP contracts are **derived/locally checked**.

추가 로컬 대조: `results/LOCAL_PHOTO_LIMIT_CHECK.json`에서 q=-0.005,0,+0.005, m4/n4의 H I photon event 수는 HE21와 HE22 photo-only test double 사이에 각각 수치적으로 완전히 동일하며, 온도 차이는 약 3×10^-12 K; 이것은 native Rust 화학 정확도가 아니라 인터페이스 극한 회귀 결과다.
