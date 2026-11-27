# R8–R10 판정과 구현 인계

R8: `THEORY_KO.md` Eqs.(2)–(6)을 명시한 전제하의 derived 결과로 채택한다. 독립 R6은 `PASS_AFTER_CORRECTION`이다. 초안의 예시 산술 오류 R5-EXAMPLE-01/R6-01은 실제 Wolfram 출력과 독립 직접 산술로 교정·종결했다. 동일 근거의 반복 감사나 기존 science suite 재실행은 필요하지 않다. 원전 v3 Eq.(26)의 부호 교정은 해당 source version과 식에 한정한다.

R7의 Wolfram 호출1회는 corrected residual0을 두 spin에서 확인했다. 실제 toolwall8.981s, symbolic body CPU0.066279s/wall0.066602s이며 전체 원격 CPU는 UNKNOWN_NOT_ZERO다. 선택적 phase-endpoint 쿼리는 비음수 전제가 빠진 복소수 형태/경고를 반환했으므로 그 출력은 채택하지 않았다. Eq.(5)는 직접 증명·R6 및 새 coding control의 대상이다. 불필요한 재호출은 하지 않는다.

R9: `FROZEN_CONTRACT.json`의 입력 representation과 식–함수 대응을 lower-tier 구현자에게 전달했다. 구현은 새 폴더에만 추가한다. 원전의 raw CCC momentum-interchange pair, already-coherent density, already-spin-weighted density, phase-missing intensities를 구분한다. raw pair의 상대 위상은 새로 만들지 않는다. TP Table I 8개 published4CCC 값의 정규화 보존과 BRM 대비 산술 ratio가 실제 source 입력 검증이다. 제조된 complex controls는 구현 oracle에만 사용한다.

R10: 이론 결과와 코딩 계약은 인계 완료다. 코딩 실행·C9·Git 게시·이중 백업은 각 실제 응답으로 단계 상태를 갱신한다. 새로운 전체 joint payload, finite-mass dynamics, 전 domain/count/frame/recoil/uncertainty 의무는 `HE-ANG-SOURCE-PAYLOAD`에 남는다. 이번 조건부 adapter의 완료를 physical source admission으로 바꾸지 않는다.

## 판정 규칙

- Theory: DERIVED + independently reviewed, current blocker0.
- New implementation: actual results와 C9 전까지 PENDING.
- Parent HE-ANG: SOURCE_INPUT_PENDING.
- New strong no-go: NOT_CLAIMED; NG1–NG7 신규 배제정리 admission은 수행하지 않는다. 원전 부호 교정과 실수 대수항등식의 신규성은 주장하지 않는다.
- DDCS20·HE-X1·HE-ANG-CONTRACT·HE38·Hex: identity-matched evidence reused, old suite runs0.
- Publication: source base c8f5818c61d14872837abf7e9bc1a73c670ae25c 위의 additive draft branch. C9 뒤 actual expected SHA, force=false. Merge/activation0.
- Preservation: 이전 비용·실패·unknown은 immutable references로 유지. 새 CPU8/wall30은 실제 새 source-convention kernel의 allocation이며 이전 allowance의 reset/transfer가 아니다.

## 다음 유효 행동

R6가 닫혔으므로 implementation 준비 B1 checkpoint를 양쪽 provider에 보존하고, 계획된 tests → actual table analysis → plot의 세 child를 실행한다. 오류는 raw output과 누적비용을 보존하고 한 개의 진단된 repair reserve 안에서 root가 승인한 수정에만 사용한다. 최종 C9는 같은 독립 reviewer가 실제 diff/출력/그림을 평가한다. source payload가 도착하면 그 source에 맞는 별도 수치 예산·지원 범위를 동결하고 다음 물리 admission을 진행한다.
