# REI-PHYS22 — Initial-time coupled shear response

실제 paired 초기 기체에서 HII와 온도의 약한 shear 응답은 t³부터 음수, HeII는 t⁴에서 음수, HeIII는 t⁴에서 양수로 시작한다. 연속 birth의 특정해는 각각 한 차수 늦게 시작한다.

통합 결과는 [PHYS22_REPORT_KO.md](PHYS22_REPORT_KO.md), 판정은 [independent/DECISION_REVIEW_KO.md](independent/DECISION_REVIEW_KO.md), 다음 문제는 [NEXT_HANDOFF_KO.md](NEXT_HANDOFF_KO.md)다. 별도 최종 판정은 PROMOTE_SCOPED이며 physical admission은 HOLD다.

이 경로는 기존 파일을 변경하지 않는 additive docs projection이다. 보고서, 실제 원시 결과, 코드, 수정 전 문서, 독립 판정과 PNG 그림을 포함한다. 완전한 standalone reproduction에는 ARCHIVE_IDENTITY.json이 식별하는 ZIP을 사용한다. 그 ZIP에는 정확한 pinned source snapshots, root payload manifest, reproduce.py와 PDF 그림도 들어 있다. 이 projection에서 full archive verifier를 실행했다고 주장하지 않는다.

최초 새 계산: radiation 52/52, gas 11/11, owner 21/21, 교차 비교 16/16 PASS. 별도 portability replay와 fresh local ZIP restore는 독립적인 추가 물리 검산으로 합산하지 않는다. 유한시간 history/remainder와 native arithmetic equivalence는 주장하지 않는다.

Scientific source tree cb69b4736dd046e4675557577eb8e0ead037d1f3, physical HOLD, [160,161] FAIL/tick160/auxiliary FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. Actual publication ACK는 별도 receipt에 기록한다.
