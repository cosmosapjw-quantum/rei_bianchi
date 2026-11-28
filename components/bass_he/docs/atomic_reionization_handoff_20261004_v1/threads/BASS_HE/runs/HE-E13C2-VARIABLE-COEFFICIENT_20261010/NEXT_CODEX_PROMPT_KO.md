# BASS_HE 다음 연구 루프 인계문 — E13C2 완료 뒤

## 바로 실행할 요청

`physmath-research-loop`를 현재 host 모델에 맞게 적용해 **E13C3_EXPONENTIAL_DEFECT_CORRECTION_ON_FIXED_GAS_PATH**를 수행하라. 먼저 이 패키지의 `NEXT_DAG.json`, `REPORT_KO.md`, `THEORY.md`, `INDEPENDENT_REVIEW.json`, `state/RUN_HISTORY.json`을 읽고 지금까지 실제 완료한 범위를 유지하라. 다음 최소 계산은 저장된 여섯 local segment에 대한 저비용 지수 감쇠 보정의 평가다. 이전 결과의 이름이 바뀌었거나 문서가 옮겨졌다는 이유로 이미 끝난 계산을 다시 실행하지 말라.

## 시작 상태와 근거

Repository: `cosmosapjw-quantum/BASS_HE`.

Active branch: `research/shared-c64-crossrepo-20260928`; existing draft PR #17. 이번 게시의 실제 commit/tree와 archive identity는 detached delivery receipt가 권위다. Intake HEAD `81c1dacc1439807d41dc2684619dee499f3e06b0`는 E13C2 실행 전의 parent이며 최종 게시 HEAD라고 혼동하지 말라.

E13C2 Git projection:

`docs/atomic_reionization_handoff_20261004_v1/threads/BASS_HE/runs/HE-E13C2-VARIABLE-COEFFICIENT_20261010/`

Git에는 compact evidence와 코드·보고서가 있다. 전체 raw stage/segment/node 입력은 `BASS_HE_E13C2_VARIABLE_COEFFICIENT_20261010_v1.zip`에서 복원한다. 단순 Git projection만으로 full reproduction이 가능하다고 가정하지 말라. Archive byte SHA와 payload `FILE_MANIFEST.json`을 먼저 확인하라. 원 입력 24개의 해시는 `inputs/INPUT_FILES.json`에 있다.

바로 이전 canonical 원 archive는 `BASS_HE_E13C_PHOTON_PHYSICS_20261010_v1.zip`, 4,096,240 bytes, SHA-256 `06b5c02afb92e356ec66072a918e014f61fab5a795f26024fae55ca4d93acb33`이다. 별도 PHOTON_HEATING draft는 이 canonical 결과를 덮어쓴 것이 아니다. 그 draft의 late k7/k59 입력 문제는 독립 OPEN이다.

이번 루프는 GPT-6 Astra host metadata를 근거로 연구·코딩 harness v4.0.0을 적용했다. 다음 루프에서도 모델 라우터를 실제 host metadata에 따라 선택하라. 과거 archive의 모델 이름을 현재 실행 모델의 증거로 삼지 말라.

## 실제로 끝난 계산

OFF/KF/GM의 저장된 첫 두 macro transaction, 전체 14,652 native event segment에서 같은 affine gas 경로를 유지하고 continuous \(q(s),\lambda_i(s)\)와 captured midpoint-frozen path의 signed difference를 계산했다. 각 mode의 photon correction은 첫 macro에서 둘째 macro까지 운반했다. 새로운 native 실행 0, gas advance 0, old full3×384 replay 0이다.

Signed convention은 continuous − frozen이다. 여섯 transaction 모두 총 primary heat가 감소했고 상대 차이는 −1.46×10⁻⁷부터 −2.16×10⁻⁷이다. HI·HeI count는 감소하고 HeII count는 증가한다. 첫 macro에서만 HeI 직접항이 양수이며 field feedback이 더 큰 음수다. 둘째 macro의 HeI 직접항은 음수다.

기존 gas algebraic tolerance로 나눈 heat 차이는 −142.49부터 −277.94다. **이 tolerance는 continuum time-discretization acceptance가 아니다.** 이 수치를 기존 solver의 FAIL, gas state error 또는 cosmological observable error로 바꾸어 말하지 말라.

새 E13C2 계산의 rtol 2e−9/2e−11 대조는 최대 1.2122×10⁻⁹ old-TOL 차이를 보였다. 별도 70자리 Decimal 12/20점 collocation의 여섯 local control과 비교한 최대 차이는 number/count 7.6342×10⁻²⁴, absorption energy 5.1049×10⁻²³ eV다. Exact Fraction Taylor 항등식 17/17도 통과했다. 독립 reviewer의 scoped 판정은 별도 파일에 있다.

Primary coefficient arithmetic은 64 significand bits인 longdouble, ODE state는 binary64였다. “128-bit 전체 계산”이라고 부르지 말라. Decimal oracle은 local captured `f0`에서 시작하며 global correction history 전체의 독립 oracle이 아니다.

