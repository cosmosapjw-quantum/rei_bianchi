# HE-ANG-CCC-EXCHANGE: equal-sharing CCC 입력의 위상·교환·정규화

## 1. 문제, 기준 입력과 확보 범위

이 단위는 source payload를 받아들이기 전에 필요한 **CCC equal-energy-sharing amplitude 해석과 수치 변환**을 완성한다. 실제 H(1s) 전 범위 joint payload는 아직 확보되지 않았다. HE-ANG-SOURCE-PAYLOAD와 부모 HE-ANG의 SOURCE_INPUT_PENDING은 유지한다. 완료된 HE-X1, HE-ANG-CONTRACT, HE38, Hex와 DDCS20의 식·실행·검토를 재사용한다.

기준 저장소는 BASS_HE `c8f5818c61d14872837abf7e9bc1a73c670ae25c`다. 새 원전은 Igor Bray, arXiv:physics/9906008v3, PDF SHA256 `5f52f7624aab3beb7a6062d301787645d35b0a5f543c1f8b83d9de8fe8f09700`의 Eqs.(2),(21),(24)–(27), 그리고 A. T. Stelbovics, arXiv:physics/9905020, PDF SHA256 `1ae2401f79af8e7722c4bb72bdbac854641d913e3dc32830bd258dc32597f755`의 Temkin–Poet(TP) equal-sharing 논의와 Table I다. 원문 PDF·스크린샷은 공개 Git에 재배포하지 않는다. 원전 위치·해시·짧은 식 전사와 수치 사실만 남긴다.

과학적 새 작업은 (i) 원전 Eq.(26)의 부호를 직접 교정, (ii) 위상 의존성을 보존하는 진폭 입력 경로와 이미 정규화된 밀도 경로의 분리, (iii) phase/complex-error 정보에 따른 결정론적 범위, (iv) Table I의 이미 적용된 factor-four를 보존하는 실제 입력 검산이다. 보존량·frame·recoil 일반 계약은 이전 단위를 인용한다.

## 2. 원전 convention과 순수 대수

총 전자 spin S=0,1에 대해 s=(-1)^S라 하고, **같은 producer의 같은 물리 상태·위상 convention**으로 계산한 raw CCC 진폭을

\[
a_S=f_S^{(N)}(\mathbf k,\mathbf q),\qquad
b_S=f_S^{(N)}(\mathbf q,\mathbf k)
\]

로 둔다. outgoing energy가 같은 영역에서 원전의 coherent 조합은 z_S=a_S+s b_S다. 원전이 쓰는 atomic units는 출처 convention으로 보존한다. 진폭의 제곱이 반환하는 differential density의 단위·측도를 공급자가 명시해야 하며, 여기서 자연단위나 추가 flux·2!·spin factor를 삽입하지 않는다. SI momenta를 연결할 때 p=ħk를 적용하는 기존 계약은 그대로다.

다음은 임의 복소수 a,b에 대한 대수적 정의다.

\[
U_S=|a_S|^2+|b_S|^2,\quad
C_S=|a_S+s b_S|^2,\quad
\delta_S=a_S-s b_S,\quad D_S=|\delta_S|^2.
\tag{1}
\]

전개하면 U=A+B, C=A+B+2s Re(ab*), D=A+B-2s Re(ab*)이므로

\[
\boxed{2U_S=C_S+D_S},\qquad
\boxed{C_S=2U_S-D_S}.
\tag{2}
\]

Bray v3 p.10 Eq.(25)는 δ=a-sb를 정의하지만, Eq.(26)의 우변에는 C-D가 인쇄돼 있다. 식 (2)의 **C+D**가 그 정의와 일치한다. 예를 들어 a=1+i,b=2-i,S=0이면 (U,C,D)=(7,9,5)이고 14=9+5다. 인쇄 부호로 계산한 우변은 4다. 이 지적은 확인한 v3의 해당 항등식에 한정된다. 논문의 numerical curves를 잘못 계산했다고 추론하지 않는다.

U>0에서는

\[
\eta_S=\frac{D_S}{2U_S}\in[0,1],\qquad
\frac{C_S}{2U_S}=1-\eta_S.
\tag{3}
\]

