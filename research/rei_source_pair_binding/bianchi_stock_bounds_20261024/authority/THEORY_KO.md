# 주어진 Bianchi I 배경에서 질량 있는 collisionless 저장고의 모멘트 경계

작성: 2026-10-24. 단위: REI_BIANCHI_STOCK_BOUNDS_PREP.
판정 전 상태: ROOT_DERIVED / INDEPENDENT_REVIEW_PENDING / NUMERICAL_NOT_RUN.
이 문서는 다음 단위의 이론과 구현 계약이다. 이번 pressure 단일 child의 실행 결과와 별개다.

## 1. 질문과 입력

현재 승인된 HI summary-consumer는 한 redshift에서 주어진 표적당 주입률을 소비한다.
현재 pressure 단위는 유한 양의 측도의 N, U, L로부터 압력 모멘트의 구간을 구한다.
여기서는 이를 시간에 따른 저장고로 연결하기 전에 필요한 한 cohort의 자유 수송 경계를 유도한다.
실제 HI 주입 이력, 우주론 배경, 초기 저장고 또는 stopping model을 추정하여 채우지 않는다.

부호는 ds²=-c²dt²+Σ_i a_i(t)²(dx^i)², a_i>0인 대각 Bianchi I로 고정한다.
t는 공운동 관측자의 고유시간, p_i는 고정된 세 공간축을 따르는 정규직교틀의 물리 운동량이다.
유한 시간 구간에서 a_i는 C¹이다. 배경은 외부에서 주어진다.
입자는 질량 m>0, M=mc²>0이며 충돌, stopping, Lorentz force가 없는 geodesic 자유 수송만 따른다.
공간적으로 균질한 유한 양의 운동량 측도 ν_s는 시간 s의 물리 부피당 입자 수를 나타낸다.
등방성은 가정하지 않는다. 구현은 c가 이미 제거된 운동에너지 표현 k=√(M²+c²|p|²)-M을 쓴다.

주어진 모멘트는 N=∫dν_s, U=∫k dν_s, 0≤k≤L, 따라서 0≤U≤NL이다.
N의 단위는 number/physical-volume, U와 pressure trace mean의 단위는 energy/physical-volume,
M,L,k는 동일한 energy unit이다. 단위 변화나 부피·시간 계수는 코드가 암묵적으로 삽입하지 않는다.
유한 비음수 측도는 원자 측도를 허용한다. 매끄러운 분포만 허용할 경우 아래 원자 extremizer는 근사 극한이다.

## 2. 특성과 물리 부피

공간 평행이동 Killing 대칭에서 covariant momentum q_i=a_i(t)p_i(t)가 보존된다.
r_i=a_i(s)/a_i(t)>0, R=diag(r_1,r_2,r_3), D=r_1r_2r_3로 두면

p_i(t)=r_i p_i(s),    ν_t=D (T_R)_*ν_s,    N_t=DN,

여기서 T_R(p)=Rp이다. D는 좌표 부피를 고정했을 때의 물리 부피 비율이다.
측도에 D를 곱하는 것은 입자 수를 생성하는 것이 아니라 물리 부피당 밀도의 변환이다.

기초 문헌: Heinzle & Uggla, arXiv:gr-qc/0512031, §2 식(2d)–(3)은
질량 있는 Vlasov stress와 covariant momentum을 쓰는 균질 분포를 제시한다.
Dash & Jaiswal, arXiv:1711.07130, §V 식(32)–(35)도 같은 momentum characteristic을 설명하지만
그 논문의 명시적 massless pressure 식은 여기의 M>0 모멘트 식으로 채택하지 않는다.
이 문서의 유한 support/moment 경계는 아래 계산으로 직접 유도하며 문헌의 정리라고 주장하지 않는다.

## 3. 방향 불확실성을 포함한 단일 입자 경계

r_-=min_i r_i, r_+=max_i r_i이고
F_r(k)=√[M²+r² k(k+2M)]-M라 두면

F_{r_-}(k_s) ≤ k_t ≤ F_{r_+}(k_s),    0≤k_t≤L_t^*=F_{r_+}(L).

증명은 r_-²|p|²≤|Rp|²≤r_+²|p|²와 c²|p|²=k(k+2M)에서 따른다.
F_r는 k와 r에 대해 증가한다. S=√[M²+r²k(k+2M)]로 두면

F'_r(k)=r²(k+M)/S,
F''_r(k)=r²M²(1-r²)/S³.

