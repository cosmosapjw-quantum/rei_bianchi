# BASS_HE 연구 재개 인계 — HE-ANG-SOURCE-HEX-INTAKE

## 현재 위치

HE-X1와 HE-ANG-CONTRACT는 COMPLETE_SCOPED로 재사용했다. 이번 HE-ANG-SOURCE-HEX-INTAKE는 actual-source/data intake와 저장된 coefficient의 생략 오차 제어 범위에서 COMPLETE_SCOPED다. 부모 HE-ANG은 SOURCE_INPUT_PENDING이다.

과학 핀 S는 `15053fe4445a32e0544d644e864fe27780d08743`, 중앙 관측 C는 `0d3184538fcf27404d1b88572fc5b7f26432acdb`, 실제 중앙 백업 ACK E는 `8b6e741ceb305cb0a6fde244ee002eb5926559fe`다. 정확한 게시 정보는 [PUBLISHED_PINS.json](delivery/PUBLISHED_PINS.json)을 읽어라. E는 실제 부모 `476587d049cc5b265e599fdec45b1026d3bf6b23`의 병렬 C23D 변경을 보존했고 ACK 파일 한 개만 추가했다. 원래 고정 인계0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17와 이후 중앙 bass_cr 변경68420637a9ab54ada92afd786c5733bc0764b8c9도 보존했다.

동일한 최종 로컬 archive에 대한 Dropbox와 Drive 양쪽의 완료 ACK 및 크기 일치를 확인했다. 원문은 [FINAL_ARCHIVE_ACK.json](delivery/FINAL_ARCHIVE_ACK.json), 중앙 게시 ACK는 [중앙 E의 ACK](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8b6e741ceb305cb0a6fde244ee002eb5926559fe/research/orchestration_longterm_20261023/assembly/returns/BASS_HE_HEANG_SOURCE_BACKUP_ACK_20261024.json)에 있다. Provider metadata가 독립적인 원격 SHA256을 반환하지 않았으므로 원격 SHA256 비교는 **NOT_AVAILABLE**이다. 로컬 archive SHA256과 provider 수신 ACK를 기록하며 독립적인 원격 해시 검증을 주장하지 않는다.

## 재개할 때 먼저

1. 실제 AGENTS, 실제 HEAD, dirty/parallel 변경과 provider 백업 ACK를 확인한다. 이 디렉터리는 API로 게시한 materialized snapshot이며 로컬 git checkout이라고 가정하지 않는다.
2. RESULTS_KO.md, CLAIM_GATE.json, NEXT_SOURCE_CONTRACT.json 및 evidence/execution/RESOURCE_LEDGER.json을 읽는다.
3. 기존 완료된 X1 32fixture, HE38, HE-ANG-CONTRACT와 이번 unchanged algebra는 재실행하지 않는다. 미확정 과거비용은 UNKNOWN_NOT_ZERO로 유지한다.

## 확정한 자료 사실

Hex v2.02 source archive SHA ebb2695ff7dbf40274d329cf706a93e040d4997254c1f6677d0ccf791a9fe6ad. Hex-170210.sql.xz SHA afa8d83ada688ecf91c40340da669e204885ec5c52d04fc55b48837b52135101. 전체 decoded69,441,007B SHA82def29890bba56bb31f31524dcbea58bd0a0f5b39441ee7b6594bd28fc54896.

948,557 INSERT는 모두tmat다. H1초기100 tmat86,457행의 Ei raw extrema는1e-7..0.9374Ry이고 ionf는0이다. 이 파일의 입력부재 판정을 다른 모든source의부재나σ=0으로 바꾸지 않는다.

## 다음 단위

HE-ANG-SOURCE-PAYLOAD. 실제 H1 ionization coefficients 또는 동등한 joint differential law를 확보해 해당 payload를 명시적ABI·정규화·support로 읽는다. fixed-proton Hex를 finite-proton recoil law로 자동 변환하지 않는다. ionf/ionamp와tdcs radial power차이, incidentRy/outgoingdensityunit, spin/exchange/count2/half-shell을 해소한다. 그 뒤 기존 HE-ANG source/frame/event gate에서 동일법칙의 K_e,D_e와ionmoments를 확인한다.

현재 intake budget은 CPU18.434312/wall18.739399를 소비했다(실패포함). 남은CPU1.565688/wall41.260601은다른node로이전하지않는다. 새physicalsolve·provider scan·IVP용수치예산은없다. 새로운입력/실행이필요하면exactscope와freshcap부터고정한다.

A1/A2는 실제입력newline형식과literal검사비용을수리했고A3는INSERTguard1method를수리했다. 앞선두catalogue실패와nominal8CPUovershoot를삭제하지않는다. 실제catalogue완료evidence는A2, 최종guard검사는A3다. 과학평가와자원제한편차를구분한다.

## 복사해 사용할 재개 문구

> $physmath-research-loop로 BASS_HE를 이어가라. 이 파일과 delivery/PUBLISHED_PINS.json을 먼저 읽어라. HE-X1·HE-ANG-CONTRACT·HE-ANG-SOURCE-HEX-INTAKE의 scoped근거를 재사용하고, 첫 열린 입력은 HE-ANG-SOURCE-PAYLOAD다. 실제 ionization payload/ABI/normalization/frame/event 의무를 충족하기 전 경험적각분포나finite-mass recoil로 승격하지마라. 각node전 AGENTS·실제HEAD·병렬변경·백업을 확인하고, 실패포함누적예산을보존하며변경의존성만검증하라. 독립검토후expectedSHApush하고DAG·claim·Dropbox/Drive를갱신하라. no_merge/no_activation.
