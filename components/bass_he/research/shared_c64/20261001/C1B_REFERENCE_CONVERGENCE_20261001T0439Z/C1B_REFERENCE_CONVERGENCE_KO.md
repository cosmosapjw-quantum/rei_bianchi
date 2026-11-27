# C1b: 한 지점 독립 reference 수렴

**C1B_R2_REFERENCE_CONVERGENCE_CLOSED.** R=2a_A에서 두 fixed-sector energy와 물리적 charge-center angular coupling의 사전 수치 기준을 충족했다. 이는 독립 이산화와 시험한 refinement에 근거한 경험적 수렴 판정이다. Continuum error enclosure, R 전역 정확도, collision observable 또는 production readiness의 인증은 아니다.

## 1. 입력과 변경 범위

Parent는 C1 commit `75470153f0883765cf41dd92011206aba8ac988b`다. A1/A1b의 frame·channel 정식화와 A2 asymptotics는 그대로 재사용했다. C1의 실패한 O-centered spherical reference ℓ_max=18과 prolate 결과도 삭제하거나 재실행하지 않았다. 새 O-centered ℓ_max=24 한 쌍으로 기존 추세를 확인한 뒤, B-centered spherical representation을 구현했다. 원 Hamiltonian, 전하, 물리적 관측량 원점, 위상, 단위는 변경하지 않았다.

H=−ℏ²∇²/(2m_e)−κ_A/r_A−κ_B/r_B, κ_B=2κ_A. a_A=ℏ²/(m_eκ_A), E_A=ℏ²/(m_ea_A²)이며 코드에서는 이 단위를 정한 뒤 무차원화했다. Fixture의 Z_A=0도 이미 정한 단위를 바꾸지 않는다. Nuclear repulsion은 전자 에너지에 포함하지 않는다. g는 lowest m=0, b는 lowest real-cosφ |m|=1이고 exact meridional amplitudes의 positive phase를 따른다.

ψ_g=G/√(2π), ψ_b=A cosφ/√π, ∫ρdρdz G²=∫ρdρdz A²=1.

이번 산출물은 채팅 연구 환경에서 작성·실행한 새 연구 파일이다. Production source와 이전 연구 namespace는 변경하지 않는다.

## 2. 전개 중심의 변경과 관측량 보존

O는 charge center, z_B=Z_A R/(Z_A+Z_B)다. B를 수치 구면좌표 원점으로 놓으면 핵 위치는 (z_A,z_B)=(-R,0)이고, r=r_B, η=(z_O−z_B)/r이다. 축방향 평행이동이므로 m sector와 azimuth convention은 같다. 물리적 angular generator는

L_y(O)=L_y(B)+z_B p_x.

즉 전개 중심의 선택이 물리적 L_y 원점의 선택을 바꾸지 않는다. B의 강한 Coulomb cusp는 중앙 radial channel에 들어가지만, A의 off-center cusp는 r=R,η=−1에 남는다. 따라서 이 변경만으로 exponential ℓ convergence를 주장하지 않는다. 실제로 같은 ℓ=24에서 에너지 정확도는 크게 개선되었지만 L_O의 오차는 O-centered 결과보다 컸다. 최종 통과는 중심 변경·효율적인 assembly·충분한 angular refinement를 함께 사용한 결과다.

Finite spherical expansion은

G_m=Σ_{ℓ=m}^{ℓmax}u_ℓ(r)A_ℓm(η)/r,
A_ℓm=√[(2ℓ+1)(ℓ−m)!/(2(ℓ+m)!)](−1)^mP_ℓ^m.

C1의 radial hp Galerkin form과 정확한 finite angular projection을 유지한다. V_L=−Σ_C Z_C sign(a_C^(num))^L r_<^L/r_>^(L+1), a_C^(num)=(−R,0)이며, 중앙 B에는 L=0의 −Z_B/r만 넣는다. Angular Gaunt selection에서 L≤2ℓmax면 유한 trial space에 대한 원 Coulomb potential의 정확한 projection이다. 전하 softening이나 benchmark fit은 없다. r=R을 radial element boundary로 넣는다.

