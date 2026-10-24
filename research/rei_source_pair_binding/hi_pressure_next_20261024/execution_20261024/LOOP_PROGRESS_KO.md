# 단계별 DAG·완료 범위

원래 고정 authority와 보호 예약은 유지한다. 유한 단위의 단계 상태와 전체 모델의 상태를 구별한다.
전체 모델 완료율은 **null**이다.

## 의존 DAG

~~~mermaid
flowchart TD
  A[고정 authority와 최신 의존성] --> P[기존 pressure 이론·코드]
  A --> S[7repo와 대화·백업 조사]
  P --> X[한 pressure fixture 실행]
  S --> X
  X --> V[독립 raw 심사와 scoped admission]
  V --> D[소유 경로 게시와 A·B·C 보존]
  P --> T[Bianchi I stock 경계 유도]
  T --> R[독립 이론·정적 코드 심사]
  R --> B[stock 준비물 B2 보존]
  B --> N[다음 stock fixture 미실행]
  N --> H[초기 저장고·주입 이력·배경 입력]
  H --> W[tensor work·stopping·thermal 결합]
  W --> E[자기일관적 Einstein 진화]
~~~

C23E·HE·CR·REC·PHYS의 별도 provider 상태는 survey/SURVEY_SYNTHESIS_KO.md와 CLAIM_GATE.json에 유지한다.
이들의 유한 진단 통과가 마지막 물리 진화 노드를 자동으로 닫지는 않는다.

## 정확한 단계 상태

complete=해당 의무 완료, reused=불변 근거 재사용, in_progress=부분 완료,
pending=남은 의무, not_applicable=해석적 명제에 적용 제외.

| 단계 | pressure 유한 단위 | stock 다음 단위 | 백업·게시 연결 |
|---|---|---|---|
| R1 | complete: 현재 권한·연구 위치 | complete: prescribed geometry·massive cohort | pressure A/reused parentC; stock B2 |
| R2 | complete: 기존 근거와 최신 의존성 | complete: 원전·pressure 연결 | pressure A/reused parentC; stock B2 |
| R3 | reused: 양의 측도 가정 유지 | complete: 정의역·단위·angular class | pressure A/reused parentC; stock B2 |
| R4 | reused: concave kernel·extremizer 유지 | complete: F_r·축 min/max·유리화 | pressure A/reused parentC; stock B2 |
| R5 | reused: sharp pressure·NR bound 유도 | complete: energy·pressure·shear work 유도 | pressure A/reused parentC; stock B2 |
| R6 | reused: 불변 이론 독립 검토 | complete: 독립 수학 검토 | pressure A/reused parentC; stock B2 |
| R7 | complete: 한 exact fixture 실제 실행 | not_applicable: 해석적 명제는 직접 증명·수작업 검토로 닫힘; 코드 실행은 C6–8의 별도 의무 | pressure B; stock B2 |
| R8 | complete: scoped admission | complete: 조건부 analytic 범위 채택 | pressure B; stock B2 |
| R9 | complete: 결과·구현 연결 | complete: 구현 계약 연결 | pressure B; stock B2 |
| R10 | pending: 게시·최종인계 대기 | pending: 최종 보존·재개 인계 대기 | pressure C/publication; stock C/handoff |
| C1 | complete: baseline·최신 HEAD | complete: baseline·입출력·단위 | pressure A/reused parentC; stock B2 |
| C2 | reused: 식–코드 대응 | complete: 식–fields 대응 | pressure A/reused parentC; stock B2 |
| C3 | reused: exact Fraction 설계 | complete: 외측 구간·상쇄·경계 | pressure A/reused parentC; stock B2 |
| C4 | complete: 한child CPU1/wall5/retry0 | complete: static task와 미래 release 분리 | pressure A/reused parentC; stock B2 |
| C5 | reused: 고정 구현 사용 | complete: 8파일 구현·fixture·runner | pressure A/reused parentC; stock B2 |
| C6 | complete: 실제 assertions 통과 | pending: 실제 stock fixture NOT_RUN | pressure B; stock B2 static; future raw pending |
| C7 | complete: 수식·참조·경계 확인 | in_progress: 정적 식 대응 완료; 실제 controls 남음 | pressure B; stock B2 static; future raw pending |
| C8 | complete: 정확 산술·측정·재현 근거 | pending: 실제 수치·CPU/wall 결과 없음 | pressure B; stock B2 static; future raw pending |
| C9 | complete: native raw 심사·metadata finding 종결 | in_progress: 독립 static PASS; 실행 raw 심사 남음 | pressure B; stock B2 static; future raw pending |
| C10 | pending: 게시·최종 전달 대기 | in_progress: 준비물 인계; 수치 판정 미발행 | pressure C/publication; stock C/handoff |

## 완료도의 의미

Pressure의 실제 science 의무는 닫혔고 이 기록 시점에는 게시·최종인계가 남았다. 최종 readback 뒤 R10/C10만 complete로 바꾼다.
Stock 해석적 유도와 정적 준비는 완료되었다. C1–C5 complete, C6–C8의 실제 실행, C9의 raw 심사, C10의 수치 판정은 열려 있다.
단계수나 백업수로 전체 물리 모델 완료율을 만들지 않는다. 저장 ACK와 commit은 실제 receipt로 확정한다.

