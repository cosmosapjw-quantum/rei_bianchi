# C1–C8 implementation observed results

이 문서는 실행자가 실제 JSON/로그 값을 전사한 기계적 결과 요약이다. 과학 수용 판정은 C9/root에 남긴다. Root THEORY/CONTRACT/source를 변경하지 않았다.

## 실행과 비용

3 planned invocations 모두 FINISH. 누적 local CPU=1.9570049999999997 s, wall=2.104758352987119 s. CPU는 child+timed parent delta다. 새로운 allocation은 20 CPU/60 wall이며 1 repair invocation은 미사용이다.

| Run | Child CPU s | Parent CPU s | Accounted CPU s | Wall s | Status |
|---|---:|---:|---:|---:|---|
| 01_tests | 0.119602000 | 0.001375000 | 0.120977000 | 0.166686151 | FINISH |
| 02_actual_analysis | 0.114766000 | 0.001111000 | 0.115877000 | 0.166606423 | FINISH |
| 03_plot | 1.716787000 | 0.003364000 | 1.720151000 | 1.771465779 | FINISH |

기존 Hex CPU18.434312000000002/wall18.739398924000852와 HEANG_CONTRACT CPU0.5922019999999999/wall0.5168205270092585, nontransferable 잔여 및 HE_X1/HE38/D10/remote UNKNOWN_NOT_ZERO는 ledger의 별도 inherited metadata로 유지했다. 새 budget 잔여와 합치거나 complete grand total을 만들지 않았다.

## 검증 관측

8 unittest PASS, 실패0/오류0. Constant/affine closed forms, independent cellwise GL16/32, n=1..6 exhaustive vertices (signed/ties/equal/collapsed bounds), witness equality/stationarity, common-scale invariance, theta radian/sin Jacobian, positivity/PSD와 입력 거부를 포함한다. Actual analysis의 11 checks는 모두 true다.

## 실제 window 출력

| Raw moment | Value (m² eV^q) |
|---|---:|
| R_0_0 | 1.918935932462322e-21 |
| R_0_0.5 | 4.088447783668332e-21 |
| R_0_1 | 8.79078610465918e-21 |
| R_1_0 | 1.000907432154299e-21 |
| R_1_0.5 | 2.132562352933905e-21 |
| R_1_1 | 4.585750869536331e-21 |
| R_2_0 | 8.698980369488815e-22 |
| R_2_0.5 | 1.856411371050203e-21 |
| R_2_1 | 3.998089087615456e-21 |

| Conditional scalar | Nominal | Deterministic minimum | Deterministic maximum | Linear-theta alternative |
|---|---:|---:|---:|---:|
| mean_mu | 0.5215950231699314 | 0.4463277016561826 | 0.5963051462262531 | 0.5201497577569106 |
| mean_P2 | 0.1799846901344856 | 0.0922143276271729 | 0.2671526749765701 | 0.17932811806022 |
| mean_E_eV | 4.581073268756349 | 4.431612712651814 | 4.725062230463735 | 4.58138945035865 |
| mean_sqrtE_mu | 1.111325457435915 | 0.9496644189267021 | 1.271018556498302 | 1.108233342343482 |

모든 box 끝점은 각각의 scalar에 대한 witness32개와 equality/stationarity residual을 `results/moments.json`에 제공한다. 서로 다른 scalar의 extrema를 한 simultaneous physical vector로 묶지 않는다. Nonlinear covariance의 exact box range는 계산하거나 주장하지 않았다.

조건부 covariance diagonal / (2 m_e epsilon): `[1.2487902633867187, 1.2487902633867187, 0.8484484696377634]`. 최소 성분은 nonnegative다. Trace/STF와 energy-weighted raw tensor를 같은 JSON에 보존했다. Per-energy J_r와 primary32 source-cell/bounds도 보존했다.

## Figure 관측

`figures/ddcs20_window.png` 및 `.svg`를 실제 결과에서 한 번 생성했다. 패널(a)는 degree theta 축의 source DDCS와 quoted source errors, (b)는 angular-window integral, (c–f)는 scalar deterministic box, nominal linear-mu와 linear-theta marker다. Source 1σ와 선택한 deterministic box/not CI를 footer에서 분리했다. 실행자가 PNG를 직접 보았으며 잘림/overlap을 발견하지 않았다. Root의 최종 180 mm 시각 검토와 C9는 pending이다.

## 범위

E0=20 eV, E=3–6 eV, theta15–120degree의 detected-electron window/축대칭 보간 조건부 결과만 생성했다. E2는 원문 데이터에 보존하되 계산에서 제외했다. Full-domain sigma, event law, pair/recoil, finite-mass provider 또는 X1 empirical correction을 추가하지 않았다. HE-ANG parent는 SOURCE_INPUT_PENDING이다.

## Identity

requested execution identity: gpt-6.1-sol/high. Observed runtime model: not independently observable.
