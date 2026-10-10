# REI-PHYS20 독립 decision review

## 판정

**PROMOTE — PHYS21의 후속 이론 연구에 사용하는 범위에 한정한다.** 고정 후보의 수학·측도·부호·단위·유효범위에서 이 범위의 승격을 막는 치명적 오류는 발견하지 못했다. **Physical admission은 HOLD**이며, 기존 `[160,161] FAIL`, `tick160`, `auxiliary escape FAIL`은 그대로 보존한다. 새 gas 해, native accuracy certificate 또는 physical dataset admission을 승인한 판정이 아니다.

검토한 최종 후보는 `PHYS20_REPORT_KO.md`, SHA-256 `42d05d3a96a962728d7deac7d380e71914cdbf31b360a1fec13161a913ea974e`다. 기계 판정과 실제 읽은 파일 identity는 `DECISION_REVIEW.json`에 있다. Reviewer는 `/root/decision_review`이며, 후보 생성과 사전 검증 설계에 참여하지 않은 별도 subagent다. 호스트가 알려준 모델은 GPT-6 Astra다. 이번 독립 검토 과정에서 수행한 작은 추가 계산은 아래에 별도로 구분했다.

## 핵심 판단 근거

**각도 측도의 소유권은 맞다.** 보존 covariant momentum의 방향을 q, 현재 물리 방향을 n이라 하면 `dΩ_n=J_t dΩ_q`, `J_t=(a_1a_2a_3 g_t³)⁻¹`이다. 따라서 isotropic physical birth source는 q 좌표에서 `J_b`를 가진다. 이미 q별 광자 count로 저장한 양의 scalar 합에는 `J_t`를 다시 곱하지 않는다. 현재 물리적 입체각당 response를 표시할 때는 `J_t`로 나눈다. Pinned `paired_runtime.rs`의 count 정의, source weights, scalar grouping이 이 해석과 일치한다. 이 검토는 소스 의미를 확인한 것이며 Rust binary 실행을 주장하지 않는다.

**흡수와 가열의 부호는 올바르게 구별했다.** 더 빨리 팽창하는 축은 광자의 에너지를 낮춘다. 감소하는 HI 단면적에서는 순간 hazard가 증가할 수 있지만, 누적 생존확률은 반대로 감소한다. 보고서의 `δ ln P=+Σq_i²M_i`는 이 반대 효과를 포함한다. 현재 물리적 입체각당 사건률에는 추가로 `−3ΔB`가 들어간다. Primary 가열에는 `E−χ`가 곱해지므로 threshold 근처에서 흡수 증가와 가열 감소가 동시에 가능하다. `coupled_primary.rs`의 `photo_rates`와 `photo_heat`가 해당 primary ledger 해석을 지지하며, HI fit cutoff 13.60 eV와 thermal binding energy 13.598434599702 eV를 구별한 것도 맞다.

**Scalar cancellation은 명시한 조건 아래의 정리다.** 연속 구면의 second moment `⟨q_iq_j⟩=δ_ij/3`는 trace-free shear forcing을 소거한다. Gas 선형화의 초기변화가 0이고 scalar source에 독립적인 O(ε) forcing이 없으며 해당 선형 Volterra 문제의 해가 유일하면 scalar gas first variation도 0이다. 검토 중 초기 photon count/spectrum와 source scalar amplitude의 ε 독립성을 명시하도록 지적했고, 최종 후보 §5.2에 반영된 것을 확인했다. C¹에서 o(ε), 유계 C²에서 O(ε²)를 구분한 설명도 정확하다. 관측자 redshift 또는 lightcone endpoint를 바꾼 optical depth로 자동 확장하지 않는다.

**Native midpoint rule의 정확한 한계를 보존했다.** 수학적 grid의 second moment는 `Q=diag(1/3+1/(6N²),1/3+1/(6N²),1/3−1/(3N²))`다. 따라서 `Q:B=−Bzz/(2N²)`이며 현재 xy shear가 통과하는 것은 모든 방향의 STF response를 보증하지 않는다. 같은 eigenvalues를 보존한 `diag(1,0,−1)` 회전 반례도 올바르다. 선두 free-energy 계수의 continuum 값 8/15와 finite-grid 값 `8/15+1/(3N²)−7/(60N⁴)`는 독립 모멘트 결과와 일치한다. N=8의 0.971221923828125%는 이 **2차 계수의 bias**이며 실제 온도나 optical depth의 상대오차가 아니다.

