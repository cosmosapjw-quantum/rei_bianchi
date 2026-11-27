# APERTURE07 후속 scientific intake와 KINEMATIC08 유도 초안

작성: 2026-10-28 KST. 역할: 기존 원자료·코드 읽기, 후보 비교, 직접 유도 및 root 설계 검토.
새 science/test/plot 실행·기존 archive 재생성·repo 수정·게시·백업은 수행하지 않았다.
아래 해석식의 근거 상태는 **derived**이며 신규 구현·실행의 근거는 root의 별도 결과에 연결한다.

## 1. 실제 읽은 근거와 재사용 경계

기준 저장소는 `/workspace/scratch/1ab916cbe4d9/BASS_HE`다. 다음 본문을 읽었다.

- `AGENTS.md`: 원 논문의 독립 구현, 동일 입력의 기존 suite replay 금지, immutable execution identity와 publication identity 구분, source PDF 공개 재배포 금지.
- `research/program_expansion_20261025/continuation_aperture_20261027/THEORY_KO.md`, `MODEL_CONTRACT.json`, `NUMERICAL_DESIGN_KO.md`, `IMPLEMENTATION_NOTES.md`, `src/aperture.py` 전체.
- `continuation_angular_20261027/THEORY_KO.md`, `review/INDEPENDENT_DERIVATION_KO.md`의 source 조사와 운동학 유도 부분, `sources/SOURCE_MANIFEST.json`.
- `continuation_photon_20261027/THEORY_KO.md`, `sources/PHOTON05_SOURCE_OBSERVATIONS.json`.
- `continuation_20261027/sources/r3_update/raw/PROVIDER_ROWS.json`의 M0475002/M0475003 원문 BIB·locator.
- `continuation_aperture_20261027/sources/PRIMARY_RICE_READ_KO.md`.

APERTURE07의 결정은 `ACCEPT_SCOPED_CONDITIONAL_APERTURE_REFERENCE`다. 그 단위는 저장된 유리수 γ,a에 대한 극각창 역상과 비음수 degree≤8 Bernstein event measure의 경계다. 실제 질량·광자 에너지에서 γ,a로 가는 수치 변환은 해당 certificate 밖이다. 이번 후보1은 이 명확한 계산 연결을 닫는다.

기존 검증 source Local S05 `3e41e230ff028fe28eb8aa35d9d6fecb1b22fd1f`와 remote same-tree S05 `1e6d82845e922e0d733be3d2f80e9bd2efc41e04`, 채택 Local S09 `39dd3b52ad87cfa2298c1f6897bf7d34991d1224`와 remote P09 `2f53703f621791a004c3ad13fa7e012536ab2cf6`는 기존 인계의 신원이다. 새로운 유도 노트를 그 source 실행 결과로 기록하지 않는다.

## 2. M0475002의 실제 실험과 원자료 위치

