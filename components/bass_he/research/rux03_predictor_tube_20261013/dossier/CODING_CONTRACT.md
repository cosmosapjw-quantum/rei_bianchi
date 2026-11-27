# THEORY07 predictor·tube·old-state family 구현 계약

**단위:** `HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07`  
**저자 상태:** `author_complete` — 최종 채택 여부와 허용 범위는 [독립 판정](../review/DECISION.json)을 따른다. 이 문서는 구현 인계이며 별도의 채택 선언을 두지 않는다.  
**실행 범위:** 이 문서 작성 중 새 과학 실행은 없다. THEORY07의 native build·test·RHS·ODE·stage/corrector 반복 실행은 모두 **0회**다.

이번 delta는 기존 7변수 moving-gas BE 단계에 **실제 FT03/Verner 계수의 유리수 predictor, 두 전체 매개변수 구간의 고정 preconditioner 인증, 작은 old-gas 입력 family, 유한 affine 재anchor와 오류 전달**을 연결한다. 실제 인증은 \(h\le10^9\,\mathrm s\)까지이며, 동일한 이전 상태에서 출발하는 implicit 단계의 매개변수 family다. 구현 완료 상태는 아래 네 coding owner가 실제 source 경로와 부동소수점 enclosure를 갖추고 독립 검토를 받을 때 바뀐다.

## 1. 불변 부모 계약과 delta의 경계

[THEORY06 전체 코딩 계약](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3932669f7904f7f68f2f07dced4cf1da9d472480/research/rux03_continuation_certificate_20261013/dossier/CODING_CONTRACT.md)을 변경 없이 재사용한다.

- BASS_HE commit: `3932669f7904f7f68f2f07dced4cf1da9d472480`.
- 부모 계약 SHA256: `61fe0dd8b3b1fc14822f6c0676ae30d42ec521598eff2969527621c40ddf022e`, 33,430 bytes.
- 부모 science manifest SHA256: `9f223a9663ecec8da1edf90ee896d3aeabbf4f4c5bdd111df3e4f08b838c3192`.
- 실제 source snapshot: rei_bianchi commit `a5c958c414dea41216b445c05f58df837f05cacb`, tree `2e96362102caa69c814d477bae5d1c0177b502f9`.

부모 계약의 정규화, primitive positive-gap 회복, 조성·밀도·Doppler JVP, 동일 종말점 광자 소거, CI3/RR3/두 DR/PI 및 kinetic·binding·escape 소유권, 잔차 반올림 예산과 gross-ledger 기준은 그대로 적용한다. 이번 문서는 그 인터페이스의 predictor/tube/family 추가 조건을 정한다.

| Pending coding owner | 소비·반환할 책임 | THEORY07의 추가 요구 |
|---|---|---|
| `HERE_RUX03_PRIMARY_PROVIDER_03` | 실제 FT03/Verner, 후보 종말점의 공통 사건·미분·광자 소거 | exact anchor coefficient와 native 값의 source/precision 일치 |
| `HERE_RUX03_COVARIANT_MOMENTS_04` | 실제 방향을 보존한 에너지·운동량 모멘트 | transverse 입력을 포함한 전체 7행을 유지 |
| `HERE_RUX03_MOVING_GAS_STAGE_05` | lab 보존형 잔차와 physical primitive/JVP | old gas를 fixed chart의 \(\xi\)로 받으며 small increment를 보존 |
| `HERE_RUX03_CONTINUATION_CERTIFICATE_ADAPTER_06` | whole-domain enclosure, 종료오차와 branch 포함 증거 | 아래 predictor·두 tube·family·재anchor 인증 bundle을 소비 |

THEORY07은 네 번째 adapter의 계약을 확장한다. 별도의 다섯 번째 coding owner를 완료된 것으로 추가하지 않는다.

## 2. 공통 chart와 입력형

성분 순서는 항상
\[
X=(X_{\zeta_1},X_{\zeta_2},X_{\zeta_3},X_t,X_{m_x},X_{m_y},X_{m_z})
\]
다. \(\zeta=(n_{\rm HII},n_{\rm HeII},n_{\rm HeIII})/n_H\)는 모두 H당 abundance이고,
\(e=E/(D\epsilon)\), \(m=\mathbf M/(D\epsilon)\), \(D=\gamma n_H\)다. \(\mathbf M/c\)가 물리 운동량 밀도다. 고정 Eulerian tetrad와 lab 체적, 부호 \((-+++)\), lab 시간 \(h\)를 유지한다.

부모의 fixed reference chart를 그대로 사용한다.
\[
t=\gamma_*(e-\boldsymbol\beta_*\cdot m)-[\mu+B(\zeta)],\qquad
X=H_s^{-1}(z-z_*),\quad z=(\zeta,t,m),
\]
\[
H_s=\operatorname{diag}(10^{-3},10^{-3},10^{-3},1/4,
a_*10^{-6},a_*10^{-6},a_*10^{-6}),\qquad
a_*=\mu+B_*,\quad B_*=\frac{8871068060291}{10^{12}}.
\]
여기서 \(B(\zeta)=b_\chi\cdot\zeta\),
\(b_\chi=(\chi_0,\chi_1,\chi_1+\chi_2)\)다.

| 입력 | 인증된 값·범위 | 소비 규칙 |
|---|---|---|
| \(D,f\) | \(10^{-3}\,\mathrm{cm^{-3}},\,2/25\) | 이 family 전체에서 고정 |
| \(\mu\) | \(10^9\le\mu\le1.5\,10^9\) eV/H | 한 member 안에서 고정; 상계는 전체 범위에 균일 |
| Anchor | \(\zeta_*=(1/2,1/50,1/50),\,T_*=50000\) K | midpoint/source anchor 정의와 동일 |
| Anchor velocity | \(\beta_*=(0,0,41/841),\,\gamma_*=841/840\) | lab 방향과 함께 고정 |
| old gas \(\xi\) | \(\Xi_\eta=[-\eta,\eta]^7,\ \eta=1/100\) | 이 fixed chart의 7개 scaled 성분 |
| 후보 \(X\) | \(Q=[-1,1]^7\)와 아래 tube | 부모 전체 physical/smooth-cell 증명을 소비 |
| old photons | 각 \(p_q^-=N_q^-/D=1/100\) | old gas가 변해도 고정 |
| 외부 photon source | \(s_q=S_q/D=0\) | 이번 인증의 numerator |
| 광선 순서 | \(23\) eV의 \(+x,-x\); \(35\) eV의 \(+y,-y\); \(70\) eV의 \(+z,-z\) | coefficient의 6개 열 순서와 동일 |