**Birth-time artifact와 threshold 반례도 유효하다.** Physical-angle isotropic source의 continuum 변수변환은 constant directional rates의 free-photon energy를 photon age에만 의존하게 만든다. Uniform-q source로 바꾸면 `4σ²bΔ/5` 항이 생기고, normalized finite-grid J source에도 보고서가 명시한 O(N⁻²) 잔여항이 남는다. 별도 threshold line에서 `(E−E_th)_+`의 평균이 `2E_th|u|/(3π)+O(u²)`가 되는 반례는 직접 각도평균으로 확인된다. 그러므로 evenness만으로 quadratic onset을 주장할 수 없다. 해당 반례는 실제 13.7 eV FT03 line을 변경한 모델이 아니다.

## 실제 추가 계산과 읽기 범위

최종 angular report, exact-fraction/Decimal80 결과, execution metadata를 모두 읽었다. Owner의 kernel v2, 81개 check, threshold JSON과 이를 생성하는 코드를 읽었으며, pinned source 5개 파일의 관련 부분을 검사했다. 검토한 local source bytes는 manifest의 size, SHA-256, git blob ID와 모두 일치했다. 전체 저장소 build 또는 별도 remote refetch를 수행한 것은 아니다.

Reviewer의 작은 독립 계산은 `decision_spotcheck_decimal.py`와 `decision_spotcheck_results.json`에 있다. Candidate 코드를 import하지 않고 HI fit과 exact characteristic을 별도 작성하여 Decimal70과 composite Simpson256/512를 사용했다. x/y축의 b=0 cohort 및 `(3/5,4/5,0)` 방향의 b=t/2 cohort에서 6개 fractional response, 적분 refinement, binary64 input trace와 부호를 대조했다.

- 실제 실행: exit 0, **23/23 검사 통과**.
- Candidate v2와 fractional change의 최대 절대차: `1.69948214×10⁻²⁶`.
- Baseline optical depth의 상대차: `4.33680869×10⁻¹⁷`. 이는 candidate의 GL24와 Simpson 비교에 이미 나타나는 수치차 수준과 일치한다.
- 위 차이는 관측한 수치차다. Rigorous interval enclosure 또는 전체 오차 경계로 해석하지 않는다.
- 새 native 실행, gas IVP, 과거 proof 재실행, production code 변경: 모두 0회.

첫 optional mpmath 시도는 해당 패키지가 없어 import에서 중단됐다. `decision_spotcheck_runtime_failure.json`과 원 script를 보존하고, 설치 없이 표준 Decimal 구현으로 전환해 위 결과를 얻었다. 이는 환경 오류이며 물리적 반례나 candidate 검사 실패가 아니다.

## 유지되는 한계와 재개 조건

이 reviewer는 논문 PDF들을 다시 읽지 않았다. 문헌의 직접 확인 범위는 owner의 source ledger에 의존하며, 이번 판정의 핵심 근거는 직접 검토한 유도와 pinned source 의미다. 외부 문헌의 novelty 또는 우선권은 판정하지 않았다.

실제 gas ionization·temperature의 quadratic response, late threshold crossing, native spectral remapping 전체의 regularity, observer endpoint 변화는 unresolved다. Native generic-shear 실행에 continuum cancellation을 적용하려면 actual second moment와 leakage를 다시 검증해야 한다. 실제 coupled coefficient를 승격하려면 intended evolving gas/source history와 causal feedback 및 2차 regularity를 새 evidence로 결속해야 한다. 이런 확장을 할 때 각각 `REOPEN_VALIDATION` 또는 `REOPEN_EVIDENCE`가 필요하다.

현 고정 범위의 material risk는 해소됐다. 추가 리뷰 재귀나 이전 FLRW proof 반복 없이 PHYS21의 second-order scalar forcing과 gas feedback 유도로 진행할 수 있다.
