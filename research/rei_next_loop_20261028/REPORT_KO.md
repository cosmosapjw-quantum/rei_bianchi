# 2026-10-28 REI 연구 루프

현재 원본 전체 DAG는 작업 브랜치 **33/88**, 중앙 통합 브랜치 **28/88**이다. 이번 작업에서 원본 노드 완료 증가분은 0이다. 기존 finite_thermal_endpoint_20261028의 남은 R7–R10/C10은 보존된 계산과 교정된 독립 검토를 재사용해 종료한다. 다음 supplied-caloric-branch 단위도 유도·구현·첫 실행·독립 검토를 완료했다. 실제 recipient EOS와 전체 physical pilot은 입력 의무로 남아 있다.

## 최신 근거 종합

접근 가능한 51개 저장소의 현재 브랜치 2,397개와 고유 head 2,328개를 조사했다. 핵심 7개 저장소는 1,441개 브랜치, 고유 head 1,414개, 기준 2026-10-26T23:43:49Z 이후 commit 627개와 갱신 PR59개를 포함한다. 나머지44개 저장소는956개 브랜치,고유 head914개,최근commit32개와PR4개다. 목록 pagination을 완료했다. Tip commit 시각은 branch 생성·push 시각과 다르며 삭제된 ref와 비공개 대화 전체는 이 조사로 복원되지 않는다.

개인 대화 검색은 unavailable이었다. 공유 작업공간에서 실제 native 독립 검토 반환과 correction 실행 영수증을 찾아 직접 읽었다. 그 반환은 Git PR 설명보다 최신이며, 과거의 독립 검토 대기를 해소한다. Drive/Dropbox의 해당 REI 폴더에서는 기준일 이후 파일127개씩(각ZIP68개)을 이름·크기로 대조했다. 이는 원격 바이트 전수 SHA 검사가 아니다. 기존 archive를 재생성하지 않았다.

중앙7937ed4a842eb1ef6cec562a4224fb0add63d0d6과 작업b77c7b8d45c48a7e4722e733309430d5ba668b0d의 원본88 IDs,17edges,과거40계약 및 각노드 contract/dependencies/conditional_dependencies/claim_gate가 동일함을 확인했다. 기존 5개의 추가 작업측 완료 상태와 부분 관측이 중앙과 다르며, 이번에는 원본 gate나 canonical DAG를 수정하지 않는다.

PR237의 조건부 thermal join118검사는 이미 완료돼 재사용한다. PR239의 CR consumer, PR240의 finite-cohort/affine/BASS atomic storage, PR241의 V8 결과도 별도 범위를 유지한다. CR113과 BASS의 별도 진행중 리뷰·담당자 예약을 점유하지 않는다. 관련없는 저장소의 변경을 과학 gate 근거로 사용하지 않는다.

원래 WORK_THREAD_PROMPT_KO.md의 처방된 비등방 DM 배경·방향 광자·선택21종·현상론적 emissivity 목표를 유지한다. 이후 사용자의 n/T 및 역베타 검토 지시도 유지하며, 초기 문서의 n/T absent 기본값을 물리적 부재 결론으로 승격하지 않는다. 이번 단위는 새 n/T 생성률이나 source-matched history를 공급하지 않는다.

## 완료한 기존 연구 연결

보존된 native R6/C9가 F1 표현식 교정을 요구했고, 실제로 교정식과 한 번의 exact regression이 수행됐다. 이를 보존·재사용했다. 별도 저장값에는
delta_theta = theta_a - k_src T_native
가 남으므로 T_a^E/T_native의 상수비 식에는 delta_theta EV_src/(k_B T_native) 항이 들어간다. 원래 구현은 이미 이 잔차를 보존했으며 source 값을 바꿀 필요가 없었다.

R7은 C7의 실제 저장 source와 두 C8 근거를 판별 근거로 채택한다. 두 C8의81/158 표시는 같은 단계의 다른 검사 집합이며 합산해 새 단계나 물리 데이터로 세지 않는다. R8은 교정된 표현 source-caloric 진단만 채택하고, R9은 prescribed driver/source endpoint/actual recipient 온도를 구분한다. R10/C10은 재현 위치·남은 입력·예산을 인계한다. 자세한 근거와 식은 theory/FINITE_THERMAL_CLOSURE.md 및 reused_native_review/에 있다.

## 새 유도와 구현

선택한 다음 작업은 기존 R5§7에서 이론으로 남아 있던 caloric EOS 역변환의 유한 구현이다. 공급된 엄격 단조 구간별 선형 F0(T), 최소 기울기 m0>0, 에너지 구간[Elo,Ehi], EOS의 균일 오차 상한 eta에 대해
T_* in [F0^{-1}(Elo-eta), F0^{-1}(Ehi+eta)]
를 구성했다. 임의 기준점에서
|T_*-Tbar| <= (|F0(Tbar)-Ebar|+eE+eta)/m0
를 유도했다. 구간 포함·연속성·실제 EOS의 엄격 단조 가정은 theory/THEORY.md에 명시했다. 새 no-go나 문헌 최초성 주장은 없다.