변경 구현은 element-local COO array를 vectorize하여 Python scalar list의 비용을 줄였다. 수학적 bilinear form은 그대로다. First two Ritz roots를 같은 fixed-m sector에서 구하고 lowest state를 선택한다. 다른 R 사이의 energy sorting이나 near-degenerate cluster tracking은 수행하지 않는다.

## 3. 독립 direct momentum과 원점 변환

q=1−η², g의 angular index ℓ, b의 index k라 두면

C_ℓk=∫A_ℓ0√q A_k1 dη,
D_ℓk=∫A_ℓ0(−η√q A′_k1+A_k1/√q)dη.

Cartesian derivative를 직접 변환해 얻는 식은

p_x/(−iℏ/a_A)=(1/√2)Σ_ℓk[C_ℓk∫u_gℓu′_bk dr+(D_ℓk−C_ℓk)∫u_gℓu_bk/r dr],

d_x/a_A=(1/√2)Σ_ℓk C_ℓk∫r u_gℓu_bk dr.

두 식은 eigenenergy·gap·force 값을 사용하지 않는다. Angular coefficient는 |ℓ−k|=1만 살아남고 finite polynomial Gauss integration으로 계산한다. 독립 수학 검토에서 얻은 닫힌 계수는

a_k=√[k(k+1)/((2k−1)(2k+1))], b_k=√[k(k+1)/((2k+1)(2k+3))],

p̄=(1/√2)Σ_k{a_k∫u_g,k−1(u′_bk+k u_bk/r)dr−b_k∫u_g,k+1(u′_bk−(k+1)u_bk/r)dr}.

Local generator는 C1의 exact angular algebra를 유지한다:

L̄_B=L_B/(−iℏ)=Σ_{ℓ≥1}√[ℓ(ℓ+1)/2]∫u_gℓu_bℓ dr,
L̄_O=L̄_B+[Z_A R/(Z_A+Z_B)]p̄.

Δ=(E_b−E_g)/E_A에 대한 p̄=Δd̄는 별도로 검사하는 continuum identity다. 이를 momentum의 정의로 사용하지 않았다.

## 4. 핵 특이 force의 유한 angular moment 유도

T_C=(1/√2)∫drdη,r u_gℓu_bk A_ℓ0A_k1√q/r_C³를 합산한다. 물리 T_C는 a_A^−2 단위이며 코드 값은 무차원이다. Q_ℓk=A_ℓ0A_k1√q라 놓으면 Q는 polynomial이고 deg Q′≤ℓ+k다.

Signed nuclear position a_C≠0에서 unit-charge potential W_C=−1/r_C를 쓰면 ∂ηW_C=−a_C r/r_C³이므로

T_C=(1/(√2a_C))Σ_ℓk∫u_gℓu_bk dr ∫Q′_ℓk W_C dη.

Boundary term QW_C는 양끝에서 0이다. r=|a_C|의 cusp에서도 Q가 선형으로 소거되고 W_C가 inverse square root이므로 곱은 0으로 간다. 따라서 각방향 singular integrand를 직접 샘플링하지 않고, degree≤2ℓmax의 정확한 Legendre moments로 처리할 수 있다. Radial kink는 element boundary에서 분리하고 Gauss order14/22/30을 독립 비교한다.

a_C=0이면 나누기를 연장하지 않고

T_0=(1/√2)Σ_ℓk C_ℓk∫u_gℓu_bk/r² dr

를 사용한다. Unit-charge W를 사용한 이유는 Z_C=0인 fixture에서도 geometric T_C 자체는 정의되기 때문이다. 초기 코드는 charged V를 Z_C로 나누어 이 edge case에서 0/0 위험이 있었다. 실행된 초기 bytes를 보존한 뒤 unit-charge 표현으로 수정했고 신규 회귀검사로 확인했다. 실제 R=2,Z_A=1,Z_B=2 결과는 영향을 받지 않는다.

Torque observable은 별도의 force integrals를 계산한 다음에만 gap을 사용한다:

L̄_O=[Z_AZ_B R/(Z_A+Z_B)](T_B−T_A)/Δ,
L̄_B=−Z_A R T_A/Δ,
p̄_force=(Z_A T_A+Z_B T_B)/Δ.

