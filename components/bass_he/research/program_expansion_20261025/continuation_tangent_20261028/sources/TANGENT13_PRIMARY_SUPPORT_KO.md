# TANGENT13 문헌 연결 및 정확 positivity/dual 조건

2026-10-28 (Asia/Seoul). 이전 PRIMARY_REVIEW_KO.md의 event/medium transport는 열린 물리 입력에 대한 후보이다. 최신 실제 QUARTIC12 source를 조사한 뒤 부모 작업이 선택한 후속 단위는 TANGENT13: 저장된 moment/data-row identity를 재사용해258MeV endpoint-free quartic HEMISPHERES/CAPS 최소값의 남은 curved-positivity gap을 닫는 것이다. 원래 data windows, 각도, geometry, coefficient box, denominator floor를 바꾸지 않는다.

읽은 최신 원자료:
- restored/quartic12_source/research/program_expansion_20261025/continuation_quartic_20261028/THEORY.md
- 같은 폴더 INTERPRETATION_KO.md
이 원자료는 q(z)=b0+b1z+b2z², z=μ²∈[0,1], d=(2,2/3,2/5), |b_j|≤160, D=d·b≥49/4800000, fixed contracted/expanded data rows 및 signed moment envelopes를 정의한다.258MeV N16의 최소값 gap이 남았다는 source 기록을 참조한다. 새 수치 최적화나 geometry 호출은 이 문헌 작업에서 수행하지 않았다.

## Primary references와 적용 범위

1. Jiawang Nie and James W. Demmel, *Shape Optimization of Transfer Functions*, author PDF:
   https://mathweb.ucsd.edu/~njw/PUBLICPAPERS/TrnShapOptCoef.pdf .
   Exa fetch로 원문 앞18000자를 읽었다. §2, Theorem2.2는 finite interval에서 nonnegative univariate polynomial의 Markov–Lukacs 표현을 진술하고 이후 cone의 semidefinite 표현으로 연결한다. 현재 quadratic는 degree2 특수경우이므로 아래 exact2×2 표현을 직접 유도할 수 있다. paper의 general SDP numerical solver 성능은 이번 exact certificate의 근거로 쓰지 않는다.

2. A. Charnes and W. W. Cooper, *Programming with Linear Fractional Functionals*, Naval Research Logistics Quarterly9 (1962),181–186; CMU 원문 archive:
   https://iiif.library.cmu.edu/file/Cooper_box00010_fld00009_bdl0001_doc0001/Cooper_box00010_fld00009_bdl0001_doc0001.pdf .
   Exa fetch로 본문 전체 범위가 반환되었다. 양의 denominator 아래 변수 scaling으로 fractional program을 정규화하는 연결의 원전이다. 여기서는 inherited D>0가 이미 제공되고, 실제 certificate는 아래 cross-multiplied identity로 직접 증명하므로 solver strong duality를 별도 가정할 필요가 없다.

3. Victoria Powers and Bruce Reznick, *Polynomials that are positive on an interval*, DOI:
   https://doi.org/10.1090/S0002-9947-00-02595-2 .
   Exa search로 bibliographic identity와 interval positivity 주제를 확인했다. 본문은 이번 작업에서 읽지 않았으므로 개별 정리의 근거로 채택하지 않는다.

4. Stephen Boyd and Lieven Vandenberghe, *Convex Optimization* (2004), author-hosted book:
   https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf .
   fetch는 앞18000자의 목차/서문 범위다. supporting hyperplanes§2.5, dual cones§2.6, weak duality chapter5의 위치를 찾는 보조 참조이다. 이번 strict primary derivation은1/2와 아래 직접 대수에 근거한다.

총 targeted Exa 검색2회10 requested results 추가; fetch1회3URLs 추가. 전체 이 agent 조사: Exa searches9회53 requested results, fetch5회13URL requests, SciSpace3회30results. 이는 검색 recall 범위와 실제 access 기록이며 모든 관련 문헌의 exhaustive proof가 아니다.

## 정확 quadratic cone: 직접 확인 가능한 식

K={b∈R³:q(z)=b0+b1z+b2z²≥0 for every z∈[0,1]}.

