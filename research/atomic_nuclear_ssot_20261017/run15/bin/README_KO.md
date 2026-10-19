# Native binary 배포 범위

이 폴더의 manifest는 실제로 빌드한 executable의 bytes·SHA·출처를 기록한다. ELF bytes는 통합 연구 archive에 포함하며 Git에는 소스와 manifest를 게시한다. Git checkout에서는 `postloss_native`의 명시된 recipe로 다시 빌드한다.

`gas_rhs_server`와 `positive_planck_panel_postloss`는 최초 postloss build의 실제 bytes다. 별도 clean Git build의 binary byte identity, 수치 제어 결과 및 차이가 있으면 그 원인은 `verification/`의 최종 scoped receipt를 따른다. 같은 source에서 실행 가능한 build가 만들어지는 것과 모든 build 경로에서 byte-identical executable이 나오는 것은 서로 다른 검증 항목이다.

원래 RUN15 네 coupled history의 raw state/packet 또는 소실 전 original quadrature executable을 이 폴더의 새 binary로 대체하여 복원했다고 표시하지 않는다.
