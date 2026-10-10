# REI-ACCEL01 — 전구간 reionization 계산과 연구 가속 계획

2026-10-10 · 조사 → 모형 고정 → 실제 전구간 적분 → 수렴/독립 비교 → 통합

## 이번에 실제로 얻은 결과

**평균 부피 redshift 20에서 4까지의 reionization history를 실제 계산했다.** 선택한 FLRW 기준 모형에서 약 13.64억 년에 해당하는 구간이다. 최종 14개 경우를 각각16,384개 log-a 구간으로 계산했고, FLRW와 최대 shear 경우에는 전체 구간 격자 정밀화와 별도 적응형 적분기 비교를 수행했다. 첫 scientific plot은 `evidence/RUN002/BROAD_HISTORY.png`와 PDF로 제공한다.

이것은 R15 방출률과 HG97 case-B 재결합을 쓰는 **축약된 체적평균 모형의 과학 계산**이다. 실제 CR·RCT·열진화·방향별 복사전달까지 결합된 기존 native solver의 완료는 아니다. 원자물리 전체가 끝났다고 선언하지 않는다. 해당 원 연구의 열린 문제를 정확히 남기면서, 이미 공개된 원자율로 수행 가능한 과학 계산의 대기를 해소했다. 독립 판정은 `independent/DECISION.json` 및 검토문이 권위 있는 기록이다.

| 경우 | z50 | z90 | tau(20→4+) | FLRW 대비 delta tau |
|---|---:|---:|---:|---:|
| FLRW | 7.32839548 | 6.28138267 | 0.03744182127 | 0 |
| 초기 s/H=.01 | 7.32838875 | 6.28137829 | 0.03744156218 | −2.59090e−7 |
| 초기 s/H=.05 | 7.32822704 | 6.28127286 | 0.03743533178 | −6.48949e−6 |
| 초기 s/H=.1 | 7.32771707 | 6.28094031 | 0.03741570902 | −2.61122e−5 |

이는 현 관측자료를 새로 적합한 결과도, 관측으로 허용된 shear 모형의 검증도 아니다. tau는20→4+ 구간 기여다. z<4의 HeIII·저적색편이 전자 및 z>20의 잔류전자를 포함한 전체 CMB optical depth와 비교하지 않는다. z99=6.12318543이며, 독립 event 적분기의 Q=1 도달은 z=6.10668413이다. Q=1 이후의 중성분율이나 Lyman-alpha forest 통계를 이 모형에서 추론하지 않는다.

## 최신 repo와 스레드 반환물의 통합

GitHub 실제 source, branch/PR metadata와 게시된 연구 보고서를 다시 읽었다. 비공개 ChatGPT 대화 자체를 직접 열람하거나 각 대화에 실행을 수신시켰다는 주장은 하지 않는다. 세부 근거는 `intake/`의 repo별 반환물과 JSON에 있다.

| Repo / 최신 과학 입력 | 확인한 업데이트 | 이번 DAG에서의 의미 |
|---|---|---|
| REI PR103 `8d9526a…`; PHYS22 owner `e334866…` | CR xi=.01/.1 고정 knot 및 초기시간 shear 계수 | 고정점·국소 결과를 장기 history로 승격하지 않음. 기존 background 코드를 실제 재사용 |
| bass_cr PR25 `b157c787…`, PR27 `b5b0f224…` | 서로 다른 causal electron 모델, source convolution·tail·NIST 진단 | 이름이 같은 PHYS02B/02C를 한 계보로 합치던 위험 해소. 모델별 ID를 별도 등록 |
| BASS_HE PR17 `f9a34c88…` | E13C3 고정 gas path의 저비용 광자 보정 | 향후 scalable transport 후보. 실제 RCT spectrum/heat/recoil은 여전히 없음 |
| WU088_HH owner `569b04cd…`, PHYS03 `93e04c51…` | birth threshold remap의 분할 의존성 | 수·에너지 보존만으로 chronology 정확도가 따라오지 않음. full native source 단계에서 실제 해결 필요 |
| bass PR136 `220d765f…`, sibling132 `e5706493…` | snapshot 및 별도 clock/visibility 모듈 | 새로운20→4 전자 cell 자료를 생성. 기존 snapshot receipt를 새 history의 native 수신 증거로 재사용하지 않음 |
| rec_bianchi PR82 `b1213b09…` | HyRec의 z5.807 잔류전자 endpoint | 전구간 고유 IC나 Bianchi I provider가 아님. residual IC lane에서 재사용하되 값의 시간 범위를 보존 |

