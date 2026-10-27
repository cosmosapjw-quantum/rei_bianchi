# 다음 대화 스레드 인계 — REI CR 적분 진단 연결
문서의 source snapshot과 사후 delivery metadata는 분리한다. 이 문서가 들어 있는 ZIP 자신의 hash/ACK를 사전에 쓰지 않는다. 최종 권위는 delivery/FINAL_DELIVERY_RECEIPT.json 및 Git branch의 실제 HEAD다.

## 그대로 복사할 재개 지시
$physmath-research-loop로 cosmosapjw-quantum/rei_bianchi 연구를 이어가라. 이론 R1–R10과 코딩 C1–C10을 실제 작업으로 구분하고, 기존 근거를 재사용하라. SciSpace·Exa·Wolfram은 필요한 새 원전·기호 검증에 사용하되, 이미 완료한 계산을 장부를 채우려고 반복하지 마라.

먼저 고정 인계서를 읽어라:
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/78f7ac5864d5817ceb79b48cb5e298cc30006510/research/program_expansion_20261025/HANDOFF_KO.md

현재 작업:
- Branch: research/rei-cr-integrated-return-20261027
- Draft PR239: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/239
- 기준 PR237 최종 SHA: ee6746ab172f862dddfdec63b59e5e3707b59eaa
- 이 단위 경로: research/rei_expanded_event_consumer/cr_integrated_return_20261027
- C5 동결 코드 commit: cae5a309efb432fc2cdfada74a3529fce78de777
- 최종 source snapshot commit: C10 게시 후 FINAL_DELIVERY_RECEIPT에 기록
- Source ZIP SHA256: 포장 후 별도 receipt에 기록
- Source ZIP Drive: 최종 receipt 확인
- Source ZIP Dropbox: 최종 receipt 확인
- 별도 delivery ZIP SHA256: 자기참조 없는 사후 Git receipt 확인
- 현 branch HEAD와 AGENTS는 시작할 때 실제로 다시 읽어라. 이 문서의 포함 commit을 HEAD로 추정하지 마라.

### 현재 판정과 보존 범위
PASS_SCOPED_INTEGRATED_DIAGNOSTIC_CONSUMER. 새 실제 과학 실행1회, 24개 case/source 대안, 5,264개 assertion PASS. 독립 C5/C9 code/raw/visual review blocker0. 원래 DAG는 working32/88, central27/88, 이번 완료 원노드 증분0. REC-COUPLED는 constructive partial, L4_ready=false, global_physical_completion=null이다. 단계20개와 원래88노드 집계를 바꾸어 세지 마라. 실제20단계 Git/이중백업 여부는 STAGE_BACKUP_RECEIPTS.json의 ACK로 확인하라.

CR PR107 science4e72c89b714431eb4c6ae07def777bbf72a5ae4c, deliveryec463db0c7e5c7fb5070796071c926caa4db6445의 실제 INTEGRATED_EVENT_EXPORTS를 소비했다. Export SHA256 c6da1e2f8a079c123ab218875c27bd6f5bc73beb5465832cc28a9275b455e1b1, Gitblob3284a00148f5e16522f1c28e5db350f345c2b797,91839bytes다. 저장된 legacy source_commit b11b2e9255f2b10fb5582376412e045bd1e9151c는 실제 containing science commit과 구분하라.

사건은 He4III(index12)+tagged fast electron→He4II(index11,1s)+retained photon이다. 실제 공급자 bathT10000K, ne.14cm^-3,nHeIII.01cm^-3; elemental-He→He4 conditional, stationary heavy/zero recoil/nonrelativistic scalar-isotropic/ground spontaneous/frozen bath 범위를 유지한다. 8개 수치 case×3개의 source-z=24대안은 합산하지 마라.

A=count[m^-3],K=fast kinetic removal[Jm^-3],G=실제 supplied retained energy[Jm^-3]. 명시적 b>0에서 native25 DeltaY11=A/b,DeltaY12=-A/b,Deltazeta=-A/b,Deltaw_nt=-K/b이며 w_ext와logT를 포함한 다른 native행은0이다. 별도 photon port는(A/b,G/b)다. 진단용27행 직렬화는 새27state ODE client가 아니다. Retained G를 K+IA로 덮어쓰거나 w_ext에 중복 계상하지 마라.

b=1.4e6m^-3는 선언한 consumer normalization fixture이며 실제 recipient nb가 아니다. Production reader는 b 미제공 시 proper-volume 값과 null native projection을 유지한다. d(A/b)=dA/b-A db/b² 및 K,G의 quotient미분을 포함한다. b=beta*r이면 density행0…23,25,26에 DeltaX=beta DeltaZ와 dDeltaX=beta dDeltaZ+dbeta DeltaZ를 적용하며 logT24는 밀도로 재정규화하지 않는다. 실제 db=beta dr+r dbeta 연쇄법칙을 유지한다.

적분 사건은 proper/eta clock에 불변이며1/H를 적용하지 않는다. PR237의 continuous RHS 계약은 보존한다. 변하는 물리 reference는 dotr+3Hr=Rr, Fx=(S-xRr)/r와 full derivative를 사용하라. Endpoint (rminus*xminus+Deltan)/rplus와 drplus항은 fixed-volume manufactured algebra로만 검증됐다. 새로운 실제 시간 이력이 공급됐다고 주장하지 마라.

