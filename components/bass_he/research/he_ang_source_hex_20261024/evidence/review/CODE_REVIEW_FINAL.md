# HE-ANG-SOURCE-HEX-INTAKE C9 독립 코드 검토

**판정: `PASS_SCOPED`.** 새 Hex source intake와 저장된 유한 Chebyshev 계수 도구는 이 단원의 범위에서 승인한다. 실제로 완료된 전체 catalogue는 선택한 공식 dataset에 `ionf` row가 없음을 확인한다. 따라서 상위 `HE-ANG-SOURCE`는 **`SOURCE_INPUT_PENDING`**이며, 물리 angular provider·finite-mass event law·경험적 각분포는 승인하지 않는다.

검토자: `/root/state_backup`. 구현자는 `/root/hex_intake_code`이며, 이 검토자는 구현을 작성하지 않았다. 원전·코드·diff·저장된 raw receipt를 읽었다. 프로젝트 모듈 import, 과학 계산, test·catalogue·profile·plot 실행, 기존 suite 재실행은 각각 **0**이다. 이 문서 작성 시 수행한 자동 작업은 파일 hash와 저장된 회계 기록의 산술 확인뿐이다.

## 1. 검토한 정확한 버전

| 용도 | `code/hex_intake.py` SHA256 |
|---|---|
| 최초 synthetic15 및 실패 catalogue | `8c2a510e9d34f4a54a6035d851b32aa629b77c8ebd89c35eb331abeedb87c4c8` |
| A1 line-dialect synthetic5 및 실패 retry | `012809cd4d2141c9e505dfd8a43aa0fc0d754d79d980403384c3a44fa54da0f7` |
| A2 synthetic3·완료 catalogue·plot | `2196134dbfd7b757eaef3a83618af86c66332a550d9008166d13ac88e8b4935d` |
| A3 최종 guard·해당 test method1 | `3552737bcd6cd488756f3ae5c70d1e28882bb6163d8fc4f48606689c6ef6f93e` |

최종 core는 A2 catalogue 실행 core에서 `INSERT` 뒤 whitespace/EOF guard 한 줄만 강화했다. 각 실행 당시 source manifest와 이전 코드 사본이 보존되어 있다. 최종 source를 과거 모든 실행의 source였다고 기록하지 않는다. 전체 file identity와 receipt 목록은 동명 JSON에 고정했다.

## 2. 실제 source 결과와 입력 동일성

`evidence/execution/A2/04_catalogue.stdout.txt`와 해당 `FINISH.json`을 읽어 다음 결과를 확인했다. 완료된 stream의 compressed identity는 `evidence/intake/ACQUISITION.json`의 원자료 pin과 일치한다.

| 항목 | 완료 catalogue 결과 |
|---|---|
| 공식 원자료 | `https://utf.mff.cuni.cz/data/hex/Hex-170210.sql.xz` |
| compressed bytes / SHA256 | 7,880,672 / `afa8d83ada688ecf91c40340da669e204885ec5c52d04fc55b48837b52135101` |
| decoded bytes / SHA256 | 69,441,007 / `82def29890bba56bb31f31524dcbea58bd0a0f5b39441ee7b6594bd28fc54896` |
| statements | BEGIN1, INSERT948,557, COMMIT1 |
| `tmat` rows | 948,557 |
| H1 initial `(ni,li,mi)=(1,0,0)` `tmat` rows | 86,457 |
| H1 `tmat` literal `Ei` range | 1e-7–0.9374 Ry |
| 전체 `ionf` / H1 `ionf` rows | 0 / 0 |
| SQL 실행 / physical provider 값 추론 | false / false |

이 결과는 **선택한 파일에 H1 ionization coefficient 입력이 없다는 판정**이다. ionization cross section 또는 amplitude가 물리적으로 0이라는 판정이 아니다. 다른 dataset·다른 source의 가능성을 배제하는 no-go도 아니다. source code의 ionization 기능, generic decoder의 구현, 실제 numerical ionization payload의 확보를 구분한다.

## 3. Parser와 최소 교정 검토

