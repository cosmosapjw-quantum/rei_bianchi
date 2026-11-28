# B1 RCX: 반응률과 광자 수의 공급 경계

## 1. 문헌으로 확인된 수치와 모형

[GM25] García Muñoz, De Fazio, Wilson, France, arXiv:2511.21966v1, Appendix B.3, PDF9쪽:
https://arxiv.org/html/2511.21966v1 ; https://arxiv.org/pdf/2511.21966 .
저자들은 West et al. (1982)의 단면적을 적분한 charge-exchange rate를
200–10000 K에서 상수 1.70×10^-13 cm³ s^-1로 잘 근사할 수 있다고 명시한다.
fit 잔차의 상한/통계오차는 제시되지 않았다. 정확한 상수법칙으로 승격하지 않는다.
GM25의 Table B.2는 He²⁺+전자 복사재결합이며 이 원자충돌 자료가 아니다.

[W82] B.W. West, Rice MA thesis, April1982, `source/RICE1769.pdf`, 2–3쪽.
⁴He²⁺+H(1s) -> He⁺(1s)+H⁺의 radiative charge transfer를 optical potential로 계산한다.
2pσ -> 1sσ Einstein-A 전이와 하나의 방출광자를 갖는 과정이다.
학위논문과 PRA26,3164(DOI10.1103/PhysRevA.26.3164)의 버전을 구별한다.

이번 작업은 이 수치 근사식을 평가하는 공급기다. 원 West 단면적 또는 GM25의 적분을
재계산하지 않았다. source 선택 및 상충 인지는 호출자가 명시한다.

## 2. 열평균의 정의와 단위

국소 원자 충돌계의 비상대론적 두 종, 공통 온도 T, 상대 drift0의 Maxwell 분포를 전제로 한다.
θ=k_B T, μ=m_a m_b/(m_a+m_b), E=μg²/2이면

k(T)=sqrt[8/(πμ)] θ^(-3/2) ∫_0^∞ E σ(E) exp(-E/θ) dE.

일반적인 비평형 velocity distribution에 이 식을 강제하지 않는다. GM25의 thermal coefficient는
이미 적분된 수치이므로 Liu의 keV/u 변환을 거쳐 다시 만들 필요가 없다. 그 사실이 다른
동위원소 또는 finite-drift rate를 정한다는 뜻도 아니다. W82의4He-H ancestry만 유지하고
새 질량 rescaling을 하지 않는다.

1 cm³=10^-6 m³이므로 구현 계수는 정확한 소수 변환으로1.70×10^-19 m³ s^-1다.
반응률 계수와 단면적의 단위를 혼동하지 않는다. 온도 범위는200≤T/K≤10000로 제한한다.
dk/dT=0은 이 상수 근사식의 성질일 뿐 참 원자 반응률의 기울기 측정이 아니다.
경계에서는 유효영역 안쪽의 편미분만 표기한다.

## 3. species·전자·광자 counting

종 순서(HI,HII,HeI,HeII,HeIII,e)에서 ν=(-1,+1,0,+1,-1,0).
H핵수, He핵수, 전하 벡터와ν의 내적은 모두0이다.
C_s(T)=ν_s k(T), C_γ(T)=k(T)이며 실제 event rate로 만들 때 곱하는 밀도쌍은n_HI n_HeIII다.
밀도 자체나 유체 방정식은 공급하지 않는다. 두 다른 종의 반응에1/2를 넣지 않는다.
광자 수 한 개는 W82의 single-photon mechanism에서 유도한다. mean photon energy를 측정한 것은 아니다.
자유전자는 직접 생성되지 않는다. 이후 열화/광이온화 반응은 별개 owner다.

## 4. 에너지율을 정하지 못하는 이유

출사 무한거리의 원자 내부에너지 차이를ΔE_int라 하자. 초기 CM계에서 단일 방출광자의
에너지와 recoil을 명시하면 에너지 보존은

E_γ + K_rel,out + K_pair,CM,recoil = E_CM - ΔE_int

이다. 외부장이 없고 kinetic energy를 비상대론적으로 쓸 때의 장부이며 photon recoil을 생략하려면
별도 근사로 적어야 한다. count rate만으로 E_γ와 남는 relative kinetic energy의 분배는 정해지지 않는다.
따라서 q_int 또는 ground-state defect를 광자 에너지나 즉시 열로 치환하지 않는다.
광자 수 계수는 제공하되 heat/recoil/mean photon energy/spectrum/inverse rate는null로 반환한다.

## 5. 상수 thermal fit에서 σ(E)를 발명하지 않는다

모든θ>0에 대해 정확한 상수k0를 주는 하나의 모형은 σ(E)=k0 sqrt(μ/(2E))=k0/g다.
감마적분Γ(3/2)=sqrtπ/2로 위 열평균이k0임을 확인할 수 있다.
하지만 GM25는 유한T범위에서의 근사와 미정 잔차를 제공할 뿐이다. 이 모형을 유일한 실제σ로 역추론할 수 없다.
단일온도만 놓아도 σ_A(E)=σ0와 σ_B(E)=σ0 E/(2θ0)는θ=θ0에서 같은 thermal rate를 갖지만
다른온도에서는 비가θ/θ0이고 monoenergetic rate도다르다. 이는 양성 함수의 정확한 반례다.
정확하고 noiseless한 연속온도함수가 적절한 Laplace가정 아래 유일성을 가질 수 있다는 사실을
부정하는 반례가 아니다. 현재 자료는 그 전제를 제공하지 않는다는 점이 핵심이다.

## 6. source disagreement의 의미

GM25는 자신들의 값이 AR85 편집자료와 일치하고 KF96값보다10배 넘게 크다고 보고한다.
이번에 KF96 원 coefficient row와 normalization을 완전히 회수한 것은 아니므로 정확한 비나 원인을 판정하지 않는다.
검색 snippet의 수치를 독립 대조 결과로 올리지 않는다. 두 값을 평균하거나 차이를Gaussian오차로 정의하지 않는다.
API는 이 상충을 인지하는 explicit source selection을 요구한다. 물리 production의 승인 판단은 별도다.