실제 momentum scale은 **\(a_*(\mu)10^{-6}\)**다. 1000은 그 균일 하한을 쓰는 상계 계산에만 등장한다. \(\mu\)를 바꿔도 실제 chart의 momentum scale을 1000으로 고정하면 다른 좌표를 구현한다. 첫 네 predictor 성분은 \(\mu\) 독립이고 마지막 momentum 성분은 아래의 실제 \(a_*\)를 사용한다.

이전 상태가 바뀌는 위치는 정확히
\[
F(X,h;\xi)=X-\xi-hG_h(X)
\tag{C1}
\]
다. 모든 source와 opacity는 현재 endpoint \(X,h\)에서 계산한다. old gas를 rates에 직접 넣거나 photon input을 같이 갱신하면 (C1)의 인증과 다른 입력 family가 된다. 부모의 physical/JVP 범위는 \(Q\) 전체에서 재사용하며 anchor point 값만으로 대신하지 않는다.

## 3. 실제 compact rational predictor의 데이터 계약

정확한 계수 저장소는 [ANCHOR_RATE_RESULT.json](../evidence/ANCHOR_RATE_RESULT.json)이다. SHA256은 `75284946ef8297f34120f9cee1eefa62f01e4fce5b92ede65861cd1aa13941ac`다. 유도와 오차 전파는 [anchor enclosure](../derivations/ANCHOR_RATE_ENCLOSURES.md), [predictor 구성 P7–P14](../derivations/PREDICTOR_TUBE_CONSTRUCTION.md)를 따른다.

| 실제 JSON 필드 | 모양·의미 | 정확한 읽기 |
|---|---|---|
| `CI`, `RR`, `DR` | 각각 \(3,3,2\)개의 \([l,u]\) | 정수 문자열에 \(10^{-30}\,\mathrm{cm^3/s}\)를 곱함 |
| `KRR`, `KDR` | 각각 \(3,2\)개의 \([l,u]\) | \(10^{-40}\,\mathrm{erg\,cm^3/s}\); KDR는 이미 DR 계수×포획 에너지 |
| `sigma` | species 3 × ray 6 × endpoint 2 | \(10^{-34}\,\mathrm{cm^2}\); inactive cell의 \([0,0]\) 유지 |
| `predictor.rows` | `[1,2,3,4,7]` | **1부터 센 전체 7행 번호** |
| `predictor.A` | 길이 5 | 아래 \(A_p\), rational string |
| `predictor.B` | \(5\times6\) | 아래 \(B_p\), rational string |
| `predictor.Lambda` | 길이 6 | \(\widehat\Lambda_q\), rational string, \(\mathrm{s^{-1}}\) |
| `predictor.Bstar` | scalar | \(B_*\), rational string, eV/H |
| `predictor.uniform_point_midpoint_error_cap` | 길이 7 | \([0,H_2]\)에서 step-displacement defect의 outward cap |
| `display`, `p_at_H_display` | 가독성 표시 | accept/reject 수치의 입력으로 사용하지 않음 |

정수·유리수는 numerator/denominator를 정확하게 읽거나 outward enclosure로 변환한다. 이 anchor의 활성 species-ray cell은 12개이고, 대칭 중복을 제외한 species-energy 값은 9개다. 임계값 아래의 정확한 zero를 작은 양수로 바꾸지 않는다. binding 값 \(\chi\)와 Verner fit cutoff \(13.60,24.59,54.42\) eV는 부모 정의대로 구분한다.

먼저 5개 저장 행에 대해
\[
v_r(h)=h\left[(A_p)_r+\sum_{q=1}^6
\frac{(B_p)_{rq}}{1+h\widehat\Lambda_q}\right]
\tag{C2}
\]
를 만들고
\[
p(h;\mu)=(v_1,v_2,v_3,v_4,0,0,v_5/a_*),\qquad
\bar X(h,\xi;\mu)=\xi+p(h;\mu)
\tag{C3}
\]
로 복원한다. \(A_p\)와 \(B_p\)는 이미 정해진 source/scaling을 모은 계수다. chemical scale \(10^3\), thermal scale 4 또는 \(\gamma_*\)를 다시 곱하지 않는다. 저장 마지막 행에만 실제 \(1/a_*\)가 추가된다.

\(p_5=p_6=0\)은 이 anchor에서 같은 에너지의 \(\pm x,\pm y\) ray, 같은 inventory, \(\beta_{*,x}=\beta_{*,y}=0\)가 만드는 **true source와 midpoint 양쪽의 exact parity**다. 임의 \(\xi\), 임의 endpoint \(X\), 임의 transverse JVP가 zero라는 가정은 없다. solve와 tube는 계속 7변수다.

모든 \(h\ge0\)에서 \(h/(1+h\widehat\Lambda_q)\)가 비음수·단조 증가하므로
\[
|v(h)|\le H_j|A_p|+
|B_p|\left(\frac{H_j}{1+H_j\widehat\Lambda}\right),\quad 0\le h\le H_j
\tag{C4}
\]
를 쓴다. momentum 행의 균일 상계에는 \(a_*\ge10^9+B_*\)를 적용한다. 이것이 실제 `P_rows_outward`의 전체 구간 근거다. 동일한 rational function의 endpoint **positive majorant**를 평가한 결과이며 trajectory sampling 조건을 추가하지 않는다.

midpoint 모델은 true FT03/Verner 계수와 같다고 가정하지 않는다. 저장된 displacement cap을 **고정 상수 \(H_2=10^9\)**로 나눈
\[
\varepsilon_i=
\frac{\texttt{uniform\_point\_midpoint\_error\_cap}_i}{H_2}
\tag{C5}
\]
는 source-level 오차 전파로 정당화된 \([0,H_2]\) 전체의
\(|G_{h,i}(0)-\widehat G_{h,i}(0)|\) 상계다. 작은 또는 0인 실행 \(h\)로 cap을 나누지 않는다. 두 slab 모두 이 같은 보수적인 \(\varepsilon\)를 소비한다. \(h=0\)에서는 (C2)–(C3)가 정확히 \(p=0,\bar X=\xi\)를 준다.

