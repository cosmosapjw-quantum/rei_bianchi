# HE-ANG-SOURCE-HEX-INTAKE 원전 자격과 수학적 범위

작성: `/root/source_physics`. 2026-10-24 KST.

이 부록은 확보한 Hex v2.02 원전의 실제 기능, 이번 coefficient intake가 보증하는 수학적 성질, 물리 공급자로 사용하기 전에 남은 의무를 기록한다. 기존 HE-X1·HE38·HE-ANG-CONTRACT의 유도와 검증은 재사용한다. HE-X1의 32개 fixture, 기존 수치 모형 및 독립 검토를 재계산하거나 경험적 각분포 보정으로 확대하지 않는다.

## 1. 판정과 근거의 종류

**이번 단원의 승인 범위는 실제 source/schema 확보, raw-data catalogue, 저장된 유한 Chebyshev 계수의 해석과 생략 오차 bound이다. H1 ionization angular provider의 물리 승인과 finite-mass event law의 승인은 포함하지 않는다.**

원전 검토는 이미 완료한 `HEX_R6_SCIENTIFIC_REVIEW.md`를 그대로 재사용한다. 이 파일의 SHA256은 `4f2f56dec101c2d5139f7075bbc386d2102565de89ca27d9de7970aef7c17ce3`이며, 실행 환경 전환 후 복구된 파일도 이전 측정 hash와 일치한다. 원전 소스 8개 파일 역시 복구 전 provenance와 hash가 일치한다. 이 부록은 그 검토를 다시 수행한 결과가 아니라, 완료된 결과를 현재 단원의 계약과 연결한 저술 문서다.

재생성 직후 `code/hex_intake.py`의 초기 수식·claim boundary 검토는 SHA256 `8c2a510e9d34f4a54a6035d851b32aa629b77c8ebd89c35eb331abeedb87c4c8`에서 read-only로 수행했다. 이 identity의 검토는 historical record로 보존한다. A1/A2 읽기 경로 수정 후에는 SHA256 `2196134dbfd7b757eaef3a83618af86c66332a550d9008166d13ac88e8b4935d`와 해당 diff를 확인했으며, coordinate·decoder·`exact_tail`·`select_terms`·`evaluate`의 수학 함수는 그대로다. **수식·범위 정적 검토는 `PASS_SCOPED`**다. 이는 물리 정확도 또는 자원 한도 준수의 포괄 인증을 뜻하지 않는다. 실행 결과와 누적 예산은 소유자의 별도 receipt를 따르고, 최종 전체 CORE identity 검증은 C9가 담당한다. 이 검토자는 새 과학 실행을 하지 않았다.

이 문서에서 원전의 executable path는 **source fact**, 그 식 사이의 관계와 tail bound는 **derived**, 아직 확보·검증하지 않은 내용은 **pending obligation**으로 구분한다. 제조한 계수와 SQL fixture는 대수·입출력 검증용이며 hydrogen scattering 데이터가 아니다.

## 2. 실제 확보한 원전과 기능

