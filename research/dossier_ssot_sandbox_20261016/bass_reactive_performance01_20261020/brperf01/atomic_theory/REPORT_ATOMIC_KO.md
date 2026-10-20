# BRPERF01 — T-only 원자계수 연구와 Li/C/N/O 카탈로그

## 판정과 구현 범위

이 bounded subunit은 **`COEFFICIENT_AND_T_TABLE_ONLY_NO_NETWORK_ADMISSION`**으로 검증되었다. 원저자 데이터에서 Li·C·N·O의 24개 bound-electron 이온 단계에 대한 광이온화(PI)와 전자 충돌이온화(CI), 그리고 12개 단계로의 복사 재결합(RR)을 Rust로 옮겼다. CI·RR 계수는 초기화 때 양의 로그 표로 전개한 뒤 재사용한다. 동일 온도를 여러 이온에 쓸 때는 `PreparedTemperature`가 `ln(T)`를 한 번만 계산한다.

H/He/D 반응망, 기존 `JointCxSplit`/CX half-flow, four-corner 시간 제어기 및 physical owner는 수정하지 않았다. 새 계수는 독립 opt-in crate이다. 원소·전하 단계의 원자 fit이며, Li-6/Li-7 또는 C/N/O 동위원소별 정밀 물리나 핵반응을 추가한 것이 아니다. 새 원소의 abundance, binding-energy owner, 초기조건과 source spectrum도 도입하지 않았다.

실행 결과의 수치 SSOT는 `evidence/INDEPENDENT_VERIFICATION.json`, 모든 표별 값은 `evidence/TABLE_SCANS.csv`, Rust의 10,812개 직접 평가값은 `evidence/ATOMIC_VALUES.csv`이다. 계수에 대한 오차 검증을 전체 반응 이력의 오차나 광자 birth/spectrum 수렴으로 승격하지 않는다.

## 1. 기존 owner에서 확인한 T 의존성

부모 BR06의 `parent/crate/owner_src`에서 `igm_rates.rs`, `rate_table.rs`, `igm_thermal.rs`, `atomic_provider.rs`, `deuterium_atomic.rs`, `deuterium_charge_exchange.rs`를 직접 읽었다. SHA-256은 `evidence/INSPECTED_OWNER_IDENTITY.json`에 있다. Grackle source pin은 `af7939494ce65007887ada7b98d1813df6843346`이다.

| 원 계수 | T 표에 저장할 값 | 매 RHS에서 다시 계산할 인자/판정 |
|---|---|---|
| HI/HeI/HeII CI 3개 | cm³/s 계수 | 각각 `ne*nHI`, `ne*nHeI`, `ne*nHeII` |
| HII/HeII/HeIII RR 3개 | cm³/s 계수 | 각각 `ne*nHII`, `ne*nHeII`, `ne*nHeIII` |
| HeII DR | cm³/s 계수와 정확한 low-branch zero | `ne*nHeII`; 활성 분기의 냉각 항 일치 |
| HI/HeII CE | erg cm³/s 계수 | `ne*nHI`, `ne*nHeII` |
| metastable HeI CE | **erg cm⁶/s** 계수 | **`ne²*nHeII`**; 다른 CE와 단위·차수 다름 |
| RR cooling 3개 | erg cm³/s 계수 | 이온 밀도·전자 밀도, escape/chemical ledger |
| DR raw cooling | 원 raw 계수 | low branch에서 제외한 잔차를 별도 진단으로 보존 |
| free-free | T-only Gaunt factor 포함 계수 | `ne*(nHII+nHeII+4*nHeIII)`; D plasma 기여 별도 owner |
| D CI/RR/CE | H-equality 계약에 따른 동일 prepared H bundle의 재사용 | D 밀도 및 D binding/defect의 원 owner |
| H–D CX forward/reverse | 원 Savin 경험식은 T-only | 반응물 밀도와 exact frozen-rate map; 이번에 변경하지 않음 |
| photoionization | 단면적은 E의 함수 | 실제 photon cohort의 E(t), source flux, 경쟁 흡수와 birth geometry |
| CMB Compton exchange | 고정 상수 prefactor만 캐시 가능 | `ne*Tcmb^4*(Tcmb-T)`; 일반적인 하나의 T 표로 대체 불가 |
| expansion/geometry work | 없음 | H, V, EOS, 각 photon Killing 경로 |

