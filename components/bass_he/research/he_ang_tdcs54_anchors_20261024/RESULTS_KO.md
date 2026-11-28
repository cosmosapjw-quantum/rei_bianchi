# HE-ANG-TDCS54-ANCHORS — PASS_SCOPED, C10 실제 전달 대기

## 확보 범위와 입력

Jones–Madison, Phys. Rev. A62,042701(2000), Table IV와 article p8/Fig.10의
각도 설명에서 확보한 H(1s) TDCS 입력을 구현했다. 입사54.4eV, 느린 전자5eV,
느린 각도210도 CW, 빠른 각도4도 또는10도 CCW의 두 located joint 점이다.
다음 여섯 셀은 원전의 atomic units로 보존하며 추가 정규화 인자를 넣지 않았다.

| Fast CCW | Slow CW | CDW-EIS | CCC99 | Experiment |
|---:|---:|---:|---:|---:|
| 4° | 210° | 1.83 | 2.58 | 1.52 |
| 10° | 210° | 0.99 | 1.51 | 1.24 |

전체 Table IV의8개 특징량,24개 단면적 값과16개 printed ratio도 그대로
보존했다. 나머지 행은 peak-height 특징량이며 slow angle이 알려진 좌표가
아니다. Located2, binary-height4, all-features8의 세 그룹을 분리했다.
두 점을 보간하거나 continuous joint law를 만들지 않았다.

Source identity, PDF hash, producer와 불확실성은 source/의 원문 provenance를
따른다. CDW-EIS는 원전의 exchange-neglect 근사이고 CCC99는 unpublished
Bray 제공값이 이 논문에 실린 것이다. 실험은 Ehrhardt–Röder1997의 재수록이다.
기존 CCC raw-amplitude kernel, spin weights, count2, factor4를 적용하지 않았다.
무한 핵질량 원전이며 fast energy 수치나 finite-mass recoil를 새로 만들지 않았다.
`recoil peak`는 전자 각분포의 로브 이름이다.

## 실제 exact 계산 결과

Theory Eqs1–8을 Fraction으로 구현했다. 공통 scale A는 실험 명목값에
곱하며 model=A*u*experiment다. 다음은 printed nominal values의 정확한
최적화 결과다. 분수는 authoritative하고 decimal은 표시용이다.

| 그룹 | Producer | 자유 A* | 자유 delta* | delta* 표시 |
|---|---|---|---|---:|
| Located2 | CDW-EIS | 9435/9424 | 637/3145 | 20.254372% |
| Located2 | CCC99 | 1717/1178 | 565/3434 | 16.453116% |
| Binary heights4 | CDW-EIS | 17617/17658 | 2875/17617 | 16.319464% |
| Binary heights4 | CCC99 | 9514/8829 | 1495/9514 | 15.713685% |
| All features8 | CDW-EIS | 17547/18544 | 1593/5849 | 27.235425% |
| All features8 | CCC99 | 21585/16568 | 2179/7195 | 30.284920% |

CCC99의 located 두 점은 자유 최적 scale1717/1178이 지정한 상한27/20보다
크다. 따라서 A∈[13/20,27/20]에서는 Ac=27/20이고 q(Ac)=44/171,
약25.730994%다. CDW-EIS의 located 자유 최적 scale은 그 상자 안에 있다.
δ=1/10과 그 scale 상자를 사용한 nominated deterministic scenario에서는
세 그룹 모두 두 producer의 공통 scale 교집합이 공집합이다. 이는 명시한
조건부 상자 모형의 비교 결과이며 통계적 기각, 경험적 보정 또는 생산용
cross-section 변경이 아니다. 원전이 이 독립 상자를 검증했다고 주장하지 않는다.

Located anchor의 scale-free 비교는 다음과 같다.

| Quantity | Exact value |
|---|---|
| Experiment d4/d10 | 38/31 |
| CDW-EIS model4/model10 | 61/33 |
| CCC99 model4/model10 | 258/151 |
| CDW Q=(model ratio)/(experiment ratio) | 1891/1254 |
| CCC99 Q | 3999/2869 |
| δ=1/10의 조건부 Q 범위 | [9/11,11/9] |
| 실험 명목 비율의 조건부 민감도 범위 | [342/341,418/279] |

A의 소거와 이 sharp endpoint는 정확한 대수다. 실제 측정의 covariance나
확률모형이 공급되었다는 뜻은 아니다. 작은 전자 사이각146도/140도와
slow polar angle150도는 source의 반대 각도 감각으로부터 구했다.
실제 vector norm/dot 검사는 절대2e−14 기준을 통과했다. 이는 원전 좌표의
표현이며 유한질량 lab/COM 변환이 아니다.

## 인쇄 비율과 원전 요약

16개 printed ratio를 별도로 보존하고 nearest0.01 conditional printing
model에서 모두 compatible임을 확인했다. 예를 들어 nominal0.91/1.09는
91/109이고 printed0.84와 차이는−14/2725다. 절대차가0.005보다 크지만,
분자·분모·비율이 각각 인쇄된 상황의 ratio 범위[181/219,183/217]는
printed ratio 상자와 겹친다. 단순한 ±0.005 quotient gate로 false failure를
만들지 않았다. 이 구현은 고정표의 nominal endpoints가 h=.005보다 큰
범위에 한정하며 generic 작은 양수의 lower endpoint나 물리 오차를 주장하지 않는다.

