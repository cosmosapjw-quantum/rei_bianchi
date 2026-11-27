# BASS_HE — R10R 이후 첫 A1/B1 연구 루프 보고서

**이번 결과는 일반 연결식의 범위 내 확립과 원문 수치 권위의 확장이다. 전체 물리 모형의 폐쇄는 아니다.** A1의 형식적 유도는 `DERIVED_AND_INDEPENDENTLY_REVIEWED_IN_SCOPE`, 물리 node는 `FRAME_CONNECTION_GAP_IDENTIFIED`다. B1은 `PRIMARY_NUMERIC_AUTHORITY_MATRIX_PARTIAL`이며, 에너지·채널·원전별 제한을 모두 해소한 benchmark authority는 아직 `SOURCE_AUTHORITY_UNRESOLVED`다. 다음 단일 작업은 **A1b — 점근 채널 embedding과 finite-R ETF 선택**이다. `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`을 유지한다.

이 보고서의 파일명에 포함된 “closure”는 사용자 지정 산출물명이다. 첫 bounded loop의 종료 기록이며 A1–G1 전체 완료를 뜻하지 않는다. 게시 commit과 원격 백업 확인 수준은 이 보고서가 아닌 별도 delivery receipt에서 확정한다.

## 1. 입력과 재사용 범위

입력은 변경하지 않은 `BASS_HE_PRIMARY_SOURCE_ARCHIVE_20261001_v3.zip`이다. SHA-256은 `0f9dc51cc013aa0b91e7f3ff560bbca5afd1ee1551b67c8bb33278c445b1cd84`, 크기는 26,874,721 bytes다. ZIP CRC와 manifest의 252 payload 해시를 확인했다. 선정된 39개 source는 published PDF 24개, raw dataset 파일 6개, code source 9개이며, 별도 검색 단서 197개를 확보된 원문으로 승격하지 않았다.

시작 시 publication HEAD는 `8e458fe1588bbf575add541caffc4ed422dc4c48`, scientific source pin은 `1a83a67e12de1ddc2aede0ff67168f7071450ab3`였다. 두 revision 사이 41개 변경은 연구 기록 추가였고 관련 scientific dependency는 바뀌지 않았다. 선택한 7개 code module의 byte identity도 일치했다. 따라서 기존 closed suite를 다시 실행하지 않고 R10R proof admission과 원래의 적용 조건을 재사용했다. 실제 게시 시점의 HEAD는 delivery receipt에서 구별한다.

R10N의 ScienceDB exact 5.0-keV/u 부재, R10O의 frozen stochastic graph 식과 2배 bound, R10P의 당시 판정은 역사적 결과로 보존했다. R10O의 bound를 coherent amplitude, upper-shell return, 확장 채널에 적용하지 않는다. R10R의 nonzero theorem도 지정한 fixed finite R, exact sector ground states, charge-center origin, meridional phase와 form-domain 조건 안에서만 사용한다.

## 2. A1에서 새로 확립한 연결식

전자 하나, spinless, 비상대론적 clamped point-Coulomb Hamiltonian과 미리 주어진 매끄러운 핵궤적을 전제로 했다. 핵궤적 자체나 양자핵 산란은 풀지 않았다. 이동기저 사상 \(X=[\chi_1,\ldots,\chi_N]\), Gram matrix \(S=X^\dagger X>0\), \(D=X^\dagger\dot X\), Hamiltonian form \(h_{ab}=q_t(\chi_a,\chi_b)\)에 대해

\[
i\hbar S\dot c=(h-i\hbar D)c,\qquad \dot S=D+D^\dagger.
\]

따라서 \(c^\dagger Sc\)가 보존된다. \(W^\dagger SW=I\), \(c=Wa\)로 직교정규 표현을 만들면

\[
i\hbar\dot a=Ka,\qquad
K=W^\dagger(h-i\hbar D)W-i\hbar W^\dagger S\dot W,
\qquad K=K^\dagger.
\]

마지막 \(\dot W\) 항은 생략할 수 없다. 일반 \(S^{-1}(h-i\hbar D)\)를 Euclidean Hermitian matrix로 강제 대칭화하지 않는다. 이 결과는 정해진 유한 basis의 projected equation에 대한 보존법칙이다. 누락 공간의 weak residual, 채널·연속체 오차 또는 단면적 정확도를 제한하지 않는다. Coulomb form domain \(H^1\)과 \(\dot\chi\in L^2\)를 사용하며, \(H\chi\)라는 strong vector 표현은 별도의 \(\chi\in D(H)\) 조건이 있을 때만 쓴다. R10R의 \(L\psi\in D(H)\)를 새로 가정하지 않았다.