기존 `IgmRateTable`은 이미 15개 채널, 기본 65,537개 균일 `ln T` nodes, coefficient-major 저장, SoA batch 및 thread batch를 제공한다. 기존 표를 새 발견인 것처럼 재구현하지 않고, root 통합에서는 중복 좌표 계산과 allocation을 줄이는 쪽을 다룬다. 이 subunit은 원소 확장과 그 표의 별도 오차 계약에 집중한다.

원 low-temperature source의 운영 범위는 1–10⁶ K이며, 이것을 전 범위의 경험적 지지라고 부르지 않는다. 5,500 K RR 분기, `T/11605 <= 0.8` 분기, CI floor-mask 전환, CE/DR exponent caps는 보간 셀 경계에서 직접 평가 fallback을 유지해야 한다. CI `1e-20` floor와 CE exponent cap은 source에 실제 있는 값이다. 이 값을 줄여 underflow처럼 처리하면 source가 바뀐다. `PreparedIgmRates`는 EOS에서 얻은 정확한 동일 T에만 재사용할 수 있다. 조성·에너지 변화 이후 T가 달라지면 새 bundle이 필요하다.

## 2. 양의 로그 보간과 오차

자연로그 좌표를

\[
x=\ln T,\qquad y(x)=\ln k(e^x)
\]

로 두고 한 셀에서 선형 보간 \(L[y]\)을 적용한다. 계수가 양수이고 해당 셀이 매끄러우면

\[
y(x)-L[y](x)=\frac{y''(\xi)}2(x-x_i)(x-x_{i+1}),
\qquad |y-L[y]|\le \frac{Mh^2}{8}.
\]

따라서

\[
\tilde k=\exp L[y]>0,\qquad
\left|\frac{\tilde k}{k}-1\right|\le
\operatorname{expm1}(Mh^2/8).
\]

이 상계는 exact-real interpolation error이다. 부동소수 연산 오차는 별도의 직접 비교로 검증했다. 유한한 probe 검사를 했다는 이유만으로 곡률 상계가 자동 증명되지는 않는다. 이번 CI/RR 원식은 아래의 분석적 상계를 제공하므로 그 상계로 grid 간격을 정할 수 있다.

음수·NaN 계수는 생성자/파서에서 거부한다. 구조적 0과 underflow는 다르다. 구조적 0이 증명되지 않은 셀의 양끝이 수치적으로 0이라는 사실만으로 셀 전체를 0으로 채우지 않는다. 새 CI/RR의 엄격한 유효 구간 안에서 모든 계수는 정상 양수였으며, 비정상 양수/underflow 결과는 `ArithmeticFailure`다. 원 자료 밖의 T를 grid 가장자리로 clamp하여 새로운 물리를 만들지 않는다.

Wolfram에서 로그 Voronov 곡률과 RR 곡률을 실제 미분했다. 첫 context는 Internal error였고 재시도 후 평가가 가능했다. 중간 `MaxValue` 계산에는 `Infinity::indet` 경고가 있었으므로 이를 깨끗한 상계 증거로 쓰지 않았다. 최종 검산은 비음수 제곱 항등식과 RR 미분식의 차가 정확히 0임을 확인했다. 모든 도구 응답과 경고는 `evidence/*TOOL*.json`, `evidence/WOLFRAM_FINAL_CLEAN.json`에 보존했다.

## 3. 원소 확장에 사용한 원전과 소스

Exa로 원저자 서버를 찾고 실제 ASCII·Fortran 파일을 원시 바이트로 내려받았다. SciSpace는 관련 논문 탐색에 사용했으며, 일부 arXiv 레코드의 연도/저자 메타데이터가 부정확했으므로 원저자 서버·저널 DOI·원문으로 서지 정보를 확정했다.

| 자료 | 원시 크기 | SHA-256 | 역할 |
|---|---:|---|---|
| `photo.dat` | 17,760 B | `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389` | 전체 185개 PI fit에서 24개 선택 |
| `cfit.dat` | 21,924 B | `470ea3078c64159eece6a469314dde2356e2d6ccaf618f4eaecb46649d61a5cd` | 전체 406개 CI fit에서 24개 선택 |
| `phfit2.f` | 209,916 B | `8df982535a4a2b952e33ca2ffb6d81600e156d7373fbf547a0c0170c1cecc296` | 원 PI formula/계수의 독립 파일 일치 검사 |
| `cfit.f` | 26,609 B | `7fe7d78c25166084041bea58bb55c2fcc6ad724fba8432c167cf044e6eb1bcc1` | 원 CI formula/변환상수/계수 일치 검사 |
| `rec_table1.dat` | 6,048 B | `2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091` | low-Z RR 12개 선택 |

