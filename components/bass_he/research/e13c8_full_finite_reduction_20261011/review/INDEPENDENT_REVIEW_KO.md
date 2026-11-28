# E13C8 전체 유한 captured OFF 구간의 독립 검토

## 판정

**`PROMOTE_SCOPED_FULL_FINITE_CAPTURED_OFF`**로 판정한다. E13C7의 실제 NCP 반환 2,331경로를 이전 수용 6경로, 여기서 수용한 8경로 및 정확한 영 경로 95개와 합친 전체 2,440경로·4,884구간의 유한 captured 관측량이 대상이다. 모든 34개 raw 전체 구간은 이전 수용 구간에 포함되며 폭이 증가하지 않는다. 수용 대상은 서로 다른 N의 이전 결과를 명시적으로 포함한 전체 구간이다. 전체 2,440경로를 모두 N1024로 새로 계산했다는 뜻이 아니다.

현재 미해결 차단 사항은 없다. Physical·continuum·production·receiver는 **HOLD**를 유지한다. 새 중량 작업 0개라는 이번 소유자의 결정은 완료된 계산을 반복하지 않고 필요한 새 이론·경량 진단을 먼저 수행한다는 계약과 일치한다. 이 판단은 다음 정확도 목표나 새 방법을 대신 정하지 않는다.

## 입력과 실제 반환의 연결

실제 반환 ZIP은 124,152,692 bytes이며 SHA-256은 `a7a0fd6e58a88140071a1b623897efbd35748c86c4eda6956a937171eefe6c8f`다. 소유자가 수행한 실제 ZIP 복구에서는 18,800개 member와 18,799개 payload의 bytes/SHA를 검증했다. 독립 검토자는 그 intake 영수증과 실제 manifest identity를 재사용하고, 모든 경로의 핵심 `RESULT.json`, `ADMISSION.json`, `COMPLETE.json` 6,993개 파일의 실제 bytes와 연결을 별도로 확인했다. 원격 업로드 ACK는 이 수치 검토를 대체하지 않는다.

사용한 source lock은 `386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f`, execution lock은 `c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4`다. 반환된 순서 있는 경로 모음의 semantic은 `00b2d0133fb71f82d4994d340ca0a342bf8490c4bde2b24ab47ae84645ac8de4`로 독립 재계산과 일치했다.

검토자는 후보 코드와 과학 kernel을 작성하거나 수정하지 않았으며, 후보 또는 vendor 모듈을 import하지 않았다. 기존 독립 checker를 재사용하되 반환 경로가 package 밖에 있는 경우의 **표시 경로 처리만** reviewer 파일에서 바꾸었다. 그 변경과 원본 해시는 `REVIEWER_ADAPTATION_PROVENANCE.json`에 보존했다. 수치 assertion과 원래 E13C7 과학 코드는 바꾸지 않았다.

## 수행한 검토

| 독립 검토 | 통과 확인 수 | 실패 | 실제 시간 |
|---|---:|---:|---:|
| 2,331경로의 저장 관계와 직접 전체 합산 | 2,132,980 | 0 | 47.6387 s |
| 원래 reducer와 정확한 끝점·CSV 대조 | 200 | 0 | 0.0639 s |
| 별도 node endpoint를 사용한 파생 관측량 | 2,671 | 0 | 0.2459 s |
| 새 잔여 폭·병렬 telemetry 분석의 정의와 합계 | 11,940 | 0 | 1.1563 s |

총 2,147,791개 assertion에 실패는 없었다. 숫자는 서로 독립적인 물리 정리의 개수가 아니라 실제 저장 데이터의 반복된 관계 검사 수다. 새 coefficient evaluation·ODE solve·MPI 실행은 모두 0이다. 이 검토는 이미 완료된 중량 과학 계산을 다시 실행하지 않는다.

경로마다 source/input identity와 실제 이전 JSONL 조각, 저장한 수치 semantic, 최초 영 photon stock, incoming photon carry, undamped moment 누적, species별 합계, signed energy seam, center-radius 포함 관계와 remainder 예산을 확인했다. 각 경로의 34개 비교를 별도의 exact Fraction 연산으로 재구성했으며 overlap·nesting·폭 비증가 판정을 저장된 boolean과 대조했다.

## 전체 합산과 수용 구간

관측량 \(q\)에 대한 경로별 가중 구간을 \(J_i^{(q)}=w_iI_i^{(q)}\)라 두면, 새 전체 구간은 다음 직접 합이다.

\[
J_{\rm full,new}^{(q)}
=\sum_{i\in R_{2331}}J_{i,N1024}^{(q)}
+\sum_{i\in L_8}J_{i,\rm chosen}^{(q)}
+\sum_{i\in P_6}J_{i,\rm admitted}^{(q)}.
\]

영 경로 95개의 기여는 정확히 0이다. 모든 가중치는 원래 양의 점 가중치이며 한 번만 적용했다. 이전 전체 구간도 같은 disjoint 집합의 이전 끝점을 직접 더해서 재현했다. 기존 구간을 빼서 새 구간을 만들거나, interval intersection으로 폭을 줄이거나, 실패 경로를 이전 값으로 대체하지 않았다.

| 관측량 | E13C7 로컬 수용 후 전체 폭 | 실제 NCP 반환 합산 후 폭 | 폭 감소율 |
|---|---:|---:|---:|
| \(P_{\rm final}\) | \(6.081259221168360060912\times10^{-17}\) | \(1.657292521990147877067\times10^{-18}\) | 약 97.274754% |
| \(H_{\rm total}\) | \(3.883292513115486482735\times10^{-16}\) | \(9.214884781103738168091\times10^{-18}\) | 약 97.627043% |