Body→lab active rotation을 \(r=O+Qx\), \(V=Q^T\dot O\), \(Q^T\dot Qx=\Omega\times x\)로 정했다. 같은 unboosted clamped orthonormal basis에서는

\[
K^{(0)}=E-i\hbar\dot R F_R-\Omega\cdot L-V\cdot P.
\]

이에 따라 R10R의 bare \(L_{gb}^{O_c}=-i\hbar C_RT_R/\Delta_R\ne0\)는 정확히

\[
K^{\rm rot}_{gb}=+i\hbar\dot\theta C_RT_R/\Delta_R
\]

에 놓인다. 이것은 부호와 위치의 확립이며 수치 크기나 ETF-completed collision amplitude의 nonzero 증명이 아니다. 기존 Q12는 hidden-crossing branch/probability 표현이므로 그 확률만으로 (F_{R,ge}(t))와 coherent phase를 복원할 수 없다. (P_{Q12}+P_{angular}) 또는 임의의 양의 rate를 추가하지 않았다.

동일 span의 gauge에서는 \(K'=U^\dagger KU-i\hbar U^\dagger\dot U\)를 확인했고, 퇴화 subspace에는 비가환 unitary block이 필요하다. 원점 이동 \(O'=O+Qs\)에서는 \(L'=L-s\times P\), \(V'=V+\Omega\times s+\dot s\)와 intrinsic basis derivative의 \(+\dot s\cdot P\)가 함께 상쇄된다. 개별 bare \(L\)이나 derivative coupling이 원점 불변이라는 주장이 아니다. Common boost의 운동량·위상 미분도 일관되게 포함했으며, \(u=V\)일 때 남는 관성항은 \(m_e(\dot V+\Omega\times V)\cdot x\)다.

채널별 ETF를 \(\chi_a=e^{i\eta_a}\psi_a\)로 정하면 일반적으로 \(S\ne I\), \(h\ne\mathrm{diag}(E)\)다. \(S,h,D\)를 ETF가 포함된 전체 기저에서 한 번 계산해야 한다. 채널마다 다른 공간 위상은 유한 physical span 자체를 바꿀 수 있으므로 자동으로 동일-span gauge가 아니다. 이것이 단순 “bare coupling + ETF 보정” 합산을 피하는 정확한 구성 원칙이다.

## 3. A1이 아직 닫히지 않은 이유

현재는 어떤 \(\eta_a\), localized asymptotic subspace와 finite-R continuation이 실제 He–H 문제를 정의하는지 선택하지 않았다. 무한 핵질량 근사에서 H(1s)와 He⁺(n=2)의 점근 에너지가 같으므로 adiabatic state label만으로 parent center를 지정하기도 충분하지 않다. Incoming/outgoing projector, overlap spectrum의 비특이성, 실제 \(S,h,D\), coherent radial amplitude 자료가 필요하다.

P01 Liu2024의 AOCC ETF/overlap 식, P03 Liu2003의 finite-R MO ETF ambiguity, P24 Belyaev–Dalgarno–McCarroll의 전체 핵운동 operator 변환을 구분해서 사용했다. P24의 Jacobi reduced electronic mass를 현재의 clamped \(m_e\)로 무단 치환하지 않았다. Full quantum nuclear coordinate covariance는 prescribed-classical-path 전자 방정식의 물리적 완전성 인증이 아니다. Athavale ETF/ERF 자료는 명시한 근사 안의 보조 자료이며, 공선 이원자 기하의 rank 제한을 무시한 역행렬 처방을 채택하지 않았다. Buenker–Li는 full text 미확보 항목으로 남겼다.

CPC의 \(+\omega L_z\)와 현재 \(-\dot\theta L_y\) 사이에는 축 이름뿐 아니라 회전 방향 정의의 검증이 필요하다. Proper axis permutation 자체로 부호가 뒤집히지 않는다. Source-oriented \(\omega\) completion도 아직 열려 있다. 이 이유로 A2와 C1–G1의 물리 계산을 시작하지 않았다.

## 4. 실제 수행한 검증과 수정

