# C1: 독립 전자구조 표현과 angular coupling 계산식

판정은 `ELECTRONIC_DISCRETIZATION_NOT_CONVERGED`다. 두 표현의 설계와 최소 구현은 고정했으나, 독립 spherical reference가 R=2 a_A의 사전 기준을 통과하지 못했다. 이 문서는 문헌 보고값을 전사한 해가 아니라 Cartesian Hamiltonian에서 유도한 식과 실행된 최소 계산을 구분한다. Nuclear repulsion은 전자 에너지에 넣지 않는다.

## 1. 문제·단위·위상

물리 문제는 H=−ℏ²∇²/(2m_e)−κ_A/r_A−κ_B/r_B, κ_B=2κ_A다. 길이 a_A=ℏ²/(m_eκ_A), 에너지 E_A=ℏ²/(m_ea_A²)를 먼저 고정한다. 이후 코드의 r,R,E는 이 단위로 무차원화했고, Z_A=1,Z_B=2다. 검증 fixture의 Z_A=0 또는 다른 charge도 이미 정한 단위를 바꾸지 않는다. 코드에서 핵 반발항 Z_AZ_B/R을 더하지 않는다.

원점 O는 charge center이며 z_A=−Z_B R/(Z_A+Z_B), z_B=Z_A R/(Z_A+Z_B). A→B를 +z, bright 방향을 x로 고정한다. 정확한 대상은 lowest m=0 g와 lowest real-cosφ |m|=1 b다. 실수 meridional amplitude G,A의 정확한 바닥상태를 양으로 택해

ψ_g=G/√(2π), ψ_b=A cosφ/√π, ∫ρ dρ dz G²=∫ρ dρ dz A²=1.

π_y는 A sinφ/√π다. 이것은 임의 near-degenerate rank-5 cluster의 개별 에너지 정렬과 다르다. 이번 코드의 대상은 고정 sector의 한 ground state이며, R-grid continuation은 아직 구현하지 않았다.

## 2. Prolate separation의 직접 유도

ξ=(r_A+r_B)/R, η=(r_A−r_B)/R로 정의하면 r_A=R(ξ+η)/2, r_B=R(ξ−η)/2이다. c=R/2, p=ξ²−1, q=1−η²라 두면

ρ=c√(pq), z_O=cξη+(Z_A−Z_B)R/[2(Z_A+Z_B)], dμ=ρdρdz=R³(ξ²−η²)dξdη/8.

ξ∈[1,∞), η∈[−1,1]이다. Laplacian의 meridional 부분은 4{∂ξp∂ξ+∂ηq∂η−m²/p−m²/q}/[R²(ξ²−η²)]다. Coulomb potential은 −2[(Z_A+Z_B)ξ+(Z_B−Z_A)η]/[R(ξ²−η²)]이다. Schrödinger 식에 R²(ξ²−η²)/2를 곱하고 G_m=NX(ξ)Y(η)를 대입하면

Aξ(E)=−∂ξ(p∂ξ)+m²/p−R(Z_A+Z_B)ξ−ER²ξ²/2,

Aη(E)=−∂η(q∂η)+m²/q−R(Z_B−Z_A)η+ER²η²/2,

AξX=λξX, AηY=ληY, F(E)=λξ(E)+λη(E)=0.

원전 P06 p.3의 인쇄된 η와 R 계수는 source note에서 결함으로 분리했다. 여기의 부호와 R 인자는 위 Cartesian 유도가 소유한다. 원전 프로그램에 같은 결함이 있다는 주장은 하지 않는다.

### 2.1 Endpoint factor와 weak form

μ=|m|, X=p^(μ/2)u, Y=q^(μ/2)v. Radial weight wξ=p^μ, angular weight wη=q^μ다. Kinetic bilinear forms는

kξ[u,v]=∫p^(μ+1)u′v′dξ−μ(μ+1)∫p^μuvdξ,

