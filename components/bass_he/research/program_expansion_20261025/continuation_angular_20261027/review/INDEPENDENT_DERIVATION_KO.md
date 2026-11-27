# PHOTON05 후속 원전 조사 및 ANGULAR06 독립 유도

작성: 2026-10-27, 담당 /root/photon06_sources_theory.
범위: 원전 조사, 기존 기록 읽기, 직접 해석적 유도. 과학 코드·수치 테스트·plot 실행·GitHub 쓰기 없음.
기준: PHOTON05 S05 251c6baa6c3359b1d6997dbce51cea65500b53d6 / D05 4db5ce7297a7ded4624b93721873aacc9b4ebf30.
본 노트는 연구 작업용 중간 자료이며 원전의 정규화 미확인을 해소한 것으로 취급하지 않는다.

## 1. 실제 읽은 원자료와 문헌 결과

로컬 원자료:
- research/program_expansion_20261025/continuation_photon_20261027/THEORY_KO.md
- 같은 위치 MODEL_CONTRACT.json, sources/PHOTON05_PROPOSAL_KO.md, sources/PHOTON05_SOURCE_OBSERVATIONS.json
- research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/PROVIDER_ROWS.json 중 M0475002/003
- 공식 EXFOR 고정 source: https://github.com/IAEA-NDS/exfor_master/blob/939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4

Exa 검색 3회(7+5+7=19 candidate slots), 원문 fetch 2회(3개 URL 및 2개 URL), SciSpace 검색 2회(각 10개 결과)를 실제 수행했다. Exa skill 및 searching.md를 읽었다. 결과 수는 읽은 독립 원 논문 수를 뜻하지 않는다.

확인된 문헌:
1. J. Arends, J. Eyink, T. Hegerath, H. Hartmann, B. Mecking, G. Nöldeke, H. Rost, Experimental investigation of the 4He(γ,d)d reaction, Physics Letters B 62(4), 411–412 (21 June 1976), DOI https://doi.org/10.1016/0370-2693(76)90671-7 .
   실제 publisher page: https://www.sciencedirect.com/science/article/abs/pii/0370269376906717 .
   Publisher metadata를 읽었으나 normalization 식·본문은 확보하지 못했다. Exa DOI-derived metadata는 Hegerath initial과 날짜를 다르게 표시했다. 본 기록은 publisher의 명시 bibliographic row를 우선한다.
2. H. Hartmann, Experimentelle Untersuchung der Reaktion 4He(γ,d)d (1976), CERN record https://cds.cern.ch/record/790537 .
   제목·저자·연도 후보를 확인했다. 첫 fetch는 bibliographic content만, query-string fetch는 CRAWL_TIMEOUT. Thesis/report 본문과 원 normalization은 확보하지 못했다. Exa의 무관한 자동 topic labels는 채택하지 않는다.
3. B. J. Rice et al., Two-deuteron photodisintegration of 4He at Eγ=150–250 MeV, Phys. Rev. C 61, 064612 (2000), https://doi.org/10.1103/PhysRevC.61.064612 .
   실제 APS abstract https://journals.aps.org/prc/abstract/10.1103/PhysRevC.61.064612 확인. 두 energy bins 150–190/190–250 MeV, 여섯 각도, coincidence detection 및 sin²θ에 가까운 Legendre-fit 결과를 보고한다. 이 결과는 1976 native points의 완전한 angular law 또는 normalization을 대신하지 않는다. APS full article은 authorization required였다.
4. SciSpace는 Arends 논문을 특정한 두 질문에도 해당 논문 자체를 반환하지 않았다. 관련 Asbury–Loeffler1965, Silverman1984, Rice2000 등을 반환했으며 이 출처들을 Arends 원문으로 오인하지 않는다.

EXFOR packet이 직접 지지하는 사항(literature-supported):
- 213/258/330 MeV × CM 46/61/73/87 deg의 12 native DATA-CM/ERR-S rows, units NB/SR.
- Liquid helium target; incident bremsstrahlung photon energy reconstructed kinematically from reaction particles; two deuterons detected in coincidence using two TOF arms.
- ERR-S는 statistical-only 설명.
- M0475002는 Table 1에서 가져온 DA, M0475003는 별도 SIG 항목이다.

여전히 unresolved:
- Article-specific particle/event/full-sphere/half-sphere DCS convention.
- Beam polarization, measured azimuth law, detector angular/energy acceptance, incident response/bin semantics.
- Bare-nucleus model과 liquid-He electronic spectator/target-motion projection.
- Physical covariance/normalization error and actual encounter flux.
따라서 sparse DCS fitting/interpolation/extrapolation, 임의 1/2, event-rate admission은 이 조사에서 수행하지 않았다.

## 2. 직접 유도: 유한질량 CM→lab 각도 사상

