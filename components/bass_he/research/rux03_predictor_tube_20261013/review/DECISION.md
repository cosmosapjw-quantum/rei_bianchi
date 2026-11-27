# 독립 최종 판정 — THEORY07

**판정: PROMOTE_SCOPED_THEORY.** HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07의 C07-1–C07-6을 아래 가정과 범위에서 채택한다. 현재 단위의 미해결 material finding은 0건이며, 추가 저자 교정은 요구하지 않는다.

검토자: /root/dropbox_checkpoint. 검토자는 후보 증명·과학 코드·수용기준을 작성하지 않았고 후보 파일도 수정하지 않았다. 원전 해석, 유도와 실제 입력·원응답의 대조, 파일·JSON 메타데이터 확인을 수행했다. **검토자의 새 과학 실행, native/RHS/stage/ODE 실행, 원격 변경은 모두 0회**다.

## 1. 최종 후보와 검토 시점

| 항목 | 실제 확인값 |
|---|---|
| 최종 후보 | dossier/CANDIDATE_MANIFEST.json, revision 2 |
| Manifest 크기 | 8,153 bytes |
| Manifest SHA256 | eea91e03d3f1c042f5f85040788e8c9e7a136c134f36fa63e8a161d9c73922bd |
| 검토 입력 집합 | 39 files, 350,186 payload bytes |
| 파일 identity 불일치 | 0 |
| 최초 formal identity 확인 | 2026-10-13 01:25:34.581017 UTC |
| v2 identity·delta 확인 | 2026-10-13 01:32:34.705741 UTC |
| 과학 판정 기록 | 2026-10-13 01:35:36 UTC |

기존 INTERIM_R6_TUBE 검토를 재사용했고, 당시 출력 범위 밖이던 anchor 설명과 새 family/xAct/report/coding 자료까지 읽어 최종 검토를 닫았다. v2는 기존 문서 3개와 새 revision 기록 1개를 포함한다. 나머지 35개 입력은 v1과 동일하며, 실제 과학 코드·입력·원응답·결과 및 수용기준은 바뀌지 않았다. Manifest의 author_files는 검토 입력 집합의 필드명이다. 그 안의 문헌·중간 검토 자료 4개는 검토자 소유이며 후보 과학 저작 참여를 뜻하지 않는다.

출처 기준은 부모 BASS_HE PR34, commit 3932669f7904f7f68f2f07dced4cf1da9d472480 및 rei PR114, commit a5c958c414dea41216b445c05f58df837f05cacb이다. 이전에 채택된 source/rate/primitive 근거는 고정 identity로 재사용했다. 개별 입력·실행·최종 문서의 정확한 hash binding은 DECISION.json과 위 manifest에 있다.

## 2. 개별 주장 판정

| 주장 | 판정과 채택 범위 |
|---|---|
| C07-1 | **ADOPT_SCOPED.** 고정 anchor의 CI/RR/두 DR kinetic 계수와 12개 활성 Verner 셀의 유리수 enclosure, 제거된 photon denominator를 유지하는 7성분 predictor를 채택한다. \(0\le h\le10^9\,{\rm s}\), 각 고정 \(\mu\in[10^9,1.5\,10^9]\,{\rm eV/H}\)에서 predictor 근사로 인한 displacement defect 상계는 \(7.84285288\,10^{-17}\)이다. 횡방향 parity는 anchor에서의 성질이며 off-anchor 7성분을 제거하지 않는다. |
| C07-2 | **ADOPT_SCOPED.** 모든 \(\|\xi\|_\infty\le0.01\)에 대해 두 구간 \([0,5\,10^8]\), \([5\,10^8,10^9]\,{\rm s}\)의 물리 영역 내 predictor tube와 같은 predictor를 통한 endpoint nesting을 채택한다. 고정 chemical 3×3 행렬은 preconditioner이며 실제 전체 Jacobian을 대체하지 않는다. 검산은 full 7-row norm 상계를 사용하고 entrywise 7×7 enclosure를 주장하지 않는다. |
| C07-3 | **ADOPT_SCOPED.** Tube에서 존재하는 root, \(Q=[-1,1]^7\) 전체에서의 유일성, 각 고정 \(\mu\)의 \((h,\xi)\)에 대한 \(C^1\) family, 정량 predictor/corrector 오차 부등식을 채택한다. Cube 유일성에는 별도의 cube self-map을 가정하지 않는다. 10회 exact corrector에 관한 오차 결론은 정리이며 실제 corrector 실행 횟수는 0이다. |
| C07-4 | **ADOPT_SCOPED.** 고정 chart와 고정 nongas 입력에서 \(F=X-\xi-hG_h(X)\), \(D_\xi X=F_X^{-1}\), increment 민감도 및 유한 old-state/trial residual 오차 상계를 채택한다. Photon old input, 밀도, tetrad 등의 변화는 이 gas-only \(\xi\) family에 포함되지 않는다. 혼합 미분 항등식은 해당 analytic cell에서 유효하고 새 수치 Hessian 상계를 뜻하지 않는다. |
| C07-5 | **ADOPT_SCOPED.** 정확한 affine reanchoring, moving old-state center, 필요한 \(DP\) 항, Jacobian/corrector의 conjugacy 및 정량 조건수·미분 상계를 채택한다. Self-map은 실제 affine image와 pullback norm으로 옮긴다. 그 image를 감싸는 axis-aligned box의 domain enclosure는 자동으로 보장되지 않는다. |
| C07-6 | **ADOPT_SCOPED.** 고정 Eulerian normal과 정규화된 common gas/anchor fourvelocity 아래에서 에너지 투영의 anchor 변분, 혼합 변분, projector 및 photo/escape 부호 항등식을 채택한다. Moving anchor에서는 추가 \(-p\,\delta\gamma\) 항이 필요하다. 국소 tensor 항등식의 판정이며 all-Bianchi나 relative-species-tilt 결과를 추가하지 않는다. |