kη[u,v]=∫q^(μ+1)u′v′dη+μ(μ+1)∫q^μuvdη.

Charge/energy potentials는 해당 weight를 곱한다. 두 constant shift는 matching sum에서 상쇄되지만 각 축에서는 반드시 보존한다. Finite-energy regular branch를 conforming B-spline으로 근사한다. m=0은 축에서 finite, m=1은 ψ∝ρ다. 로그·negative-power singular branch는 이 form space에 없다. ξ=1,η=±1에 잘못된 Dirichlet zero를 추가하지 않는다. Coulomb 핵의 cusp는 point potential form으로 남겨 두며 임의 smoothing을 하지 않는다. m=0 local spherical average의 Kato cusp는 ∂r〈ψ〉=−Z_C〈ψ〉; higher local angular components의 Frobenius cusp와 단순 축 zero를 혼동하지 않는다.

바깥 ξ_max=1+2*radial_extent/R에서 radial endpoint coefficient 하나를 제거해 Dirichlet 조건을 둔다. 무한영역은 아직 유한 경계로 근사했으므로 extent의 독립 변화가 필요하다. Matrix는 일반 SPD overlap을 가진 Galerkin pair다. degree p, sector μ이면 polynomial matrix entry의 최대 차수 2p+2μ+2를 적분할 Gauss order≥p+μ+2를 요구한다. 이는 Coulomb force 적분의 정확도를 보장하지 않는다.

### 2.2 Matching·정규화·브래킷

각 축의 lowest regular eigenfunction을 선택한다. 1D weighted norm을 1로 두면 ∫X²dξ=∫Y²dη=1이며

N^−2=R³(〈ξ²〉−〈η²〉)/8, F′(E)=−R²(〈ξ²〉−〈η²〉)/2<0.

따라서 일차원 monotone matching을 쓴다. Sector hydrogenic n_min=μ+1에서 lower bound −(Z_A+Z_B)²/[2n_min²]는 kinetic energy를 Z_C/(Z_A+Z_B)로 분해하고 각 축방향 translated hydrogenic operator를 비교해 얻는다. Upper trial bound −max(Z_A,Z_B)²/[2n_min²]는 다른 중심의 attractive term을 버리지 않은 single-center trial로 얻는다. 구현의 작은 외향 padding은 유한 Galerkin/box root를 찾는 장치이며 certified energy interval이 아니다. Bracket가 없거나 norm≤0, F′≥0이면 예외로 종료한다.

Algebraic eigenresidual와 F(E)는 서로 다른 수치 잔차다. 둘이 작더라도 basis/tail 오차나 continuum gap을 인증하지 않는다. 이번 구현은 sector 내 두 번째 고윳값을 계산하지 않았다. 보고된 E_b−E_g는 서로 다른 sector의 전이 gap이며, 각 sector의 isolated spectral gap 인증이 아니다.

## 3. 독립 spherical partial-wave reference

Charge-center spherical coordinates r,η=z/r에서

G_m=Σ_{ℓ≥m}u_ℓ(r) A_{ℓm}(η)/r,

A_{ℓm}=√[(2ℓ+1)(ℓ−m)!/(2(ℓ+m)!)](−1)^m P_ℓ^m(η).

이 real convention에서 lowest ℓ=m amplitude가 양이고 ∫A_ℓm A_ℓ′m dη=δ_ℓℓ′, Σ∫u_ℓ²dr=1이다. Radial FEM form은

H_ℓℓ′=δ_ℓℓ′{(1/2)∫u′v′+ℓ(ℓ+1)∫uv/(2r²)}+Σ_L∫uv V_L(r) C_ℓℓ′L dr,

V_L(r)=−Σ_C Z_C sign(z_C)^L min(r,|z_C|)^L/max(r,|z_C|)^(L+1),

C_ℓℓ′L=∫A_ℓm A_ℓ′m P_L dη.

