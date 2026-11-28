# R10P 유한-R ground–π 회전 행렬원소: 제한된 원문·식 검토

## 판정

`SYMMETRY_ALLOWED_ONLY__MATRIX_ELEMENT_UNESTABLISHED`.

He–H의 유한-R 축대칭 Hamiltonian에서 collision-plane bright π와 σ 사이의 L_y 행렬원소는 검토한 exact symmetry로 배제되지 않는다. 그러나 이 패키지와 제한된 원문은 지정된 두 exact eigenstate의 overlap이 실제 nonzero임을 입증하지 않는다. noncentral torque operator의 존재, S1의 잠정적 경로 설명, UA 블록 밖이라는 사실만으로 nonzero를 선언하지 않는다. dark π는 아래 convention에서 반사대칭으로 제외된다. 이는 bright 후보 전체를 배제하는 판정이 아니다.

새 단면적·효과 크기·leading R power는 계산하거나 추정하지 않았다. 4620배 discrepancy 해결, REAL/EXTENDED 선택 또는 production 승인은 없다.

## 1. 입력과 source binding

R10O 전체 ZIP SHA256=f6723d62f8ad84b6633d4d0653635aef0618e455aadf65a7fb840e065f4d23e6, 35209 bytes. Dropbox 실제 회수 후 CRC PASS, 18 members 중 MANIFEST 외 17 payload의 size/SHA256가 모두 일치했다. GitHub 문서 subset을 전체 패키지로 취급하지 않았다.

Scientific source HEAD=1a83a67e12de1ddc2aede0ff67168f7071450ab3, tree=230904af1337df1b86976c54a303d41db8ab7d96. Fresh publication HEAD=3c55c90081118646cc6d5ac9e347b67f7be7355f, tree=d23a245c23420b429aa3d8f7c1c97359fc140c44. 그 사이 차이는 R10O START_HERE 문서 하나이며 관련 scientific dependency 변화는 없었다. 새 detached worktree를 사용했다.

R10G audit_support.py 3491 bytes, blob=39d5e923e6e8e779e83f1dc002d80e4c4562e3c2, SHA256=a62978c7637cec519c619aa225b062e18ad71248ec5674f0b392c0708498a970를 pinned Git 바이트와 대조했다. 이 source는 import/execute하지 않았다. 현재 rotor의 N,l 블록 제한도 원문과 source를 읽어 확인했다.

R10N NEW_AUTHORITY_NOT_COMPARABLE, PHYSICAL_SUPPORT_UNRESOLVED 및 R10M closure는 상속한다. R10O 입력에는 네 원 CSV와 사용자 /tmp 원 보고서가 없다. 해당 실행을 USER_REPORTED_EXECUTION에서 새 byte 검증으로 승격하지 않았다. R10O graph CAS와 과거 scientific suite도 재실행하지 않았다.

## 2. 실제 읽은 primary source

