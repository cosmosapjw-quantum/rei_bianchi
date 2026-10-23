# REI 동위원소–전하–열 결합: C1 계약과 유한 검산

2026-10-22 KST. 이번 재개에서 실행한 범위는 최신 READY 노드
`COUPLED_ISOTOPE_NATIVE_CONTRACT`의 **C1**이다. 핵반응으로 생기는 핵종을
기존 이온화·열 진화에 연결할 때 필요한 상태, 전자 수, 에너지 기준과
허용 조건을 실제 수식으로 고정하고 독립 실행 가능한 검산을 작성했다.
새 우주론 IVP와 기존 sweep 재실행은 모두 0회다. 실제 판정과 게시·보존
상태는 `evidence/INDEPENDENT_REVIEW.json`과 `delivery/`의 영수증을 따른다.

## 재개 지점과 기존 결과

최신 상태는 PR 번호만으로 판단하지 않았다. 현재 REST updated 목록에서
PR219의 최종 dossier 반환이 PR220보다 나중이다.

| 기준 | 이번에 확인한 identity | 사용한 범위 |
|---|---|---|
| PR219 | `5a1e5220b301a1c497f2863d6fd823e605faba80` | 핵반응·dossier 완료와 다음 READY 계약의 권위 |
| PR220 | `8be7533cc97b3302bf42608699d6e8313ed6af8a` | 127 main + 2 full62 oracle, 고정 33좌표 lift, 독립 원자 donor |
| REC119 복구 반환 | `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7` | 126개 별도 cohort와 복구 댓글 연결 |

PR219의 원래 원자 기록 83개와 조건부 핵반응 배경 82개, 이후 dossier의
새 사례·control은 그대로 보존한다. PR220/REC126과 합산하지 않는다.
PR219의 외부 UV는 5–60 eV, PR220은 5–200 eV이므로 source identity도
서로 다르다. 이번에는 해당 차이를 없애는 cohort 통합을 하지 않았다.

기존 원본 보존본은 현재 메타데이터로 다시 확인했다. PR219의 양쪽
보존본 크기는 76,130,340 B, PR220의 Dropbox 보존본은 58,890,242 B로
기존 영수증과 일치한다. 과거 full GET/SHA256/CRC 영수증을 재사용했으며,
이번 단계에서 큰 원본 ZIP 전체를 다시 내려받아 검증했다는 뜻은 아니다.
접근 가능한 이전 대화 요약은 조회했으나 다른 세션의 전체 transcript와
살아 있는 worktree는 `UNAVAILABLE`이다. 상세 범위는 SOURCE_INTAKE.json에 있다.

## 1. 핵반응 source는 21개 절대 abundance에 넣는다

보존되는 baryon number로 정규화하여

\[
Y_i=\frac{n_i}{n_B},\quad i=(A,q),\qquad
\dot n_B=-3Hn_B,\qquad \sum_i A_iY_i=1
\]

로 둔다. n, H1, D, T, He3, He4, Li6, Li7과 채택된 비음수 charge state의
21개 slot을 유지한다. 핵반응 branch의 사건률 \(R_{jb}\)는
events per baryon per second이며,

\[
\dot Y_i=F_i^{\rm atom}+\sum_{jb}\nu_{i,jb}R_{jb}.
\]

각 branch에서 \(A^{\mathsf T}\nu=0\)이어야 한다. 핵종별 총수는
반응으로 달라질 수 있으므로 이를 고정해 놓고 사후에 T를 붙일 수 없다.
특히 \(Y_T=0\)인 시작점에서 T charge fraction은 정의되지 않는다.
첫 T 생성 사건의 물리적 daughter branch가 절대 source를 정해야 한다.

PR220의 fixed lift는 n=T=0과 고정 동위원소 inventory를 포함한다.
이미 채택된 \(D+D\to H1+T\)의 사건 벡터는 T 성분이 +1이므로 그 lift의
상공간 밖에 있다. 이번 검산은 이 반례를 실제 정수 벡터로 확인했다.
이는 해당 고정 lift를 새 source에 그대로 적용할 수 없다는 국소 결론이다.
반사 대칭을 보존하는 기하학적 축약이나 새롭게 증명되는 다른 축약까지
부정하는 결론은 아니다.

공유 electronic generator \(G_Z\) 아래에서 \(Y_{Aq}=Y_Af_{Aq}\)를 미분하면

\[
\dot f_{Aq}=(G_Zf_A)_q+
\frac{S_{Aq}-f_{Aq}S_A}{Y_A},\qquad S_A=\sum_qS_{Aq}.
\]

따라서 electronic rate가 같아도 동위원소별 source 항이 다르면 공통
fraction은 유지되지 않는다. 반대로 \(S_{Aq}=f_qS_A\)인 정렬된 source는
공통 fraction을 유지할 수 있다. 이 특수 경우도 함께 검산하여 축약의
적용 조건을 필요 이상으로 좁히지 않았다.

