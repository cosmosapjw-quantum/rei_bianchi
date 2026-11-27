# F02 — 첫 검증 실패와 승인된 test20 fixture 수정

immutable local source `2e1de5c12311b94002ca2c786cfa4d25d050314f`의 첫 전체 검증은
25 unique method 중 **24 PASS, 1 FAIL, error0**였다. 실패는 test20의 마지막
`manual coincidence width > 2^-40` assertion이다. 원 FAIL report, saved JSON,
stdout/stderr, 두 자원 receipt와 실행 pin을 `evidence/validation/initial/`에
바이트 그대로 보존했다. 원 test source는 원 Git S05 commit에 그대로 있다.

독립 same-pass reviewer의 F02 판정은 `TEST_ORACLE_FIXTURE_FALSE_FAIL`이다.
모형 A=3,M=2,e=8/3에서 k=40/51이고 F는 증가한다. 원 polar A[0,4/5], B[-4/5,0]의
첫 coincidence assignment는 mu>=k를 요구하지만
F(k)^2=73984/82993>16/25이므로 동시에 F(mu)<=4/5일 수 없다. 반사된 둘째 assignment도
비어 있다. 따라서 원 반환 coincidence[0,0]과 manual width0은 올바르며, 이를 양의
폭으로 요구한 fixture가 잘못되었다. 기존 enclosure 한도 assertion들은 통과했다.

parent는 test20 내부만 수정하도록 승인했다. 원 manual fixture를 exact0 control로
유지하고 positive fixture의 polar 범위만 A[0,1], B[-1,0]으로 바꿨다. 반대 arc의
위치와 폭1/3, default/manual delta, 모든 기존 tolerance와 폭 assertion을 유지했다.
새 fixture의 비자명한 root ±40/51은 nondyadic이며 delta1/16 bracket의 실제 폭은1/16이다.
J=1/6+(12-3sqrt3)/(80pi)>1/6이므로 manual outer-inner mass gap은
2*(1/16)*J>1/48>2^-40이다. 증명과 승인은 `F02_FIXTURE_DIAGNOSIS.json`에 있다.

static AST 비교에서 나머지24 method와 test20 밖 코드가 그대로임을 확인했다.
production code, 네 script와 Wolfram program의 SHA256은 원 실행 pin과 같다.
수정된 test 파일은 compile만 했고 import나 test 실행은 하지 않았다.

첫 실행 whole process CPU는 **0.791723s**, wall은 **0.8169768509997084s**이며
outer orchestration CPU는 별도 **0.003971411s**였다. 누적 CPU20s·wall60s 한도는
초기화하지 않는다. 남은 whole process 예산은 CPU19.208277s·wall59.18302314900029s이며
process당 AS512MiB·thread1을 유지한다. targeted reserve는 아직 **0회 소비**다.

현재는 수정 준비 완료 상태이며 S06 전체 완료나 과학 결과 채택이 아니다.
parent가 새 immutable repair source의 실제 publication·dual backup ACK와 local pin을
제공한 뒤 원 external resource를 prior receipt로 넘겨 test20만 한 번 실행한다.
나머지24 검증은 변경되지 않은 source와 method body에 해당하는 원 결과를 재사용한다.
full suite 반복, 이전 단위 실행, 도표, provider call과 commit은 수행하지 않았다.
