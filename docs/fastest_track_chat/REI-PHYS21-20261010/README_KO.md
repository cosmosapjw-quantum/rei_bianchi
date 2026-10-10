# REI-PHYS21 — scalar shear의 2차 응답

PHYS20의 후속 물리 연구다. 일반 continuum 2차 radiation kernel, fixed-q/birth-angle 일치, inverse-cube cumulative absorption 부등식, 순간 흡수·가열 부호 반례, 실제 HI-fit 고정 neutral-fraction 진단, source-bound 선형 Volterra gas response를 완성했다.

별도 독립 판정은 scoped PROMOTE이며 physical=HOLD다. HI 39/39, tensor 44/44, local gas 60/60 검산이 통과했고, 세 진단의 portable replay도 성공했다. 실제 evolving-gas의 finite-time coefficient, native discretization, physical admission은 이번 결과로 닫히지 않는다.

- [주 보고서](PHYS21_REPORT_KO.md)
- [결과와 근거 상태](RESULTS_SUMMARY.json)
- [독립 최종 판정](independent/DECISION_REVIEW_KO.md)
- [다음 PHYS22 handoff](NEXT_HANDOFF_KO.md)
- [Archive identity](ARCHIVE_IDENTITY.json)

## Git projection과 complete ZIP

이 Git 경로는 보고서·코드·JSON 근거·source identity·판정·handoff의 텍스트 projection이다. 전체 ZIP에는 materialized source bytes, figure PNG/PDF, payload manifest 및 reproduce.py가 추가로 있다. 완전한 archive 재현은 ZIP을 푼 뒤 README_REPRODUCE.md를 따른다. 이 projection을 complete ZIP의 root manifest와 혼동하지 않는다.

Complete ZIP: REI_PHYS21_SECOND_ORDER_SCALAR_SHEAR_20261010.zip

SHA256: `345a7449f43bed11e954dd2d36774a69b40c2c3c5cd8b693f22fbc25eeafbf20`

Size: 312483 bytes. Archive는 이 채팅의 다운로드 파일로 제공된다. Fresh local extraction에서 payload55개와 source7개 identity 확인이 통과했으며 remote full restore를 수행했다는 뜻은 아니다.

Source input commit faec51259ed26f660cf14568bcaa3d288e54bf9a, scientific src tree cb69b4736dd046e4675557577eb8e0ead037d1f3. 같은 branch에 새 docs 경로만 추가한다. Source/default/runtime returns는 변경하지 않는다. 기존 [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다.
