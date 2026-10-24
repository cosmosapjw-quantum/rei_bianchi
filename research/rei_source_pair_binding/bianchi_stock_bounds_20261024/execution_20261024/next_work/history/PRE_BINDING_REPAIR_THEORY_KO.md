# 유한 질량 저장고의 stress 집합과 순간 work 경계

단위: REI_BIANCHI_WORK_BOUNDS_20261024. 작성: 2026-10-24.
현재 root 직접 유도. 정식 independent review와 실제 구현 결과는 별도 decision에 연결한다.

## 1. 연구 질문과 convention

기존 stock 단위는 주어진 Bianchi I 배경의 한 collisionless cohort에서 N과 U의 시간간 수송을 감싼다.
여기서는 한 순간 N,U,L이 허용하는 pressure tensor 전체를 기술하고, 주어진 팽창/shear와의 contraction을 구한다.
이 결과는 현재 미정인 anisotropic work를 유효한 구간으로 계산하는 데 사용한다.

metric (-,+,+,+), ds²=-c²dt²+Σa_i²(dx^i)², 고유시간 t와 물리적 정규직교틀을 쓴다.
m>0, M=mc². p는 그 틀의 물리운동량, k=√(M²+c²|p|²)-M이다.
ν는 물리 부피당 유한 비음수 운동량 측도, N=∫dν, U=∫k dν, support 0≤k≤L.
입력 N,U,L≥0, M>0, U≤NL. 각분포는 자유이며 원자 측도를 허용한다.
평균운동량0을 추가해도 아래 구성은 대칭 ±beam으로 만족한다.
매끄러운 밀도만 허용하면 원자 extremizer는 근사 극한이다.

P=∫ c²ppᵀ/(k+M) dν, S=tr P, Π=S/3, π=P-(S/3)I.
P,S,U는 energy/physical-volume이고 π는 signed STF tensor다.
실대칭 3×3 B는 같은 틀에서 주어져 있으며 측도 최적화 중 고정한다.
W_B=tr(BP). B가 rate이면 W는 energy/physical-volume/proper-second다.

## 2. 정확한 trace 구간

각 입자에 대해 c²|p|²=k(k+2M)이므로
g(k)=k(k+2M)/(k+M)=k+M-M²/(k+M),
g(0)=0, g''(k)=-2M²/(k+M)³<0이다.

N>0,L>0이면 chord와 Jensen 부등식으로

S_lo=U(L+2M)/(L+M) ≤ S ≤ S_hi=U(U+2MN)/(U+MN).

N=0이면 U=0 및 S=0. U=0 또는 L=0도 S=0이다.
각 나눗셈보다 먼저 영 경계를 처리한다.
N=U=0의 형식적 0/0을 평가하지 않는다.

상한은 N δ_(U/N)의 단일 에너지로 달성된다.
하한은 (N-U/L)δ_0+(U/L)δ_L로 달성된다.
두 radial measure는 같은 N,U를 가지며 그 convex mixture는 [S_lo,S_hi]의 모든 S를 만든다.
U=NL이나 U=0에서 양 극값이 합쳐지는 경우에도 성립한다.

## 3. 가능한 pressure tensor 집합의 구성

정리: 위 순간 측도 집합이 만드는 stress는 정확히
{P=Pᵀ : P⪰0, S_lo≤tr P≤S_hi}
이다.

필요성: 각 c²ppᵀ/(k+M)는 PSD이고 trace는 §2를 따른다.
충분성: 임의의 해당 P에 S=tr P>0이라 하자.
§2의 convex radial mixture로 trace S인 radial measure를 택한다.
P/S=Σ_j w_j e_j e_jᵀ, w_j≥0, Σw_j=1인 spectral decomposition을 사용한다.
각 비영 radial energy에 독립적으로 방향 ±e_j를 w_j/2씩 배치한다.
그 결과 N,U,support는 유지되며 pressure tensor는 S(P/S)=P다.
평균운동량은 각 ±쌍에서 0이다.
S=0이면 P=0이고 U=0이므로 rest measure로 달성한다.

이는 주어진 순간 N,U,L만을 고정한 집합의 정리다.
특정 과거 각분포·고정 초기 measure 또는 self-consistent diagonal Einstein 해까지 고정한 부분집합의
모든 tensor를 실현한다고 확장하지 않는다. 대각 B의 work 극값은 대각 stress beam으로도 달성된다.

