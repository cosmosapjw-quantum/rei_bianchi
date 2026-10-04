# Fastest-track ChatGPT ↔ Codex 동기화

대상 대화: https://chatgpt.com/c/6ac2217b-3210-83ee-ae3d-d37ba50351b3
공유 Git 브랜치: `forward/rust-reion-kernels-20260922`.

동기화 방식은 같은 브랜치의 append-only 연구 인계와 구현 반환이다. Codex는 작업 시작과 게시 직전에 원격의 새 인계를 읽고, 작은 구현·고정 검증·리뷰 뒤 이 파일과 `runtime_returns/`를 갱신한다. 원래 게시된 EXECUTION_STATE와 과거 FAIL은 보존한다. Git 게시 확인과 ChatGPT 대화의 직접 전달/확인은 별개다.

이번에 실제 읽은 최신 연구 인계는 `REI-CHAT-FT05-20261004`이며 게시 직전 읽은 원격 커밋은 `ba86cc133ff21b27ebf6fb991864d9557f66863b`다. FT03 controlled rate-moment closure와 FT05 방향 수송/에너지 장부는 각각 선언된 연구 모형의 조건부 결과다. 기존 synthetic fixture를 소급 치환하거나 physical provider를 admitted로 만들지 않았다. FT05의 proper gas-frame opacity, species event와 heating의 동일 quadrature, per-H packet의 중복 expansion 금지, escape energy/work 소유권은 향후 구현의 연결 조건이다. ChatGPT 연구의 다음 ready node는 FT06 paired science spec이며 FT04 actual-map remainder는 실제 residual/source-site를 기다린다.

Codex 구현 반환은 `../atomic_reionization_handoff_20261004_v1/runtime_returns/`에 있다. F00은 7개 독립 좌표를 갖는 별도의 homogeneous synthetic successor와 모든 Case/process/opacity 선택을 고정했다. F02는 상수율 H endpoint와 photo/collisional/secondary/recombination 사건 수를 제공하는 작은 Rust oracle다. 새로운 H/He solver, actual nonlinear remainder, physical first interval, Bianchi history는 실행하지 않았다.

검증은 crate 49개 테스트, 직접 Rust 출력에 대한 독립 Decimal(1100) 103개 사례, clippy 및 fmt를 통과했다. 독립 native 리뷰에서 수치 blocker는 없었고 P3 급수 주석을 수정했다. 유한 사례 비교와 코드 리뷰의 범위를 넘어서는 보장은 주장하지 않는다.

F01이 다음 구현 작업이다. F02는 F00만을 선행조건으로 가지므로 F01의 physical-source 검토와 독립적으로 먼저 구현했다. F01은 FT02/FT03의 exact source/domain/energy-policy 입력을 필요한 범위만 읽어 typed provider와 homogeneous bound-free adapter를 만든다. source admission과 physical claim은 각각의 실제 검증 뒤 판단한다.

엄격한 local error <2e-4 / public width <2e-3, 기존 [160,161] FAIL=2.1245050576368385e-4와 tick160 prefix는 그대로다. F02와 독립 finite Decimal 검증의 성공은 nonlinear interval 인증이 아니다.

현재 직접 대화 동기화 상태: `UNDELIVERED_BROWSER_MODULE_MISSING`.
브라우저 연결 시 필수 `browser-service.mjs`가 누락되어 대화 본문을 직접 읽거나 이 반환을 전송하지 못했다. 이 파일의 대화 URL은 owner가 지정한 연결 대상이며, 대화가 반환 내용을 확인했다는 증거가 아니다. Git 인계를 통한 내용 동기화와 이 직접 전달 상태를 분리해서 유지한다.
