# A1 원전 범위와 방정식 대조

이 메모는 문헌 근거와 적용 한계를 정리한다. A1의 새 유도나 HeH²⁺ 물리적 완결성을 인증하지 않는다. PDF 번호는 1부터 세며 표지 포함 여부가 문헌마다 다르다. 원본 identity는 `A1_SOURCE_MANIFEST.json`에 기록했다.

| 원전 | 직접 확인 위치 | A1에 쓸 수 있는 근거 | 그대로 확장할 수 없는 부분 |
|---|---|---|---|
| Liu et al. 2024, DOI [10.1088/1674-1056/ad5322](https://doi.org/10.1088/1674-1056/ad5322) | §2, 083401-2–3; PDF 3–4; Eqs. (3)–(6) | projectile-centered AO의 ETF, trajectory 전자 TDSE, overlap matrix가 있는 계수 방정식 | finite-R moving-MO switching, 양자 핵운동 완결성 |
| Belyaev–Dalgarno–McCarroll 2002, DOI [10.1063/1.1457443](https://doi.org/10.1063/1.1457443) | §§II–III, 5396–5398; PDF 3–5; Eqs. (11)–(17) | 원점 이동에 따른 NAC 변화와 전체 핵운동 방정식의 상쇄 | 전자 미분결합만 바꾸는 처방, asymptotic ETF의 완전한 구축 |
| Stolterfoht et al. 2010, DOI [10.1103/PhysRevA.81.052704](https://doi.org/10.1103/PhysRevA.81.052704) | §II, 052704-2–3; PDF 2–3 | ETF를 가진 AO와 전자 상태에 결합된 고전 핵궤적, 최종 채널 projection | 완전 양자 핵산란, 논문 자체만으로 END 구현 재현 |
| Liu et al. 2003, DOI [10.1103/PhysRevA.67.052705](https://doi.org/10.1103/PhysRevA.67.052705) | §I 및 §II.A, 052705-1–3; PDF 1–3 | asymptotic ETF 조건이 finite-R switching을 유일하게 정하지 않는다는 한계; HSCC의 별도 경로 | 일반 이동기저 항등식에서 곧바로 HSCC 동등성을 추론 |
| Gusev–Solov’ev–Vinitsky 2023, DOI [10.1016/j.cpc.2023.108662](https://doi.org/10.1016/j.cpc.2023.108662) | §§2.6–2.7, article/PDF 11–12; Eqs. (47)–(54) | 회전 프레임의 비단열 항과 small-R 모형의 범위 | ARSENY probability matrices를 coherent MO amplitude propagation으로 사용 |

## 정확한 매핑

**P01.** 원문의 원자단위 ETF는 `exp[-i v² t/2 + i v·r]`이다. 전자 질량과 ℏ를 복원하면 `exp[i(m_e v·r − m_e v²t/2)/ℏ]`이며, 복원은 차원에 의한 표기 변환이다. 원문은 `R(t)=b+vt`, target 기준 전자 좌표, projectile 중심 AO를 사용한다. 인쇄 Eq. (3)의 AO 인자는 축약 표기이므로 `ψ_j^P(r)`를 움직이지 않는 고정 함수로 읽어서는 안 된다. Eq. (6)은 `i dc/dt=S^{-1}Mc`이고 S와 M을 overlap/coupling matrices라고 정의한다. 이것은 일반 metric transport와 양립하지만 M의 완전한 채널별 정의나 finite-R MO 선택을 제공하지 않는다. PDF 3–4 수식을 렌더링하여 확인했다.

**P24.** 원점은 Eq. (11)의 `R_O=R_CNM+γR`이다. Eq. (12)의 chain rule로 바뀐 핵좌표 미분과 전자좌표 미분이 연결된다. Eq. (14)는 핵-전자 mixed derivative와 전자 운동에너지 계수 변화를 포함하며, Eq. (15)는 이것들이 NAC의 원점 변화와 상쇄됨을 보인다. 따라서 coupling matrix element 하나의 불변성을 요구하는 것이 적절하지 않다. 원문 Eq. (16)의 radial 변화는 `−γ(m/ℏ²)(V_j−V_k)〈j|z′|k〉`, Eq. (17)은 `〈iL_y〉`의 원점 변화식이다. Bra/ket를 j,k로 일관되게 쓰면 그 보정은 `+γ(m/ℏ)R(V_j−V_k)〈j|x′|k〉`이며, `〈L_y〉` 보정은 이 값에 −i를 곱한 것이다. m은 해당 Jacobi 전자 reduced mass다. 인쇄된 Eq. (17)의 일부 에너지 subscript는 bra/ket label과 일치하지 않아, 여기서는 chain rule과 [H,x]=−iℏp_x/m으로 재유도한 j,k 표기를 사용했다. 인쇄 Eq. (13)는 m/ℏ²를 명시하지 않지만 Eq. (16)는 명시하므로, 단위 검산에는 Eq. (12)/(16)를 기준으로 삼는다. 전자 원점 변경과 전체 계의 일정한 병진을 혼동하면 안 된다. PDF 4–5를 직접 렌더링하여 확인했다. 원문은 올바른 asymptotic state construction을 상세히 다루지 않는다고 명시한다.

**P02.** END는 전자를 양자적으로, 핵을 고전 궤적으로 다룬다. 궤적은 전자 동역학과 함께 결정되며 고정 직선으로 강제되지 않는다. §II의 확률 정의는 최종 상태와 점근 전자상태의 내적 절댓값 제곱이다. 뒤따르는 coefficient shorthand에는 modulus-square가 명료하지 않으므로, overlap amplitude와 probability를 구분한 앞 정의를 사용해야 한다. 이 문헌의 작은 에너지 오차나 기존 단면적 일치가 현재 구현의 검증을 대신하지 않는다.

**P03.** 도입부는 원자별 asymptotic ETF만으로 finite-R MO의 translational motion이 정해지지 않아 switching function 선택이 필요하다고 지적한다. 이는 특정 ETF가 전부 잘못됐다는 명제가 아니다. HSCC는 mass-weighted Jacobi 좌표와 hyperradius를 사용하는 양자 세 입자 formulation이며, 그 hyperradius를 MO의 internuclear R로 대체할 수 없다.

**P06.** Eq. (47)은 원자단위에서 `i∂t|A〉=[εR²(t)L_x²+ω(t)L_z]|A〉`다. x축이 internuclear axis이고 z축이 collision plane의 법선인 특정 convention이다. 이 부호는 다른 active/passive rotation 정의에 직접 이식할 수 없다. 같은 N,l multiplet의 small-R splitting 모형이며, Eq. (50)은 hidden-crossing **확률** 행렬들의 곱이다. PDF 11 수식을 렌더링하여 확인했다.

## 추가 원전과 적용 제한

Athavale et al., [JCP 159, 114120 (2023), DOI 10.1063/5.0160965](https://doi.org/10.1063/5.0160965), 직접 읽은 버전은 [arXiv:2308.14621v1](https://arxiv.org/abs/2308.14621v1)이다. §§III–IV 및 VI를 확인했다. ETF Eq. (36), pp.12–14는 서로 다른 원자의 ETF로 생기는 MO 비직교성과 위상 차이를 무시하고 속도 1차 항을 남긴 뒤 AO correction을 Hermitianize한다. 따라서 exact nonorthogonal transport의 근거로 사용할 수 없다. ETF-corrected coupling은 Eq. (53), p.15; ETF+ERF는 Eq. (96), p.22다. §IV.B p.21은 rotation basis의 정확성 범위를 rigid rotation으로 한정한다. §VI pp.24–26은 외부장과 spin–orbit 상황을 제외한다. 논문의 publication와 preprint의 equation-by-equation 동일성은 주장하지 않는다.

추가 추론: Eq. (97)의 `Λ=Σ_B |d_B| R_B R_B^T`는 중심을 잡은 diatomic에서 rank≤1이다. 따라서 Eq. (96)의 3차원 역행렬은 HeH²⁺에 그대로 적용할 수 없다. 이것은 원문의 직접 주장이 아니라 해당 정의와 공선성에서 얻는 적용 제한이다. 별도 rank 처리의 정당화 없이 ERF 공식을 구현으로 채택하면 안 된다.

Buenker–Li, JCP 112, 8318–8321 (2000), DOI [10.1063/1.481437](https://doi.org/10.1063/1.481437)는 P24 reference 6 및 publisher issue/저자 publication list의 검색 metadata로 확인했다. 직접 DOI 읽기 실패와 issue page timeout으로 full text는 미확보다. 제목의 “independence”만으로 P24와의 모순을 판정하지 않는다. 이 문헌은 현재 `METADATA_ONLY` 탐색 기록이며 A1의 직접 유도 근거가 아니다.

## 근거 상태

- 위 문헌의 범위와 식 위치: **literature-supported**.
- 현재 프로젝트의 common-frame/general metric identities: 별도 A1 유도에서 판정할 사항.
- finite-R channel-dependent MO ETF 선택, 구체적 integrals, 비특이 overlap, 누락 채널의 영향, 물리적 단면적 정확도: 이 메모로 닫히지 않는다.
- solver, fitting, numerical benchmark, 물리 gate 변경: 이 하위 작업에서 실행하지 않았다.

이 폴더에는 원문 PDF나 전체 텍스트 추출본을 포함하지 않는다. 추가 preprint 원본과 렌더링은 임시 작업 폴더에만 있다.
