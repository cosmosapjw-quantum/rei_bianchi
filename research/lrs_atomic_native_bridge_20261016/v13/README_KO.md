# REI-LRS V13: backup-first native source-on executable handoff

## 먼저 확인한 새 실행 결과
V12 RELEASE를 Drive와 Dropbox에서 실제로 각각 회수했다. 4,721,915 bytes, SHA256 a8d596c56eb837a0ecc1762c00fd2f8d5fe5790d9141ddc40f4b6e1c1962d634가 일치했다. PR195 HEAD46b567e0ee96e725a21e77fed9ab4160d0ffa9e7의 source-free144건은 이미 로컬 Rust에서 끝난 결과다. NCP 실행으로 오인하거나 V12를 다시 구현하지 않았다.

## 실제 변경
V12 native_owner를 독립 사본으로 사용하고 원래 production/기존 branch/checkpoint는 변경하지 않았다. SOURCE_DELTA.json과 source_delta/*.txt는 네 파일의 실제 컴파일된 변경을 담는다.

1. axbi_covariant_transport.rs: 기존 BE 및 양의 exponential survival/interval-mean photon occupation.
2. axbi_driver.rs: opt-in gas clocks, 동일 midpoint absorber, source before/symmetric halves/disabled, 동일 photo-event와 binding/heat의 단일 소유.
3. tests/v13_source_clocks.rs: 신규7개 회귀 테스트.
4. examples/v13_source_clock_sweep.rs: 7제어군 fixed-run 실행기와31열 단계 CSV.

RESTORE_NATIVE.py가 sibling v12/native_owner를 새 폴더로 복사하고, 부모파일2개와 결과파일4개 SHA를 확인하며 자동 패치를 적용한다. 원본 소스 덮어쓰기는 없다. 처음 monolithic encoded packet 게시의 전송 오류는 작은 byte-verified 조각으로 교체됐다. 현재 SOURCE_DELTA 및 복원 출력 SHA만 재현 기준이다.

## 검증
샌드박스 Rust1.94.1 컴파일 및 표적29/29PASS(새7개). 전체 crate 시도는334PASS/16FAIL: BASS CSV/JSON·signed continuation 입력이 V12 backup에 없어서 실패한3기존 target. 전체 회귀 PASS라 하지 않는다.

새 native119이력/8792단계 행. tight short Xend1e-5,cells8,Nmax256에서 photon self-order BE0.98210→combined1.98278. 온도는 부호 상쇄가 있어 전체 source-on p2HOLD. 긴구간Xend1e-4,cells32의 photon p1.86557,source-freeT p2.01284는 관측값이지 source-on 전체 보증이 아니다. 전체 energy residual max4.573674772245795e-12eV/H,photon residual7.623296525288703e-21/H. 독립 연속 source-on RHS NOT_RUN.

RUN_V13.sh 전체 fresh smoke도 실제 완료: 별도28이력/336행 및29테스트PASS. NCP에서 새로운 모델 코드를 작성할 필요 없이 이 실행기를 사용할 수 있다. 코드는 fixed-run용이고 experimental checkpoint/resume 직렬화는 추가하지 않았다.

## 재현 및 백업
GitHub checkout에서 v13과 형제 v12/native_owner를 함께 확보한 뒤 `bash RUN_V13.sh`를 실행한다. Bash/Python3/git/Rust 필요, cargo offline/locked, 제3자 crate나 Python 패키지 필요 없음. 본 기본 실행은7모드×6분할×2구간=84이력7056단계다. NCP는 이번 응답에서 NOT_RUN.

전체 archive: REI_LRS_V13_SOURCEON_AVERAGE_20261018_FULL.tar.gz,2307220bytes,SHA25649be73ce38094a87ac23bacd6190a9ce1517775a13dbf339b8733269162bad6d.
Drive: https://drive.google.com/file/d/1s1WAL2M2Ixfk8HgkJd69ECsLkiid59Vc/view
Dropbox: /bianchi/research_backups/rei_bianchi/REI_LRS_V13_SOURCEON_AVERAGE_20261018_FULL.tar.gz ; id:BSpOijBcT10AAAAAAD-8Ug.
두 원격 바이트 SHA일치,199개 원본 manifest검사, fresh 복원·컴파일·29테스트, 저장119이력 재분석 content identity를 확인했다. 119개 적분을 다시 실행했다고 세지 않는다. 단계별R5/C5-C6/C8/C10 Drive·Library snapshot과 whole Dropbox archive를 구별한다.

No independent subagent review; unavailable. Full EoR,CaseB,signedBianchi,uniform stiff accuracy,source-on global2차는 HOLD. 상세한 논리와 수치는 stages/C8_RESULTS.md, archive의 evidence/C8_ANALYSIS.json 및 raw CSV, DELIVERY_RECEIPT.json에 있다.
