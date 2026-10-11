# C11 독립 판정

판정은 **PROMOTE_LOCAL_PRODUCTION_PREREQUISITES**다. 범위는 C2·FLRW r=0의 변경된 진입 정밀도, native smooth-support 값 연산, 고정 척도 시간 제어, 실제 macro 경계 cold restart의 국소 선행조건이다. 전체 이력의 과학적 수용은 **HOLD / NOT_EVALUATED**다. 미완성·미실행 full-interval runner를 운영 준비 완료로 판정하지 않는다.

동일 배경식·보간·물리 입력을 유지한 source 연산은 새 5e9 및 2.5e9 s 입력에서 원래 1e-10 order-pair와 1e-12 pairing 기준을 통과했다. 저장된 born-cell 80자리 기준값과 NPZ로 재계산한 10개 상대오차는 보고값과 일치하며 최대 1.49e-15다. N/U가 유일한 authoritative 상태이고 D는 진단값이다.

새 native coordinate 경로의 source별 미분 경계, 감쇠 logsumexp 경계, 양의 측도 Taylor 경계는 일관된다. 실패 cell의 exact q/P 저장값에서 64/128 경계를 독립 재계산했으며, 합계 7.211679232457615e-12가 재현된다. 이를 원래 1e-7 내부에서 차감한다. 명시적 caller source-cap provenance와 정확한 node/mean 물리영역을 요구하며, endpoint·threshold 불명확성은 계속 거부한다. 새 물리 provider나 endpoint Jacobian을 인정한 것이 아니다.

PILOT02는 새 12개 trial map, native RHS 108회, SIGMA 7536회를 실행했다. 이전 완료된 첫 거부 trial은 재실행하지 않았다. 세 macrostep의 여섯 half 경계와 세 atomic checkpoint를 받아들였고 t=4.539815858150909e9 s에서 선언된 macro 예산으로 종료했다. 요청한 1e10 s에는 도달하지 않았다. 저장된 12개 trial 경계의 분율·온도·방사선 cone·고정 원점 ledger를 독립 계산해 위반이 없음을 확인했다. 보고된 accepted energy 잔차 최대는 4.8945e-16, number 잔차 최대는 1.9961e-19다.

실제 C11 restart는 Python -I의 별도 child PID에서 새 native 프로세스를 열고 generation 1→2의 다음 제어 macro만 실행했다. RHS 27회, SIGMA 1884회다. 저장된 uninterrupted 결과와 아홉 checkpoint 배열, 전체 prefix의 R/support, 다음 trial 및 cursor가 byte 또는 exact 비교에서 일치한다. cold harness와 잔여/검증 실행 예산 때문에 metadata 전체의 byte 동일성은 주장하지 않는다.

153개 frozen 파일, PILOT02의 41개 dependency와 as-run Python, cold evidence index 31개 파일, 네 checkpoint manifest에 hash 불일치가 없다. 이 검토자는 후보·테스트·oracle을 작성하지 않았고, simulation이나 기존 완료 테스트를 실행하지 않았다. 동일한 독립 검토 문맥에서 저장 자료의 읽기·산술만 수행했다.

남은 핵심 gate는 full-interval 실행기의 완성·검증, 실제 15.9→4 C2/C3 및 same-grid temporal pair, 각 65/129 집합의 독립 정규화, 9 temporal/24 spectral-angular field와 전체 domain·ledger·geometry 검사다. solver 고정 척도는 공식 분모를 대체하지 않는다. Bianchi와 새 native BASS는 그 이후까지 HOLD다. 이번 결과만으로 장기 비용, 전역 수렴, 임의 시점 restart 또는 remote restore를 인정하지 않는다.

세부 판정과 파일 identity는 INDEPENDENT_DECISION.json, SAVED_EVIDENCE_CHECKS.json, REVIEWED_FILE_HASHES.json에 있다.
