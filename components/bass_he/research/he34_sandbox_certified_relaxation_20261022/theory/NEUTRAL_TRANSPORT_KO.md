# HE34 중성 H/He 수송 하위 범위: 원전·유도·실행 인계

## 확보한 결과와 범위

중성 원자 H/He의 공통 온도, 희박 기체, 작은 비평형이라는 Chapman–Enskog 조건에서, 1차 Sonine 전단점성 계산을 2×2 선형계에서 양의 항으로 구성된 유리식 하나로 축약했다. 이 축약은 해당 선형계에 대해 대수적으로 정확하다. 점성의 물리적 근사 차수는 바뀌지 않는다.

입력은 T [K], 원자질량 m_H,m_He [kg], H/He 원자 수에 비례하는 두 비음수 가중치다. 가중치 합을 1로 만들거나 작은 성분에 임의의 floor를 넣을 필요가 없다. 양쪽 가중치가 동시에 0이면 조성은 정의되지 않아 명시적으로 거절한다.

기존 HE32의 21상태 전체, 전자·이온 수송, 동위원소별 수송, 반응에 따른 중성종 유입·유출의 tensor source를 이 식에 포함시키지 않았다. 이번 원전 확보는 B1의 중성 H/He 하위 범위와 실제 계산 축약을 제공한다.

## 출처와 확인 위치

1. Wargnier et al., A&A 635,A87 (2020), DOI10.1051/0004-6361/201834686.
   - 저자 PDF: https://jbscoggi.github.io/website/assets/pdf/Wargnier2020_A&A.pdf
   - HTML: https://www.aanda.org/articles/aa/full_html/2020/03/aa34686-18/aa34686-18.html
   - 확인 위치: §2.1의 시간척도 분리; Eq5–6의 전자/무거운 입자 에너지 교환; Eq10의 점성 부호; Eq32의 완전 이온화 비교; Appendix C29,C30,C35–C38의 무거운 입자 점성 선형계.
   - PDF의 Appendix C는 page15. 출판된 식과 Mutation++ 구현의 질량·Q 정규화를 대조했다.
2. Bruno et al., Phys.Plasmas17,112315 (2010), DOI10.1063/1.3495980.
   - 저자 업로드 원문: https://www.researchgate.net/publication/234852143_Transport_Properties_of_High-Temperature_Jupiter-Atmosphere_Components
   - 확인 위치: §I의 50–50000K 범위, §II Eq1–2의 수송 충돌 적분, Eq11의 유차원 fit, TableI의 계수, §II.A.2의 H–He/He–He 상호작용.
   - 본 보고서는 원문 PDF를 재배포하지 않는다.
3. 공식 Mutation++ 원전 구현·데이터:
   https://github.com/mutationpp/Mutationpp/tree/58678c0e038eb2f078fed3b45640741fdaf167dc
   - data/transport/collisions.xml: H–H pair line1823; H–He pair line1980; He–He pair line2434.
   - src/transport/CapitelliIntegrals.h lines42–49: PI factor와 Å² 단위를 지정.
   - src/transport/CapitelliIntegrals.cpp lines56–62: Bruno Eq11의 log(T) 평가.
   - src/transport/CollisionDB.cpp lines107,118 및 etai/nDij 함수: 순수 점성·확산 계수의 질량/온도 인자.
   - src/transport/ViscosityChapmannEnskog.cpp lines73–92: G와 xᵀG⁻¹x.
   - 다섯 원본 파일의 Git blob을 실제 받은 바이트에서 모두 확인했다. 세부 SHA256/크기는 UPSTREAM_MANIFEST.json에 있다. 원본 C++ 파일의 LGPL 고지는 그대로 유지했다. 새 Python prototype은 논문 식의 독립 구현이다.

Exa 3회 검색에서 요청한 후보 수는 20개(10+5+5)이며, 이는 전문을 읽은 논문 수가 아니다. SciSpace 자연어 검색 1회를 함께 사용했다. 확인한 핵심 전문 범위는 위 위치다. 이전 HE32 전체 자료 조사를 반복하지 않았다.

## 물리량과 정규화

Bruno Eq11의 7개 계수를 a1,...,a7, z=ln(T)라 두면

F(T)=(a1+a2 z) expit(2(z-a3)/a4)+a5 expit(2(z-a6)/a7).

이 식이 내는 σ²Ω*는 Å² 단위다. Wargnier/Mutation++의 면적형 적분은

Qbar(T)=π·10^(-20)·F(T) [m²].

계수 네 묶음만 필요하다: QHH22,QHHe11,QHHe22,QHeHe22.
NEUTRAL_H_HE_TRANSPORT_SUBSET.json은 이를 정확한 upstream blob과 함께 보존한다.
T=50,50000K 경계는 허용하고 범위 밖은 외삽 없이 거절한다.

필요한 순수 점성과 밀도 제거 확산계수는

η_H=(5/16)√(π k_B T m_H)/QHH22,
η_He=(5/16)√(π k_B T m_He)/QHeHe22,

nD=(3/16)√(2π k_B T(1/m_H+1/m_He))/QHHe11.

nD의 단위는 m^(-1)s^(-1), η의 단위는 Pa·s다.
k_B=1.380649×10^(-23)J/K를 사용하고 원자 질량은 호출자가 명시한다.