## 4. 고정 chemical preconditioner와 실제 7변수 잔차

\(h_{c,1}=250000000\), \(h_{c,2}=750000000\) s에서 rational midpoint chemical 모델을 만든다. 모델 구성 시 \(T,\gamma,\beta\)와 atomic/sigma 계수는 anchor에 고정하지만
\[
y=(1-\zeta_1,f-\zeta_2-\zeta_3,\zeta_2),\quad
v=(\zeta_1,\zeta_2,\zeta_3),\quad
e_H=\zeta_1+\zeta_2+2\zeta_3
\]
를 변수로 유지한다. \(\lambda_{iq}\), \(\Lambda_q(\zeta)\), \(1+h\Lambda_q(\zeta)\)의 **조성 미분도 유지**한다. 각 gross CI/RR 및 두 DR의 target는 부모와 동일하다.

\[
J_j=\left.\partial_\zeta\widehat S_\zeta^{\rm fr}(\zeta,h)\right|_{\zeta_*,h_{c,j}},
\qquad
A_j=\operatorname{diag}\big[(I_3-h_{c,j}J_j)^{-1},I_4\big].
\tag{C6}
\]
세 abundance scale이 모두 \(10^{-3}\)이므로 이 chemical block은 해당 scaled chemical block과 동일하다. 실제 [TUBE_CERTIFICATE_CHECK.wl](../derivations/TUBE_CERTIFICATE_CHECK.wl)의 `jBase`, `jMatrices`, `blocks`, `aMatrices`가 재구성 정의다. 실행 input SHA256은 `ae1d5dfe6743ee0b73d016ae5e088e37dc221c5bdfcaf0822775200a11661c22`다.

\(A_j\)는 각 slab 전체에서 고정한다. 매 \(h\), \(\xi\), corrector iteration마다 다시 만든 행렬은 새로운 인증 대상이다. 결과 JSON의 `preconditioner_3x3_display`는 표시용 근사값이다. 정확한 rational 식을 재구성하거나 행렬 오차를 감싼 후 소비한다.

고정하는 것은 preconditioner 모델이다. 실제 \(F\), \(G_h\), JVP는 부모 primitive 회복, 온도·밀도·속도, 모든 FT03 source, candidate opacity와 photon denominator를 미분한다. 아래
\[
D_XT_j=I-A_j+hA_jD_XG_h,\qquad T_j(X)=X-A_jF(X,h;\xi)
\tag{C7}
\]
의 **전체 \(7\times7\) derivative**를 인증한다. \(\widehat S^{\rm fr}\)를 endpoint source로 사용하지 않는다.

native가 \(\widetilde A_j=A_j+\Delta A_j\)를 고정하여 사용한다면 그 차이도 포함한다. 같은 source residual cap \(R\)와 \(\ell\)에 대해
\[
\widetilde Y\le Y+|\Delta A_j|R,\qquad
\widetilde z\le z+|\Delta A_j|\mathbf1+
H_j|\Delta A_j|\ell(H_j)
\tag{C8}
\]
처럼 실제 행렬의 안전 여유를 갱신할 수 있다. 행렬 생성·inverse·곱셈 오차와 이 변화를 구별해 저장한다. (C8)은 후속 구현이 사용할 오차 전파식이며 이번에 native 행렬을 계산했다는 뜻은 아니다.

## 5. 두 slab의 exact certificate와 필드 대응

정확한 결과는 [TUBE_CERTIFICATE_RESULT.json](../evidence/TUBE_CERTIFICATE_RESULT.json), SHA256 `881a66af1a5733249d83182f8840cd36e905b6a221a78defaf0d9f191e65176a`다.

| 항목 | Slab 1 | Slab 2 |
|---|---:|---:|
| 실제 \(I_j\), s | \([0,500000000]\) | \([500000000,1000000000]\) |
| `H_seconds[j]`: upper end \(H_j\) | `500000000` | `1000000000` |
| `h_preconditioner_centers_seconds[j]` | `250000000` | `750000000` |
| 공통 `eta` | \(1/100\) | \(1/100\) |
| `P[j]`: predictor norm cap | \(2/5\) | \(77/100\) |
| `rho[j]`: 동일 7성분 반경 | \(1/50\) | \(1/10\) |
| `physical_inclusion_margins[j]` | \(57/100\) | \(3/25\) |
| `q_outward[j]` | \(23012093111/10^{12}\) | \(2916886651/62500000000\) |
| `minimum_tube_margins[j]` | \(516310980739/50000000000000\) | \(300947250667/5000000000000\) |

`H_seconds`는 두 upper end를 저장한다. 배열 전체를 단일 slab \([H_1,H_2]\)로 읽어 첫 구간을 누락하지 않는다. 실제 tube는
\[
\mathcal T_j(h,\xi)=
\{X:\|X-\bar X(h,\xi)\|_\infty\le\rho_j\},\quad h\in I_j .
\tag{C9}
\]
\(\eta+P_j+\rho_j<1\)이 전체 family tube를 \(Q\) 내부에 넣는다. 부모의 smooth physical cube, primitive/JVP와 Verner cutoff cell 증명을 재사용할 근거다.

부모 exact result의 7개 \(\ell^{(0)},\ell^{(1)}\)로
\[
\ell(H_j)=\ell^{(0)}+H_j\ell^{(1)},\qquad
R_{j,i}=H_j[\varepsilon_i+\ell_i(H_j)(\eta+P_j)]
\]
를 만들고
\[
Y_j\ge |A_j|R_j,\qquad
z_j\ge |I-A_j|\mathbf1+H_j|A_j|\ell(H_j)
\tag{C10}
\]
를 outward로 감싼다. 실제 결과의 `Y_outward`와 `Z_row_norm_outward`는 각각 \(2\times7\) 배열이다. **`Z_row_norm_outward`의 각 항은 한 행의 절대합 상계이며, \(7\times7\) entrywise matrix가 아니다.** 비등방 radius를 새로 선택할 때 이 7개 수만으로 임의 \(Z_{ik}\)를 만들어 사용하지 않는다.

