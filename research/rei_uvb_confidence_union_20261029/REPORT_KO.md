# REI UVB confidence-union 연구 결과 — 2026-10-29
기존 UVB 계수의 결정론적 EOS–Jeans 허용집합에 통계 공분산을 결합했다. 고정 template·알려진 공분산·Gaussian 오차 모형 아래에서 단일 κ의 95% nuisance-union 구간은 양수이나, 두 모수 공동 95% 영역의 κ 투영은 0을 포함한다. 원 DAG는 작업 33/88, 중앙 28/88이며 이번 원노드 증가는 0이다.

## 계산 대상과 조건
7개 BB13 관측의 datum은 log10[Γ_HI/(10^-12 s^-1)], C의 단위는 dex²다. 고정 저장 Puchwein2019 template m에 대해 X=[1,z-3.6], r=d-m+θv+j, a=(β,κ), θ∈[-1,1], j_i∈[l_i,u_i]를 사용한다. κ의 단위는 dex/redshift다. θ는 온도–밀도 관계 기울기의 보정 좌표이며 Bianchi 속도 tilt가 아니다. source bytes SHA256은 13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b로 유지했다.

통계 coverage 정리에는 추가로 d=m+Xa_*−θ_*v−j_*+ε, ε~N(0,C), 실제 nuisance가 고정 상자 안에 있음, C가 알려진 고정 양정치 행렬임, m·X·v·상자가 고정되고 평균모형이 맞다는 조건이 필요하다. 이번 실행은 이 조건부 정리의 계산을 검증한다. BB13 표만으로 해당 Gaussian 모형이나 고정 template의 물리적 적합성이 확립되지는 않는다.

## 유도와 계산식
A=(XᵀC⁻¹X)⁻¹XᵀC⁻¹, V=(XᵀC⁻¹X)⁻¹로 두고 j_c=(l+u)/2, j_h=(u-l)/2라 하면 c=A(d-m+j_c), G=[Av,A diag(j_h)]다. 결정론적 계수집합은 Z=c+G[-1,1]^8이며 support는 h_Z(s)=sᵀc+||Gᵀs||₁다.

E_q={δ:δᵀV⁻¹δ≤q}에 대해 nuisance-union은 U_q=Z+E_q이고
h_U(s)=h_Z(s)+sqrt(q sᵀVs)다.
따라서 좌표 k의 투영은 [L_k−sqrt(qV_kk),U_k+sqrt(qV_kk)]다. q₁=[Φ⁻¹(.975)]²≈3.841458820694124는 사전 지정한 한 스칼라의 양측 95% 보장에 사용하고, q₂=−2log(.05)≈5.991464547107982는 두 모수 공동 95% 보장에 사용한다. union은 실제 nuisance에 대응하는 Gaussian 집합을 포함하므로, 조건을 만족하는 각 고정 nuisance에서 coverage는 적어도 95%다.

동일 nuisance에서 중첩 모형의 차이는 ΔQ=Q_intercept−Q_affine=κ̂²/V_κκ다. 이 값은 nuisance별 두 Q를 따로 최소화한 통계량과 구별한다. κ 구간이 0을 가로지르면 ΔQ 최솟값은 내부에서 0이며, 상자 꼭짓점만으로 최솟값을 찾지 않는다.

## 실제 결과
| κ 집합 | 하한 | 상한 | 해석 |
|---|---:|---:|---|
| 결정론적 EOS–Jeans 상자 | 0.05361750476791550 | 0.09922533966611835 | 확률 수준 없는 계수 support |
| 조건부 scalar 95%, q₁ | 0.00613871527194178 | 0.14670412916209208 | 사전 지정한 단일 κ |
| 조건부 joint2 95%, q₂의 투영 | -0.00567749117590223 | 0.15852033560993609 | 공동 (β,κ) 영역의 κ 투영 |

ΔQ 범위는 [4.899030064039117,16.77807359164515]다. q₁과 q₂의 차이는 모순이 아니다. 투영한 공동영역은 한 좌표만을 대상으로 정한 구간보다 넓다.

## 실행과 독립 검토
동결된 새 프로그램을 한 번 실행했다. 새 8개 묶음 검사가 모두 통과했고 실행 종료 코드는 0이었다. 정확한 AX=I, AC Aᵀ=V, 정상방정식, 제곱완성 및 동일 nuisance의 직접 Q 차이, source 방향 support와 ellipsoid witness, 해석적인 작은 사례·내부 영점·고정 nuisance·입력 오류를 점검했다. rtol=1e-10, atol=1e-12를 유지했다. 원래 256-corner 캠페인과 기존 suite는 재실행하지 않았다.

