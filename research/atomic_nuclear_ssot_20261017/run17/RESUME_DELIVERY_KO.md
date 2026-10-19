# RUN17 게시·복구 완료 지점

과학 기준 커밋은 `589ffbaff7b74a6cf1dbaf797285f15a58131dbd`, tree는 `b2c5d15e8f4baf0fc12d03ac40a86110c187a37e`다. 이 delivery는 해당 111개 science 파일을 수정하지 않는 추가 기록이다. 실제 최신 branch HEAD는 재개 시 다시 조회한다. PR은 [207](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/207)이며 draft 상태로 게시했고 merge하지 않았다.

## 실제 전달 검증

새 clean Git checkout에서 111개 파일, 6,069,404 bytes의 SHA-256·Git blob·Git mode가 일치했다. RUN16 base 대비 111개 추가이며 수정·삭제 0이다. 기존 5개 raw chunks로 두 원본 ZIP을 복원하고 332개 내부 manifest 항목 및 사용한 112개 source/input/evidence identity를 대조했다. 이는 원본 gas 실행 파일과 전체 toolchain의 Git-only 재빌드를 뜻하지 않는다.

ZIP `REI_RUN17_FIRST_BIRTH_RESIDUAL_20261019_125500Z.zip`은 **4,247,502 bytes**, SHA-256은 `2392f298e8c93aaba0bd802a14c0b34c142bf2c848fbae83d6aa80302de1f523`다. 실제로 새 디렉터리에 116개 항목을 복원해 byte/mode를 확인했다.

- [Google Drive ZIP](https://drive.google.com/file/d/165NpTCLSTJemPQJELIwsoJbXUiYBoxQm/view)
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/REI_RUN17_FIRST_BIRTH_RESIDUAL_20261019_125500Z.zip`, ID `id:BSpOijBcT10AAAAAAD_Q1Q`

양쪽에서 각각 전체 GET을 수행하여 4,247,502 bytes와 같은 SHA-256, ZIP CRC, manifest, 파일 mode까지 대조했다. Dropbox는 중단 전에 올라간 파일을 찾아 검증했다. 업로드를 중복하거나 덮어쓰지 않았다.

## 계산 재개 규칙

이 복구 단계에서 native RHS·IVP·build·test·과거 m2 재실행은 모두 0이다. RUN17의 실제 생산자 계산은 `README_KO.md`, `SCIENTIFIC_STATUS.json`, 실행 로그에 보존되어 있다. RUN13 standard/tight 전체 이력은 완료 상태를 유지한다. checkpoint3071이나 RUN17 A/B를 다시 실행하지 않는다.

현재 이어지는 작업은 별도 RUN18의 정확 유리수 기반 깊이 다항식 연속성 복원과 VigilODE directed interval 어댑터다. 새로운 RUN18 문서가 게시되면 그 `RESUME_KO.md` 및 `RESUME_DELIVERY_KO.md`를 우선한다. 기존 DAG의 **P4-S4C-SPECTRAL-EDGE-SUPPORT / SUBTHRESHOLD-SURVIVOR-RESOLUTION**은 계속 미완료다. 전체 시간에 대한 native RHS interval extension, admissible tube와 결합 오차, prefix 초기 오차 및 source spectral forcing이 남아 있다. 보존 residual이나 작은 수치 차이를 spectral continuum bound로 사용하지 않는다.

정확한 영수증은 `DELIVERY.json`, `delivery/BACKUP_READBACK.json`, `delivery/LOCAL_RESTORE_RECEIPT.json`, `delivery/git_readback/CLEAN_GIT_READBACK_RECEIPT.json`에 있다. signed 다운로드 URL과 인증정보는 포함하지 않는다.
