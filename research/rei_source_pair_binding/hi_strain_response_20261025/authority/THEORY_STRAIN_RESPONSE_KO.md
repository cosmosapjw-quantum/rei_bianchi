# HI native 측도의 Bianchi I 순간 변형 응답

단위 `HI_NATIVE_STRAIN_RESPONSE_20261025`. Root Astra가 작성한 물리·수학 계약, 2026-10-25. 내장 physmath-research-loop 1.0.0의 R1–R10/C1–C10을 적용한다. 이전 massive-stress 루프의 plugin 1.3.0 기록은 당시 근거로 보존한다.

## 1. 대상과 선택

이미 채택한 HI/z=2.479의 4,368개 원자 측도에서, 초기 등방인 collisionless cohort의 순간 Bianchi I strain-to-stress 연산자와 질량·진폭 JVP를 구성한다. 이전 Science `42f5984a78f123ce26950cec0e0b8505da3e7ce4`, Documents `ecbb3124b49e75d8a7e948705b3894307d628349`의 W, S=∂W/∂M, A, K, support L 및 정수 dyadic enclosure를 재사용한다. 새로 적분할 native kernels는 R와 R_M 둘이다.

최신 조사에서 CR105의 조건부 spontaneous H1 RR, REC136의 same-source K_s 인증, BASS189의 angular endpoint/pressure-tail, HE101의 finite-M CBA, PHYS90의 conditional covariance consumer, VigilD5의 callback 결과를 읽었다. 실제 HI time/source/density/initial-stock/geometry binding은 선택 원문에서 공급되지 않았다. 그 입력을 임의로 선택하는 시간 진화 대신, 현재 native 측도로 결정되는 순간 응답을 이번 한정 작업으로 택한다. REC_HISTORY02의 별도 retarded-crossing/direction tangent 작업과 실제 owner reservation을 유지한다.

