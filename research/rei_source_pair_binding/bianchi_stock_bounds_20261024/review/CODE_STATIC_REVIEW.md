# Bianchi stock 단위 독립 정적 코드 검토

## 판정

**PASS_STATIC_SCOPED. 수정이 필요한 정적 finding은 0이며 코드 repair를 요청하지 않는다.** Root에는 아래 정확한 파일을 `PREPARED_PASS_STATIC_SCOPED`로 기록하도록 권고한다. 이 검토는 advisory이며 과학 admission과 향후 실행 release는 root의 별도 판단이다.

현재 stock 수치 검증은 **NOT_RUN**, 실행 제안은 **PROPOSED_NOT_RELEASED**다. 앞선 pressure 단일 child의 실행·판정·소비된 예산과 이번 stock 정적 준비를 구분한다. Candidate·fixture·runner의 import, compile, test, 실행, CAS, render는 수행하지 않았다.

검토자: `/root/pressure_survey`. 구현자: `/root/pressure_coding`. 검토자는 root 이론이나 candidate/fixture/runner를 작성하거나 수정하지 않았다. 최종 이론·계약과 8개 파일을 직접 읽었고, SHA256·본문·new-file diff의 동일성만 기계적으로 대조했다. 실제 backend 모델은 독립 관측하지 않았다.

## 검토 대상과 고정 identity

| 파일 | SHA256 |
|---|---|
| stock_bounds.py | 25c0e7919df496b79c131ffe0a25cc1101e9bf1d804e721bf190e48d3a165907 |
| focused_check.py | 47ecf7dc0ec59790e4eb339d59c527e71c07aab4ecb7b2fc0c4e265e77b35f43 |
| run_focused_once.py | f3c40f3d426104503370e7ba3f833a15ec19ef41d0cbbab3f70d78f30e3e9cda |
| PROPOSED_EXECUTION.json | 529f9f182407424d09c4521274bcc2795c49fda9eb5ad7787f673fd680cdcdd1 |
| README.md | 82741186ab4a804db445bcd357e6af97b86bacf84da3b198754200aa82cf3122 |
| SOURCE_BINDING.json | 8a48fa83837bafccb2a276d115cf0dde68f4d3c27f24742df5ce941e458a9b9a |
| authority/THEORY_KO.md | 4041f7bd3971e3930ddcd76adca2b91f74c63cee05cca674f522cfbe3dfa15e9 |
| authority/IMPLEMENTATION_CONTRACT.json | b65528e96764b5eb7dc44284b1b50d61ee406d0a0bf692ec01ca61be09e93fb9 |