Center z_C=0에는 L=0 term만 −Z_C/r로 넣는다. Gaunt selection 때문에 L≤2ℓ_max면 유한 angular subspace에 대한 원래 Coulomb potential의 정확한 projection이다. 이것은 임의 multipole potential model truncation과 구분된다. Exact triangle/parity zeros를 assembly에 적용한다.

Radial element boundary에 |z_A|,|z_B|를 넣어 multipole kink를 분리한다. Lobatto interpolation node의 degree-p FEM이며, ordinary overintegrated Gauss integration을 사용해 DVR diagonal metric을 가정하지 않는다. u(0)=u(r_max)=0은 form-domain endpoint 조건이다. Higher-ℓ exact Frobenius power를 endpoint zero만으로 강제했다고 주장하지 않는다.

좌표·basis·assembly·eigensolver가 prolate lane과 독립이다. 그러나 off-center point cusp는 spherical 각방향으로 비해석적이므로 radial hp 증가만으로 reference가 수렴하지 않는다. ℓ, radial h/p, quadrature, outer radius를 따로 바꿔야 한다. Large R에서는 각해상도 비용이 커져 이 표현의 효율이 나빠질 수 있다. 이번 선택은 '검증 가능한 독립 reference 후보'이지 이미 고정밀 인증된 reference가 아니다.

Direct angular generator의 독립 식은

L_O/(−iℏ)=Σ_{ℓ≥1}√[ℓ(ℓ+1)/2] ∫u_{gℓ}u_{bℓ}dr.

이 lane은 force나 energy gap을 입력으로 사용하지 않는다. 동일 ℓ에서 y축 회전이 만드는 m=1→m=0 angular coefficient를 정확히 적용한다.

## 4. Direct·torque 두 연산자 lane

φ를 정확히 적분하면

L_O/(−iℏ)=(1/√2)∫dμ G{z_O(A_ρ+A/ρ)−ρA_z},

p_x/(−iℏ/a_A)=(1/√2)∫dμ G(A_ρ+A/ρ), d_x/a_A=(1/√2)∫dμ ρGA.

코드의 derivatives는 ξ,η에서 Cartesian으로 직접 변환한다. Jacobian entries는 ρξ=cξ√(q/p), ρη=−cη√(p/q), zξ=cη,zη=cξ이고 determinant는 c²(ξ²−η²)/√(pq)>0이다. 그러므로 Aρ=(zηAξ−zξAη)/det, Az=(−ρηAξ+ρξAη)/det다. Open Gauss node로 좌표 도함수 endpoint infinity를 직접 평가하지 않는다.

Torque lane은 derivative가 들어가지 않는 독립 force form을 적분한다:

T_C=(1/√2)∫dμ ρGA/r_C³, Δ=E_b−E_g>0,

L_O/(−iℏ)=[Z_AZ_B R/(Z_A+Z_B)](T_B−T_A)/Δ,

L_B/(−iℏ)=−Z_A R T_A/Δ.

B origin direct lane은 z_O를 z_Blocal=c(ξη−1)로 바꾼다. 검사할 identity는

L_O=L_B+[Z_A/(Z_A+Z_B)]R p_x, p_x=−im_eΔ_E d_x/ℏ.

Torque는 point-Coulomb form으로 취급한다. 각 핵의 corner u=ξ−1,v=1∓η 근방에서 m=1 factor를 포함한 meridional integrand는 uv/(u+v)² 정도여서 적분 가능하지만 방향에 따라 극한이 달라진다. 단순 polynomial exactness를 주장하지 않는다. 첫 radial cell과 양끝 angular cell을 두 triangle로 나누어 (u,v)=(hξ t,hη ts) 또는 (hξ ts,hη t), Jacobian hξhηt의 Duffy map을 적용한다. 나머지 cell은 composite Gauss다. q16과 q24를 따로 실행해 force quadrature 오차의 경험적 안정성을 검사했다. 이것은 Hardy/form 존재성과 수치 오차 인증을 구분하는 구현이다.

