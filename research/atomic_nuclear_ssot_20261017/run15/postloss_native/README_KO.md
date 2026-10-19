# RUN15 postloss native source quadrature

## 검증된 범위

2026-10-19 workspace 경로 소실 뒤, 실제 도구 출력에 남아 있던 production 소스를 사용해 **새 crate를 작성하고 Rust 1.94.1로 실제 컴파일했다.** 하나의 native CLI process에서 정확히 세 개의 source quadrature control을 계산하고, 독립적인 SciPy QUADPACK 적분과 비교했다. 세 control 모두 지정한 mass, physical mean 및 positive interior node 조건을 만족했다.

이 산출물은 소실 전 RUN15 전체 source archive의 byte 복원을 뜻하지 않는다. 원래 `lib.rs`의 test 부분은 완전하게 회수되지 않았다. 누락된 tests를 채우지 않았고, 과거 9 tests를 재실행하지 않았다. 새로운 native IVP는 0회다.

## Source identity

| 항목 | 현재 source 및 검증 상태 |
|---|---|
| `src/main.rs` | 원래 전체 파일 1,916 bytes와 SHA-256 `347e9900e4392b8bd1c7ded852ef3412d7867622be46f79a30b6ba250f11760b` 일치 |
| `src/lib.rs` | 원래 1–324행의 production 구현을 그대로 복사한 **새 완전한 Rust source file**, 11,840 bytes, SHA-256 `88fc199c4f6ab00f01619c203a8e4ce2082f261c55d8bb761f2c8c8f28e2942c` |
| 소실 전 전체 `lib.rs` | 원래 16,705 bytes, SHA-256 `7be80eef3ff45132e0a6cc51e0ebb23c3ee6f602240d963fd1c8d6539ca1f971`; 전체 파일 복원 미완료 |
| 원본 atomic/gas dependency | RUN13 `rei_bass_coupled`, Git `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`에서 확보한 91개 code 파일. 두 native build 뒤에도 전부 원본과 일치 |
| 신규 package | `rei_run15_postloss_positive_planck` |
| 신규 binary | `positive_planck_panel_postloss`, 569,800 bytes, SHA-256 `ec88048296f47a4683595aeddcafe2453cfef85bdada53189143913b076e8f66` |

원문 fragment와 회수 범위는 `provenance/`에 보존했다. 새 crate provenance는 `SOURCE_PROVENANCE.json`에 있다. 새 binary에는 소실 전 binary의 identity를 부여하지 않는다.

## API와 수학적 범위

`panel(lo, hi, kt, order)`는 기존 source shape

\[
dM(E)=\frac{E^2}{\operatorname{expm1}(E/kT)}\,dE
\]

의 positive quadrature를 반환한다. 입력 energy와 `kt`의 단위는 eV, absolute weights와 mass는 eV³다. Photon normalization 이전의 source measure이며, evolved survivor를 보정하는 알고리즘이 아니다.

회수한 production 구현은 local coordinate \(z=(E-\mathrm{mid})/\mathrm{half}\)에서 positive GL64 measure를 만들고, Stieltjes recurrence와 작은 symmetric Jacobi eigensolver를 사용한다. Total mass는 변경하지 않은 RUN13 `blackbody_moments`의 \(M_0\)에 맞춘다. Order 범위는 2–16이다. 이 코드에서 원자 공급자, gas 초기조건, geometry, threshold 또는 packet은 변경하지 않았다.

Positive discrete measure에 대한 polynomial exactness와 연속 source의 오차 bound는 서로 다른 명제다. 이번 세 control은 실제 수치 진단이며 continuum enclosure, 전체 spectral convergence, nonlinear opacity feedback bound를 확립하지 않는다.

## 이번에 실제 계산한 세 control

모든 control의 `kt=4.0 eV`는 명시적인 **manufactured source 설정**이다. 과거 RUN13/RUN15 packet의 설정을 교체하지 않는다. 독립 참조값은 local coordinate에서 연속 Planck shape를 QUADPACK으로 적분했다.

