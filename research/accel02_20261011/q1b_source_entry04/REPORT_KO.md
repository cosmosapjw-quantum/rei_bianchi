# Source-entry fixed-bath 후속 결과

독립 Astra 판정은 `PASS_SOURCE_ENTRY_FIXED_BATH_SCOPED`이다. 실제 HM12 emissivity로 첫 dormant cell에 광자를 생성하고, 기존 N/U를 보존하는 양성 node fitting 및 고정 기체 흡수를 실행했다. 233개 검사 PASS, 추가 재시도 없음. 기존 실패와 입력은 변경하지 않았다.

동일 종료시간의 1/2/4 분할 차이는 주입 총량 기준으로 최대 1.25e-9, 5.20e-10이다. 이것은 개별 흡수 채널의 상대 수렴을 의미하지 않는다. HI/HeI 흡수량과 열 자체의 상대 변화는 약 60%에서 33%로 남아 있다. 실제 interval에는 내부 event가 없으므로 event-crossing 경로도 미검증이다.

이번 실행은 native 1회, SIGMA 28회/2688 energies, source evaluation 464회, 실제 substep 7회 및 제조 grey substep 112회였다. Wall 1.1226273049833253 s, CPU 1.081874 s. 미계측 overhead는 UNKNOWN_NOT_ZERO이다. owner 승인 controller 직접 실행을 기록하며, 요청된 tier와 관측된 runtime 모델을 혼동하지 않는다.

다음 노드는 radiation work와 gas work의 소유권 분리 및 gas-direction absorption derivative 검사다. gas solve, 장기 history, CR/RCT/HH ON 및 global scientific admission은 여전히 HOLD이다. 백업·additive 게시만 별도로 승인되었으며 게시 자체는 과학 범위를 확장하지 않는다.
