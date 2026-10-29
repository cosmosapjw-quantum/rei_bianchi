# 조건부 17상태 진화와 비교·수치 진단 figure set

2026-10-29 KST. 이번 목표는 이미 계산된 OFF_base·ON_base·ON_refined의 17상태 진화, ON/OFF 효과, refinement, 초기 transient와 보존 잔차를 외부 보고서용 그림으로 전달하는 것이다. 사용자가 지정한 physmath-research-loop 내장1.0.0의 이론·코딩 루프를 적용했다. ON_refined를 기본으로 유지하고 기존 IVP와 clock 적분을 재실행하지 않았다. 원자료·유효한 기존 결과를 재사용하며, 새로운 유한 offline 진단과 표시만 수행했다.

기준 PR251 HEAD `c5ab42c8673db614e7fb16695ad071c65becb81b`, 새 실행 전 checkpoint `81721528c4a40b90aa38fd65a29f032dcf9c5f41`이다. 현재 scientific/visual 채택은 `review/REVIEW.json`, 게시·백업은 최종 delivery receipt를 기준으로 읽는다. 첫 그림의 가독성 지적과 표적 수정은 원본을 보존하고 기록한다.

## 실제로 해소한 의무

| 의무 | 실제 결과 | 적용 범위 |
|---|---|---|
| 원시 배열과 clock 연결 | 3 case의 공통361시각, CSV/NPZ population 일치, 저장 eta–t 대응 및 tick 역변환 확인 | source turn-on 이후 proper elapsed time |
| ON/OFF 해석 | ON_base−OFF_base와 ON_refined−OFF_base를 별도 저장 | source와 escape를 함께 바꾸는 설정 효과 |
| refinement | 최대 isotope-normalized 차이 9.475629213×10⁻⁸, 원 기준10⁻⁵ 통과 | 저장점에서의 두 정밀도 비교 |
| 열린계 수지 | 빠른 n/T·hidden Li6·외부 ledger 포함 재계산이 저장 잔차와 정확히 일치 | baryon 및 heavy-charge/electron ledger |
| n/T 평탄화 | 공급·손실 및 빠른 저장고 분기비로 sampled quasi-stationarity 판별 | 한 수명에서 완전평형이라는 해석 교정 |
| Li I 떨림 | 양쪽 ON 정밀도의9개 극값 재현, 최대 상대차1.2278×10⁻⁴ | scalar atol 원인설명의 전제가 실제 코드와 다름 |
| 후기 중성종 V | 실제 첫 bath knot와 희소 표본, 그 점의 양의 RHS 확인 | 정확한 연속 최소점·불연속성·인과 원인은 별도 구별 |
| 보고서용 표시 | 전체17, 함량별5그룹, ON/OFF·refinement·transient·수지 그림 | raw 값 보존, 축 배율·표시 범위와 제외 수 명시 |

## 시간축과 초기조건

아래축은 `t(Myr)=elapsed_proper_s/31557600000000`이고, 위축은 저장된 `eta=ln(a/a0)`에서 `z_mean=21 exp(-eta)-1`을 계산한다. z tick의 위치는 실제 저장된 eta(t)를 역으로 보간한다. z를 시간에 선형으로 보간하거나 별도 ΛCDM cosmic-age 관계를 대입하지 않았다. t=0은 광원 켜짐 z=20이며, 종점은 `9.742841241346858e16 s`와 z=2다. 절대 우주 나이의 원점은 공급되지 않았다.

초기 n/T transient 동안 z는 그림 정밀도에서 거의20이다. 해당 그림의 위축에는 이 사실을 적고, 구별되지 않는 z 눈금을 인위적으로 벌리지 않는다. 실제 초기 bath는 기존300 K이며, 이전8 K 후보는 이 실행에 적용되지 않았다. 17개 표시 상태에 Li IV가 포함되고, fast stocks·에너지·경계 ledger는 진단용 보조좌표로 별도 취급한다.

## 물리·수치 해석에서 바뀐 결론

열적 중성자와 삼중수소 합의 식은 각각 `n'=P_n−L_n n`, `X'=P_T−L_T X`, `X=T I+T II`다. P에는 직접 공급과 빠른 저장고의 slowing이 들어간다. n에는 capture도 포함되고 T 전하교환은 X의 식에서 상쇄된다. `P/L`과 현재 저장량을 비교한 정상성·추적 두 조건을 함께 사용했다.

동결된 n 베타 평균수명은878.4 s, T 평균수명은5.6052868×10⁸ s다. 1% 조건을 이후 모든 저장점에서 만족하는 첫 저장시각은 n에서4,142.168 s, 열적 T 합에서3.442953888×10⁹ s였다. 이는 연속시간 전체의 인증이나 정확한 최초 진입시각이 아니다. 일정 공급·초기량0인 단일 저장고조차 한 평균수명에서는 정상값의63.2%에 도달한다. OFF의0/0 추적비는 미정의로 남겼다.

