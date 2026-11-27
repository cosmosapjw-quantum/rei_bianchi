# ENDPOINT14 비저자 실행 전 심사

**결정: PASS_SCOPED_PREEXEC. 현재 blocking 0건, 미해결 nonblocking 0건. F1·F2 모두 종결.**

이 심사는 고정된 CONTRACT와 여섯 Python 파일, THEORY, 구현 설명, 실행 계획을 읽고 수행했다. 심사자는 현재 이론·구현의 저자가 아니며, GitHub source intake의 저자다. 부모 대화 맥락을 공유하므로 blind review라고 주장하지 않는다. producer와 certificate reader는 같은 하위 등급 구현자가 작성한 별도 코드 경로이고, 독립적인 과학 판단은 본 비저자 심사에서 제공한다.

## 실제 발견과 수정 확인

**F1 — 수정 완료.** 양의 정규화 하한을 보장하려면 87도 nominal mu를 중심으로 한 반경 delta=(7/50)/(36B)의 구간이 [-1,1] 안에 들어가는 실제 saved-input 검사가 필요하다. 최초 구현에는 이 제어가 없었다. Root가 허가한 최소 수정 후 producer는 saved mu와 확장 구간, Lstar, 18B, delta, Dmin을 보존하고 포함 관계를 검사한다. reader는 immutable 원본 rows에서 같은 값을 독립적으로 재구성하여 모든 필드와 값을 비교한다. 이 수정은 실행 전 수정이므로 science repair reserve를 사용하지 않았다.

**F2 — 주석 정정 완료.** 테스트의 weighted primitive derivative 주석이 이 코드에서 사용하는 tail moment G_j의 도함수 -2*t^(2j)+2*t^(2j+2)로 정정되었다. 실제 함수, CONTRACT와 THEORY는 이미 올바른 감소 공식을 사용했다. Root가 허가한 comment-only 수정의 실제 행과 파일 hash만 읽어 확인했으며 추가 audit·test·science 실행은 없었다. 테스트 파일 SHA256은 d18e4e79ed987b9c11a13b2a1a22a6bb1f974d520be6d0878beeb86d825eb516에서 57a84b1abf0eb36af1fd617018bf4148f5f3597da5272878e22e0cf746d71c9c로 바뀌었고, 나머지 다섯 Python 파일 hash는 그대로다. 이전 S02 심사는 당시 스냅샷으로 보존하며 S03에 이 closure를 싣는다.

## 과학 및 구현 판단

- Endpoint factorization, 세 coefficient의 signed interval error, B=160, Dmin=49/14400000, 고정 candidate, N=1/4/16이 계약과 일치한다.
- 새 THEORY의 same-event 두 꼬리 geometry 증명은 saved zeroth moment로 threshold를 복원하는 근거를 제공한다. 과거 monomial moment의 겹침 검사는 보조 호환성 검사로만 쓰인다.
- Producer는 모든 3-active-constraint 조합을 정확히 열거하고 singular/feasible counts와 active witnesses를 보존한다. 유계 polytope의 모든 정점에 관한 증명과 코드의 실제 exhaustive loop를 함께 확인했다.
- Reader는 producer를 import하지 않고 행, moment, 제약식, 정점, witness, nesting, 극값 bound, outward decimals 및 saved curve를 재구성·검사한다. 별도 optimizer나 두 번째 exhaustive enumeration이라고 과장하지 않는다.
- Signed numerator lower의 concavity와 upper의 convexity, 양의 D를 이용하는 정점 bound는 타당하다. Inner/candidate 실제 feasible witness는 최소값의 상한과 최대값의 하한을 제공한다.
- 여덟 test group은 변경된 수학 경로와 known cube/simplex, signed coefficients, exact tail examples, corruption rejection을 직접 검사하도록 구성되어 있다. 실제 reader는 campaign에서 직접 한 번, actual-certificate test에서 다시 읽는다. 이는 construction 반복과 구별한다.
- Mandatory EXECUTION_PIN 검사는 실제 construction 전에 수행된다. 코드·계약·두 입력의 hash를 요구하고 actual source commit/tree와 publication scope를 기록한다. S05 실제 게시·readback과 pin 생성은 아직 controller 단계다.
- Runner는 T13에서 수정된 namespace-aware runner와 byte-identical하다. 기존 모니터 수정의 재검증을 위한 과학 실행은 요구하지 않는다. 자원 기록은 whole runner + waited children의 CPU와 wall을 명시하며 세션 전체 비용이라고 주장하지 않는다.
- Plotter는 저장된 값만 읽고 일반 스케일로 PNG/SVG를 생성한다. 과학 import/call이 없으며 실제 rendering과 image QA는 추후 한 번 수행한다.

모든 파일 hash, 상세 근거, 발견 이력은 PREEXEC_REVIEW.json에 보존했다. STATIC_SYNTAX의 여섯 SYNTAX_PASS 기록과 현재 hash가 일치함을 읽어서 확인했으며, 심사자가 compilation이나 science를 반복하지 않았다.

## 실행으로의 전이

**PASS → S05 실제 source 게시·ref readback → 실행 pin 작성 → root GO → 하위 등급 실행자의 단일 bounded campaign.**

검사 상한은 validation wholeCPU120s/wall300s, plot wholeCPU10s/wall30s, AS768MiB/thread1이다. 한 번의 진단된 repair는 root 허가와 같은 누적 자원 상한을 필요로 한다. 고정 candidate와 N을 결과에 맞춰 바꾸지 않는다.

현재 결과는 실행 전 정적 심사 PASS이며 실제 candidate의 네 데이터 창 통과, 여섯 polytope의 정점, 실제 극값과 자원 결과에 대한 scientific admission은 아직 없다. 심사자의 science/test/import/CAS/plot 실행은 모두 0회이고 review 비용 CPU/wall은 측정하지 않았다. 완료된 이전 캠페인을 재실행하지 않는다.