이 lane은 state 값과 potential moments를 사용하므로 direct derivatives와 다르지만, Hamiltonian assembly와 potential projection을 공유한다. 특히 common ℓ cutoff의 L_B는 Galerkin subspace를 보존하므로 그 direct/torque identity가 finite projection 안에서 이미 강제될 수 있다. 따라서 L_B 두 식이 기계 정밀도로 일치한다는 사실을 독립 state convergence 증거로 세지 않았다. L_O의 momentum translation, separate refinements와 prolate cross-representation 비교가 필요하다.

## 5. 유한 경계와 residual/gap의 범위

B-centered Dirichlet 구에서 L_B는 boundary에 접하지만 p_x는 그렇지 않다. 실수 normalized full states의 finite-box surface term은

L̄_O−L̄_O,torque = z_B/(2Δ)∮n_x(∂_nψ_g)(∂_nψ_b)dS

이며 여기 z_B,Δ와 적분은 무차원 computational units다. 코드에서 boundary derivative를 측정했다. Selected state의 항은 극히 작고, box24→32 변화에서도 관측량이 안정적이었다. 이 경험적 관찰을 continuum 경계항의 엄밀한 상계로 부르지 않는다. xψ_b는 Dirichlet 조건을 보존하므로 position commutator p̄=Δd̄의 domain 문제와 구분한다.

두 번째 Ritz root로 측정한 same-sector gaps는 약 1.16701910 E_A (m=0), 0.38703434 E_A (m=1)다. 이는 유한 행렬의 empirical isolation 진단이다. Exact continuum isolation gap, strong/dual PDE residual enclosure, interval arithmetic은 계산하지 않았다. Algebraic residual을 continuum residual로 대체하지 않는다. R-grid continuation·cluster phase transport도 NOT_RUN이다.

## 6. 사전 계약과 한 번의 실행 범위 수정

첫 `NUMERICAL_CONTRACT.json`은 모든 새 physical run 전에 작성했다. Cross-representation energy/L 기준은 각각 10^−5, angular/radial/box refinement 기준은 2×10^−6, O direct/torque 및 momentum commutator는 10^−7, force quadrature는 10^−8이다. C1 기준을 사후 완화하지 않았다.

초기 angular cap40에서는 L 비교가 실패했다. 이 실패를 그대로 남겼다. Vectorized reference의 실제 l40 실행이 1.116초·210,836 KiB였으므로 기존 전체14 pair/600초/4GiB envelope 내에서 l72,l96 두 수준을 추가하는 **단 한 번의 operational amendment**를 새 실행 전에 기록했다. 선택한 두 수준의 각해상도 비는4/3이며, 실제 값의 변화를 판정에 사용했다. Fitting이나 extrapolated limit는 사용하지 않았다. Cap96 이후 추가 연장은 하지 않았다.

전체 R=2 target-state solve는14쌍=28개이고, B-centered12쌍에서는 각 sector의 second Ritz root24개를 추가 계산했다. 수치 eigensolve와 operator 평가 시간의 합은 약52.60초다. 기록된 최대 RSS1,206,608 KiB는 spherical drivers의 관측치다. 실행된 prolate-tail driver에는 RSS/4GiB limit 계측이 없었으므로 전체 node peak 또는 모든 child의 cap enforcement를 주장하지 않는다. 실행 원본을 보존하고 전달용 driver에 향후 resource limit/measurement만 추가했으며 물리 계산을 반복하지 않았다.

## 7. 실제 수렴 결과

Reference는 B-centered l96, radial56, degree4, rmax24, Hamiltonian q14다. 아래 raw numbers의 많은 자릿수는 재현용이며 그만큼의 continuum accuracy를 뜻하지 않는다.

