# 다음 물리 연구 루프 — PHYS23_SPECTRAL_INITIAL_RESPONSE_AND_THERMAL_SIGN

PHYS22에서 지정한 단일 후속 문제다. 이 문서는 PHYS23 실행 기록이 아니다.

## 1. 다음에 바로 풀 질문

실제 paired 초기 기체를 유지하고, HI만 직접 광이온화하는 threshold-separated 에너지 영역에서 **초기 HII와 온도의 shear response 부호가 방출 에너지와 spectrum에 따라 어떻게 달라지는가**를 구하라.

PHYS22의 13.7 eV에서 HII와 온도는 음수로 시작한다. 이 부호가 다른 에너지에서도 유지되는지, 두 부호가 갈리는 구간이 있는지, 양의 photon measure로 spectrum을 섞을 때 어떤 가중 조건으로 부호가 정해지는지를 연구한다. 현재 13.7 eV source를 바꾸는 production 수정이 아니라, 명시적으로 정의한 mathematical diagnostic family다.

우선 HI opacity cutoff 13.60 eV와 HeI cutoff 24.59 eV 사이의 열린 영역을 사용한다. 안전하게 떨어진 compact interval은 예를 들어 [13.61,24.58] eV로 잡을 수 있다. 실제 cutoff 값은 pinned atomic_provider.rs에서 재사용한다. 필요 이상의 에너지 sweep을 먼저 만들지 말고 analytic derivative와 root/sign structure를 먼저 본다. 이 구간 안에 부호 분기가 없다는 결과도 유효한 종결이다.

## 2. 현재 input identity와 최소 읽기

저장소 cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, [기존 draft PR83](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/83).

- PHYS22 input commit: 3dc42c64ab32075f0a59c96af3ddf7435d9b7f97.
- Input root tree: 668aee2a4e573826ee0b937897157a97825c70a8.
- Scientific Rust src tree: cb69b4736dd046e4675557577eb8e0ead037d1f3.
- 최종 PHYS22 report SHA256: a3d4ed48e753538eee763a3fe26931dfea6332132de15fc3a7b43b2b600797f6.
- 고정 PHYS22 계약 SHA256: 1706650c98b6b30f12e57b2af670113fe8ec30770ae2f48909823c30936de4a6.
- Canonical Astra harness SHA256: dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7.

PHYS22 publication commit은 위 입력 뒤의 additive docs commit이다. 그 실제 commit/remote ACK/archive identity는 detached publication receipt에서 읽는다. 다음 시작 시 현재 branch와 source identity만 필요한 범위에서 확인한다. Source subtree가 같으면 닫힌 PHYS20/21/22 과학 검산을 다시 실행하지 않는다.

최소 읽기는 이 handoff → PHYS22_REPORT_KO.md §§3, 6–9, 12 → RESULTS_SUMMARY.json → independent/DECISION_REVIEW.json이다. 실제 HI fit과 단위는 source manifest 및 atomic_provider.rs, hhe_events.rs에서 필요 부분만 읽는다. Code를 재사용할 때는 code/initial_time_coefficients.py의 spectral helper와 고정 입력을 읽되 main을 실행해 옛 결과를 재생하는 것을 출발 절차로 삼지 않는다.

## 3. 유지하는 물리 convention

\[
F_\epsilon=F_0+\epsilon^2F_2+o(\epsilon^2),\quad
F_2=\tfrac12\partial_\epsilon^2F|_0,\quad
\Sigma=\varsigma\,\mathrm{diag}(1,-1,0),\quad
q=\operatorname{tr}\Sigma^2=2\varsigma^2.
\]

\(B(t)=t\Sigma\), metric \((-+++)\), proper time [s], energy [eV], gas thermal coordinate \(w\) [eV/H]. Mean \(H,n_H\), scalar IC와 각 진단 family의 physical birth measure는 \(\epsilon\)에 독립적이다. 시간 계수에 추가 factorial을 붙이지 않는다. Formal \(\epsilon^2\), physical \(q\) 또는 \(\varsigma^2\), 시간 거듭제곱을 구분한다.

실제 IC는 \(H=10^{-14}\,\mathrm{s}^{-1}\), \(\varsigma=((1.01e{-14})-(0.99e{-14}))/2\)의 binary64 차이, \(n_H=10^{-4}\,\mathrm{cm}^{-3}\), \(f=0.083\), \((x,h_1,h_2,T)=(0.9,0.3,0.6,50000\,\mathrm K)\), \(N_0=0.05\) photon/H, \(S=5\times10^{-15}\) photon \(\mathrm{H}^{-1}\mathrm{s}^{-1}\)다. 현재 production birth energy는 13.7 eV다.

\(\chi_{\rm HI}=13.598434599702\) eV는 opacity cutoff 13.60 eV와 다르다. PHYS22의 source-inspected continuum는 native binary arithmetic와 동등성 인증을 받은 모델이 아니다. Decimal 계산의 50000 K 정규화와 source binary64 초기 w의 역변환 49999.99999999999 K 차이를 알고 비교하라.

## 4. 재사용할 닫힌 식

\[
D=E\partial_E,\quad\mathscr C=D(D+3),\quad
\lambda(E)=c n_H(1-x_*)\sigma_{\rm HI}(E),
\]

