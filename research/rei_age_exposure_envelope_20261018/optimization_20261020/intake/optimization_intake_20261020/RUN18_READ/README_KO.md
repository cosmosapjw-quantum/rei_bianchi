# RUN18 — VigilODE 구간 산술을 적용한 정확 연속 재구성과 잔여 오차 분리

**결과:** RUN17의 저장된 첫 birth 구간을 다시 적분하지 않고, 그 23개 DOP853 다항식의 경계값을 정확 유리수로 조사했다. 기체 5성분은 이미 정확히 연속이었다. 광학 깊이 252성분에서는 세 시간 경계에 걸쳐 431개 좌표 불일치가 있었고, 최대 크기는 정확히 $2^{-55}$였다. 누적 부호를 반영한 상수 보정으로 전체 기체·깊이 재구성을 연속으로 만들었으며, 모든 깊이의 비음수성을 유지했다. 이 **재구성 보정만**이 고정된 양의 survivor 관측량에 주는 상대 변화의 상한은

$$
\beta=\frac{9}{288230376151711735}
\simeq3.122502256758253\times10^{-17}
$$

이다. 원래 native IVP나 spectral continuum 해의 오차 상한을 뜻하지 않는다.

이 계산에는 실제 VigilODE `directed.rs` 원문과 Rust `num-rational`·`num-bigint`를 사용했다. 정확 유리수 Python 기준 구현과 Rust 결과가 5,911개 종단 값·접합 및 도함수 관계에서 일치했다. VigilODE 구간 산술은 5,911개 오른쪽 종단 값과 5,911개 오른쪽 종단 도함수의 정확한 유리수 값을 포함했다. 실제 Rust 테스트는 4개 통과했다. 생산자 실행 로그와 source/binary identity를 그대로 보존했으며, 중단 후 재개에서는 이 계산이나 빌드를 반복하지 않았다.

## 1. SSOT와 적용 범위

RUN17 science 기준은 [`589ffbaff7b74a6cf1dbaf797285f15a58131dbd`](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/589ffbaff7b74a6cf1dbaf797285f15a58131dbd), RUN18의 직접 부모는 RUN17 전달 증거를 추가한 [`0e23addf4fefa69287d4626622bf97505677ea43`](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/0e23addf4fefa69287d4626622bf97505677ea43)다. 전자는 과학 source, 후자는 실제 Git ancestry다. `SOURCE_IDENTITY.json`이 두 역할과 각 입력 해시를 분리한다.

대상은 RUN17 B의 첫 birth 직후부터 두 번째 birth 직전까지인

$$
z\in[0.004989333151072248,\ 0.02371416180174271],
\qquad z=\frac{X-0.7}{0.0004}.
$$

여기서 $z$는 계산용 정규화 좌표이며 우주론적 적색편이가 아니다. 원래 설정은 $X=\ln(a/a_{\rm ref})$, $a_{\rm ref}=1/21$, $X\in[0.7,0.7004]$, prescribed BASS121 `SIGNED_MINUS`, birth 160개, GL8, 48 spectral cells다. 504개 물리 ray row의 정확한 반사 대칭으로 얻은 252개 cohort 깊이와 5개 invariant 기체 좌표를 사용한다. 원래 265개 상태 중 수동 ledger 8성분은 이 연속성 감사 대상에서 제외했다. 기존 ledger를 수정하거나 새로운 결합 이력의 ledger로 선언하지 않았다.

Native atomic 공급자, 제조된 10,000 K 초기 상태, prescribed geometry, HHeD 기체 모델을 바꾸지 않았다. $E_{\rm H,binding}=13.598434599702\,\mathrm{eV}$와 $E_{\rm H,fit}=13.6\,\mathrm{eV}$를 구별하며, D 제조 시험은 $13.602134599702\,\mathrm{eV}$와 threshold-gated H-equality approximation을 유지한다. D의 isotope-specific 실험 단면적을 새로 도입한 작업이 아니다. Metric convention은 $(- ,+,+,+)$, 기존 물리 유도에서 $c,\hbar,k_B$를 명시하는 계약을 유지한다.

