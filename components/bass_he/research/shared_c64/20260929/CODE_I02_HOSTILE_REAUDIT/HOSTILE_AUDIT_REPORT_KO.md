# CODE-I02 적대적 재감사: repaired ac04d2a9

기준: 2026-09-28 UTC, 2026-09-29 KST. 판정: HOLD.
이 문서는 동일 작성 대화 맥락에서 수행한 source-first 적대적 재감사다. 완전 blind 또는 별도 independent decision review가 아니다. 기존 판정과 isolated 18-test 기록은 이번 PASS 근거로 사용하지 않았다.

## 실행 대상과 접근 복구

PR #15 HEAD ac04d2a9e62120a0da4377ddf92451fde0c44431, tree 5697bfb7b2ceae5854499a8132b44e573672df85를 GitHub에서 fresh-read했다. PR #17의 게시 전 HEAD는 89c8ad1986a98f3677a5a90735f975d255a45aa9다. PR 설명 body에는 오래된 HEAD와 재실행 요구가 남아 있으므로 현재 ref와 source-bound evidence가 우선한다.

컨테이너의 github.com DNS는 실제로 실패했다. 그러나 현재 Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2는 사용 가능했다. Google Drive의 기존 R1 archive를 가져와 SHA256 b70fbd51736d6e3004c27793cb1c47e50878fc72bad090de83e2a57aa94522a2 및 ZIP CRC를 확인했다. 그 dependency_snapshot의 실제 package source에 이미 게시된 변경만 재구성한 뒤, 실행 전에 전체 src subtree를 GitHub hash와 비교했다.

- 전체 src subtree: fb9344caec799308f995aee67a231890f602e16d, 정확히 일치.
- src 파일 27개. validator만 따로 복사한 reproducer가 아니다.
- spectral.py blob: cad7901342cf7003e55e40dcff2202486fb8a223.
- sturm_geometry.py blob: a9b09af1ffd165c7fc03a2e100bb0a0dfe84c580.
- 원래 focused test blob: ea7e768b6a15815a083787d459ab130ebc6bb40d.

이것은 source-tree-verified snapshot이다. 전체 Git checkout, wheel-install verification 또는 cloud parity를 수행했다고 표현하지 않는다. 자세한 각 파일 identity는 provenance/SOURCE_IDENTITY.json에 있다.

## 실제 테스트

| 검증 | 결과 | 증거 |
|---|---|---|
| 게시된 tests/test_dr11h_certificate_binding.py | 23 passed, exit 0, pytest 1.05 s | evidence/official.log, official.xml |
| 새 적대적 계약 검사 | 54 passed / 10 failed, exit 1, pytest 1.19 s | evidence/hostile.log, hostile.xml |
| 전체 source identity 실행 전/후 | 동일 | provenance/SOURCE_IDENTITY.json, POSTCHECK.json |

새 검사는 실제 find_exceptional_point()에서 얻은 정상 certificate를 deepcopy하여 한 필드씩 바꿨다. 실제 validator와 실제 sturm_geometry.contour_geometry()를 호출했다. 최초 bound_pair 호출만 관찰용 sentinel로 바꿔서 거부 위치를 측정했다. 실패 열 개는 모두 validator ACCEPTED, anchor_calls=1이었다. 잘못된 action을 완성한 증거가 아니라, 잘못된 certificate가 admission 경계를 통과한 증거다.

원래 테스트와 새 테스트가 각각 정상 endpoint fixture를 한 번 생성했다. 56-action replay, 7-branch 재계산, worker sweep, saved R1/R2 analysis, Eq55, cloud job은 실행하지 않았다. 따라서 spectral work가 완전히 0이었다고 주장하지 않는다.

## F01: Important, matching-error 유효성 검사가 fail-open

위치: src/bass_he/spectral.py:84-85.

현재 조건은 float(error) > tolerance일 때만 거부한다. NaN은 이 비교를 거짓으로 만들고, 음수 및 -Infinity 역시 양수 tolerance보다 크지 않다. genuine certificate의 max_scaled_matching_error를 NaN, -Infinity, -1.0, 문자열 'nan'으로 각각 바꾸는 네 공격이 모두 통과했다. endpoint, binding, hash, tolerance는 바꾸지 않았다.

max_scaled_matching_error는 scaled norm의 최댓값이므로 필요한 조건은 단지 error <= tolerance가 아니라 finite(error) AND 0 <= error <= tolerance다. 여기서 구현 검증은 실패했다. NaN/-Infinity는 일반 strict JSON writer에서 거부될 수 있지만 -1.0은 정상 JSON 값이므로 serialization이 이 결함을 일반적으로 막아주지는 않는다.