컨벤션: metric (-,+,+,+), q=cp (에너지 단위), A=m_target c², M=m_d c², incident photon energy e.
PHOTON05의 0<A<2M, e>e_th, kappa>0 영역을 사용한다.

s=A²+2Ae, W=sqrt(s), Delta=2M-A,
e_th=Delta+Delta²/(2A)=(4M²-A²)/(2A),
kappa=sqrt(A(e-e_th)/2),
E*=W/2, gamma=(A+e)/W, beta=e/(A+e).

CM 방향 μ=cos θ*, azimuth φ를 택하면 한 labeled daughter에 대해

q_parallel = gamma*kappa*(μ+a),
q_perp = kappa*sqrt(1-μ²),
a=beta E*/kappa=e/(2 gamma kappa)>0.

D(μ)=sqrt(gamma²(μ+a)²+1-μ²),
Q=|q|=kappa D,
ν=cos θ_lab=gamma(μ+a)/D,
φ_lab=φ wherever the transverse direction is defined.

직접 미분하면

dν/dμ = gamma(1+a μ)/D³.

φ를 유지하므로 solid-angle Jacobian은 J=|dν/dμ|이다. 부호 있는 derivative와 밀도에 쓰는 absolute Jacobian을 혼동하지 않는다. q 좌표로 직접 쓰면

J = kappa² |gamma*kappa+(e/2) μ| / Q³.

이는 a의 큰 값을 만들지 않고도 계산할 수 있는 동등한 식이다. κ=0 또는 Q=0에서는 이 방향 사상을 정의하지 않는다.

분류:
- 0<a<1: D>0, derivative>0. [-1,1]을 [-1,1]로 단사·전사한다.
- a=1: μ=-1에서 Q=0이다. μ>-1에서 monotone이며 ν∈(0,1]. 정지 daughter의 방향은 정의되지 않는다.
- a>1: q_parallel>0, 모든 daughter는 lab forward hemisphere. μ_c=-1/a에서 fold.
  ν_min=gamma sqrt(a²-1)/sqrt[1+gamma²(a²-1)].
  ν∈(ν_min,1)는 두 CM preimages를 갖는다. ν=ν_min은 합쳐진 한 preimage이며, ν<ν_min은 support 밖이다.
  tan θ_lab,max=1/[gamma sqrt(a²-1)].

역상은 변형 전 식과 sign을 보존해야 한다. ν∈[-1,1]에 대해

G=gamma²(1-ν²), L=G+ν²,
B=L-a²G,
μ_±=(-aG ± |ν|sqrt(B))/L.

후보는 B>=0, -1<=μ<=1, Q>0과 원 사상 ν=gamma(μ+a)/D의 부호 조건을 만족할 때만 채택한다. 제곱 방정식만 풀면 spurious roots가 남는다. ν=0에서는 μ=-a가 실제 domain 내에 있고 Q>0일 때만 가능하다. Duplicate fold root를 두 번 세지 않는다. a<1에서 단일 적합 root는 (-aG+ν sqrt(B))/L로 쓸 수 있다. Endpoint φ는 방향 구면좌표의 coordinate degeneracy로 다룬다.

## 3. a=1 전이와 threshold의 차이

a=1은 e_th와 다르다. Daughter가 lab에서 정지할 수 있을 때 남은 daughter's rest-shell 조건은

(A+e-M)²-e²=M²,

따라서 A>M일 때

e_transition = A(2M-A)/[2(A-M)].

e_transition-e_th = M(2M-A)²/[2A(A-M)] > 0.

원래 endothermic domain 0<A<2M 중:
- M<A<2M: e_th<e<e_transition에서는 a>1, e=e_transition에서 a=1, e>e_transition에서는 a<1.
- 0<A<=M: 모든 finite e>e_th에서 a>1. a=1 finite transition이 없다.

독립적인 부호 확인:
a²-1의 부호는
2M(A+e)-s = A(2M-A)-2(A-M)e
의 부호와 같다. 나머지 인수·분모는 e>e_th에서 양수다.

e→e_th+에서는 κ→0, a→∞, ν_min→1. 정확 threshold κ=0에서는 두 daughter momentum이 모두 (e/2)n이고 angular pushforward가 forward Dirac measure로 붕괴한다. 보통 함수 형태의 angular density는 이 점에서 적절한 표현이 아니다.

## 4. Fold density와 적분 가능한 caustic

CM absolutely continuous density f(μ,φ)를 주었다고 가정한다. 이 f의 의미(사건의 symmetric lift 또는 inclusive daughter yield)는 호출자가 명시해야 한다.

Regular lab direction에서 pushforward density:

g(ν,φ)=sum_{μ_i in preimage(ν)} f(μ_i,φ)/J(μ_i).

a>1 fold에서 D_c=D(μ_c)>0이고
ν''(μ_c)=gamma a/D_c³ >0.