Markov–Lukacs degree2 특수경우와 일치하는 표현은
q(z)=[1,z]Q[1,z]^T+τz(1−z), Q⪰0, τ≥0.
coefficients는 b0=Q00, b1=2Q01+τ, b2=Q11−τ.
따라서 어떤 τ≥0에 대해
Q=[[b0,(b1−τ)/2],[(b1−τ)/2,b2+τ]]⪰0
가 필요충분하다.2×2 PSD는 b0≥0, b2+τ≥0,4b0(b2+τ)≥(b1−τ)²로 정확히 확인할 수 있고 rotated second-order cone과 동등하다.

위 cone의 dual functional y는
Y=[[y0,y1],[y1,y2]]⪰0, y1−y2≥0
일 때 모든 b∈K에 대해
y·b=trace(YQ)+τ(y1−y2)≥0.
이 조건들은 정확 dual cone의 표현이다. 특히 evaluation functional
v(r)=(1,r,r²), r∈[0,1]
는 Y=[1,r]^T[1,r]⪰0, r−r²≥0이므로 v(r)·b=q(r)≥0이다. root의 rational tangent/evaluation certificate는 이 특수 dual element를 사용한다.

Bernstein inner controls가 nonnegative일 때 polynomial positivity가 성립한다는 기존 QUARTIC12 증명은 nonnegative partition-of-unity의 직접 대수이다. Curved-cone certificate가 필요한 이유는 zero-touching q=a(z−r)²가 finite cell Bernstein sufficient cone의 경계와 다를 수 있기 때문이다. 이는 infinite-order/angular-law completeness를 주장하는 데 쓰이지 않는다.

## 실제 선택된 constrained certificate와의 연결

부모가 확인한 saved N16 최소 witness에서는61deg lower .15 및73deg upper .23가 두 geometry 모두 active다. 따라서 unconstrained cone ratio stationary formula를 이번 답으로 자동 채택하지 않는다.

외부(data outer) row를 m61,m73, literal relaxed bounds를 L61,U73라고 하자. U73>0이다.
h=m61−(L61/U73)m73.
모든 true feasible b는 relaxed constraints m61·b≥L61, m73·b≤U73를 만족하므로 h·b≥0이다.

어떤 rational α,λ,μ,r에 대해
k_mid−αd=λh+μv(r), λ≥0, μ≥0,0≤r≤1
를 exact arithmetic으로 확인하면
(k_mid−αd)·b=λ h·b+μ q(r)≥0
이고 D>0이므로 (k_mid·b)/D≥α.
이 global lower bound는 모든 full-positive feasible quartic에 적용된다. λ 또는μ sign, row orientation, r interval을 필수로 확인해야 한다. Endpoint-grid positivity surrogate의 최적해를 full cone의 최적해로 동일시하는 절차가 아니다.

실제 moment k는 saved interval 안에 있으므로 midpoint dual certificate만으로 실제 objective 하한을 주장하지 않는다. 부모 설계는 inherited outer-polytope vertex에서 얻는 max|b_j|/D를 이용해
|(k−k_mid)·b|/D≤Σ_j δk_j C_j
를 보수적으로 빼는 방식이다. C_j는 실제 reused certificate를 연결해야 한다. 이 오차 bound는 signed b에 그대로 유효하다.

상한은 contracted data에 실제로 들어가는 square boundary q=a(z−r_in)²를 rationally bracketed root와 feasible amplitude로 구성한 뒤 saved signed moment envelope로 계산한다. 최종 tolerance≤1e−10은 exact rational lower/upper gap으로 판정하며 화면 반올림으로 판정하지 않는다.

## 과학적 지위

이 후속 노드는 fixed data/window/family/geometry의 최적화 정밀도를 개선한다. event/inclusive normalization, liquid-He electron/target-motion/response projection, actual full angular/polarization law, photon encounter history, named nonthermal birth/deposition/thermalization, global species binding은 이번 문헌 조사에서 새 실험 입력을 확보하지 못했다. 기존 physical gate와 null consumer를 그대로 유지한다.

새 strong no-go는 제안하지 않는다. 기존 finite cone empty 이력과 QUARTIC12의 더 큰 positivity family feasible witness는 서로 다른 정의역의 결과로 함께 보존한다. 이번 lower-bound certificate는 목적값의 양화된 조건부 경계를 증명하며 cosmic production이나 thermalization에 대한 배제정리가 아니다.