새 `connection_algebra.py`는 같은 기저에서 온 metric/derivative 조건과 Hermiticity를 검사한다. 특이하거나 너무 ill-conditioned인 S, 잘못된 \(\dot S\), 빠진 \(\dot W\), nonfinite 값과 non-Hermitian 입력은 실패시킨다. 결과 K를 사후 대칭화하지 않는다.

작은 행렬 fixture **12개가 PASS**했다. Static limit, metric norm, 직접 직교기저 표현과의 일치, rephasing/비가환 covariance, constant-H exponential, 원점 상쇄, common boost, R10R 부호와 실패 사례를 포함한다. Test tolerance는 \(2\times10^{-12}\), matrix validation은 (10^{-12})였고 이 값들을 물리 convergence 기준으로 사용하지 않았다. 첫 실행은 11 PASS/1 FAIL이었다. Bright-term의 부동소수 완전일치 assertion을 이미 정해진 tolerance 비교로 고쳤으며 물리식·허용오차를 바꾸지 않았다. 첫 실패와 수정 기록을 보존했다.

Wolfram algebra evaluator는 **실제 2회** 호출했다. 첫 결과는 0 residual들과 wrapper warning을 함께 반환했으며 대화 출력의 transcript로 보존했다. 원 transport envelope라고 주장하지 않는다. 두 번째 raw response에는 common boost, quantum nuclear chain rule, unitary/Hermitian matrix residual 및 diatomic rank fixture가 남아 있다. 별도 context 조회는 connector 내부 오류로 실패했고 그 기록도 보존했다. CAS 결과를 독립 물리 검토로 세지 않았다.

작성에 참여하지 않은 별도 검토자가 식·단위·부호·domain·claim ceiling을 검토했다. (1) form-domain에서 strong residual을 사용한 표현, (2) P24 Eq.(17)이 \(\langle iL_y\rangle\)의 식이라는 점을 고쳐야 한다는 두 지적을 수용했다. 국소 수정본 재확인으로 둘 다 닫혔고 검토된 파일 SHA-256을 확인했다. 독립 검토 판정은 형식적 유도 범위에 한정된다. 새 Coulomb eigensolve, collision solve 또는 단면적 적분은 **0회**다.

## 5. B1의 새 원문 수치와 중요한 정정

**Minami2008 P04에는 Appendix Tables A1–A12가 있고, Table A3는 native 5 keV/u를 명시한다.** PDF 8쪽/인쇄 7쪽이다. v3의 “numbered table header를 찾지 못했다”는 결과는 letter-prefixed appendix header를 놓친 색인 오류였다. 원 v3를 수정하지 않고 `B1/SOURCE_RECOVERY_ERRATA.json`으로 정정했다. 별도 author raw file의 미확보와 PDF 내 수치표 존재를 분리한다.

A3의 원문 n=1 capture 값은 다음과 같다. 단위는 cm²이며 새 합계나 보간값이 아니다.

| 원문 방법 열 | n=1 capture |
|---|---:|
| LTDSE | 1.95×10⁻¹⁹ |
| AOCC-A | 2.55×10⁻¹⁹ |
| AOCC-B | 2.33×10⁻¹⁹ |
| CTMC | 3.20×10⁻¹⁷ |

AOCC-A는 논문이 인용·수록한 Toshima/NIFS 자료로, Minami가 새로 계산한 독립 값으로 바꾸지 않았다. P04 자체는 lab/CM frame을 명시하지 않아 unresolved로 남겼다. H(1s) 초기상태 연결은 P01의 Minami 인용에 근거한 cross-source binding임을 기록했다. 방법 간 차이를 통계적 오차막대로 해석하지 않았다. 원문 n=1–20 total의 quantum 열에는 정규화한 CTMC high-n 보충이 있어 순수 quantum 합계와도 구별했다.

기계 판독 셀은 총 **1,131개**다. ScienceDB 4파일의 비어 있지 않은 dependent cells 743개, P03 Table II 9개, P04 A3 63개, P09 Tables 25–30 300개, P08 Table II 16개다. P09의 convergence ε token 300개는 각 셀의 진단 메타데이터이며 추가 단면적 셀로 세지 않았다. Benchmark metadata는 논문 7개·ScienceDB 4파일·제외 확인용 IAEA proton 2파일의 **13행**이다. 모든 값은 native axis/단위/observable을 보존하며, 서로 다른 source grid를 하나의 물리 비교 grid로 합친 것이 아니다.

