# 17상태 기준 그림과 n/T 생성·붕괴 연구 결과

Li IV를 포함한 **17상태 기준 time-evolution 그림**과 **실제 저장된 n/T 생성·붕괴 이력의 보조 그림**을 생성했다. 각각 독립 검토를 통과했다. 두 그림은 서로 다른 배경·모형의 저장 결과를 사용하므로 별도 패널 세트로 제시한다. 기존 IVP·율 적분·완료 campaign은 재실행하지 않았다.

## 그림과 검증

| 산출물 | 실제 입력과 결과 | 검토 |
|---|---|---|
| `outputs/grid044_M4_nominal_selected17.png` | ANGTHERM01 201시점, mean z=20→2. 17상태 모두 표시, Li6 내부 closure 보존 | PASS_SCOPED_EXECUTED_SAVED_HISTORY_PROJECTION_AND_FIGURE |
| `nt_extension/outputs/nt_saved_projection.png` | 원래 82×257 핵반응 결과 중 명시한 case0의 257시점. T/n stock과 두 누적 β사건 표시 | PASS_SCOPED_EXECUTED_CONDITIONAL_NT_HISTORY_AND_FIGURE |

기준 그림의 검사3개와 n/T 검사3개가 통과했다. n/T C2 표본의 시간·stock 9개 대조는 모두 정확히 일치했다. 기준 그림의 전체21상태 baryon reference는1.32808000350006/Href, 최대 baryon drift는1.9984014443252818e−15/Href였다. 이 값은 저장 결과 추출의 수지 검사이며 새로운 연속체 수렴 시험이 아니다.

n/T 첫 그림의 title 잘림을 발견해 constrained-layout 높이만 한 번 고쳤다. 원래 PNG와 실행 기록은 `nt_extension/outputs/before_title_fix/` 및 별도 PLOT/REPAIR receipt에 보존했다. 데이터 추출·검사는 반복하지 않았다. 두 최종 그림은 pilot 검토용이며 저널의 특정 단·인쇄 크기에 대한 최종 조판 승인을 뜻하지 않는다.

## n/T의 물리적 의미

기준 ANGTHERM01 atomic-only case의 n/T는 source조건상0이다. 새로 회수한 기존 핵반응 모형은 **완전 이온화된 핵, 즉시 열화, 고정 배경 핵종량**을 가정하며 DD 분기·전환·포획·붕괴로 n/T를0에서 생성한다. 같은 표본의 끝 시점은 elapsed proper time9.74270001421817e16s이며,

- log10(Y_T)=−103.85577102750815,
- log10(Y_n)=−109.6589700782797,
- 누적 n β붕괴 사건의 log10값≈−95.40049928 events/baryon,
- 누적 T β붕괴 사건의 log10값≈−95.40220574 events/baryon이다.

이는 해당 조건부 DD 및 포획율 모형의 결과다. 실제 IGM의 cosmic-ray/고에너지 광자 source를 공급한 예측은 아니다. 작은 값은 임의 floor로 표시하지 않고 원본 자연로그를 log10으로 변환했다. 초기의 정확한0과, 매우 작지만 유한한 양수를 구별했다.

**양성자 공급:** B_n=∫λ_nY_n dt만큼 중성자 β붕괴가 H II와 전자를 각각 생성한다. 그림의 아래 패널은 이 누적 생성 기여를 보여 준다. H I는 후속 재결합을 거쳐야 한다. T I/T II의 딸 이온은 spectator-electron 근사에서 각각³He II/III다. 누적 β사건을 전체 p/³He abundance로 바꾸거나, 거의 상쇄되는 생성−소멸 사건 차를 n/T stock으로 대체하지 않았다.

**생성·포획·붕괴:** 배경 핵종량을 고정하면 u=(Y_T,Y_n)는 du/dt=M(t)u+s(t)의 결합 선형계를 이룬다. Metzler 행렬의 지수와 양의 endpoint-source 가중치로 원래 구간 해의 양성을 유도했다. n 포획과 붕괴의 경쟁은 k_capture/λ_n 및 환경에 의존한다. 장시간 잔존량은 지속 생성과 손실의 균형을 요구한다. BBN 때의 초기 자유 n/T를 late-time 상수 잔류량으로 둘 수 없다.

