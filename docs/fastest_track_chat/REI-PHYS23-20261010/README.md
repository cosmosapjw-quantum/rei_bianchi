# PHYS23 — Spectral initial response and thermal sign

최종 과학 판정은 PROMOTE_SCOPED, physical admission은 HOLD다. 실제 HI-only 에너지 구간의 HII·heat·50000 K 온도 초기 계수의 음의 부호, 양의 spectrum으로의 부호 전달, inherited numerical Jacobian에 조건부인 HeIII 전환과 같은 N/U의 반례를 기록했다.

- [통합 연구 보고서](PHYS23_REPORT_KO.md)
- [독립 최종 판정](independent/DECISION_REVIEW_KO.md)
- [결과와 근거 상태](RESULTS_SUMMARY.json)
- [Claim DAG](CLAIM_DAG.json)
- [다음 단일 PHYS24 질문](PHYS24_NEXT_HANDOFF_KO.md)
- [완성 archive identity](ARCHIVE_IDENTITY.json)

이 디렉터리는 문서·원 증거·그림의 Git 게시용 투영본이다. 인용한 source snapshot은 문서 근거를 위해 포함했다. 전체 재현에는 완성 묶음 **REI_PHYS23_SPECTRAL_INITIAL_RESPONSE_20261010.zip**을 사용한다. 일부 표시용 grid, PDF, 중복 replay 결과, 루트 wrapper와 full manifest는 이 투영본에서 제외했다. [재현 안내](README_REPRODUCE_KO.md)의 명령은 전체 ZIP을 푼 루트에서 실행한다.

Archive SHA256: ff4231bfcec99a8ea4c6bf83a8cc8172e7503f978f64bfa6642ebd8bdf98835d  
Archive bytes: 555815  
Report SHA256: ae030aa17c34f1eda35b092ade8ea14b5f9e967bbd446db60edfb97b063b353b  
Decision JSON SHA256: 3548db4954ef89846044cd049d5e58b929751a61b0aa3b4723b58688d2d0afe7

Source scientific input commit: e334866a4ac1be963f573c0b35182d25eb4d666b. Scientific Rust src tree: cb69b4736dd046e4675557577eb8e0ead037d1f3. Native0, gas IVP0, closed old scientific suites0, production changes0. 추가되는 새 문서 경로만 게시하며, 기존 source/default/runtime나 기존 docs는 바꾸지 않는다.

정확한 최초 검산은 31/31, 새 수치 검산은 65/65다. 한 번의 별도 portability replay에서 두 결과의 raw bytes까지 일치했다. 완성 ZIP은 새 로컬 디렉터리에서 64개 payload를 verify-only로 확인했다. 이 기록은 full remote restore를 주장하지 않는다. 실제 publication commit·CAS ACK·선택적 remote readback은 완성 ZIP과 함께 전달된 detached PHYS23_PUBLICATION_RECEIPT.json을 따른다.