다음 표는 JSON rational 값과 정확히 같은 유한소수 outward cap이다.

| 전체 행 \(i\) | \(Y_{1,i}\) | \(z_{1,i}\) | \(Y_{2,i}\) | \(z_{2,i}\) |
|---|---:|---:|---:|---:|
| \(\zeta_1\) | 0.009213538523 | 0.023012093111 | 0.035143531225 | 0.046670186416 |
| \(\zeta_2\) | 0.002907672447 | 0.008714271492 | 0.011095808456 | 0.019053971655 |
| \(\zeta_3\) | 0.000259291956 | 0.000752707201 | 0.000991251421 | 0.001631064977 |
| \(t\) | 0.000706853705 | 0.001724033427 | 0.002700259873 | 0.003461871632 |
| \(m_x\) | 0.000000143374 | 0.000000349691 | 0.000000550938 | 0.000000706330 |
| \(m_y\) | 0.000000143374 | 0.000000349691 | 0.000000550938 | 0.000000706330 |
| \(m_z\) | 0.000000143374 | 0.000000349691 | 0.000000550938 | 0.000000706330 |

각 7행에서
\[
Y_{j,i}+\rho_jz_{j,i}<\rho_j,\qquad
q_j=\max_i z_{j,i}<1
\tag{C11}
\]
를 검사한다. 실제 14개 strict tube inequalities와 두 physical inclusions는 전체 \((h,\xi,\mu)\) 범위를 감싼다. predictor의 transverse zero를 이유로 마지막 세 행을 생략하지 않는다.

선택한 부모 \(\ell(H)\)의 증명은 \(1+h\Lambda\ge1\)을 사용하여 모든 유한 \(H\ge0\)에 적용된다. 재사용은 그 analytic coefficient의 적용 범위에 근거한다. 부모의 particular self-map \(H_1B<1\)을 \(H_2\)까지 가정한 것이 아니다. 실제 \(H_2B=2007609719349141/1250000000000000>1\)이고, (C9)–(C11)의 translated predictor tube가 확장된 존재 증명이다.

## 6. 동일한 해의 endpoint 연결

공통 경계 \(h_*=500000000\) s에서는 동일한 \(\xi,\mu\), 동일한 old photons/source, 동일한 rational \(p(h_*)\)를 사용한다. 따라서
\[
\mathcal T_1(h_*,\xi)\subset\mathcal T_2(h_*,\xi)
\tag{C12}
\]
가 \(\rho_1<\rho_2\)에서 직접 따른다. **첫 tube의 전체 endpoint root box**가 둘째의 uniqueness domain 안에 있다. 서로 다른 old state의 box 합집합이 교차한다는 조건은 이 receipt를 대체하지 않는다.

\(h=0\)에서는 \(F=X-\xi\)이고, branch는 \(X(0;\xi)=\xi\)에서 출발한다. \(\xi=0\)의 branch와 기존 THEORY06 branch는 동일 residual의 \(Q\) 안 해이므로 공통 구간에서 일치한다. 전체 cube의 더 강한 uniqueness 상수는
\[
q_Q=\frac{22546206219}{500000000000}<1,\quad
\|F_X^{-1}\|_\infty\le
L_{\rm inv}=\frac{500000000000}{477453793781}<\frac{21}{20}.
\tag{C13}
\]
여기의 \(q_Q\)와 preconditioned tube의 \(q_j\)는 역할과 필드가 다르다.

이 연결에서 \(H_1\)의 output을 새로운 old gas/photon input으로 넣지 않는다. 두 slab는 **같은 이전 상태에서 출발하는 한 BE residual의 \(h\) 변화**다. 실제 다음 시간 단계는 새로운 source 문제이며 그 입력 포함 의무는 제11절을 따른다.

## 7. Old-gas family, initial-input 및 residual 오류

고정 source definition에는 old gas의 직접 인자가 없다. 따라서
\[
F_\xi=-I,\qquad
D_\xi X=(I-hD_XG_h)^{-1},\qquad
D_\xi(X-\xi)=(I-hD_XG_h)^{-1}hD_XG_h.
\tag{C14}
\]
부모의 fixed \(D\) 아래 \(n_H=D/\gamma(X)\), \(T(X)\), composition, candidate Doppler와 photon denominator는 모두 이 \(D_XG_h\)에 포함된다. 이것들을 동결해야 \(F_\xi=-I\)가 되는 것은 아니다. source의 입력 소유권을 fixed chart에서 선언했기 때문에 성립한다.

\(q_Q\)로부터
\[
\|D_\xi(X-\xi)\|_\infty
\le\frac{22546206219}{477453793781}<\frac1{20}.
\tag{C15}
\]
정확한 old gas \(\xi\)의 해 \(X_*\)와 입력 \(\widetilde\xi\)로 계산한 후보 \(\widetilde X\in Q\)를 비교한다. 실제 잔차
\(r=\widetilde X-\widetilde\xi-hG_h(\widetilde X)\)의 계산값이
\(\widetilde r\), 잔차 계산 enclosure가 \(\eta_F\), old-chart 입력 오류가 \(\eta_\xi\ge\|\xi-\widetilde\xi\|_\infty\)이면
\[
\|X_*-\widetilde X\|_\infty
\le L_{\rm inv}\,[\eta_\xi+\|\widetilde r\|_\infty+\eta_F].
\tag{C16}
\]
convex \(Q\)의 source derivative 상계를 소비한 공식이다. \(\widetilde r\)가 작은 것만으로 최종 solve 오류를 인증하지 않는다. primitive/rate/opacity 평가, photon denominator, event 합산, affine/scaling과 입력 표현의 실제 오차를 각각 \(\eta_F,\eta_\xi\)에 넣는다.