**역약반응:** 고에너지 lepton 분포가 공급되면 p+e−→n+νₑ 또는 p+ν̅ₑ→n+e+를 계산할 수 있다. 정지 자유 양성자 기준 문턱은 각각 대략0.783MeV의 전자 운동에너지와1.806MeV의 반중성미자 에너지다. 문턱은 반응률을 정하지 않는다. 회수한 source의5–60eV 광자는 MeV 광핵 문턱에 미달하며, CR113의 현재 원자 전자 입력도 핵반응 source를 제공하지 않는다.

## 세 축

| 축 | 이번에 확보한 연결 |
|---|---|
| 대칭성·게이지 | source의 정상 tetrad, proper-time·부피·baryon 정규화를 유지. η와 proper seconds를 혼용하지 않음. mean z와 관측 방향별 redshift 구별 |
| 불변량 | 각 핵반응의 baryon/charge 보존, β전자 공급, 양성 보존 구간 해. photon·fast electron·neutrino·열의 에너지 소유권을 분리하며 Q 전부를 열로 넣지 않음 |
| 관측가능량 | 기준 그림은 이온 population; 보조 그림은 동일 핵반응 case의 n/T stock과 누적 β사건. 별도 ion partition·전방 관측모형이 필요한 부분은 유지 |

이론·문헌 근거 및 실제 Wolfram 기호 검산은 `nt_extension/theory/NT_THEORY_AND_SOURCE_DECISION.md`와 원본 도구 기록에 있다. SciSpace·Exa 원전 검토를 사용했으며 scalar/2×2 문제에 xAct는 필요하지 않았다. 실제 n/T ion 분기·감속/탈출·에너지 침적은 기존 공급자 범위에 없으므로 새로 만들어 넣지 않았다.

## DAG 및 다음 의무

원래 DAG **작업33/88, 중앙28/88, 이번 원본 증가0**. 빠른 경로는 F0 source/범위, F1 회수, F2 검사, F3 기준 그림·검토·게시까지 **4/7**이다. F3의 실제 게시 근거는 최종 delivery receipt를 따른다. n/T 조건부 생성 그림은 F4의 재사용 근거를 확보했지만, F4의 물리 source/수송/charge coupling 완료를 뜻하지 않는다.

가장 짧은 남은 경로는 (1) 동일 배경에 대응하는 비열적 n/T 생성·감속·탈출 입력, (2) 딸핵의 charge branching 및 전자/광자/열 분배를 결속하고, (3) 그 유한 계약에 맞춘17상태 결합 이력을 계산·검토하는 것이다. 기존 n/T isotope-total 이력을 ANGTHERM01 TI/TII로 임의 분배해 붙이지 않는다. 두 source의 실제 입력과 계산은 다음 노드에 재사용할 수 있게 보존했다.

## 실행·비용·저장

| 단계 | 자식 CPU s | 관측 wrapper CPU s |
|---|---:|---:|
| 기준 검사 |0.117719|0.002448|
| 기준 그림 |1.003654|0.001715|
| n/T 검사·추출 |0.336434|0.001764|
| n/T 첫 그림 |0.701622|0.001114|
| n/T 조판 교정 |0.723463|0.001408|

새 관측 자식+wrapper 합은2.891341 CPU s다. 누적 known+reserve charge는 planning17.295332885, presentation54.561494494로 기록했다. 승인 임시 상한18/55를 닫고 원래10/30으로 복귀했다. main595.225063/600과 NO_MORE_IVPs는 그대로다. 과거·현재 미계측 overhead는UNKNOWN_NOT_ZERO로 보존했으며 전체 세션 CPU를 정확히 측정했다는 주장은 하지 않는다.

PR243에 additive 결과를 게시하고 그림·CSV·code·review·원본 복구 위치를 포함한 새로운 JSON backup을 두 기존 provider에 저장한다. 실제 최종 SHA·provider ACK·크기는 `RUN_DELIVERY_RECEIPT.json`에서 확인한다. 이전 준비 snapshot·실패·source archive는 그대로 보존한다.
