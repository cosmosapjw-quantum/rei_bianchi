# R5 구성적 유도: 공유 누적량의 정확한 정보 경계

## 1. 단조 closure와 존재성

l_i=max(0,L_0,…,L_i), u_i=min(P_U,U_i,…,U_m)로 둔다. 두 배열은 nondecreasing이다. 모든 feasible F는 l_i≤F_i≤u_i를 만족한다. 따라서 어느 i에서 l_i>u_i이면 P는 공집합이다.

역으로 모든 l_i≤u_i이면 l 자체가 각 원래 lower/upper·cap·monotonicity를 만족한다. exact F_0=0 입력 때문에 l_0=u_0=0이다. u 또한 feasible하다. 이것으로 존재성의 필요충분조건을 얻는다.

## 2. 연속 window와 extremizer

0≤a<b≤m에서 단조성과 endpoint bounds는
max(0,l_b−u_a)≤F_b−F_a≤u_b−l_a
를 준다.

상한 witness는 i<b에서 F_i=l_i, i≥b에서 F_i=max(l_i,u_b)다. 뒤쪽 u_i≥u_b이므로 각 upper를 넘지 않고 연결점도 monotone이다. F_a=l_a,F_b=u_b이므로 상한을 달성한다.

하한은 c=min(u_a,l_b)로 두고 i<a에서 F_i=min(u_i,c), i≥a에서 F_i=max(l_i,c)로 구성한다. i<a이면 l_i≤l_a≤c이고 i≥a이면 c≤u_a≤u_i라서 모든 원래 interval에 들어간다. 연결점은 c를 사이에 두고 nondecreasing이다. F_a=c,F_b=l_b이므로 하한을 달성한다. 따라서 정보 polytope 안에서 두 경계가 sharp하다.

연속 bin의 합은 Σ_(i=a+1)^b(F_i−F_(i−1))=F_b−F_a이다. 반드시 이 telescoping을 먼저 수행한 뒤 경계를 취한다. Canonical bin marginal enclosure의 합과 비교한 폭 감소는 정보 표현의 개선이며 새로운 물리 모델 오차 감소를 뜻하지 않는다.

## 3. 두 endpoint projection과 variable-reference 범위

Endpoint projection은 정확히 Q=[l_a,u_a]×[l_b,u_b] ∩ {x≤y}이다. 필요성은 자명하다. 임의(x,y)∈Q에 대해 i<a에서 min(u_i,x), a≤i<b에서 max(l_i,x), i≥b에서 max(l_i,y)로 전체 chain을 확장할 수 있다. 각 구간의 원래 bound와 연결점 monotonicity가 성립하며 F_a=x,F_b=y다.

고정 양수 b_a,b_b에서 y/b_b−x/b_a는 선형이므로 feasible rectangle corners와, d_lo=max(l_a,l_b)≤d_hi=min(u_a,u_b)인 경우의(d_lo,d_lo),(d_hi,d_hi)에서 최솟값·최댓값을 취한다. 꼭짓점 선택이 바뀌는 kink에는 일반 smooth Jacobian을 주장하지 않는다.

## 4. 단위와 단일 사건 사상

n=10^6 N[m^-3], e=10^6 eV_J E[Jm^-3], eV_J=801088317/5000000000000000000000000000J/eV, I=(2721/50)eV_J이다. 이 변환은 정확한 유리수로 한 번만 적용한다.

명시적 b>0에서 ΔY_11=n/b, ΔY_12=−n/b, Δzeta=−n/b, Δw_nt=−e/b이며 다른 native25행은0이다. 별도 photon port는(n/b,(e+In)/b), binding 변화는−In/b다. ΣΔY=0, q·ΔY−Δzeta=(1−2+1)n/b=0, (1+q)·ΔY−Δzeta=(2−3+1)n/b=0이며 energy 합은−e−In+(e+In)=0이다. 같은 pair가 모든 reservoir를 소유한다.

미제공 b는 null native projection을 남긴다. b와 eta fixture를 사용한 사상은 실제 finite physical state update가 아니다.

## 5. 몫 미분과 clock

고정 SI witness f, amplitude s≥0와 양수 b,τ에 대해 q=sf/(bτ),
dq=ds·f/(bτ)−s f db/(b²τ)−s f dτ/(bτ²).
τ=1은 integrated map, τ=ΔT는 proper bin average, τ=Δeta는 supplied eta bin average다. 평균 간에는 q_eta=(ΔT/Δeta)q_t가 성립한다. integrated event는 clock 불변이다. 공급되지 않은 source의 horizon 미분을 추정하지 않는다.

manufactured eta(T)=T/Tstar+(T/Tstar)²,Tstar=10^7s이면 Δeta=ΔT[1/Tstar+(T_a+T_b)/Tstar²]. 임의 endpoint H로 나누는 것은 이 finite-bin 변환과 다르다. Δeta 미제공 시 eta average는 null이다.

독립 divisor 방향은 dΔT=.17ΔT,dΔeta=−.09Δeta, db=.13b, s=.7,ds=.11이다. 양의 구간폭을 유지하는 FD 두 step2e−4,1e−4를 사용한다. 제조한 방향이지 physical history나 horizon sensitivity가 아니다.

## 6. 변하는 기준밀도의 endpoint 보정

X=s(F_b/b_b−F_a/b_a)
 =s(F_b−F_a)/b_b+sF_a(1/b_b−1/b_a).

마지막 항이 기준밀도 변화 보정이다. 전미분은
dX=ds(F_b/b_b−F_a/b_a)+s(F_a db_a/b_a²−F_b db_b/b_b²).

event 항의 미분과 correction 항의 미분을 더하면 이 식이 정확히 재현된다. 보정항 미분은 ds F_a(1/b_b−1/b_a)+sF_a(db_a/b_a²−db_b/b_b²)다. F_0=0만 검사하면 초기 기준밀도 항이 사라지므로 실제 양의 prefix를 가진 a=1,b=6도 검사한다.

이 endpoint state change는 미공급 ∫j(t)/b(t)dt와 같다고 가정하지 않는다. 기존 continuous convention dotr+3Hr=R_r,F_x=(S−xR_r)/r 및 전미분은 PR237 계약대로 보존한다.