## 2×2 계와 양의 유리식

아래 x,y는 H/He 수에 비례하는 비음수 가중치다. 정의:

r=m_He/m_H,
A=QHHe22/QHHe11,
u=1/[nD(m_H+m_He)],
a=1/η_H,
b=1/η_He,

c_H=u[(6/5)Ar+2],
c_He=u[(6/5)A/r+2],
c_o=u[(6/5)A-2].

선형계는

G = [[x²a+xy c_H, xy c_o],
     [xy c_o, y²b+xy c_He]],

η_mix=(x,y) G^(-1) (x,y)^T.

이 식에서 공통 xy 인자를 대수적으로 소거하고

c_H c_He-c_o²=(12/5) A u²(r+1/r+2)>0

를 사용하면

N=u[(6/5)A(x/√r-y√r)²+2(x+y)²]+xy(a+b),

D=x² c_He a+y² c_H b
  +xy[ab+(12/5)A u²(r+1/r+2)],

η_mix=N/D.

N,D는 양의 입력에서 양수이며, x 또는 y가 0이어도 나머지가 양수면 정의된다.
y=0일 때 η_mix=η_H, x=0일 때 η_mix=η_He다.
x,y를 공통 상수로 곱해도 값이 같으므로, prototype은 overflow를 피하려고 max(x,y)로 두 수를 함께 나눈다. 조성 값에 인위적 하한이나 반올림을 넣지 않는다.
T와 질량이 고정된 HE32 저장 epoch 진단에서는 Q 네 값과 a,b,u,A,r을 한 번 준비하고 각 조성에 유리식만 평가한다.

## νπ 대응과 물리적 적용 조건

HE33의 저주파·작은 비등방성 근사 q≈−2ps/νπ와 Newtonian 점성 q=−2ηs를 맞추면

νπ,match=p/η.

이는 점성 일치 모델의 정의이며, Landau/Boltzmann 충돌 연산자의 정확한 과도 이완률을 결정하는 식은 아니다. CI/RR/CX number-rate를 이 νπ에 대입할 근거도 제공하지 않는다. 원전의 수송 적분은 산란각과 상대속도의 moment를 사용한다.

저장 배경에서는 p_neutral=(n_H0+n_He0)k_B T를 사용할 수 있다. χ_neutral=p_neutral/(η_mix H)는 해당 중성 성분에 대한 hydrodynamic matching 진단량이다. n_H0,n_He0를 변화시키는 반응 source moment와 전자·이온 간 수송 의존성이 없으므로, 이를 전체 gas의 닫힌 tensor IVP에 자동 대입하지 않는다.

공통 T/속도와 작은 Knudsen 수를 채택하려면 관련 종간 momentum/energy 교환률을 H,|s|,온도·조성·source 변화율과 비교해야 한다. 공통 유속과 공통 온도는 서로 다른 교환 moment의 조건이다. 원전은 전자와 heavy의 두 온도계를 별도로 취급하며, scalar chemical production과 energy relaxation을 구분한다. 현재 확보 범위는 prescribed common-T 중성 H/He 수송 계수다.

## 실제 검산과 실행

- GENERAL_WEIGHTS_WOLFRAM.json: 양의 독립 x,y,a,b,u,r,A에 대해 G 식과 N/D의 차이가 0, determinant identity 차이가 0, 양 끝점이 1/a와1/b인 것을 기호 검산했다.
- REDUCTION_WOLFRAM.json은 먼저 x+y=1로 확인한 기록이다. 그 실행의 undefined-symbol 경고도 보존되어 있다. 일반 가중치 검산에는 경고가 없었다.
- 실행 명령: python3 /tmp/he34_transport_sources/neutral_viscosity_prototype.py
- Python3.12.14 / NumPy2.3.5, 종료코드0.
- T=50,100,1000,20000,50000K에서 40개 내부 조성을 별도 NumPy 2×2 solve와 비교: 최대 상대차5.111955429020404e−16.
- 순수종·1e−300 trace·가중치 동차성25건 확인, 잘못된 입력/온도 범위6건 거절.
- 여기서 원자질량은 수치 test parameter m_H=1u,m_He=4u,u=1.66053906660e−27kg다. 향후 물리 실행의 질량을 선택한 것으로 간주하지 않는다.
- T=20000K에서 η_H=2.0918983850590453e−4Pa·s, η_He=5.108978608572882e−4Pa·s, H:He=12:1이면 η_mix=2.6010886459017614e−4Pa·s.
- PROTOTYPE_EXECUTION.json에 실제 tool chunk, command, exit code, 환경, 입력, 결과, source/data SHA256을 기록했다.
- 새 IVP0. 배경 재적분0. 성능 향상 수치는 측정하지 않았으며 여기서 주장하지 않는다.

## 다음 연결

HE34 본체는 이 JSON과 식을 받아 HE32의 실제 질량 convention을 명시하고, neutral composition의 순간 수송 진단을 계산할 수 있다. prescribed-χ mechanical 비교와 이 물리적 transport 진단을 별도 결과 열로 유지한다. 원전 전체 혼합물 계수·반응 tensor source·종간 에너지교환은 다음 DAG 의존성으로 남는다.

