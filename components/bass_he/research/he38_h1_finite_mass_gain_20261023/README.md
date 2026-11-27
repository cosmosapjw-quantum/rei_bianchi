# HE38-FMG — H1 이온화의 유한질량 gain과 종별 보존 모멘트

Workflow **1.0.0** / approval **0.2**. 직전 HE37 완료 publication `b97bccaabc246af5672b2ead8dfa9f08d169da6d`를 이어간다. Author: ChatGPT research team.

## 과학 결과

원전 Jacobi 좌표의 유한질량 운동학과 명시적 uniform-G 모형에서 전자·중성 H·양성자의 number/heat/STF source를 유도하고 sandbox component로 구현했다. CommonT/commonbulk Maxwell 기준과 독립적인 무한소 π_e,π_H를 사용한다. 새로운 공유 모멘트는 Λ=β−k_B T α로 압축되어 별도 production 적분이 필요 없다.

**결과의 증거 수준은 explicit-model-conditional이다.** 측정으로 교정된 H1 angular law나 전체 gas closure를 완료한 것이 아니다. 원래 HE32의394완료IVP와 그림6쌍은 재사용하며 이번 새IVP는0이다.

먼저 [RESULTS_KO.md](RESULTS_KO.md), [CONTRACT.json](CONTRACT.json), [DAG.json](DAG.json), [NEXT_DAG.json](NEXT_DAG.json), [RUN_RECORD.json](RUN_RECORD.json)을 읽는다. 전체 수식은 [theory/DERIVATION.md](theory/DERIVATION.md), API와 코드는 [components/finite_mass/README_KO.md](components/finite_mass/README_KO.md)에 있다.

| 완료 근거 | 파일 |
|---|---|
| 최신 변경분 및 source admission | evidence/intake/INTAKE_REPORT_KO.md; SOURCE_QUALIFICATION.json |
| Exact/Wick/Wolfram 유도 검증 | theory/CHECKS.json; WOLFRAM_IDENTITIES.json |
| 새 코드107개 affected controls | components/finite_mass/attempts/ |
| 독립 raw integral4cases | evidence/raw_controls/ORACLE_REPORT_KO.md |
| 새129T 진단과 공유 적분 비용 | components/diagnostic/outputs/ |
| 독립 검토·3지적 종료 | evidence/review/FINAL_REVIEW.json |
| 실제 최종 그림1쌍 | figures/HE38_FMG.png; figures/HE38_FMG.svg |
| 단계별 게시·백업 및 최종 pin | delivery/*_ACK.json; delivery/FINAL_ACK.json; DELIVERY_LEDGER.md |

## 저장 결과만 확인하는 재개

```bash
python research/he38_h1_finite_mass_gain_20261023/verify_saved.py --require-delivery
```

이 명령은 표준 라이브러리로 저장된 hash·행·receipt·DAG만 확인한다. 과학 코드·IVP·benchmark·renderer를 실행하지 않는다. 이번 새 stage/final tar.gz가 로컬에도 있을 때만 `--archives --archive-root /tmp`로 archive payload까지 검사할 수 있다. 복원 확인만을 위해 원 diagnostic·oracle·tests를 재실행하지 않는다.

다음 연구용 handoff는 HANDOFF_KO.md, 실행기용 handoff는 HANDOFF_EXECUTOR.md다. PR은 https://github.com/cosmosapjw-quantum/BASS_HE/pull/91 이며, exact final science pin/archive는 FINAL_ACK, publication pin은 PR head와 외부 final readback에 기록한다. Commit은 자신의 SHA를 자신의 내용에 포함할 수 없으므로 이 권위를 구별한다.
