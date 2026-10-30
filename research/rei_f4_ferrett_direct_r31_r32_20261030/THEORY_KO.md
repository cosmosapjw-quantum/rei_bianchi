# Ferrett 1987 원문에서 직접 측정된 R31·n3/n2만으로 구성한 Li I K-shell 분기와 광전자 운동학

## 1. 원전·SSOT·유효범위

- 사용자 제공 원고: Ferrett, Lindle, Heimann, Brewer, Becker, Kerkhoff & Shirley, *Lithium 1s Main-line and Satellite Photoemission: Resonant and Nonresonant Behavior*, LBL-22068, March 1987. 최종 논문 *Physical Review A* **36**, 3172–3183 (1987), DOI 10.1103/PhysRevA.36.3172.
- 업로드 PDF 정확한 SHA-256: `7fbabb1fe8c77a2fb561c7900e198f40f4c16125dd12ac3d08505b997a93b6a9`. PDF 전체 60쪽. 논문 인쇄 -28- / PDF 34쪽 Table I, 인쇄 -29- / PDF 35쪽 Table II, 인쇄 -30- / PDF 36쪽 Table III, 인쇄 -31- / PDF 37쪽 Table IV를 직접 영상 대조했다.
- BASS source owner commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`; 원본 관측/동역학 입력은 선행 PR289 원본 포함 ZIP SHA-256 `f5fa78b9087a60051bb7161d69ada6019f42cfa093674a2fc07c7ed9cc7cdd4f`에 byte-frozen. 동일 원래 193 저장 epoch, Li6I·Li7I, 원본 71-bin photon 이력 중 원문에서 직접 측정 R31의 공통 지원구간 80–92.5 eV에 속하는 세 bin 81.85233848280362, 86.70882056440522, 91.85344857617926 eV만 사용한다. 각 `193×2×3=1158` 원본 photon-bin 사건율 행을 재가중한다.
- 사용한 clock은 원본 BASS 저장된 `x=ln[21/(1+z)]`, `H(x)>0`; Simpson 구적은 저장 이력의 후처리. **추가 IVP=0, 새로운 광자장·중성기체·온도 이력 없음.**

## 2. 직접 측정량과 PR289 자료 해석의 교정

PDF p.35 Table II는 실험비

\[
R_{31}(E) \equiv {\sigma[1s2s\,^3S]\over\sigma[1s2s\,^1S]+\sigma[1s2p\,^1P]+\sigma[1s2p\,^3P]}
\]

을 75–92.5 eV에 기록한다. PDF p.36 Table III는 `R32(E)=σ(n=3)/σ(n=2)`를 80–99 eV에 기록한다. 이 두 비는 **80–92.5 eV**의 겹치는 계측 지원구간에서 실험적 표본값이다. 반면 p.35 각주 a,c에 따르면 80 eV 이상 `Rc=σ3S/(σ1S+σ3P)`는 실측 `R31`에 추정된 `Rp=σ1P/σ3S`를 결합해 얻었고, 93–99 eV는 평균 `R31` 가정까지 사용한다. 또한 p.37 Table IV의 `σ3S`, `σ(1S+3P)`는 여러 분기비와 외부 total σ를 결합해 **유도한 값**이다. 그러므로 PR289의 모델 보조된 Table IV 정규화를 `직접 측정한 σ3S의 고유 비율`로 해석하면 과잉 주장이다.

**가정:** 관심 있는 `n=2+n=3` core-photoionization 부분집합 안에서 분기를 정의하며, 기타 n≥4 위성이나 2s valence ionization 및 이중 광이온화는 전체 실제 분모에 포함되지 않는다. Ferrett III.B에서도 2s 가 약 1–2%, 높은 n이 무시된다고 지적한다. BASS native K 사건에 아래 분기를 곱하는 것은 **두 단면적 모형 사이의 조건부 projection**이며 source-common 절대 예측이 아니다.

`σ(n2)=σ3S+σ1S+σ1P+σ3P`, `σ(n3)=R32 σ(n2)`이므로:

\[
f_{3S}(E)={R_{31}(E)\over[1+R_{31}(E)][1+R_{32}(E)]},\quad
f_{n2,rest}(E)={1\over[1+R_{31}(E)][1+R_{32}(E)]},\quad
f_{n3}(E)={R_{32}(E)\over1+R_{32}(E)}.
\]

세 분기 합은 정확히 1. **미분리 순수 singlet**은 `0≤f[1s2s ^1S]≤f[n2,rest]`이며 양의 하한을 부여할 수 없다. 두 물리적 배정 (모든 나머지 강도를 ^1S에 배정, 또는 전부 ^3P에 배정) 모두 같은 R31과 R32를 재현한다. 이 비식별성은 데이터의 해상도에서 나오는 것이지 계산 실패가 아니다.

## 3. 실험오차 구간의 의미

Table II/III의 괄호 표기는 마지막 자리 실험 통계오차다. 각 측정 에너지에서 `R31=r±dr`, `R32=t±dt`를 갖는다고 놓고, 인접 측정 절점 사이의 중앙비와 `dr,dt`를 **직선보간**한다. 보간 자체에 대한 이론오차, 2비의 joint covariance, 측정 시스템 간 교차 공분산은 제시되지 않는다. 그래서 다음 수치는 **점별 기입 통계오차의 직사각형 구간 영상**, 확률적 confidence band나 통계적으로 완전한 posterior가 아니다.

\[
\partial_r f_{3S}={1\over(1+r)^2(1+t)}>0,\qquad
\partial_t f_{3S}=-{r\over(1+r)(1+t)^2}<0,
\]

\[
f_{3S}^{-}={r-dr\over(1+r-dr)(1+t+dt)},\quad
f_{3S}^{+}={r+dr\over(1+r+dr)(1+t-dt)}.
\]

`f[n2,rest]`와 `f[n3]`에도 같은 단조성으로 구간을 만든다. 각 bin의 비율오차를 독립 표본으로 취급해 곱한 적은 없으며, 여러 epoch에서 공통 표의 비율이 그대로 쓰인다. 보고된 전체 적분 구간은 각 에너지별 직사각형 안의 보존적인 범위다. 선형보간의 미지 오차를 포함하는 강한 보증은 아니다.

## 4. 물리적 광전자·잔류 이온 에너지

사용자 PDF p.34 Table I에 인쇄된 historical binding energies를 원본의 숫자로 사용한다: Li I `1s2s ^3S = 64.41 eV`, `1s2s ^1S=66.15`, `1s2p ^3P=66.67`, `1s2p ^1P=67.61`, `n3` 네 채널 `74.17..75.04 eV`. 선행 NIST 계산의 `1S` 에너지와 약 0.16 eV 차이를 **혼합 보정하지 않았다**. 원전별 에너지 identity는 분리해야 한다.

단일 흡수 사건의 출사 1차 광전자 에너지는 `K=E_photon−χ_residual`이고, 1987 잔류 상태 자료와 분기 불확실성만 적용하면

\[
K_{\rm eff}(E;r,t,\chi_{rest},\chi_{n3}) = E-f_{3S}\,(64.41\,{\rm eV})-f_{n2,rest}\,\chi_{rest}-f_{n3}\,\chi_{n3},
\]

`66.15≤χ_rest≤67.61`, `74.17≤χ_n3≤75.04` eV. `r=r0±dr, t=t0±dt`의 네 극점과 두 state-energy endpoints를 계산해 진짜 **허용 모델 내 최소·최대 에너지**를 보존한다. 모든 경우 `K+Σ fχ=E` (eV 차원 검사). `K`는 생산된 photoelectron의 **초기 운동에너지**이지 실제 deposited gas heat가 아니다.

조건부 진공 M1 방출에서는 원본 Ferrett ^3S 분기 사건에 독립 원자 준위 `E_M1=59.02072367315768 eV`를 곱해 광자 공급 가능 에너지를 얻는다. 2E1 ^1S는 `0..f_n2,rest` 이므로 **상한만** 독립 NIST `E_2E1=60.922559447552 eV`로 곱한다. 이 광자는 1s 광이온화 이후의 *secondary vacuum photons*이고 실제 운반/흡수/열침적은 계산하지 않았다.

## 5. 계산 매핑·단위·검증

원본 K photo rate `Γ_K(x,E)` 단위 `events baryon⁻¹ s⁻¹`. 새 source-scope rate `Γ_{3S}=f_{3S}(E) Γ_K`. 저장된 `x=ln(a/a_i)`이므로 `dt=dx/H`; 원본 193 노드에서

\[
{N_{3S}\over N_b}=\int_{x_i}^{x_f}{\Gamma_{3S}(x)\over H(x)}dx \simeq \sum_{k=0}^{192} {w_k\Gamma_{3S}(x_k)\over H_k}.
\]

양의 source epoch values, 3-bin 지원구간, 2 isotopes, 193 epochs, 1158 unique keys를 검사한다. Wolfram exact `f3+frest+fn3−1=0`, analytical derivative check PASS. Python 21 targeted tests include source SHA corruption controls, energy ledger, branch closure, no 97.3-eV extrapolation and missing singlet identification counterexample. All tests are 본 작성자 동일 환경 검사이며 `R6/C9 distinct-author NOT_RUN`.

Original canonical DAG: Working **33/88**, Central **28/88**, F4-fast **4/7**; new scientific auxiliary scoped **1/1**, canonical physical delta **0**. `F4 PARTIAL`, `L4_ready=false`, `THERMAL_PORT=UNBOUND`, `PRODUCTION=HOLD`, `NO_MORE_IVPS`, `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false`.
