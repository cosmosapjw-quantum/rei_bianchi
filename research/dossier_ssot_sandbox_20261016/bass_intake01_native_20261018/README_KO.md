# BASS-INTAKE-01 native 결과 보존 재시도

2026-10-18. 사용자의 '백업/게시부터 재시도'에 따라 첨부 native full-table 결과를 먼저 게시했다. PR193의 미컴파일 prototype과 구분하며 기존 branch/production/source owner를 변경하지 않는다.

첨부 FULL ZIP의 실제 SHA256 `33a89398e24235191799b45a67d083a7b22b078ac58483a247c8fd673c5e8c7e`,2056141bytes,81members,80payload SHA256을 이번 runtime에서 재검증했다. 함께 제공된 report/receipt의 과거 실행 근거는 Rust20tests,6744rows/6720cells,4512rays,1152thresholdqueries 및 전체 source-only fresh replay다. 이 보존 commit은 새로운 HHeD 실행이나 반복된 테스트 PASS를 주장하지 않는다.

GitHub는 두 immutable owner 파일과 나머지9파일의 정확한 압축 source packet을 보존한다. `python RESTORE_SOURCE.py`는 해시 검증 후 총11-file standalone native crate를 복구한다. 로컬에서9파일 복원을 실제 실행했고 source packet의 Git blob identity도 대조했다. 원자료/독립 분석기/실행로그 전체는 아래 FULL ZIP에 있다. 원자 반응 SourceAgeBridge 연결은 다음 미완료 단위다.

Drive FULL: https://drive.google.com/file/d/1bt70RIxlzgXqjV_CQNPmLi8WQtbH4uJc/view?usp=drivesdk
Drive raw download2056141bytes와 로컬 archive SHA256 일치.
Dropbox FULL: `/bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_BASS_INTAKE01_NATIVE_20261018_33a89398_FULL.zip`,id `id:BSpOijBcT10AAAAAAD-6Vw`. Upload completed2056141bytes, provider-specific content hash `6fe0bde26742931d653fdacc34d5236c1959190d88f13c8820817b8c02e89e08`가 로컬 계산과 일치. Raw download는 DNS error(curl exit6)로 미완료다. Content-hash검증과 raw restore를 혼동하지 않는다.

Scope: SOURCE_ONLY_NATIVE_FULL_TABLE_KINEMATICS. Full P4 PARTIAL; SA01/02,FLRW-CONV,BI-SIGNED,FULL_EOR HOLD. 기존 S10 78-file budget_native.rs와 PR192 79-file nested_budget.rs를 임의 대체/병합하지 않는다. 다음 선택단위는 검증된 BASS표를 actual reactive source-age bridge에 연결하고 짧은 matched HHeD histories를 계산하는 일이다.
