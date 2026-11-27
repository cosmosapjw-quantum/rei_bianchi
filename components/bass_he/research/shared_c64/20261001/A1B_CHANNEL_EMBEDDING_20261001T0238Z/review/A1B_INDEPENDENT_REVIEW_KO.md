# A1b 독립 물리·수학 검토

최종 판정: **A1b의 명시적 원자 채널 선택과 exact P⊕Q 보강 정식화를 독립 검토했다.** A1b에는 `A1_PHYSICAL_CHANNEL_EMBEDDING_SPECIFIED`, parent A1에는 `FRAME_COMPLETE_CONNECTION_DERIVED`를 prescribed-classical-path 전자 문제의 정식화에 한정해 부여할 수 있다. 원래 DAG의 다음 단일 node는 **A2: SMALL_R_LARGE_R_ANALYTIC_STRUCTURE**다. 6채널 Galerkin 정확도, 실제 collision 계산, 과학적 promotion은 이 판정에 포함되지 않는다.

초기 검토에서는 candidate-only generator가 R10R의 omitted-sector 항을 포함하지 않는다는 한계를 지적했다. 작성자가 같은 A1b 본문 §9에서 exact complement와 그 coherent 교환을 실제로 정의했으며, 그 추가 부분만 targeted 검토했다. 초기 판정과 최종 판정의 차이는 gate를 완화한 결과가 아니라 명시적인 수학적 보강의 결과다. 전후 identity와 판정은 동반 JSON에 남긴다.

검토자는 본문·병렬 수학 노트·코드를 작성하지 않은 별도 agent다. 원자 함수와 위상, Gram/projector, domain과 tail, R10R 연결의 주장 범위를 직접 재유도했다. 새 테스트의 소스·기록과 CAS raw response를 읽었으며 기존 또는 새 테스트/CAS를 다시 실행하지 않았다. 정확한 검토 파일 identity는 동반 JSON에 기록한다.

## 1. 확인한 수학

1. B.2–B.3의 H1s 및 He1s/2s/Cartesian 2p 정규화와 직교성은 맞다. 전자 질량을 공통으로 사용하는 고정핵 문제에서 H1s와 He n=2의 에너지 축퇴도 맞다. 공통 속도·위상을 제거한 합체 orbital fixture는 s=(16√2/27,−1/2,0,0,0), δ=139/2916이며, 1s–2px dipole은 (64√2/243)a_A다. R=0 Gram fixture가 Coulomb phase의 R=0 통과를 허용하지 않는다는 제한을 지켜야 한다.
2. 고정 lab r에서 phase 미분의 운동학적 항은 m a_C·ρ_C−m v_C²/2다. 원자 에너지와 monopole 항까지 포함하면 (H−iℏ∂t)χ=[V_other+κ_other/R+m a_C·ρ_C]χ가 된다. 가속항은 양의 부호다. 운동량 교차항 및 kinetic scalar는 정확히 상쇄된다. ℏ 및 질량·길이·시간 차원은 일관된다.
3. 전자 Hamiltonian만 사용할 때의 +κ_other∫dt/R 비교 위상과, 핵 반발을 복원할 때의 공통 −∫2k dt/R 위상을 구분한 처리는 맞다. 입사 중성 채널의 leading monopole은 소거되고 출사 두 양이온에는 +k/R potential, 즉 phase exponent에는 −k∫dt/R가 남는다.
4. R>0에서 A 중심의 nonzero 1s cusp와 B 중심 함수들의 A 근방 해석성을 비교한 선형독립 증명은 타당하다. 따라서 Gram matrix는 점별 양의 정부호다. λ=1±||s|| 및 1의 4중 고유값, 삼각 직교화 W, Wdot와 metric identity가 맞다. 이 증명은 모든 충돌 parameter에 대한 균일한 conditioning 상한은 아니다.
5. 물리 projector의 p_B=||b+s a||² 및 p_A=|a+s†b|², 직교 분할 p_B+δ|a|²=c†Sc는 맞다. 유한 R에서 p_A+p_B를 배타적 합으로 취급하면 안 된다. 순수 u의 직교 좌표는 (√δ,s)다. 여기의 projectile projector는 선택한 He1s+n2 부분공간이며 전체 He bound spectrum을 뜻하지 않는다.
6. 선택한 orbitals는 H²에 속하고 이동/유한 boost 후에도 strong Hχ와 χdot가 존재한다. Coulomb singularity의 국소 L² 적분 및 exponential tail을 사용한 O(R⁻²) orbital residual bound가 타당하다. R≳|t|, bounded velocity, acceleration O(t⁻²)의 충분조건 아래 compensated finite-dimensional K는 시간 적분 가능하고 선택된 Galerkin 모형의 unitary scattering matrix를 정의한다. exact full-Hilbert scattering completeness는 증명되지 않는다.
7. 최종 본문 §10의 Q_N(HX−iℏXdot)c는 Galerkin state의 omitted-space defect이며, Duhamel 노름 경계에는 부호가 영향을 주지 않는다. 전자 propagator와 적절한 domain regularity를 별도로 가정한 점이 정확하다. 이 defect의 실제 크기는 계산하지 않았다.
8. B.18–B.21의 같은 원자 중심 off-diagonal momentum cancellation 및 origin-lever 항은 서로 모순되지 않는다. bare L의 nonzero를 dressed K 또는 capture amplitude의 nonzero로 옮길 수 없다. 원래 full R10R matrix element가 전부 상쇄되었다는 주장은 현재 결과로 정당화되지 않는다.