\(\mu,D,f\), photon-old 수, source, geometry의 변경은 (C16)의 gas \(\eta_\xi\)에 묻어 넣지 않는다. 동일한 입력으로 정확히 표현하거나 별도의 input derivative와 domain enclosure를 증명해야 한다. 물리 guard \(g\)의 부모 Lipschitz 상수 \(L_g\)를 사용하면 해당 오류는 \(L_g\)에 (C16)을 곱해 감싼다. 예를 들어 \(L_T=1400\) K, \(L_\beta=3\times10^{-6}\)는 각각 reference norm에 대한 상수다.

## 8. Predictor/corrector와 native 종료 조건

정확한 predictor의 해 오차는
\[
e_j=\frac{\max_iY_{j,i}}{1-q_j},\qquad
e_1=\frac{9213538523}{976987906889},\quad
e_2=\frac{35143531225}{953329813584}.
\tag{C17}
\]
표시값은 각각 약 \(0.00943055534,\ 0.03686398005\)다.
더 좁은 성분 enclosure는 \(Y_{j,i}+z_{j,i}e_j\)를 사용한다.

같은 tube 안의 후보에 대해
\[
\|X_*-\widetilde X\|_\infty
\le\frac{\|A_jF(\widetilde X,h;\xi)\|_\infty}{1-q_j}.
\tag{C18}
\]
native는 계산된 preconditioned residual \(\widetilde w\)와
\(\eta_{AF}\ge\|A_jF-\widetilde w\|_\infty\)를 함께 반환하여 분자에
\(\|\widetilde w\|+\eta_{AF}\)를 사용한다. \(\eta_{AF}\)는 residual 평가, 실제 preconditioner와 exact \(A_j\)의 차이, 행렬 곱 roundoff를 포함한다. old input까지 달라진 비교에는 (C16) 또는 그 입력 항을 포함한 정당화된 bound를 사용한다.

정확한 갱신 \(X^{(k+1)}=T_j(X^{(k)})\)을 \(\bar X\)에서 시작하면 \(q_j^ke_j\)가 오차 상계다. 결과의 `corrector_updates_in_theorem=10`과 `updates_executed=0`를 구분한다. 표시된 10회 이론 상계 \(3.92734\times10^{-19},1.80717\times10^{-15}\)는 실제 반복 잔차가 아니다. native 갱신 오류가 매회 \(\eta_T\), 초기 predictor 계산 오류가 \(\eta_0\)이고 모든 계산점이 인증 tube에 포함되면
\[
\|X^{(k)}_{\rm native}-X_*\|_\infty
\le q_j^k(e_j+\eta_0)+\eta_T\frac{1-q_j^k}{1-q_j}
\tag{C19}
\]
를 쓸 수 있다. 실제 source input·chart 오차가 있으면 별도로 전달한다.

solver 종류는 고정하지 않는다. 정확한 source identity, valid tube 포함, finite-precision residual bound를 내는 Newton 또는 다른 corrector도 (C18)을 소비할 수 있다. numerical convergence와 이론 tube PASS를 별도 필드로 남긴다.

## 9. 유한 재anchor를 small increment로 평가하는 API

[family 유도 F10–F20](../derivations/OLD_STATE_FAMILY_AND_REANCHORING.md)의 유한 변환을 사용한다. \(\alpha=\gamma_b/\gamma_a\), \(a=\mu+B(\zeta)\)일 때
\[
t_b=\alpha t_a+(\alpha-1)a+
\gamma_b(\beta_a-\beta_b)\cdot m.
\tag{C20}
\]
\(\zeta,m,D\)와 lab time은 그대로다. \(z_b=A_{ba}^{\rm chart}z_a+c_{ba}\)는 affine이며, identity 행을 제외한 thermal row는
\[
((\alpha-1)b_\chi^T,\ \alpha,\ \gamma_b(\beta_a-\beta_b)^T),
\]
thermal offset는 \((\alpha-1)\mu\), determinant는 \(\alpha>0\)다. \(A_{ba}^{\rm chart}\)와 corrector \(A_j\)를 다른 타입·필드로 둔다.

일반 center에 대해
\[
X_b=P X_a+d,\quad
P=H_{s,b}^{-1}A_{ba}^{\rm chart}H_{s,a},\quad
d=H_{s,b}^{-1}(A_{ba}^{\rm chart}z_{a,c}+c_{ba}-z_{b,c}).
\tag{C21}
\]
old state는 \(P\xi+d\)로 변환한다. new anchor를 실제 old gas의 primitive \(u_b(\xi)\)로 선택하고 그 same physical old state를 new center로 두면 정확히
\[
X_b=P(\xi)(X_a-\xi),\qquad
X_a=\xi+P^{-1}X_b,\qquad
F_b=P F,\qquad
G_{b,h}(X_b;\xi)=P G_h(\xi+P^{-1}X_b)
\tag{C22}
\]
가 된다. 구현은 **\(X_a-\xi\)의 작은 increment**를 곱한다. 큰 rest-energy baseline 두 개를 다시 만들고 빼서 (C22)를 평가하지 않는다. \(P,\xi\)와 interval/floating 오류도 함께 반환한다.

구체적인 preferred scale은 모든 \(\xi\)에 같은 \(H_s\)다. \(P\)는 thermal row만 비자명하고
\[
P_{t,\zeta}=(\alpha-1)\frac{s_\zeta}{s_t}b_\chi^T,\quad
P_{t,t}=\alpha,\quad
P_{t,m}=\frac{s_m}{s_t}\gamma_b(\beta_a-\beta_b)^T.
\tag{C23}
\]
\(P(0)=I\)다. \(\xi\)는 입력 parameter이므로 각 fixed \(\xi\)의 \(h\) slab 안에서는 chart와 \(P\)를 고정한다.

### 9.1 Family derivative의 \(DP\) 항

root를 따라
\[
D_\xi X_b[v]=(D_\xi P[v])(X_a-\xi)
+P(D_\xi X_a[v]-v)
\tag{C24}
\]
다. endpoint increment가 비영이면 첫 항도 일반적으로 비영이다.
\[
D\alpha=D\gamma_b/\gamma_a,\quad
DP_{t,m}=\frac{s_m}{s_t}
[(\beta_a-\beta_b)^T D\gamma_b-\gamma_bD\beta_b^T]
\tag{C25}
\]
와 (C23)의 나머지 미분을 함께 반환한다. \(D\gamma_b,D\beta_b\)는 부모 primitive inverse의 composition·binding·particle-count·density 미분을 포함한다.