새 이론은 서로 다른 작성자의 R6 PASS_SCOPED, 새 구현은 C9 PASS_SCOPED를 받았다. 원 PR257 역시 별도 작성자의 R6/C9가 완료됐다. 원 기록의 “256개 항등식 검사”는 실제 코드가 수행한 “256개 중첩 부등식 검사”로 보충 교정했다. 항등식은 독립적으로 유도했고 새 표적 검사에서 직접 확인했다.

정밀도 범위도 구분한다. 원 PR257은 Fraction.from_float로 binary64 실수상을 사용했다. 새 core는 Fraction(str(parsed value))의 십진 유리수계를 사용하며, 분위수·제곱근·출력은 binary64 반올림이다. 출력 차이는 원 허용오차 이내다. 새 대수 항등식의 exact 범위는 그 십진 유리수계이고, 표의 값은 numerically_checked다. 원 PR257과 동일한 유리수 문제라는 주장이나 방향 반올림 interval 인증은 채택하지 않는다.

## 자원과 보존
실행 wall은 0.15205098s다. 원 receipt의 0.160679 CPU-s는 알려진 prelaunch child 0.001970s를 제외했다. 원 receipt를 보존하고 별도 보충 기록에서 inclusive 관측값 0.162649 CPU-s로 교정했다. 미계측 tail용 1s reserve를 유지하면 source lineage는 609.913253 CPU-s이며, 별도 sibling reserve70을 포함한 기록값은 679.913253이다. 임시 main 상한700은 원 baseline600보다 16.67% 높아 기존 <50% 자동 증액 정책 범위다. 원 600/30/10 정책 상한을 복원했고, 원인별 미확인 비용과 과거 figure 배정 문제는 unresolved로 유지한다. 전체 세션 비용 PASS를 주장하지 않는다.

새 IVP·native build·rate-provider 호출·기존 캠페인 replay·새 render는 0이다. presentation65는 이전 단위에서 소진되어 새 그림을 실행하지 않았다. 수치표와 코드가 이번 계산의 출력이다. 단계별 ZIP/실제 백업 응답은 private delivery 기록에서 관리하며, 큰 조사·증거 묶음의 Git 게시 거절 기록은 보존한다. 공개 후보는 새 과학 결과·코드·공개 입력 투영으로 한정한다.

## 다음 연구
조건부 Γ_HI 보정의 통계적 집합과 실제 REI source-rate 오차를 연결하려면 source spectrum/absorber, redshift–proper-time clock, density와 source-to-observable map의 실제 소유 입력을 결속해야 한다. 이를 확보하기 전에는 Γ 오차를 물리적 F4/L4·native25·실제 온도/물리적 반경으로 전환하지 않는다. 다음에는 기존 공급자 branch의 실제 source-to-rate/observable derivative를 읽어 최소 연결을 선택한다. 완료한 수치 실행을 새 환경에서 반복하지 않는다.

원전: [Becker–Bolton2013 Table1/2](https://academic.oup.com/mnras/article/436/2/1023/1118137). 정리의 논증과 적용 조건은 review/PHASE1_THEORY.md, 실제 판정은 SCIENTIFIC_DECISION.json, 재개 지시는 HANDOFF_KO.md에 있다.

## 최종 보존·게시와 상류 갱신
R1–R10/C1–C10 전체20단계의 소유자 Drive·Dropbox 완료 ACK 및 동일 size를 확인했다. 새 과학 결과32경로/186779 bytes는 Draft PR260에 실제 게시됐으며 source commit ed21c58b44ccabeb5d621628579fe80fea3df180이다. 승인 local tree와 원격 tree가 같고 결과·보고서·C9기록3개는 원격내용과 직접 대조했다. 전체 조사·ZIP·providerACK는 소유자 비공개 보존으로 유지한다. 최종 메타데이터는 별도 후속 commit으로 기록한다.

게시 준비에서 관측된 promisor fetch24.177CPU-s, CLI조회0.041s, APIrequest준비0.637s, stage packaging2.124795674s를 과학 CPU0.162649s와 구별해 보존했다. 예측되지 않은 준비 비용을 지우지 않았고, 다음 게시에는 원 main600 대비25% 임시상한750을 적용한 뒤600/30/10을 복원한다. 알려진 부분합과 reserve만으로 전체 비용 PASS를 선언하지 않는다.

최종 재조회 PR259 HEAD045118543c266f164c4bd177ac0194ee1ba22096은 기존17상태 그림의10/10쪽 시각 검토 완료를 기록한다. owner 승인 completion 비용으로 presentation누적65.980312494가 유지된다. 본 단위의 새render는0이며 해당 업데이트는 본 통계결과·33/88·28/88·F4/L4에 변화를 주지 않는다.