## 2. 출처와 계산 증거

기존 hash-bound 원문에서 P01 PDF 3의 AOCC/ETF 식, P03 PDF 6의 neutral/ionic matching 및 2s/2p 축퇴 주의, P08 PDF 2의 asymptotic coefficient probabilities와 별도 cutoff 검사를 직접 읽었다. 이 원문들이 이번 6채널 근사나 새 monopole phase 자체를 검증했다고 주장하지 않는 출처 분리는 타당하다. P02 관련 상세 원문은 이번 독립 검토에서 재열람하지 않았으며 source-note 작성자의 근거로 남긴다.

작성자의 새 matrix tests 8개는 기록상 PASS이며, ambient-space reference projector, finite-overlap 반례, unitary covariance, coherent cancellation 및 잘못된 입력 거부를 실제로 검사한다. helper는 주어진 overlap vector의 대수만 구현하고 orbital overlap을 계산하지 않는다. CAS raw response는 정규화·중첩·dipole의 정확한 값과 ETF/asinh derivative의 zero residual을 반환한다. 이것은 수치 충돌 계산이나 정확도 인증이 아니다. 검토자가 추가로 실행한 과학 테스트, CAS, eigensolve, collision solve는 모두 0회다.

## 3. 추가된 exact P/Q 보강의 검토

초기 문서의 B.16–B.17은 exact bare R10R 행렬요소를 projected term과 세 remainder로 분해했지만, 그 remainder가 당시 6채널 K에는 없었다. 이것만으로 원계약 §5/§29의 exact-sector embedding 완료를 선언할 수 없다는 초기 판단은 유지한다. 보존된 `provenance/A1B_PRE_PQ_DRAFT_KO.md`가 그 검토 대상이다.

최종 §9는 Ψ=Ya+η, Y†η=0를 두고 complement를 명시적으로 유지한다. 제약을 미분하면 Y†ηdot=−Ydot†η이므로 finite-sector 식은 iℏadot=K_PP a+F†η, F=HY−iℏYdot가 된다. 나머지 TDSE에 이를 대입하면 iℏηdot=(QHQ−iℏPdot)η+QFa를 얻는다. 움직이는 Q 제약을 유지하는 −iℏPdot의 부호와 두 sector의 반대 방향 norm exchange를 확인했다. η=0 및 QFa 무시는 이제 별도로 이름 붙인 Galerkin 근사다.