원전의 approximate summaries는 다음과 같이 별도 보존했다.

- Binary: CDW1.00±0.16(16%), CCC1.08±0.17(16%).
- All features: CDW0.95±0.25(26%), CCC1.30±0.39(30%).

특히 all-CDW의 exact nominal delta*=1593/5849=27.23542485895…%를
26%로 바꾸지 않았다. Approximate summary와 재계산의 차이를 출력에 남겼다.
Source summary는 descriptive comparison이지 exact acceptance gate가 아니다.

## 실제 검증, 실패와 비용

최초 planned3child는 모두 종료0/PASS였다. Fraction equality와 독립 frozen
hand/R6/Wolfram rational oracle를 사용하는14개 test method가 통과했다.
Positive input/float·bool 거부, 공통 scale 방향, 구성 witness, touching/empty
intersection, 한 점/같은 ratio, clipped optimum와 q≥1, δ0 및 δ≥1 거부,
scale cancellation와 sharp endpoints, source signs/norms,24+16원전값과
2located 제한, conditional printing과 descriptive-summary 차이를 검산했다.
Kernel을 test oracle로 재사용하지 않았고 기존 kernel/suite를 실행하지 않았다.

독립 C9 첫 pass의 유일한 finding C9-FIG-01은 왼쪽 kinematics annotation이
fast4도 CCC99 marker와 일부 겹친다는 표시 문제다. Root가 sole reserve를
승인했다. 원래 plot code, runner, PNG와 SVG는 reviews/C9-FIG-01_BEFORE/에
보존하고 annotation x를.03에서.40으로만 바꿨다. 실제 plot-only child를
한 번 실행해 PASS했고 새 PNG를 열어 겹침 해소를 확인했다. 데이터·축·caption,
Fraction core, source, tests와 실제 analysis 출력은 바꾸거나 재실행하지 않았다.
독립 C9는 실제 변경과 결과를 확인해 C9-FIG-01을 닫고
PASS_AFTER_FIGURE_CORRECTION으로 판정했다. Root는 PASS_SCOPED를 채택했다.

| Child | CPU seconds | Wall seconds | 판정 |
|---|---:|---:|---|
| 01_tests | 0.04848099999999999 | 0.06792041000153404 | PASS,14methods |
| 02_source_analysis | 0.03323699999999999 | 0.03571938499226235 | PASS,24values/16controls |
| 03_plot | 1.214902 | 1.2202520070131868 | PASS,원래figure |
| 04 C9-FIG-01 plot reserve | 0.591269 | 0.6193045279942453 | PASS,주석위치수정 |
| 측정 누적 | 1.887889 | 1.9431963300012285 | 4children,reserve1 |

새 CPU8/wall30 allocation에서 측정된4child+runner 구간은 cap 안에 있다.
각 child CPU2, wall5/5/10/10, memory512MiB, threads1이다. 실패·측정 cap
overshoot·old suite replay·새 IVP·provider solve는0이다. Matplotlib cache는
별도 tdcs54_ops/ 아래 있으며 Git/package에 넣지 않는다. 두 render의 시간
차이를 성능 개선으로 해석하지 않는다. Host orchestration, source acquisition,
일부 준비·문서 I/O와 remote symbolic 전체 CPU는 UNKNOWN_NOT_ZERO다.
따라서 end_to_end_cpu_cap_established=false이며 완전한 전체 CPU합계를
주장하지 않는다. 이전 ledger의 실패·unknown과 사용된 reserve는 그대로다.

Root의 Wolfram evaluator1회는 toolwall8.504초, body CPU0.102054초와
wall0.102377초다. Context1회는 별도 계측하지 않았으며 exec wall19.9초를
관찰했다. Helium으로 잘못 확장된 context query와 No Results는 NOT_ADOPTED다.
채택한 primary source와 explicit evaluator algebra는 H1s를 사용한다.
전체 remote CPU는 UNKNOWN_NOT_ZERO를 유지하고 추가 호출하지 않았다.

## Backup·review·publication 상태

B1은 178,668 bytes,54members, SHA256
`5c166c53609fd1c8b6b0af6059ea3e205bd50e5a69de613d845bec3b98d7cdcd`다.
Drive10bExiGPtKflSI2cJy2vb06d5eaYhN2T3와 Dropbox
id:BSpOijBcT10AAAAAAD_9RQ의 실제 dual upload와 metadata size readback을
확인한 뒤 root GO로 실행했다. B1은 재생성하지 않았다. 실제 receipt는
`delivery/B1_BACKUP_ACK.json`이다. SciSpace의 실제 query와10개 citation
metadata만 evidence/SCISPACE_INTAKE.json으로 연결하고 abstract/fulltext는 제외했다.

현재 R1–R10/C1–C9의19단계가 완료됐고 C10 actual publication/delivery는
pending이다. 최종 수용은 CLAIM_GATE와 SCIENCE_DECISION_KO에 연결하며
actual source_analysis.json의 당시 PENDING_C9 status는 그대로 보존한다.
Source PDFs/fulltexts/page images와 archive payload는 공개 경로에 넣지 않았다.
부모 HE-ANG은 SOURCE_INPUT_PENDING, physical_provider_admitted=false다.
새 full joint law, spin/amplitude/count/support/frame/recoil/uncertainty 의무,
C9-NB-01, C23E 및 다른 owner의 scoped result/OPEN 상태를 유지한다.