CR의 PR25 `PHYS02B_DELAY`는 DarkHistory 계열10–1000eV 고정 bath이고, PR27 `PHYS02B`는 BEQ/BED+CCC 계열0.1–900eV다. PR25 NIST `PHYS02C`가 PR27의 원자입력 일관성 문제를 이미 해결했다고 읽으면 안 된다. `BLOCKERS.json`에 충돌 없는 source ID와 다음 입력을 기록했다.

## 공개 물리를 적용한 범위

원문에서 확인한 입력과 byte identity는 `EXTERNAL_SOURCE_CONTRACT.md/json`에 있다. Robertson et al.2015의 방출률·우주론·clumping/온도 가정, Hui–Gnedin1997의 재결합식을 사용한다. 본 프로그램의 과학계약은 `SCIENTIFIC_CONTRACT.md`다.

\[
\rho_{\rm SFR}=\frac{0.01376(1+z)^{3.26}}{1+[(1+z)/2.59]^{5.68}},\qquad
S=\frac{0.2\,10^{53.14}\rho_{\rm SFR}}{n_{H,0}},
\]

단, 분자와 분모의 comoving volume 단위를 일치시킨다. 구현에서는 Mpc³→cm³ 변환과 수소 질량으로 나누는 number-density 변환을 명시한다. z>약10은 관측이 직접 주는 값이 아니라 해당 모형의 연장이다. HM12 표의 최대 z15.93을20까지 조용히 외삽하지 않았다.

\[
\alpha_B(T)=2.753\times10^{-14}
\frac{(315614/T)^{1.5}}{[1+((315614/T)/2.740)^{.407}]^{2.242}}
\;\mathrm{cm^3\,s^{-1}},\quad T=20000\,\mathrm K.
\]

HII 영역 안에서는 HII와 HeII, 밖에서는 중성 기체를 가정한다. 내부 전자는 nH+nHe이고 체적평균 전자는 Q(nH+nHe)다. 따라서 재결합은 Q에 선형이다. Q를 다시 내부 전자밀도에 곱해 Q² 식으로 바꾸지 않는다. 이 조건부 closure가 He photon budget, HeIII 또는 에너지 방정식까지 해결하지는 않는다.

\[
\dot Q=S-RQ-U,\qquad R=C\alpha_B(n_H+n_{He}),\qquad C=3,
\]

U는 Q<1에서0이고 Q=1에서 max(S−R,0)이다. Q가 감소할 조건이면 감소를 허용한다. U의 적분은 **overlap 이후 미배정 광자 budget**이지 복사 에너지·흡수·escape의 물리적 해가 아니다. 전체 구간에서

\[
Q-Q_i+N_{\rm rec}+N_{\rm excess}=N_{\rm emit}
\]

를 보존한다. 기준 모형의 최종 budget은 방출5.68859191, 재결합0.80409052, 미배정3.88450139, 이온화 inventory1이다(수소 핵당 유효 광자 수). CaseB에 포함한 on-the-spot 재결합 광자를 다시 source로 더하지 않는다.

## Bianchi 적용과 새 수학적 해석

기존 source-pinned dust+Lambda axisymmetric Bianchi I background를 수정 없이 호출했다.

\[
a_\perp=ae^{-b},\quad a_\parallel=ae^{2b},\quad
s=\dot b=s_0a^{-3},\quad
H^2=H_{\rm fid}^2(\Omega_m a^{-3}+\Omega_\Lambda)+s_0^2a^{-6}.
\]

Wolfram 계산으로 trace H_i=3H, sigma²=3s² 및 Einstein constraint의 조합3(H²−s²)를 확인했다. 이 계산은 일반 상대론 전체 증명을 대신하지 않는다. 초기 r=s_i/H_i를 고정하고 같은 baryon/source/평균 a 조건으로 비교한다. radiation·thermal stress backreaction과 각도별 spectrum 재분배는 현재 식에 없다.

