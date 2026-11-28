# HE-FLRW02B: 고정 입력 native 실행 완료

판정은 FIXED_INPUT_NATIVE_PASS다. 원 계약의 consumer3dceea736f9aaa363617a9a6a5bb2854d9ff9986 전체 crate와 기존 prepared test를 실제 Rust1.94.1/Cargo로 컴파일·실행했다. code/test/GOLDEN/허용오차 수정은0이다. 원자율이나 물리모형을 재구현하지 않았다.

native 명령1회, test2개 PASS, logged comparison274개(독립 기준값192, 보존/scale82), 유일 상태5개다. 최대 상대차는 기준값2.809899931685239e-15, 보존/scale3.4885067388312133e-16이며 기존5e-14*max(abs(a),abs(b))+1e-300을 유지했다. 전체 필드 최대 절대차9.582351452493627e41은 comoving loss의 cMpc^-3 s^-1 값이며 약4.994e56 대비1.918678706357168e-15다. 단위가 다른 절대차를 하나의 물리오차로 해석하지 않는다.

실제 command:

    cargo test --manifest-path rust/rei_microphysics/Cargo.toml --test he_flrw02_absorption --locked --offline -- --nocapture --test-threads=1

기존 owner84/116/현재 전체 suite를 반복하지 않았다. 원래 준비된 혼합 두 시험의 첫 실행이다. 이전 Python reference 성공을 Rust 성공으로 바꿔 부른 것이 아니다. 실제 stdout/stderr/exit/binary hash와274개 개별 비교를 ZIP에 보존한다.

소비기 archive를 Drive1SNAc_Y3BrM86PMaVUPeritFB6oZLwGmK에서 내려받아462062bytes/SHA2567d6783579f59563eadb98c0436044f43067f0d6c461d8707d88c572d87933f6e와135개 payload를 검증했다. 원 BASS_HE reference ZIP의35개 payload도 일치했다. 이는 이 과거 Drive archive의 실제 restore 증거다. 새 결과 ZIP의 remote restore와 혼동하지 않는다.

최신 관측8fd440a2e547a61d14d7a890147f7e835fae4f2b의 atomic_provider/hhe_events/homogeneous_rates/group_rates Git blob는 실행 source bytes와 모두 같다. 그러나 live lib.rs와 추가 모듈은 빌드하지 않았다. 따라서 최신 전체 crate 검증이 아니라 원래 계약된 고정입력의 native gate 완료이며, consumer 채택 ACK는 별도다.

사용자가 준 Rust archive의 SHA256은 공개 Buildroot 원 배포 기록과 일치했다. 공식 endpoint 직접 다운로드는 DNS 실패였고 GPG는 공개키 부재로 미검증이다. rustc/cargo의 실제 -Vv 출력과 설치 로그를 보존했다. RUSTCORE는 별도 bianchi_rustcore이므로 본 소비기로 대체하지 않았다.

HE-F2의 RCT local-RHS 수락 및 stepper 대기, HE-F3/REI-F09, baseline OFF/physical HOLD/source-moment null/Eq55/legacy는 바꾸지 않는다. 소비기 remote mutation0, RCT stepper0, history0, 독립 과학 재심사0이다. 소비기는 이 return identity를 수신하고 필요한 경우에만 live build-context 회귀를 수행한다. 같은 reference derivation과 전체 suite를 재시작하지 않는다.

Git에는 결과·입력·다음 지침·이 요약을 게시한다. 정확 실행 crate/test, 원 GOLDEN/입력, 상세 보고서, 모든 명령/출력/비교/환경은 BASS_HE_FLRW02B_NATIVE_20261005_v1.zip에 있다. toolchain과 compiled binary bytes는 재배포하지 않고 hash만 남긴다. 새 ZIP의 실제 백업은 DELIVERY_RECEIPT.json을 따른다.