\[
\Pi_*=1+f+x_*+f(h_{1,*}+2h_{2,*}),\quad
\mathcal A_T=\frac{2e_{\rm V}}{3k_B},\quad
e_{\rm th,*}=\frac{w_*}{\Pi_*}=\frac{3k_BT_*}{2e_{\rm V}}.
\]

초기 monoenergetic cohort의 선도 응답은

\[
a_{3,x}(E)=\frac{qN_0}{45}\mathscr C\lambda(E),\quad
a_{3,w}(E)=\frac{qN_0}{45}
\mathscr C[\lambda(E)(E-\chi)],
\]

\[
\theta_3(E)=\frac{qN_0}{45}\frac{\mathcal A_T}{\Pi_*}
\mathscr C\{\lambda(E)[E-\chi-e_{\rm th,*}]\}.
\]

여기서 \(D\)는 \(T,y\)를 고정한다. 입자수 항을 버리면 thermal sign problem 자체를 바꾼다. Product rule은

\[
\mathscr C[\lambda(E)(E-\chi)]
=(E-\chi)\mathscr C\lambda+2E D\lambda+4E\lambda.
\]

이 식들은 PHYS22가 닫은 초기시간 결과다. 에너지 구간 전체의 부호·root 수·spectral mixture에 대한 해석은 PHYS23이 새로 판정할 대상이다.

연속 birth forcing은 같은 baseline의 특정해로 한 차수 늦는다. 같은 spectrum일 때 H/T의 birth leading coefficient는 \(S/(4N_0)\) times initial \(t^3\) coefficient이며 He birth는 \(S/(5N_0)\) times initial He \(t^4\) coefficient다. 이것을 전체 해의 \(S\)-parameter derivative로 확장하지 않는다.

## 5. PHYS23의 최소 완료 기준

1. Energy diagnostic family와 spectrum normalization을 고정한다. 처음에는 positive photon number measure와 고정 총 \(N_0\)를 쓰고, energy-normalized family를 추가한다면 별도로 정의한다.
2. \(\mathscr C\lambda\)와 thermal functional의 explicit energy dependence를 도출한다. Power-law 근사로 source Verner fit을 무단 대체하지 않는다. Fit의 로그 기울기·곡률 표현은 유용한 대안이다.
3. 선언한 compact interval에서 부호와 가능한 영점을 판정한다. 수치 root를 쓰면 bracket/residual과 구간 가정을 남기고, 단순 dense scan을 영점 부재의 증명으로 부르지 않는다. Rigorous enclosure가 없으면 근거 수준을 수치적 분류로 제한한다.
4. 두 monoenergetic 기능의 부호를 positive spectral measure 적분과 연결해 broadband 선도 응답의 조건을 쓴다. 적분과 \(D\)의 작용 대상 및 cutoff boundary 항을 명확히 구분한다.
5. 현재 13.7 eV 값은 PHYS22 결과를 anchor로 사용한다. 새 구현의 필수 연결 확인이 있다면 한 번의 작은 비교로 충분하며 PHYS22 suite를 전부 재실행하지 않는다.
6. 새 spectral 주장에 대한 독립적인 작은 검산과 별도 final decision review를 수행한다. 보고서, 결과, 그림이 유용하면 정확한 coefficient plot, 다음 질문 하나를 남기고 종료한다.

He의 leading sign은 PHYS22의 electron/temperature map으로 연결할 수 있지만, H/T spectral question을 닫는 데 필요하지 않으면 별도 대규모 확대를 하지 않는다. Threshold crossing, redshift로 cutoff에 도달한 뒤의 분포 미분, 다른 atomic lanes, full gas trajectory는 이 후속 문제에 자동으로 포함되지 않는다.

## 6. 보호 범위와 종료

Physical=HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. Native history, new gas IVP, old PHYS19/20/21/22 proof replay, firstmacro 8/16/32, full raw/NCP, source/default/runtime returns 변경을 실행하지 않는다. 유한시간 sign이나 remainder certificate는 별도 문제다.

PHYS22 최초 과학 실행은 radiation 52/52, gas 11/11, root 21/21, coefficient comparison 16/16으로 모두 exit 0이었다. Contribution과 통합 보고서의 수식·단위 표기를 좁게 수정했으며 v1을 보존했다. Science code/result와 tolerance는 그대로다. 별도 portability replay는 같은 결과의 재현성 기록이며 새로운 독립 물리 검산으로 합산하지 않는다.

Archive byte 손상이 의심되면 reproduce.py --verify-only를 우선 사용한다. 전체 diagnostic replay는 새로운 portability 필요가 있을 때만 실행한다. Remote ACK/tree/blob 일치와 fresh local ZIP restore는 다른 근거다.

세션에서 허용된 동일 branch의 additive docs publication은 nonforce compare-and-swap로 이어갈 수 있다. 새 PHYS23 docs 경로를 쓰고 기존 파일과 source를 바꾸지 않는다. Merge 및 타인에게 메시지 전송은 포함하지 않는다. 연구 질문과 검산이 완료되면 필요한 artifact와 최소 metadata만 기록하고 루프를 끝낸다.
