# A1 독립 검토 — 일반 연결식과 물리적 완결성의 경계

최종 판정: **DERIVED_AND_INDEPENDENTLY_REVIEWED_IN_SCOPE**. 처음 식별한 아래 R1·R2에 대한 저자의 국소 수정본을 직접 확인했으며 두 지적은 닫혔다. **FRAME_CONNECTION_GAP_IDENTIFIED**와 다음 단일 node **A1b_ASYMPTOTIC_CHANNEL_EMBEDDING_AND_ETF_CHOICE**는 타당하다. **FRAME_COMPLETE는 아니다.** A1 작성에 참여하지 않은 별도 검토자가 전달된 식을 수동으로 재유도하고 원전·기존 theorem admission과 대조했다. 기존 테스트를 PASS 수 확보 목적으로 재실행하지 않았다.

## 식별하고 닫은 두 국소 수정

**R1 — 중간 중요도, form-domain과 strong residual의 구분.** §2는 일반 기저에 form-domain regularity를 요구하면서 A1.2의 `h=X†HX`와 A1.7의 `Q(iℏXdot−HX)c`를 Hilbert-space 연산으로 쓴다. Coulomb form domain H¹만으로 Hχ∈L²는 보장되지 않는다. 유도 자체의 부호 문제가 아니라 정칙성 진술의 불일치다. 다음처럼 고치면 된다.

- 일반 form-level 정의는 `h_ab=q_t(χ_a,χ_b)`로 쓴다. 모든 χ_b∈D(H)이면 `h_ab=〈χ_a,Hχ_b〉`와 같다. X가 적절하게 L²에서 시간 미분 가능하다는 조건도 명시한다.
- A1.7의 strong vector는 χ_a∈D(H)일 때만 사용한다. 일반 H¹ 기저에서는 모든 `v∈H¹∩Ran Q`에 대한 weak residual `r_t(v)=iℏ〈v,Xdot c〉−q_t(v,Xc)`를 사용한다. `〈v,X cdot〉=0`이므로 이 표현이 projected solution의 수직 residual이다.
- §8의 임의 real differentiable η도 곱한 상태가 필요한 form/time-derivative domain에 남아야 한다. `(p+ℏ∇η)²`의 strong 해석에는 추가 공간 정칙성이 필요하며, 그렇지 않으면 quadratic-form 해석을 쓴다. 실용적인 선형 공간 ETF는 이 제한과 양립한다.

이 보완 때문에 R10R의 `Lψ∈D(H)`를 새로 요구할 이유는 없다. 해당 기존 theorem의 weak commutator와 `Lψ∈H¹` 근거는 그대로 유효하다.

**수정 확인: CLOSED.** A1.2는 sesquilinear form으로 바뀌었고 χdot∈L²가 명시되었다. A1.5의 equivalent Y 표현도 form으로 제시한다. A1.7은 weak residual이고 strong vector에는 추가 domain 조건이 붙었다. A1.20에 covariant-gradient quadratic form과 phase의 H¹ 보존 조건을 추가했다. 이 수정은 필요한 regularity를 충족하며 matrix 코드나 물리식의 부호를 바꾸지 않는다.

**R2 — 중간 중요도, P24의 회전 결합에는 i가 포함된다.** 원전 메모의 “Eq.(17)의 rotational 변화는 +γ(m/ℏ)R(V_j−V_k)〈j|x′|k〉”에는 이것이 **〈j|iL_y|k〉의 변화**임을 명시해야 한다. 〈L_y〉의 변화로 읽으면 i가 빠져 Hermiticity/phase와 충돌한다. 직접 도출하면

