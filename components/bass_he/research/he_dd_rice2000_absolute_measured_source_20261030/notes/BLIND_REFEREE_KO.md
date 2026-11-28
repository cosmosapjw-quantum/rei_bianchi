# Blind referee | PR125 Rice measured-source contract

`MODE=ADVERSARIAL_SERIAL_SAME_AUTHOR; NATIVE_DISTINCT_AUTHOR_SUBAGENT=NOT_RUN`. 모델이 자기 연구물을 심사했으며 독립 인물의 peer review라고 주장하지 않는다. 실제 업로드 논문 PDF 표/그림을 직접 대조했다.

| Object | Adversarial countercheck | Finding / treatment |
|---|---|---|
| Source Rice 2000 Table I | 원문 PDF 페이지 4의 12 수치-오차-각도 배열, SHA256 및 재생성 | PASS 12/12, 직접 published 값 |
| Source Rice 2000 Table II | 동일 사건 총단면적 `2π A0` | **FAIL_SCOPED_AUTHOR_TABLE** 150–190 unconstrained P2 row A0=1.31 vs sigma=8.32; 원문 그대로 보존 |
| Error budget Table II | Source 7.1% / 13% systematic vs 각 fit 줄 | 위 한 행 0.65 nb vs 0.59072 nb, 원전 보고 문제 보존 |
| Thesis/Table conflict | Rice 1998 Table 5.1 6점과 Rice 2000 동일 실험의 6점 | 출판값/논문 이전값 약 1.206–1.213 비율, 독립 실험 아님 |
| Thesis original completeness | 첨부 PDF 139장, last page Fig.5.4 | Table 5.2가 없는 불완전 판본; 본문 3.6, 5.1은 활용 가능 |
| Supplied EXFOR zip | ZIP 내부 REQUEST 8587001 | M0826/Arkatov, Rice 2000이 아님, 새 Rice 자료 count 금지 |
| Identical-particle factor | Paper Section IV 직접 `sigma_tot=2π A0` | Rice reported DA는 이미 반구 사건 총단면적 규약에 결속, 4π 중복 적분 금지 |
| Time reversal ratio | spin 9 vs photon2, k/q phase space, PR107 문서의 ratio 방향 | `(cap/photo^ord)=(2/9)(k/q)^2`; 역수 라벨 주의 |
| Energy bin | Source 150–190 / 190–250, finite reconstructed energy | 170/220 MeV 실측점이나 direct beam rate로 변경 금지; 동일 비음수 source-energy weight 가정에서만 interval bounds |
| Nuclear source vs astrophysical rate | photon flux history, medium, stopping absent | rate and heat strictly null; production HOLD |

Exit: `BLIND_REFEREE_SCOPED_COMPLETE_WITH_AUTHOR_SOURCE_DISCREPANCY`, separate author R06/C09 `NOT_RUN`, no merge authorization. 다음 가능한 실제 물리 과제는 원본 radiation source proper-He-frame MeV spectrum 및 D_fast stopping에 대한 source-owned coupling이다.