η는 raw amplitude exchange defect의 정규화된 진단량이다. U=0이면 a=b=0, C=D=0이고 η는 정의되지 않는다. δ가 작다는 조건은 상대 크기를 제시해야 하며, coherent amplitude가 0인 곳에서 상대 오차를 나누지 않는다. 구현은 C와 D를 각각 복소수 합·차에서 구한다. C=2U-D의 뺄셈은 잔차 검사에만 사용한다.

대수식 (1)–(3)은 에너지가 달라도 복소수 항등식으로 성립한다. **이 조합을 물리적 CCC TDCS로 해석하는 이번 adapter의 범위는 equal-sharing source profile**이다. unequal-sharing에 같은 복원 규칙을 적용하는 승인은 이 단위에 없다. equal-energy point와 유한 energy bin의 평균은 구별한다.

## 3. 가중과 count의 독립성

Unpolarized e–H source에서 원전 Eq.(21)의 spin weights는 w0=1/4,w1=3/4다. 두 channel 모두 같은 측도·density 단위를 갖고 아직 spin 가중되지 않았을 때

\[
\bar C=\tfrac14C_0+\tfrac34C_1,\quad
\bar U=\tfrac14U_0+\tfrac34U_1,\quad
\bar D=\tfrac14D_0+\tfrac34D_1,
\qquad 2\bar U=\bar C+\bar D.
\tag{4}
\]

이미 spin-weighted density라면 해당 값에 weight를 다시 곱하지 않는다. raw ordered amplitudes에 coherent 합성을 했으면 뒤에서 equal-sharing factor 2 또는 4를 다시 붙이지 않는다. 이미 coherent channel density를 받으면 그 density를 그대로 보존한다. 공개 Table I의 `4CCC`는 이미 원전이 factor-four를 적용한 값이다.

이 weight는 singlet/triplet 준비확률이다. event를 unordered로 세는 factor와 inclusive electron count2를 만드는 연산은 이전 HE-ANG-CONTRACT가 별도로 소유한다. raw amplitude의 상대 위상 없이 두 확률을 더하는 연산은 quantum exchange interference를 생성하지 않는다. 이번 모듈은 전체 event normalization, finite-mass recoil 또는 σ를 출력하지 않는다.

## 4. 위상이 없을 때의 정확한 범위

A=|a|²,B=|b|²만 주어졌으면 relative phase φ에 대해

\[
C=A+B+2s\sqrt{AB}\cos\phi,
\]

이므로

\[
\boxed{(\sqrt A-\sqrt B)^2\le C\le(\sqrt A+\sqrt B)^2}.
\tag{5}
\]

φ를 0부터 π까지 바꾸면 모든 중간값을 얻는다. 이 식은 주어진 비음수 A,B와 자유로운 상대 위상의 **정확한 결정론적 range**다. 추가 phase model 없이 단일 C를 반환하지 않는다. 한 진폭이 0이면 interval은 한 점으로 축퇴한다. A=B>0이면 range는 [0,4A]다. phase interval을 empirical confidence interval로 해석하지 않는다.

## 5. 복소수 오차 원판의 전파

별도 입력 계약이 |a-â|≤εa, |b-b̂|≤εb를 제공한다고 하자. 두 complex errors가 독립적인 원판 전체를 채울 수 있을 때, z=a+s b는 중심 ẑ=â+s b̂, 반지름 r=εa+εb인 원판을 채운다. 따라서

\[
\boxed{\max(0,|\widehat z|-r)^2\le C\le(|\widehat z|+r)^2}.
\tag{6}
\]

이는 triangle/reverse-triangle inequality와 ẑ 방향의 경계점으로 증명된다. 독립 원판이 joint uncertainty의 superset인 경우에도 enclosure는 유효하지만 sharpness는 일반적으로 보장되지 않는다. ε를 calibration 없이 만들어내지 않는다. spin별 오차 집합이 독립이면 양의 spin weights로 lower/upper를 합한 range도 sharp하다. D의 별도 extrema와 C의 extrema를 한 공통 witness로 합치지 않는다.

## 6. 실제 source table의 제한된 검산

Stelbovics Table I는 TP S-wave 모델의 **singlet energy differential cross section**이다. total three-body energy E=2Ry와3Ry이며 incident laboratory energy나 full-H TDCS가 아니다. native unit은 πa0²/Ry다. 표의 8개 CCC 수치와 2개 BRM 비교값을 그대로 전사한다. 이미 `4CCC`인 값으로 relative deviation (published/BRM)-1을 계산한다. 이는 인쇄 데이터의 산술 비교다. 새 CCC/BRM solver 계산·엄밀한 수렴률·H full angular calibration을 뜻하지 않는다.

