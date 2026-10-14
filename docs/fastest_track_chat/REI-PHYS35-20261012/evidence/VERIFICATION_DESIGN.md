# PHYS35 판별 검증 설계 — 실행 전 고정

## 질문과 경쟁 결과

비교량은 기존 서로 다른 두 수준을 유지한
\(G_\alpha=W_{-,\alpha}(A_-)-W_{+,\alpha}(A_+)\)다.
후보는 \(G_p-G_u>0\), \(<0\), 또는 현재 균일 경계가0을 포함하는 세 경우다.
개별 \(W_p-W_u<0\)로 상대 부호를 정하지 않는다. 아래 한정된 새 계산으로 세 경우를 구별한다.

## 기존 증거와 새 계산의 분리

PHYS33/34의 근 존재·유일성·Peano·도함수 전구간 인증은 입력이다. 전작 source generator는 grid 의미를 확인하는 읽기 전용 자료다. PHYS35는 저장 point/cell 구간의 정확한 유리수 결합만 수행한다. 기존 초월함수 경계를 더 조밀하게 만들거나 과거 main을 재실행하지 않는다. 이전 generic helper를 import하지도 않는다.

Python Fraction의 분자·분모 정수 연산으로 과학 경계를 계산한다. 유한 소수 입력은 문자열로 읽으며 float 및 limit_denominator를 쓰지 않는다. 최종 유리수의 Decimal90 방향 반올림은 출력 표시이며 각 표시가 정확한 끝점을 포함하는지 유리수 비교로 검사한다.

## 판별 의무

| 의무 | 반증 가능한 검사 | 의미와 한계 |
|---|---|---|
| 이전 증거를 정확히 재사용 | full input hash, raw/contract/protocol/decision 상태 및 A·W·J·source const 일치 | identity는 과학적 증명 자체가 아님; 이전 독립 결정에 의존 |
| full tube 유지 | 원래 \(\hat W\pm.25\), \(0\le\delta\le.001\)와 packet supports 정확 일치 | 국소 tube 밖 근은 주장하지 않음 |
| reference slope 유효 | 같은 retained xref의 k,k′, signed D와 양의 D² 사용; reference/path domain 포함 | xref와 정확한 root 또는 reconstructed center를 동일시하지 않음 |
| geometry/smoothing 오차 | \(M_3(d/6+H_c/3)+\mu_2 M_4d^2/4\)의 전구간 유리수 상계 | 계수는 직접 유도, 도함수는 이전 continuous bounds |
| packet k4 포함 | 이전 exact grid 재구성, 닫힌 cell 교집합 전부 선택, 연속 union으로 support 포함 | point samples나 rounded z row를 exact domain으로 취급하지 않음 |
| Peano numerator | 양의 packet k4 bounds에 \(p\)와 \(1-p\)의 affine extrema 사용 | profile family는 지정된 uniform/P4 두 개 |
| 상대 부호 | \([L_+-U_-,U_+-L_-]\)의0 배제 | 겹치면 HOLD_BOUND_OVERLAP, 무단 refinement 없음 |
| 실제 실행 | first1 및 새 경로 archive restore후 replay1; O_EXCL ledger; stdout/stderr/observed exit/tool envelope | replay byte identity는 다른 모델/수학/산술 backend 독립성 증거가 아님 |
| 최종 독립 판정 | 후보·검증설계에 참여하지 않은 /root/joint_decision가 완성 evidence와 freeze 읽기 | 동일 host/model의 NONBLIND role independence; 후보 owner self review와 구별 |

## 계산 한도와 종료

계약의 first1+replay1, per-main wall15s/CPU10s/RSS384MiB를 지킨다.
두 이전 인증서, 64개의 기존 k4 record, packet query4, branch assembly2, joint assembly1, coarse comparison1만 수행한다.
새 kernel/Bernstein/ln/exp/sqrt/jet/root residual/search/quadrature/native/gasIVP/NCP/old main0.
이전 PHYS33/34 ledger는 SPENT 그대로다. 실패 시 원 출력과 역할 marker를 보존한다.
성공하면 독립 판정 이후 같은 branch 새 prefix의 자료 추가와 최종 전달로 닫는다.

## 기술 출처

- Python3.12 Fraction 공식 문서: https://docs.python.org/3.12/library/fractions.html — 유리수 연산 및 문자열 생성자. 조회2026-10-12. 페이지 표제3.12.15와 실제 실행 runtime 버전은 구별한다.
- Python3.12 Decimal 공식 문서: https://docs.python.org/3.12/library/decimal.html — FLOOR/CEILING 출력 표시 semantics. 조회2026-10-12.
- 두 전작의 ROOT_TUBE_PROOF_KO.md, CERTIFICATE_FIRST.json, DECISION_REVIEW.json과 이 작업의 이론기여 파일. 이전 과학 certificate의90digit elementary arithmetic 의미와 동일 backend 검산 한계는 상속한다.

## 실행 전 상태

새 비교 계산0, 최종 독립 판정NOT_RUN. 이 문서의 고정은 계산 성공을 뜻하지 않는다.