최초 catalogue는 세미콜론 전용 framing 때문에 8 MiB statement cap에서 실패했다. 제한된 65,536-byte prefix에는 LF937, semicolon0이 있었다. Hex v2.02 `hex-db/src/db.cpp::hex_import_`는 `getline`으로 읽은 행을 처리하며, `hex_dump_`도 행 끝 세미콜론 없이 BEGIN·INSERT·COMMIT을 쓴다. 따라서 A1의 명시적 `--dialect hex-lines`는 관측된 형식 차이에 직접 대응한다. 기본 semicolon lexer, 총 128 MiB decoded cap, 8 MiB statement/line cap은 유지되었다.

기본 lexer의 quote·comment·chunk 경계는 최초 제조 fixture의 raw 결과를 재사용했다. 새 line dialect는 한 행의 literal INSERT, full-line comment, transaction marker, 제한된 known-table CREATE 기록을 처리하며, 여러 행 또는 여러 statement/VALUES는 거부한다. 완성된 실제 catalogue의 verb tally는 BEGIN·COMMIT·INSERT뿐이다. 따라서 이 실제 payload에서 malformed INSERT verb가 조용히 생략된 흔적은 없다.

A2는 숫자로만 구성된 행의 token별 반복 검사를 동일 `NUMBER_PATTERN`의 compiled whole-row match로 바꿨다. BLOB/NULL fallback, field 수·순서, H1 initial integer와 finite energy 검사는 보존했다. 단일 승인 prefix 262,144 bytes에서 완결된 INSERT3,627개에 대한 old/new parse output이 정확히 일치했다. 이 prefix profile는 full availability 판정에 사용하지 않는다.

독립 검토 중 `INSERTfoo`와 `INSERT(foo)`, `INSERT;`, comment-adjacent prefix가 literal parser를 우회할 수 있는 문제를 발견했다. 최종 A3는 `INSERT` 뒤 whitespace/EOF를 요구한다. 이 변경에 영향을 받는 기존 unittest method 하나에 punctuation negatives를 넣어 한 번 실행했고 PASS했다. 정상 literal INSERT는 이미 공백을 요구하므로 해당 guard는 지원 문법을 확장하지 않는다. A2 전체 catalogue를 다시 실행할 필요는 없으며 실제로 재실행하지 않았다. **현재 열린 blocking code finding은 0개다.**

## 4. ABI·H1 matching·Chebyshev 보증 범위

원전 `common/hex-arrays.h`의 BLOB는 native bytes이며 precision과 complex layout을 스스로 증명하지 않는다. 새 decoder는 little/big endian과 `binary64-real-imag`를 외부에서 명시하도록 요구한다. nonempty 16-byte 배수, finite complex coefficient, schema·quantum number·양의 excess-energy 조건을 확인한다. plausible 값을 근거로 endian을 고르는 경로는 없다. `decode_ionf_row`는 generic utility이며 H1 이외의 initial state를 decode할 수 있으나, catalogue의 H1 증거는 정확한 `(1,0,0)` matching으로 분리한다. 실제 ionf가 없으므로 실제 producer ABI를 이번 결과로 인증하지 않는다.

저장된 유한 표현은 `P_N(t)=C0/2+Σ_{j=1}^{N-1} Cj Tj(t)`이고, `evaluate`는 full prefix를 기본으로 사용한다. `x∈[0,1]`, `t=2x−1`, `1≤m≤N`에서

\[
|P_N(t)-P_m(t)|\le\sum_{j=m}^{N-1}|C_j|\le\sum_{j=m}^{N-1}(|\operatorname{Re}C_j|+|\operatorname{Im}C_j|)=\tau_m.
\]

`exact_tail`은 입력된 binary64 성분을 exact Fraction으로 바꾸어 **전체 생략 suffix**를 더한다. `select_terms`는 이 nonnegative suffix를 사용하므로 중간의 작은 계수만 보고 뒤의 큰 계수를 놓치지 않는다. 독립 forward recurrence, `C=(2,0,2)`의 late-nonzero 반례, negative tolerance·domain·nonfinite·잘못된 ABI·누락 payload 등의 제조 controls가 저장된 raw에서 PASS했다.