표가 제시하는 (N,Npos) 순서를 보존한다. 3Ry sequence는 단조 convergence를 가정하지 않는다. 인쇄 마지막 자리 rounding이 있고 statistical error model은 주어지지 않았다. 실험 또는 producer error를 숫자 차이 하나로 추정하지 않는다.

## 7. 수치 알고리즘과 판별 기준

복소수 성분의 max scale t로 a,b를 나눈 뒤 U,C,D와 η를 계산한다. 제곱밀도는 mantissa ×2^exponent로 보존해 입력이 매우 크거나 작아도 normalized diagnostic을 유지한다. ordinary binary64 값이 표현범위 밖이면 명시적 overflow/underflow 상태를 반환하며 JSON infinity 또는 조용한 0으로 바꾸지 않는다. zero amplitude의 η는 null이다. NaN/Inf와 음수 density/error radius는 입력 오류다.

필수 검산은 exact-rational complex oracle, S=0/1, exchange swap와 common phase invariance, constructive/destructive interference, zero 및 near-zero, scale range, spin weight exactly once, phase range endpoint와 complex-error-disk 경계점, unequal-sharing profile rejection, source Table I no-op normalization이다. 기본 산술 허용오차는 독립 oracle 대비 scale-normalized 5e-13다. 물리 uncertainty나 source admission tolerance가 아니다.

Eq.(5)의 lower endpoint는 A+B>0일 때 (A-B)²/(sqrt(A)+sqrt(B))²로 평가하면 거의 같은 제곱근의 뺄셈을 피할 수 있다. A=B=0은 별도로0을 반환한다. 수학적 range와 sharpness는 실수 산술의 명제이며, binary64 endpoint는 위 수치 허용오차로 검증한 근사값이다. Directed rounding을 통한 machine-certified enclosure는 이 구현의 주장이 아니다.

2-panel figure는 manufactured amplitude phase controls와 실제 Table I/BRM ratios를 구분해 표시한다. 이 단위의 새로운 local scientific cap은 CPU8s/wall30s, 계획된3child와 진단된 repair reserve1child다. 이전 모든 비용·실패·UNKNOWN_NOT_ZERO와 allocation은 불변·전용 불가다. Wolfram 검산은 별도 toolwall과 원격 CPU 상태를 기록한다.

## 8. 주장·다음 입력

현재 문서의 Eq.(2)–(6)은 직접 유도다. 실제 구현·Wolfram·독립 검토 결과는 해당 evidence에서 판정한다. 새 strong no-go 또는 문헌상 신규 정리 주장은 없다; NG1–NG7의 신규 no-go admission 대상이 없다는 상태를 기록한다.

후속 physical payload는 producer identity, raw complex amplitudes의 relative-phase convention, spin weight 적용 여부, absolute density units/measure, full energy/solid-angle support, count/exchange normalization, source-consistent finite-mass dynamics 또는 명명된 근사와 threshold/Jacobian/flux/error를 공급해야 한다. Eq.(27)의 partial-wave Coulomb phase를 버리고 modulus만 가져오면 complex-amplitude route에 필요한 입력이 사라진다. 공급되면 이번 adapter와 기존 event/moment contract를 연결하여 변경된 source에만 affected verification을 수행한다.

## 교정 이력

R7 Wolfram의 실제 출력에서 초안의 예시 산술값 (7,10,4)을 (7,9,5)로 교정했다. 정의·항등식·알고리즘은 변하지 않는다. 최초 원격 호출의 일반 복소수 residual은 두 spin 모두0이며 예시와 일치한다. 같은 호출의 선택적 sqrt(A),sqrt(B) endpoint 출력은 A,B≥0 조건을 주지 않아 일반 복소수 형태와 경고를 반환했다. 이 선택적 출력은 Eq.(5)의 검산 근거로 채택하지 않으며, Eq.(5)는 명시한 비음수 전제하의 직접 증명과 독립 구현 control로 확인한다. 호출 원문·경고·toolwall·원격 CPU unknown을 그대로 보존한다. 과학 suite 재실행은 발생하지 않았다.