fixed \(X_b\)에서 source parameter derivative를 계산할 때는
\[
(D_\xi X_a[v])_{X_b}
=v-P^{-1}(D_\xi P[v])(X_a-\xi)
\tag{C26}
\]
를 chain에 넣는다. fixed reference source의 \(\partial_\xi G_h=0\)을 \(G_{b,h}\)에도 그대로 적용하면 coordinate dependence를 누락한다. \(h=0\)에서는 \(X_a=\xi\), \(D_\xi X_a=I\)이므로 (C24)는 정확히 zero다.

source projection도 moving anchor를 따른다. \(\Psi_b=-u_b\cdot C\)의 변화는
\[
\delta\Psi_b=-(\delta u_b)\cdot C-u_b\cdot\delta C
\tag{C27}
\]
이고 두 commuting 변화에는
\[
\delta_1\delta_2\Psi_b
=-(\delta_1\delta_2u_b)\cdot C
-(\delta_1u_b)\cdot\delta_2C
-(\delta_2u_b)\cdot\delta_1C
-u_b\cdot\delta_1\delta_2C .
\tag{C28}
\]
unit-timelike normalization과 mixed normalization을 적용한다. 실제 old gas에 함께 붙은 anchor는 \(\delta t_b({\rm old})=\delta w\)를 주며, 부모의 fixed-anchor differential과 미분 조건이 다르다. 구현 JVP는 어떤 anchor를 고정·변화시키는지 입력으로 명시한다.

선택적으로 \(s_{m,b}=a(\xi)10^{-6}\)를 쓰면
\(P_{\rm var}=\operatorname{diag}(I_3,1,\theta_m I_3)P\),
\(\theta_m=a_*/a(\xi)\)이고 \(D\theta_m=-a_*Da/a(\xi)^2\)도 포함한다.
이는 증명된 optional mode다. preferred fixed-scale mode에 불필요한 scale derivative를 추가하지 않는다.

### 9.2 Norm, radius와 reanchored certificate

실제 [FAMILY_VARIATIONS_RESULT.json](../evidence/FAMILY_VARIATIONS_RESULT.json)의 bounds는
\[
L_P<1/30,\quad
\|P-I\|_\infty<1/3000,\quad
\|P\|_\infty\le3001/3000,\quad
\|P^{-1}\|_\infty\le3000/2999,\quad
\kappa_\infty(P)\le3001/2999 .
\tag{C29}
\]
고정·optional scale 양쪽에서 성립하며 \(\mu\) 범위 전체에 균일하다.

fixed \(\xi\)에서
\[
J_b=PJP^{-1},\qquad
\|v_b\|_{a,\xi}:=\|P^{-1}v_b\|_\infty .
\tag{C30}
\]
이 pullback norm에서는 기존 q와 inverse bound가 그대로 적용된다. 재anchor 후 tube center는 \(Pp(h)\), radius domain은
\[
\|P^{-1}(X_b-Pp(h))\|_\infty\le\rho_j
\tag{C31}
\]
다. 이 parallelepiped를 ordinary axis-aligned box로 저장한다면 적어도 성분 반경
\(\rho_j|P|\mathbf1\)를 감싸야 한다. uniform outer radius로
\((3001/3000)\rho_j\)를 쓸 수 있다. 이 outer box의 모든 점이 정확한 affine image에 속하는 것은 아니므로 인증 domain을 두 표현 사이에서 구별한다. outer box 자체를 새로운 평가·uniqueness domain으로 사용하려면 그 추가 점들까지 physical/smooth domain과 derivative budget에 포함하는 별도의 enclosure가 필요하다.

원 corrector를 conjugation하면 \(A_j^b=P A_jP^{-1}\)이고, 정확히
\[
\Phi_b(X_b)=X_b-A_j^bF_b(X_b)
=P\bigl[\Phi_a(\xi+P^{-1}X_b)-\xi\bigr]
\]
다. 따라서 실제 self-map은 이미 인증한 tube의 **affine image**로 운반된다. fixed \(\xi\)에서 (C31)의 pullback norm과 q\(_j\)를 유지한다. ordinary norm에서는 \(\kappa(P)\)를 포함하여 여유를 계산한다. 같은 물리 해를 연결할 때 두 endpoint enclosure와 uniqueness domain을 **동일한 \(P(\xi)\)**로 변환하고, 실제 affine rounding enclosure를 포함해 (C12)를 보존한다.

실제 family 결과가 \(q_Q\)를 소비하여 주는 ordinary-norm corollary는 \(P(hD_XG_h)P^{-1}\)의 상계, 즉 reanchored **unpreconditioned** contraction \(<1/20\), 그리고 residual inverse norm \(<21/20\)다. 이 상수를 실제 \(I-A_jD_XF\)의 \(q_j\) 필드로 바꾸어 쓰지 않는다. 또한 tube의 \(\|X_a-\xi\|\le P_2+\rho_2=87/100\)를 사용하여
\[
\|D_\xi X_b\|_\infty
\le \frac1{30}\frac{87}{100}
+\frac{3001}{3000}\frac{q_Q}{1-q_Q}
=\frac{18199940820361}{238726896890500}<\frac2{25}.
\tag{C32}
\]
서로 다른 \(\xi\)에 따라 움직이는 chart의 output을 비교할 때는 \(DP\)와 이 norm 변환을 사용하거나 둘 다 fixed reference chart로 옮긴다.

이번 construction에서 chart는 \(h\)에 따라 바뀌지 않는다. 후속 \(P(h,\xi),d(h,\xi)\)를 택하면 (C21)의 유한 동등성은 유지되지만 \(\partial_hF_b\)와 branch derivative에 \(P_h,d_h\)가 추가된다. family 유도 F21의 완전한 chain을 소비한 뒤 새로운 parameter certificate로 기록한다.

## 10. 실제 구현의 입력·출력 및 precision receipt

아래 이름은 **의미 인터페이스**다. 현재 repository에 이미 존재하는 함수 이름을 주장하지 않으며 기존 production API를 일괄 변경하라는 계약도 아니다.