권위 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`, 진입 중앙 `8e946b46aa44581f09141184f193223277f2ec88`, AGENTS blob `429a5a13ee75b1222bc50627f8d5973d01dd21c4`. ANGTHERM02 branch/head `research/rei-coupled-isotope-contract-20261022 @ 8d10231b1f0f788164d5eadbe1bcee0b802cceca`는 읽기 전용이다.

## 2. Convention과 물리량

서명 (-,+,+,+), proper time, 물리 orthonormal frame을 쓴다. M=mc²>0, k≥0, E=k+M, q=c²|p|²=k(k+2M). c는 이 관계에 보존하며 새 c 수치를 삽입하지 않는다. ħ, k_B는 classical collisionless transport에 나타나지 않는다. 고정 원자 (k_i,w_i)는 CSV의 represented binary64를 exact rational로 읽는다. χ=represented 13.6 eV, ground HI, bath-rest target, zero recoil, no deposition 및 50000 eV photon endpoint는 선행 계약과 같다.

μ=Σ_i w_i δ_{k_i}, 각도는 명시적 초기 closure dΩ/(4π)이다. 저장 w는 target⁻¹ proper_s⁻¹이고 W,R,C는 eV target⁻¹ proper_s⁻¹, S,R_M,C_M는 target⁻¹ proper_s⁻¹이다. 아래 P는 이 source-weighted measure를 운반한 tensor이다. 실제 birth interval와 target density를 곱한 cohort에도 선형적으로 적용된다. 이번에 그러한 물리 진폭·birth history를 새로 채우지 않는다. δP/δε는 dimensionless strain에 대한 미분이라 P와 같은 단위다. Rest energy M A는 기존 kinetic/binding/UV energy ledger에 더하지 않는다.

대칭 실수 3×3 matrix B, 무차원 ε를 두고 A_ε=exp(-εB), D_ε=det A_ε=exp(-ε tr B), ν_ε=D_ε(A_ε)_*ν_0라 한다. Diagonal B는 Bianchi I의 각 축 log-scale 증분이고 일반 symmetric B는 회전한 frame에서의 동일 순간 연산자다. 특정 a_i(t)나 H_i(t)는 선택하지 않는다. 유한 strain family는 이 국소 미분과 remainder를 정의한다.

P(ε)=D_ε∫ c²(A_εp)(A_εp)^T/[M²+c²|A_εp|²]^(1/2) dν_0.

N(ε)=∫dν_ε, K(ε)=∫(E_ε-M)dν_ε. ν_0는 positive finite measure이며 아래 native 입력은 finite support다.

## 3. 구성적 유도

E'|_0=-c² p^T Bp/E. 직접 미분하면

δP=-(tr B)P_0-BP_0-P_0B+∫c⁴ pp^T(p^TBp)/E³ dν_0.  (1)

초기 등방의 angular identities는 ⟨n_i n_j⟩=δ_ij/3,
⟨n_i n_j n_a n_b⟩=(δ_ijδ_ab+δ_iaδ_jb+δ_ibδ_ja)/15다. 따라서

W=Σw q/E,   R=Σw q²/E³,   C=5W-R,

L_C(B):=δP=-(C/15)[(tr B)I+2B].  (2)

θ_B=tr B, B_tf=B-θ_B I/3이면 δp=-(C/9)θ_B, δπ=-(2C/15)B_tf다. κ=2C/15가 shear response 계수이다. P_0=(W/3)I, 초기 STF=0이지만 trace-free strain은 δπ를 만든다. 이는 순간 collisionless response이며 시간 비국소 정보를 가진 viscosity constitutive law를 도입하지 않는다.

같은 미분으로 δN=-θ_B A, δK=-θ_B(K+W/3). 초기 isotropy에서 shear의 kinetic work는 0이고, 생성된 anisotropic stress는 이후 work에 참여한다. W>0일 때 등방 압축의 순간 logarithmic slope Γ=C/(3W)는 δln p=Γ δln N를 준다. 이후 시간 전체에 Γ를 상수 closure로 사용하지 않는다.

## 4. 질량 미분과 물리적 범위

Fixed k,w에서

r=q²/E³=k²(k+2M)²/(k+M)³,
r_M=k²(k+2M)(k-2M)/(k+M)^4,
R_M=Σw r_M,  C_M=5S-R_M.  (3)

동일한 per-atom C의 도함수는

∂(5g-r)/∂M=k²(4k²+10kM+9M²)/(k+M)^4≥0.  (4)

M에 대한 방향 미분은 sensitivity parameter이며 변하는 전자 질량의 물리 가정이 아니다. β²=q/E²∈[0,1), r=gβ². 따라서 0≤R≤W, 4W≤C≤5W, 4/3≤Γ≤5/3. k≤L이면 β_L²=L(L+2M)/(L+M)²로 R≤β_L²W, C≥(5-β_L²)W이다. Native L<2M이면 r_M≤0이고 양의 k,w가 있으면 R_M<0. 식 (4)는 C_M≥0을 일반적으로 보인다.

비상대론적 극한 k/M→0에서는 R/W→0, Γ→5/3, κ→2W/3=2p. 초상대론적 극한 M/k→0에서는 R/W→1, Γ→4/3, κ→8W/15=8p/5다. C를 5W로 근사했을 때 exact C 대비 상대 과대평가는 R/C다. 이 비교에서는 이미 relativistic인 저장 W를 유지한다.

## 5. 진폭·질량·strain JVP

T(B)=(tr B)I+2B, Q=aX L_C(B), a,X≥0. 방향 da,dX,dM,dB는 signed finite이며 dB도 symmetric이다.

Jv=-(1/15){[(a dX+X da)C+aX dM C_M]T(B)+aX C T(dB)}.  (5)

모든 스칼라·matrix component를 represented rational로 다룬다. 정확한 products와 interval sums 후 binary64 endpoint 일치를 확인한다. 심한 cancellation은 fixed precision에서 unresolved를 반환할 수 있다. Matrix를 몰래 symmetrize하지 않는다. 기존 공개 API는 수정하지 않고 새 consumer API를 추가한다.

## 6. 유한 strain의 명시적 remainder

b=||B||_op, t=tr B, s=|ε|라 하자. 각 p의 tensor G_ε=D_ε c²p_εp_ε^T/E_ε와 ℓ=c²p_ε^TBp_ε/E_ε²에 대해

G'=-BG-GB+(ℓ-t)G,
ℓ'=-2u+2ℓ²,  u=c²p_ε^TB²p_ε/E_ε².

Cauchy와 c²|p|²/E²≤1로 ℓ²≤u≤b², |ℓ|≤b, |ℓ'|≤2b². Frobenius norm에서

||G'||_F≤(|t|+3b)||G||_F,
||G''||_F≤[(|t|+3b)²+2b²]||G||_F.

g(p)=c²|p|²/(M²+c²|p|²)^(1/2)는 |p|에 단조이고 |p_ε|≤exp(bs)|p_0|이다. λ=exp(bs)≥1에 대해 g(λp_0)≤λ²g(p_0)이므로 ||G_ε||_F≤exp((|t|+2b)s)g(p_0). Taylor integral remainder와 positive measure integration을 결합하면

||P(ε)-P_0-ε L_C(B)||_F
≤ ε²/2 [(|t|+3b)²+2b²] exp((|t|+2b)|ε|) W.  (6)

일반 positive measure에서도 (1)을 선형항으로 쓰면 같은 bound가 성립한다. Closed form (2)에만 초기 isotropy가 필요하다. 이 lemma는 finite angular fixture와 native infinitesimal coefficient의 해석을 잇고, 실제 geometry history를 대신하지 않는다.

## 7. 독립 hand/cubature 기준과 수치 계약

Hand atom (k,w)=(1,2), M=1에서 A=2,K=2,W=3,S=1/2,R=9/4,R_M=-3/8,C=51/4,C_M=23/8,κ=17/10,Γ=17/12. B=diag(1,-1,0)는 L=diag(-17/10,17/10,0), B_01=B_10=1/2는 L_01=-17/20, B=I는 L_ii=-17/4이다. a=2,X=3,da=-1,dX=2,dM=3,dB=diag(0,1,-1)에서 Q=diag(-51/5,51/5,0), Jv=diag(-43/5,-8/5,51/5)다. 이는 코드에서 독립 literal 기대값으로 쓴다.

14개 방향은 ±axes에 각 1/15, 8 cube vertices (±1,±1,±1)/√3에 각 3/40을 준다. 이 measure는 정확한 2차·4차 sphere moments를 갖는다. n_i n_j는 rational로 저장 가능하다. 따라서 hand strain derivative를 원래 tensor 미분 (1)으로 독립 확인할 수 있다. 이 14점이 유한 ε의 연속 sphere 적분 전체를 정확히 한다고 주장하지 않는다. Hand 14-ray finite transport의 Decimal100 exp/sqrt 계산에서 B=diag(1,-1,1/2), h=2^-8,2^-9,2^-10을 쓰고 centered derivative error가 h 반감마다 ≤0.3배인지, one-sided endpoint가 (6) 안에 있는지 확인한다.

Native R/R_M은 exact per-term rational과 선행 dynamic-scale outward dyadic integer accumulator P128/P160을 사용한다. 각 interval width≤Nδ, P160⊂P128, finite binary64 stable rounding을 확인한다. W/S는 저장된 nominal mass 문자열 `510998.95069` 행의 intervals를 그대로 쓴다. Decimal100의 새 독립 식은 E=k+M, b=M/E에서 r=E(1-b²)², r_M=(1-b²)[(1-b²)-4Mk/E²]다. 100자리 Decimal의 exact rational 해석값이 P160 안에 있고 float relative≤2e-15여야 한다. C/C_M 비교에는 저장 Decimal W/S를 재사용한다. 상대오차 기준과 원래 L0 gate 2e-12를 바꾸지 않는다.

## 8. 문헌, 검토, 종료

Heinzle & Uggla, arXiv:gr-qc/0512031, §2 eqs.2c–2f 및3의 covariant momentum 보존과 det(g)^(-1/2) stress 구조를 확인했다. 원전은 c=1이고 second fundamental form sign을 구분한다. Sarbach & Zannias, arXiv:1303.2899, eq.58의 stress 및 mean pressure와 현재 orthonormal-frame 정의를 대응시켰다. Exa/SciSpace로 Dash & Jaiswal arXiv:1711.07130 등 인접 문헌도 찾았다. 새 내용은 native HI input에 이 local response를 결속하고 certified numerical coefficient를 산출하는 것이며, 일반 kinetic stress identity의 최초 발견은 주장하지 않는다.

Wolfram algebra 확인은 별도 CAS 근거다. Fresh native Astra reviewer가 원문·이 유도·실제 code/diff/raw를 읽고 R6/C9를 수행한다. 새 no-go 정리는 제시하지 않는다. NG1–NG7 관점은 명제/조건/비자명 유도/실제 귀결/원전 비교/독립 심사의 범위를 확인하며, 입력 부재를 불가능성으로 바꾸지 않는다.

한 bounded child CPU6s/wall8s, render0, historical failed 10s sequence10.110448s와 overrun0.110448s를 보존한다. Known partial CPU before=11.160661s, whole L0 UNKNOWN_NOT_ZERO, original cumulative cap NOT_FROZEN, 원격 CAS·model·IO 비용은 별도 미측정이다. 이전22/66/83/ANG/NCP/nativeHI/massive-stress/stock/work/donor 재실행0. R1–R10/C1–C10의 현재 한정 결과를 독립 심사·채택·백업·allowed leaf 게시 후 종료한다. 전체 모델 완성도 null, L4_ready=false, C23E conditional D43K, HE94 partial window, PHYS85 historical state를 보존한다.