따라서 0<r<1에서는 convex, r>1에서는 concave, r=1에서는 F_1(k)=k이다.
모든 방향이 팽창하거나 수축할 필요는 없다. r_-<1<r_+인 혼합 경우도 아래 식에 포함된다.

## 4. N,U,L만으로 정한 sharp 에너지 경계

N>0, L>0에 대해 μ=U/N라 하고

0<r≤1:
ell_r=N F_r(μ),       u_r=(U/L)F_r(L),

r≥1:
ell_r=(U/L)F_r(L),    u_r=N F_r(μ).

r=1에서 두 정의는 모두 U로 일치한다. Jensen 부등식과 [0,L] chord 부등식으로
ell_r≤∫F_r(k)dν_s≤u_r이다. 따라서

U_-^*=D ell_{r_-} ≤ U_t ≤ U_+^*=D u_{r_+}.

N=0이면 U=0이며 U_t=0이다. U=0 또는 L=0도 모든 입자의 운동에너지가 0이므로 U_t=0이다.
0으로 나누는 식을 평가하기 전에 이 경계를 처리한다.

Sharpness의 허용 집합은 N,U,L만 고정한 모든 양의 운동량 측도이다.
Jensen 쪽 등호는 k=μ에 모인 측도로, chord 쪽 등호는
(N-U/L)δ_0+(U/L)δ_L로 달성한다. 비영 운동량은 r_- 또는 r_+의 축에 정렬하고
+/- 방향에 절반씩 놓으면 평균 운동량도 0이다. 각 상·하한은 별도의 측도로 달성한다.
이 구성은 극값 축이 중복되어도 유효하다.
초기 angular isotropy를 추가로 요구한 더 작은 집합에 대해서는 경계의 유효성만 주장한다.
그 제한된 집합에서 sharp하다고 주장하지 않는다.

## 5. 압력 trace의 안전한 합성 경계

정규직교틀의 stress는
P_ij=∫c² p_i p_j/E dν_t, E=k+M이고 Π_t=Tr(P)/3이다.
각 입자의 trace kernel은
g(k)=c²|p|²/E=k(k+2M)/(k+M).
g''(k)=-2M²/(k+M)³<0이므로 이미 유도된 모멘트 식이 angular isotropy 없이 trace에 적용된다.

주어진 N_t,U_t,L_t에 대해

U_t(L_t+2M)/[3(L_t+M)] ≤ Π_t ≤
U_t(U_t+2MN_t)/[3(U_t+MN_t)].

왼쪽 계수는 L에 대해 감소하며, 오른쪽 함수는 U에 대해 증가한다.
따라서 실제 U_t,L_t를 몰라도 다음 외측 경계가 유효하다.

Π_- = U_-^*(L_t^*+2M)/[3(L_t^*+M)],
Π_+ = U_+^*(U_+^*+2MN_t)/[3(U_+^*+MN_t)].

N_t=0이면 두 값은 0이다. 이 합성 압력 경계는 보수적인 외측 구간이며 sharpness를 주장하지 않는다.
Π는 pressure tensor의 trace/3이다. 이 정의로 P_ij=Πδ_ij가 성립한다고 주장하지 않는다.

## 6. 에너지 보존과 shear work

H_i=dot(a_i)/a_i, θ=Σ_iH_i라 하면 dot(p_i)=-H_i p_i이고

dot(N)+θN=0,
dot(U)+θU+Σ_i H_i P_ii=0.

두 번째 식은 dot(k)=-Σ_i H_i c²p_i²/E와 물리 부피 변화에서 직접 얻어진다.
H_i=θ/3+σ_i, P_ij=Πδ_ij+π_ij로 분리하면

dot(U)+θ(U+Π)+Σ_i σ_i π_ii=0.

따라서 scalar Π만 주어졌다는 사실은 anisotropic work를 수치적으로 닫아 주지 않는다.
이는 명시적 항을 가진 보존식이며 새로운 strong no-go 또는 보편적 불가능성 주장으로 사용하지 않는다.
정지질량 에너지 MN은 전체 입자 에너지와 구별한다.
HI 원자에서 자유 전자로 재분류되는 정지질량을 기존 energy-source ledger에 새 에너지원처럼 더하지 않는다.

## 7. 양의 주입 cohort와의 조건부 연결

물리 부피당·고유시간당 운동량 주입 측도 I_s가 주어지고 적분 가능하다면,
초기 저장고 ν_0와 각 cohort를 선형 중첩하여

ν_t=D(t,t0)(T_{t,t0})_*ν_0
    + ∫_{t0}^t D(t,s)(T_{t,s})_*I_s ds