Portable checker는 source 해시 15개, 수치 셀 1,131개와 matrix 13행에 대해 PASS를 기록했다. 원 raw CSV 743셀은 literal cell과 대조했고, PDF 셀은 보존된 전사 기록과 비교했다. 별도 reviewer는 직접 source 해시 8개를 확인하고 P04 24셀·P08 16셀, 총 40셀을 실제 페이지에서 육안 대조하여 `PASS_BOUNDED_RECORD_REVIEW`를 반환했다. 이는 전체 전사를 다시 독립 추출한 인증이나 B1 global authority closure가 아니다. 근거는 `B1/VERIFICATION.json`과 `review/B1_INDEPENDENT_RECORD_REVIEW.json`에 있다.

| 자료 | exact 5.0/0.5 keV/u 판정과 제한 |
|---|---|
| P04 Minami | Native 5 keV/u A3 있음. 0.5 row 없음. Lab/CM label과 H(1s) 교차 근거를 명시. |
| P08 Winter | Table II의 native axis는 alpha projectile **20 keV lab**. A=4일 때 20/4=5라는 조건부 adapter를 기록하되 native 5-keV/u token으로 바꾸지 않음. 0.5에 대응하는 native 2 keV row 없음. |
| P03 Liu HSCC | 9개 값은 cm-energy eV와 n=2 capture. 4000 eV를 mass adapter 없이 5 keV/u로 부르지 않음. |
| P09 Agueny / P07 Hose | Native velocity axis. 이번 루프에서 velocity→energy 변환하지 않음. P09 ε는 basis-convergence 진단이며 표준편차가 아님. |
| P10 Faulkner | 10–1000 keV/amu 범위로 관심 두 에너지 밖. Fig. curve를 digitize하지 않음. |
| P22 Shah/Gilbody | Native ³He total lab energy와 isotope mapping을 보존. Native 5 keV를 5 keV/u로 오인하지 않음. |
| ScienceDB / IAEA | ScienceDB raw grid에 exact 5와 0.5 token 없음. 일부 단위·frame authority도 미해결. IAEA 2파일은 H⁺ projectile이므로 He²⁺ authority에서 제외. |

이 bounded subset에서 바로 사용할 수 있는 native exact 0.5-keV/u benchmark cell은 확보하지 못했다. P04 A1–A12 전체 및 P09 114개 table 전체 전사는 하지 않았다. P08의 native shell sum이 없는 항목은 새로 더하지 않았고, 다른 table의 graphically interpolated 비교값을 exact authority로 채택하지 않았다. P04의 발견은 과거 R10N의 ScienceDB-specific 부재 판정을 바꾸지 않는다. 또한 새로운 원문 셀만으로 G1 비교를 허용하지 않는다.

## 6. 남은 공백과 gate

수치 coupling database는 상징적 연결 관계만 담고 실제 (L_{gb}(R)), radial amplitude, 단면적 예측값을 생성하지 않았다. Basis·continuum·channel·propagation·impact·interpolation·trajectory·projection·roundoff·source·digitization·model의 12개 uncertainty component도 물리 예측 부재 때문에 개별 `NOT_EVALUATED`로 남겼다. 임의 Gaussian error나 단일 합성 theory error bar는 없다.

A2의 small/large-R 계수·차수, C1 전자 solver 선택, C2 finite-R magnitude, D1/D2 coherent propagation·quadrature, E1/E2 return·continuum, F1 trajectory, F2 support/Stokes, G1 frozen benchmark discrimination은 `NOT_RUN_BLOCKED_A1_CLOSURE`다. 약 4620 discrepancy, n=2 reconciliation, REAL/EXTENDED 선택 및 production 정확도는 해결됐다고 주장하지 않는다. Source extraction을 이용한 solver fitting도 수행하지 않았다.

```text
CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN
production_default_change=NOT_AUTHORIZED
```

다음 A1b는 H(1s) incoming과 He⁺(1s,n=2) outgoing subspaces를 명시적 finite-R basis/ETF embedding으로 연결하는 한 질문에 집중한다. 최소 한 candidate의 \(\chi,S,h,D\), 시간미분 좌표 convention, 비특이성 조건과 boundary projectors를 정하고 독립 검토한다. 그 뒤에야 A1 physical closure 여부를 다시 결정한다. 자세한 실행 계약은 `NEXT_HANDOFF_KO.md`, 수식별 근거는 `A1/FRAME_ETF_DERIVATION_KO.md`, 독립 판정은 `review/A1_INDEPENDENT_REVIEW.json`에 있다.
