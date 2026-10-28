# 실제 DR 유한 온도 구간 연구 — 실행 대기 인계

## 현재 완료 범위

단위는 `rei_dr_finite_temperature_enclosure_20261028`이다. Root의 실제 결정에
따라 이론 R1–R10은 10/10, 코드 준비 C1–C5는 5/10, 합계는 **15/20**이다.
독립 이론 검토는 PASS_SCOPED_INDEPENDENT_THEORY이고, 수정 후 소스 검토는
PASS_SCOPED_STATIC_PREPARATION_AFTER_TARGETED_REPAIR이다. 실제 실행을 읽은
검토가 아니므로 C9는 STATIC_ONLY_NOT_RUNTIME_ACCEPTED이며 완료 수에 넣지 않는다.
C6/C7/C8은 NOT_RUN, C10은 HANDOFF_PREPARED_NOT_COMPLETE이다.

인정된 결과는 고정된 실제 DR 세 행의 binary64 매개변수 이미지를 정확한 실수로
취급한 함수에 대한 D1–D5, 양성 증명, 바깥쪽 구간 연산 구현의 준비와 정적 검토다.
이미 수행된 단일 CAS의 세 항등식 결과와 관측 CPU 0.00341초는 별도 원본에 남아 있다.
원자 적합 오차, 전체 native callback 반올림 오차, RR/Mao, 실제 REI 열 상태나
native25/radii는 이 결과에 포함하지 않는다. 물리 T/native25/radii는 null,
L4_ready는 false, global_physical_completion은 null을 유지한다.

## 발견 사항과 한 차례 수정

F-ZERO는 동일한 Taylor 끝점에서 ln(1)의 이웃 구간이 subnormal 연산을 유발하던
경우다. 검증된 동일 끝점은 이제 h=[0,0], radius=0, enclosure=f0를 반환한다.
alpha와 L의 두 검증 항목을 기존 단일 선택 실행에 추가했으며 아직 실행하지 않았다.
F-FAMILY는 내부 leaf의 setsid가 외부 session 감시에서 빠지던 문제다. leaf는
부모 session에 남고 내부 감시는 알려진 단일 PID를 직접 종료하도록 바뀌었다.
두 수정은 독립 검토에서 CLOSED_STATIC이다. 기존 F-PLOT1의 지수 표기/축/레이블
수정도 CLOSED_STATIC이나 실제 SVG/PNG와 시각 검사는 아직 없다.

초기 보고서, 실제 수정 전 소스, author diff, 전후 해시, 독립 검토의 종료 기록과
읽기 원장은 review/에 보존했다. PREPARED_IDENTITIES.json은 최종 코드 상태를
지정한다. R9/R10의 이전 코드 사본은 변경하지 않은 역사적 캡슐이며, C5의 최종
코드가 공개 경로를 갱신한다. 이력 캡슐을 새 소스로 덮어쓰지 않는다.

## 예산과 필요한 승인

이번 포장 전 보수적 잔액은 planning **21.004288062**, presentation
**59.929009308 CPU-s**이다. 이미 포함된 CAS 전체 예약 0.05초 안에 실제 관측
0.00341초가 들어 있으므로 둘을 다시 더하지 않는다. 이번 기계적 포장의 실제 CPU
prefix만 delivery/PACKAGING_RECEIPT_C1_C5.json에서 presentation에 추가한다.
기록 이후 tail, 도구/모델/전송 비용은 UNKNOWN_NOT_ZERO이며 전체 예산 PASS는 없다.

현재 승인된 20/60으로 새로운 수치/그림 실행을 시작할 수 없다. 제안하는 절대
누적 한도 **22/62는 아직 승인되지 않았다**. 제안 실행분은 수치 target 0.4초와
별도 tail 0.2초, 그림+renderer target 1.5초와 별도 tail 0.3초다. 다른 branch의
30/65 승인이나 미래 main 700 제안을 가져오지 않는다. main은
595.225063/600, NO_MORE_IVPs를 유지한다.

Root가 준비 결과를 공개하고 실제 양쪽 provider ACK를 보존한 뒤, 남은 실행에
대한 구체적 추가 승인을 요청한다. 승인 전에는 아래 명령을 실행하지 않는다.

## 승인 후 단일 실행 순서

단위 디렉터리에서 수치 작업을 한 번만 실행한다.

```bash
python -B -S code/execute_bounded.py numerical --execute-authorized
```

정상 결과의 원시 출력, source hash, scalar oracle/구간/잔차/zero-step 기록과
전체 command 비용을 실제로 읽고 독립 runtime 검토를 받은 뒤, root가 그림 작업을
별도로 dispatch한다.

```bash
python -B -S code/execute_bounded.py presentation --execute-authorized
```

그림은 저장된 출력만 읽으며 rate/test를 재평가하지 않는다. SVG와 PNG, renderer
stdout/stderr/exit 및 실제 이미지를 검사해야 C8을 판단할 수 있다. 수치/그림은
각각 한 번이며 자동 재시도와 fallback 렌더링은 없다. 실패하거나 stop이 작동하면
원시 증거와 비용을 보존하고 멈춘다. Linux tick/poll 감시는 엄격한 whole-host
상한 보증이 아니며 실제 전체 command와 별도 supervisor prefix를 기록한다.

원래 DAG는 working 33/88, central 28/88, 88 IDs/17 edges, delta 0이다.
이 로컬 준비 결과는 전역 물리 완료나 기존 gate 통과를 추가하지 않는다.