[저자 기관의 Hex 배포 페이지](https://utf.mff.cuni.cz/data/hex/index.html)가 연결하는 [공개 source archive](https://utf.mff.cuni.cz/data/hex/hex-src.tar.gz)를 실제로 확보했다. 이 source는 `Hex-src-v2.02`, 682,869 bytes, SHA256 `ebb2695ff7dbf40274d329cf706a93e040d4997254c1f6677d0ccf791a9fe6ad`이다. source 안의 MIT notice와 버전별 README를 읽었다. 현재 웹의 더 새로운 개발 환경 설명을 이 archive의 요구 조건으로 소급하지 않는다.

| 실제 파일·경로 | 확인한 기능 | 이 사실이 보장하지 않는 내용 |
|---|---|---|
| `hex-ecs/src/amplitudes.cpp::fcheb` | ECS scattering solution에서 radial ionization amplitude의 Chebyshev 계수 생성 | 이번 단원에서 ECS solution을 계산했거나 수렴을 검증했다는 뜻이 아님 |
| 같은 파일의 SQL writer | `Xi_Sl1l2`를 `ionf` BLOB로 기록 | source archive에 실제 ionization dataset이 들어 있다는 뜻이 아님 |
| `hex-db/src/var/ionf.cpp` | `(ni,li,mi,L,S,Ei,l1,l2,cheb)` schema와 radial consumer | 다른 consumer와 normalization이 자동으로 일치하는 것은 아님 |
| `hex-db/src/var/tdcs.cpp` | bipolar spherical harmonics와 Coulomb phases를 합한 angular TDCS 경로 | finite-mass recoil, empirical calibration 또는 full-domain 오차를 제공하는 것은 아님 |
| `hex-db/src/var/ics.cpp` | 같은 coefficient의 half-shell integral cross-section 경로 | 출력이 실험으로 교정되었다는 뜻이 아님 |
| `common/hex-arrays.h` | native-endian binary BLOB 직렬화 | producer endian·precision·complex ABI를 BLOB 자체가 알려 주는 것은 아님 |

source archive에는 `.sql`, `.db`, `.sqlite`, `.h5` ionization payload가 없었다. 포함된 `singlet.dcs`와 `triplet.dcs`는 test script가 요청하는 elastic `1s→1s` 표본이다. 따라서 **ionization code의 존재와 numerical ionization payload의 존재는 별개**다.

별도로 확보한 [공식 `Hex-170210.sql.xz`](https://utf.mff.cuni.cz/data/hex/Hex-170210.sql.xz)는 7,880,672 bytes, SHA256 `afa8d83ada688ecf91c40340da669e204885ec5c52d04fc55b48837b52135101`이다. 실제 첫 catalogue 시도는 8 MiB statement cap에서 실패했으며, **그 당시 판정은 `INTAKE_FAILED / DATA_AVAILABILITY_UNKNOWN`**이었다. 그 실패에서 `ionf` 부재를 추론하지 않았다. 실패·진단·수정 receipt는 그대로 보존한다.

이후 명시적 `hex-lines` dialect로 수행한 **A2 전체 catalogue가 완료**되었다. [실제 출력](../evidence/execution/A2/04_catalogue.stdout.txt)과 [종료 receipt](../evidence/execution/A2/04_catalogue.FINISH.json)를 직접 읽어 다음을 확인했다.

| 관측 항목 | A2 실제 결과 |
|---|---|
| 전체 INSERT row | `tmat` 948,557개 |
| H1 초기 `(1,0,0)`의 `tmat` row | 86,457개 |
| 해당 H1 row의 incident `Ei` 최솟값·최댓값 | `1e-7`, `0.9374` Ry |
| 전체 `ionf` row | 0개 |
| H1 `ionf` row | 0개 |
| 압축 해제한 크기 | 69,441,007 bytes |
| 압축 해제한 SHA256 | `82def29890bba56bb31f31524dcbea58bd0a0f5b39441ee7b6594bd28fc54896` |
| 입력 압축 파일 identity | 위 7,880,672-byte archive hash와 일치 |
| SQL 실행 / 물리 공급자 값 추론 | 둘 다 수행하지 않음 |

이 값들은 **이 hash로 고정된 파일의 실제 raw row 판정**이다. `Ei` extrema는 연속 domain coverage나 accuracy를 뜻하지 않는다. 관측된 H1 `tmat` incident energy는 source의 H1 ionization threshold `1 Ry`보다 낮고, 이 파일에는 `ionf` 입력이 없다. 따라서 **현재 물리 HE-ANG 상태는 `SOURCE_INPUT_PENDING`**이다. 이는 이 파일에서 필요한 ionization coefficient를 얻지 못했다는 결론이며, 물리 단면적을 0으로 계산한 결과나 다른 모든 source에 대한 no-go가 아니다. 이 source code의 존재와 수학적 intake 성과는 그대로 보존한다.

### 제한된 input-format diagnosis의 원전 근거

소유자가 수행한 65,536-byte prefix diagnosis에서는 LF 937개, semicolon 0개, quote 0개가 관찰되었고, `BEGIN TRANSACTION` 다음에 한 줄당 `INSERT INTO tmat VALUES(...)`가 있었다. 이는 prefix의 형식 관찰이며 전체 dataset의 채널 존재 판정이 아니다.

이 failure의 원인을 좁히기 위해 actual source의 `hex-db/src/db.cpp::hex_import_`만 추가로 읽었다. 이 함수는 `std::getline(is,cmd)`로 한 줄씩 받고 그 줄 안에서 semicolon을 찾는다. semicolon이 없으면 그 줄 전체를 `cmd1`로 두어 `st << cmd1; st.exec()`를 실행한다. 따라서 newline-terminated statement는 원전 importer가 수용하는 형식이다. 관련 파일 SHA256은 `5f932dfe4f985eee3560b8c466d7c5acdd16493abf3341cff01112527b2c5038`이다.

이 근거는 explicit `generated-line` dialect를 추가하는 최소 input-boundary 수리를 뒷받침한다. 구현의 명칭은 `hex-lines`다. 기존 semicolon default와 크기 cap을 유지하며 물리·정규화·수학적 bound는 바뀌지 않았다. A2 전체 catalogue가 완료되기 전에는 데이터 존재 여부를 unknown으로 유지했고, 완료 후에만 위 actual-byte 판정으로 갱신했다.

## 3. Generic decoder와 H1 source admission

현재 구현의 `decode_ionf_row`는 generic source-schema utility다. 필요한 숫자 field, 일부 quantum-number 조건, 양의 excess energy, nonempty finite binary64 complex coefficient와 외부에서 명시한 ABI를 확인한다. H1 이외의 초기 상태를 decode할 수 있다. 이는 다른 초기 상태를 H1 증거로 채택하는 동작이 아니다. 이 utility 자체가 angular parity, exchange relation, 모든 채널의 완전성 또는 물리해의 정당성을 증명하지도 않는다.

`catalogue`의 availability 판정은 초기 `(ni,li,mi)=(1,0,0)`인 H1 row만 별도로 센다. 모든 `ionf` row 수와 H1 row 수가 분리되어 있다. 반환 상태의 의미는 다음과 같다.

| 상태 | 정확한 의미 |
|---|---|
| `SOURCE_INPUT_PENDING` | 선택한 입력에서 H1 `ionf` row를 확인하지 못했다. 단면적이 0이라는 결론이 아니다. |
| `RAW_H1_IONF_PRESENT_ABI_UNCONFIRMED` | H1 `ionf` SQL row가 존재한다. coefficient ABI·값·수렴·물리 normalization의 인증은 아직 없다. |

catalogue는 SQL을 실행하지 않고 literal row를 읽는다. raw row 존재만으로는 nonempty coefficient가 decode되었다고 주장할 수 없다. 빈 BLOB·NULL·누락 row를 물리적 zero cross section으로 바꾸지 않는다. 단면적·각분포·recoil 값을 새로 만들어 반환하지 않는다.

원전의 BLOB는 native-endian `sizeof(T)` byte열이다. 이번 decoder가 요구하는 `binary64-real-imag`는 외부 provenance로 확인해야 하는 import convention이다. `little` 또는 `big` endian을 명시해야 하며, plausible 값이 나오는 endian을 고르는 방식은 허용하지 않는다. 실제 데이터의 ABI 확인은 해당 데이터의 producer 정보에 의존한다.

## 4. Chebyshev convention과 생략 오차의 엄밀한 bound

저장된 finite complex coefficient를 `C0,...,C(N−1)`라 하고 `N≥1`이라 하자. source의 유한 표현은

\[
P_N(t)=\frac{C_0}{2}+\sum_{j=1}^{N-1}C_jT_j(t),\qquad -1\le t\le1.
\]

현재 `evaluate(C,x)`는 `x∈[0,1]`, `t=2x−1`로 두고 이 식을 floating Clenshaw recurrence로 계산한다. default는 모든 coefficient를 유지한다. `C0/2` convention은 원전과 일치한다.

`m`이 유지하는 coefficient의 수이고 `1≤m≤N`이면

\[
P_m(t)=\frac{C_0}{2}+\sum_{j=1}^{m-1}C_jT_j(t),\qquad
\tau_m=\sum_{j=m}^{N-1}(|\Re C_j|+|\Im C_j|).
\]

실수 `t∈[−1,1]`에서 `Tj(t)=cos(j arccos t)`이므로 `|Tj(t)|≤1`이다. 따라서

\[
|P_N(t)-P_m(t)|
\le\sum_{j=m}^{N-1}|C_j||T_j(t)|
\le\sum_{j=m}^{N-1}|C_j|
\le\tau_m.
\]

이는 coefficient가 단조 감소한다는 가정 없이 성립하는 uniform absolute bound다. 모든 생략 계수를 포함하며, `m=N`이면 `τN=0`이다. `m≥1` 조건으로 constant term을 반드시 유지한다. interval 밖의 extrapolation이나 nonfinite coefficient에는 이 정리를 적용하지 않는다.

구현은 finite binary64의 real/imaginary 성분을 `Fraction.from_float`로 정확한 유리수로 바꾸고 합산한다. 따라서 `exact_tail`이 반환하는 값은 **입력된 binary64 coefficient에 대한 정확한 L1 bound**다. 임의 precision source coefficient를 binary64로 변환할 때의 오차까지 보증하는 것은 아니다.

`select_terms`는 마지막 coefficient부터 nonnegative suffix를 정확히 누적한다. tolerance를 넘기 전까지 왼쪽으로 이동하므로 조건을 만족하는 최소 retained prefix를 찾는다. 생략 가능한 suffix의 크기는 왼쪽으로 갈수록 감소하지 않는다. 전체 suffix를 보지 않고 중간의 작은 coefficient만으로 절단하지 않는다. 상대오차 조건이나 숨은 `1e-8` tolerance도 도입하지 않는다.

### 원전 local cutoff의 정확한 반례

`C=(2,0,2)`이면 원전 `tail(eps)`는 `C1=0`에서 정지해 두 coefficient만 유지한다. `x=1/2`, 즉 `t=0`에서

\[
P_2(0)=1,\qquad P_3(0)=1+2T_2(0)=-1.
\]

실제 coefficient omission은 2이고 `τ2=2`가 이를 정확히 잡는다. 이는 특정 finite polynomial의 구성적 반례다. hydrogen angular distribution의 오차가 2라는 결과가 아니다.

### Bound가 포함하지 않는 항목

- Clenshaw recurrence의 floating roundoff, overflow 또는 normalized coordinate 계산 오차.
- 저장되지 않은 coefficient, source Chebyshev fit/aliasing 오차. 원전 generator도 같은 `tail` heuristic을 사용하므로 저장 coefficient를 전부 유지하는 것만으로 source fit 수렴이 인증되지는 않는다.
- ECS radial grid, B-spline, angular truncation, extraction radius, 적분 및 scattering dynamics의 오차.
- 실험 측정 오차, model discrepancy, finite-proton-mass 오차.
- `k1k2`로 나누는 physical amplitude의 slow-electron endpoint bound.
- 함수의 zero 부근을 포함한 relative error bound.

따라서 현재 synthetic oracle는 finite-polynomial convention과 represented-coefficient bound를 검증한다. 실험적 각분포, source 수렴, 전 물리 domain 또는 HE-ANG collision closure를 검증하지 않는다.

## 5. 원전 coordinate와 channel normalization

ECS generator가 `[0,kmax]`에서 `k1`을 넣고 TDCS consumer가 `[0,1]`에서 `sqrt(s)`를 넣는 것은 서로 일치한다.

\[
k_1=k_{\max}\sqrt{s},\qquad
t=2k_1/k_{\max}-1=2\sqrt{s}-1.
\]

이 interval rescaling은 bug가 아니다. `IonfRow.normalized_coordinate`는 `Ei>1/ni²`인 source interval을 `x=k1/sqrt(Ei−1/ni²)`로 옮긴다. H1 threshold는 source의 fixed-nucleus convention에서 `Ei=1 Ry`다.

반면 실제 입력 triplet 순서는 source parameter 설명과 다르다. executable code는 `(theta,phi,Efrac)`를 `(x,y,z)`에서 읽는다. future angular adapter는 이름 있는 field를 사용하고 ambiguous triplet을 그대로 수용하지 않아야 한다.

### Exact stored H1 energy에서 확인한 내부 관계

`Ei_Ry>1`, `ki=sqrt(Ei_Ry)`, `kmax=sqrt(Ei_Ry−1)`, `k1=kmax sqrt(s)`, `k2=kmax sqrt(1−s)`로 둔다. 채널 `a=(L,l1,l2)`의 source polynomial을

\[
Q_a(\kappa)=\frac{C_{a0}}2+\sum_{j=1}^{N_a-1}C_{aj}T_j(2\kappa-1)
\]

라 쓰면 `tdcs.cpp`의 spin sector 식은

\[
F_S=\frac{1}{k_1k_2}\sum_a
i^{-l_1-l_2}e^{i[\sigma_{l_1}(k_1)+\sigma_{l_2}(k_2)]}
\mathcal Y^{L0}_{l_1l_2}(\Omega_1,\Omega_2)Q_a(\sqrt{s}),
\]

\[
D_S=w_S\frac{k_1k_2}{k_i}|F_S|^2,\qquad w_S=\frac{2S+1}{4}.
\]

`ics.cpp`는 같은 coefficient로

\[
\sigma_S=\frac{w_S}{k_i}\sum_a\int_0^{\pi/4}|Q_a(\sin\beta)|^2\,d\beta
\]

를 계산한다. bipolar spherical harmonics의 두 solid-angle 적분 직교성과

\[
k_1=k_{\max}\sin\beta,\quad k_2=k_{\max}\cos\beta,\quad
d\varepsilon_1^{\rm Ha}=d(k_1^2/2)=k_1k_2\,d\beta
\]

를 적용하면 두 expression은 outgoing-energy density를 Hartree당으로 해석할 때 내부적으로 일치한다. 이는 **source-internal normalization 관계의 유도**다. 물리 absolute amplitude의 독립 교정은 아니다. incident `Ei` 입력은 Ry인데 TDCS 출력 header에는 differential-energy 단위가 충분히 명시되지 않고, output scaling도 `lfactor²`만 곱한다. 따라서 future importer는 이 추론과 단위 변환을 명시하거나 primary convention 확인 전까지 normalization을 pending으로 유지해야 한다.

`β∈[0,π/4]`는 `0≤s≤1/2`인 unordered-event half-shell이다. exchange-symmetric density를 labelled full shell로 옮길 때 event double counting을 제거해야 한다. HE-ANG의 inclusive count2 marginal은 각 event에서 두 outgoing electron을 각각 더해 total mass `2σ`를 얻는 객체다. event measure 자체를 두 배로 하는 것과 구분한다. 원전의 spin sector output에는 `wS`가 이미 있으므로 unpolarized result에서 두 번 곱하지 않는다.

아직 해소하지 않은 source 내부 차이도 보존한다.

| 항목 | 실제 source 관찰 | 현재 처리 |
|---|---|---|
| Radial division | `ionf.cpp`·`ionamp.cpp`는 `(k1k2)^2`로 나누고, `tdcs.cpp`는 `k1k2`로 나눔 | 서로 다른 amplitude convention을 조정하기 전 physical evaluator 승인 보류 |
| 직접 ECS triplet total | angular-block loop에서 triplet integral을 대입하고 singlet은 누적함 | database `SUM(...)` 경로와 구분; direct total의 상호 검증 주장 안 함 |
| Multi-energy TDCS interpolation | 요청한 `Ei`의 momentum·phase를 여러 stored energy coefficient에 사용 | 위 normalization 비교는 exact stored energy에 한정 |
| Endpoint | TDCS radial division에서 `k1k2=0` 가능 | slow-electron limit 및 omitted support의 별도 의무 유지 |

현재 adapter는 radial division, spherical harmonics, spin weighting, flux 또는 cross section을 적용하지 않는다. 따라서 이 source 차이를 은폐한 physical-provider 값이 만들어지지 않는다.

## 6. Fixed-proton source와 finite-mass event law

원전 [ECS 문서](https://utf.mff.cuni.cz/data/hex/hex-ecs/index.html) 및 실제 `hex-ecs/src/doc.h`의 Hamiltonian을 SI 상수 표기로 복원하면

\[
H_\infty=-\frac{\hbar^2}{2m_e}(\nabla_1^2+\nabla_2^2)
 +\frac{e^2}{4\pi\epsilon_0}
 \left(-\frac1{r_1}-\frac1{r_2}+\frac1{r_{12}}\right).
\]

원전은 이를 atomic units로 쓴다. nucleus는 고정되어 있고 초기 상태의 spin에 따라 두 전자의 exchange symmetry를 적용한다. 이 source는 해당 근사에서 quantum-exchange amplitude의 실제 후보이나, finite-proton-mass scattering law는 아니다.

유한 proton mass `M`에 대해 전체 COM 운동을 제거하고 proton-relative coordinates를 사용하면 internal Hamiltonian은

\[
H_{\rm int}=-\frac{\hbar^2}{2\mu}(\nabla_1^2+\nabla_2^2)
-\frac{\hbar^2}{M}\nabla_1\cdot\nabla_2+V,
\qquad\mu=\frac{m_eM}{m_e+M}.
\]

reduced mass와 mass-polarization derivative는 dynamics와 threshold convention을 바꾼다. frame boost만으로 이 항들이 생기지 않는다. fixed-target lab source event가 `E1+E2=E_in−I`를 만족할 때 `p_p=p_in−p1−p2`만 덧붙이면 보통 양의 recoil energy `|p_p|²/(2M)`만큼 finite-mass energy shell이 어긋난다.

momentum을 재투영해 conservation을 맞추는 근사는 별도 identity를 가진 새 source model이다. 그 모델은 distribution, Jacobian, rate/flux, threshold 및 approximation error 의무를 명시해야 한다. 이미 완료한 HE-ANG source/frame/event 계약이 이 다음 단계의 gate다. 이번 source intake에서 K_e, D_e, ion recoil momentum·energy·STF 또는 실험적 angular correction을 새로 승인하지 않는다.

## 7. 유지하는 다음 의무

한 source family와 한 공식 dataset의 actual-byte 판정은 위 범위에서 완료했다. 이 dataset에 없는 H1 ionization 입력과 물리 승격을 위해서는 다음 의무가 실제로 충족되어야 한다.

1. 선택한 H1 preparation과 exact incident-energy domain에서 유효한 numerical ionization coefficient 또는 동등한 joint data.
2. producer ABI, amplitude/flux·energy-density convention, spin/exchange·half-shell count와 source channel normalization의 해소.
3. angular/energy/slow-electron support와 부분 domain의 누락 오차, source의 numerical convergence evidence.
4. source-model uncertainty와 numerical arithmetic uncertainty를 구분한 책임 범위.
5. finite-mass dynamics 또는 명시된 named approximation을 기존 HE-ANG의 동일 law·frame·event 계약에 연결한 증거.

raw row 부재가 확인되더라도 그 dataset의 입력 공백을 뜻한다. 다른 모든 source가 불가능하다는 no-go가 아니다. source code 존재가 확인되더라도 경험적 각분포가 확보되었다는 뜻은 아니다. 기존 budget, 실패 기록, claim gate와 no-activation 상태는 그대로 보존한다.
