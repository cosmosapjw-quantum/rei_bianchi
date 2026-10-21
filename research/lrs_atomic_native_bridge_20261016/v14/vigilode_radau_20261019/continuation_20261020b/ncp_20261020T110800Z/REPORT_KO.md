# LRS V14 NCP 결과 | 2026-10-20

고정 source `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf`와 VigilODE pin `8a8bd409b1d96c7b7421f496d229e119fd3d284e`에서 실제 NCP release build와 기존 10개 표적 테스트를 수행했다. host `s1a0e5abed09`, 64 CPU, 125.75 GiB, cargo/rustc 1.99.0다. Build exit 0 (345.148 s), focused tests exit 0이다.

`cell-cache` 19개 고정 설정이 모두 완료됐고 native 누적 wall은 4.937 s로 180 s cap 이하였다. 동일 binary의 `cell-borrowed` fixed Radau N2 compatibility case도 exit 0 (0.0618 s)다. Cache와 borrowed의 finite N2 config/initial/observable records/RHS 시도, `charged_rhs_attempts=395`, `occupied_cell_preparations=2680`, `node_visits=252800`가 일치했다. 시간 차는 최적화 성능 주장 근거로 사용하지 않는다. `speedup=NOT_ESTABLISHED`, `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`다.

원시 case 결과와 실행 파일, receipts는 `REI_LRS_V14_CACHE_BORROWED_NCP_20261020T110800Z.tar.gz`에 보존했다. archive 47,372,583 bytes / SHA256 `b1cb2ce21c14626794c69585822a29ed016206769ec1dd217ae59ec3f70f53bd`; Drive와 Dropbox 전체 다운로드 readback이 모두 같은 크기와 SHA를 반환했다.
