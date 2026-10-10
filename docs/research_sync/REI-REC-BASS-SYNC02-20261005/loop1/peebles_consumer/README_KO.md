# REI-PB03 실제 REC pointwise 소비자

`crate/`는 기존 REI solver와 분리한 `rei_peebles_reference` 연구 crate다.
REC live revision `cd68764aacfeae9fe794d7966604ac6fbb80ba7f`를 Git 의존성으로
고정하고 실제 `rec_microphysics::hydrogen_peebles` public API를 호출한다.

`ReferenceInput::from_si(Tm,Tr,nH,H,xp,x2)` 또는 명시적
`from_cgs`로 단위를 검증한다. `evaluate_collapsed`의 escape/source는
`x2=0`에서 조립하며 `dxp_dt`를 반환한다. `evaluate_retained`는 실제
`x1=1-xp-x2`로 재조립한다. `evaluate_reference`는 두 결과를 함께 내보내고
같은 retained rate에서의 closure defect와 source 조립 차이를 분리한다.
H=0, Tm≠Tr, zero ground, invalid population/units는 오류다.

실제 REC 전체 source module과 새 consumer를 Rust 1.94.1로 컴파일했다.
새 public behavior tests 10개가 통과했고 probe의 SI/cgs 두 입력과 불일치
온도 거절을 확인했다. 고정 numeric fixture는 이전 REC의 source parity
검증값을 사용한다. 새 독립 point oracle과 history 검증은 중앙 loop의
별도 증거다. 이 crate 자체의 시험을 독립 source 검증으로 중복 집계하지 않는다.

초기 missing API E0432와 첫 시험의 decimal ground expectation 오류를
각각 보존했다. 후자는 `(1-.1)-.3`의 정확한 이진 연산값을 기대하도록
수정했고 과학 수용 tolerance는 바꾸지 않았다. `RETURN.json`에 기록했다.

재현: `python build_native.py --rustc <rustc1.94+> --rec-crate <exact REC crate>`.
REC source는 `DEPENDENCY_LOCK.json`과 먼저 대조한다. 이 오프라인 rustc
시험은 Cargo의 네트워크 Git dependency resolution을 실행한 증거가 아니다.
게시 위치는 REI 저장소의 `rust/rei_peebles_reference/`다.

`PROBE_CONTRACT.json`은 LLM/독립 검사기용 입출력 예와 binary identity를
포함한다. 완전한 matched history, retained stiff integration, 열/광자 장부,
일반 Bianchi 및 원자 스레드의 과학 admission은 이 반환의 범위 밖이다.