이 bound는 represented finite polynomial의 coefficient omission만 다룬다. floating Clenshaw roundoff, overflow, 저장 전 fit·aliasing, 원전 dynamics·numerical convergence, 상대오차, physical model uncertainty 및 radial endpoint division은 포함하지 않는다. 원전 `ionf.cpp`와 `tdcs.cpp`의 `(k1k2)^2` 대 `(k1k2)` division 차이는 보류한 채 유지한다. 새 코드가 이 차이를 숨겨 물리 amplitude·TDCS를 생성하지 않는다. Fixed-nucleus source를 finite-proton-mass dynamics로 바꾸는 보증도 없다. 기존 HE-X1 결과를 경험적 angular correction으로 승격하지 않는다.

## 5. 실행·회계·재사용 판정

새로 허용한 dependency만 검사한 네 synthetic invocation은 각각 15, 5, 3, 1 method를 실행했다. 마지막 1개는 A3 변경된 method에 대한 국소 회귀이며, 이 숫자들을 24개의 서로 독립적인 physical fixture로 해석하지 않는다. catalogue는 실패2회와 성공1회, diagnostic2회, synthetic plot1회다. 과거 HE-X1의 32 fixture와 HE38·HE-ANG-CONTRACT 검토는 재실행하지 않았다.

회계 authority는 `evidence/execution/RESOURCE_LEDGER.json`, SHA256 `b1eb4cf0e367f46260997f1e4cebf33228d5e9b7376329370bd91d323ef52450`이다. 10개 실제 child의 stdout/stderr hash, 연결된 이전 ledger hash, 실행 source-manifest hash, aggregate 합계와 invocation count를 확인했다. accounting carrier를 실제 시도로 중복 가산하지 않았다.

| 자원 | 누적 측정 | 한도 | 남은 값 |
|---|---:|---:|---:|
| CPU seconds | 18.434312000000002 | 20 | 1.565687999999998 |
| Wall seconds | 18.739398924000852 | 60 | 41.26060107599915 |

실패 시도와 진단 비용을 모두 포함하며, 이전 unit의 잔여 예산을 가져오거나 reset하지 않았다. HE-X1의 failed prelaunch와 D10 등에 남은 `UNKNOWN_NOT_ZERO`는 0으로 바꾸지 않는다.

**Aggregate 20/60은 충족했지만, 모든 child가 설정 CPU8초 이하였다고 주장해서는 안 된다.** A1 실패 catalogue는 CPU8.349479초, A2 성공 catalogue는 CPU8.144439초를 실제로 소비했다. 두 overshoot를 보존한다. A1의 `rc=-9`는 SIGKILL이고 설정 CPU 경계와 부합하지만, receipt만으로 정확한 kernel 원인을 확정하지 않는다. A2의 완성된 데이터 결과와 이 운용상 초과를 구분한다.

synthetic plot은 한 번 생성되었고 root의 `FIGURE_REVIEW.json`을 재사용한다. 계수 `(2,0,2)`의 유한 다항식 및 suffix bound만 표시하며 physical provider 값이 없다. 이 검토자는 그림을 다시 계산하거나 과학 실행을 추가하지 않았다.

## 6. 종결과 유지되는 gate

이 C9의 새 과학 실행 요구는 없다. source acquisition·입력 공백 판정·generic coefficient intake·정확한 represented-tail bound 및 해당 구현 검토를 `PASS_SCOPED`로 닫는다. 상위 physical-provider gate는 `SOURCE_INPUT_PENDING`으로 유지한다. 다음 단계는 numerical H1 ionization payload, producer ABI, normalization·spin/exchange·support·convergence와 finite-mass 또는 명시된 approximation의 source/frame/event 계약을 충족해야 한다.

Expected-SHA publication, 중앙 DAG에서 다른 node·원계약 보존, Dropbox/Drive backup receipt는 root의 별도 delivery 작업이다. 이 코드 검토는 그 작업이 이미 완료되었다고 주장하지 않는다.