## 4. 주어진 대칭 B와의 sharp contraction

a=λ_min(B), b=λ_max(B)라 하자.
aI⪯B⪯bI와 P⪰0으로 aS≤tr(BP)≤bS이다.
trace의 허용 구간까지 최적화하면

W_lo = a S_lo  (a≥0),  a S_hi  (a<0),
W_hi = b S_hi  (b≥0),  b S_lo  (b<0).

각 끝점은 해당 trace radial extremizer와 a 또는 b 고유축 ±beam으로 달성되므로 sharp하다.
각 끝점은 별도 측도로 달성한다. 동시 endpoint 달성 주장은 없다.
0인 eigenvalue는 어느 trace를 써도0이며 정의상 비음수 분기를 택한다.

부호 검사:
- 모든 rate 양수: 작은 a에는 S_lo, 큰 b에는 S_hi.
- 모든 rate 음수: 작은 a에는 S_hi, 큰 b에는 S_lo.
- 혼합 부호: 양 끝 모두 S_hi.
- B=hI: W=hS이며 h<0에서 endpoints가 바뀐다.

일반 대칭 B의 정리는 해석적 결과다. 이번 구현 API는 exact represented 대각 rate (H1,H2,H3)를 받는다.
그 eigenvalue는 min/max이므로 floating eigensolver나 새 spectral tolerance가 필요 없다.

## 5. Bianchi work·shear·운동에너지 미분

H_i=dot a_i/a_i, θ=ΣH_i, σ_i=H_i-θ/3.
B=diag(H_i)의 work W_H와 diag(σ_i)의 shear work W_σ에 §4를 각각 적용한다.
Σσ_i=0이므로 W_σ=Σσ_i P_ii=Σσ_i π_ii이다.

source-free, collisionless, force-free, homogeneous cohort의 기존 보존식은

dot N=-θN,
dot U=-θU-W_H=-θ(U+Π)-W_σ.

고정된 정확한 U에 대해 sharp 순간 미분 구간은
[-θU-W_H,hi, -θU-W_H,lo]이다.
W_H를 직접 구하여 pressure와 shear의 서로 다른 극값을 독립적으로 더하는 불필요한 폭 증가를 피한다.
W_σ의 범위는 별도로 제공하며 work·shear·norm의 모든 극값을 동시에 취할 수 있다고 해석하지 않는다.

이 식은 순간의 allowable derivative다. 시간적 경로 선택, EOS, initial/injection history,
stopping, thermalization, Einstein feedback 또는 global evolution을 선택하지 않는다.

## 6. Full Frobenius anisotropy

P의 eigenvalue λ_j≥0, Σλ_j=S이므로 Σλ_j²≤S²이다. 따라서

||π||_F²=tr(P²)-S²/3≤2S²/3≤(2/3)S_hi².

S_hi의 rank-one stress(단일 에너지 ±beam)에서 등호가 성립한다.
따라서 ||π||_F≤√(2/3)S_hi는 sharp하다.
구현은 norm_squared_upper=(2/3)S_hi²를 Fraction으로 반환한다.
1/2이나 LRS 축약계수를 넣지 않는 full Frobenius convention이다.

여러 reservoir의 실제 STF stress를 조립할 때는 signed tensors를 먼저 합산한다.
이 scalar upper bound들을 합해 실제 stress라고 대체하지 않는다.
별도 tensor 자료가 있으면 opposite-stress cancellation을 보존한다.

## 7. stock 외측 energy/support 구간과 합성

실제 N_t를 알고 U∈[u_lo,u_hi], 0≤u_lo≤u_hi≤N_t Lbar, 실제 support≤Lbar라 하자.
φ(U,L)=U(L+2M)/(L+M), ψ(U,N)=U(U+2MN)/(U+MN).
φ는 U에서 증가,L에서 감소하며 ψ는 U에서 증가한다.
따라서 S∈[φ(u_lo,Lbar), ψ(u_hi,N_t)]이다.

이 trace 구간을 §4에 넣으면 W_H와 W_σ의 안전한 outer interval을 얻는다.
A_lo=min(-θu_lo,-θu_hi), A_hi=max(-θu_lo,-θu_hi)라 하면
dot U∈[A_lo-W_hi,A_hi-W_lo].
energy와 work의 상관관계를 사각 구간으로 감쌌으므로 이 합성 미분 구간에는 sharpness를 주장하지 않는다.
norm squared도 (2/3)S_hi²로 감싼다.
현재 stock API의 support_upper_enclosure 및 energy_interval은 이 입력 조건과 직접 연결된다.