를 얻는다. 초기와 주입의 에너지 support와 moments가 주어지면 위 경계를 cohort별로 적분할 수 있다.
현재의 한 redshift HI rate card에는 시간 이력, 실제 표적 밀도, 초기 저장고, a_i(t)가 모두 들어 있지 않다.
여기서는 그러한 자료를 생성하거나 시간 quadrature를 실행하지 않는다.
Collision/stopping/thermal deposition을 이 자유 수송식에 포함했다고 주장하지 않는다.

## 8. 상쇄를 피하는 유리수 enclosure 알고리즘

입력 int, finite float, Fraction은 표현된 값 그대로 Fraction으로 옮긴다.
공급자 float에 들어오기 전에 잃은 정보는 이 절차로 복구하지 못한다.
k, M, r의 분수값을 사용해 x=r²k(k+2M)≥0, Q=M²+x로 둔다.
b는 정수 1..4096, 기본 128이며 input energy unit에서 sqrt의 절대격자를 정한다.
이 선택은 물리 정확도 허용오차나 기존 2e-12 gate를 변경하지 않는다.

Q=p/q≥0, s=2^b라 두고 n=isqrt(floor(p s²/q))를 계산한다.
sqrt(Q)의 enclosure는 [n/s,(n+1)/s]이다.
n²q=p s²이면 양 끝을 n/s로 합쳐 exact square를 보존한다.
정의에서 n²q≤p s²<(n+1)²q이므로 이 구간은 증명된 외측 경계이고 폭은 2^-b 이하이다.

작은 k에서 sqrt(Q)-M를 직접 빼는 대신

F_r(k)=x/(sqrt(Q)+M)

을 사용한다. sqrt enclosure [E_-,E_+]를
[x/(E_++M), x/(E_-+M)]로 옮기면 방향이 올바른 F enclosure를 얻는다.
x=0이면 exact 0, r=1이면 exact k를 반환한다.
x>0이고 M>0이면 Fraction의 lower endpoint도 엄밀히 양수이므로 최종 float underflow와 혼동하지 않는다.
이번 구현은 float 출력 자체를 하지 않는다.

실제 energy interval은 sharp lower bound enclosure의 아래 끝과 sharp upper bound enclosure의 위 끝을 취한다.
U_+는 추가로 N_t L_upper와의 min으로 줄일 수 있다.
압력 lower에는 U_lower와 L_upper를 사용하고, upper에는 U_upper와 N_t를 사용한다.
모멘트 정보 부족에 따른 구간폭과 sqrt enclosure의 계산폭은 별도 필드에 보존한다.

## 9. 판정·검증·현재 정지점

이론 독립 검토와 static code review를 받고 다음 정확한 유한 fixture를 준비한다:
identity, isotropic expansion, contraction, mixed axes, tiny k, zeros, invalid moments/ratios, common weight scaling.
정확한 radicals는 제곱 부등식으로 독립 확인할 수 있다. Decimal/CAS가 이 수학적 증명의 독립 심사를 대신하지 않는다.
현재 단일 pressure child release는 이 새 stock candidate의 실행을 포함하지 않는다.
새 stock 수치 결과, 실제 EOS, self-consistent Einstein evolution, L4 admission은 현재 없다.
미측정 원격/model/I/O 비용을 0으로 쓰지 않는다. 전체 모델 완료율은 null이다.

## 10. 출처와 이번 직접 유도의 경계

- Heinzle & Uggla, “Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations”,
  arXiv:gr-qc/0512031, https://arxiv.org/abs/gr-qc/0512031 ,
  https://arxiv.org/pdf/gr-qc/0512031 . 실제 읽은 범위: §2 식(2c)–(5), massive stress 및 covariant momenta.
- Dash & Jaiswal, “Metric anisotropies and emergent anisotropic hydrodynamics”,
  arXiv:1711.07130, Phys. Rev. D 97,104005 (2018),
  https://arxiv.org/abs/1711.07130 , https://arxiv.org/pdf/1711.07130 .
  실제 읽은 범위: §III의 massless convention과 §V의 characteristics.
- SciSpace는 이번 metadata 탐색으로 사용했다. 원문 식의 권위는 위 primary text와 직접 유도이다.
- Wolfram context는 호출되었으나 이 식의 검증 결과를 반환하지 않았다. evaluator 호출은 0이고 CAS proof로 표기하지 않는다.
- §§3–8의 유한 support/moment 경계와 enclosure는 이번 직접 유도이다. 새로움/최초성의 문헌 주장은 하지 않는다.