\[
L_y^O=L_y^{\rm CNM}-\gamma R p_x,
\quad (p_x)_{jk}=\frac{i m}{\hbar}(E_j-E_k)(x')_{jk},
\]
\[
\Delta (iL_y)_{jk}=+\frac{\gamma mR}{\hbar}(E_j-E_k)(x')_{jk},
\qquad
\Delta (L_y)_{jk}=-\frac{i\gamma mR}{\hbar}(E_j-E_k)(x')_{jk}.
\]

여기서 m은 P24의 Jacobi 전자 reduced mass다. PDF p.5의 인쇄 Eq.(17)을 직접 보았으며, 인쇄된 에너지의 Λ 첨자는 bra/ket 첨자와 일관되지 않아 보인다. 그 인쇄 첨자를 무비판적으로 복사하지 말고, 위 일반 bra/ket 에너지 차를 직접 유도한 식으로 명시하면 된다. 기존 메모가 지적한 Eq.(13)의 m/ℏ² 누락과 이 문제를 구분한다. A1.16–17의 일반 벡터 상쇄 자체에는 이 원전 표기 문제가 전파되지 않았다.

**수정 확인: CLOSED.** 원전 메모는 Eq.(17)을 〈iL_y〉의 식으로 명시했고 〈L_y〉의 −i factor, Jacobi reduced mass 및 인쇄 subscript에 대한 주의를 추가했다. `j,k`의 energy difference는 원전의 무비판적 전사가 아니라 commutator로 재유도했다고 명시했다.

## 확인한 핵심 식

| 항목 | 판정과 근거 |
|---|---|
| A1.3–6 metric transport | `iℏS cdot=(h−iℏD)c`, `Sdot=D+D†`에서 norm derivative가 0이다. `c=Wa`를 대입하면 `−iℏW†S Wdot`가 반드시 포함되며, 미분한 `W†SW=I`로 K의 Hermiticity가 따른다. R1의 form 해석하에서도 성립한다. |
| A1.8–10 일반/비가환 gauge | 가역 A에 대한 D의 추가 항 `A†S Adot`와 unitary U에 대한 `−iℏU†Udot`가 맞다. `U=e^{iα}`이면 diagonal에 `+ℏαdot`가 생긴다. 퇴화 subspace의 scalar gap division을 배제한 점도 타당하다. |
| A1.11–13 회전·병진 | active body→lab U와 `QᵀQdot x=Ω×x`에서 `U†Udot=−i(V·p+Ω·L)/ℏ`; 따라서 회전·병진 항은 각각 `−Ω·L`, `−V·p`다. |
| A1.14–15 R10R | 기존 admission은 지정된 sector ground pair와 charge-center/meridional phase의 bare matrix에 한정된다. `L_gb=−iℏC_RT_R/Δ_R`이면 `K_gb^rot=+iℏ θdot C_RT_R/Δ_R`가 맞다. 비교한 R10P convention과 일치한다. |
| A1.16–18 원점 이동 | `L′=L−s×P`, `V′=V+Ω×s+sdot`, intrinsic contribution `+sdot·P`가 정확히 상쇄한다. s(R)에 대한 `F′_R=F_R+(i/ℏ)s_R·P`도 맞다. 동일 physical basis를 변환한 finite span에 국한한 불변성 진술이 적절하다. |
| A1.19 common boost | `B†pB=p+m_eu`, `−iℏB†Bdot=m_e udot·x+ℏγdot_b`다. 회전 항은 `−m_eΩ·(x×u)=+m_e(Ω×u)·x`; u=V에서 총 관성항은 `m_e(Vdot+Ω×V)·x`다. scalar phase의 부호도 lab ETF와 일치한다. |
| A1.20 ETF | ket별 phase 차, S와 D의 변화 및 kinetic operator product가 필요하다. `a=ℏ∇η`에 대해 `(p+a)²=p²+2a·p−iℏ∇·a+a²`이므로 단순 수치적 square로 바꾸면 안 된다. 원문의 주의가 맞다. |
| A1.22 nuclear kinetic | `∇_R|r=∇_R|x−γ∇_x`를 제곱하면 mixed derivative의 +γℏ²/μ_N와 추가 electronic Laplacian의 −γ²ℏ²/(2μ_N)가 나온다. P24의 완전 양자핵 operator와 classical prescribed-path 전자 TDSE는 분명히 다른 근사 수준이다. |

E,K는 energy, F_R는 inverse length, P는 momentum, L은 action이다. `Rdot F_R`, Ω 및 frame/gauge 미분은 inverse time이며 ℏ를 곱한 뒤 energy다. Common boost의 관성항은 mass×acceleration×length다. CNM→charge-center 계수는 dimensionless이고 식 A1.18의 질량·전하 가중차도 맞다.

## 물리적 claim ceiling

1. 직교화된 projected K의 Hermiticity는 주어진 finite ansatz의 norm 보존을 보장한다. 누락 채널·연속체·basis error, ETF 선택의 정확도 또는 단면적 정확도를 인증하지 않는다. R1의 residual 설명은 바로 이 구분에 필요하다.
2. P24는 coordinate change에 따라 **전체** 핵운동 방정식이 일관되게 변환된다는 근거다. clamped m_e를 reduced mass m으로 바꿔 쓰거나 원점 변화가 개별 NAC를 불변으로 만든다는 근거가 아니다. 현재 본문은 이를 올바르게 제한한다.
3. Bare R10R nonzero는 finite-R ETF-dressed coherent collision amplitude의 nonzero 또는 정량적 중요도까지 보장하지 않는다. angular+Q12 probability의 단순 합산은 coherent path의 간섭과 phase를 복원하지 못한다. 확률만으로 radial derivative amplitude를 복원할 수 없다는 지적은 타당하다.
4. 임의 채널별 ETF가 A1.8의 동일-span gauge라는 뜻은 아니다. 채널마다 다른 공간 위상을 곱하면 일반적으로 finite-dimensional physical span 자체가 바뀐다. §8에 이 문장을 추가하면 origin/gauge covariance와 ETF 근사 선택의 차이가 더 명확해진다. 이는 권고이며 별도의 연구를 요구하지 않는다.
5. P03가 지적한 finite-R ambiguity, 서로 다른 핵 속도, H(1s)와 무한핵질량 He⁺(n=2)의 점근 축퇴 때문에 localized channel/projector의 지정과 finite-R continuation이 필요하다. 현재 자료는 그것을 지정하지 않았으므로 A1b가 정확한 다음 node다. 경계 projector, S의 비특이성, S/h/D의 실제 계산 전에는 downstream collision 연구를 열지 않는다.
6. 추가 ETF/ERF 원전의 Λ에 관한 centered-diatomic rank≤1 지적은 공선 벡터들의 outer product 합이라는 정의에서 직접 따른다. 해당 3×3 역행렬을 그대로 채택할 수 없다는 제한은 타당하며 새로운 ERF prescription을 인증하지 않는다.

## 증거 수준과 종료

12개 테스트 결과와 원 코드·사전 tolerance·첫 실패 기록의 존재를 읽었다. 정확한 변환으로 만들어진 작은 matrix fixtures는 implementation/algebra consistency 증거다. Coulomb domain 논증, 실제 channel matrix elements, physical completeness의 독립 증명은 아니다. Wolfram 결과는 transcription임이 명시되어 있어 원 transport envelope로 승격하지 않는다. 이번 독립 검토는 새 solver, CAS, 과거 scientific suite, collision solve를 실행하지 않았다.

R1·R2의 좁은 텍스트 수정 확인 후 형식적 유도는 **DERIVED_AND_INDEPENDENTLY_REVIEWED_IN_SCOPE**로 기록한다. 물리 node 상태는 계속 **FRAME_CONNECTION_GAP_IDENTIFIED**, `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `downstream_allowed=false`다. 이 리뷰를 물리적 A1 closure로 사용하면 안 된다. 아래 JSON은 최초 검토본과 수정 확인본의 SHA-256을 구분하여 보존한다.
