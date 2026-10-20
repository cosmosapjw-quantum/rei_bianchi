# R1–R10 / C1–C4 — 동일 노드열을 빌려 쓰는 native RHS
## 이번 질문과 이전 증거
현재 독립 LRS adapter의 과학 입력은 source 33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1, 전달 HEAD 70a9ff3f2437101a1df13054dcb10f8106741b26이다. 고정된 VigilODE 8a8bd409b1d96c7b7421f496d229e119fd3d284e와 original native 152개 파일 및 기존 append hook을 유지한다. 앞선 cache 최적화의 19설정 결과와 비용 측정은 유효한 baseline으로 재사용한다. 이번 질문은 남은 per-cached-RHS 상태·노드 복사를 없애도 같은 native 사건과 시간적분 결과가 유지되는가이다.

물리 관례는 total-H 정규화, e=x+Y(y+2z), Y=.2454/[4(1-.2454)]이다. 원시 P/C/R/D, binding/heat/cooling/escape/CMB/work의 분리를 유지한다. 광자 reference energy와 gas thermal energy를 혼동하지 않는다. 기존 에너지 항등식 및 GL2 선형 정확도 결과는 재검산·재집계하지 않는다. 이번 유도는 저장 표현의 변경에 관한 것으로 시간 차수 정리가 아니다.

## R3–R6: storage 변경의 동등성 유도
셀 i의 원본 준비 함수가 반환하는 순서 있는 노드열을 Q_i(p,r_i)라 하자. geometry r_i는 해당 Context 안에서 고정된다. cache가 보유한 base p0에서 상태 p로 바뀔 때 changed=k이면 k 하나만 원본 prepare_cell로 재구성한다. shape, support, 미변경 셀의 N/U 동일성 검사 이후 사용 가능한 노드열은

\[
\mathcal N(p;k)=Q_0\oplus Q_1\oplus\cdots\oplus Q_{C-1},\qquad
Q_i=\begin{cases}Q_i(p,r_i),&i=k,\\Q_i(p_0,r_i),&i\ne k.\end{cases}
\]

기체 좌표만 바뀌면 changed가 없고 모든 Q_i를 재사용한다. \(\oplus\)는 셀 오름차순 연결이며 빈 셀은 길이 0이다. 원래 flatten은 이 열의 값을 복사한다. borrowed iterator는 동일 값의 불변 참조를 같은 순서로 반환한다. 길이가 m_i인 셀의 node j는 평탄 위치 \(j+\sum_{h<i}m_h\)에 대응한다. 변경 셀의 길이가 달라져도 이 식에 현재 m_k를 사용하므로 일대일 대응과 순서가 유지된다. replacement를 끝에 붙이면 이 대응이 깨진다.

모든 rate 결과와 보정 합산 변수를 묶은 계산 상태를 S_l, 한 node의 기존 연산을 \(\Phi\)라 하면

\[
S_{l+1}=\Phi(S_l,\nu_l),\quad S_0=\text{기존 초기값}.
\]

두 경로가 같은 \(\nu_l\), 같은 \(\Phi\), 같은 S_0를 가지므로 귀납적으로 전체 상태열이 같다. 이 논증은 합산의 교환·결합 법칙에 기대지 않는다. 종 순서 j=0,1,2, 곱셈 결합, gas 채널의 +=, 세 compensated_add의 호출과 cell index를 그대로 공유한다. diagnostics도 같은 cell 순서로 접는다. 따라서 shader/SIMD/병렬 reduction처럼 산술 순서를 바꾸는 작업을 이 수정과 섞지 않는다.

실제 Rust 컴파일에서 이 조건이 지켜졌는지는 원본 body를 하나의 generic helper로 공유하는 diff와 native 수치 대조로 확인한다. 언어 수준 추론만으로 모든 컴파일러/플랫폼의 signed-zero 비트 동일성을 선언하지 않는다. 캐시 유효 범위, shape와 stale 검사, 최초 fatal/domain 실패, RHS charge 및 실패 후 transaction도 기존대로여야 한다.

## R7–R8: 제거되는 비용과 남는 비용
셀 수 C, 전체 노드 수 M, node 크기 S_node일 때 제거되는 것은 각 successful cached prepare의 논리적 복사 payload \(4C\,\mathrm{sizeof}(f64)+M S_\text{node}\)와 flat Vec 구축이다. 좌표 decode, Jacobian 시작의 base clone, 변경 셀의 준비, 결과·보정 벡터 여섯 개, O(C) 검증·diagnostics, O(M) rate 순회는 남는다. allocator 호출 수·메모리 대역폭·최대 RSS는 이 논리량과 같은 측정값이 아니다.