Fraction을 이용한 정확한 유리수 역변환·오차구간·잔차 상한 코드와 독립 기대값 검사, 기존 C7 source의 실제 저장 E/D/cv/T를 읽는 calibration runner를 준비했다. 과거 이상기체 나눗셈을 재실행하지 않고 새 adapter 경로와 비교할 계약이다. 사용자의 예산 증액 승인 뒤 단 한 번의 bounded 실행에서 6개 검사 모두 통과했고, actual saved-source의 역변환 값이 독립 E/(cv D) 및 저장 T와 정확히 일치했다. 독립 검토는 PASS_SCOPED_EXECUTED_REPRESENTED_BRANCH다. 입력 source는 재생성하지 않았다.

| 물리 축 | 의미 |
|---|---|
| 대칭성·게이지 | 같은 reference-volume/energy 단위와 일관된 에너지 영점 변화에서 온도 결과 불변. 새로운 시공간 gauge 또는 Einstein 동역학을 추가하지 않는다. |
| 불변량 | thermal/atomic/radiation/fast-electron 에너지 소유권을 분리하고, 동일 에너지 변환을 EOS와 target 모두에 적용한다. |
| 실제 관측 연결 | 계산 대상은 공급된 caloric slice의 온도구간이다. 실제 REI recipient EOS·상태·물리 오차가 없으므로 실제 온도 갱신과 physical interval은 null이다. |

SciSpace/Exa 원전 탐색은 단조 caloric interpolation과 전체 열역학적 일관성의 구분에 사용했다. Wolfram 대수 출력 및 경고는 theory/SELECTED_TOOL_EVIDENCE.json에 기록했다. 증명은 본문의 구간별 합·순서·삼각부등식에 근거한다. xAct가 필요한 tensor 연산은 이번 단위에 없다.

## 단계·게시·백업

| 구간 | 연구 상태 | 원본 DAG | 전달 상태 |
|---|---|---|---|
| R1–R2/C1 | 최신 source·예약·예산 조사 완료 | 33/88 | intake 원문 보존; 최종 receipt 참조 |
| 기존 R6/C9 | 실제 native 교정 검토 재사용 | 33/88 | 원문 반환·교정 raw 보존 |
| 기존 R7–R10/C10 | 범위 한정 연구 내용20/20 종료 | 33/88 | 새 종료 기록의 게시/백업은 FINAL_DELIVERY_RECEIPT 참조 |
| 새 R1–R6/C1–C5 | 유도·코드 구현 및 독립 정적 검토 완료 | 33/88 | 검토한 source와 사전 계약 보존 |
| 새 R7/C6–C9 | 첫 실행 통과, 원출력 독립 검토 완료 | 33/88 | 실행 raw·자원 정정 기록 보존 |
| 새 R8–R10/C10 | 범위 한정 채택·재현 인계 완료 | 33/88 | draft 게시·백업의 실제 결과는 최종 receipt 참조 |

현재 단위 최종 commit, provider ACK 및 미완료 전달 항목은 별도 FINAL_DELIVERY_RECEIPT.json에 기록한다. 원본 계산·그림·실패·닫힌 allocation은 재실행하지 않는다.

## 예산과 다음 실행

과거 planning 부분 하한16.323598885 CPU s와 이미 별도 승인·종료된 F1 child0.026759 CPU s를 한 번씩 계상하면 알려진 하한은16.350357885 CPU s다. Presentation 하한48.263016494 CPU s, main595.225063/600 NO_MORE_IVPs를 유지한다. 이전16/47 ceiling 및 닫힌 할당을 새 실행에 사용하지 않는다. 이번 읽기·작성·전송과 미측정 비용은UNKNOWN_NOT_ZERO이며 전체CPU의 정확한 합이나 전역 budget PASS를 주장하지 않는다.

사용자가 2026-10-28 예산 증액을 승인한 뒤 planning 임시 절대한도18 CPU s, 실행 예약1.5 CPU s를 동결했다. 첫 실행의 outer wait4 CPU0.113551에는 내부 worker0.062480이 이미 포함돼 있다. Observer 자체0.023059를 더한 관측 pre-receipt CPU는0.136610이다. 초기에 nested worker를 다시 더한 raw accounting field를 삭제하지 않고 ACCOUNTING_CORRECTION.json으로 정정했다. 재실행0회다.

이 측정 증가를 더한 알려진 하한은16.486967885 CPU s이고, 명시적 final-tail reserve0.1을 포함한 charged ledger는16.586967885 CPU s다. 두 숫자를 전체 실측 비용으로 동일시하지 않는다. Planning 일시 cap18은 종료하고 원래 cap10으로 복귀했다. 누적 비용은 유지한다.

Presentation은 이번 결과 그림과 새 단위 묶음에 한해 임시 cap52 CPU s, 예약3.5 CPU s를 승인 범위로 기록했다. 실제 완료 비용과 원래 cap30 복귀는 delivery resource receipt 및 FINAL_DELIVERY_RECEIPT.json에 적는다. 과거 final ZIP cap60/reservation8 제안의116파일 재포장은 수행하지 않는다.

사전 계약·이론·test docstring의 NOT_RUN은 작성 시점 기록으로 보존했다. 현재 판정은 ADMISSION.json과 원출력 및 독립 검토에 있다. source-matched physical history, 실제 recipient bath/EOS, stopping 및 전체 pilot gate는 남아 있다.