Dark π_y=0은 φ selection으로 정확히 소거된다. Equal charge에서는 G,A가 z-even이고 force difference 및 angular-generator integrand가 z-odd이므로 L_O=0이다. 이 두 성질은 이번에 algebraic fixture로 검사했고, equal-charge molecular eigensolve를 실행했다고 주장하지 않는다.

## 5. 수렴·spectral pollution·정량 인증의 경계

Bounded-domain conforming Ritz method의 exact integration과 positive metric은 min–max 구조를 보존한다. 실제 finite quadrature와 floating point에서는 matrix symmetry, metric norm, algebraic residual, nested basis/box 변화 및 서로 다른 표현을 함께 보아야 한다. Bound-state negative roots만 사용하며 discretized positive continuum root를 물리 bound state로 라벨링하지 않는다. 준연속 spectrum, resonances 또는 collision completeness를 이 코드로 인증하지 않는다.

Full-space residual η=||(H−E)ψ|| 또는 appropriate dual-form residual과 verified spectral gap γ가 실제 확보될 때에만 projector error에 η/γ 형태의 bound를 적용한다. Cusp 때문에 strong residual이 의미를 갖는 domain인지도 확인해야 한다. Discrete vector residual에 γ를 나누어 full-space bound처럼 쓰면 안 된다. 이번에는 continuum residual, rigorous gap, interval arithmetic을 구현/실행하지 않았다.

에너지, 파동함수, derivative, angular coupling, singular torque의 수렴은 별도 항목이다. 작은 energy error가 derivative accuracy를 보장하지 않는다는 실제 degree5 실패를 보존했다. Spherical ℓ12→18 비교는 radial grid/domain을 고정해 angular truncation의 미해결을 보였다. 남은 차이 전체가 angular error라는 증명은 아니다. Prolate base→refined는 mesh와 extent를 동시에 바꿨으므로 독립 tail-error 측정이 아니다.

## 6. 실제 실행된 결과

`NUMERICAL_CONTRACT.json`은 root의 two-center pilot 전에 고정했다. H/He 물리점은 R=2 하나뿐이며 prolate 2개 설정×2 sector와 spherical 3개 설정×2 sector, 총 10개 state solve였다. Main driver wall time은 약 7.071초, exit 0이다.

| 표현 | E_g/E_A | E_b/E_A | L_O/(−iℏ) |
|---|---:|---:|---:|
| prolate base | −2.512193016590182 | −0.899646912169362 | 0.340977757757635 |
| prolate refined | −2.512193016591858 | −0.899646912168827 | 0.340977757757509 |
| spherical ℓ_max=8 | −2.501124436077967 | −0.899623172685227 | 0.340155498165601 |
| spherical ℓ_max=12 | −2.508315112366040 | −0.899643444338485 | 0.340719719764850 |
| spherical ℓ_max=18 | −2.510909118978587 | −0.899646404343223 | 0.340895785708762 |

Refined prolate direct/torque O 차이=7.44×10^−13, B 차이=1.23×10^−13, momentum commutator 차이=9.89×10^−13, origin identity 차이=4.44×10^−16, q16→24 force 차이=1.04×10^−11이다. 이 숫자는 같은 근사 state에서 서로 다른 연산자를 평가한 consistency evidence다.

독립 spherical ℓ18과 prolate의 E_g 차이는 1.28390×10^−3 E_A, L 차이는 8.19720×10^−5ℏ이다. 사전 기준 각각 10^−5를 넘는다. E_b 차이 5.07826×10^−7 E_A는 energy 기준 안이지만 전체 pair의 수렴을 닫지 못한다. 따라서 `electronic_discretization_converged=false`, C2 broad audit는 미실행이다. Method disagreement를 Gaussian error bar로 바꾸지 않는다.

