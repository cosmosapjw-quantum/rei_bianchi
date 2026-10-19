# RUN18 Rust 패키지의 실제 적용과 검증 경계

## 실제 적용 결과

`num-rational 0.4.2`의 `BigRational`과 원본 VigilODE `directed.rs`를 새 crate
`exact_dense_adapter`에 실제 적용했다. 기존 Rust 1.94.1을 사용해 오프라인으로
빌드했으며, 새 테스트 3개와 변경 없이 포함한 VigilODE 테스트 1개가 통과했다.
사용자가 재첨부한 installer를 사용한 작업은 없다.

독립 Python reference와 Rust 계산은 RUN17 B의 저장 다항식 23개와 기체/깊이
257성분에 대해 5,911개 오른쪽 종단 값과 접합 관계를 대조했다. VigilODE의
구간 산술은 같은 오른쪽 종단의 정확한 값 5,911개와 정확한 도함수 5,911개를
포함했다. 비교 대상은 반올림한 실수가 아닌 `BigRational` 값이다. 도함수
접합을 위해 시작점 도함수도 정확하게 계산했다. 이 구간 포함 시험은 각
시간 panel 전체의 비선형 residual enclosure가 아니다.

| 검증량 | 실제 결과 |
|---|---:|
| 내부 기체 상태 접합 불일치 | 0 / 110 |
| 내부 깊이 상태 접합 불일치 | 431 / 5,544 |
| 최대 깊이 접합 크기 | `1/36028797018963968 = 2^-55` |
| 누적 부호 포함 깊이 offset의 최대값 Γ | `9/288230376151711744` |
| Γ의 표시용 근삿값 | `3.122502256758253e-17` |
| 표현 연속화만의 상대 survivor 상한 β | `9/288230376151711735` |
| 연속화 후 깊이의 정확한 Bernstein 하한 | 23개 panel 모두 비음수 |
| 마지막 종단의 저장 상태 불일치 | 0 |
| 실제 Rust CLI process | 2 |
| 이 실행의 기체 RHS / IVP / quadrature | 0 / 0 / 0 |

실제 결과, 정확한 입력 해시, 명령, 시간과 원시 출력을
`adapter_execution01/RUST_EXACT_VIGILODE_RESULT.json` 및 같은 디렉터리의
TSV/JSONL 파일에 보존했다. Rust 종단 계산은 1.6731초,
검증 Python process의 전체 측정 시간은 1.8764초였다.

정의는 `J_i = 다음 accepted 상태 - 앞 panel의 정확한 다항식 종단`이며,
`c_i = 이전 내부 J들의 부호 포함 합`, `tau_tilde_i = tau_i - c_i`이다.
따라서 저장 다항식의 연속화가 구성된다. 양의 source weight와
`0 <= Γ < 1`에서 이 **표현 수정만**의 상대 survivor 변화는
`exp(Γ)-1 <= Γ/(1-Γ) = β`로 제한된다. 기체 tube, 정확한 IVP 해,
스펙트럼 연속 극한 또는 전체 sub-H 오차의 상한은 아직 주어지지 않는다.
도함수의 좌우 불일치는 1차 상태 residual의 원자적 jump 항이 아니다.

## 패키지 선택과 실제 사용 지위

| 항목 | 현재 적용 지위 | 용도와 확인한 제약 |
|---|---|---|
| `num-rational 0.4.2` + `num-bigint 0.4.6` | 실제 빌드·실행 | 저장 binary64의 정확한 유리수 변환, 다항식 값/도함수, Bernstein 계수, 접합 및 β |
| VigilODE `directed.rs` | 원본 그대로 포함하여 실제 실행 | 같은 식의 outward interval 계산과 정확한 유리수 포함 대조 |
| `inari 2.0.0` | 공식 원본 다운로드·검산·정적 조사만 | 독립 구간 산술 대조 후보. 기본 `gmp` feature는 GMP/Rug를 가져오므로 현재 빌드하지 않음 |
| `rug 1.30.0` | 공식 문서 조사만 | GMP/MPFR/MPC 기반 고정확도 및 명시적 rounding이 필요해질 때 후보. 이번에 다운로드·빌드하지 않음 |

`num-rational` 공식 API는 arbitrary precision `BigRational`을 제공한다.
실제로 받은 0.4.2의 `src/lib.rs`에서 `from_float`가 비유한 값을 거부하고
finite binary64를 정수와 2의 거듭제곱으로 변환하는 구현을 읽었다.
사용한 다섯 dependency archive는 `num-rational`, `num-bigint`,
`num-integer 0.1.46`, `num-traits 0.2.19`, `autocfg 1.5.0`이며 합계
223,651 bytes이다. Cargo.lock은 정확한 버전과 공식 checksum을 고정한다.
문서: <https://docs.rs/num-rational/0.4.2/num_rational/>.

