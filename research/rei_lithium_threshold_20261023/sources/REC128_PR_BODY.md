## 결과와 목적

ANGULAR01의 다음 의무였던 source-owned line number/energy와 escaped angular injection을 **조건을 명시한 detached effective line** 범위에서 닫았습니다. 기존 Einstein source class와 ANGULAR01 B,Q를 재사용해 보존 장부를 연결했고, 고정 배경의 optically thick population 갱신을 시간 적분 대신 정확한 local map과 단조 대수근으로 계산합니다.

**최종 HEAD 6d32330e7f45e7caa9840c558547880b7d28a069** · branch `research/rec-line-source-20261023` · parent PR127 `5185c396b7e07076565ca2f5044a5ccd193e6ee1`.
**80개 Git raw blob 동일성 PASS**, 누락/추가/불일치0.

## 물리와 구현

- Pinned native complete scalar snapshot1개(z≈1100)에서 xr2p departure를 실제 population으로 복원하고, Dfplus distortion과 total Planck/stimulated occupation을 구분합니다.
- Primary는 statistical1:2 fine populations/common profile·energy·fplus를 명시한 g3 coincident-line model입니다. NIST g1/g2 fine cards는 별도 유지합니다. 실제 overlapping doublet나 native compressed-source parity를 주장하지 않습니다.
- R=A D B, radiation energy=E R, atomic internal energy=−E R, radiation PSTF injection=E A D Q. Recoil-free bound–bound thermal/ionic/electron yield는0입니다.
- Thick drift에서 A가 소거되며 W0/log-root 해가 있습니다. 초기값부터 평형까지의 whole-path opacity gate, finite-opacity trajectory bracket, 별도 tensor-packet bound를 증명했습니다.
- `standalone_detached` guard는 동일 native line owner와의 중복 합산을 거부합니다. Canonical residual/JVP/feedback/diffusion owner 교체는 다음 leaf입니다.

## 유한 결과와 원FAIL 보존

고유 source36, local-map27, direct Einstein/angular6, finite-opacity separable reference2, invalid-input18, 그림용3×81=243 analytic samples.
**704 PASS = 기존616재사용 + 새88; FAIL0**. Cosmological/local IVP0, native runtime0, 완료campaign replay0.

원 attempt001은 성공source36/map25 후 native ω1의 binary64 bracket collapse로 중단됐습니다. 원코드·FAIL·traceback·raw·manifest를 그대로 보존했고 nextafter1ULP outward bracket4줄만 수리했습니다. 식/tolerance변경0. 성공prefix재실행0; 미완료map2와 후속미실행block만 continuation에서 생성했습니다.

새 independent review **1pass**, off-grid6/6 PASS, 실제PNG3개 확인, **PASS_AFTER_TARGETED_REPAIR / 열린지적0**.
W0 endpoint 절대차≤3.34e−17, direct phase/gross≤6.52e−16, B상대차≤2.11e−15, Q_F/B≤7.37e−14. 두 finite reference의 analytic bracket 이탈0.
단위/physical assumptions/오차종류의 정확한 범위는 FROZEN_CONTRACT, THEORY, REPORT_KO, REVIEW_KO에 있습니다.

## 단계별 게시·백업

| 단계 | Commit | ZIP / payload | 보존 확인 |
|---|---|---|---|
| A source/theory | b5e330c6918daea256ea0634ad92bd142d5510ae | 90137f3e70c1…, 136234B /22 | Dropbox+Drive ACK·size |
| B code/results | e1e3e6cfe76ffbbd788609e33b6914508f179bb0 | 468065fd119f…, 344262B /63 | Dropbox+Drive ACK·size |
| C review/plots/handoff | 6d32330e7f45e7caa9840c558547880b7d28a069 | 6f4f814675f7b7d3491aaf3bd266223814f0fabebc108e68f572bd534b5a931c, 1910886B /135 | Git80 identity, Dropbox whole-byte/CRC/all135payload PASS; Drive ACK·size |

Final: **REC_LINE01_FINAL_6f4f814675f7.zip**.
Dropbox `id:BSpOijBcT10AAAAAAD_v4g`, path `/bianchi/rec_bianchi/20261016/REC_LINE01_FINAL_6f4f814675f7.zip`.
Drive [final archive](https://drive.google.com/file/d/1jEr6SO2cHFkROPi8UEgfbznLBtTYGSGU/view).
Drive whole-byte readback **NOT_RUN**. 최종 ZIP의135payload=Git80+post-publication2+owner-intake48+이전stageZIP2+deliverytools3. Manifest는 별도1entry.
최종 archive는 작성 후 얻는 provider receipt를 자기 내부에 소급 포함하지 않습니다. 최종 영수증은 아래 반환 댓글과 별도 파일에 보존합니다.

## DAG와 다음 재개

이번 이론R1–R10/코딩C1–C10 단위와 A/B/C전달을 완료했습니다. GLOBAL_DAG의 LINE_MAP은 scoped complete입니다.
다음 **LINE_NATIVE_OWNER**: 같은 저장상태에서 native Lyα real diagonal/feedback/diffusion/Tvv 소유권을 분해하고 독점적 replacement 계약 → residual/JVP/number-energy adapter 순서로 진행합니다. 완료행·전체history를 다시 돌리지 않습니다.
Li ionic yield=MISSING_EXACT_INPUT, actual-field backreaction 및 physical daughter/electron/neutrino/recoil/stopping inputs는 열려 있습니다. PR220 compact33은 이후 결합의 재사용후보입니다.

**Physical HOLD / REC U5 HOLD_9_FAIL/HOLD_8_FAIL / CLOSED_HOLD_NOT_RESET / global convergence NOT_RUN / production NOT_APPROVED / REI_activation=false** 유지.
REC119의126, REI220의129, warm729, THERM02별도8IVP, ANGULAR01의405를 이 연구와 합산하지 않습니다. REI 첫실패 raw historical local-only 범위도 유지합니다.
조건부21population/유효line을 모든핵종 완전핵망·완전열역학·전체Bianchi 재결합폐쇄로 표현하지 않습니다. Draft 유지, merge/activation 없음.

복사 가능한 다음 스레드 지시는 HANDOFF_KO.md와 archive의 delivery/FINAL_HANDOFF_KO.md에 있습니다.
