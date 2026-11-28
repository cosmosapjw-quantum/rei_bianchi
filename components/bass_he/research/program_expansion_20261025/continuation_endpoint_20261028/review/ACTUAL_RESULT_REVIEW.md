# ENDPOINT14 실제 결과 비저자 심사

**결정: PASS_SCOPED. 과학·실행 blocking 0건.** 고정된 endpoint-zero sextic 증인과 명시된 전체 모델 가족의 aperture reference를 수용할 근거가 갖춰졌다. 실제 결과 심사는 기존 실행 전 심사의 연속이며 추가 science를 실행하지 않았다.

## 실행과 입력

실행 pin은 source `501f4c5a5e5b14b0e05ff5d504578b5b9218caf7`, tree `54bbaf71c917c67f3c5d3b9dcda44e3eecb740c4`이다. 보존된 S05 실제 ref·commit readback에서 부모와 tree를 확인했고, 9개 source 파일·2개 immutable 입력의 현재 hash가 pin과 일치했다. S05 source 스냅샷의 9개 hash도 일치한다. START, saved certificate와 PREEXEC_REVIEW의 여섯 Python hash는 동일하다.

새 primary construction 1회, **8 PASS + 0 FAIL**, reader PASS다. Reader는 6개 polytope의 26개 정점 기록과 24,690개 exhausted bases를 확인했으며 enumeration/search/producer import는 없다. Producer·reader의 같은 구현 저자와 비저자의 과학 판단을 구별한다. 전체 정점 목록의 완전성은 유계 polytope 정리 및 심사한 exhaustive producer loop와 실행 counts에 함께 의존한다.

| N | Inner 정점 | Outer 정점 | Inner bases | Outer bases |
|---:|---:|---:|---:|---:|
| 1 | 6 | 4 | 680 | 560 |
| 4 | 4 | 4 | 1771 | 969 |
| 16 | 4 | 4 | 16215 | 4495 |

총 26은 **14 inner + 12 outer의 case별 기록 합**이다. 여섯 case 전체에서 서로 다른 정점이 26개라는 뜻은 아니다. N4와 N16의 각 inner/outer 정점 목록은 실제로 동일하다. 네 nesting 검사는 모두 PASS이고, 여섯 polytope 모두 nonempty다. 저장된 모든 quadratic minimum은 양수다.

## 고정 증인의 실제 성공

사전 고정한 a=(1411/10000,-1/4,33/25)는 바뀌지 않았다. 별도 CANDIDATE_OUTCOME와 certificate가 일치하며, r의 최소값은 **170627/1320000 > 0**, 위치는 z=25/264, D=14297/52500이다. f는 열린 각도 구간에서 양수이고 양끝에서 정확히 0이다.

네 실제 nominal 데이터 창이 exact interval로 모두 통과했다. 저장된 enclosure를 표시용으로 변환한 값은 46도 약 0.1696359137194086, 61도 약 0.1187691275310318, 73도 약 0.1183158557170647, 87도 약 0.1400405082938579 nb/sr이다. 수용 판단은 반올림값이 아닌 저장된 유리수 enclosure에 근거한다.

이전 동일 endpoint/data 조건의 quartic certificate는 inner·outer 정점이 모두 0인 EMPTY_OUTER로 보존된다. 따라서 차수를 4에서 6으로 늘렸을 때 feasibility가 달라지는 구성적 증거가 생겼다. 이전 배제는 원래 차수와 cone 범위에서 유지된다.

## Aperture 결과

검토한 monotone lab-map 증명과 실제 K<0, CAS의 H>0가 same-event 두 꼬리 구간의 형태를 뒷받침한다. Saved zeroth moment에서 복원한 threshold의 기존 j=0,1,2 monomial bounds는 두 geometry에서 모두 exact equality/overlap을 통과했다. 이 호환성 비교를 geometry 증명의 대체로 사용하지 않았다.

N4·N16의 바깥 방향 12자리 표시는 다음과 같다.

| Geometry | 전체 허용 범위의 enclosure | 최소값 bracket | 최대값 bracket |
|---|---|---|---|
| HEMISPHERES | [0.747050288674, 0.783542448014] | [0.747050288674, 0.747050288675] | [0.783542448013, 0.783542448014] |
| CAPS | [0.317079169073, 0.404464291607] | [0.317079169073, 0.317079169074] | [0.404464291606, 0.404464291607] |
| FULL | [1, 1] exact | [1, 1] exact | [1, 1] exact |

HEMISPHERES 최소·최대 exact bracket 폭의 표시값은 각각 7.696712203527597e-15, 4.381139846926824e-15다. CAPS는 각각 1.422475782906539e-14, 1.0097284931301006e-14다. N1 CAPS 최대 bracket 폭 0.012228846675262136도 그대로 보존한다. 작은 계산 bracket 폭, 허용 모델별 aperture 변화 범위, 실험 ERR-S의 결정론적 민감도 창은 서로 다른 양이다.

## CAS와 실제 그림

제출 코드를 읽고 실제 Wolfram 응답의 **14 literal zero + 16 True**, isError=false를 확인했다. 16개 True 중 2개는 단순 부호 smoke control이다. CAS는 제출된 algebra와 fixed witness·네 창을 검산했으며, polytope exhaustive enumeration이나 전체 물리 law를 따로 검증한 것으로 해석하지 않는다. Context documentation 응답과 evaluator 결과도 분리했다. 상세 범위는 CAS_REVIEW.json에 있다.

실제 PNG를 보았다. 고정 증인, 네 positive-mu 창, endpoint zeros, ordinary-scale aperture 범위가 올바르고 읽을 수 있다. 다만 오른쪽 위 legend가 N16 HEMISPHERES mark의 가장 오른쪽 부분을 조금 가린다. **Nonblocking 표시 한계**로 수용한다. 정확한 수치는 certificate와 표가 권위 자료이며, 같은 값의 N4 mark도 보인다. 성공한 plot 1회를 다시 렌더링할 이유는 없다. 상세 관찰은 PLOT_REVIEW.json에 기록했다.

## 비용과 다음 단계

Validation whole runner + waited children CPU는 **2.020525 s**, wall은 **1.9446278749965131 s**다. Plot은 CPU **1.635101 s**, wall **1.5717367499964894 s**다. 각각 고정 상한 안에서 exit 0, rerun 0으로 끝났다. 새 science repair는 0회다. Remote CAS CPU/wall은 제공되지 않아 null이며 위 local 측정에 포함하지 않는다.

세 physical input은 계속 open이다. Binding sole owner, null/off fields, 중앙 **28/88, HE delta 0**을 유지한다. 이 결과는 absolute event normalization, medium response, photon flux/history나 nonthermal/global species binding을 제공하지 않는다.

**PASS → 해석·최종 scoped 심사·S08–S10 게시와 백업·중앙 전달을 진행한다.** 완료된 science/test/CAS/plot을 재실행할 남은 필요가 없다. 심사자는 producer·reader·test·CAS·plot을 실행하지 않고 원시 결과와 코드를 읽었다.

