# C5 독립 사전 검토

판정: **PASS_SCOPED_PREEXEC**. 동결한 consumer/checker/runner에 새 실행을 차단할 과학·알고리즘·수용 기준 오류를 발견하지 않았다. 이 판정은 한 번의 동결된 capped 실행 준비에 대한 것이며, 수치 통과나 최종 과학 채택은 아직 판정하지 않는다.

## 검토 독립성과 범위

검토자는 이번 이론 문서와 기호 유도에 참여했지만, consumer·checker·runner를 작성하거나 수정하지 않았다. Root가 이론과 동결 계약을 별도로 검토했다. 이번 검토에서는 실제 code 본문, manifest, CR 원래 validation helper, actual24 반환 형식과 고정 native species/coefficient source를 읽었다. 실행·module import·기존 suite 또는 source replay를 수행하지 않았다.

## 확인한 핵심 경로

1. **세 moment와 단위:** reader는 기존 SI 값 A, K=-fast_kinetic, G=radiation을 읽고 G 및 일곱 signed reservoir를 원문에 보존한다. production에서 b를 주지 않으면 projection이 null이다.
2. **Native25와 photon port:** indices11/12/21/22는 a,-a,-a,-k이고 photon count/energy는 별도 port다. Native external index23과 logT24를 포함한 나머지 행은 0이다. Flattened27은 serialization으로 표시한다.
3. **일반 JVP:** independent signed dA,dK,dG,db를 허용한다. Quotient 미분과 energy constraint derivative가 동결 식과 일치한다. Conservative tangent는 검사에서만 선택하고 incompatible dG 방향을 0으로 강제하지 않는다.
4. **Reference와 clock:** beta scaling에서 dbeta를 포함하고 logT를 제외한다. Proper/eta integrated packet은 같은 값이며 H 방향 derivative는 0이다. 기존 continuous RHS를 실행하거나 수정하지 않는다.
5. **Endpoint와 capacity:** endpoint의 drplus 항과 logT pass-through가 구현되어 있다. Capacity는 제조한 nonnegative 수·에너지 제약으로 표시하고 physical step/history/submeasure qualification을 false로 유지한다.
6. **Supplier 조건:** unchanged validate_event 경로가 실제 frame/channel/support, canonical/source identity, null rate/exposure/RHS/history/spectrum/heating, event ownership과 false physical update 상태를 검사한다. 중복 및 다른 case/z 대안의 합산을 거부한다.
7. **검사 독립성:** Decimal50 expected 값은 consumer helper를 호출하지 않고 명시적인 row quotient로 작성되어 있다. 두 FD step의 baseline operand scale, exactzero 행, conserved 및 incompatible tangent, unit-specific mutant가 동결 기준과 일치한다.
8. **실행 경계:** runner는 exact GO/manifest, 기존 attempt 보존, 누적 prior+.90<=14.9, child .75 CPU s, wrapper .10 CPU s, wall8 s, 512 MiB, one worker, tail .05를 사용한다. Checker의 CPU timer와 runner의 process/receipt 경로를 읽었다. 실패 시 자동 재실행 경로는 없다.

Native cumulative binding vector는 pinned atomic_network source에서 HeI와 HeII 문턱을 순차 합산한다. He4 index11/12와 54.42 eV row를 확인했으므로 이번 event의 binding sign과 threshold 대응이 맞다. 실제 floating-point output은 동결 residual 기준으로 판정한다.

## 적용한 범위 교정

Root가 발견한 runner 실행자 provenance 문구는 requested lower-tier와 실제 tool metadata의 의미를 구분하도록 실행 전에 교정됐다. 검토자는 변경된 runner와 새 manifest를 다시 바이트 식별하여 이 판정에 묶었다. Consumer, checker, 물리 식, tolerance와 numerical work는 바뀌지 않았다.

차단 finding은 0개다. 추가적인 일반 hardening이나 adjacent physics 확장은 이번 실행 조건에 넣지 않았다.

## 다음 실행과 채택

Root가 해당 소스 checkpoint의 게시·이중 백업 및 최신 입력 상태를 확인한 뒤, 정확한 manifest에 묶인 EXECUTION_GO를 작성하면 한 번의 bounded 실행으로 이동할 수 있다. 실행 후 raw stdout, CHECKS/OBSERVATIONS,24 map table, resource receipt와 실제 figure를 C9에서 확인한다. 현재 status는 preexecution PASS이며 numerical/scientific admission은 pending이다.