따라서 δν=ν-ν_min→0+에서
μ_±=μ_c±sqrt(2δν/ν''_c)+O(δν),
J(μ_±)=sqrt(2ν''_c δν)+O(δν).

f가 fold에서 연속이면 두 branch 합은
g(ν,φ) ~ sqrt(2) f(μ_c,φ) / sqrt(ν''_c δν).

즉 pointwise density는 δν^(-1/2)로 발산하지만 finite lab angular bin의 적분은 유한하다. 정확 caustic에서 finite density 값을 만들어내지 않는다. 수치 구현은 branch-resolved roots와 mapped CM-bin integrals 또는 원 CM measure에서의 quadrature를 우선할 수 있다. 구면을 엄밀히 pushforward하는 것은 새로운 full angular law를 추정하는 작업과 구별된다.

a=1 stopped daughter 경계:
연속 CM density의 μ=-1은 measure zero이므로 적분 결과에는 임의 방향 할당이 영향을 주지 않는다. 그러나 discrete/atomic measure가 그 점에 양의 무게를 두면 방향 구면에 억지로 놓을 수 없다. Zero-momentum atom을 momentum-space 별도 항으로 보존하거나 angular-only API에서 명시적 오류를 내야 한다.

에너지·stress moments:
a>1에서 같은 lab ν에 두 μ와 서로 다른 daughter energies가 대응할 수 있다. Angular marginal g만 반환하고 한 energy를 선택하면 energy/stress 정보가 손실된다. Weighted pushforward는
g_W(ν,φ)=sum_i f(μ_i,φ) W(q(μ_i,φ))/J(μ_i)
로 branch별 계산하거나 CM에서 직접 적분해야 한다. 이는 PHOTON05의 pair stress S_++S_- 및 energy ownership과 연결된다.

## 5. 동일입자 quotient와 factor 2

Physical unordered event orientation은 RP²=S²/{u~-u}이다. q_+(−u)=q_−(u)이며 pair event observable
F(u)=B(q_+(u))+B(q_−(u))
는 even이다.

σ_event를 total event cross section이라 하자. 다음 세 convention을 정확히 구별한다.

1. Symmetric full-sphere event lift f_event(u)=f_event(−u):
   integral_{S²} f_event dΩ=σ_event.
   사건 observable 적분은 integral f_event F dΩ.

2. Inclusive daughter density h(u):
   h=2 f_event, integral_{S²} h dΩ=2σ_event.
   사건 observable은 (1/2) integral h F dΩ.
   단일 daughter observable의 전체 생성량은 integral h B(q_+) dΩ이며, 여기에는 추가 factor 1/2를 적용하지 않는다.

3. Hemisphere representative event density H:
   한 hemisphere에서 antipodal pair당 한 대표를 택한다.
   H=h on that representative domain, integral_H H dΩ=σ_event.
   사건 observable 적분은 integral_H H F dΩ.
   Equator에서 atoms가 있으면 deterministic boundary tie-break가 필요하다.

이 등식들은 source의 convention이 확인된 후에만 적용한다. M0475002 DATA-CM가 위 세 값 중 어느 것인지 본 조사로 확정하지 못했다. 따라서 native coefficient에 factor2/half를 자동 적용하면 안 된다.

밀도의 불변성:
CM inclusive h는 antipodal-even이지만 lab inclusive angular density는 boost 뒤 일반적으로 antipodal-even이 아니다. Event multiplicity integral 2σ는 보존된다. Lab symmetry를 CM symmetry와 혼동하지 않는다.

## 6. 지금 구현 가능한 범위와 root에 제안한 계약

ANGULAR06의 조건부 이론/구현 후보:
- PHOTON05 운동학의 forward lab-angle map.
- Exact inverse branch enumeration와 support/threshold/stopped-direction 처리.
- Jacobian density pushforward 및 branch-resolved moment transport.
- 명시적 input normalization enum: EVENT_SYMMETRIC_FULL_SPHERE / INCLUSIVE_DAUGHTER_FULL_SPHERE / EVENT_REPRESENTATIVE_HEMISPHERE.
- Convention 미지정 입력은 변환 거부.
- Synthetic explicitly declared measures로 multiplicity/conservation/branch support/caustic-bin integral 검증을 설계.
- 기존 native DATA-CM 및 ERR-S는 immutable source values로 보존; full angular law inference는 하지 않음.

현재 노트의 상태:
- 위 대수와 measure 관계: derived, 독립 해석적 유도.
- Parent PHOTON05 kernel/science outcomes: 기존 근거 재사용, 재실행 없음.
- 새 scientific numerical checks/implementation: 이 agent는 not_run.
- Original experiment normalization: unresolved; 본문 확보 입력 의존성.
- No new physical rate/provider/thermal admission.
- PHOTON05 plot FAIL와 4 complete +1 partial+3 open/8, HE101 C8 PARTIAL_EXPORT19/20 reserve0 PASS/FAIL/FAIL 보존.