## 2. 자유전자는 생성된 weak electron 수와 다르다

positron과 음이온을 제외하고 모든 자유전자를 포함하면

\[
Y_{e,\rm total}=q^{\mathsf T}Y,\qquad
\Delta N_e=q^{\mathsf T}\nu.
\]

bound electron 수와 함께 보면

\[
\Delta N_e+\Delta N_{\rm bound}=Z^{\mathsf T}\nu.
\]

따라서 핵전하 증가, 기존 전자의 shake-off, 자유전자 재포획은 서로
다른 기작이지만 같은 전하 보존식 안에서 연결된다.

| 조건부 endpoint | 자유전자 변화 | bound electron 변화 |
|---|---:|---:|
| n → H1 II + e + antineutrino | +1 | 0 |
| T I → He3 II + e + antineutrino | +1 | 0 |
| T II → He3 III + e + antineutrino | +1 | 0 |
| T I → He3 III + 2e + antineutrino | +2 | −1 |

네 행 모두 baryon·전하 보존을 만족한다. 마지막 행의 두 자유전자는
weak decay가 두 전자를 새로 만들었다는 뜻이 아니다. 하나는 기존 bound
electron이다. 실제 tritium beta 최종상태는 excited/continuum state를
포함하므로 이 endpoint들의 물리적 확률은 별도 입력이다. 문헌에서
확률값을 추정하여 채우지 않았다. [Williams–Koonin1983; Frolov2015/2016,
SOURCES.md]

fast electron을 유지하면 neutrality에는 thermal+fast 합이 들어간다.
공통 온도 EOS와 thermal atomic rate에는 thermal subset을 쓴다. 이 둘을
같은 전자 수로 처리하거나 relativistic fast electron에 cold Thomson
계수를 그대로 적용하는 것은 이 계약이 허용하는 closure가 아니다.

## 3. 기존 두 beta decay 항을 동시에 켜지 않는다

실제 PR220 donor의 `atomic_network.py`는 decay matrix를 만들어 RHS와
Jacobian에 넣는다. PR219 nuclear module도 독립적으로 beta family와
decay constant를 갖는다. 새 결합에서 둘을 동시에 더하면 같은 사건을
중복 계산한다. 이는 앞으로 모듈을 합칠 때 발생하는 구체적 위험이며,
기존 n=T=0 계산이 이미 잘못되었다는 주장은 아니다.

두 입력은 수치도 완전히 같지 않다.

| checked-in 정의 | half-life [s] | lambda [s^-1] |
|---|---:|---:|
| 12.32 Julian years | 388,789,632.0 | 1.7828335004569908e-9 |
| 12.312 × 365.24219878 days | 388,528,872.5991767 | 1.784030041121361e-9 |

\[
\lambda_{\rm selected}/\lambda_{\rm legacy}-1
=6.711454906269676\times10^{-4}
=0.06711454906269676\%.
\]

새 coupled mode의 단일 owner는 기존 nuclear
`EVALUATED_DECAY_INPUTS.json`으로 정했다. 그 모드에서는 atomic beta block을
별도로 더하지 않도록 구현해야 한다. **이번 C1에서는 이 계약과 중복
거부 검산을 완료했으며, 기존 production RHS를 변경하지 않았다.**

## 4. 핵반응 Q와 이온화에너지의 기준을 맞춘다

PR219의 실제 `_q_j()`는 bare nuclear mass 차를 사용하고 beta-minus에서
전자 rest mass를 추가로 뺀다. Li는 atomic mass−3me 근사로 atomic binding을
무시한다. 따라서 기존 Q를 neutral-atom Q라고 다시 이름 붙일 수 없다.

\(B_{Aq}\)를 양의 총 전자 binding energy,
\(I_{Aq}=B_{A0}-B_{Aq}\)를 누적 ionization energy로 두면

\[
Q_0=Q_{\rm bare}+\sum_A B_{A0}\nu_A,
\qquad
Q_{\rm available}=Q_0-\Delta I
=Q_{\rm bare}+\sum_i B_i\nu_i.
\]

두 표현은 일관된 mass/binding table에서 같은 에너지를 서로 다른 기준으로
쓴 것이다. 이 관계를 34개 방향 × 3개 charge assignment의 102개 제조
입력에서 확인했다. 경험적 질량값이나 동위원소 threshold 정확도를
새로 검증했다는 뜻은 아니다.

에너지는 사건마다 한 번만 배분한다.

\[
Q_0+W=\Delta I+\Delta E_{\rm th}+\Delta E_{\rm fast}
+\Delta E_{\rm exc}+\Delta E_{\gamma,\rm ret}
+E_{\gamma,\rm esc}+E_\nu.
\]

