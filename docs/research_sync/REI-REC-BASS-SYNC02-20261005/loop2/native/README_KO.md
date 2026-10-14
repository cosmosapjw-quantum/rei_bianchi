# 실제 REC–REI–BASS 짧은 팽창 history 실행체

이 실행체는 새 REI consumer의 `collapsed_redshift_rhs`를 RK4 모든 stage와
accepted endpoint에서 호출한다. 별도 고정 matter-only FLRW 배경은
`../research/PREREGISTRATION.json`과 같고 기존 static FT03 fixture를 바꾸지 않는다.
실행 명령은 `runtime/peebles_bass_history 400`이며 800/1600도 등록되어 있다.
`constant` 인수는 동일 BASS 경로의 별도 constant-x 해석 검산이다.

각 cell의 midpoint 상태는 accepted left state에서 독립적인 반 길이 RK4로
구한다. 이 값과 proper nH로 HHe density carrier를 만들고 실제 BASS
`integrate_rei_visibility`에 전달한다. Carrier의 H/He chemistry RHS는 호출하지
않으며, positive ideal-gas internal energy는 상태 유효성 검사만 위한 것이다.
REC 열/결합/방출 장부와의 물리 연결을 새로 주장하지 않는다.

normal/conformal time edge는 고정 배경에서 해석적으로 구한다.
`a_eff=Δt/Δη`, `χ=cη`와 동일 cell q를 new BASS clock adapter에 넣는다.
normal-clock 새 adapter 결과는 기존 visibility 결과와 bitwise 동일해야 한다.
이는 frozen cell surrogate의 좌표변환이며 실제 연속 opacity의 midpoint
근사오차는 별도 독립 history 검사기가 평가한다.

실제 pinned REC 전체 crate, 실제 최신 REI crate, BASS의 실제 네 모듈을
rustc로 함께 컴파일했다. 전체 BASS 애플리케이션 build는 아니다.
`BUILD_RESULT.json`은 source/binary identity와 command/exit를 기록한다.
오류 CLI 4개는 실행체가 nonzero exit로 거절했다. 이 구현 담당자는 history를
중복 실행하지 않았다. 중앙 `LOOP1_SYNC.json` 이후 root 독립 검사기가
원시 history를 실행했고 `../evidence/INDEPENDENT_HISTORY_RESULT.json`이
그 결과를 소유한다. 구현자의 build PASS와 독립 history 수용을 구분한다.

재현은 `sh reproduce.sh <rustc1.94+>`로 두 native build를 순서대로 수행한다.
받은 전체 packet의 상대 디렉터리 구조를 유지하고 실행 전에 각 source를
`SOURCE_BINARY_MANIFEST.json` 및 intake source lock과 대조한다. 실행체의
등록된 history는 root 독립 검사기로 검증한다. `PROBE_CONTRACT.json`은
입출력, `BUILD_RESULT.json`은 실제 build, `SOURCE_BINARY_MANIFEST.json`은
packet-relative source와 binary identity다.