최초 primary evidence는 당시 입력 23개를 검증했다. 이후 oracle provenance에 필요한 원 `photon_green.py`를 24번째 입력으로 추가했고, 이 파일은 primary가 import하지 않는다. 최초 실행에 producer code SHA가 기록되지 않았으므로 최종 코드 hash를 당시 실행의 hash로 소급 주장하지 말라. Scientific RHS는 그대로이며 precision/outflow guard만 이후 추가했다. 최초 verifier가 symbolic 결과를 PASS gate에 연결하지 않은 결함은 수정했고, 독립 false-symbolic fixture가 old PASS / corrected FAIL을 확인했다. 최초 evidence를 보존했다.

## 다음에 풀 문제와 최소 실행

목표는 E13C2 reference를 이용해 **base optical depth를 그대로 유지하는 1차 coefficient-variation correction**의 비용과 정확도를 측정하는 것이다. 실제 \(\Lambda_m h\) 최대가 약 0.64057이므로 단순 \(h^3\) Taylor 항만으로 값이나 부호를 보증하지 말라.

\[
r=\delta q-\delta\Lambda\widehat P,\qquad
e'=r-\Lambda e,
\]

\[
e_1(u)=e^{-\Lambda_m u}e_a+
\int_0^u e^{-\Lambda_m(u-v)}r(v)\,dv.
\]

정확한 remainder는

\[
e-e_1=-\int_0^u e^{-\Lambda_m(u-v)}\delta\Lambda(v)e(v)\,dv.
\]

\(e_a=0\)인 local control이면 \(\sup|e-e_1|\le D_\Lambda B_r\)다. Incoming correction이 있으면 \(D_\Lambda(|e_a|+B_r)\)와 incoming uncertainty를 포함하라. Samples를 적분한 값만으로 outward enclosure라고 주장하지 말라.

Moment correction에는 직접항 \(\int w\delta\lambda_i\widehat P\)와 field 항 \(\int w\lambda_{i,m}e_1\)를 모두 넣고, remainder의 \(\delta\lambda_i e\) 항을 빠뜨리지 말라. \(w=1,E,E-\chi_i\)의 차이를 유지하라. Source injection과 redshift energy 차이도 보존식에 포함한다.

순서는 다음과 같다.

1. 기존 수식과 저장 oracle의 입력·단위를 확인하고 cheap correction의 구현 범위를 고정한다.
2. 이미 선택된 여섯 local control에서 새 correction만 계산해 저장 E13C2 reference와 비교한다. Reference를 다시 구하지 않는다.
3. `NEXT_DAG.json`의 연구용 1% total-heat correction 재현 기준, count/heat signed errors, positive endpoint, source/redshift ledger를 평가한다. 1%는 physical acceptance가 아니다. 거의 0인 차이에 대한 상대오차는 강제로 계산하지 않는다.
4. Local gate가 통과하고 누적 incoming correction을 다룰 준비가 된 경우에만 같은 first2 path로 새 approximation을 확장한다. Reference와 gas path는 그대로 둔다.
5. 실패가 나면 최초 결과·입력·명령을 보존하고 수학/물리/수치/구현/환경을 구분한다. 결과를 보고 tolerance를 완화하거나 기존 campaign으로 문제를 덮지 않는다.
6. Contributor와 분리된 실제 독립 final reviewer를 거쳐 범위가 한정된 결론과 다음 DAG를 작성한다.

## 보호 상태와 소유권

`baseline_RCT=OFF`; actual atomic RCT photon/heat/recoil moments `null`; physical/production `HOLD`; HE-F2/F09 `OPEN`; receiver adoption 별도; legacy Gamma alias `3.543295 FAIL` 유지.

원 atomic long lane, 실제 spectrum-average sign, gas/coupled solve, late k7/k59 stock 문제는 이 노드의 자동 실행에 포함하지 않는다. Receiver owner가 아직 정하지 않은 continuum accuracy budget을 Newton tolerance로 대신하지 않는다. 같은 날짜의 parallel draft를 canonical source로 승격하거나 다른 repository의 owner 상태를 수정하지 않는다.

기존 연구 branch에서의 additive non-force 게시와 기존 Drive/Dropbox dossier 폴더의 create-only 백업에 대한 누적 authorization을 유지한다. 최종 결과가 구체적으로 준비되고 독립 검토된 뒤 실행하라. 기존 파일·evidence는 덮어쓰지 않는다. Ref를 갱신하기 직전에 실제 HEAD를 확인하고 expected SHA를 사용한다. PR merge, production 설정 변경, 사람에게 메시지 발송 또는 receiver 채택은 이 인계의 권한 범위가 아니다.

## 기본 확인 명령

Archive를 복원한 패키지 루트에서:

```bash
python3 -B code/reproduce.py --output ../e13c2_resume_verify_new
```

이 명령은 저장 evidence의 재검증이다. `--recompute`는 이번 E13C2 계산만 다시 만드는 선택 경로지만, 다음 연구를 시작한다는 이유만으로 실행하지 말라. E13C3의 새 판별 계산을 먼저 수행하라.