가정은 고정 Eulerian lab volume/tetrad, \(D=10^{-3}\,{\rm cm}^{-3}\), 선언된 EOS·Case A closure, 6개의 고정 old photon inventory와 source-defined full warm CI/RR/DR/photo source다. CR/RCT/HH는 꺼져 있다. 검산은 선언된 real-decimal 함수에 대한 exact 식과 유리수 상계다. Native 부동소수점 함수 자체의 enclosure, 실제 암시적 stage 구현, 시간 적분 정확도는 이 판정에 포함되지 않는다.

## 3. 정량 결과와 실제 실행 근거

두 tube의 contraction 상계는 각각 0.023012093111과 0.046670186416이고, 최소 strict self-map 여유는 약 0.01032621961478과 0.0601894501334다. 물리 cube 여유는 각각 0.57과 0.12다. 전체 cube의 Lipschitz contraction 상계는 0.045092412438이다. 서로 다른 corrector, cube source map 및 변환된 source map의 상계를 구분한 서술이 맞다.

\(H=10^9\,{\rm s}\)에서 \(HB=1.6060877754793128>1\)이므로 부모의 원래 충분 self-map 조건 \(hB\le1\)을 넘어선 양의 구간을 인증했다. 이 비교는 이전 충분조건의 한계를 넘는다는 뜻이며 물리적 최대 step, fold 위치 또는 그 이후 root 부재를 증명하지 않는다.

| 실제 evaluator batch | Named group | 결과 |
|---|---:|---|
| Anchor rate/predictor | 10 | 전부 PASS |
| Tube certificate | 14 | 전부 PASS |
| Family variations | 12 | 전부 PASS |
| xAct reanchor variations | 9 | 전부 PASS |

실제 과학 evaluator는 4 calls, 45 named groups다. 이는 6개 주장 family를 뒷받침하는 검사 묶음이다. 내부 power/exp witness, 성분별 부등식, family zero/boolean 항목과 xAct tensor zero 12개를 다시 더해 정리 수를 늘리지 않는다. 검토자는 이를 재실행하지 않고 보존된 실제 call code와 입력 파일, 원응답과 정규화 결과를 대조했다.

네 과학 원응답은 전부 수신된 JSON으로 해독되며, exact rational 문자열과 check flag가 보존돼 있다. Tube에 내장된 부모·anchor 값도 해당 고정 결과와 일치한다. xAct wrapper의 실제 body는 보존된 WL과 같고 package identity도 묶여 있다. Package load 중의 backend 메시지와 body에서 명시한 backend 설정을 구분했다.

## 4. 닫힌 검토 지적

- **Anchor error cap:** cap을 임의로 \(H_2\)로 나눈 것이 아니다. 실제 WL은 전체 구간의 source error에서 \(H_2\) 배 displacement enclosure를 만들고, 바깥쪽 유리수 반올림을 직접 확인한다. 따라서 cap/\(H_2\)의 uniform 사용 근거가 있다.
- **변환과 연결 범위:** 실제 affine image의 self-map, 같은 \(\xi\)·같은 predictor의 tube joining, 고정 chart의 민감도 가정이 구분돼 있다. Gas-only family를 여러 stage의 history로 확대하지 않았다.
- **표시값과 엄밀한 중심:** v2 REPORT 식 (35)는 근삿값 표기로, 식 (36)은 정확한 저장 predictor 성분으로 바뀌었다. 네 개 display-only JSON 숫자의 raw/normalized 표기 차이는 EXECUTION_RECORD에 기록돼 있고 CAPTURE의 설명도 그 범위로 한정됐다. Exact bound와 판정 기준에는 변화가 없다.
- **보존 문서와 문헌 표기:** 부모 문서의 단위 표시 잔여 5곳은 display erratum으로 한정해 기록했고 부모 과학 파일을 수정하지 않았다. Sarah Day 및 절 기호도 교정됐다. 새 whole-paper read나 표준 contraction 정리의 신규성을 주장하지 않는다.

**열린 material finding: 0. 현재 THEORY07의 미완료 과학 의무: 0.**

## 5. 후속 범위와 인계

다음 이론 단위는 **HERE_RUX03_JOINT_INPUT_AND_TWO_STAGE_ENCLOSURE_08**이다. Joint gas/photon old-input family, photon-input/output 민감도와 실제 첫 stage output의 다음 stage input domain 포함관계를 구성해야 한다. 현재의 gas-only 반경 0.01과 첫 predictor 이동량을 고려하면 reanchoring만으로 두 stage domain 포함관계를 주장할 수 없다. 이 후속 의무를 THEORY07의 완료 조건으로 소급하지 않는다.

다음 native owner는 계속 pending이다.

1. HERE_RUX03_PRIMARY_PROVIDER_03
2. HERE_RUX03_COVARIANT_MOMENTS_04
3. HERE_RUX03_MOVING_GAS_STAGE_05
4. HERE_RUX03_CONTINUATION_CERTIFICATE_ADAPTER_06

원래 DAG **RUX02 + global RUX03 → RUX04 → RUX05**와 owner 상태는 유지한다. 별도 all-Bianchi·abundance-source·reference-current·class-B·relative-species-tilt D2.3 의무도 그대로다. Global RUX03 완료, strong no-go, 보편적 신규성, 다중 stage history 또는 temporal accuracy를 채택하지 않는다.

저자는 이 39개 과학 입력을 바꾸지 않는 closeout, 최종 science manifest 및 게시·전달 기록을 추가할 수 있다. 실제 원격 게시와 백업의 완료 기록은 저자에게 인계한다.
