# RUN15 최소 RESUME

현재 과학 source의 기준은 RUN13 recovery HEAD `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`이다. 작업 브랜치는 `research/rei-run15-subh-optical-enclosure-20261019`이며, 최신 게시·검증 SHA와 백업은 `RESUME_DELIVERY.json`을 우선한다.

1. **RUN13을 반복하지 않는다.** m2 standard/tight는 COMPLETE, 6,241개 구간, 차원40,357이다. 원본333개 파일,113개 소스·입력,84개 endpoint 관측량이 검증됐다. checkpoint3071을 기본 재시작점으로 삼지 않는다.
2. **소실된 새 raw state를 endpoint로 선택하지 않는다.** 소실 전 새 optical n4/n6/n8 standard 및 n8 tight는 실제 완주했지만 raw case342개 파일, packet 및 일부 driver가 현재 없다. 수치는 `surface_recovery/INCIDENT_AND_RESULTS_20261019.json`의 transcript evidence로 남았다. 해당 raw history 전달은 BLOCKED다.
3. **현재 재현 가능한 최신 bounded unit은 postloss_diagnostic이다.** Tight13의 E12/T24 core는1.1803145305811728e-10, standard18의 동일 설정은1.180315129027609e-10 comoving m^-3이다. 정의된 두 gas 경로의 민감도는5.070225921291e-7이다. Tail upper1.3682511605478213e-24는 core error를 포함하지 않는다. 실제 IVP 경로와 continuum feedback bound는 없다.
4. **Native 구현도 보존했다.** `postloss_native`에는 컴파일 가능한 production source,3개 CLI controls와 재현 helper가 있다. 공식 Rust 복원 recipe와 hash가 일치하는 원래 gas 재빌드를 함께 보존한다. 원래 누락된 tests를 복구했다는 뜻은 아니다. 새 quadrature binary SHA는 `ec88048296f47a4683595aeddcafe2453cfef85bdada53189143913b076e8f66`이다.
5. **다음 기존 노드를 유지한다.** `P4-S4C-SPECTRAL-EDGE-SUPPORT/SUBTHRESHOLD-SURVIVOR-RESOLUTION` 안에서 실제 gas trajectory의 event 사이 오차와 continuous-source feedback을 고정 gas 경로의 energy error에서 분리·통제한다. 현재 노드를 전체 COMPLETE로 표시하지 않는다. 원래45-node/26-node DAG와 모든 미완료 의무를 유지한다.
6. 새 bounded unit을 완료하면 source·input·result의 원격 checkpoint를 즉시 만든다. 원본이 없는 숫자나 hash를 raw state처럼 재구성하지 않는다.

재현 명령과 실제 실행 범위는 `README_KO.md`와 각 unit의 receipt를 따른다. 기존 archive와 실패 기록은 덮어쓰지 않는다.