| 동작 | 필수 입력 | 필수 반환 |
|---|---|---|
| `load_predictor_bundle` | pinned result/WL/source SHA, schema | rational \(A_p,B_p,\widehat\Lambda,B_*\), 1-based row map, 7개 defect cap, source units |
| `predictor` | \(h,\mu,\xi\), common chart | 7개 \(p,\bar X\), 실제 \(a_*\), native 평가오차 또는 exact 값 |
| `fixed_preconditioner` | slab ID, exact midpoint/source 정의 | 고정 \(A_j\), exact 또는 enclosed inverse, \(\Delta A_j\), norm·nonsingularity 증거 |
| `endpoint_events_and_jvp` | 같은 \(X,h\), fixed photon-old | 부모의 공통 PI/CI/RR/DR2/kinetic/binding/escape와 \(p^+\), full7 \(G_h\), JVP, parameter derivative |
| `certify_tube` | slab, \(\Xi_\eta,\mu\) 범위, source/primitive caps | \(P^{row},P,\rho,R,Y,z,q\), physical·strict margin, 전체 입력 범위 |
| `certify_candidate_error` | actual candidate와 잔차·roundoff enclosure | tube/Q 포함, (C16) 또는 (C18)의 해 오류, 실제 solver 호출 수 |
| `reanchor_increment` | physical old-state primitive, reference \(\xi\), 작은 \(X-\xi\) | \(P,P^{-1},DP\), transformed increment·잔차·radius/norm enclosure |
| `connect_endpoint` | 같은 \(h,\xi,\mu\)와 source snapshot의 두 enclosure | whole endpoint root containment, chart map, rounding 여유 |

정수·유리수 parse, source-real-literal의 수학적 해석, native floating value, certified outward endpoint를 다른 필드로 기록한다. source의 실제 binary `powf`/`exp`/`sqrt` 및 compiler 최적화가 만드는 값을 exact-real predictor 계수와 자동으로 동일시하지 않는다. 실제 library/precision/rounding 방법과 각 수학 함수의 enclosure가 필요하다.

최소 source binding은 [CURRENT_SOURCE.json](../source_map/CURRENT_SOURCE.json)에 있다.

| 실제 receiver source 경로 | SHA256 |
|---|---|
| `rust/rei_microphysics/src/ft03_rates.rs` | `1a97cd7a3555deeb4d8700376cd84580c5102127773bc3a235a29c33b0c1542f` |
| `rust/rei_microphysics/src/ft03_controlled.rs` | `afcc1c7dd3ad0830552ed1736ff6d96482944d7a3ceac0c5d44b638c15fb01f4` |
| `rust/rei_microphysics/src/atomic_provider.rs` | `b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3` |
| `rust/rei_microphysics/src/hhe_events.rs` | `c100b08e034089c2d67b2102769ccdd51f1d29a2f388d6bb2dfe7984af93b290` |

부모의 exact full-source result SHA256 `ae529e4fdc6d68e3400fe14c9167fb0945b448daf884db019d2c3c0f184b683f`가 \(\ell^{(0)},\ell^{(1)}\)의 입력이다. 본 단위는 그 원응답에서 일부 보조 exact fields가 생략됐다는 부모 capture 기록도 유지한다. 수신된 \(\ell\), \(B\), \(q\)에서 재구성한 공식을 과거 원응답에 있던 필드로 기록하지 않는다.

후속 native receipt는 실제 commit/tree/source, compiler·target·binary SHA, 계산 library, 입력 byte SHA와 units, chart와 old-state identity, 6개 ray의 순서·weight·source owner, exact proof bundle, 실제 candidate·event·derivative·enclosure·반복 횟수를 묶는다. 최종 science manifest의 identity는 freeze 후 그 manifest에서 읽는다. 독립 판정은 이 계약의 `author_complete`와 별도이며 [DECISION.json](../review/DECISION.json)에서 한 번만 선언한다.

## 11. 다음 THEORY08과 실제 두 단계의 입력 포함 의무

다음 이론 ID는 **`HERE_RUX03_JOINT_INPUT_AND_TWO_STAGE_ENCLOSURE_08`**이다. 첫 의무는 예를 들어
\[
p_q^-=p_{0q}(1+\pi_q),\qquad |\pi_q|\le1/100
\]
와 같은 명시적인 photon-old family를 \(\xi\)와 합쳐, 실제 fixed \(D\)/tetrad source에서
\[
F_X^{-1}hG_\pi
\]
및 eliminated photon output의 **직접 photon-input 항과 endpoint 변화 항을 모두 포함한 total derivative**를 정량화하는 것이다. 이 photon-input derivative의 수치 budget은 THEORY07의 (C14)–(C16)에 포함되지 않는다.

그다음에는 첫 stage의 joint gas/photon **output enclosure 전체**가 실제 둘째 stage의 재anchor input domain에 포함됨을 새로 증명해야 한다. 현재 old-gas family는 \(\|\xi\|\le0.01\)이고, 첫 stage의 predictor는 \(h=10^9\)에서 약 0.76인 성분을 갖는다. 현재 root enclosure도 그 출력을 같은 작은 old-input cube에 넣지 않는다. 좌표를 재anchor했다는 사실만으로 다음 stage의 source·temperature·opacity·photon-old domain 인증이 생기지 않는다.

각 stage의 적절한 입력 domain과 joint enclosure가 먼저 연결되면, 그때 각각의 solve/input error 상수에 대한 두 단계 recurrence를 적용할 수 있다. 현재 숫자의 Lipschitz 상수를 단순히 곱하여 2-stage 결과로 기록하지 않는다. 이는 fixed \(D\)/tetrad 아래 implicit stage composition의 후속 이론 의무이며, ODE temporal truncation error 또는 geometry 변화의 인증은 별도다. THEORY08은 완료된 THEORY07의 채택 조건을 소급하여 늘리지 않는다.

## 12. Native 완료를 판별할 최소 추가 증거