영향은 certificate decision gate의 유효성이다. 실제 branch misidentification이나 잘못된 cross section이 새로 관측되었다는 뜻은 아니다. 허용오차의 수치값을 바꿀 필요는 없다. 향후 별도 repair에서는 부호/유한성/허용 scalar type을 먼저 검사하고, 이 네 회귀를 유지해야 한다.

## F02: Important, 저장된 binding payload와 checksum 불일치가 통과

위치: src/bass_he/spectral.py:58-61, 80-81.

binding != expected는 Python value equality이고, stored SHA는 expected의 SHA와 비교한다. 그런데 True == 1, 1.0 == 1, 64.0 == 64다. 따라서 certificate.binding의 state_a[0]을 True 또는 1.0으로, depth를 64.0으로 바꾸면 semantic equality 검사를 통과하고 원래 SHA도 expected와 일치한다. 실제 변경된 binding payload를 canonical JSON으로 직렬화한 SHA는 저장된 SHA와 다르다.

실제 재현의 원래 SHA:
79b8a120cdd120d84dc6f4592c5f469df38caca5052c27a99a29d92f7daabedc

state_a[0]=True로 바뀐 binding payload의 실제 SHA:
d4822b4b206dc71f04619bbe56e298182e73420824af9b048d7dd735e53939a6

세 공격 모두 validator와 anchor 경계를 통과했다. 이것은 SHA256 충돌이나 재서명 공격이 아니다. hash를 다시 계산하여 입력에 넣지도 않았다. 현재 endpoint 자체는 여전히 정상 정수이고, earlier lossy endpoint repair를 우회한 사례와 구분한다.

Important 분류는 '저장된 canonical binding payload의 checksum consistency도 검사한다'는 기존 계약 기준이다. 의미론적 equality만 보장하려는 설계라면 이 checksum claim을 명시적으로 축소해야 한다. byte identity, semantic identity, origin authentication은 서로 다르다. 향후 repair는 stored payload 자체의 canonical representation과 digest를 검증한 후 expected identity와 비교해야 한다. 유효한 기존 V2 payload를 반드시 변경해야 한다는 결론은 아니다.

## F03: Minor, passed flag의 truthiness 허용

위치: src/bass_he/spectral.py:65-67.

passed='False', passed='0', passed=1 세 값이 모두 통과했다. Boolean False 자체는 올바르게 거부한다. 이 세 witness는 genuine certificate의 status-field type confusion이지, membership 계산이 실제로 실패한 endpoint를 승인한 실험은 아니다. 따라서 현 증거만으로 Important나 잘못된 물리 결과로 확대하지 않는다. 명시적 boolean success contract로 정리할 필요가 있다.

## 수리가 확인된 범위와 검토에서 제외한 범위

기존 lossy int endpoint 결함은 이번 검사에서 재현되지 않았다. 모든 state 좌표와 depth에 적용한 22개 type/alias 공격, R/p/lambda/Z1/Z2의 one-ULP 변조 5개, 비유한 endpoint 5개, 기존 certificate metadata 공격 17개는 validator 단계에서 거부되었다. 정상 Python 정수, NumPy int64/uint64, 정상 JSON round trip, 정상 permutation 순서 교환의 다섯 control은 anchor에 도달했다.

이 제한된 결과로 모든 임의 입력에 대한 정리를 주장하지 않는다. malicious user-defined numeric class, concurrent mutation race, endpoint와 certificate/hash를 함께 조작한 authenticity 공격은 이번 범위 밖이다. legacy bass_he.geometry.contour_geometry는 opt-in Sturm path와 별도 함수다. 해당 legacy path 전체가 새 validator로 보호된다고 주장하지 않는다.

## 결론과 다음 작업

이번 재감사 분류는 Critical 0, Important 2, Minor 1이다. 원래 endpoint int 수리의 tested scope는 통과했지만 certificate 전체의 fail-closed 계약은 통과하지 못했다. CODE_I02_CLOSED=false, scientific_PROMOTE=HOLD, Eq55_next_node_authorized=false, Eq55=NOT_RUN을 유지한다.

검토 대상 production code와 PR #15는 수정하지 않았다. 실패 테스트는 xfail/skip으로 바꾸지 않았고 expected acceptance로 뒤집지도 않았다. 새로운 결과와 실패 원문을 보존했다. Codex 인계문은 별도 맥락에서 초기 판정을 파일과 SHA로 먼저 고정하고, 그 뒤 이 증거를 공개하는 outcome-blind 2단계 절차다. 실제 독립성은 그 실행 context가 충족하는지 별도로 기록해야 한다.

Codex는 준비된 테스트를 실행하고 독립 판정 및 return evidence를 남기는 역할이다. 발견된 certificate policy/schema 문제를 그 reviewer 자신이 자동 수정하여 승인하는 fix-review 루프는 금지한다. 연구 스레드로 반환한 후 별도 repair node를 열어야 한다.