실제 저장된 stock identity fixture raw를 후속 fixture의 입력 artifact로 소비한다.
stock module을 다시 실행하지 않는다. 원자료의 provenance와 현재 소비 JSON의 Fraction encoding을 연결한다.

## 8. exact 계산과 유한 판별 fixture

int, finite float, Fraction 입력을 표현된 값 그대로 Fraction에 옮긴다.
bool, 비유한 값, 음의 N/U/L, M≤0, U>NL, 역전 energy interval, rate 길이≠3은 입력명과 함께 ValueError.
rate는 음·영·양 모두 허용한다. 함수는 float 출력/제곱근/수치 eigensolver를 사용하지 않는다.
공급자 float 이전의 정보 손실은 그대로 남는다. 기존2e-12 gate는 바꾸지 않는다.

N=U=L=2,M=1이면 S=[8/3,3], norm²_upper=6.
H=(-2,1,4): θ=3, σ=(-3,0,3), W=[-6,12], W_σ=[-9,9], dot U=[-18,0].
H=(1,2,3): W=[8/3,9], dot U=[-21,-44/3].
H=(-3,-2,-1): W=[-9,-8/3], dot U=[44/3,21].
H=(2,2,2): W=[16/3,6], W_σ=0, dot U=[-18,-52/3].
H=(-2,-2,-2): W=[-6,-16/3], W_σ=0, dot U=[52/3,18].
H=0: 모든 work/미분은0, stress bounds 자체는 유지된다.

위 endpoints는 radial0/L 또는 mono k=1의 discrete symmetric beam으로 직접 확인한다.
별도 sanity controls는 common weight7/3 scaling, rate reversal, 축 permutation, U=NL, 영 경계와 invalid input.
outer example N=2,U∈[1,2],L=2,M=1,H=(-2,1,4)는 S=[4/3,3], W=[-6,12], dot U=[-18,3].
고정 fixture 하나 안에서 수행한다. 기준값은 symbolic rational literal과 independent discrete measure sums다.
actual stock identity raw 소비는 물리 초기조건의 채택과 구별된 synthetic integration check다.

## 9. 원전 대조·CAS·심사와 결과 범위

2026-10-24 Exa2질의20result slots, SciSpace1질의10results를 탐색했다.
관련 kinetic definition은 다음 primary text에서 직접 읽었다.
- Heinzle & Uggla, Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations,
  https://arxiv.org/pdf/gr-qc/0512031 , §2 식(2c)–(3).
  c=1 source의 massive stress를 위 physical-frame c-explicit convention으로 옮겼다.
- Rendall, The initial singularity in solutions of the Einstein–Vlasov system of Bianchi type I,
  https://arxiv.org/pdf/gr-qc/9505017 , §2 식(2.3),(2.6)–(2.9).
  원전 second fundamental form k^i_j=-H_i δ^i_j, 원전 mean curvature=-θ에 주의한다.

위 원전의 global Einstein–Vlasov asymptotics는 이번 prescribed-background 결과로 채택하지 않는다.
§§2–7의 finite N,U,L stress set와 contraction은 여기서 직접 증명했다.
검색에서 가까운 동일 정리를 확인하지 못한 사실을 최초성/부재/불가능성 근거로 쓰지 않는다.
새 strong no-go는0; NG1–NG7 신규 no-go admission은 적용대상없음이다.

Wolfram context 첫호출은 internal error.
첫 evaluator의 D[g,k,2]가 잘못된 미분 문법이라 g''를 반환하지 못했고 그 raw를 보존했다.
D[g,{k,2}]로 한 번 수정한 evaluator는 g''와 φ_U,φ_L,ψ_U를 모두 반환하여 직접 유도와 일치했다.
remote kernel/parent 비용은 별도 미측정으로0이 아니다. CAS는 동일 controller의 보조 algebra check이며
native independent model review를 대신하지 않는다.

실행·심사·admission의 최종 상태와 raw hashes는 별도 DECISION에 기록한다.
정식 독립 심사가 끝나고 frozen implementation을 검사하면 해당 순간 구간을 후속 연구에 사용한다.
전체 모델 완료율 null, L4_ready=false를 유지한다.