고정 인계 commit은 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`, base central은 `9f410bf0f4b5d14d1e6b7c17cd2e23a916f241c9`다. 최종 bibliography를 교정한 root 이론과 local authority copy가 byte-equal이다. 이 code review에서는 외부 문헌을 다시 조회하지 않았으며 직접 수식과 구현 대응을 검토했다.

`CODING_REPORT.json`의 8파일 size/SHA, proposal의 candidate·fixture·runner SHA, binding의 prepared hashes가 실제 bytes와 모두 일치한다. `CODING_DIFF.patch`의 SHA는 `074182c5e66e9cd079bba2dd9b2eabdf3f42804555eca6bda7571295f71f86d4`이고, 8개 `/dev/null` additions는 읽은 파일과 각각 정확히 일치한다. 모두 허용된 새 unit prefix 안에 있다. 읽기 시점의 `raw/`는 존재하지 않았다.

## 수치 알고리즘을 실행하지 않고 검토한 근거

### 표현 입력과 sqrt 외측 구간

`_fraction`은 int/Fraction/finite float를 표현된 값 그대로 Fraction으로 바꾸고 bool, nonnumeric, nonfinite, 부호 위반을 거부한다. M과 세 ratio는 엄격히 양수다. `_bits`는 bool을 제외한 정수 1…4096만 받는다. N,U,L,k는 비음수이며 `U<=N*L`를 정확히 비교한다. 오류는 입력 이름을 포함한다.

`_sqrt_interval`은 Q=p/q, s=2^b에 대해 `n=isqrt((p*s*s)//q)`를 사용한다. 따라서 n²q≤ps²<(n+1)²q이고 [n/s,(n+1)/s]가 외측 구간이다. `n*n*q==p*s*s`일 때만 두 끝을 합치므로 grid에서 정확히 표현되는 root의 exactness를 보존한다. float sqrt나 tolerance clipping은 없다.

`kinetic_map_interval`의 x=r²k(k+2M)에 대해 반환 순서는
`x/(sqrt_upper+M), x/(sqrt_lower+M)`이다. 양의 분모에 대한 역수의 방향이 맞다. x=0과 r=1을 먼저 정확히 처리한다. k>0의 작은 입력에서도 양의 Fraction numerator/denominator를 유지하므로 sqrt−M 상쇄나 float 출력 underflow를 만들지 않는다.

### 에너지 분기와 압력 trace

D와 Nt는 각각 세 ratio의 곱, D·N이다. Support는 rmax를 사용한다. Lower는 rmin≤1에서 Jensen 값 D·N·F(U/N), rmin>1에서 chord 값 D·(U/L)·F(L)이다. Upper는 rmax≤1에서 chord, rmax>1에서 Jensen을 사용한다. r=1의 양쪽 정의는 같고 mixed axes를 별도로 배제하지 않는다.

N=0/U=0/L=0은 moment 나눗셈보다 먼저 처리하며, supply된 L의 support map은 유지한다. 실제 outer energy interval은 lower enclosure의 아래 끝과 `min(upper enclosure 위 끝, Nt*support upper)`이다. 두 min 후보가 모두 실제 U의 상한이므로 cap 방향도 유효하다. 수학적 sharp endpoint들의 산술 enclosure는 별도 필드로 보존한다.

압력 lower는 Ulower와 Lupper를 쓴다. (L+2M)/(3(L+M))가 L에 대해 감소하므로 올바른 보수적 방향이다. Upper는 Uupper와 정확한 Nt를 쓴다. a=M·Nt>0에 대해 U(U+2a)/(3(U+a))의 미분은 (1+a²/(U+a)²)/3>0이다. 분모의 양성과 영 분기가 모두 맞다.

문서와 반환값은 압력을 **Tr(P)/3**로 한정한다. Pij=Πδij, 합성 pressure interval의 sharpness, 실제 anisotropic work의 closure를 주장하지 않는다. 에너지의 sharpness 역시 주어진 moments/support를 갖는 unrestricted angular positive measure 집합에 대한 조건부 값이다.

## 준비된 fixture의 독립성

`check_radical`은 a>0인 a√q+b를 양 끝에서 역변환해 유리수 제곱 부등식으로 검사한다. Upper의 역변환이 비음수라는 조건을 함께 검사하고, lower가 음수이면 lower inequality가 자동 성립함을 올바르게 처리한다. Production private sqrt helper를 import하거나 호출하지 않는다.

Identity, expansion, contraction, mixed-axis의 radical 계수·offset은 고정 계약과 같다. Tiny k=2^-200, M=1, r=1/2, bits=64는 양의 lower를 요구하고, 독립된 (F+M)²와 Q의 비교를 준비한다. 영 경계, U>NL, nonpositive M/r, ratio 길이, bool, bits의 계약상 사례와 양의 weight scale 7/3도 포함한다. Fraction 출력은 numerator/denominator 문자열로 직렬화한다.

이 검토는 미래 fixture의 구조와 수식을 읽은 것이다. 실제 assertion 통과나 실행 개수를 보고하지 않는다. Fixture는 계약의 한 유한 그룹이며 모든 valid input의 동적 검증을 의미하지 않는다.

## Runner와 예산 경계

Parent runner는 candidate나 fixture를 import하지 않는다. 소스·fixture hash를 비교하고 exclusive `raw/attempt.json`을 만든 뒤 한 번의 Popen만 수행하도록 준비되어 있다. Child CPU soft=hard 1 s를 설정하며, Popen 전 wall timer를 시작하고 launch elapsed를 5 s에서 뺀 나머지를 communicate timeout으로 사용한다. Timeout은 child kill로 기록하고 retry loop는 없다. 검토한 fixture/production path에는 추가 child 생성이 없다.

실제 stdout/stderr, RUSAGE_CHILDREN CPU 차이, launch-inclusive elapsed, return code, timeout, 오류, 파일 identity를 남기도록 되어 있다. 이것은 prospective runner의 정적 확인이다. 실제 runtime, 종료 overhead, CPU/wall 통과와 resource admission은 **미관측**이다. 향후 release가 있으면 실제 receipt로 판단해야 한다.

`bits`는 입력 단위의 sqrt 절대격자이며 물리 tolerance나 역사적 **2e-12 gate의 대체값이 아니다**. 검토한 diff는 이 새 단위의 8파일 추가뿐이며 기존 gate 또는 pressure 구현을 수정하지 않는다. Proposal의 PROPOSED_NOT_RELEASED, separate root release, pressure/L1 allowance 비전용과 미계측 비용 분리가 일관된다.

## Findings와 권고

- Blocking finding: **0**
- Nonblocking code finding: **0**
- Requested code repair: **없음**
- Reviewer candidate/fixture/runner import·compile·test·과학 child·CAS·render: **0**
- Implementation 변경, Git/cloud 변경: **0**
- 검토·모델·기계적 읽기/I/O 비용: **UNMEASURED_NOT_ZERO**

Root가 이 exact candidate를 **PREPARED_PASS_STATIC_SCOPED**로 기록하는 데 반대할 정적 결함을 찾지 못했다. 수치 상태는 NOT_RUN, stock scientific admission은 NOT_ISSUED를 유지한다. 별도 root release 없이 준비된 명령을 실행하지 않는다. 실제 HI history·초기 저장고·cosmological background·stopping·EOS·Einstein evolution·L4 또는 전체 완료율을 새로 승인하는 결과가 아니다.