모든 URL·HTTP metadata·다운로드 날짜는 `data/PROVENANCE.json`이다. 원시 설명 파일도 보존한다. PI 185개와 CI 406개 전체 ASCII 계수가 각각 별도의 Fortran 데이터 블록과 수치적으로 일치했다. 기존 H/HeI/HeII owner의 PI 계수 3세트도 원 `photo.dat`의 같은 원소 계수와 일치했다. 이는 coefficient identity 검증이며 기존 이력의 새 실행 결과를 뜻하지 않는다.

### 3.1 광이온화

[Verner et al. (1996), ApJ 465, 487](https://doi.org/10.1086/177435)의 원저자 [photo page](https://www.pa.uky.edu/~verner/photo.html)와 `photo.dat`를 사용한다. 바닥상태 outer-shell fit은

\[
x=E/E_0-y_0,\quad y=\sqrt{x^2+y_1^2},
\quad \sigma=\sigma_0[(x-1)^2+y_w^2]
y^{P/2-5.5}(1+\sqrt{y/y_a})^{-P}.
\]

입력 E는 eV, `sigma0`는 Mb, 출력 변환은 정확히 1 Mb = 10⁻²² m²다. `Eth` 아래는 0, `Eth..Emax`가 fit 사용 구간이며 `Emax` 위는 오류로 거부한다. 원소별 inner shell을 더하지 않은 채 `Emax`를 넘어 총단면적으로 외삽하지 않는다. 예를 들어 Li I의 `Emax=64.39 eV`이므로 source 전체 고에너지 tail에 무조건 적용할 수 없다. 원 H fitting edge 13.60 eV, 물리 binding energy 13.598434599702 eV와 제조된 D edge는 이전 계약 그대로 구별된다.

### 3.2 전자 충돌이온화

[Voronov (1997), ADNDT 65, 1–35](https://doi.org/10.1006/adnd.1997.0732)의 원저자 [col page](https://www.pa.uky.edu/~verner/col.html), `cfit.dat`, `cfit.f`를 사용한다.

\[
U=\frac{\Delta E}{8.617385\times10^{-5}T},\qquad
C(T)=A\frac{1+P\sqrt U}{X+U}U^K e^{-U}.
\]

`A`의 cm³/s를 m³/s로 10⁻⁶배한다. `8.617385e-5 eV/K`는 원 Fortran의 변환 상수이며 다른 CODATA 상수로 교체하지 않았다. ASCII의 `Tmin`은 **eV**, `Tmax`는 **keV**다. 이 둘을 K로 오독하지 않고 각 이온마다 엄격한 유효 범위를 유지한다. 원 Fortran의 `U>80` zero cutoff는 선택한 24개 fit의 이 구간에서 닿지 않는다. 따라서 그 cutoff를 이용해 저온 CI를 임의로 0으로 만든 적이 없다.

\[
\frac{d^2\ln C}{d(\ln T)^2}
=\frac{P\sqrt U}{4(1+P\sqrt U)^2}
-\frac{XU}{(X+U)^2}-U,
\qquad M\le U_{\max}+\frac5{16}.
\]

`P`는 0 또는 1, `X>0`다. 이 상계로 목표 상대오차 \(\epsilon\)에 대해
\(h\le\sqrt{8\ln(1+\epsilon)/M}\)를 고른다. 새 fit의 가장 낮은 Tmin도 1 eV, 즉 약 11,604 K이다. 따라서 이 데이터만으로 10⁴ K 또는 더 차가운 실제 EoR의 추가 원소 CI까지 검증했다고 말할 수 없다. 원 fit의 단순성/원 자료 재현 정도와 이번 f64 이식/표의 수치오차는 별개다.

### 3.3 희소한 복사 재결합

[Verner & Ferland (1996), ApJS 103, 467–473](https://doi.org/10.1086/192284), [원문 Eq. (4)](https://arxiv.org/pdf/astro-ph/9509083)를 사용한다.

\[
\alpha(T)=\frac{A}{\sqrt{T/T_0}
(1+\sqrt{T/T_0})^{1-b}(1+\sqrt{T/T_1})^{1+b}}.
\]

원 라벨은 **재결합으로 형성되는 최종 이온**을 뜻한다. `N`개 전자 항목은 `N-1 -> N` capture다. 이 catalog에서 Li I/II/III와 C IV/V/VI, N V/VI/VII, O VI/VII/VIII의 총 12개만 있다. 나머지는 `Option::None`이며 0 계수를 뜻하지 않는다. 선택한 low-Z 계수의 구간은 3–10⁹ K이며, 출력은 m³/s다. DR나 RR의 열/escape 에너지 moment를 RR 사건수 계수로 대체하지 않는다.

\[
\frac{d^2\ln\alpha}{d(\ln T)^2}
=-\frac{(1-b)s_0}{4(1+s_0)^2}
-\frac{(1+b)s_1}{4(1+s_1)^2},\qquad
s_i=\sqrt{T/T_i}.
\]

선택한 `0<=b<=1`에서 \(s/(1+s)^2\le1/4\)이므로 \(M\le1/8\)이다. 원문의 원자 자료 오차와 재결합 fit 정확도는 이번 표 보간 오차 상계와 같지 않다.

## 4. D CX 상세평형 비 검산

원 `Savin2002::rates`는 2.7–200,000 K에서

\[
k_f=2.00\times10^{-10}T^{0.402}e^{-37.1/T}
-3.31\times10^{-17}T^{1.48},
\]
\[
k_r=2.06\times10^{-10}T^{0.396}e^{-33.0/T}
+2.03\times10^{-9}T^{-0.332}
\]

의 경험식을 각각 사용한다(cm³/s). 이를 제조된 0.0037 eV defect로 계산한 `exp(-DeltaE/kBT)` 비에 강제로 맞추면 owner를 바꾸는 것이다. 실제 60자리 control에서는 174,110 K의 owner `kf/kr≈0.9651895`이고, 그 제조 defect Boltzmann 비는 약 0.9997534였다. 이 차이는 새 수치 오류가 아니다.

동일 grid와 동일 선형 연산자 L에 대해서는

\[
L(\ln k_r)-L(\ln k_f)=L(\ln(k_r/k_f)).
\]

따라서 `[ln kf, ln ratio]` 표 표현만 선택해도 ratio 근사오차가 자동 개선되지는 않는다. 그 표현은 비를 별도 검증하는 계약에 유용하지만, 정확한 owner 비를 요구하면 직접 계산 또는 ratio에 대한 별도의 오차 제한이 필요하다. 서로 다른 grid/degree로 두 계수를 보간하면 비에 두 오차가 결합한다. 이번 단위는 CX flow를 변경하지 않았다. 거친 예시 grid의 ratio 오차는 진화 계산의 오차나 이미 사용한 표의 오차로 보고하지 않는다.

## 5. 검증과 성능의 해석

새 Rust crate는 외부 crate가 필요 없고 기본 std만 사용한다. 8개 테스트는 소스 coefficient/입력 거부, 이온 범위, PI 문턱과 상한, CI의 eV/keV domain, 표 곡률 상계, 희소 RR 라벨, 과도한 grid 요청의 `TableBudget` 분류 및 prepared-temperature parity를 검사한다. strict Clippy와 scoped rustfmt도 새 코드에 대해 실행했다.

독립 Python은 원 ASCII를 다시 읽고, Rust의 로그 구현과 다른 직접 곱/거듭제곱 표현을 **stdlib Decimal 60자리**로 평가했다. PI 3,096점, CI 6,168점, RR 1,548점의 최대 상대차는 각각 `1.4134858452e-14`, `1.0383412773e-14`, `9.2864397394e-15`였다. Decimal 문턱과 f64 문턱의 1 ulp 표현 차이는 원 f64 gate에 맞춘 별도 endpoint 처리로 명시되어 있다.

| 표 | 목표 상대오차 | 실제 셀당 3개 probe 최대상대오차 | heap 계수 payload | 평가점 수 |
|---|---:|---:|---:|---:|
| 24 CI | 10⁻⁴ | 9.8430096222e-5 | 250,360 B | 93,813 |
| 24 CI | 10⁻⁵ | 9.8703899546e-6 | 791,064 B | 296,577 |
| 24 CI | 10⁻⁶ | 9.8771436075e-7 | 2,500,904 B | 937,767 |
| 12 RR | 10⁻⁴ | 8.7415094591e-5 | 23,712 B | 8,856 |
| 12 RR | 10⁻⁵ | 8.7852668772e-6 | 74,592 B | 27,936 |
| 12 RR | 10⁻⁶ | 8.7848438346e-7 | 235,680 B | 88,344 |

표 저장 용량은 struct/vector header를 제외한 f64 coefficient payload이다. 물리 fit의 불확실성은 이 수치오차보다 훨씬 큰 경우가 있지만, 그 이유로 진화 시간 적분의 오차 budget을 생략하지 않는다.

벤치마크는 Rust release, 300,000회 계수 조회, 12회 순서 교대 반복이다. 생성·파일 I/O는 timed query에서 제외했고 setup은 별도 기록했다. 공통 T 묶음에서는 **12,500개 T×24개 CI 계수**, 그 교집합 유효온도 범위를 썼으며 `ln T` 준비 비용은 timed loop에 포함했다. 각 이온마다 `ln T`를 반복 계산하는 경로와 비교하여 이를 공유한 경로가 더 빨랐다. 최종 수치는 JSON의 median 및 paired median에서 읽는다. 공유 샌드박스의 다른 작업 때문에 초기 probe와 마지막 재현 gate 사이 wall time은 변했다. 이 변화와 범위를 숨기지 않고, kernel 속도를 전체 기체·복사 solver의 속도로 환산하지 않는다. explicit SIMD, GPU 또는 추가 병렬화 효과를 이 카탈로그에서 주장하지 않는다.

## 6. 실패 분류와 다음 DAG

현재 확인한 실패는 네트워크 sandbox 권한, 첫 Wolfram 내부 오류, 경고가 있는 심볼릭 최적화 호출 및 선택적 `mpmath` 미설치였다. 공개 원데이터 다운로드는 승인된 경로로 완료했고, 심볼릭 상계는 경고 없는 항등식 검산으로 대체했으며, Python은 외부 의존성을 추가하는 대신 표준 Decimal을 사용했다. 이 실패들을 물리적 해 부재나 수렴 실패로 바꾸지 않았다. 새 atomic code에는 CX integrator 자체가 없으므로 `Cx(WorkLimit)`의 새 발생 여부를 주장하지 않는다.

| DAG 항목 | 상태 | 다음 의존성 |
|---|---|---|
| ATOMIC-SOURCE-01 원계수·단위·라벨 | COMPLETE_VERIFIED | 없음 |
| ATOMIC-CATALOG-01 PI/CI/RR 포트 | COMPLETE_VERIFIED | standalone opt-in |
| ATOMIC-TTABLE-01 양성·곡률 상계 | COMPLETE_VERIFIED_SCOPED | 시간 이력 오차 budget은 별도 |
| ATOMIC-RESTORE-01 | fresh-restore receipt 참조 | 소스 snapshot에서 실제 재빌드 |
| ATOMIC-NETWORK-01 새 원소 반응망 | NOT_ADMITTED | 아래 목록 |
| BR07 native birth/age/energy | 이 subunit에서 변경 없음 | root 기존 DAG |

추가 원소 반응망의 다음 단계에는 부족한 전하 단계 RR/DR, CX, CE와 cooling moment, inner-shell photoionization, 독립 binding-energy owner, abundance/charge/electron constraints, thermal/chemical/escape ledger, source-native 이력 검증이 필요하다. 특히 10⁴ K 아래 CI의 원자자료와 전자의 Maxwellian/바닥상태 가정을 다시 선택해야 한다. 이 coefficient library를 활용해 다음 단위를 진행할 수 있지만 그 의존성이 완료되기 전에 기존 H/He/D 이력에 활성 원소를 조용히 더하지 않는다.

## 7. 재현

공급된 Rust 1.94.1 toolchain을 활성화한 뒤 다음을 실행한다.

```bash
export CARGO_TARGET_DIR=/tmp/rei_atomic_catalog_target
bash RUN_ATOMIC.sh
```

`generate_catalog.py`는 고정 SHA와 원 ASCII/Fortran identity를 확인하고 generated Rust를 재생성한다. `RUN_ATOMIC.sh`는 해당 generated 파일에 scoped rustfmt를 적용한 뒤 full crate tests, strict Clippy, release experiment와 독립 Decimal 검산을 실제 수행한다. 재현에는 Python stdlib와 Rust std만 필요하다. `data/PROVENANCE.json`, `SOURCE_CONTRACT.json`, `NOTICE.md`를 함께 보존한다. 외부 원데이터에 새 소프트웨어 라이선스를 임의로 붙이지 않았다.
