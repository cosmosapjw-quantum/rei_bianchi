# D8 delta 독립 검토 — 저장된 late shear reversal bracket

판정: **PASS_SCOPED_PRELIMINARY**. 기존 237개 검토는 재사용했고 새 25-case plane의 signed sample 전이와 4개 bracket만 확인했다. ODE·root solver·보간·benchmark는 모두 0회다.

## 검토 결과

초기 $\Sigma_{F,i}=0.003$, $P_{r,i}=-0.001$에서 아래 네 matter seed가 z̄=4에서 양의 signed shear를 갖고 z̄=2에서 음수가 된다. $S=\sqrt6s/H$를 저장된 s,H로 직접 계산하여 새 JSON/CSV와 대조했다. 평균 redshift는 시간이 흐를수록 감소하므로 earlier sample은 z_upper, later sample은 z_lower다.

| 초기 P_m | 인접 index (0-based) | z̄ open bracket | S(z_upper)>0 | S(z_lower)<0 |
|---:|---:|---:|---:|---:|
| -0.0003 | 135/136 | (2.8729833462, 2.9353050508) | 1.0225221742e-06 | -2.0454133017e-06 |
| -0.0001 | 141/142 | (2.5192408407, 2.5758703349) | 7.5977785757e-07 | -1.8922134430e-06 |
| +0 | 144/145 | (2.3546766722, 2.4086580994) | 8.0142315605e-07 | -1.6697382872e-06 |
| +0.0001 | 147/148 | (2.1978077332, 2.2492649203) | 9.1457581672e-07 | -1.3906997662e-06 |

25개 plane의 저장된 z̄=4→2 sample 전이를 직접 살펴 positive→negative 4개, negative→positive 0개, exact-zero sample 0개를 확인했다. 새 보고서는 이 네 전이를 빠짐없이 포함한다. 각 index가 인접하고 mean-z·signed shear·case axes·source raw hash가 저장된 값과 정확히 일치하며 elapsed proper time도 증가한다. CSV 네 행은 JSON과 동일하다.

## 해석 범위

이 구간은 수치적으로 저장된 연속 궤적을 해석할 때 최소 한 번의 zero crossing을 포함하는 sample bracket이다. 정확한 root 위치, interval 내부의 uniqueness, continuum 해의 엄밀한 오차 enclosure를 주장하지 않는다. 모든 자릿수는 저장된 sample 좌표를 식별하기 위한 것이다. 구간 폭은 약 0.0515–0.0623이며 그보다 작은 event-time 정확도를 부여하지 않는다.

## 작은 provenance 수정

모호한 source_results_commit 필드를 bass_he_compact_results_commit=65cc2af0caeaa4d5ce6aff37d72cf352cf24aaa7 및 rei_published_source_results_commit=3a525e3e16f1ba9393818a800327cc58597fd7b5로 분리했다. 수치는 변하지 않았다. 외부 publication 자체는 parent의 Git 영수증을 따르며 이 delta reviewer는 해당 외부 상태를 새로 조회하지 않았다.

## 실제 읽은 파일

- `/workspace/scratch/39bb8df06b79/repos/BASS_HE/research/he30_z2_continuation_20261021/src/late_reversal_brackets.py` — SHA256 `5ebbb3cc6bf923c0109d051de6d5e025385d7d4765de283045c328d5b92675ba`
- `/workspace/scratch/39bb8df06b79/repos/BASS_HE/research/he30_z2_continuation_20261021/results/LATE_REVERSAL_BRACKETS.json` — SHA256 `b74d954485fe225db8d4f549d7efe1f518f8e24964a7030e6d02e05374d26c18`
- `/workspace/scratch/39bb8df06b79/repos/BASS_HE/research/he30_z2_continuation_20261021/results/late_reversal_brackets.csv` — SHA256 `45a83238f2be264984297433c9276d635df2b0ac1e213870c4f50bc1b1e8a5be`
- `/workspace/scratch/39bb8df06b79/repos/BASS_HE/research/he30_z2_continuation_20261021/results/CATALOG.json` — SHA256 `434b86965887b104ee88ec518f2de96b4d57ea44f1b1af2b0813909b86afbbd1`
- `/workspace/scratch/39bb8df06b79/repos/BASS_HE/research/he30_z2_continuation_20261021/results/histories.npz` — SHA256 `d4258bc58948b318df2b9d5ea7ceca6258eac62147aececc6ec10068987b6c6c`
- `/workspace/scratch/39bb8df06b79/investigation/physics/D8_BRACKET_DATA_READBACK.json` — SHA256 `1e42ca65f2d812c26110823e05b84161ab8b9dce5fa9eaa9e70d862b12c08dc1`
- `/workspace/scratch/39bb8df06b79/investigation/physics/INDEPENDENT_RESULT_REVIEW.json` — SHA256 `391abdab37ffed3ae0a0b02a347574cde184743629a1fed1471db426ef69bd65`

최종 기계 판정과 각 case 검토 결과는 `D8_INDEPENDENT_REVIEW.json`, data-only readback은 `D8_BRACKET_DATA_READBACK.json`에 있다. 현재 delta에 blocking finding은 없다.