이번 부호는 모형 안에서 설명할 수 있다. x=ln(a/a_i), u=r²/(1−r²), H=H_F sqrt(1+uK(x))로 쓰면 K=H_F(a_i)²(a_i/a)^6/H_F(a)²>0이다. 아래 B_F=R/H_F, D_F=c sigma_T(n_H+n_He)/H_F로 정의한다. overlap 전 w=partial Q/partial u|0는

\[
w'+B_Fw=-\tfrac12KQ_F',\qquad w(0)=0.
\]

따라서 재이온화가 진행되는 Q_F'>0 구간에서 w≤0이다. 현재 source의 S/R은 전체 범위에서 증가한다. 실제로 v=[(1+z)/2.59]^5.68에 대해 d ln(S/R)/dx=−.26+5.68v/(1+v)>0이다. 초기 Q=0에서 이 조건은 Q_F가 증가함을 보장한다. 동일 부피 팽창까지 걸린 proper time이 줄어 유효 이온화 inventory가 지연된다. 이 sign argument는 제시한 감소를 뒷받침하는 **새 유도**이며 일반적인 시간가변·feedback source에 대한 부호 정리는 아니다.

구간 광학깊이의 첫 u 응답도 overlap 전 integrand D_F[w−KQ_F/2]로 음수다. overlap 이후 w=0인 공통 saturated 영역에는 −D_F K/2가 남는다. cap의 이동경계에서는 Q가 연속이라 선도 적분에 경계 jump 항을 추가하지 않는다. +/-r의 scalar 결과는 같고 b는 반대 부호여야 한다. 실제 비교에서 이를 확인했다.

PHYS22는 평균 H를 고정한 채 방향별 photon kernel의 초기시간 반응을 계산했다. 이번 계산은 평균 H의 shear 에너지 기여를 반영하는 전구간 축약 모형이다. 둘은 같은 효과를 두 방식으로 재검산한 것이 아니며, 합칠 때 고정한 변수와 누락한 각도 전달을 구분해야 한다.

균일·non-tilted 기체의 동일 proper-time 경계에서는 tau=integral c sigma_T ne dt가 방향 독립이다. 관측 방향별 같은 observed-z 경계를 비교하려면 emission time을 방향별로 역산해야 한다. 이번 평균 redshift를 그 observed-z로 표시하지 않았다.

## 수치 실행과 독립 검증

첫2048/4096/8192 ladder에서 |delta Q|=1.29633e−7가 기준1e−7를 넘었다. 실패 결과는 RUN001에 그대로 남겼다. 허용오차를 변경하지 않고16,384로 정밀화했다. RUN002는 이전4096/8192 자료를 exact input/code/data identity가 같은 경우에만 재사용했다.

| 검사 | 관측 최대 | 기준/해석 |
|---|---:|---|
| 8192→16384, 전구간 Q 차이 | 3.24195e−8 | ≤1e−7 |
| 같은 tau 차이 | 4.9860e−10 | ≤1e−8 |
| 별도 DOP853, 16,385 동일 출력점 Q 차이 | 1.08065e−8 | ≤1e−7 |
| 별도 DOP853, 같은 tau 차이 | 1.78572e−10 | ≤1e−8 |
| 별도 DOP853, z50/z90 차이 | <9e−9 | ≤1e−5 |
| FLRW photon-ledger 절대 잔차 | 1.59873e−14 | 정규화 잔차≤1e−10 |
| +/-shear scalar 비교 | Q/tau 동일 | 기준1e−12 |

정밀화의 Q 오차비는 약4로 midpoint의2차 거동과 일치했다. 이는 관측된 convergence이며 continuum interval certificate가 아니다. 독립 reference는 같은 논문 계수·상수를 사용하지만 primary model/step 함수를 import하지 않았고, adaptive DOP853+overlap event로 별도 구현했다. 초기5개 해석적/입력-domain 시험을 실제 RED→GREEN으로 진행했다. 초기 pytest 부재는 실행환경 문제로 기록했고 설치 후5개 실제 feature-missing FAIL을 보존했다. RUN002 첫 호출의 상대경로 처리 실패도 별도 로그에 남기고 복구했다.