빠른 생성물이 열화될 때는 fast reservoir에서 감소한 만큼 thermal
reservoir가 증가한다. 이때 nuclear Q를 다시 더하지 않는다. 의도적으로
Q를 thermal과 fast에 모두 넣은 음성 대조군은 정규화 잔차 1/3으로 거부됐다.

원자 photo rate나 RR/DR number-rate coefficient만으로 열에너지 전달이
정해지지는 않는다. photo excess energy, 포획 전자 운동에너지 및 cascade,
secondary electron·핵반응 photon 재처리에는 각 energy moment와 source
field가 필요하다. Grackle의 chemistry/thermal interface는 재사용 후보지만
현재 21-state nuclear daughter closure의 완성 증거로 취급하지 않았다.

## 5. 열적 입자 수 변화가 온도식에 들어간다

열적 common-T pool에 대해

\[
C_{\rm th}=\sum_iY_{i,\rm th}+Y_{e,\rm th},\qquad
e_{\rm th}=\frac32k_BT C_{\rm th}
\]

이며, \(Q_{\rm th}\)를 J m^-3 s^-1 단위의 순수 translational deposition으로
정의하면

\[
\boxed{\dot T=-2HT-\frac{T}{C_{\rm th}}\dot C_{\rm th}
+\frac{2Q_{\rm th}}{3k_Bn_BC_{\rm th}}.}
\]

모든 입자가 thermal인 제한에서는
\(\dot C_{\rm th}=(1+q)^{\mathsf T}\dot Y\)이다. 기존 atomic-only 모형에서
가능했던 전자 source만의 표현을 핵반응계에 그대로 적용하면 핵 입자 수
변화를 놓친다. 실제 사건 벡터 H1 II+n→D II에서
\(\Delta Y_e=0\)인데 \(\Delta C_{\rm th}=-1\)이다.

물리적 의미는 단순하다. 같은 translational energy가 더 많은 열적 입자에
나뉘면 온도가 내려가고, 입자 수가 줄면 그 효과는 반대가 된다. 반응
가열·냉각과 이 입자 수 효과는 온도식에서 따로 계산해야 한다.
고정 조성·무가열 극한에서는 T∝a^-2, 고정 체적·threshold H photoionization
제조 대조군에서는 C가 1→2가 되면서 8192 K→4096 K가 나왔다. 이 수치는
우주론적 열 이력이 아닌 에너지/EOS 검산 예다.

## 실행 및 근거 상태

`check_contract.py`는 Python 표준 라이브러리만 사용한다. 실제 최종 실행은
exit0, **191개 명명된 검산 통과**다. 정수 보존 잔차와 채택된 부동소수점
대수 항등식의 정규화 잔차는 0이었다. 후자의 허용치는
64epsilon=1.4210854715202004e-14이다. 정수·정확히 표현되는 제조 입력을
택한 검산이므로 임의의 실물 rate/trajectory에 대한 오차 인증은 아니다.

실행 시간은 wall0.02289s, CPU0.02174s, peakRSS11,904KiB였다. 이는 실행
영수증이며 속도 향상 benchmark가 아니다. 실제 Wolfram evaluator도 EOS,
fraction source, Q-reference 세 항등식에서 잔차0을 반환했다. Symbol undefined
경고는 원출력에 보존했고 의도적으로 기호 변수를 사용한 검산으로 분류했다.

| 근거 상태 | 이번 결과 |
|---|---|
| derived | 전하/전자 식, Q 기준 변환, changing-particle EOS, source-corrected fraction 식 |
| numerically checked | 191개 유한 대수/반례/거부 대조군 |
| implementation-verified | 해당 표준 라이브러리 진단 스크립트의 실제 실행 |
| literature-supported | beta 최종 전자상태의 비자명성, atomic/thermal source 분리 필요성 |
| unresolved | 실제 daughter branching, charge-resolved nuclear applicability, stopping, RR/DR energy moments, 닫힌 photon field |
| unchanged | 기존 PR219/PR220/REC119 scoped 결과와 각 cohort |

## 다음 의존성

이번 C1은 다음 항목을 요구 입력으로 확정했다. C2에서 실제 코드 함수와
source row에 연결할 대상은 charge-resolved daughter/rate, 일관된 mass와
ionic binding table, 단일 beta owner, atomic cooling energy moments,
thermal/fast 분할과 radiation source다. C3 이후의 native operator·ODE 연결,
FLRW/LRS 검증과 수렴성 평가는 별도 미완료 단계로 남긴다.

재개 방법은 RESUME.md, 재현은 README.md, 단계 상태는 DAG.json을 따른다.
이번 단계의 수용이 전체 coupled production의 수용을 뜻하지는 않는다.