표의 십진수는 표시값이다. 정확한 유리수 끝점과 34개 비교는 `INDEPENDENT_FULL_SUMS.json`에 보존했다. 이 직접 합은 원래 reducer의 전체 결과와 정확히 일치한다. CSV 역시 개행을 포함한 실제 bytes가 독립 생성본과 일치했다. 수용한 reduction semantic은 `d647ba154b84baf22a3f85f9b7dca19f029b97f466838c036a9d3321f4c315d1`이다.

## 파생 관측량의 단위·부호 검사

마지막 에너지 stock은 captured endpoint 에너지와 저장한 energy correction을 연결해야 한다. 독립 검토에서는 후보 분석이 사용하는 segment 선택과 다른 원자료인 `OFF_NODES.csv`의 step 2 endpoint 2,440개를 사용했다. 그 \(u_i\)와 \(w_i\)가 마지막 segment의 captured 값과 정확히 일치함을 확인한 뒤

\[
U_{\rm final}
=\sum_i\frac{\widehat u_i\widehat w_i}{\widehat\epsilon_{\rm erg/eV}}
+\Delta U_{\rm full}
\]

를 재구성했다. Hat은 기존 계약과 같은 binary64 값의 정확한 유리수 lift다. 에너지 변환 상수로 나누는 연산과 가중치는 각각 한 번이다. 이 단계에서 변환 상수를 새로운 정확한 십진 상수로 바꾸지 않았다.

초기 photon stock이 0인 같은 유한 target에서 다음 세 ledger 구간이 모두 0을 포함한다.

\[
P_{\rm final}+A_{\rm total}-Q_N,
\qquad
U_{\rm final}+B_{\rm total}+Z-Q_E-A_{\rm seam},
\qquad
H_{\rm total}-B_{\rm total}+\sum_s\chi_sA_s.
\]

\(A_{\rm seam}\)은 부호를 보존한 에너지 jump와 true photon stock의 곱의 합이며 에너지 ledger에서 **뺀다**. \(\chi_s\)는 기존 이온화 에너지 `(13.598434599702, 24.587389011, 54.41776)`의 lift다. Captured mask의 cutoff `(13.6, 24.59, 54.42)`와 혼동하지 않았다. 양의 분자·분모 구간에서 얻은 다섯 비율의 정확한 끝점과 표시값도 검토했다.

Ledger 중점은 cancellation 때문에 거의 0이다. 그 중점으로 나눈 큰 relative width 수치는 유용한 정확도 지표가 아니므로 ledger는 absolute 끝점과 zero inclusion으로 해석해야 한다. 관측량 및 비율은 같은 유한 captured 계산의 결과이며 continuum efficiency나 실제 물리 오차 보장을 뜻하지 않는다.

## 잔여 폭과 실제 병렬 실행의 해석

새 잔여 폭 분해는 저장된 certified half-width를 양의 항들로 배분한다. 이전 photon radius의 항별 배분을 절댓값 gain으로 전파하고, seam과 누적의 outward excess를 별도로 더한다. Moment는 species 구간 합을 쓰고 photon stock은 마지막 endpoint만 사용한다. 2,345개 nonzero 경로의 새 attribution 행이 각 half-width와 정확히 일치하며, 분류별·출처별 합계가 독립 전체 폭을 재현함을 확인했다.

광자 half-width의 약 60.257817%는 midpoint truncation 배분, 39.742183%는 coupling bound 배분이다. 열에서는 각각 65.948360%, 34.051640%다. 이 배분은 실제 오차의 유일한 원인 분해가 아니다. Coupling 항의 incoming radius 의존성이 남아 있으므로 이를 \(N\)과 무관한 floor나 물리적 오차 하한으로 해석할 수 없다.

실제 실행은 64개 계산 rank, rank당 thread 1, 서로 다른 CPU 0–63을 사용했다. Controller wall은 2,037.825321570 s, MPI launcher wall은 1,994.250447431 s다. Rank wall 평균/최대 약 98.439877%는 경과시간의 부하 분산 지표다. UTC 작업 구간의 겹침도 관측되지만 실제 CPU busy-time 표본은 없다. 따라서 CPU 이용률은 `NOT_MEASURED`, 같은 작업의 직렬 대비 speedup은 `NOT_ESTABLISHED`다.

Rank별 lifetime 최대 RSS를 합한 값은 서로 다른 시점의 최대값 합이며, 실제 동시 전체 memory peak가 아니다. 사후 관측한 경로 시간을 고정해서 다시 배분한 LPT 값도 실행한 새 scheduler의 성능이 아니다. 이 상한을 유지한 성능 분석과 현재 새 중량 작업 0개 결정에 차단 사항은 없다.

## 최종 한계와 다음 상태

이번 수용은 상속한 directed-interval 수학적 보장 아래 같은 frozen gas, source, mask, 초기값, 양의 가중치와 seam을 유지한 유한 captured OFF 구간에 한정된다. 이전 사건 경로의 미세한 captured branch 차이를 자연 임계값의 새 해석으로 바꾸지 않았다. 새 물리 모델·기체 진화·연속 극한·생산용 타당성은 입증하지 않았다.

중량 반환의 scientific admission과 전체 정확한 합산은 이 단계에서 닫혔다. 추가로 필요한 과학 목표가 정해지기 전에는 완료된 N1024 batch를 재실행하거나 자동 N2048 전체 계산을 시작할 근거가 없다. 이후의 파일 게시·백업 보수·최종 전달 package readiness는 별도 전달 기록에서 확인하며, 이 독립 과학 판정이 그 완료를 대신 주장하지 않는다.

기계 판정과 모든 근거 파일의 정확한 identity는 `INDEPENDENT_DECISION.json`에 있다.
