# Decision log

## Intake

PHYS19의 명시적 successor를 따른다. Repository의 다른 Einstein/HM12 또는 precision-atomic lane과 섞지 않고, prescribed constant-H FT03의 directional response를 연구 질문으로 고정했다. 실제 source를 16개 파일의 commit/blob/SHA256에 결속했다.

## 연구 중 결정

1. Photon count의 fixed-q measure를 먼저 고정했다. Per-emitted-photon kernel과 현재 입체각당 kernel에 같은 이름을 붙여 부호를 섞지 않았다.
2. 실제 midpoint rule을 읽고 second/fourth moments를 직접 유도했다. 현재 xy null을 임의 STF에 확장하는 가설을 반례로 기각했다.
3. Scalar cancellation은 differentiability·uniqueness·isotropic epsilon-independent input 조건부 정리로 남겼다. Threshold cusp를 별도 음성 대조로 보존했다.
4. Numeric probe는 초기 neutral fraction 고정과 density dilution이라는 범위를 명시했다. 실제 evolving gas 해로 해석하지 않았다.
5. Decimal 초기화 수정 전 v1과 reviewer 환경 실패를 원 evidence로 보존했다. 새 방식의 실제 성공 실행을 별도 기록했다.

## 최종 독립 결정

후보/검증 설계에 참여하지 않은 `/root/decision_review`가 frozen report를 검토하고, 독립 Decimal70/Simpson 계산 23/23 통과 evidence와 함께 **PROMOTE**를 결정했다. Owner가 reviewer 판정을 대리 생성하지 않았다.

C01–C06은 각각의 조건과 claim ceiling 아래 다음 이론 단계의 입력으로 승격한다. C07(full coupled gas/physical admission)은 HOLD다. Fatal findings는 없다. 이미 닫힌 검산·리뷰를 반복하지 않고 PHYS20을 닫는다.

다음 노드는 **PHYS21_SECOND_ORDER_SCALAR_SHEAR_RESPONSE**다. 다음 목표·실행 범위·stop condition은 `NEXT_HANDOFF_KO.md`에 고정했다.