핵심 입력은 RUN17 `native/control_B_execution01/ACCEPTED_AND_DENSE_STATE.npz`다. 380,629 bytes, SHA-256 `ddc62155d70a9a9b2f7ae3ab2caf827cbb8bab6bebc1aeae6ce229b4b4ebddf4`인 원본을 읽었다. 이 NPZ를 손대지 않고 이식 가능한 binary64 hex fixture를 새로 만들었다. 모든 과학 결론은 저장된 유한 binary64 값을 **정확한 실수 계수**로 해석한 다항식에 대한 결론이다. 실행 중 임의의 반올림 평가나 정확한 물리 해의 연속성 인증으로 확대하지 않는다.

## 2. VigilODE에서 실제로 활용한 코드

[VigilODE](https://github.com/cosmosapjw-quantum/vigilode)의 초기 조사 source는 `ac1cd2a4738c2441c92e5fdae5f70aba35e53544`였다. 그중 [`crates/rodas5p-core/src/directed.rs`](https://github.com/cosmosapjw-quantum/vigilode/blob/ac1cd2a4738c2441c92e5fdae5f70aba35e53544/crates/rodas5p-core/src/directed.rs)의 **17,215 bytes를 변경 없이** 새 crate에 포함했다.

- 원문 SHA-256: `2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814`
- Git blob: `89e2b3122b08db1849e4e56cc94f1f58c473b735`
- 보존 위치: `runtime/exact_dense_adapter/provenance/vigilode_directed.rs`
- 원본 MIT LICENSE도 같은 provenance 디렉터리에 보존했다.

새 crate는 원본 모듈이 참조하는 `CoreError::{InvalidInput, NonFinite}`와 `CoreResult` alias만 제공한다. 실제 사용한 API는 `Interval::point`, `new`, `add`, `sub`, `mul`, `div`다. 저장된 DOP853 degree-7 nested recurrence와 그 해석적 도함수를 새 어댑터에 구현하고, 같은 식을 정확 유리수와 outward interval 양쪽에서 평가했다. 구간 끝점도 정확한 dyadic rational로 변환해 포함 여부를 비교하므로, 반올림된 정답이 구간에 들어가는지만 검사한 것이 아니다.

2026-10-19 **17:37:56 UTC**에 원격 상태를 다시 읽었다. source branch HEAD는 `b56bb19ce85bc28a021138ee29689701a81bc4f0`, PR71 HEAD는 `64b9852124b67eedbb8575b42c01127e4b86283b`, PR72 HEAD는 `57840c749ca51642bf828ce43f5d6273d21ea05f`로 진행되어 있었다. 세 새 SHA에서 실제로 읽은 `directed.rs`는 빌드에 사용한 원문과 byte-for-byte 동일했다. 이 확인은 해당 재사용 파일에 한정된다. 새 operator/CLI 변경 및 벤치마크 전부를 검증한 것으로 표시하지 않는다. 상세 기록은 `inventory/recovery_20261019T173756Z/RECOVERY_REFRESH_RECEIPT.json`이다.

VigilODE의 다른 유용한 API도 읽었다. `ContinuousResidualProvider`는 시간·상태 상자 전체의 RHS 포함과 admissible tube 전체의 **Euclidean logarithmic norm** 상한을 요구한다. 현재 native f64 서버의 점별 RHS/Jacobian은 그 계약을 충족하지 않는다. 내부 `Rodas5pQuarticSegment`는 RODAS5P 8-stage 결과로 구성되는 4차 객체이므로 DOP853 7차 계수를 그대로 넣을 수 없다. 전체 VigilODE workspace, RODAS5P 적분기, private quartic tube verifier, `exp_interval`, logarithmic-norm helper를 이번 실행에서 사용했다고 주장하지 않는다.

향후에는 실제 interval 기체 Jacobian을 얻은 뒤 `nonnormal_certificate::symmetric_part_upper`의 Gershgorin/interval-Cholesky 경로를 작은 기체 block에 적용할 수 있다. 먼저 동일한 물리 owner와 norm/scaling 계약을 충족해야 한다. 조사 결과와 코드별 재사용 지위는 `inventory/VIGILODE_REUSE_KO.md`에 있다.

## 3. 현재 작업에 맞춘 Rust 패키지

| 패키지 또는 원문 | 실제 적용 지위 | 이번 작업에서의 역할 |
|---|---|---|
| `num-rational 0.4.2` | 빌드·테스트·실행 | `BigRational`, 정확한 binary64 변환, 값·도함수·접합·상한 |
| `num-bigint 0.4.6` | 빌드·실행 | 분자·분모와 dyadic 계수의 임의 정밀도 정수 |
| `num-integer 0.1.46`, `num-traits 0.2.19`, `autocfg 1.5.0` | 실제 dependency 빌드 | 정수/수치 trait 및 빌드 지원; Cargo.lock 고정 |
| VigilODE `directed.rs` | 원문 그대로 실제 실행 | 독립적인 outward interval 포함 검사 |
| `inari 2.0.0` | 공식 archive 다운로드·해시 대조·정적 조사 | 향후 독립 interval backend 후보; 빌드하지 않음 |
| `rug 1.30.0` | 공식 문서 조사 | 향후 MPFR rounding/transcendental 후보; 다운로드·빌드하지 않음 |

적용한 다섯 Rust dependency의 공식 배포 archive 합계는 **223,651 bytes**다. 실제 다운로드 SHA-256을 공식 metadata 및 Cargo.lock checksum과 대조했다. 공식 archive와 그 안의 LICENSE를 보존하고, 오프라인 vendor 복원 helper를 제공한다. `inari`는 추가로 140,941 bytes를 받아 읽었으나 사용한 dependency graph에는 포함되지 않는다. GMP 기본 feature와 x86 AVX+FMA/AVX512F 요구를 확인한 상태이며 실제 새 feature 조합을 시험한 결과는 없다. 정확한 dyadic 다항식에 대해서는 pure Rust 유리수 경로가 작은 의존성으로 충분했다.

공식 API: [num-rational](https://docs.rs/num-rational/0.4.2/num_rational/), [num-bigint](https://docs.rs/num-bigint/0.4.6/num_bigint/), [inari](https://docs.rs/inari/2.0.0/inari/), [rug](https://docs.rs/rug/1.30.0/rug/). 다운로드·source 검사와 적용 여부는 `runtime/RUST_PACKAGE_ASSESSMENT_KO.md` 및 `runtime/CRATE_DOWNLOAD_RECEIPT.json`을 따른다.

## 4. 정확한 경계 불일치와 연속성 복원

첫 piece를 0으로 번호 매기고, 경계에서

$$
J_i=\tau_{i+1}(t_{i+1}^{+})-\tau_i(t_{i+1}^{-}),
\quad c_0=0,\quad c_{i+1}=c_i+J_i,
\quad\widetilde\tau_i=\tau_i-c_i
$$

로 정의한다. 그러면 $J_i-(c_{i+1}-c_i)=0$이므로 보정된 좌우 값이 정확히 일치한다. 각 열린 piece에서 도함수는 변하지 않는다. 유한 개의 연속 piecewise polynomial은 절대연속이므로, 이 새로운 기체·깊이 재구성에는 일반적인 적분 residual 공식을 적용할 수 있다. 기체 좌표는 원래 jump가 0이어서 그대로 남는다.

| 정확 유리수로 확인한 양 | 결과 |
|---|---:|
| 실제 저장 시계로 계산한 오른쪽 정규화 좌표가 정확히 1 | 23 / 23 |
| 내부 기체 좌표의 값 불일치 | 0 / 110 |
| 내부 깊이 좌표의 값 불일치 | 431 / 5,544 |
| 불일치가 존재하는 시간 경계 | 3개, piece 1·2·3 뒤 |
| 최대 개별 깊이 jump | $1/36028797018963968=2^{-55}$ |
| 경계별 depth 무한대 norm의 합 | $13/288230376151711744$ |
| 누적 signed offset의 최대값 $\Gamma$ | $9/288230376151711744$ |
| 보정 후 모든 기체·깊이 접합의 정확한 연속성 | 22 / 22 |
| 보정 깊이의 정확한 Bernstein 하한 비음수 | 23 / 23 |
| 원래 마지막 다항식과 저장된 마지막 상태의 불일치 | 0 |

431은 세 경계에서 불일치한 **좌표 항목 수**다. 물리적 threshold event 수나 독립 계산 수가 아니다. 최종 local endpoint mismatch가 0이어도 이전 jump의 누적 보정 $c_T$는 일반적으로 0이 아니다. 보정된 최종 깊이가 원래 최종 깊이와 같다고 주장하지 않는다.

비음수성은 정확한 Bernstein 계수로 확인했다. 기존 piece 공통 하한을 $L_i$라 하면

$$
\widetilde\tau_{i,k}(t)\ge L_i-\|c_i\|_\infty\ge0
$$

가 23개 piece 모두에서 성립했다. 기존 gas lift, nuclei 합과 EOS 영역 증거는 기체 다항식이 같으므로 유지된다. 원본 배열과 RUN17 certificate는 수정하지 않았다.

독립 Python 기준은 명시적 power basis와 `Fraction`을 사용하고, Rust는 nested recurrence 및 별도의 Bernstein 변환을 사용한다. 모든 계수, 좌우 도함수, offset, 하한과 원시 입력/출력을 `theory/execution01` 및 `runtime/adapter_execution01`에 보존했다.

## 5. 보정 자체의 응답 상한과 그 경계

같은 기체·geometry·source에서 $p_k=B_ke^{-\tau_k}$, $B_k\ge0$라 하자. 보정 후에는 $\widetilde p_k=p_ke^{c_{i,k}}$다. $0\le\Gamma<1$이고 $|c_{i,k}|\le\Gamma$이면 지수함수 급수로

$$
|e^{c_{i,k}}-1|\le e^\Gamma-1
\le\frac{\Gamma}{1-\Gamma}=\beta
$$

를 얻는다. 여기의 마지막 값은 유리수 나눗셈으로 정확히 계산했으며 부동소수점 지수함수를 엄밀성 근거로 사용하지 않았다. $\Gamma$와 $\beta$는 표시용 binary64에서 같은 소수로 반올림되지만, 분모가 다른 정확한 유리수다.

고정된 비음수 가중치 $w_k(t)$에 대해

$$
Q(t)=\sum_k w_k(t)p_k(t)\ge0,
\qquad |\widetilde Q(t)-Q(t)|\le\beta Q(t)
$$

이다. $Q>0$일 때만 이를 상대 오차 형태로 나눈다. geometry가 정한 threshold membership은 보정에 의해 바뀌지 않으므로 고정 survivor subset에도 적용할 수 있다. 개별 양의 흡수·가열 channel과 그 양의 시간 적분에도 같은 주장이 성립한다.

그러나 상쇄가 있는 기체 net rate에는 상대 $\beta$를 곧바로 적용하면 안 된다. $\Phi_q=\sum_a v_aR_a$, $R_a\ge0$일 때 적절한 성분별 식은

$$
|\widetilde\Phi_q-\Phi_q|\le\beta\sum_a|v_a|R_a.
$$

특히 HeII net rate를 분모로 나누는 방법은 일반적으로 성립하지 않는다. $r=\widehat y'-F(\widehat y)$ 관례에서 기체 residual은

$$
\widetilde r_q=r_q+\Phi(q,\tau)-\Phi(q,\widetilde\tau),
\qquad\widetilde r_\tau=r_\tau
$$

로 바뀐다. 이것이 보정 비용을 이후 결합 오차 비교에 넣어야 하는 위치다. 물리적인 opacity feedback 해가 $10^{-17}$ 정확하다는 결과는 아니다.

보정을 사용하지 않는 경우에도 부호와 항을 명시했다. 재구성의 상태 jump는 distributional residual의 $J_i\delta_{t_i}$ 항이며, 연속인 참해에 대한 $e=y-\widehat y$는 $e^+=e^--J_i$를 따른다. 도함수 좌우 값의 불일치만으로는 1차 상태 residual에 Dirac 항이 추가되지 않는다. 두 경로의 차 $P-R$에는 $J_P-J_R$가 들어간다. 비음수 비교 기본행렬 $\Phi_M$를 쓰면 jump norm의 기여는 $\sum_i\Phi_M(t,t_i)\gamma_i$다. 이 식의 적용에는 여전히 전체 tube에서 성립하는 비교 계수와 연속 residual 상한이 필요하다.

## 6. 실제 실행과 과거 결과의 구분

| RUN18에서 실제 완료한 실행 | 기록 |
|---|---|
| Python 정확 유리수 reference | 내부 1.7876 s, native RHS·IVP 0 |
| Rust `cargo test --offline --locked --lib` | **4 PASS, 0 FAIL**; 신규 3개 + 변경 없이 포함한 VigilODE 1개 |
| Rust release build | 실제 성공, 약 4.6666 s |
| 정확 종단/도함수 CLI | 5,911 cases, 약 1.6731 s |
| 정확 $\beta$ CLI | 1회, 약 0.0016 s |
| 독립 reference와 interval 포함 검증 driver | 약 1.8764 s, 모든 대상 일치 |
| 공식 crate archive로 새 vendor 복원 | 130 source files + 5 checksum maps 일치; 재빌드 없음 |
| 이 실행의 native gas RHS / IVP / quadrature / 과거 m2 재실행 | **0 / 0 / 0 / 0** |

실행환경은 Linux x86-64, Rust/Cargo 1.94.1, Python 3.12.14다. 기존 retained Rust prefix를 사용했다. 재첨부된 Rust installer는 현재 제공되어 있지만 이 완료된 빌드에 사용한 것으로 소급 표시하지 않는다. 실행 binary는 691,152 bytes, SHA-256 `e523de3ada7784e5f0b0cbd2e5304461f6f15ac291fdd1047e7cc4f120323600`이다.

중단 후 다시 읽은 runtime 53개 payload와 theory 8개 payload는 보존된 manifest와 일치했다. 해당 읽기·해시 대조는 새 PASS 계산이나 재컴파일이 아니다. 독립 검토는 한 차례 수행했으며, 검토 범위 안에서 구체적 결함을 찾지 못했다는 지위다. 일반적인 모든 입력의 interval backend 증명이나 전체 native solver의 검증 완료로 확대하지 않는다.

RUN17에는 별도의 새 native 첫-birth A/B 적분 2회와 총 native RHS 1,378회가 실제 기록되어 있다. RUN18 수치에 그 호출 수를 중복 합산하지 않는다. RUN17에서 기존 tight 경로를 invariant 좌표로 재구성한 $P$와 native B $R$의 endpoint 온도 차는 $+0.12465231681380828\,\mathrm K$, 첫-birth survivor 상대차는 $+3.095494720825061\times10^{-6}$였다. 이는 RUN13 전체 이력의 sub-H survivor와 다른 observable이다.

RUN13 m2 standard/tight 완료 이력, 6,241 segments, 40,357 states는 계속 보존한다. 당시 전체 survivor의 M2 tolerance 차이 약 $-1.4510\times10^{-15}$, tight M2–M1 차이 약 $8.4023\times10^{-6}$, 작은 sub-H 성분의 M1/M2 상대 차 약 51.99%는 과거 source의 결과다. RUN18의 $\beta$는 그 51.99%를 해결하거나 재평가한 값이 아니다. 세 실험의 대상과 오차 원인이 다르다.

## 7. 검증 지위와 남은 과학 노드

| 지위 | 이번에 적용하는 주장 |
|---|---|
| `ESTABLISHED` | 저장 계수로 정의한 이상적 실수 다항식의 정확 접합·C0 보정·깊이 비음수성과 보정 응답 부등식 |
| `DERIVED` | 상태 jump를 포함한 residual measure, 조건부 block comparison, signed photo channel allowance, Euclidean norm 연결식 |
| `IMPLEMENTATION_VERIFIED` | 명시한 입력의 실제 Rust/Python 일치·4 tests·구간 포함 및 source byte identity |
| `NUMERICALLY_CHECKED` | 제한된 입력의 실제 실행 시간과 RUN17 finite tolerance/path contrasts |
| `LITERATURE_SUPPORTED` | 연속 재구성 기반 a posteriori 분석의 원리; 기존 논문의 수렴차수를 새 결합 문제에 이전하지 않음 |
| `ARCHIVED_EVIDENCE_ONLY` | 재실행하지 않은 과거 RUN13 endpoint와 그 당시 테스트 기록 |
| `UNRESOLVED` | 정확한 native 결합 IVP tube, 전체 시간 residual 상한, spectral continuum/subthreshold bound |

기존 **P4-S4C-SPECTRAL-EDGE-SUPPORT / SUBTHRESHOLD-SURVIVOR-RESOLUTION**의 미완료 부분을 그대로 유지한다. 이번에는 RUN17이 요구한 "연속 재구성 증명 또는 representation jump 처리"를 새 C0 객체에 대해 구체화했다. 다음은 원래 rate branch·temperature·threshold 조건을 유지하는 **continuous interval RHS extension**이다. 이후 동일한 invariant lift와 scaling에서 interval Jacobian, gas↔depth coupling, tube 전체의 logarithmic norm, polynomial derivative−RHS의 전체 시간 포함을 계산해야 한다. prefix의 exact-IVP 초기 오차, 이후 physical event, spectral source forcing도 필요하다.

VigilODE의 Euclidean $\mu_2$에 RUN17에서 몇 점에 한해 측정한 $\mu_\infty$를 대입하지 않는다. $J=\left(\begin{smallmatrix}A&B\\C&0\end{smallmatrix}\right)$, tube 전체에서 $a_2\ge\lambda_{\max}(\operatorname{sym}A)$, $d\ge\|B+C^T\|_2/2$라면 $\mu_2(J)\le(a_2+\sqrt{a_2^2+4d^2})/2$라는 연결식은 유도했지만 아직 실제 tube 계수를 계산한 결과는 없다.

원래 45-node/26-node DAG의 identity와 미완료 의무는 `DAG_CONTINUATION.json`에서 계승한다. Continuous spectral refinement, uniform native m4, angular convergence, birth-time continuum, whole donor domain, full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, Li/Be 및 nuclear T1–T8는 완료로 바꾸지 않았다.

문헌 조사는 SciSpace와 Exa, 부등식/조건 검토는 Wolfram을 실제 사용한 영수증을 `theory/`에 보존했다. 연속 재구성의 배경 문헌은 Makridakis–Nochetto, *A posteriori error analysis for higher order dissipative methods for evolution problems*, Numerische Mathematik 104 (2006), DOI [10.1007/s00211-006-0013-6](https://doi.org/10.1007/s00211-006-0013-6)다. 2004 저자 preprint의 Lemmas 2.1–2.2를 조사했으며, 여기의 coupled photo-chemistry에 해당 논문의 order/error theorem이 자동 적용된다고 하지 않는다. 정확한 새 증명은 `theory/EXACT_CONTINUOUS_DEPTH_REPAIR.md`에 있다.

## 8. 재현·전달·실패 기록

정확한 생산자 명령과 portability 경계는 `REPRODUCE_KO.md`, `runtime/REPRODUCE.md`, `theory/EXECUTION_RECEIPT.json`, `runtime/build_execution01/BUILD_RECEIPT.json`에 있다. 새 output 디렉터리와 명시한 Rust prefix를 쓰면 공식 archive로 의존성을 오프라인 복원할 수 있다. 원본 NPZ를 다시 읽을 필요 없이 portable hex fixture와 reference로 Rust adapter만 검증하는 경로도 제공한다. 새 환경의 binary byte가 같다는 일반적 약속은 하지 않으며, 정확 유리수 결과와 명시한 inclusion checks가 재현 기준이다.

최초 Python probe의 parse 오타, 기본 sandbox crates.io 접근의 `Operation not permitted`, 후속 허용된 read-only 다운로드 성공, release의 unused import 경고를 그대로 보존했다. 별도 tool launch에서 발생한 `bubblewrap ... No space left on device`는 Rust 계산 실패가 아니다. 실패를 지우기 위한 반복 실행이나 원본 삭제를 하지 않았다. 현재 source와 결과가 읽히고 새 Git/ZIP 전달 검증이 성공했는지는 별도의 delivery 영수증으로 판정한다.

`SCIENCE_MANIFEST.json`은 자신을 제외한 전체 RUN18 파일의 SHA-256·Git blob·mode를 고정한다. ZIP은 실제 science commit/tree/parent와 대조한 뒤 만들며 원본 source, 결과, 실행 binary와 소형 공식 crate archive를 포함한다. RUN17 archive는 identity로 연결한다. 과학 ZIP 안에 그 ZIP 자신의 SHA를 넣지 않는다. 실제 업로드, 원격 존재, 전체 다운로드 byte 일치, 새 계산 재현은 별도 지위다. 게시·이중 백업 완료 후의 최신 정보는 추가 파일 `DELIVERY.json`, `RESUME_DELIVERY_KO.md`가 제공한다.
