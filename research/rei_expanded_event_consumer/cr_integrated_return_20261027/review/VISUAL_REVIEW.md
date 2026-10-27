# 독립 시각 검토

판정: **PASS_SCOPED_FIGURE**. 검토자가 실제 PNG를 열어 두 panel, axes, units, markers, 범례, caption을 읽었다. Root의 별도 시각 검토와 독립적으로 판정했다. 이 그림은 저장된 source 대안과 실제 FD residual을 읽기 쉽게 보여 준다.

## 실제 그림에서 확인한 내용

- Panel(a)는 24개 integrated capture count를 m^-3 단위로 표시한다. 두 색은 chi1.5/3, 네 marker는 R/N 조합을 구별한다.
- X축은 세 discrete source z=2.316,2.479,2.649다. 점의 수평 offset은 readability를 위한 것이라고 축에 명시한다. 이 offset을 다른 source redshift로 해석할 이유가 없다.
- 각 점이 대안이라는 caption과 no sum/history/rate/spectrum/uncertainty band 설명이 보인다. 점을 잇는 시간 궤적이나 근거 없는 error band는 없다.
- Panel(b)는 24개 대안 각각의 두 step에 대해27행 중 maximum scaled FD residual을 표시한다. Filled/open marker의 step 구분과 원래2e-8 criterion이 읽힌다.
- Y축 residual은 무차원이며 caption이 saved row-unit normalization과 consumer b=1.4e6m^-3 fixture를 명시한다. 실제 단위량을 무차원1로 덮는 normalization을 뜻하지 않는다.
- 제목, 범례, 축 label, caption이 잘리지 않고 겹침 없이 읽힌다. 24개 source 대안의 의미와 두 FD step의 의미가 구별된다.

PLOT_INPUTS의 canonical event ID를 key로 OBSERVATIONS와 한 번 대조한다. 실제24 A 값,48 FD 값과 함께 저장된24 G 값이 동일해야 하며, CHECKS 전체의 반복 scan은 하지 않는다. 해당 metadata 비교의 결과와 image identity는 VISUAL_REVIEW.json에 기록한다.

## 자원 예외의 별도 판정

PLOT_RECEIPT는 renderer CPU4.972565719s, tail0.05s, charged5.022565719s, wall4.974030811s, RSS98772KiB를 기록한다. CPU cap4s를 초과했으므로 within_limits=false가 맞다. CPU 초과량은 measured 기준0.972565719s다.

이 receipt를 사후 PASS로 바꾸지 않는다. 저장한 figure의 scientific/visual validity와 renderer의 resource-limit 판정은 별개다. Figure는 읽을 수 있고 저장 data와 일치하므로 재렌더링을 요구하지 않는다. 원래 출력, receipt와 실패한 resource criterion을 모두 보존한다. 신규 scientific execution이나 provider/consumer/checker import는 없다.

## CRAG 적용

- Correctness: count와 FD의 값·단위·source 대안 해석이 실제 출력에 맞는다.
- Retrieval: retained capture를 thermal heat나 외부 escape로 바꾸지 않고 동결 event ownership과 일치한다.
- Augmented: 그림은 이미 계산한 두 FD step과24 source/numerical 대안만 비교한다. 새로운 parameter sweep을 암시하지 않는다.
- Generation: 새 history·spectrum·uncertainty 예측을 생성하지 않는다. 후속 transport에는 별도로 자격화된 입력이 필요하다.

시각 차단 finding은0개다. 과학 재실행이나 추가 그림을 요구할 잔여 오류를 발견하지 않았다.