Γ=[Pdot,P]+Y(Y†Ydot)Y†는 anti-Hermitian이고 ΓY=Ydot, QΓQ=0를 만족한다. 따라서 Γ가 생성하는 unitary transport는 선택 Y를 그대로 운반하며 complement를 한 가지 명시적 parallel transport로 완성한다. Y∈H², Ydot∈H¹와 유한 구간 norm의 유계성으로 Γ는 H¹에서도 bounded finite rank이므로 U_*의 form-domain 보존이 정당화된다. 일반 H² 보존을 가정하지 않은 점이 중요하다.

이 완성에 의해 K_QP=Z†F, K_PQ=F†Z, K_QQ=q_t(Z·,Z·)가 된다. 제한된 Coulomb form은 dense domain H¹∩Ran Q_*에서 닫힌 semibounded form이며, 시간 regularity를 포함한 명시 조건 아래 full generator가 자기수반이다. Q의 수치 spectrum이나 coupling을 모르는 것과 generator의 정의가 없는 것은 다르다. 현재 보강은 후자를 해결했으며 전자는 후속 계산으로 남긴다.

B.29의 body expression은 p,L 및 시간미분이 정의되는 공통 domain에서 lab expression의 unitary pullback이다. 모든 H¹ vector에 angular momentum form을 적용하지 않는 제한을 확인했다. J_b가 onto이므로 B.30의 full-coordinate matrix element는 exact R10R L_gb를 P–P/P–Q/Q–P/Q–Q 네 block 전체에 보존한다. 따라서 bare term을 다른 유한 원자 상태와 동일시하거나 remainder를 0으로 놓지 않고도, 원래 R10R operator contribution의 정확한 위치를 하나의 coherent generator 안에 제시한다. 전체 dressed amplitude나 observable의 nonzero는 이 identity로부터 나오지 않는다.

B.31–B.32의 complement 제거식은 −i/ℏ 부호의 coherent memory kernel을 가진다. Kernel의 energy²와 dt/ℏ의 조합도 맞다. 초기 complement가 0이어도 backcoupling은 일반적으로 남으며, 이를 양의 rate로 바꾸지 않은 점을 확인했다. 기존 Q12 probability에서 phase를 복원하지 않고 같은 full operator와 basis의 derivative coupling으로 coherent dynamics를 정의하는 것은 명시적인 정식화 선택이다. Q12의 별도 정량적 correspondence를 완료했다는 뜻은 아니다.

새 P/Q fixture의 소스와 실제 evidence에는 15개 대수 residual이 기록되어 있으며 최대 2.4868995751603507×10⁻¹⁴, 고정 절대 허용오차 2×10⁻¹²로 PASS다. 소스·로그 identity도 기록과 일치했다. instantaneous finite-dimensional 검산이며 continuum, ODE 또는 실제 collision 실행은 아니다. 검토자는 이를 재실행하지 않았다.

## 4. 최종 gate와 다음 일

추가된 exact complement, frame dictionary 및 approximation 분리로 **원래 A1의 formulation closure**를 지지한다. 다음 A2는 exact R10R bare bright sector의 small/large-R 구조와 frame-completed contribution의 차이를 분석하면 된다. 새로운 기저를 benchmark에 맞추거나 수치 residual을 먼저 작게 만들어야 A2를 시작할 수 있다고 요구하지 않는다. C1은 원래 DAG의 A2 선행조건을 충족한 뒤 시작해야 하므로 이번 검토만으로 C1/collision 실행을 직접 해제하지 않는다.

후속으로 남는 것은 실제 BO coordinates, P/Q exchange와 truncation residual의 크기, finite-R matrix elements, conditioning, 공간 적분·채널·continuum 수렴, 궤적 오차와 benchmark comparison이다. CPC의 ω adapter는 현재 lab/active-frame 정식화에 사용하지 않았으므로 import 전까지 unresolved로 유지한다. Full P/Q의 unitarity는 선택된 6채널 확률 합이 1임을 뜻하지 않으며 full continuum의 asymptotic completeness도 증명되지 않았다. 6D S-matrix의 unitarity는 6D Galerkin 근사에 한정한다.

`scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED` 및 기존 fail-closed gate를 모두 유지한다. 이번 판정은 exact classical-path electronic frame/embedding의 정의 완료이며, 전체 물리 정확도나 production readiness 완료가 아니다.