완전한 중앙차분이 모두 허용되는 Jacobian에서 광자 좌표 P, 기체 좌표 G, 차원 d=P+G라 하면 기존 cached prepare의 상태 복사는 \(1+2d\)번이다. node 수가 섭동으로 달라질 수 있음을 반영한 전체 node 복사는

\[
K=(1+2G)M+\sum_{a=1}^{P}
\left[2M-2m_{c(a)}+m_{c(a),+}+m_{c(a),-}\right].
\]

새 경로의 해당 두 clone 계수는 0이며, rate가 방문하는 node 수는 여전히 K이다. 모든 섭동에서 node 수가 같다면 K=(1+2d)M이다. C=40, P=80, G=4, M=640 예의 식은 상태 169회, node 108160개 복사를 뜻한다. 이는 조건부 비용식 대입이며, 새 native 관측값은 C6–C8 receipt에서 별도로 판정한다. domain 때문에 단측 차분을 쓰거나 실패하면 실제 계수를 따른다.

기존 cache profile의 preparation 시간은 clone·validation·replacement 등의 묶음이므로 모두 제거 가능한 시간으로 계산하지 않는다. 같은 binary, CPU affinity, profile-off AB/BA pairing으로 순수한 개선의 실제 크기를 관측한다. 5개 pair의 분산과 모드별 차이를 함께 보고한다. 개선이 없으면 그 결과도 보존하며, clone 제거와 wall speedup을 별개로 판정한다.

## 실제 Wolfram 확인과 범위
theory/borrowed_order_and_cost_corrected.wl을 Wolfram 커널에서 실행했다. 빈 셀과 길이가 바뀐 replacement를 포함하는 noncommutative symbolic fold의 두 상태식은 SameQ=True, replacement를 끝으로 옮긴 반례는 False였다. 위 copy-count 식의 동일 길이 환원과 169/108160 대입도 반환됐다. 일반적 근거는 위의 임의 길이 노드열 귀납법이며, 이 작은 기호 사례를 native 우주론 이력이나 새 시간 정확도 실험으로 세지 않는다.

첫 호출에서 사용하지 않는 protected built-in C를 ClearAll에 넣은 경고가 있어 그 한 항목을 제거했다. 원래 소스·출력도 보존했다. 두 출력의 undefined symbol 안내는 의도한 기호 M/G/P에 대한 것으로 식과 값을 반환했다. 이것은 Rust 실패나 과학적 FAIL이 아니다. 실제 native 수치 판정은 아직 대기이다.

## R9–R10 / C4: 채택 기준과 실행 전이
계약은 CONTRACT.json에 고정했다. opt-in cell-borrowed를 추가하고 legacy/default 및 cell-cache 비교 경로를 보존한다. 기존 seeded/empty/delta full-J, threshold/steep changed-cell, stale/shape/index, cap/transaction/domain/fatal 사례를 새 모드에 적용한다. changed cell의 node 수 변화가 기존 사례에 없을 때만 해당 분기를 한 번 추가한다. 기존 19설정을 한 번 재현하고 모든 공유 물리 필드를 비교한다. 이는 기존 fixture의 새 구현 회귀 재현이다.

C5–C8은 lower-tier coder에게 위 계약으로 위임했다. native 총180초, case40초, build1200초, jobs1이다. C9는 이 수정을 구현하지 않은 Astra reviewer가 diff와 실제 stdout/exit/raw를 읽는다. 구체적 결함이 있으면 한정된 수정 후 해당 회귀만 다시 실행한다. 동등성과 비용에 관한 유한 판정이 끝나면 게시·백업·실행 인계로 전이한다.

외부 source intake는 intake/upstream/의 실제 receipt를 사용한다. VigilODE 신규 AD/grid 작업, RUN19 T-only RHS cache, rec/BASS/HH 작업을 자동으로 이 LRS 증거에 편입하지 않는다. 현재 병목에 직접 적용되는 Rust의 불변 borrow와 iterator를 사용하고, 이미 통합된 VigilODE solver/faer 및 Rayon batch를 유지한다. 새 수치 패키지 추가나 pin 변경은 이번 단위에 없다.

source-on 전체2차, uniform stiff, 일반적 양수성, CaseB, fullEoR, signed Bianchi, positive-CMB/nonzero-boundary의 넓은 범위, production 적용은 이 변경으로 승격하지 않는다. 과거76 제조문제·Python57 및 기존19 설정의 누적 개수를 늘리지 않는다.

