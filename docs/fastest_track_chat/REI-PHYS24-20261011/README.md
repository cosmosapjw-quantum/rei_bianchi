# PHYS24 — Fixed-moment HeIII initial-response envelope

**PROMOTE_SCOPED / research PROMOTE / physical admission HOLD.**

[한국어 통합 보고서](PHYS24_REPORT_KO.md) · [최종 독립 판정](independent/DECISION_REVIEW_KO.md) · [기계 판독 결과](RESULTS_SUMMARY.json) · [PHYS25 단일 후속 질문](PHYS25_NEXT_HANDOFF_KO.md)

고정 수치 J, 초기 기체, 양의 광자 수와 I=[13.61,24.58] eV에서 실제 HeIII 초기 응답 커널이 엄격히 볼록함을 정확한 유리수 Bernstein 인증으로 보였다. 평균 m의 정확한 가능 구간은 단색 응답 k(m)과 두 끝점 chord B(m) 사이이며, 내부 평균에서 두 극값 측도는 유일하다. 모든 중간 응답은 두 선 이하로 달성된다. 약 15.43367087–19.55655168 eV에서는 동일 N,U 아래 음·영·양 응답이 모두 가능하다. 경계 소수는 수치 위치이며 물리 입력 오차의 상한이 아니다.

Exact 20/20 및 별도 원식 수치 경로 156/156이 최초 실행에서 통과했다. 별도 최종 reviewer는 후보 생성·검증 설계에 참여하지 않았고 NONBLIND 검토임을 명시했다. 두 새 프로그램의 제한 portability 재생은 결과 바이트까지 같았다. 이는 독립 과학 검증을 추가한 횟수로 세지 않는다.

이 디렉터리는 완성 연구 묶음의 **문서·증거 투영본**이다. 전체 재현에는 `REI_PHYS24_FIXED_MOMENT_HEIII_ENVELOPE_20261011.zip`을 사용한다. ZIP은 692,961 bytes이고 SHA256은 `b883d4cc5e078c649cc33bbac7af0d0b9819038294c7fe5ee840b95a96958f80`이다. [Archive identity](ARCHIVE_IDENTITY.json)에 manifest와 새 로컬 폴더의 verify-only 결과가 있다.

Git 투영에서는 루트 MANIFEST.json과 reproduce.py, 그림 PDF·표시용 JSON, portability의 중복 결과 JSON 두 개를 생략했다. 원 과학 결과·코드·입력·실행 기록·정정 전 문서·판정·PNG는 그대로 게시했다. 하위 manifest와 candidate freeze는 완성 ZIP의 문맥에서 읽는다. [재현 안내](README_REPRODUCE_KO.md)의 명령은 ZIP을 푼 루트에서 실행한다.

Scientific input commit: `6104a9655439b15143933a97b9926e61dfb62b53`. Scientific src tree: `cb69b4736dd046e4675557577eb8e0ead037d1f3`. 기존 [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. 물리 source 승인, finite-time/finite-epsilon 보장, native 동등성으로 확대하지 않는다.

완성 후 원격 ref ACK·tree/blob 대조와 전달 결과는 별도 `PHYS24_PUBLICATION_RECEIPT.json`에 연결한다. PHYS25는 평균 18 eV의 부호 반전 최소 분산 질문만 고정했으며 실행하지 않았다.
