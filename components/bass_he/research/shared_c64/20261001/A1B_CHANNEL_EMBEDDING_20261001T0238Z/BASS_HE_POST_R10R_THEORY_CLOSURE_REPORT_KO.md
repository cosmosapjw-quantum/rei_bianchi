# A1b 결과: 실제 ETF 기저와 exact P/Q completion

**A1 정식화를 `FRAME_COMPLETE_CONNECTION_DERIVED`로 판정했다.** 범위는 prescribed classical nuclear trajectory를 따르는 단일전자 비상대론적 **exact P⊕Q formulation**이다. A1b는 `A1_PHYSICAL_CHANNEL_EMBEDDING_SPECIFIED`다. 독립 검토가 이를 확인했고 다음 단일 node는 원래 DAG의 **A2 — small/large-R analytic structure**다. Six-channel-only 정확도, 실제 단면적 또는 전체 프로그램 완료는 아니다. C1은 A2까지 대기한다.

이번에는 H(1s) 하나와 He⁺(1s,2s,2p_x,2p_y,2p_z)의 정규화된 원자 함수로 유한 P 공간을 정했다. 각 중심의 속도 ETF와 원자 에너지 위상에 다른 핵의 −κ/R monopole을 보상하는 시간 위상을 넣었다. 고정 lab r에서 직접 미분하면

\[
(H-i\hbar\partial_t)\chi_{C\nu}=
\left[-\frac{\kappa_{\bar C}}{|r-X_{\bar C}|}
+\frac{\kappa_{\bar C}}R+m_e\dot v_C\cdot\rho_C\right]\chi_{C\nu}.
\]

운동량·kinetic boost 항이 상쇄되고 가속항은 +m_e a_C·ρ_C로 남는다. 이 residual을 직접 적분하는 M=h−iℏD 계산형도 명시했다. 핵 반발 공통 phase를 복원하면 중성 entrance의 monopole은 0, H⁺+He⁺ exit는 +κ_A/R가 되어 전하·부호가 일치한다. 장거리 phase와 과거 문헌의 quantum nuclear matching을 동일한 계산으로 주장하지 않았다.

중심 간 overlap s=V†u에 대해 S=[[1,s†],[s,I₅]], δ=1−s†s다. H 중심의 cusp와 He 중심 함수들의 해석성을 이용하여 모든 R>0에서 δ>0를 증명했다. 이는 수치 조건수가 작다는 인증은 아니다. 원자 orbital의 제한된 R=0/common-boost fixture에서는 δ=139/2916>0다. 따라서 합체가 이 기저의 선형종속을 자동으로 뜻하지 않지만, 사용한 1/R 시간 phase를 R=0 경로에 적용하지 않는다.

유한 시각의 He projector 값은 p_B=||b+s a||²다. 원자 H와 He projector는 유한 거리에서 서로 직교하지 않아 각 계수 제곱이나 두 projector의 합을 배타적 확률로 사용할 수 없다. 점근적으로 s→0이고, 명시한 선형 분리·가속도 tail 조건에서 보상된 6차원 generator가 시간 적분 가능하여 이 근사 모델의 산란 극한이 존재한다. 유한 T 오차와 full Hilbert-space completeness는 별도 문제다.

처음 만든 6채널 후보에는 exact R10R g,b의 projection remainder가 남았다. 독립 검토는 이를 원계약의 A1 완료로 부를 수 없다고 지적했다. 실제 해결로 Ψ=Ya+η, Y†η=0를 유지하는 **exact P/Q dynamics**를 추가했다. Γ=[Pdot,P]+Y(Y†Ydot)Y†로 complement를 unitary parallel transport하고,

\[
\mathbb K=\begin{pmatrix}K_{PP}&K_{PQ}\\K_{QP}&K_{QQ}\end{pmatrix},
\qquad K_{QP}=Z^\dagger(HY-i\hbar\dot Y),\quad K_{PQ}=K_{QP}^\dagger
\]

를 정의했다. Full body-frame generator에는 rotation, translation, ETF와 phase connection이 함께 들어간다. Exact R10R matrix element는 네 P/Q block 모두를 통한 unitary dictionary에서 원래 값을 유지한다. 6채널에 빠진 세 remainder를 0으로 가정하지 않는다. Q를 제거하면 initial-Q source와 coherent memory/backcoupling이 남으며, 이를 임의의 양의 rate나 irreversible sink로 바꾸지 않았다.

독립 검토는 H¹ form-domain 보존, strong η equation의 추가 domain 조건, body L의 unbounded domain, block adjoint와 memory kernel 부호·단위를 확인했다. Initial candidate-only 판정과 P/Q 보강 전후 파일 identity를 리뷰에 보존했다. Source-specific CPC omega adapter는 이 explicit active-frame formulation에 사용하지 않아 미확정 상태로 남지만 현재의 정식화 폐쇄를 막는 입력 의존성은 아니다.

실제로 새로 수행한 검증은 다음과 같다.

| 검증 | 결과 | 적용 범위 |
|---|---|---|
| Wolfram exact CAS 1회 | 정규화·overlap·dipole exact 값, ETF/asinh 미분 residual 0 | 직접 유도의 대수 확인 |
| 새 Gram/projector unit tests 8개 | PASS | 주어진 s의 유한차원 구현 |
| 별도 P/Q fixture 1회, residual 15개 | PASS; max 2.49×10⁻¹⁴ ≤ 2×10⁻¹² | Γ·Hermiticity·P/Q norm exchange |
| 별도 저자의 독립 검토 | FORMULATION_CLOSURE 확인 | exact P⊕Q 및 명시한 domain/경로 범위 |

기존 A1의 12개 tests, R10R proof, unchanged scientific suites는 exact dependency를 확인하여 재사용했고 재실행하지 않았다. 원전은 P01/P03/P02/P08을 필요한 부분만 읽었으며 4개 PDF의 hash/bytes가 일치했다. 새 네트워크 문헌 취득은 없었다. B1의 1,131개 native cells와 13행 matrix 및 Minami A3 색인 정정도 그대로 유지했다.

새 Coulomb eigensolve, 물리 overlap grid, spatial quadrature, collision propagation, impact integration, continuum/channel convergence, Q memory 수치 계산, benchmark fitting/비교는 **NOT_RUN**이다. Exact BO projection coefficients와 finite-R coupling 크기, 전체 error ledger는 미완료다. 다음 A2에서 united-atom selection과 leading admixture, separated-atom origin lever 및 ETF-completed asymptotics를 실제 유도해야 한다. 특히 Coulomb singularity/cusp 때문에 외부 multipole series를 R=0까지 무조건 적용하지 않는다.

```text
CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN
production_default_change=NOT_AUTHORIZED
```

자세한 수식은 `A1B_CHANNEL_EMBEDDING_DERIVATION_KO.md`, 판정 근거는 `review/A1B_INDEPENDENT_REVIEW.json`, 다음 실행 계약은 `NEXT_HANDOFF_KO.md`다. Publication 및 provider backup identity는 외부 delivery receipt가 소유한다.