| Control | Energy band (eV) | Order | Mass (eV³) | 참조 mass 상대차 | 참조 mean 절대차 (eV) |
|---|---|---:|---:|---:|---:|
| Sub-H source moments | [13.598434599702, 13.6] | 2 | 0.009997262946094005 | 0 | −1.7763568394002505e−15 |
| Thin band | [13.6, 13.6000001] | 6 | 6.385836287920841e−7 | +1.658030579441313e−16 | +1.7763568394002505e−15 |
| Optical panel source | [13.598644599702, 13.598884599702] | 8 | 0.001532811952995095 | −1.4146577737301527e−16 | −1.7763568394002505e−15 |

모든 node가 해당 band 내부에 있고 모든 absolute weight가 양수다. n2의 local moments 0–3 정규화 차이의 최대값은 약 `1.1408851697605662e-13`이다.

폭 `1e-7 eV` band에서는 출력된 binary64 energy를 local `z`로 다시 바꾼 moment 2의 차이가 `3.908668023718045e-9`로 관측됐다. 좁은 band의 energy-to-z 변환은 energy 반올림을 `1/half`만큼 증폭한다. 이 이유로 narrow-band 검증은 계산 전에 mass·physical mean·positivity로 범위를 정했으며, local moment 차이도 삭제하지 않고 receipt에 함께 남겼다.

실제 stdout, 모든 node/weight, QUADPACK 값과 추정 오차, 사전 acceptance threshold는 `evidence/controls/THREE_CLI_CONTROLS.json`에 있다. Build와 exact commands는 `evidence/POSTLOSS_NATIVE_BUILD_RECEIPT.json`, 원본 code 불변성은 `evidence/OWNER_UNCHANGED_AFTER_NATIVE_BUILD.json`에 있다.

## 재현 명령

`Cargo.toml`은 저장소 내 canonical 위치인 `run15/postloss_native`에서 `../../run13/recovered/code/rei_bass_coupled`를 참조한다. `/tmp` 생산 경로가 template에 고정되어 있지 않다.

Canonical Git checkout에서는 다음과 같이 별도 새 output 경로에 build와 세 control만 실행한다. Rust prefix는 공식 1.94.1의 `bin/rustc` 및 `bin/cargo`를 포함해야 한다. Python에는 SciPy가 필요하며 이번 실제 실행은 Python 3.12.14, SciPy 1.17.0이었다.

```bash
python -B /path/to/run15/postloss_native/build_and_check.py \
  --crate-root /path/to/run15/postloss_native \
  --toolchain-prefix /path/to/rust-1.94.1-prefix \
  --output-root /path/to/new-native-evidence
```

다른 디렉터리 배치에서는 원본 native source를 명시해 새 build copy를 만든 뒤 같은 검증기를 실행한다.

```bash
python -B /path/to/postloss_native/materialize.py \
  --source-root /path/to/rei_bass_coupled \
  --output-root /path/to/new-build-crate

python -B /path/to/postloss_native/build_and_check.py \
  --crate-root /path/to/new-build-crate \
  --toolchain-prefix /path/to/rust-1.94.1-prefix \
  --output-root /path/to/new-native-evidence
```

`materialize.py`는 복사본의 Cargo dependency 경로만 변경하고 각 원본/복사 hash를 기록한다. 배포된 `Cargo.lock`은 실제 `cargo generate-lockfile --offline` 산출물이다. 일반 재현에서는 `--generate-lock`을 사용하지 않는다. Build는 `--release --offline --locked --jobs 2`이며, target과 Cargo cache는 source 밖에 둔다.

검증 지위는 `IMPLEMENTATION_VERIFIED_WITH_THREE_NUMERICAL_CONTROLS`다. 원래 missing tests, 전체 historical RUN15 source와 trajectory의 복구 상태, threshold-crossing과 전체 nonlinear spectral 오차 문제는 이 작은 실행 증거와 별도로 관리한다.
