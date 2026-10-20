# C3 — borrowed cell view의 동등성 조건과 최소 검사

**판정: 구현 가능한 복사 제거 후보. 성능·최종 코드 승인은 아직 미판정.** 현재 addon의 `NativeCellCache::prepare`와 `native_rates`, adapter의 FD·오류 경로를 읽었다. 구현하지 않았으며, C9에서 최종 diff와 실제 원시 결과를 별도로 한 번 검토한다.

## 유도

광자 상태를 \(p=(N,U,\ell,h)\), 고정 ray scale을 \(r_i\), 셀별 원본 준비 함수를 \(P_i(p,r_i)\)라 하자. 기체 섭동에서는 모든 \(P_i\)가 base와 같고, 광자 좌표 하나의 섭동에서는 해당 셀 \(k\)만 재준비한다. 유효한 view가 제공해야 할 노드열은

\[
\mathcal N(p;k)=\bigoplus_{i=0}^{C-1}
\begin{cases}
P_i(p,r_i).\mathrm{nodes},&i=k,\\
P_i(p_0,r_i).\mathrm{nodes},&i\ne k ,
\end{cases}
\]

이다. \(\oplus\)는 **셀 오름차순, 셀 내부 원래 순서의 연결**이다. \(k\)가 없으면 전부 base이다. 기존 flatten은 이 값들을 복사할 뿐이므로, 같은 열의 불변 참조를 generic iterator로 전달하면 복사는 필요 없다. 현재 rate body가 template에서 읽는 값은 셀 수와 \(\ell_i\)뿐이다.

노드 \(\nu\)의 종 \(j\) 흡수 사건률은 \(A_{\nu j}=c\,a_j\sigma_{\nu j}n_\nu\)이다. total-H 기준에서

\[
\dot N_i=-\sum_{\nu\in i}\sum_{j=0}^{2}A_{\nu j},\qquad
\dot U_i=-\sum_{\nu\in i}q_\nu\sum_{j=0}^{2}A_{\nu j},\qquad
\dot O_i=-\sum_{\nu\in i}(q_\nu-\ell_i)\sum_{j=0}^{2}A_{\nu j}.
\]

동등성은 수식의 교환법칙보다 강한 **동일 연산열** 조건으로 구현한다. `j=0..3` 반복, 곱셈의 결합, photo/binding/heat의 `+=`, 세 `compensated_add` 호출 순서를 모두 그대로 둔다. 이를 통해 P와 binding/heat를 만드는 원시 사건이 유지된다. 시간 정확도·강성 정확도·다른 과학적 적용 범위는 이 유도로 승격되지 않는다.

## 구현 계약과 위험

| 조건 | 필요한 이유 |
|---|---|
| shape 검증 → changed 범위 → 모든 support 및 미변경 셀의 \(N,U\) stale 검증 → replacement 준비 순서 유지 | 기존 최초 실패와 fatal/domain 분류를 보존한다. NaN을 equality 검사에 맡기지 않는다. |
| view가 cache·현재 state를 불변 borrow하고 replacement 하나를 소유 | rate 평가가 끝날 때까지 참조 대상이 살아 있고 변하지 않아야 한다. base cache는 같은 Context geometry에서만 유효하다. |
| replacement를 원래 셀 위치에서 선택 | 끝에 append하거나 셀을 중복·누락하면 전역 photo/binding/heat 합산 순서가 바뀐다. |
| diagnostics도 셀별 원래 순서로 병합 | tail의 세 `+=` 및 max 항목을 그대로 보존한다. node_count는 현재 replacement를 포함해야 한다. |
| Legacy와 CellCache도 같은 arithmetic helper 사용 | body의 물리식이 두 벌로 갈라지지 않게 한다. 별도의 SIMD·병렬 reduction이나 수식 인수분해를 섞지 않는다. |

셀 수 \(C\), 현재 전체 노드 수 \(M\), node 크기 \(S\)일 때, 이 후보는 평가 한 번당 논리적 복사 payload \(4C\,\mathrm{sizeof}(f64)+MS\) 및 평탄 벡터를 제거한다. **\(O(C)\) 검증·diagnostics, \(O(M)\) rate 순회, 변경 셀의 준비·할당, 캐시 생성 때 base clone, 결과·보정 벡터 6개의 할당은 남는다.** 따라서 allocation-free나 정량 RSS 감소는 아직 주장할 수 없다.

## 필요한 유한 검증

1. **순회·수치 동등성:** 기존 seeded/empty/delta full-J 및 threshold/steep replacement 사례에 새 모드를 넣는다. finite scalar의 차이 0, full Jacobian·호출 수·node 수·diagnostics·모든 사건/에너지 채널을 확인한다. 부호 있는 0의 IEEE 비트를 비교하지 않았다면 “bitwise 동일”이라 쓰지 않는다.
2. **실패 계약:** 기존 stale·support 변경·changed 범위·shape 및 cap/transaction/domain/fatal 사례를 새 모드에도 적용한다. 지원 끝점으로 replacement 노드 수가 달라지는 사례가 기존 사례에 없다면 그 구체적 분기만 한 번 추가한다.
3. **실제 경량 측정:** 같은 source/build/input/affinity에서 CellCache와 CellBorrowed를 교차 배치하고, wall 타이머 밖에서 전체 결과를 비교한다. 변한 준비/노드 계수와 inclusive/exclusive profile을 구별한다. 메모리를 말하려면 동일한 작은 fork/exec/wait4 부모를 사용한다.

기존 152개 native 원본 및 hook 불변, 새 opt-in/default 불변, FD step·budget charge·허용오차·실패 후 상태 보존은 최종 diff에서 확인할 계약이다. **C3 메모 완료 / C9 대기 / 새 native 실행·검사·Git 게시·업로드 없음.** 이번 메모의 게시·백업은 root의 단계 전달에 포함한다.

근거: `optimization_20261020/coder/patch_files/native_additions/axbi_native_rhs.rs`의 현재 구현, 같은 `patch_files/src/lib.rs`의 evaluate/Jacobian/regression 경로, 복원 원본 `axbi_covariant_transport.rs`의 PhotonState·PreparedCell·prepare_cell·validate_state. 적용 정책은 `physmath-research-loop` internal operating policy 1.0.0이며, 기존 증거를 새 실행으로 재집계하지 않는다.

