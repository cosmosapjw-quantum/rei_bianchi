# HE-EXP-STATE-04 결과 — 2026-10-27

## 실제 source와 조건부 scalar consumer

공개 EMAA DOI `10.17178/EMAA_HD_Rovibration_805a7aa5`의 CC BY 4.0 원문은 71,451 bytes, SHA256 `feda215f1d75ee85de399903c77e18f62c8e323fe709015215634d6ccc7720b6`이다. 52 local levels, 368 radiative transitions, H+ 충돌 171 rows, 25 native T, 4,275 rate cells를 보존한다. HITRAN Apr2022 DOI `10.1016/j.jqsrt.2021.107949`, 충돌 원전 DOI `10.1063/5.0128598`와 EMAA를 함께 인용한다. EMAA level ID를 WU aggregate ID에 자동 결속하지 않았고 기존 source inventory 104/138/155는 변하지 않았다.

선택 edge는 HD(v=0,j=1)→HD(v=0,j=0)의 H+ 충돌이며 반응성 HD 파괴가 아니다. 원문 1005 K 하향 계수는 `2.48e-10 cm³/s`이고 Δ는 `1.772463922970989e-21 J`이다. 명시적 zero-relative-drift Maxwellian relative collision-energy bath, microscopic reciprocity 및 원문 weight 관례 하에 상향 계수는 `6.547809139557261e-16 m³/s`, 평형 비율은 `2.6402456207892184`다. 상향 계수는 유도값이며 원문 독립 측정값이 아니다. 원문 3005 K는 보존하지만 논문 상한 3000 K와 support 결속 전 `HOLD_SUPPORT_BINDING`이다. 보간·외삽·DCS 추론을 하지 않는다.

`HE_NATIVE_HD_HPLUS_EXPLICIT_LEVEL_EDGE`는 호출자가 제공한 온도와 density로 level count 및 population-derived internal-energy witness를 구한다. 물질 총 kinetic compensation은 witness의 반대이며 종별 분해는 없다. 내부 에너지 독립 RHS는 없고 종별 heat/momentum/stress는 null, birth pool은 `UNASSIGNED`다. 자발복사 A21은 별도 source metadata로서 충돌마다 광자를 방출하지 않는다. 이 named scalar consumer는 전체 물리 consumer 승인이나 종별 열화를 뜻하지 않는다.

## LiH 정오표와 경계

Bennett 2008 DOI `10.1111/j.1365-2966.2008.12586.x`의 교정 27행은 동일 물리 소유자의 2003 원표/fit을 명시적으로 supersede하며 두 값을 합하지 않는다. 원 77 cells, 기존 source와 ledger는 불변이다. 원문 표에서 1000 K는 17.7→3.19, 3000 K는 51.2→1.80 (단위 `10⁻²⁰ cm³/s`)이다. 이번 fit 평가나 covariance 추정은 없으며 <7%는 인쇄 fit 잔차다. LiH/LiD D0 source 불일치와 중성 원자 mass convention은 source 관찰로 보존하고 event mass나 RA branch에 자동 결속하지 않는다.

## 검증과 범위

새 19개 tests를 한 프로세스에서 한 번 실행해 PASS, exit 0, CPU `0.115736379 s`, wall `0.11492365499725565 s`, repair 0이다. CPU 4 s / wall 15 s / 256 MiB / 1 thread cap 안이다. Raw START/FINISH, stderr/stdout, measured ledger, 24 native points와 synthetic examples는 `evidence/validation/`에 있다. 준비·네트워크·모델·IO 비용은 `UNKNOWN_NOT_ZERO`이며 end-to-end cap을 주장하지 않는다.

저장 데이터만 읽은 plot은 한 프로세스 PASS, CPU `3.35712228 s`, wall `3.3577162440051325 s`, 과학 함수 호출 0이다. PNG/SVG와 exact data는 `evidence/plot/`, 직접 시각 판독은 `evidence/PLOT_READ_KO.md`에 있다. 선은 시각적 연결일 뿐 보간이 아니다. 독립 이론 검토는 `evidence/THEORY_REVIEW.json`, 최종 코드·결과 독립 판정은 `evidence/CODE_REVIEW_POST_EXECUTION.json`의 `PASS_BOUNDED_SOURCE_BOUND_STATE_ADAPTER`, blocking 0이다.

정확한 global state/mass binding, differential/branch input, named deposition은 열린 세 dependency다. HE101 C8 `PARTIAL_EXPORT`, 전달 19/20, reserve 0 및 기존 실패·원장은 보존했다. old START와 replay는 0이다. physical provider=false, activation=false, production=NOT_APPROVED, global completion=null, L4=false이며 전체 완료율은 제시하지 않는다.

## 전달과 게시

원격 게시 재시도의 네 번째 `create_tree` 거절은 기존 DRIFT02 75-file 후보에 대한 `user rejected MCP tool call`이다. 사유는 null, STATE04 외부 쓰기 시도는 0이며 대체 경로는 사용하지 않았다. S04 `2addfab8c8975febd69d2c88eecc09afea508fbe`의 source ZIP은 Dropbox와 Drive 업로드 ACK 및 독립 metadata의 ID/size 확인을 마쳤다. 두 원격 사본의 전체 재다운로드 SHA256은 확인하지 않았다. 13-file 중앙 후보는 로컬 metadata-only 독립 검토에 PASS했으며 R10/C10은 partial이다. `delivery/PUBLICATION_BLOCK.json`과 `HANDOFF_KO.md`를 따른다.

Root의 범위 내 수용 판정은 `evidence/SCIENTIFIC_ACCEPTANCE.json`이며 네 번째 거절의 실제 도구 응답은 `delivery/FOURTH_APPROVAL_RESULT.json`에 보존한다.

최종 전달 preflight의 09:58:54–10:01:06 UTC 비원자적 관측에서 central HEAD는 `55202663275cd0607c968129b33de805d06f5d8b`, WU HEAD는 `a49104da1491f20d087ddfafcdf60347aaeca16a`다. Frozen MODEL의 central `5abe0d19`와 WU `4ea08eb`은 그 전 관측이다. Central은 B3h native absorption 관찰을 추가했으므로 장래 별도 후보는 새 HEAD를 기준으로 그 관찰과 다른 노드를 보존해야 한다. WU R5의 pH2/LAMDA 100 K lift는 별도 병렬 작업이며 EMAA H+ 1005 K 및 Bennett 교정 입력을 바꾸지 않는다. `delivery/preflight/PREFLIGHT.json`의 refs는 관측 시점에 한정되며 snapshot 파일 경로는 원 조사 workspace 기준이다. 과학 입력 수정·재실행은 없었다.

마지막 전달 preflight에서 2026-10-27 10:15:04 UTC의 central은 `55202663275cd0607c968129b33de805d06f5d8b`로 동일하고 WU는 `eb59de011f7cc67d465cda8e84b598a5d17251d6`이다. WU R5 S06 별도 checkpoint는 targeted checks/repair 완료와 R8 판정 대기를 보고하지만, 이를 HE 결과로 채택하거나 검증하지 않았다. 상세는 `delivery/FINAL_PREFLIGHT.json`이며 이전 비원자 snapshot은 보존한다.
