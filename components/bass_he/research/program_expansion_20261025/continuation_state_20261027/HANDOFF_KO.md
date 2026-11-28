# HE-EXP-STATE-04 인계

`MODEL_CONTRACT.json`, `THEORY_KO.md`, `src/state_edge.py`, `RESULT.json`, `RESULTS_KO.md`와 raw validation/plot 기록이 이 단위의 기준이다. 승인된 범위는 한 native HD–H+ state edge와 explicit Maxwellian relative-energy closure, named scalar population/internal-energy consumer 및 Bennett 2008 correction selection이다. 전체 differential 물리 공급자 승인이 아니다.

EMAA 원문은 `sources/HD.Rovibration.805a7aa5.radex`에 있으며 CC BY 4.0 원전·EMAA·HITRAN·충돌 논문을 인용해야 한다. 3005 K 원문점은 support binding 전 HOLD다. 52 local level ID를 기존 WU species에 자동 연결하지 않는다. LiH 정오표는 2003 원표를 현재 소비에서 supersede하며 합산하지 않는다. D0 isotope 관찰 및 modern atomic mass를 RA final state나 event mass에 자동 적용하지 않는다.

19 tests는 1 process PASS, CPU 0.115736379 s / wall 0.11492365499725565 s, repair0이다. 별도 saved-data plot은 1 process PASS, CPU 3.35712228 s / wall 3.3577162440051325 s, scientific calls 0이며 root의 시각 판독은 `evidence/PLOT_READ_KO.md`에 있다. 독립 이론과 최종 코드·결과 검토는 각각 `PASS_SCOPED_STATE_THEORY`, `PASS_BOUNDED_SOURCE_BOUND_STATE_ADAPTER`이며 blocking 0이다.

다음 단계는 정확한 state/isotope/global identity 및 mass convention 결속, 물리 differential/branch source, 종별 kinetic partition과 named deposition consumer의 공급이다. 총 kinetic compensation을 종별 heating으로 부르지 않고 명시적 internal populations와 equilibrium heat capacity를 중복 계산하지 않는다. 기존 HE101 C8 PARTIAL_EXPORT/19-of-20/reserve0 및 모든 예산과 실패는 보존하며 이전 suite START는 0이다.

GitHub `create_tree` 거절 총 4회는 앞선 DRIFT02 75-file 후보에 대한 것이며 원문 `user rejected MCP tool call`, 추가 사유는 null이다. STATE04 직접 외부 쓰기는 0이고 source/central publication은 false다. S04 source commit과 source ZIP은 생성되었고 Dropbox/Drive 업로드 ACK 및 독립 ID/size 확인을 마쳤다. 전체 원격 재다운로드 SHA256은 확인하지 않았다. 중앙 13-file 후보는 `delivery/central/INDEPENDENT_REVIEW.json`의 `APPROVED_LOCAL_METADATA_DELTA_ONLY` 판정을 받았다. R10/C10은 partial이며 전체 물리 완료율은 null, L4=false다.

Source S04 `2addfab8c8975febd69d2c88eecc09afea508fbe`와 tree `af0f52ee8885e1a5f31aa933ed5efb730d7dc3bf`로 `delivery/build_source_zip.py`를 한 번 실행해 source archive를 생성했다. Builder는 선택한 committed HEAD의 전체 program_expansion, 원 DRIFT02 dependency 179 filenames와 루트 AGENTS 및 ac6042를 prerequisite로 하는 실제 Git bundle을 포함한다. PDF는 제외하고 CC BY 4.0 EMAA raw는 포함한다. 실제 source archive 영수증과 백업 확인은 `delivery/SOURCE_ARCHIVE_RECEIPT.json` 및 `delivery/BACKUP_ACK.json`에 기록한다. S04 당시 archive와 backup이 false였던 기록은 그 시점의 역사이며 현재 delivery overlay를 따른다. 이 전달 metadata를 고정하기 직전 D04, tail ZIP 및 tail 백업은 아직 없고 실제 결과는 이후 별도 external closeout에 기록한다.

Root의 범위 내 수용 판정은 `evidence/SCIENTIFIC_ACCEPTANCE.json`이며 네 번째 거절의 실제 도구 응답은 `delivery/FOURTH_APPROVAL_RESULT.json`에 보존한다.

최종 전달 preflight의 09:58:54–10:01:06 UTC 비원자적 관측에서 central HEAD는 `55202663275cd0607c968129b33de805d06f5d8b`, WU HEAD는 `a49104da1491f20d087ddfafcdf60347aaeca16a`다. Frozen MODEL의 central `5abe0d19`와 WU `4ea08eb`은 그 전 관측이다. Central은 B3h native absorption 관찰을 추가했으므로 장래 별도 후보는 새 HEAD를 기준으로 그 관찰과 다른 노드를 보존해야 한다. WU R5의 pH2/LAMDA 100 K lift는 별도 병렬 작업이며 EMAA H+ 1005 K 및 Bennett 교정 입력을 바꾸지 않는다. `delivery/preflight/PREFLIGHT.json`의 refs는 관측 시점에 한정되며 snapshot 파일 경로는 원 조사 workspace 기준이다. 과학 입력 수정·재실행은 없었다.

마지막 전달 preflight에서 2026-10-27 10:15:04 UTC의 central은 `55202663275cd0607c968129b33de805d06f5d8b`로 동일하고 WU는 `eb59de011f7cc67d465cda8e84b598a5d17251d6`이다. WU R5 S06 별도 checkpoint는 targeted checks/repair 완료와 R8 판정 대기를 보고하지만, 이를 HE 결과로 채택하거나 검증하지 않았다. 상세는 `delivery/FINAL_PREFLIGHT.json`이며 이전 비원자 snapshot은 보존한다.