| 표현 | E_g/E_A | E_b/E_A | L_O/(−iℏ) | prolate 대비 L 차이 |
|---|---:|---:|---:|---:|
| 기존 prolate refined | −2.512193016591858 | −0.899646912168827 | 0.340977757757509 | — |
| O-centered l24 | −2.511620468261219 | −0.899646784025171 | 0.340941708840082 | 3.605×10^−5 |
| B-centered l24 | −2.512177188087986 | −0.899646454262561 | 0.341038183811235 | 6.043×10^−5 |
| B-centered l40 | −2.512189281186453 | −0.899646873019235 | 0.340991912899296 | 1.416×10^−5 |
| B-centered l72 | −2.512192337874424 | −0.899646909957271 | 0.340980322028394 | 2.564×10^−6 |
| B-centered l96 | −2.512192723447947 | −0.899646911631157 | 0.340978864689074 | 1.107×10^−6 |

Selected independent energy differences는 (2.9314×10^−7,5.3767×10^−10)E_A다. Angular l72→96에서 energy increments는 (3.8557×10^−7,1.6739×10^−9)E_A이고 L increment는1.4573×10^−6ℏ이다.

| 별도 refinement | max energy 변화/E_A | L_O 변화/ℏ |
|---|---:|---:|
| radial elements56→80 | 3.26×10^−10 | 1.36×10^−9 |
| degree4→5, 동일 mesh/q | 2.45×10^−9 | 9.36×10^−9 |
| Hamiltonian q14→22 | 1.59×10^−13 | 3.79×10^−14 |
| B sphere radius24→32, 기존 내부 element 보존 | 5.33×10^−15 | 2.00×10^−15 |
| Prolate extent30→40, 기존 내부 knots 보존 | 7.26×10^−12 | 3.29×10^−13 |

Prolate extension은 옛 outer clamping 근방의 basis support를 바꾼다. '내부 knots 보존'과 '모든 basis function 불변'은 다르다. 두 tail checks는 기존 C1의 mesh·extent 동시 변화와 달리 내부 grid를 유지했다.

Selected O direct/torque 차이는7.21×10^−11ℏ, momentum commutator residual은6.90×10^−10(ℏ/a_A), force q22→30 변화는1.67×10^−16ℏ이다. Separate h/p/q/box 설정에서도 모든 해당 기준을 통과했다.

State 변화도 energy와 별개로 기록했다. l72→96의 L² increments는 g≈1.9883×10^−5, b≈1.3643×10^−6이다. Radial h/p 변화의 g increment는8.04×10^−7 이하, b는3.74×10^−8 이하이다. Stable direct squared-difference integration을 사용했으며, 2−2overlap subtraction으로 생기는 √ε floor는 별도 precision note에 기록했다. 이 값도 discrete state 간 차이이며 exact state error bound가 아니다.

## 8. 구현 검증·실패 기록·claim gate

변경된 origin, direct operator, explicit mesh, two-root interface, invalid input seam의 신규5개 검사가 PASS였다. Force angular moments는 원래 point-force integrand를 off-center 핵 반경의 안팎 smooth radii에서 직접 적분한 값과 비교했고, central selection·zero-charge geometry를 포함한3개 검사가 PASS였다. 이전에 닫힌 atomic suites는 재실행하지 않았다.

독립 reviewer가 확인한 I/O seam은 실행 원본을 보존한 뒤 수정했다. Focused test runner는 이제 기존 출력이 있으면 setup/solve 전에 거부하고 atomic create-only JSON을 쓴다. Cached state NPZ는 사용 전에 size/SHA/origin/grid identity를 검사한다. Same-length tamper rejection과 기존 출력 불변 검사는 physical solve 없이 통과했다. Positive-charge numerical results의 코드 identity와 수정 후 delivered bytes를 구분한다.

`electronic_discretization_converged=true`의 scope는 **R=2에서 이번에 명시한 empirical energy/coupling criteria**뿐이다. C1의 전체 R-grid numerical validation, six-channel accuracy, continuum completeness 또는 collision observables를 닫지 않는다. `full_certificate_fail_closed=true`, `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다.

다음 단일 node는 **C2_FINITE_R_COUPLING_NUMERICAL_AUDIT**다. 첫 단계는 이번 reference를 바탕으로 R-grid·continuation·scaled asymptotic acceptance의 구체적 실행 계약을 고정하는 일이다. 이번 turn에서 C2 physical R-grid를 실행하지 않았다.
