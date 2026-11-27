# A1b: AOCC 이동 원자기저와 점근 투영의 원전 근거

상태: **literature-supported**, 아래 지정 절·식의 원문을 직접 확인했다. 이 문서는 A1b에서 선택하는 유한 $R$ 기저나 새로운 위상 제거식의 증명이 아니다. 모든 PDF는 기존 v3 원본을 읽었고, `SOURCE_MANIFEST.json`의 SHA-256과 재검산 결과를 남겼다. 새 문헌을 다운로드하지 않았다. 수식의 단위는 각 원문에서 atomic units이며, $m_e,\hbar$ 복원은 연구 본문의 직접 유도로 구분해야 한다.

## 1. P01 Liu et al. (2024): AOCC 기저와 ETF

출처: DOI [10.1088/1674-1056/ad5322](https://doi.org/10.1088/1674-1056/ad5322), §2, PDF 3–4쪽 / 인쇄 083401-2–3, 식 (1)–(8). 식 (3)은 원본 페이지를 시각 확인했다.

원문의 핵 운동은 고전 직선 궤적 $\mathbf R(t)=\mathbf b+\mathbf v t$이다. Fig. 1의 $\mathbf r$는 표적 중심 기준 전자 좌표이고, projectile/target 원자 상태는 각각 그 중심의 GTO 전개로 구성한다. 식 (1)–(2)의 $N_k$는 개별 Cartesian Gaussian 정규화 인자이다. 이 진술은 **두 중심 전체 기저의 직교성**을 뜻하지 않는다.

식 (3)은 target 항에 $e^{-i\epsilon_i^Tt}$, projectile 항에 $e^{-i\epsilon_j^Pt}\,e^{-iv^2t/2+i\mathbf v\cdot\mathbf r}$를 사용한다. 즉 원자 내부 에너지 위상과 병진 운동 ETF의 시간 위상을 별도로 쓴다. 원문은 projectile 상태를 식 (3)에서 $\psi_j^P$\mathbf r$$로 적으면서 문장으로 projectile 중심 상태라고 정의한다. **움직이는 중심 $\mathbf r-\mathbf R(t)$를 구현에서 명시하는 것은 그 기하를 풀어 쓰는 것이며, 원문에 명시적 인자가 인쇄되어 있다고 인용하면 안 된다.**

식 (5)의 전자 Hamiltonian은 두 핵의 Coulomb 퍼텐셜과 전자 운동에너지다. 식 (6)은

\[
i\dot c=S^{-1}(b,v,t)M(b,v,t)c
\]

를 제시하고 $S$를 overlap, $M$을 coupling matrix라고 부른다. 따라서 비직교 metric을 유지하는 AOCC 전개는 직접적인 원전 근거가 있다. 다만 본문은 모든 $S_{ab},M_{ab}$ 적분·시간미분 항을 전개하지 않으며 상세 방법은 참고문헌 [26]으로 돌린다. A1의 $S=X^\dagger X$, $D=X^\dagger\dot X$, $M=h-i\hbar D$ 및 $c^\dagger Sc$ 보존은 **우리의 정의와 직접 유도**로 제시해야 한다.

식 (7)은 transition probability를 계수의 절댓값 제곱으로 제시한다. 그러나 이 짧은 방법 절은 유한 종료 시간에서의 두 중심 overlap 허용치, 채널 투영 오차 상한, Coulomb 장거리 위상 제거법을 지정하지 않는다. 따라서 식 (7)만으로 임의의 유한 $R$에서 “계수 제곱=유일한 최종 capture probability”를 정당화할 수 없다. §3 첫 문단은 GTO가 $L^2$ 함수여서 정확한 연속상태 경계조건을 기술하지 못한다는 한계를 명시한다. 이점은 bound-channel formalism의 완결과 ionization/continuum 수렴을 구분해야 할 이유다.

## 2. P03 Liu et al. (2003): MO-ETF의 유한 거리 비유일성과 점근 채널

출처: DOI [10.1103/PhysRevA.67.052705](https://doi.org/10.1103/PhysRevA.67.052705), §I PDF 1–2쪽; §II.A PDF 2–3쪽; §II.C PDF 5–6쪽, 식 (35)–(40). PDF 6쪽의 matching 설명과 식 (36)–(40)을 시각 확인했다.

§I는 분리된 원자 전자의 병진 운동을 원자궤도에 평면파 ETF를 붙여 표현하더라도, 그 조건은 유한 핵간 거리에서의 MO 병진 처리법을 정하지 않는다고 설명한다. 서로 다른 switching function을 사용하는 MO-ETF가 그 결과다. 이는 **점근 ETF 조건만으로 유한 $R$ MO embedding이 유일하게 결정되지 않는다**는 원전 근거다. AOCC가 임의의 유한 기저에서도 완전하다는 주장, 모든 MO-ETF가 틀렸다는 주장, 특정 새로운 switching 처방의 검증으로 확대하면 안 된다.

이 논문은 별도의 양자 3체 HSCC 정식화를 사용한다. hyperradius와 핵간 거리는 동일한 좌표가 아니며, 세 Jacobi arrangement의 전자·핵 질량을 포함한다. §II.C 식 (35)에서 분리된 원자의 hydrogenic bound state와 heavy-particle 상대 운동을 조합하여 내부 $R$-matrix 해와 match한다. 다음 두 채널은 구분된다.

| 점근 arrangement | 원문이 사용하는 상대 운동 함수 |
|---|---|
| $\mathrm{He}^{2+}+\mathrm H$ | regular Bessel / irregular Neumann |
| $\mathrm H^++\mathrm{He}^+$ | regular / irregular Coulomb |

식 (36)은 각 Jacobi 채널의 wave number와 **각 reduced mass**를 통해 동일한 $E-U_n(\infty)$를 나타낸다. 따라서 entrance의 neutral-atom 장거리 거동과 exit의 두 이온 Coulomb 거동을 동일한 free phase로 다루는 것은 이 원문과 맞지 않는다. 다만 **우리 semiclassical 전자 Hamiltonian에서의 “상대 핵 중심별 monopole 위상”, 그 부호, logarithm/asinh 표현은 이 논문의 식을 그대로 옮긴 결과가 아니다.** 전자 Hamiltonian에 nuclear repulsion scalar를 넣었는지 여부까지 고정하여 직접 유도해야 한다.

유한 matching radius와 degenerate final channels에 관해 PDF 6쪽은 특별히 강한 주의를 준다. $\mathrm{He}^+(2s)$와 $\mathrm{He}^+(2p)$의 점근 에너지는 축퇴하며, 안쪽 adiabatic 채널은 각 partial wave $J$에서 비정수 또는 복소 angular momentum을 갖는 dipole states와 연결된다. 이 논문의 간소화된 matching은 개별 $2s,2p$ capture를 보고하지 않고, **둘의 합이 matching radius에 의존하지 않음을 확인한 뒤 합만 보고한다.** 개별 채널은 two-dimensional matching 또는 Coulomb function 대신 dipole state를 쓰는 matching이 가능하다고 적는다.

이 점은 A1b의 $n=2$ 부분공간과 그 안의 특정 $l,m$ 채널을 구분하는 근거다. 그것이 고전 궤적 전자 전파에서도 개별 $2s/2p$ 투영이 원천적으로 불가능하다는 뜻은 아니다. 정식화가 다르므로 해당 관측량의 점근 분석과 오차 통제를 별도로 해야 한다.

## 3. P08 Winter (2007): two-center basis와 종료 구간 검증

출처: DOI [10.1103/PhysRevA.76.062702](https://doi.org/10.1103/PhysRevA.76.062702), §II.A–B, PDF 1–2쪽 / 062702-1–2; §II.C 및 §III.A 첫부분 PDF 3쪽. P08은 이전 A1 manifest에 없으므로 이전 **B1 SOURCE_MANIFEST**의 SHA-256을 기준으로 검증했다.

§II.A는 고전 직선 궤적과 He+/H의 two-center approximate atomic eigenstates를 사용한다. 각 중심 atomic Hamiltonian을 Sturmian basis에서 대각화하며 positive-energy pseudostates도 포함한다. 계수의 절댓값 제곱이 transition probability가 되는 것은 명시적으로 **asymptotically**라고 기술한다. 이 방법 요약은 ETF 위상식을 직접 쓰지 않는다. P01의 ETF를 P08의 인쇄된 식인 것처럼 병합하여 인용하지 않는다.

§II.B는 핵 운동 좌표 $z=vt$의 전파 종료 $z_{\max}$와 charge-exchange matrix element 평가의 제한 $R_{\max}$를 서로 다른 수치 파라미터로 구분한다. 69-state reference basis의 비교에서 $z_{\max}=500a_0$를 $1000a_0$로, $R_{\max}=40a_0$를 $50a_0$로 각각 변경하는 등 파라미터 민감도를 검사한다. 이것은 종료/평가 구간 민감도를 별도로 확인해야 한다는 사례이며, A1b에 그 숫자를 보편적 asymptotic cutoff로 이식할 근거는 아니다. Table I의 검사는 production basis 전체에 대한 독립된 엄밀 오차 상한이 아니다.

## 4. P02 Stolterfoht et al. (2010): metric을 포함한 최종상태 투영

출처: DOI [10.1103/PhysRevA.81.052704](https://doi.org/10.1103/PhysRevA.81.052704), §II PDF 2–3쪽 / 052704-2–3. END는 전자와 결합된 고전 핵 궤적을 사용하며, AO에 ETF를 포함한다. 고정 직선 궤적 AOCC와는 핵 운동 모델이 다르다.

PDF 3쪽의 기본 정의는 $P_f(b)=|\langle\psi_f|\psi_i(\infty)\rangle|^2$이며, 최종 projectile atomic state로 투영한다. 같은 문단의 다음 shorthand는 $P_f=z_f^\dagger S z_i$로 인쇄되어 있지만, 이 표현 자체는 일반적으로 복소 진폭이고 기본 정의의 절댓값 제곱이 없다. 따라서 구현에서는 앞의 확률 정의를 따라야 하며, 뒤의 shorthand를 무비판적으로 복사하지 않는다. 원문에서 “명시된 약식과 기본 정의의 불일치”로 기록하며 새 보정 값을 만들어내지 않는다.

이 논문은 궤적을 projectile/target electronic charge에 더 이상 변화가 없을 때까지 진행한다고 설명한다. 이것은 실무적 종료 판단의 원전 사례다. 개별 채널 진폭의 장거리 위상 수렴, 다른 basis의 수렴 또는 엄밀한 tail bound까지 입증하는 조건은 아니다.

## 5. A1b에서 사용할 수 있는 주장 범위

* **literature-supported:** atomic-centered translating channels, 내부 에너지 위상과 ETF 위상의 구분, 비직교 overlap 유지, 점근 채널 투영, 유한 전파/matching 구간 민감도 확인의 필요성.
* **literature-supported:** 점근 atomic ETF가 유한 $R$ MO switching을 유일하게 정하지 않음; 양자 HSCC의 entrance/exit 장거리 함수와 reduced mass 차이; $n=2$ 축퇴 채널 matching의 주의점.
* **derived로 따로 제시할 것:** $m_e,\hbar$를 유지한 이동기저 Hamiltonian, 중심별 Coulomb monopole 위상 제거, 그에 따른 coefficient convention과 로그 위상의 부호, metric projector와 finite-time projection 식, 동일 finite-span gauge와 다른 finite-span embedding의 구분.
* **unresolved / not evaluated:** 새 finite-$R$ embedding의 collision 정확도, overlap spectrum, basis/continuum 수렴, 끝점 오차 상한, 개별 state-resolved cross section, 0.5/5 keV/u의 실제 계산. 이 노트는 어떠한 production 또는 PROMOTE gate도 변경하지 않는다.