**S1** Stolterfoht et al., PRA81,052704(2010), pp.3,5,6,8을 private PDF에서 fresh-read했다. p.3은 rotational Δm=±1과 radial Δm=0을 구별한다. pp.5–6의 n=1 해석과 p.8 hump 설명에는 잠정성이 남아 있다. 특히 p.6은 직접 2pσ–1sσ radial 경로 뒤에 2pσ–2pπ–1sσ를 추가 가능성으로 제시한다. 이 범위에는 이번 origin/ETF convention에 맞는 특정 finite-R 행렬원소 식이나 nonzero overlap 증명이 없다. [DOI](https://doi.org/10.1103/PhysRevA.81.052704)

**CPC** Gusev et al., CPC286,108662(2023), Sec.2.6 pp.11–12 Eq.(47)–(50)을 확인했다. 작은 R에서 같은 UA principal N 및 l을 가진 상태의 분열과 2l+1 회전 공간을 사용하는 근사다. Eq.(47)의 normal-axis even/odd projection 선택규칙은 이 표현의 규칙이며 ground–π를 유한-R 전체 공간에서 금지하는 정리가 아니다. Eq.(49)–(50)의 확률 조립 역시 UA label을 사용한다. 문서의 다른 페이지를 context로 읽었으나 Eq55를 계산하거나 실행하지 않았다. [DOI](https://doi.org/10.1016/j.cpc.2023.108662)

S1 refs24/25는 각 한 번의 APS fulltext 회수를 시도했으나 HTTP401이었다. 원문을 읽지 못했으므로 제목·초록에서 행렬원소나 leading power를 추정하지 않는다. 이는 추가 authority의 공백이며, 이미 읽은 S1/CPC의 제한된 symmetry 결론을 nonzero 판정으로 바꾸지 않는다. PDF와 긴 원문 추출 텍스트는 공개 배포하지 않고 size/SHA256/페이지 metadata만 남긴다.

## 3. Convention과 exact symmetry

분자축 z, 충돌평면 xz, 회전축 y를 사용한다. 원점은 audit 선언인 순간 nuclear charge center O=(Z1 R1+Z2 R2)/(Z1+Z2), Z1=1,Z2=2이다. z1=-Z2 R/(Z1+Z2), z2=Z1 R/(Z1+Z2). 이는 CPC Sec.2.6의 원점/ETF를 새로 확정한 주장이 아니다.

전자 snapshot은 unboosted clamped-nuclei eigenstate다. L_y=-iℏ(z∂x-x∂z), U(θ)=exp(-iθL_y/ℏ). 움직이는 O의 병진 connection 및 ETF는 이 angular overlap에 포함하지 않는다. 원점 이동 a에 대해 L_(O+a)=L_O-a×p이므로 bare angular matrix만으로 물리적 missing-edge amplitude를 확정할 수 없다.

He–H는 heteronuclear이므로 homonuclear inversion g/u rule을 가정하지 않는다. y→-y 반사에서 σ와 π_x는 even, π_y는 odd이며 L_y는 even이다. 따라서 <σ|L_y|π_y>=0, bright <σ|L_y|π_x>는 이 반사로 소거되지 않는다. |Λ|=0→1은 angular operator의 허용 sector다. 허용은 특정 overlap nonzero의 충분조건이 아니다.

UA R=0에서 H_e는 구면대칭이고 L_y는 orbital-l sector를 보존한다. UA1s(l=0)↔UA2p(l=1)는 0이다. 유한-R exact eigenstate에 UA의 정확한 l을 부여하여 이 0을 그대로 적용하지 않는다. 선택된 상태가 UA limits로 접근하고 L_y domain을 통제하는 convergence가 있으면 off-block limit도 0이다. L2 norm continuity만으로 unbounded operator의 행렬원소 극한을 입증했다고 하지 않는다. 그 convergence 증명과 감소 속도/leading R power는 미확립이다.

## 4. 전달된 operator의 overlap 검산

여기서 ρ는 **전자 transverse radius**이며 collision impact parameter가 아니다. x=ρcosφ, y=ρsinφ로 놓고

σ=G(ρ,z)/√(2π), π_x=A(ρ,z)cosφ/√π, π_y=A(ρ,z)sinφ/√π,

∫ρ dρ dz |G|²=∫ρ dρ dz |A|²=1로 정규화한다. 이는 exact eigenfunction을 구한 것이 아니라, 전달된 L_y에 축대칭 orbital form을 대입한 경량 식 검산이다.

ℒ_g,bright= -iℏ/√2 ∫ρ dρ dz G* [ z(∂ρA+A/ρ)-ρ∂zA ].

ℒ_g,dark=0.

CAS는 φ 적분과 √2 factor, dark cancellation을 확인했다. radial/z 적분은 수행하지 않았고 G,A가 실제 해당 eigenstate라는 새 numerical/analytic authority도 얻지 않았다. 따라서 이 식은 판정할 quantity의 정의이지 nonzero의 증명은 아니다.

H_e=p²/(2m_e)-Σ_A κ_A/[ρ²+(z-z_A)²]^(1/2), κ_A=Z_A e²/(4πε0)에 대해

[H_e,L_y]=iℏ Σ_A κ_A z_A x/[ρ²+(z-z_A)²]^(3/2).

CAS에서 각 nuclear potential의 residual과 kinetic commutator residual은 각각 0이었다. 선형성으로 합에 적용된다. W=Σ_A κ_A z_A/[ρ²+(z-z_A)²]^(3/2)라 하면

<g|[H_e,L_y]|r_bright>= iℏ/√2 ∫ρ² dρ dz G* A W.

Exact eigenstates, 같은 H/domain/convention에서

(E_g-E_r)ℒ_gr=<g|[H_e,L_y]|r>

를 **나누지 않은 형태**로 유지한다. 퇴화점에서 energy gap으로 나누지 않는다. RHS operator가 일반적으로 nonzero인 것과 이 signed overlap이 nonzero인 것은 다르다.

## 5. Hermiticity, phase, 단위와 source sign 한계

L_y의 미분 vector field (z,0,-x)는 divergence 0이다. regular bound orbitals, 공통 self-adjoint domain, vanishing surface term 조건에서 integration by parts로 ℒ_gr=ℒ_rg*이다. real G,A에서는 ℒ가 pure imaginary이며 reverse element는 반대 부호다. commutator는 anti-Hermitian이다. CAS divergence 검산은 domain/surface 조건 자체를 증명한 것은 아니다.

φ_a→exp(iχ_a)φ_a이면 ℒ_gr→exp[i(χ_r-χ_g)]ℒ_gr. nonzero/zero는 이 local gauge에 불변이고 absolute sign은 phase-dependent이다. χ(R)의 radial connection에는 diagonal derivative 항도 있다. ℒ는 action, F_ab는 length^-1, -θdot ℒ는 energy, commutator는 energy×action이다.

Active U에 대한 -iℏ U†∂θU=-L_y를 CAS로 확인했다. 따라서 전달된 amplitude connection은 -θdot L_y다. CPC axes의 proper cyclic permutation (x_C,y_C,z_C)=(z,x,y)은 L_xC→L_z, L_zC→L_y이며 그 자체로 부호를 바꾸지 않는다. CPC의 +ωL_zC와 비교하려면 angular/passive convention을 별도로 bind해야 한다. ω=-θdot은 형식상 일치 조건이며 authors의 oriented ω가 실제 그렇다고 원문 scope에서 확정하지 않았다. production 부호를 바꾸거나 block probability의 sign-insensitivity로 coherent equivalence를 주장하지 않는다.

## 6. 현재 source와의 대응 및 Q12

CPC small-R fixed-(N,l) rotor와 현재 rotational.py/full_rotational_probability 및 R10G BLOCKS는 (2,1),(3,1),(3,2) 내부만 연결한다. g=(1,0,0)는 별도 l=0 block이며 밝은 π→g edge가 표현되지 않는다. 이는 **approximation이 제외한 candidate operator 항**이다. 실제 finite-R ℒ_gr≠0는 이번에 미확립이므로 “실제 nonzero 항을 발견했다”로 보고하지 않는다.

Q12는 이미 2pσ–1sσ direct radial 경로다. hypothetical e→π→g rotation amplitude와 같은 final channel을 공유한다. origin/ETF, basis, time ordering, phase-coherent radial/angular decomposition을 확정하지 않은 채 positive rate를 기존 Q12 probability 위에 더하면 coherence와 double counting 문제가 생긴다. 새로운 inter-block 또는 coherent model에는 R10O의 block-stochastic factor-two bound를 자동 적용하지 않는다.

## 7. 실제 실행과 종료

새 실행은 입력 ZIP 검증, fresh Git/source 읽기, private primary PDF 추출, 선택적 fulltext access 두 건, CAS_CHECK.wl 한 번뿐이다. CAS raw response는 15개 named symbolic result를 반환했다. generic Amp/W에 대한 undefined-symbol warning을 포함하며 원 반환 그대로 보존했다. isError=false, residual/normalization 결과는 예상과 일치한다. 이 경고를 지우기 위한 재실행은 하지 않았다. kernel15.0.1이다. numerical finite-R overlap, rotation ODE, transport 및 과거 graph CAS를 실행하지 않았다.

독립 검토 기록은 INDEPENDENT_REVIEW.json에 별도 보존한다. 이론의 미확립을 독립 심사나 symbolic algebra PASS로 대체하지 않는다. bounded 다음 handoff는 지정 eigenstate의 origin/ETF-matched overlap authority 하나만 연구 스레드에 요청하며 solver를 승인하지 않는다.

CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN
production_default_change=NOT_AUTHORIZED