최종14개 세밀한 trajectory의 측정 적분시간 합계는 **3.21초**다. 파일저장·그림·문헌·검토 시간은 이 수치에 포함하지 않는다. 기존 native solver와 통제된 속도 비교를 수행하지 않았으므로 가속 배율을 주장하지 않는다. 작은 redshift 구간에서 또 검증을 기다리는 대신, 계산 가능한 전구간 모형을 분리한 것이 이번 실행상의 개선이다.

## 과학적 우선순위가 어떻게 바뀌는가

fesc=.1/.3은 tau를 −.01272/+ .00869, C=2/5는 +.00262/−.00395, T=10000/30000K는 −.00466/+ .00239만큼 바꿨다. Q_i=.001은 +4.5405e−5다. 이는 정해진 한 변수씩의 scenario 변화이며 posterior·통계적 신뢰구간·원자율 fit 오차가 아니다. 이 범위의 효과는 r=.1의 평균팽창 효과2.61e−5보다 크다.

따라서 다음 논문 수준 비교에서는 source/thermal/초기조건의 불확실성과 shear 효과의 분리를 먼저 해야 한다. 작은 atomic remainder를 계속 더 엄밀하게 증명하는 일만으로 현재의 주요 astrophysical 불확실성이 줄지는 않는다. 미포함 radiation·angular transport 등 모형 오차도 수치 오차보다 클 수 있으므로 현재 delta tau를 관측 예측으로 홍보하지 않는다. 새로움(novelty)이나 논문 게재 가능성은 아직 확립하지 않았다.

## 짧은 DAG와 원 연구의 보존

완료된 baseline 경로는 **공개 입력 고정 → 전구간 paired histories → 독립 검증/과학 비교**다. 이 경로의 필요한 원자율 공급 문제는 HG97-B로 해소했다. 고유 RCT·HH·CR 증명이 이 세 노드의 선행 조건이 되지 않도록 했다.

다음 실행은 `DAG.json`에서 선택한다. N1의 cold/physical-source native adapter와 N2의 source-chronology/성능 수리를 병렬로 진행한 뒤 N3에서 실제 H/He+열+광자+Bianchi 전구간을 결합한다. N4의 BASS reduced-cell adapter는 지금 생성된 자료로 별도 병렬 시작할 수 있다. CR, He RCT, HH 원 연구는 각각 source identity와 unresolved input이 명시된 분기로 유지한다. 전체 원자 연구를 임의로 DONE 처리하거나 재개 지점을 잃어버리는 방식으로 가속하지 않는다.

시간 계획은 보장된 완료일이 아닌 작업 budget이다. 첫 native source/domain 통합은 반나절–2일, chronology/performance 수리는1–3일을 우선 배정한다. 두 결과가 통과하면 첫 full native paired history에1–3일을 배정한다. 추가 원자 입력이나 비국소 CR transport가 필요한 경우 해당 일정은 적용되지 않는다. 각 노드에서4시간이 지나면 실제 코드/입력/진단 상태를 checkpoint로 남기고 다음 최소 실험을 특정한다. 새 검증 계획만 반복해서 기존 DONE 노드를 다시 실행하지 않는다.

`BLOCKERS.json`은 해결·비차단 분리·실제 미해결을 구분하고, `RESUME.json`과 `START_CODEX_KO.md`는 low-cost LLM/local Codex 시작점이다. Repo별 전파는 additive branch의 handoff이며 기존 owner PR를 자동 병합하거나 production gate를 변경하지 않는다.

## 출처

- Robertson et al.2015, [arXiv1502.02024v2](https://arxiv.org/abs/1502.02024), ApJL802 L19, eq1/2/4/5.
- Hui & Gnedin1997, [astro-ph/9612232v1](https://arxiv.org/abs/astro-ph/9612232), MNRAS292,27, AppendixA.
- Madau2017, [arXiv1710.07636](https://arxiv.org/abs/1710.07636): overlap 이후 Lyman-limit absorption과 caseA/B 해석의 한계.
- Oñorbe et al.2017, [arXiv1607.04218](https://arxiv.org/abs/1607.04218): prescribed UVB rates와 self-consistent reionization history의 구별. 이번에는 이 논문의 코드를 실행한 것이 아니다.

SciSpace는 관련 연구 탐색에, 원문 PDF는 실제 계수 확인에, Wolfram은 명시한 대수 검산에 사용했다. 출판 논문 전체 PDF나 추출 원문은 전달 archive에 재게시하지 않는다.