현재 Radau 적분변수는 `x_i=y_i/scale_i`다. 물리변수의 국소 오차 가중치는 `atol*scale_i+rtol*abs(y_i)`이며 base/refined의 scaled atol은 각각10⁻¹¹,2×10⁻¹²다. 늦은 Li I 저장량 약10⁻¹⁵에 비해 base 가중치는 약5×10⁻²¹이다. 따라서 원시 scalar atol≈10⁻¹⁵ 때문이라는 조언은 이 구현을 설명하지 않는다. 공식 Radau 문서는 국소 오차 추정의 제어를 설명하며 궤적의 smoothness나 전역 상대오차를 보장하지 않는다: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.Radau.html .

Li I의9개 극값이 두 정밀도에서 모두 남는다는 사실은 이 tolerance 변경에 대한 재현성이다. 같은 bath와 저장격자에서 생기는 표현오차도 공유할 수 있으므로 물리적 진동의 증명으로 확대하지 않는다. 원래 isotope-normalized 기준과 희귀 이온의 상대차이를 나란히 보고하고 기준을 바꾸어 PASS를 만들지 않았다.

H I·D I·³He I·⁴He I의 저장 최소는 첫 bath knot `8.0325473529e13 s`에 놓인다. 그 점에서 H I RHS는 이미 양수이므로 해가 회복 중이다. 실제 hazards는 연속 piecewise-linear이고 도함수만 바뀐다. 희소한 저장점을 직선으로 이으면 날카로운 V가 보일 수 있다. 표본을 추가하거나 knot에서 재시작하면 해결된다는 주장은 이번 근거로 확정하지 않았다. 자세한 식·수치·소스 범위는 `theory/PHYSICAL_FINDINGS_KO.md`에 보존했다.

## 세 연구 축

| 축 | 이번 의미 | 별도 남은 의무 |
|---|---|---|
| 대칭성·게이지 | proper elapsed time, 평균 a·z와 normal frame의 국소 population; Bianchi 공간 주축과 연구 분류의 세 축은 별개 | 관측 방향별 redshift·radiation과 shear의 통제된 연결 |
| 불변량·수지 | baryon inventory+외부 ledger, heavy charge−electron ledger; slowing의 retained-total 상쇄 | 자기일관적인 광자·열·Einstein 에너지 전달 |
| 실제 관측가능량 | 이 모형의 종별 수 함량과 설정별 차이·수치 진단 | 선흡수/방출·광학깊이 및 관측 likelihood로의 물리 전달 |

ON baryon inventory가1.32808에서1.20572로 줄어드는 것은 열린계 ledger와 함께 읽는다. 이것을 보존 실패로 표시하지 않는다. 가장 큰 세-case baryon 잔차1.3041×10⁻¹²와 charge 잔차6.5361×10⁻¹³는 원 기준1.0820×10⁻⁸ 안에 있다. 별도 Bianchi 해석 helper를 화학 민감도 궤적으로 섞지 않았다.

## 최신 조사와 원래 DAG

접근 가능한51개 GitHub repo의2,462 branch refs를67개 terminal page로 확인했다. 이전 목록 대비39개 변경/new ref의 이력에서236개 최근 unique commit과8개 repo의32개 갱신 PR을 확인했다. REI252–258의 조건부 slope/EOS/Jeans 분석과 해당 미완료 독립 검토, RR250·DR247의 최신 실행 상태, 관련 BASS/REC/CR/WU/HE/VigilODE의 실제 적용 범위를 취합했다. source와 담당자의 예약·예산은 서로 이전하지 않았다.

Library 최신3페이지의417 file metadata를 이전 cutoff까지 조사하고 새 handoff/report/stage 문서5개를 읽었다. Personal Context는 unavailable을 반환해 다른 비공개 대화 전부를 읽었다고 주장하지 않는다. Dropbox의 네 scoped root는13페이지에서 cursor를 소진했다. Drive dossier는1,000개 cap이므로 전체 역사 archive 완전성은 미확인이다. 자세한 범위는 `intake/CURATED_INTAKE_REPORT.md`에 있다. 사용자가 폐기한13개 첨부는 이번 의존성에서 제외했다.

원본88-node DAG는 중앙 HEAD `4824eec8526185b6b866a5e7e0dabdc624b5543c`의 exact blob `83280906f45287b183fdbea4ede4d1fcfacc5770`으로 확인했다. **working33/88, central28/88, physical fast4/7**을 유지한다. 이 figure set은 유효한 유한모형 산출물이며, source-qualified full feedback을 요구하는 REI-L4나 그 후속 관측 gate 전체를 완료하지 않는다. 세부 그림이나 검증 항목을 원본 노드로 더하지 않았다.

## 10단계 이론·코딩 근거와 보존