새 focused checks는 spherical 6개, 최종 prolate 4개, coupling-specific analytic/failure 4개가 PASS다. 마지막 coupling check는 known hydrogenic wavefunction fixture로 direct/dipole/momentum/origin operator를 검사하여 이미 끝난 eigensolve를 반복하지 않았다. 입출력 보호의 I/O-only regression도 PASS다. Degree5 failure와 출력 capture 회복 기록은 삭제하지 않았다.

## 7. 설계만 준비한 다음 검증

R-grid에서 각 sector의 candidate subspace를 구한 뒤, 공통 Cartesian measure에서 cross-overlap을 평가한다. Isolated state는 maximal overlap과 positive overlap phase를 함께 사용하고, spectral separation과 residual이 부족하면 label을 보류한다. Rank-k cluster의 old/new orthonormal bases overlap S=UΣV†에는 polar/Procrustes transport VU†를 적용한다. 작은 singular value, rank 변화, 다른 threshold 유입은 cluster enlargement 또는 STOP 사유다. 서로 다른 basis의 coefficient dot product를 physical overlap으로 쓰지 않는다. H1s+He n2 rank5와 bright fixed-m branch를 섞지 않는다. 실제 continuation 구현·실행은 `NOT_RUN`이다.

A2의 scaled sequences는 후속 C2 계약에만 준비했다: x→0에서 iL_O/(ℏx³)→4√2/15, x→∞에서 iL_O/(ℏx)→32√2/243, −iL_B/(ℏx^−2)→128√2/729. 각 x에서 spatial error를 먼저 감소시키고 그 다음 asymptotic parameter sequence를 비교한다. Small-R에서는 raw absolute error가 작다는 이유로 cubic coefficient를 통과시키지 않는다. A2 remainder constants/radii는 계산하지 않았으므로 tolerance의 근거로 사용하지 않는다.

UA energies −9/[2n²], B-local large-R E≈−4/[2n²]−1/R, H-local E≈−1/[2n²]−2/R의 threshold/detuning을 보존한다. Quadrupole와 degenerate dipole block은 A2 원문을 재사용한다. Global energy sorting은 branch tracking을 대체하지 않는다. Hellmann–Feynman ∂RE=〈∂RH〉는 isolated differentiable normalized eigenbranch의 continuum identity다. Moving finite basis의 Pulay term, moving box/domain term을 무시하지 않는다. Fixed nuclei를 함께 scale하는 molecular virial은 2〈T〉+〈V〉+R∂RE=0이며 atomic 2T+V=0을 유한 R에 강제하지 않는다. 이 derivative/virial, large-R sequence, asymptotic scale 검사는 이번에 준비만 했다.

Cache identity에는 exact float R의 hex/byte representation, charges, convention, origin/frame, state sector, basis/grid/quadrature/box, solver tolerance, code/dependency SHA, source commit, phase/cluster policy를 모두 넣는다. Arbitrary rounded-R key는 금지한다. Persistent electronic cache는 아직 없다. Final result writer는 create-only atomic link, fsync와 SHA를 사용한다. 실행된 초기 driver와 postpilot I/O 수정본의 identity를 분리했다. 물리 결과를 다시 실행하지 않고 임시 경로의 I/O 실패 검사만 했다.

## 8. 단일 다음 dependency

다음은 `C1b_INDEPENDENT_REFERENCE_CONVERGENCE`다. 같은 R=2에서 reference의 ℓ 증가와 radial h/p·quadrature·tail을 분리해 최소한 현재 기준을 충족하는지 판정한다. 비용이 과도하면 cusp-adapted independent representation을 연구 스레드에서 유도·검토한 뒤 교체할 수 있으나, efficient lane의 tolerance만 바꾼 복제본을 reference로 부르지 않는다. C1b가 닫히기 전 broad C2 R-grid, collision propagation, Eq55는 실행하지 않는다.

Gate는 CODE_I02_CLOSED=true, full_certificate_fail_closed=true, scientific_PROMOTE=HOLD, Eq55_next_node_authorized=false, Eq55=NOT_RUN, production_default_change=NOT_AUTHORIZED를 유지한다.