`inari`는 IEEE 1788.1/1788의 부분 집합을 구현하는 `Interval`/
`DecInterval` API를 제공한다. 실제 2.0.0 archive의 Cargo.toml,
README와 `src/simd/x86_64.rs`를 읽었다. x86-64에서는 AVX+FMA 또는
AVX512F target feature 요구가 있으므로 새 호스트에서는 CPU와 build
flags를 먼저 맞춰야 한다. `default-features = false`는 GMP 의존을 피하는
선택이지만 제공 연산 범위도 달라진다. 이번에는 해당 feature 조합의
빌드나 정확성 확인을 실행하지 않았다. 문서:
<https://docs.rs/inari/2.0.0/inari/>.

`rug`의 공식 문서는 arbitrary precision Integer/Rational/Float 및
MPFR rounding API를 설명한다. 현재 exact dyadic 식은 작은 pure Rust
의존성으로 해결되었으므로 GMP/MPFR/MPC build를 추가하지 않았다.
문서: <https://docs.rs/rug/1.30.0/rug/>.

## VigilODE 원본의 정확한 적용

실제로 읽은 저장소는 <https://github.com/cosmosapjw-quantum/vigilode>이며
확인 commit은 `ac1cd2a4738c2441c92e5fdae5f70aba35e53544`다. Core source base
`a21d573980f66fe02891bd216153443b5352f921`와의 `crates/` byte identity는
별도 inventory가 기록한다. 이 adapter는 그중
`crates/rodas5p-core/src/directed.rs`의 17,215 bytes를 그대로 포함한다.

- SHA-256: `2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814`
- MIT LICENSE SHA-256: `bfb425597830af905d9b52262dc5fc56e436de05796f6638a78258adaa0b8760`
- 원본과 LICENSE는 `exact_dense_adapter/provenance/`에 있다.
- 변경한 원본 산술 행은 0개다. `CoreError`의 두 variant와
  `CoreResult` alias만 새 crate에서 제공한다.

실제 사용 API는 `Interval::point/new/add/sub/mul/div`다. 공개된 interval
field를 직접 신뢰하지 않고 입력 생성자는 finite/domain 검사를 거친다.
VigilODE의 `exp_interval`과 logarithmic-norm helper가 있다는 사실은
읽었지만 이번 endpoint 검증에 그 함수의 실행 성과를 포함하지 않는다.
전체 VigilODE workspace, RODAS5P integrator 또는 private quartic tube
verifier를 빌드·실행한 것도 아니다. DOP853의 degree-7 recurrence는
새 adapter에 명시적으로 구현했다.

## 다음 연속 오차 인증에 필요한 구체적 입력

저장 다항식의 연속성과 물리 영역 하한은 이제 exact arithmetic으로
검증할 수 있다. 다음 작업은 원래 HHeD physical owner를 보존한 채,
선택한 전체 panel과 상태 tube에서 다음 값을 실제 포함하는 구현이다.

1. 원래 native gas reaction, photoabsorption 및 heat의 interval RHS.
2. 동일한 invariant five-coordinate lift와 명시적 scaling에 대한 interval
   gas Jacobian, gas-to-depth와 depth-to-gas coupling 상한.
3. polynomial derivative와 RHS의 차인 연속 forcing defect의 포함.
4. 이전 prefix의 초기 오차와 source/event 경계 및 표현 접합 항의 분리.

VigilODE의 continuous-provider trait은 전체 상자 RHS와 전체 tube의
logarithmic-norm 상한을 요구한다. native f64 server의 점별 RHS/Jacobian
출력만으로 이 계약을 충족하지 않는다. 먼저 원래 rate branch와 threshold,
temperature-domain 조건을 포함하는 interval extension을 작성해야 한다.
작은 gas block에서 실제 interval Jacobian을 얻은 다음, inventory가 확인한
VigilODE symmetric-part/Gershgorin 또는 interval-Cholesky 도구를 적용할 수 있다.
현재 작업은 이 다음 노드를 지우거나 이미 완료한 것으로 표시하지 않는다.

## 실패 및 제한 보존

최초 inline Python probe는 괄호 오타로 실행 전에 parse 실패했다. 이후
실제 probe는 한 번 실행했다. 기본 sandbox의 crates.io 읽기는
`Operation not permitted`로 실패했고, 허용된 read-only network escalation에서
공식 metadata와 소형 archive 다운로드가 성공했다. 공식 checksum과 실제
바이트는 일치하지만 별도 서명 검증을 했다고 주장하지 않는다.

Cargo build의 유일한 경고는 테스트에서만 쓰는 `Signed` import가 release에서
사용되지 않는다는 것이다. 검증된 소스와 binary identity를 유지하기 위해
해당 비기능 경고를 지우는 재빌드를 하지 않았다. 다운로드 receipt의
`builds: 0`은 다운로드 단계의 상태이며, 후속 실제 빌드·테스트는
`build_execution01/BUILD_RECEIPT.json`이 기록한다.

후속 오프라인 복원 helper를 준비하는 동안 다른 agent가 tool launch의
`bubblewrap ... /tmp/.git ... No space left on device`를 보고했다. 이를
Rust 계산 실패로 분류하지 않는다. helper 실행 여부는 별도 복원 receipt로
확인해야 한다. 기존 결과나 원본을 삭제하는 정리 작업은 이 unit에서 하지 않았다.