Source residual max1.2031443924538344e-16/2e-13, algebra max1.681255923043035e-16/2e-14, mixedFD max1.127517777594486e-10/2e-8. FD는 각 대안 한 방향, 두 step2e-4·1e-4이고 full-Jacobian 인증이 아니다. Capacity와192mutation signature는 manufactured 진단이며 물리 finite update를 실행하지 않았다.

### 최신 조사 경계와 병렬 결과
초기 전수 metadata 경계 2026-10-27 14:57:40 KST:7repo의1380branch metadata, REI236PR, 공급자최근300PR. 지정Dropbox211항목은끝까지, Drive230반환은exposed continuation 없음, 최근Library20개 및 대화 검색에서 찾은 연구는 원전대조. 모든 branch본문·모든 대화 전체export·게시되지 않은desktop까지 읽었다는 주장은 금지한다.

마지막 bounded refresh2026-10-27 16:26:51 KST:
- Central5abe0d19df95db730e3e33bae0373c81ba37ce89와 CR ec463db0… 유지.
- WU f949c21cca6e2534b725241068bd6c6e06158495: 정수식/원전 범위 결과; physical rate/Q/partition/state-lift/named-consumer/runtime/IVP activationfalse.
- REC d6dbe39a4923439547c01695d9020ba39367ea90: HD/history 진단; physical coverage0/313, physicalepsilonnull, REIactivationfalse. 별도 draft PR238/central-return60b246beedf3536ecea0848aa74a23e4786eed58.
- HE ac6042a6b0610b09d0576538767ee0299389a5eb 유지.
- BASS delivery009a1238c09adf889c7421132f530b960cdafb07; scienceaf14fc72d99f6d0e396f60aedadcdb5d05213280. DL2와 KM 별도 병렬 lane을 덮어쓰지 마라.
- VigilODE selectedGit72836e0290b66d33f4ca1771284b1c8070669a74. 별도 V8 Git미게시 sourceZIPd1fe70d681dc7dfab690e1d973829997c2b4fad2bb3c70607030dc48e39506be,650assertions는 domain-only. Native trajectory/RHS residual/Jacobian/error-bound와fullV8은별도다.

### 다음 직접 연구점
실제 donor/recipient 상태에 맞는 proper-time injection/history 계약과 recipient nb를 공급자 근거로 먼저 동결하라. 그 후에만 적분 diagnostic을 qualified rate/finite abundance step과 연결한다. Retained photon spectrum/measure, REC finite opacity, BASS source-matched transport/absorption/error radii, HE physical stopping/thermalization J_N,Q와미분·불확실성, native VigilODE client/tube 의무가 남는다. Capture hazard를 physical stoppingnu로 대신하지 마라. 전체망/L4 완료는 별도 gate로 유지하라.

PR219 bootstrap, 기존83,GRID044 opacity,PR221conditional,PR233/235/236/237의 승인된 근거를 재사용하라. 새83전구간/NCP/IVP/projection/quadrature/provider solve/old fullsuite와 attempt01 replay를 자동실행하지 마라.

### 예산·게시 권한
사용자는 필요한 백업·게시·자동 실행을 명시적으로 승인했다. 같은 권한을 다시 묻지 마라. 과학 범위와 자원 계약은 별도로 지켜라.
Main595.225063/600,NO_MORE_IVPs 유지. CR6.988054525/30는별도owner이고 HE101remaining0,V6closedlease를 보존한다.
Planning known+reserve14.477120760CPU s; presentation최종값은BUDGET_STATUS.json/FINAL_DELIVERY_RECEIPT를 읽어라. 기존누적을 초기화·이체하지마라. Temporary14.9/44.5는본유한단위종료때원cap10/30으로복원하고누적액은남긴다. Remote/tool/LLM/startup미측정비용은UNKNOWN_NOT_ZERO다.
과학실행charge.376458678CPU s,exit0,RSS12800KiB. Renderer4.972565719>4, sourceextract.184582739>.15, 첫metadata.229571720>.20, DAGupdate.154160372>.06 및 independentDAGreview.214802957>.03의초과기록을삭제하거나사후PASS로바꾸지마라. 유효한savedfigure를재렌더링하지마라.
각 새 노드 전 최신AGENTS·실제HEAD·병렬반환·이전백업ACK를 확인하라. 단일event/energy소유권과실제공급자유효범위를유지하라. 독립검토→expected-SHA/non-forcepush→sourceZIP→Drive/Dropbox이중ACK→DAG/인계갱신 순으로완료하라. 이단위의8개DAG변경은88IDs/17edges와이전nestedcontracts를보존한다. PR239는draft이며merge되지않았다.

## 읽을 파일
1. REPORT_KO.md, FROZEN_CONTRACT.md, ADMISSION.json.
2. theory/THEORY_KO.md, SOURCE_FINDINGS.md, SYMBOLIC_CHECKS.json.
3. implementation/PREEXEC_MANIFEST.json, attempt01/RESOURCE_RECEIPT.json, ACTUAL24_MAPS.md.
4. review/C5_REVIEW.json, C9_REVIEW.json, C9_ADDENDUM.json, VISUAL_REVIEW.json, DAG_REVIEW.json.
5. intake/ROOT_SURVEY.json, PREEXEC_FINAL_REFRESH.json, VIGILODE_V8_SUPPLEMENT.json.
6. STAGE_LEDGER.md/json, delivery/STAGE_BACKUP_RECEIPTS.json, FINAL_DELIVERY_RECEIPT.json, BUDGET_STATUS.json.