부모 계약 제10절의 native discriminating gates를 그대로 유지한다. 특히 split baseline/increment roundtrip, composition/primitive JVP의 \(dB,dd,dn_H,D_XE'\), candidate opacity와 photon denominator 미분, \(h=0\)·\(\Lambda=0\)·multiple absorbers, gross CI/RR/DR2/PI 장부, nonzero bulk와 transverse 방향, whole-box enclosure, residual-roundoff와 root nesting이 먼저 실제 source 경로에 있어야 한다.

THEORY07 delta의 다음 판별 증거를 그 실제 coding 작업에 더한다.

| 구별할 위험 | 후속 native 증거 |
|---|---|
| coefficient 행·단위·momentum scale 오독 | exact bundle의 5→7 mapping, \(h=0\), 서로 다른 허용 \(\mu\)에서 첫 네 행 불변·마지막 actual \(a_*\), 6개 denominator와 enclosure 대조 |
| anchor 대칭을 전체 model 대칭으로 오인 | anchor parity와 일반 transverse \(\xi,dX\)를 구분하는 full7 source/JVP 결과 |
| frozen block을 true Jacobian으로 사용 | endpoint primitive/opacity/temperature 피드백을 포함하는 JVP와 고정 \(A_j\)를 별도 반환 |
| 표시 행렬 또는 잘못된 \(Z\) shape 소비 | rational inverse 또는 \(\Delta A\) enclosure, \(2\times7\) row-norm schema, 실제 행별 strict margin |
| point sample로 uniform tube를 대체 | 모든 \(h,\xi,\mu\)의 domain enclosure, 두 slab의 actual margins, native roundoff가 차감된 여유 |
| 다른 입력·다른 root를 연결 | 같은 \(\xi,\mu,\) photon-old에서 전체 common-endpoint nesting과 affine 오류 포함 |
| residual만으로 final error 선언 | actual \(\eta_\xi,\eta_F,\eta_{AF}\), valid candidate domain, (C16)/(C18) 결과 |
| 재anchor에서 큰 수 cancellation·old-state term 누락 | small-increment (C22)와 원 7개 residual의 동등성 enclosure, non-old-center에서 transformed old-state 유지 |
| \(DP\) 또는 moving-anchor source chain 누락 | 비영 increment의 family 방향에서 (C24)–(C28), \(h=0\) limit, optional scale의 \(D\theta_m\), 독립 고정밀/구간 대조 |
| affine outer box를 image로 취급 | \(P\)와 pullback norm, 실제 transformed radius/endpoint inclusion; ordinary norm의 condition factor |
| gas-only family를 두 시간 단계로 확대 | THEORY08의 joint gas/photon input·output domain receipt가 있을 때만 composition 주장 |

사건·energy·momentum residual 정규화는 부모 계약의 **gross 사건 scale**을 사용한다. 차감 후 작은 net source를 유일한 분모로 삼아 CI/RR/DR cancellation 또는 escape 중복을 가리지 않는다. 위 표는 미래 coding gate이며 이번 단위에서 실행한 native test 목록이 아니다.

## 13. 근거, 상태와 원래 DAG

실제 anchor 10개, tube 14개, family scalar 12개, moving-anchor xAct 9개 그룹이 모두 PASS다. 네 evaluator 실행의 총 45개 named group이며 native test 수 또는 독립 정리 수가 아니다. xAct의 12개 tensor residual은 모두 정확히 zero다. family scalar의 69개 내부 항목은 58개 algebraic zero와 11개 true Boolean을 함께 센다. 전체 실행·입력·raw·result binding은 [EXECUTION_RECORD.json](../evidence/EXECUTION_RECORD.json)에 있다. 이 계약은 성공한 과학 검산을 재실행하지 않았다.

Family scalar result SHA256은 `10434b44261079c18f62c1522820fb65c642192b46306b22bdb2aa4c5dd9a023`, xAct result SHA256은 `44619b81acb41c55854e9d332229807949ac2ae9dbd2e9fa5289b64900336738`이다. [실제 xAct 결과](../evidence/XACT_REANCHOR_RESULT.json)는 xTensor 1.3.0의 실제 load와 9개 그룹·12개 zero를 기록한다. 모든 source identity와 수학적 적용 범위를 유지한 상태에서 native 구현은 별도 pending이다.

- [과학 계약](SCIENTIFIC_CONTRACT.json), [재사용 기록](REUSE_RECORD.json), [source identity](../source_map/CURRENT_SOURCE.json).
- [Anchor 유도](../derivations/ANCHOR_RATE_ENCLOSURES.md), [실제 anchor 입력](../derivations/ANCHOR_RATE_CHECK.wl), [실제 anchor 결과](../evidence/ANCHOR_RATE_RESULT.json).
- [Predictor와 full7 tube 증명](../derivations/PREDICTOR_TUBE_CONSTRUCTION.md), [실제 tube 수치 해설](../derivations/TUBE_CERTIFICATE_NUMBERS.md), [실제 tube 입력](../derivations/TUBE_CERTIFICATE_CHECK.wl), [실제 tube 결과](../evidence/TUBE_CERTIFICATE_RESULT.json).
- [Old-state family와 finite reanchor](../derivations/OLD_STATE_FAMILY_AND_REANCHORING.md), [실제 family scalar 결과](../evidence/FAMILY_VARIATIONS_RESULT.json), [실제 moving-anchor xAct 입력](../derivations/XACT_REANCHOR_VARIATIONS.wl), [실제 xAct 결과](../evidence/XACT_REANCHOR_RESULT.json).
- [부모 전체 구현 계약](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3932669f7904f7f68f2f07dced4cf1da9d472480/research/rux03_continuation_certificate_20261013/dossier/CODING_CONTRACT.md), [receiver FT03 원본](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_rates.rs).

원래 owner DAG **RUX02 + global RUX03 → RUX04 → RUX05**를 보존한다. PRIMARY_PROVIDER_03, COVARIANT_MOMENTS_04, MOVING_GAS_STAGE_05, CONTINUATION_CERTIFICATE_ADAPTER_06은 모두 native pending이다. 별도 all-Bianchi·abundance-source·reference-current·class-B·relative-species-tilt D2.3 의무는 이 단위에서 변경하지 않는다. THEORY07의 채택은 정해진 source/input/domain의 predictor·tube·gas-only family·재anchor 이론에만 적용되며 실제 전체 RUX03 owner 완료는 이후 native receipt와 독립 검토에서 판정한다.