원 실험은 J. Arends et al., *Experimental investigation of the 4He(γ,d)d reaction*, Physics Letters B 62 (1976), 411–412, DOI [10.1016/0370-2693(76)90671-7](https://doi.org/10.1016/0370-2693(76)90671-7)이다. 확인된 원자료 경로는 [IAEA-NDS/exfor_master의 고정 M0475.x4](https://github.com/IAEA-NDS/exfor_master/blob/939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4)다. 이번 intake에서는 새 web fetch 대신 위 pinned source packet에 보존된 raw BIB와 locator를 읽었다.

기존 source record의 원문 identity는 3349 bytes, SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, git blob `c49433293921dbb012d7f1b0387745732a598efa`다. 이것은 기존 기록의 재사용이며 이번 해시 재계산을 뜻하지 않는다.

M0475002는 Table 1의 `DA`이고 CM 46/61/73/87°와 incident 213/258/330 MeV의 12행이다. `DATA-CM`·`ERR-S`는 NB/SR이며 ERR-S는 통계오차다. M0475003은 Table 2의 별도 `SIG` entry다. Parent BIB는 Bonn synchrotron, reaction-particle-tagged bremsstrahlung의 kinematic photon-energy reconstruction, cylindrical liquid-He target, 두 deuteron의 coincidence/TOF scintillation spectrometer 측정을 기록한다.

본문 normalization을 포함한 Arends 원 논문은 선행 inquiry에서 확보되지 않았다. Hartmann 1976 동명 연구의 CERN bibliographic record는 https://cds.cern.ch/record/790537 이며 해당 thesis 본문 역시 선행 기록상 미확보다. Rice 1998 thesis의 [공식 TUNL 원문](https://nucldata.tunl.duke.edu/nucldata/Theses/PhD/Rice_1998.pdf)은 다른 실험의 유한 geometry와 event cross-section convention을 제공한다. 이미 읽은 원전 요약의 `σ_event=2πA0`를 Arends의 convention으로 자동 이식할 근거는 없다.

현재 직접적인 물리 입력 공백은 normalization/target-response, complete angular law와 encounter flux, named nonthermal/deposition/global binding 세 가지다. KINEMATIC08은 첫 항목 중 **bare stationary model 안의 exact kinematic adapter**를 개선한다. liquid-He response 자체가 supplied 되는 것은 아니다.

## 3. 후보 비교와 선택 근거

| 후보 | 실제 새로운 계산 연결 | 기존 입력으로 가능한 결과 | 별도 물리 입력 |
|---|---|---|---|
| 1. 물리 입력 exact angular predicate | A,M,e에서 γ,a의 roundoff 경로를 우회하여 방향 predicate와 aperture bound 직접 구성 | 같은 bare stationary channel의 exact supplied-mass/energy reference, 실제 213/258/330 MeV labels에 조건부 적용 | 물리적 error distribution/신뢰구간·실험 response는 별도 |
| 2. 유한 방위각 공동 사건 | `(μ,φ)→(F(μ),φ)`, 교환 `(−μ,φ+π)`와 2D detector response를 결합 | 선언된 2D nonnegative density와 rectangular patch에 대한 조건부 정확 적분 | 실제 φ law·원형 telescope geometry·efficiency |
| 3. 움직이는 표적 encounter kernel | `s=A²+2e(E_t−n·Q_t)`와 상대 flux로 target distribution 적분 | supplied target/photon distributions에 대한 Lorentz-consistent per-event source | liquid-He target momentum/전자 response, normalized DCS 및 실제 photon history |

후보1의 비교 연산은 원래 irrational γ,a를 정확한 이차근호 부호 판정으로 대체하므로 단순 API wrapper와 구별되는 실질적인 알고리즘이다. 기존 Bernstein 적분·집합 연산을 그대로 이용하면서 certificate의 입력 의미를 A,M,e로 올릴 수 있다. Root는 이 후보를 **KINEMATIC08** 한 과학 단위로 선택하였으며 physical uncertainty box는 후속으로 유지한다.

후보2는 실험 유한 geometry에 더 가깝지만 실제 detector shape와 φ density가 없는 상태에서는 역시 supplied geometry reference다. 후보3은 물리 사건률에 가장 직접적인 연결이나 실제 target distribution/flux가 없는 현재 한 단위에 넣으면 물리 모델 선택까지 확대된다.

## 4. KINEMATIC08 exact comparator 유도

### 4.1 정의와 domain

계량은 `(-,+,+,+)`, 에너지 단위 사운동량은 `q=(E,c p)`다. 입력 `A=mα c²`, `M=md c²`, `e=Eγ`는 같은 에너지 단위의 정확히 선언된 유리수다. 선행 endothermic scope를 유지하려면 `0<A<2M`, `e>0`으로 둔다. 양의 질량 전체에 식은 유효하지만 그 확장은 별도 명시해야 한다.

`s=A²+2Ae`, `H=s−4M²`, `G=A+e`, `R=H/s`, `r=√R`로 둔다. `H>0`인 open channel에서는 `0<R<1`. `H=0`은 threshold atomic measure이고 이번 연속 밀도 API 밖이며, `H<0`은 닫힌 channel이다.

CM momentum `κ=√H/2`, boost `γ=G/√s`이므로

\[
2q_z=e+G\mu r=:U,\qquad 4q_\perp^2=H(1-\mu^2)=:V^2,
\]

\[
F(\mu)=\frac{U}{\sqrt{U^2+V^2}}.
\]

따라서 필요한 irrational은 고정된 양의 유리수 R의 제곱근 하나다. γ,a의 binary64 roundoff나 decimal 근호 근사를 boundary oracle로 사용할 필요가 없다.

### 4.2 이차근호의 부호

유리수 p,q와 `R>0`에 대해 `sgn(p+q√R)`는 다음 exact predicate로 구한다.

1. `q=0`이면 `sgn(p)`, `p=0`이면 `sgn(q)`.
2. p와 q가 같은 부호이면 그 부호.
3. 반대 부호이면 `sgn(p) sgn(p²−q²R)`.

마지막 단계는 서로 반대인 두 항의 절댓값을 제곱하여 비교한다. equality도 정확히 보존한다. 이 연산의 입력과 출력은 모두 유리수·정수 부호다.

### 4.3 원래 방향 부호를 보존한 경계 비교

먼저 `sgn U = sgn(e+Gμ√R)`와 `sgn ν`를 비교한다. 서로 다르면 해당 부호 순서로 F−ν의 부호가 정해진다. 둘이 0이면 F=ν=0이다. 같은 0 아닌 부호일 때

\[
\operatorname{sgn}(F-\nu)=\operatorname{sgn}(U)\operatorname{sgn}\{(1-\nu^2)U^2-\nu^2V^2\}.
\]

대괄호는 `P+Q√R`이고

\[
P=(1-\nu^2)(e^2+G^2\mu^2R)-\nu^2H(1-\mu^2),
\quad Q=2eG\mu(1-\nu^2).
\]

이 부호 판정은 제곱한 방정식의 spurious roots를 허용하지 않는다. `U=V=0`이면 방향이 없으므로 먼저 별도 처리해야 한다. H>0에서 이는 μ=−1과 `e²=G²R`인 stopped endpoint다. 공개 compare는 이를 거절하고 경계 탐색 내부에서만 해당 case의 연속 보조극한 0을 쓸 수 있다.

차원 검사: U와 V는 에너지, P와 Q는 에너지², R·μ·ν는 무차원이다. 따라서 sign 결과는 에너지 단위 변환에 불변이다.

### 4.4 branch와 fold 분류

선행 `a=e/(G r)`이므로 양의 값끼리의 제곱 비교만으로

\[
a<1 \iff e^2<G^2R,\quad a=1 \iff e^2=G^2R,\quad a>1 \iff e^2>G^2R
\]

를 정확히 분류한다. Derivative의 부호는 `sgn(G r+eμ)`와 같다. fold가 존재하면

\[
\mu_c=-\frac{G r}{e}\in(-1,0).
\]

μc는 일반적으로 유리수가 아니다. 기존 APERTURE07의 exact rational fold `−1/a`를 그대로 사용하면 새로운 exact physical-input 주장을 만족하지 못한다.

## 5. Rational fold bracket와 적분 포함 경계

fold가 있을 때 `G√R+eμ`의 exact sign을 이용해 유리수 bracket `J=[c_L,c_U]`를 만들고 `|J|≤δ`까지 이분한다. 정확한 rational fold를 만나면 J의 폭을 0으로 둘 수 있다.

`[-1,c_L]`은 감소 branch이고 `[c_U,1]`은 증가 branch다. 이 두 구간에서 기존 방식의 exact monotone root bisection으로 lab window의 역상 inner/outer를 계산한다. J는 outer에만 포함하고 inner에서는 제외한다. 실제 fold strip에 일부 또는 전부가 창 밖이어도 이 처리는 포함성을 보존한다.

창 하나의 branch boundary는 최대4개이고 각 bracket 폭이 δ 이하이므로 총 uncertain CM 길이는

\[
|O\setminus I|\le4\delta+|J|\le5\delta.
\]

두 창과 두 daughter reflection을 조합한 boolean event의 uncertain set은 네 입력 집합의 uncertain set의 합집합 안에 있다. 따라서 coincidence/hit 분할에 안전한 공통 bound는 `20δ`다. 공유 fold strip의 중복을 세밀하게 제거하면 실제 폭은 더 작아질 수 있으며 현재 상수20은 안전한 간명한 bound다.

비음수 Bernstein 밀도 ρ, `B=max b_k`, `σ=2Σb_k/(n+1)`에서 `σ>0`이면

\[
\delta=\frac{\sigma}{20B\,2^{40}}
\implies U_Y-L_Y\le20B\delta=\sigma2^{-40}.
\]

`B/σ≤(n+1)/2≤9/2`이므로 `δ≥2^-40/90`. 길이≤2의 bracket에 필요한 bisection은 `ceil(log2(2/δ))≤48`회다. 기존 default error 목표와 degree8 경량 비용 구조를 유지한다. 이는 임의 길이의 rational input에 대한 wall-time 정리가 아니다.

zero-density case에서도 domain·geometry·입력 검사는 먼저 수행한다. 적분0을 반환할 때 기하학적 역상 자체가 공집합이라고 표시하지 않는다. 수동 δ 입력은 반환된 실제 width/width_bound로 평가한다.

## 6. 에너지와 moments의 추가 경계

같은 변수에서 daughter 에너지는

\[
E_\pm=G/2\pm(e/2)r\mu.
\]

pair energy `E_++E_−=G`는 정확한 유리수 상수다. 따라서 selected-event pair-energy 경계는 `G·[L_Y,U_Y]`로 직접 전달할 수 있다. 같은 event set과 대칭ρ에서는 label별 energy 적분이 각각 `(G/2)Y`가 된다.

일반적으로 한 detector가 받는 daughter-energy weight의 선형 계수 `(e/2)r`는 irrational이다. **기존 rational `BernsteinDensity.bounds(w0,w1)`에 그 계수를 float로 넣으면 exact physical moment claim이 끊어진다.** 이번 최소 범위는 event mass/count와 exact pair-energy, exact symmetric label-energy로 한정하거나, 별도의 outward rational bracket으로 energy1을 감싸는 구현을 추가해야 한다. 임의 irrational weight를 exact라고 표기해서는 안 된다.

이 때문에 geometry와 mass certificate를 먼저 닫는 설계가 가장 작고 직접적이다. source field가 generic linear rational observable이면 그대로 정확한 supplied observable 범위이며, physical daughter-energy adapter와 구분해 표기한다.

## 7. 새 구현이 확인해야 할 판별 사례

아래는 신규 구현을 위한 검증 요구이며 이 intake에서 실행하지 않았다.

- exact radical sign의 양/음/0, 완전제곱 및 비제곱 R, 서로 반대인 항의 exact cancellation.
- `H<0`, `H=0`, `H>0` 구분; 부호나 threshold를 float tolerance로 clip하지 않음.
- exact `a=1`의 stopped public endpoint와 boundary-only limit 분리.
- a<1·a=1·a>1 regime에서 원래 4-vector 방향과의 독립 비교. 기존 suite를 통째로 replay하지 않고 새 adapter에 대한 입력만 사용.
- rational fold가 있는 manufactured input과 irrational fold를 가진 input. J를 outer에만 넣은 포함성과 `5δ` bound.
- 동일 사건 양딸입자의 교환·불연속 indicator·두 창 coincidence에서 `20δ` bound와 기본ε.
- 실제 native energy labels 213/258/330 MeV 및 literal mass 중앙값을 사용한 **manufactured density**. Native DCS/error를 사용하지 않음.
- 다른 단위로 같은 A,M,e를 함께 scale해 direction·mass result 불변.
- nested delta에서 outer가 과도하게 줄어 참값을 놓치지 않는지 확인. δ 변경으로 새로운 physical uncertainty가 생기거나 사라지는 것으로 해석하지 않음.

원 물리 입력 세 개, `Gamma_thermal`, `Cv`, species heating·thermal deposition·independent binding RHS의 null, `birth_pool=UNASSIGNED`, sole `population_rest_energy_witness`와 production 상태는 기존 인계를 유지한다.

## 8. 다른 두 후보의 실제 유도 시작

### 유한 방위각

`t=φ/(2π)∈[0,1)`, `f̃(μ,t)=2πf(μ,2πt)`로 두면 `dσ=f̃dμdt`. Daughter exchange는 `R(μ,t)=(-μ,t+1/2 mod1)`다. Lab rectangular patch `Aν×At`의 CM 역상은 `F^-1(Aν)×At`이고, coincidence는 `P_A∩R(P_B)`와 `P_B∩R(P_A)`의 합집합이다.

비음수 tensor-Bernstein density를 supplied input으로 택하면 rational rectangle 적분은 두 1D polynomial 적분의 곱으로 구성된다. 임의 g를 exchange-even으로 만들려면 `(g+g∘R)/2`를 쓰되 t의 half-period seam을 정확히 나눈다. μ marginal만 사용하면 유한 azimuth coincidence 정보가 소거된다. 예를 들어 identity map, isotropic event density, 서로 반대 polar windows라도 두 azimuth windows가 π 이동 후 겹치지 않으면 coincidence는0이다.

이 구성은 spherical cap나 실제 Rice telescope acceptance의 대체가 아니다. 일반 cap에는 `d·n_lab≥cosα`의 곡선 경계와 trig/근호 interval enclosure가 추가로 필요하다.

### 움직이는 표적과 encounter measure

표적 에너지 사운동량을 `(E_t,Q_t)`, `E_t²−|Q_t|²=A²`로 두면

\[
s=A^2+2e(E_t-\mathbf n\cdot\mathbf Q_t),\qquad
v_\mathrm{flux}=c\left(1-\frac{\mathbf n\cdot\mathbf Q_t}{E_t}\right)>0.
\]

Lab number densities `Nγ(e,n)de dΩγ`와 `Fα(Q_t)d³Q_t`가 선언되면 event measure는 해당 density들의 곱, 위 flux factor 및 event-normalized CM differential cross section을 적분하는 형태다. 이 단계에서 event/inclusive normalization을 명시해야 한다.

전체 CM boost는 `(Q_t+e n)/(E_t+e)`, CM daughter momenta는 ±κu다. Lab으로 boost한 두 daughter의 에너지 합은 `E_t+e`, 운동량 합은 `Q_t+e n`이다. 따라서 한 사건의 rest-energy 변화 `2M−A`와 material kinetic-energy 변화 `e−(2M−A)` 및 photon loss `−e`가 합하여0이다. Target motion은 daughter split·stress·angular response를 바꾸지만 이 총 energy identity를 바꾸지 않는다.

실제 liquid-He target distribution와 normalized DCS/flux는 별도 공급자다. 이 대안은 추후 직접 rate 계산에 필요한 물리 연결로 보존한다.

## 9. 현재 인계

Root의 선택: KINEMATIC08 fixed exact A,M,e comparator/preimage와 기존 supplied-density mass/pair-response 적분 연결. Physical parameter uncertainty box는 후속. 이 문서는 source intake와 직접 유도 초안이며 구현·테스트·독립 결과 채택은 아직 이 문서의 근거에 포함되지 않는다.

새 source diff에 대한 검토에서는 위 부호, stopped point, irrational fold strip, width constant20, physical energy1의 irrationality를 핵심으로 확인한다. 기존 APERTURE07·ANGULAR06·PHOTON05의 완료 과학/plot/backup과 소진 예산은 replay하지 않는다.
