# HE-RCT-STEP06-LIVEBUILD

CURRENT_LIBRARY_LINK_AND_FIXED_API_PARITY_PASS__OWNER_ADOPTION_PENDING. 현재 rei_microphysics library 전체23source와 기존 STEP01 add-on/STEP05 bridge/controller를 함께 빌드했다. 원자/ODE/model 연구나 새로운 mandatory gate가 아니다. 원격 consumer와 root/TASKS/dispatcher는 변경하지 않았다.

## 실제 입력과 빌드

Consumer a2bc41f848854e99e8eae9a3c5bfed06f14ccd43,root tree7f813a12c69f8ef7b29bcc1edb684a04018ed5c4,src treeec6d94bd94f335695e04a7e10fe08db36ab9a03f. 23개 원본 blob와 src tree를 모두 실제 bytes에서 대조했다. 18개는 기존 archive의 동일 source를 재사용했고 나머지5개는 Dropbox raw file로 확보했다. Cargo.toml/lock도 current blob와 같다.

RUSTFLAGS=-D warnings로 current library --lib build와 additive bridge build를 --locked --offline 실행하여 모두 exit0이다. Cargo metadata에서 current rei,addon,bridge 세 local package와 registry dependency0을 확인했다. 이는 src 전체의 일반 library build이며 examples/tests/all-targets 또는 F08 paired campaign 검증이 아니다.

기존 addon Rust,bridge Rust,restart.py,journal.py 본문은 byte-identical하다. Cargo manifest relative path만 바꿨다. 원 make_contract의41e459 historical metadata가 남는 실패를 실제 regression으로 확인하고 새 make_live_config.py에서 current dependency와 old supplier archive ownership을 분리했다. 수치 설정과 source/Ebar는 그대로이며 CLI default OFF다.

## 실행 범위

이미 저장된 OFF/KF96 Q-1,Q,Q+1 각8macro의32macro를 새 linked binary로 실행했다. step 상태8,baseline events17,RCT events4,metrics3 총1024scalar가 저장값과 bit-identical하다. 각 최종 상태/누적장부29개,총116개도 STEP05와 같으며 이116개는 일부 중복하는 별도 확인이다. 수치값은 같아도 새 worker/binding이므로 snapshot hash chain은 다르다. old worker config는 native 실행과 run directory 생성 전에 WORKER_IDENTITY_CHANGED로 거절됐다.

새 config regression1개 RED/GREEN,고정자료 campaign1회/32macro,init10호출. 이전15/18/mixed/F04/F05/SIGKILL/ODE reference를 재실행하지 않았다. 독립 scientific review/physical/interval/cross-host 인증은 없다. Rust1.94.1 archive pin은 일치하나 GPG authenticity NOT_VERIFIED다.

## 전달 및 다음 동작

전체 현재 library23파일,원 manifest/lock,기존 addon/bridge/controller,새 생성기/checker,실제 빌드/실행/snapshot은 BASS_HE_RCT_STEP06_LIVEBUILD_20261005_v1.zip에 있다. Git은 요약과 연결 도구의 projection이며 전체 runnable checkout이 아니다. library의 미빌드 examples/tests와 compiler/binary는 ZIP에 넣지 않았다. 재현 wrapper는 구성 명령 실제 실행+shell syntax 확인이고 전체 wrapper 반복실행은 하지 않았다.

이 pin에 대한 current-library 미빌드 blocker는 닫는다. Owner가 기존 EventControl/underflow 및 residual1e-15의 제한된 설정을 수락하고 동일 addon을 선택된 정적 dispatcher에 연결하는 것이 다음 동작이다. F08 팽창/분광 경로의 자동 대체나 owner 승인 대행이 아니다. HE-F2globalfalse,HE-F3/F09blocked,RCT baselineOFF,momentsnull,physicalHOLD,Eq55NOT_RUN,legacyPARKED_OPEN을 유지한다. exact archive/object identity는 DELIVERY_RECEIPT.json을 따른다.
