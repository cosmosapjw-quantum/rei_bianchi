# REI-CHAT-FLRW06-20261005

상태: **REFERENCE_COMPLETE__NATIVE_BLOCKED**.

실제 public Rust API에 96개 스펙트럼 node를 전달하는 것이 주 작업이다. 이 환경의 `rustc`와 `cargo` 부재로 native preflight는 exit 78을 반환했다. Native compile/call은 모두 0회다. Python의 기대값·protocol 시험을 native 성공으로 바꾸지 않았으며 FLRW06 전체를 완료 처리하지 않는다.

## 이번에 완료한 연구

FLRW05의 원 96-node 입력을 보존하고 정확한 binary64 입력에 대한 80자리 독립 기준값을 만들었다. 기존 기대값과 비교한 27개 field 중 18개가 비영이고 최대 상대차는 2.3871363948098301e-15다. 비교 대상 모두 수학적 reference이며 native 반환이 아니다.

고정 bin [L,R]에서 양의 measure가 존재할 조건은 N>=0, U-LN>=0, RN-U>=0다. 고정 forward-Euler 방향에 대해 q=(N,U-LN,RN-U), d=(dotN,dotU-L*dotN,R*dotN-dotU)를 정의하면 hmax=min_{d_j<0}q_j/(-d_j)가 정확한 closed-cone 이탈 제한이다. 안정성·truncation error·물리 또는 interval 인증의 상계가 아니다.

정확 반례: [10,20] eV에서 N=1,U=15, dN/dtau=-1,dU/dtau=-25. Count만의 제한은 Delta tau<=1이나 moment 제한은 <=1/3이다. Delta tau=1/2이면 N1=1/2>0인데 평균에너지는 5 eV로 bin 밖이다. 원 native 코드의 버그 판정은 아니다.

원 96-node의 세 bin에서도 count-only 제한과 moment-cone 제한이 달랐다.

| bin/eV | count-only h/s | moment-cone h/s | 제한 face |
|---|---:|---:|---|
|13.6–24.59|1.113020926458034e11|9.718025354290178e10|RN-U|
|24.59–54.42|7.428367066492438e11|5.759105963788322e11|RN-U|
|54.42–100|5.132056142366495e12|3.433917399651662e12|U-LN|

각 두 제한 사이에서 N은 양수이나 해당 face는 음수다. Moment-cone 조건을 production timestep으로 자동 채택하지 않았다. 유한 exponential reconstruction은 strict interior 또는 명시적 vacuum을 요구하며 boundary mean에는 delta 성분이 필요하다.

## 실행 증거

`python research/run_all.py`: 새 reference, stage/cone, unit/protocol, Python syntax의 네 명령 모두 exit 0. Unit 14개, 정확 유리수 cone 240개, 기호 항등식 4개, 80자리 reference profile 11개를 검사했다. Native error profile 6개는 준비됐지만 native 실행한 사례가 아니다. Protocol tests는 manufactured records를 사용한다. 초기 count-only 실패와 동일 cone 시험의 red/green 로그를 보존했다.

ODE 0, native compile/call 0, 과거 suite 재실행 0. 별도 reviewer dispatch 0. `results/FINAL_VERIFICATION.json`의 native blocker는 PASS 명령과 별도다.

## 최소 native 반환 경로

`research/run_native.py`는 기존 local repo에서 고정 commit의 원 source 6개를 git show로 읽어 Git blob을 확인한다. Scientific module 5개는 byte 변경 없이 사용하고 원 lib.rs의 공통 type block에 최소 wrapper와 driver만 추가한다. Cargo/전체 crate/과거 시험/network 없이 단일 rustc compile과 단일 probe process를 실행한다. Driver의 컴파일은 아직 미검증이다.

    python research/run_native.py --repo /path/to/rei_bianchi --output /path/to/new_result_directory

PhotonInput의 absorption은 실제 native photo API의 bin별 반환에서만 조립하며 expected sink를 stdin에 넣지 않는다. 167개 scalar 비교와 6개 오류코드, source/input/compiler/binary/stdout 증거가 있어야 제한된 pointwise 성공이다. 이 반환도 coupled history, 독립 U consumer, 물리 또는 구간 인증을 뜻하지 않는다.

## 최신 외부 상태

읽은 HEAD b553698a114fbff05640ab6ecb95d260410de492는 이전 chat commit69fd2901 이후 3개 commit이다. 최신 runtime 반환에서 REI-F04는 pinned static FT03 numerical domain에 한해 completed이며 다음 외부 task는 REI-F05다. 받은 checker의 최대 local bound는9.534453118819423e-9, public width는1.5867951486958153e-6이다. 이 checker를 여기서 재실행하거나 expanding spectrum에 인증을 이전하지 않았다. F07 사전등록과 새 상태를 수신하되 오래된 pending 문구는 현재 판정으로 쓰지 않는다.

## 파일 및 보존

전체 보고서 `REPORT_KO.md`, source pin `SOURCE_BINDING.json`, 최소 반환 계약 `NATIVE_RETURN_CONTRACT.json`, 다음 실행 `NEXT_HANDOFF_KO.md`를 읽는다. 전체 코드·입력·로그·결과는 동일 이름 ZIP에 있으며 archive identity와 원격 저장 확인은 별도 최종 publication receipt에 있다.

다음 chat task는 계속 FLRW06 실제 native 회귀다. 기존 CODEX_SYNC/runtime_returns/원 F00/F03/FT03를 변경하지 않는다. strict local<2e-4/public width<2e-3, [160,161] FAIL=2.1245050576368385e-4, tick160 및 physical HOLD를 보존한다. 새 branch/merge/force push 없음. 백업 R1metadata와 원격 restore와 과학 검증은 별개다.