각 행은 이번 고정된 figure-set 단위의 대응이며 원래 전체 DAG의 추가 노드가 아니다. 실제 최종 review 상태와 delivery 완료는 해당 영수증을 따른다.

| 단계 | 이론 R | 코딩 C | 전체 working / physical fast |
|---|---|---|---|
| 1 | 조건부 figure set·범위 고정 | PR251 baseline·원자료 보존 | 33/88 · 4/7 |
| 2 | 최신 source·기존 식 재사용 | CSV/NPZ·clock·모델 대응 | 33/88 · 4/7 |
| 3 | 관측/모형·t/z·오차 범위 정렬 | signed/zero·scaled tolerance 설계 | 33/88 · 4/7 |
| 4 | n/T·Li·knot의 판별량 선택 | 병렬 DAG·누적 예산·한정 job | 33/88 · 4/7 |
| 5 | 공급–손실·ledger·clock 유도 | diagnostic·vector figure 구현 | 33/88 · 4/7 |
| 6 | 다른 작성자의 수식·근거 확인 | 4개 표적 검사와 실제 자료 검사 | 33/88 · 4/7 |
| 7 | 실제361시각 진단 | frozen RHS·수지·refinement 검사 | 33/88 · 4/7 |
| 8 | 조언의 전제·인과 주장 교정 | raw 보존·수치 조건·환경 실패 분리 | 33/88 · 4/7 |
| 9 | 물리 해석·figure caption | 독립 시각검토와 한정 표시 수정 | 33/88 · 4/7 |
| 10 | 다음 통제 비교 조건·handoff | 과학·10/10 시각검토 완료; 현재 게시 진행은 DELIVERY_RECEIPT.json | 33/88 · 4/7 |

실행 전 CHECKPOINT와 BUDGET_AUTHORIZATION은 Git에 정확히 보존했다. main 진단은1회 exit0, 관측 CPU1.116230 s, IVP0이다. 첫 render의 `/usr/bin/time` 부재는 child 실행 전 환경 실패로 보존하고 한 번의 launcher 수정 후 실제 render를 수행했다. 독립 시각검토의 라벨·범위 지적에 대해 표적 표시 수정을 수행했고 첫 그림과 비용을 보존했다. 수정된 개별 PDF/SVG 10개씩과 통합 PDF는 완성되었다. 이전 표적 repair는 CPU 한도에서 FAILED_PARTIAL_RASTER로 종료되어 당시 수정 PNG3/10페이지만 확인되었다. 이후 사용자가 presentation 누적상한65→66 CPU s를 명시 승인했고, 동일한 통합 PDF의4–10페이지를72dpi로 한 번 raster화했다. 이 작업은 exit0, 관측 CPU0.317124 s로 완료되었으며 새 IVP·물리 표본·벡터 재생성은 각각0이다. 독립 검토가 전체10/10페이지의 최종 시각 QA를 PASS_SCOPED로 닫았다. review/VISUAL_COMPLETION_REVIEW.json 및 .md가 이번 완료의 근거이며, 기존 review/REVIEW.json은 이를 현재 상태에 반영한다. 그림의 가독성과 저장 이력 조건부 모형 범위에서 전달 준비가 완료되었다. 원래 물리 노드의 완료 수는 유지한다.

다음 통제 비교에서는 초기·경계 복사·열 조건, 미시적 반응 법칙, 평균팽창 이력과 수치 기준을 공통으로 고정하고 초기 전단만 바꾸되, 명시된 기하–복사·열 결합에 의해 진화하는 방향별 스펙트럼과 그로부터 계산되는 반응률은 달라질 수 있도록 한다. 현재 소스 이력으로 anisotropy 효과를 분리했다고 주장하거나 전체 자기일관적 예측의 날짜를 제시하지 않는다.

초기 transient 그림은 n·T I·T II만 보여주며, 그룹 그림에서 범위 밖인 초기 He/Li 양수 표본 모두를 회복하지 않는다. 해당 값은 원시 CSV와 plot_data.json에 남아 있다.

현재 과학·시각 상태: 저장 이력 진단과 조건부 모형 해석은 기존 PASS_SCOPED를 유지하며 최종10/10 시각 QA도 PASS_SCOPED다. presentation 누적65.980312494 CPU s는 새1.0 s 예약 전체를 보수적으로 유지한 값이며 원래600/30/10 상한을 복원했다. main608.750604, planning20.819461885와 이전 비용·알 수 없는 host/tool/transport 비용을 유지했다. 이전99dd121 Git 상태의3/10 QA 및 백업 영수증은 이력이다. 현재 PR259·새 완성본 ZIP의 provider 게시 진행과 ACK는 별도 DELIVERY_RECEIPT.json을 따른다. 범위는 저장된 조건부 모형의 그림·진단이며 원래 전체 물리 DAG의 완료 수를 늘리지 않는다.
